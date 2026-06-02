"""TODO §1 とテンプレート §1 の軽量化変更に対する書き込み後検証。"""
import sys
import time
from pathlib import Path

_ROOT = Path("/Users/Daily/Development/ReviewCompass")
if str(_ROOT) not in sys.path:
  sys.path.insert(0, str(_ROOT))

from tools.api_providers.providers import get_provider

WORK = _ROOT / "tools/experiments/_yaml_audit_work"

todo_s1 = (_ROOT / "TODO_NEXT_SESSION.md").read_text(encoding="utf-8")
start = todo_s1.find("## 1. 起動手順")
end = todo_s1.find("## 2. ワークフロー")
todo_excerpt = todo_s1[start:end].strip()

tmpl = (_ROOT / "templates/todo/TODO_NEXT_SESSION.template.md").read_text(encoding="utf-8")
start = tmpl.find("## 1. 起動手順")
end = tmpl.find("## 2. 過去経緯")
tmpl_excerpt = tmpl[start:end].strip()

CONTEXT = """起動手順（§1）を軽量化した。変更の合意内容：

1. 規律 14 件は MEMORY.md 索引がセッション開始時に自動ロード済みのため、
   起動時の本文全件読み込みは不要と判断した。
2. 計画書・運営ガイドの全節読み込みも不要とし、必要な節だけ随時 Read に変更。
3. 新しい §1 は「TODO §2・§3 確認 → git 確認 → spec.json 確認」の 3 ステップのみ。
4. 操作直前に読む規律を 6 行の対応表（操作×規律ファイル名）として明示した。
5. 変更対象は TODO_NEXT_SESSION.md と templates/todo/TODO_NEXT_SESSION.template.md の 2 ファイル。
"""

PROMPT = f"""{CONTEXT}

# 成果物 1：TODO_NEXT_SESSION.md の §1（変更後）
{todo_excerpt}

# 成果物 2：templates/todo/TODO_NEXT_SESSION.template.md の §1（変更後）
{tmpl_excerpt}

# 点検の観点
(1) 合意反映：上の合意内容 1〜5 が 2 つの成果物に正しく反映されているか
(2) 内部整合：2 つの成果物の間で矛盾がないか
(3) 参照正確性：ファイルパス・規律ファイル名が正確か
(4) 重要な抜け：操作対応表に重大な漏れがないか

# 出力形式（厳守）
次の YAML だけを返してください。指摘がなければ findings: [] とし verdict: ALL_CLEAR。
verdict: ALL_CLEAR  # または HAS_FINDINGS
findings:
  - point: 1
    severity: high
    location: ...
    description: ...
    classification: substantive  # literal / substantive
"""

(WORK / "s1_verify_prompt.txt").write_text(PROMPT, encoding="utf-8")

VERIFIERS = [
  ("anthropic-api", "claude-sonnet-4-6", 120),
  ("openai-api", "gpt-5.5", 300),
  ("gemini-api", "gemini-3.1-pro-preview", 180),
]

results = {}
for provider_name, model, timeout in VERIFIERS:
  short = provider_name.replace("-api", "")
  label = f"{short}:{model}"
  try:
    provider = get_provider(provider_name)(
      model=model, timeout_seconds=timeout, max_retries=1
    )
    t0 = time.monotonic()
    resp = provider.send_request(PROMPT)
    dur = round(time.monotonic() - t0, 1)
    out = WORK / f"s1_verify_{short}.yaml"
    out.write_text(resp, encoding="utf-8")
    results[label] = ("OK", len(resp), dur)
    print(f"[OK] {label}: {len(resp)} chars, {dur}s -> {out.name}")
  except Exception as exc:
    results[label] = ("FAIL", type(exc).__name__, str(exc)[:300])
    print(f"[FAIL] {label}: {type(exc).__name__}: {str(exc)[:300]}")

ok = [k for k, v in results.items() if v[0] == "OK"]
fail = [k for k, v in results.items() if v[0] == "FAIL"]
print(f"\n=== 揃った系統：{len(ok)}/3 ===")
for k in ok:
  print(f"  - {k}")
if fail:
  print(f"=== 揃わなかった系統：{len(fail)}/3（エスカレーション対象） ===")
  for k in fail:
    print(f"  - {k}: {results[k][1]}")
