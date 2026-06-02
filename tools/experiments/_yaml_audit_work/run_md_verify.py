"""md 文書（TODO・計画書・README）の書き込み後検証。

今回の yaml-audit 作業で変更した 3 件の md ファイルを独立 3 系統で検証する。
- TODO_NEXT_SESSION.md（⑦⑧必須化リマインダを追加）
- docs/plan/reconstruction-plan-2026-05-21.md（§5.8 補助層E を追記）
- docs/disciplines/README.md（active 必読に yaml-audit を追加）
"""
import sys
import time
from pathlib import Path

_ROOT = Path("/Users/Daily/Development/ReviewCompass")
if str(_ROOT) not in sys.path:
  sys.path.insert(0, str(_ROOT))

from tools.api_providers.providers import get_provider

WORK = _ROOT / "tools/experiments/_yaml_audit_work"

# 変更差分を読み込む（変更箇所のみ渡す）
todo_excerpt = (_ROOT / "TODO_NEXT_SESSION.md").read_text(encoding="utf-8")[2400:3600]
readme_excerpt = (_ROOT / "docs/disciplines/README.md").read_text(encoding="utf-8")[:600]

# 計画書は補助層E 節のみ
plan_text = (_ROOT / "docs/plan/reconstruction-plan-2026-05-21.md").read_text(encoding="utf-8")
start = plan_text.find("#### 5.8 補助層 E")
end = plan_text.find("#### 受け入れる残余リスク")
plan_excerpt = plan_text[start:end].strip() if start != -1 else "(抽出失敗)"

CONTEXT = """今回の作業で yaml-audit 規律（補助層 E）を新設した。その作業の中で以下の合意・決定があった：

1. 設定・動作仕様 yaml 専用の監査規律（補助層 E）を新設した（md 用補助層 D と別立て）。
2. 監査観点は 11 項目。A 系統①〜⑥必須・⑦⑧推奨（段階2で自動必須化）、B 系統⑨〜⑪必須。
3. ⑦⑧は機械検査スクリプト整備と同時に自動必須化（promotion.trigger 条件）。
4. 段階づけは 1（LLM 自律・現状）/ 2（機械検査スクリプト化・⑦⑧必須化）/ 3（commit/push 関門）。
5. 計画書の多層防御補助層に補助層 E として追加した（A/B/C/D/E の 5 層構成）。
6. 規律ファイル一覧（README.md）の active 必読 表に新規律を追加した。
7. TODO に「段階2実装時の⑦⑧必須化」を将来の必須作業として記録した。
"""

PROMPT_TEMPLATE = """あなたは独立した検証者です。ある開発プロジェクトで 3 つの正本文書を更新しました。
起草者とは別系統のあなたに、更新内容が正確かつ整合しているかの点検を依頼します。

# 今回の変更の文脈
{context}

# 変更された文書（抜粋）

## 成果物 1：TODO_NEXT_SESSION.md（§3 の追加段落）
{todo}

## 成果物 2：docs/disciplines/README.md（冒頭の最終更新行と active 必読表の末尾行）
{readme}

## 成果物 3：docs/plan/reconstruction-plan-2026-05-21.md（§5.8 補助層E 節）
{plan}

# 点検の観点
(1) 文脈との整合：上の「変更の文脈」1〜7 が各成果物に正しく反映されているか
(2) 内部整合：3 つの成果物の間で矛盾がないか
(3) 参照正確性：ファイルパス・節番号・固有名詞・数値が正確か
(4) 記述の完全性：重要な決定事項が抜けていないか

# 出力形式（厳守）
次の YAML だけを返してください。指摘がなければ findings: [] とし verdict: ALL_CLEAR。
verdict: ALL_CLEAR  # または HAS_FINDINGS
findings:
  - point: 1            # 観点番号 1-4
    severity: high      # high / medium / low
    location: ...       # 対象文書と箇所
    description: ...    # 指摘内容
    classification: substantive  # literal（字句レベル）/ substantive（合意の解釈・設計判断に触れる）
"""

PROMPT = PROMPT_TEMPLATE.format(
  context=CONTEXT,
  todo=todo_excerpt,
  readme=readme_excerpt,
  plan=plan_excerpt,
)

(WORK / "md_verify_prompt.txt").write_text(PROMPT, encoding="utf-8")

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
    out = WORK / f"md_verify_{short}.yaml"
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
