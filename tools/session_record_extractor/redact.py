"""機微情報の除去（第 2 段）と書き込み前スキャン（第 3 段）。

第 2 段（redact_text）：既知の秘密パターン・ホームディレクトリ・メールを `[除去:種別]`
へ置換する。正規表現は本モジュールの既定規則に持ち、`load_rules` で外部 yaml から
追加規則を取り込める（実値は書かない）。

第 3 段（find_residual_secrets）：出力に既知パターンが残っていないか、鍵らしい高エント
ロピー文字列が残っていないかを走査する。空リストなら clean、非空なら fail-closed で
書き込みを止める判断材料とする。
"""
import re
from dataclasses import dataclass, field


@dataclass
class RedactionRules:
  """機微除去の規則一式。"""
  secret_patterns: list = field(default_factory=list)  # [(label, compiled_regex), ...]
  kv_pattern: "re.Pattern" = None
  home_pattern: "re.Pattern" = None
  email_pattern: "re.Pattern" = None
  candidate_token: "re.Pattern" = None


def _default_secret_patterns():
  return [
    # 秘密鍵ブロックは複数行にまたがるため最初に処理する
    ("秘密鍵", re.compile(
      r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
      re.DOTALL)),
    # 固有プレフィックス（普通の語に現れない）は任意長で消す。これにより
    # 既に伏せられた指紋（例: sk-ant-api03...）も公開前に除去される。
    ("anthropic-key", re.compile(r"sk-ant-[A-Za-z0-9_\-]*")),
    ("openai-proj-key", re.compile(r"sk-proj-[A-Za-z0-9_\-]*")),
    ("google-key", re.compile(r"AIza[0-9A-Za-z_\-]*")),
    ("github-token", re.compile(r"gh[pousr]_[A-Za-z0-9]*")),
    ("aws-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    # 汎用 sk- は risk-based 等の語を壊さないよう 16 文字以上の本体に限定する
    ("openai-key", re.compile(r"sk-[A-Za-z0-9]{16,}")),
    ("bearer", re.compile(r"Bearer\s+[A-Za-z0-9._\-]{20,}")),
  ]


def default_rules():
  return RedactionRules(
    secret_patterns=_default_secret_patterns(),
    # 末尾が API_KEY / TOKEN / SECRET / PASSWORD 等の変数 = 値 / : 値
    kv_pattern=re.compile(
      r"([A-Za-z_][A-Za-z0-9_]*(?:API_?KEY|TOKEN|SECRET|PASSWORD))\s*[=:]\s*['\"]?([^\s'\"]+)",
      re.IGNORECASE),
    # /Users/<名前> をホームに正規化（利用者名を消す）
    home_pattern=re.compile(r"/Users/[^/\s\"']+"),
    email_pattern=re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"),
    # ハイフン区切りの識別子（フォルダ名・rollout ファイル名・uuid 等）を鍵と
    # 誤判定しないよう、連続した base64 風の塊だけを候補とする（ハイフンは含めない）
    candidate_token=re.compile(r"[A-Za-z0-9_]{40,}"),
  )


_DEFAULT = default_rules()


def load_rules(path):
  """外部 yaml から追加規則を読み、既定規則へ重ねる（任意）。

  受け付けるキー（いずれも任意）:
    extra_secret_patterns: [{label: str, regex: str}, ...]
    home_dir_regex: str
    email_regex: str
  実際の鍵の値は書かない。正規表現だけを置く。
  """
  import yaml
  with open(path, encoding="utf-8") as f:
    data = yaml.safe_load(f) or {}
  rules = default_rules()
  for item in data.get("extra_secret_patterns", []) or []:
    label = item.get("label", "extra")
    regex = item.get("regex")
    if regex:
      rules.secret_patterns.append((label, re.compile(regex)))
  if data.get("home_dir_regex"):
    rules.home_pattern = re.compile(data["home_dir_regex"])
  if data.get("email_regex"):
    rules.email_pattern = re.compile(data["email_regex"])
  return rules


def redact_text(text, rules=None):
  """第 2 段：既知パターン・ホーム・メールを除去する。"""
  if not text:
    return text
  rules = rules or _DEFAULT
  out = text
  for label, pat in rules.secret_patterns:
    out = pat.sub(f"[除去:{label}]", out)
  if rules.kv_pattern is not None:
    out = rules.kv_pattern.sub(lambda m: f"{m.group(1)}=[除去:値]", out)
  if rules.home_pattern is not None:
    out = rules.home_pattern.sub("~", out)
  if rules.email_pattern is not None:
    out = rules.email_pattern.sub("[除去:メール]", out)
  return out


def _looks_like_key(token):
  """大文字・小文字・数字が混在する長い文字列は鍵らしいとみなす。

  sha256（小文字 16 進のみ・大文字なし）や uuid は対象外になる。
  """
  has_upper = any(c.isupper() for c in token)
  has_lower = any(c.islower() for c in token)
  has_digit = any(c.isdigit() for c in token)
  return has_upper and has_lower and has_digit


def find_residual_secrets(text, rules=None):
  """第 3 段：出力に秘密が残っていないか走査する。空なら clean。"""
  if not text:
    return []
  rules = rules or _DEFAULT
  findings = []
  for label, pat in rules.secret_patterns:
    if pat.search(text):
      findings.append(f"既知パターン残存: {label}")
  if rules.candidate_token is not None:
    for m in rules.candidate_token.finditer(text):
      tok = m.group(0)
      if _looks_like_key(tok):
        findings.append(f"高エントロピー候補: {tok[:8]}…")
  return findings
