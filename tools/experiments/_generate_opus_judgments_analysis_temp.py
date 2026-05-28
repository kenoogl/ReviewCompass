"""tools/experiments/_generate_opus_judgments_analysis_temp.py

analysis tasks の Opus 4.7（メインセッション本人）判定 23 件を一括生成する一時スクリプト。
セッション 36（2026-05-28）の analysis tasks 7 モデル比較実験で使用、後で削除予定。

本判定はメインセッション（claude-opus-4-7、私自身）の「最終判断者」としての判定。
analysis tasks の triad-review では私（メインセッション）は 3 役のいずれにも入っていない
（主役 Sonnet 4.6、敵対役 Opus 4.7 サブエージェント、判定役 Opus 4.7 サブエージェント）が、
私は起草者であるため、純粋な「既出推奨流用」ではなく「起草者としてのメインセッション判断」
として記録する。note 欄にこの立場を明記。

出力：tools/experiments/results/topic-NN-opus-4-7.yaml（23 ファイル）
"""
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent / "results"

NOTE = """本判定はメインセッション（claude-opus-4-7、私自身）の最終判断者としての判定。
analysis tasks の triad-review では私は 3 役のいずれにも入っていない（主役 Sonnet 4.6、
敵対役 Opus 4.7 サブエージェント、判定役 Opus 4.7 サブエージェント）が、
私は tasks.md の起草者であるため、純粋な独立判定ではない。
所要時間 0 は「新規 API 呼び出しではなく統合レビュー §4.1 の対処方針案を踏まえた起草者判断」
を意味する。本データは 7 モデル比較表の中で「起草者の意見」基準点として扱う。"""

