"""yaml-audit 規定（規律＋動作仕様 yaml）の初回独立検証。

起草者（Claude Opus、メインセッション）と別系統の 3 体（Anthropic Sonnet／OpenAI GPT／
Google Gemini）に、合意事項（決定の箇条書きのみ）と起草 2 ファイルを渡して点検させる。
情報最小化：判断理由・議論ログは渡さない（枠組み伝染バイアス回避）。
揃わない系統があれば標準出力に明示し、人へのエスカレーション対象とする。
"""
import sys
import time
from pathlib import Path

_ROOT = Path("/Users/Daily/Development/ReviewCompass")
if str(_ROOT) not in sys.path:
  sys.path.insert(0, str(_ROOT))

from tools.api_providers.providers import get_provider

WORK = _ROOT / "tools/experiments/_yaml_audit_work"
WORK.mkdir(parents=True, exist_ok=True)

f1 = (_ROOT / "docs/disciplines/discipline_yaml_audit.md").read_text(encoding="utf-8")
f2 = (_ROOT / ".reviewcompass/specs/workflow-management/yaml-audit-spec.yaml").read_text(
  encoding="utf-8"
)

AGREEMENT = """あなたは独立した検証者です。ある開発プロジェクトで「yaml ファイルの監査の仕組み」を
新しく定義する 2 つのファイルが起草されました。起草者とは別系統のあなたに、起草が正しく
書けているかの点検を依頼します。判断理由は伏せ、合意された決定事項のみ示します。

# 合意された決定事項（箇条書き）
1. レビューの仕組みの根幹を決める設定・動作仕様 yaml を監査する規定を新設する。既存の md 文書用
   「書き込み後検証（post-write-verification）」とは別立てとする。
2. 対象は「ワークフロー 5 段の成果物ではなく、5 段の外側で直接編集される設定・動作仕様 yaml」。
   場所パターンで判定する。含める=config/**/*.yaml, runtime/config/**/*.yaml,
   stages/*.yaml（直下のみ）, .reviewcompass/specs/**/*.yaml。
   除く=runtime/（config 以外）, tools/, docs/, stages/completed/, stages/in-progress/,
   *.md, spec.json。
3. 監査の観点は 11 項目。A 系統（機械検査）=①構文 ②構造・必須 ③値の語彙 ④参照の実在
   ⑤規律・計画との節一致 ⑥単一正本・重複整合（①〜⑥は必須）、⑦下流コード・テスト波及
   ⑧検証テスト存在（推奨）。B 系統（独立検証）=⑨合意反映 ⑩安全側既定・規律非矛盾
   ⑪デプロイ／開発文書分離。
4. ⑦⑧は機械検査スクリプトが利用可能になった時点で自動的に必須化する（3 点：状態への条件連動・
   忘れの自動検出・3 か所への多重リマインダ）。
5. 実行は段階 1（別系統モデルが点検、現状）／段階 2（機械検査スクリプト化、⑦⑧自動必須化）／
   段階 3（commit・push 段で差し戻し）。
6. 新たに監査対象へ組み入れる yaml は組み入れ時に全件を初回検証する（「過去への遡及」ではなく
   初回適用。md 用の「遡及しない原則」とは別概念）。
7. 配置は、規律本体（md）＋動作仕様（yaml）の 2 点構成とする。
"""

INSTRUCTIONS = """# 点検の観点
次の観点で、起草に問題がないかを点検してください。
(1) 合意反映：上の決定事項 1〜7 が 2 つの成果物に正しく反映されているか
(2) 参照正確性：ファイルパス・節名・固有名詞・数値が正確で、相互参照が整合しているか
(3) 既存記述整合：2 つの成果物の間、および各記述内部で矛盾がないか
(4) 内部論理：定義・条件・段階づけに論理矛盾や抜けがないか
(5) yaml 構文・構造：成果物 2 が yaml として妥当な構文・構造か

# 出力形式（厳守）
次の YAML だけを返してください。指摘がなければ findings: [] とし verdict: ALL_CLEAR。
verdict: ALL_CLEAR  # または HAS_FINDINGS
findings:
  - point: 1            # 観点番号 1-5
    severity: high      # high / medium / low
    location: ...       # 対象ファイルと箇所
    description: ...    # 指摘内容
    classification: substantive  # literal（字句レベル）/ substantive（合意の解釈・設計判断に触れる）
"""

PROMPT = (
  AGREEMENT
  + "\n\n# 成果物 1：docs/disciplines/discipline_yaml_audit.md\n\n"
  + f1
  + "\n\n# 成果物 2：.reviewcompass/specs/workflow-management/yaml-audit-spec.yaml\n\n"
  + f2
  + "\n\n"
  + INSTRUCTIONS
)

(WORK / "verify_prompt.txt").write_text(PROMPT, encoding="utf-8")

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
    start = time.monotonic()
    resp = provider.send_request(PROMPT)
    dur = round(time.monotonic() - start, 1)
    out = WORK / f"verify_{short}.yaml"
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
  print(f"=== 揃わなかった系統：{len(fail)}/3（人へエスカレート対象） ===")
  for k in fail:
    print(f"  - {k}: {results[k][1]}")