# 23 件の Opus 4.7（メインセッション）判定
# 統合レビュー記録 §4.1 の対処方針案を踏まえた起草者判断
JUDGMENTS = [
  # ===== must-fix 11 件 =====
  {
    "num": 53, "finding_id": "A-001", "decision": "採用：案 2",
    "rationale": "T-001（共通レイアウト準備）でスキーマ定義と空 manifest 雛形生成、T-002（取り込み）で内容書き込みという 2 段階分離が、共通基盤の責務一貫性と foundation／evaluation T-001 のパターン継承の両面で優れている。案 1（T-002 単独）は責務集約だが、共通レイアウト準備で manifest 関連を含めない違和感がある。",
    "case_1": 6, "case_2": 8, "confidence": 0.85,
  },
  {
    "num": 54, "finding_id": "F-015", "decision": "採用：案 1",
    "rationale": "T-002 本文への成果物追記で完結する最小変更。案 2（design.md のスキーマと実体の同一ディレクトリ統一）は意図的な責務分離（共通参照書式 vs 本機能データ）の設計判断を覆すため、根拠が薄い。",
    "case_1": 8, "case_2": 4, "confidence": 0.9,
  },
  {
    "num": 55, "finding_id": "F-008", "decision": "採用：案 2",
    "rationale": "foundation T-001 と同形式の注記（運用担保＋機械検証は規約存在と必須節充足）を踏襲。横断機能で形式統一が取れ、変更コスト最小。案 1 は機械判定を厳格化するが、「承認」の運用意味を消失させる。",
    "case_1": 5, "case_2": 8, "confidence": 0.88,
  },
  {
    "num": 56, "finding_id": "A-006", "decision": "採用：案 1",
    "rationale": "`final_label` は判定役の最終判定値で `evidence_register` の証拠属性とは別概念。T-004 完了条件から削除し foundation 3 語彙（evidence_class／review_mode／counter_status）への参照のみに修正。案 2（スキーマに追加）は設計変更を伴い影響が広い。",
    "case_1": 9, "case_2": 3, "confidence": 0.9,
  },
  {
    "num": 57, "finding_id": "F-007", "decision": "採用：案 1",
    "rationale": "T-008 前提に T-004（証拠台帳）を追加し、T-007 前提に T-005（caveat_register）を追加。前提を完全化することで依存閉包を実装者が即座に把握できる。案 2（本文で根拠明示）も妥当だが、機械検証可能性が落ちる。",
    "case_1": 7, "case_2": 6, "confidence": 0.75,
  },
  {
    "num": 58, "finding_id": "F-002", "decision": "採用：案 1",
    "rationale": "要件追跡表の T-006 行を Req 2 受入別に 4 行分解。must-fix の本質は機械検証性で、追跡表の機械検証精度を高める案 1 が筋。案 2（責務文厚化）は人間可読性のみで機械検証性を補わない。",
    "case_1": 8, "case_2": 5, "confidence": 0.85,
  },
  {
    "num": 59, "finding_id": "A-002", "decision": "別案を提示",
    "rationale": "案 1（パス検査）と案 2（スキーマ重複検査）の両方を併記し、T-011 との責務境界（T-007＝静的構造保証、T-011＝実行時入出力整合）を完了条件に明記する二段検査が筋。Sonnet 4.6 CLI も同じ別案を提示。",
    "alternative": "T-007 完了条件を 3 点に具体化：(1) 書き込み先パス制約（grep または静的解析で analysis/destinations/ 配下のみ、evaluation/ への書き込みゼロを機械検証）、(2) スキーマ非重複制約（role_diff.json／mode_diff.json のフィールド名・型定義が evaluation メトリクス契約と重複しないことをスキーマ差分で機械検証）、(3) T-011 との責務境界明記（上記 (1)(2) は静的保証、実行時整合は T-011 の責務）",
    "case_1": 5, "case_2": 7, "confidence": 0.78,
  },
  {
    "num": 60, "finding_id": "A-003", "decision": "採用：案 1",
    "rationale": "T-005 が detector を提供（書き戻し責任なし）、T-009 が呼び出し＋書き戻し（追加のみ・上書き禁止の機械検証）。design.md §305「派生段が検知主体」と整合。案 2（T-005 から detector を T-009 へ移動）は責務単純化だが design.md の規定から遠ざかる。",
    "case_1": 8, "case_2": 5, "confidence": 0.85,
  },
  {
    "num": 61, "finding_id": "A-008", "decision": "別案を提示",
    "rationale": "tasks.md T-008 完了条件と design.md §14.5 参照節の両方に対応マッピング（または TBD で仮記述）を追記する両側対処。どちらか片方のみでは不完全。Sonnet 4.6 CLI も同じ別案を提示。",
    "alternative": "(1) tasks.md T-008 完了条件に「conformance_intake.json の必須 6 項目は上流 conformance-evaluation §14.5 の必須 9 件を本機能の取り込みスキーマに再編成したもの、対応マッピングは design.md §14.5 参照節を参照（詳細は設計確認後に確定）」を追記。(2) design.md §14.5 参照節に「取り込み元 9 件 ↔ 取り込み先 6 件の対応マッピングは別途確定（TBD）、確定後ここに対応表を追記」を追加。マッピング具体内容は別途設計確認で確定。",
    "case_1": 5, "case_2": 5, "confidence": 0.8,
  },
  {
    "num": 62, "finding_id": "F-011", "decision": "採用：案 1",
    "rationale": "既存 `test_evidence_register.py` に「無声昇格検出統合版」担務を明記し、T-004 単体・T-011 統合の二層意図を T-011 責務文に明示する。案 2（専用ファイル新設）はテストファイル数を増やすが、責務一貫性は案 1 の方が高い。",
    "case_1": 8, "case_2": 5, "confidence": 0.85,
  },
  {
    "num": 63, "finding_id": "A-004", "decision": "採用：案 1",
    "rationale": "T-003 単体テスト（個別 finding の参照解決可能性）と T-011 統合テスト（全証拠の追跡経路スモーク）を二層検証として T-011 責務文に明示。foundation／evaluation T-011 と同型の責務分担。",
    "case_1": 8, "case_2": 4, "confidence": 0.88,
  },
  # ===== should-fix 12 件 =====
  {
    "num": 64, "finding_id": "F-001", "decision": "採用：案 1",
    "rationale": "Req 1 受入 2／3 を T-004 行で個別マッピング、追跡表の機械検証性を高める。F-002 must-fix と同型問題で同じ判断方針が望ましい。",
    "case_1": 8, "case_2": 4, "confidence": 0.83,
  },
  {
    "num": 65, "finding_id": "F-003", "decision": "採用：案 1",
    "rationale": "F-001 ／ F-002 と同型問題で同じ判断方針が望ましい。Req 3 受入 1／3／4 を T-005 行で個別マッピング。",
    "case_1": 8, "case_2": 4, "confidence": 0.85,
  },
  {
    "num": 66, "finding_id": "F-005", "decision": "採用：案 1",
    "rationale": "T-001 成果物欄に `shared/conformance/README.md` ／ `shared/convergence/README.md` ／ `shared/manifests/README.md` を追加し、foundation T-001 ／ evaluation T-001 の慣行（README 配置を成果物として列挙）と整合。",
    "case_1": 8, "case_2": 5, "confidence": 0.85,
  },
  {
    "num": 67, "finding_id": "F-009", "decision": "採用：案 1",
    "rationale": "grep ベース（`experiments/runtime/` 配下の文字列が成果物コードに登場しないことを検査）が should-fix 所見の投資対効果として適切。evaluation T-004 が同種を grep 系で実装しているなら統一性も高い。",
    "case_1": 8, "case_2": 5, "confidence": 0.8,
  },
  {
    "num": 68, "finding_id": "F-010", "decision": "採用：案 1",
    "rationale": "`manifest.yaml` の `superseded_versions` フィールドへの前版 ref 記録＋版番号単調増加の機械検証で完結。派生方針変更頻度が低い前提では案 1 で十分。案 2（履歴専用ファイル分離）は変更頻度が高い場合に有利だが過剰。",
    "case_1": 8, "case_2": 5, "confidence": 0.82,
  },
  {
    "num": 69, "finding_id": "F-012", "decision": "採用：案 1",
    "rationale": "T-011 既存 `test_destinations.py` に混在レビューモード検知統合テストの担務明記、T-009 単体（付与ロジック）と T-011 統合（出力先全体の一貫性）の責務分担を明示。F-011 と整合性を取る。",
    "case_1": 8, "case_2": 6, "confidence": 0.8,
  },
  {
    "num": 70, "finding_id": "F-016", "decision": "採用：案 1",
    "rationale": "design.md §配置ツリーに `analysis/fragments/` を追加（軽量再オープン）。report fragment と figures_tables は兄弟関係であり、案 2（fragments を figures_tables 配下に移動）は責務階層を誤って表現する。",
    "case_1": 8, "case_2": 4, "confidence": 0.85,
  },
  {
    "num": 71, "finding_id": "A-007", "decision": "採用：案 1",
    "rationale": "T-006 責務文に「報告断片の必須 6 項目すべて（`fragment_id` ／ `fragment_type` ／ `source_artifact_refs` ／ `maturity_label` ／ `text_stub` ／ `applicable_destinations`）を符号化」を明示追加。案 2（T-006a／T-006b に分割）は粒度を細かくするが、図表束と報告断片の責務領域は密接で 1 タスク統合が妥当。",
    "case_1": 8, "case_2": 5, "confidence": 0.82,
  },
  {
    "num": 72, "finding_id": "A-009", "decision": "採用：案 1",
    "rationale": "T-009 `audit_writer.py` から `conformance_violations_detail.json` を削除し、T-008 が単独所有として明示。書き手単一原則と design.md §484-486 の規定（T-008 が「正本の加工版を別名で配置」する役割）と整合。",
    "case_1": 8, "case_2": 4, "confidence": 0.85,
  },
  {
    "num": 73, "finding_id": "A-010", "decision": "採用：案 1",
    "rationale": "design.md の analysis 所有 4 正本節に「下流機能（self-improvement）は再定義禁止で参照のみ使用」を明示追加（design.md 軽量再オープン）。foundation の正本所有規律と同型の表現で一貫性を維持。",
    "case_1": 8, "case_2": 5, "confidence": 0.82,
  },
  {
    "num": 74, "finding_id": "A-011", "decision": "採用：案 1",
    "rationale": "F-001 ／ F-003 と同型問題で同じ判断方針。要件追跡表 Req 4 行に受入 5 ＝ T-009（`derivation_contract_version` ／ `manifest.yaml`）を個別追加。案 2（独立 Req 行化）は追跡表構造を大きく変える副作用が大きい。",
    "case_1": 8, "case_2": 4, "confidence": 0.83,
  },
  {
    "num": 75, "finding_id": "A-012", "decision": "採用：案 1",
    "rationale": "timestamp 比較ベースの検出機構（再生成側成果物の生成時刻が入力側より古い場合に登録）が should-fix 所見の投資対効果として適切。誤検出方向が安全側（過剰生成、見逃しでない）。案 2（hash 比較）は厳密だが実装複雑。",
    "case_1": 8, "case_2": 5, "confidence": 0.78,
  },
]


def generate() -> int:
  RESULTS_DIR.mkdir(parents=True, exist_ok=True)
  for j in JUDGMENTS:
    has_alt = "alternative" in j
    alt_block = f'  alternative_proposal: |\n    {j["alternative"]}\n' if has_alt else "  alternative_proposal: |\n"
    yaml_content = f"""provider: claude-code-main-session
model: claude-opus-4-7
turn_number: 1
duration_seconds: 0
sent_messages_count: 0
note: |
  {NOTE.replace(chr(10), chr(10) + '  ')}
response_text: |
  decision: "{j['decision']}"
  rationale: |
    {j['rationale']}
{alt_block}  confidence: {j['confidence']}
  turns_used: 1
  uncertainty_factors:
    - 起草者としてのバイアス（自分が書いた tasks.md を自分が判定するため、設計上の盲点を見落とす可能性）
    - 統合レビュー §4.1 の対処方針案を踏まえているが、議論前の暫定判断のため利用者議論で覆る可能性
  assumed_context:
    - 統合レビュー §1〜§3 の所見と §4.1 対処方針案を踏まえた判定
    - 過去 foundation／runtime／evaluation tasks の判断パターンとの整合性を考慮
  case_scores:
    case_1: {j['case_1']}
    case_2: {j['case_2']}
  comment_to_human:
    - 本判定は 7 モデル比較の基準点として、起草者の意見を記録するもの。最終的な対処方針は利用者議論を経て確定する
"""
    output_file = RESULTS_DIR / f"topic-{j['num']}-opus-4-7.yaml"
    output_file.write_text(yaml_content, encoding="utf-8")
    print(f"  wrote topic-{j['num']} ({j['finding_id']}, {j['decision']})")
  print(f"\n生成完了：{len(JUDGMENTS)} 件")
  return 0


if __name__ == "__main__":
  raise SystemExit(generate())
