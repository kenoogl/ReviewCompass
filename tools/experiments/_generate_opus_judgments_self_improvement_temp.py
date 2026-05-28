"""tools/experiments/_generate_opus_judgments_self_improvement_temp.py

self-improvement tasks の Opus 4.7（メインセッション本人）判定 12 件を一括生成する一時スクリプト。
セッション 39（2026-05-29）の self-improvement tasks 7 モデル比較実験で使用、後で削除予定。

本判定はメインセッション（claude-opus-4-7、私自身）の「最終判断者」としての判定。
self-improvement tasks の triad-review では私（メインセッション）は 3 役のいずれにも入っていない
（主役 Sonnet 4.6、敵対役 Opus 4.7 サブエージェント、判定役 Opus 4.7 サブエージェント）が、
私は本実験のプロンプト起草者であるため、純粋な独立判定ではない。note 欄にこの立場を明記。

出力：tools/experiments/results/topic-NN-opus-4-7.yaml（12 ファイル）
"""
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent / "results"

NOTE = """本判定はメインセッション（claude-opus-4-7、私自身）の最終判断者としての判定。
self-improvement tasks の triad-review では私は 3 役のいずれにも入っていない（主役 Sonnet 4.6、
敵対役 Opus 4.7 サブエージェント、判定役 Opus 4.7 サブエージェント）が、
私は本実験のプロンプト（事実／候補案／深掘り）の起草者であるため、純粋な独立判定ではない。
所要時間 0 は「新規 API 呼び出しではなく、判定役の統合判定と対処方向性を踏まえた起草者判断」
を意味する。本データは 7 モデル比較表の中で「起草者の意見」基準点として扱う。"""

# 12 件の Opus 4.7（メインセッション）判定
# 判定役の統合判定（§4.1 must-fix 対処方向性）と主役・敵対役の所見根拠を踏まえた起草者判断
JUDGMENTS = [
  # ===== must-fix 5 件 =====
  {
    "num": 99, "finding_id": "G-002", "decision": "採用：案 1",
    "rationale": "採番の走査対象を全 4 ディレクトリに拡張するのが、設計意図「通番リセットなし（時系列で増加）」に最も忠実かつ最小修正。第 1 期の小規模・手動運用では全ディレクトリ走査のコストは無視できる。案 2（採番台帳）は単一の真実源として堅牢だが、新規ファイル追加と競合管理が必要で第 1 期には過剰。RB-NNN にも同方式を一貫適用する。",
    "case_1": 9, "case_2": 4, "confidence": 0.88,
  },
  {
    "num": 100, "finding_id": "G-003", "decision": "採用：案 1",
    "rationale": "責務境界を一文明記するのが筋。T-004 は statistical_evidence の存在検証のみ、生成は T-005 の責務、と分ければ現行依存順（提案→検証）で破綻しない。案 2（依存逆転）はデータの流れの基本原則を崩し提案モデルが検証モデルに依存する不自然な構造になる。なお私はこの所見の must-fix 分類自体が過大評価ではないかと見ており（責務境界の明文化で解消するなら should-fix 相当）、この点は利用者議論で確認したい。",
    "case_1": 8, "case_2": 3, "confidence": 0.7,
  },
  {
    "num": 101, "finding_id": "F-005", "decision": "採用：案 1",
    "rationale": "§12.3 が明示的に metrics/ を出力先と定めている以上、§11.1 配置図への記載漏れは単純な章間不整合で、代替案は考えにくい。配置図に metrics/ を追記すれば T-001 完了条件 1 と 3 の衝突は解消する。設計は承認済みのため、再オープン手続き（軽量、§5.23.13）の要否を利用者と確認する。",
    "case_1": 9, "case_2": 0, "confidence": 0.85,
  },
  {
    "num": 102, "finding_id": "F-003", "decision": "採用：案 1",
    "rationale": "superseded は無効化された過去の承認（§8.6）であり採用に数えるのは意味的に不自然。§12.1・§8.6・T-008 完了条件 2 が分子 approved で一貫しており、§12.5 手順 3 だけが孤立した誤記。§12.5 を approved のみに統一するのが筋。案 2（§12.1 を変更）は F-013 対処の設計意図と矛盾し dominated。設計の遡及修正のため再オープン手続きの要否を確認。",
    "case_1": 9, "case_2": 2, "confidence": 0.85,
  },
  {
    "num": 103, "finding_id": "G-001", "decision": "採用：案 1",
    "rationale": "正本（pending-cross-feature-findings.md）で A-011／A-016 は対処済みであり、設計 §13.3・§19.3 の「予定／依存／前提」記述が陳腐化している。正本に合わせて更新するのみで代替案は考えにくい。tasks の「対処済み」記述は正しく、設計本文を整合させれば tasks 完了基準（§20 整合検査）が満たせる。設計の遡及修正のため再オープン手続きの要否と、同種陳腐化記述の有無を確認。",
    "case_1": 9, "case_2": 0, "confidence": 0.83,
  },
  # ===== should-fix 7 論点群 =====
  {
    "num": 104, "finding_id": "F-004", "decision": "採用：案 1",
    "rationale": "source 値域の不一致は実装（T-002 は 4 値）では既に解決済みで、本質は文書間の追跡記録の問題。tasks の DVT に差分を 1 項目追記し、要件側の追従は機能横断段で扱うのが機能内対処として軽い。案 2（要件を 4 値に更新）は承認済み要件への遡及修正で再オープン手続きが必要となり、この段階では重い。",
    "case_1": 8, "case_2": 4, "confidence": 0.78,
  },
  {
    "num": 105, "finding_id": "F-006", "decision": "採用：案 1",
    "rationale": "命名規約を一文明記するのが筋。パッケージはアンダースコア（import 対象）、CLI スクリプトはハイフン（import されない）という Python 慣行に沿い、既存の workflow-management（check-workflow-action.py）とも一貫する。案 2（全アンダースコア統一）は分かりやすいが既存補助ツールの命名と不一致になる。機能的破綻はなく文書化不足の解消が主眼。",
    "case_1": 8, "case_2": 5, "confidence": 0.75,
  },
  {
    "num": 106, "finding_id": "F-007", "decision": "採用：案 1",
    "rationale": "配置ポリシーを一文明記するのが筋。ツール内部の中間スキーマは tools/ 配下、永続データの正本スキーマは learning/ 配下、という「正本性」での分離が自然。スキーマは直下・データはサブディレクトリで階層分離すれば F-015 の誤参照リスクも限定的。案 2（全スキーマ集約）は管理しやすいがデータとスキーマが離れる。",
    "case_1": 7, "case_2": 6, "confidence": 0.68,
  },
  {
    "num": 107, "finding_id": "F-009", "decision": "採用：案 1",
    "rationale": "T-010 完了条件 3 が T-008 連動と明記する以上、前提タスクに T-008 を追加して依存閉包を前提表に明示するのが整合的。案 2（依存記述を外す）は完了条件と前提の不整合を別の形で残す。T-002 への依存（完了条件 2）も同様に前提に含めるか検討の余地。機能内対処。",
    "case_1": 7, "case_2": 5, "confidence": 0.72,
  },
  {
    "num": 108, "finding_id": "F-012", "decision": "採用：案 1",
    "rationale": "§8.8 が 5 種別すべてに追加要件を定めている以上、テストも 5 種別を網羅するのが筋。update（差分／対照表）と new_discipline（ドラフト＋関係明示）の種別固有テストを追加する。実装段で補える範囲。new_discipline の「関係明示」が grep 可能なキーワードを持つ形か、は実装時に詰める。",
    "case_1": 9, "case_2": 0, "confidence": 0.8,
  },
  {
    "num": 109, "finding_id": "F-014", "decision": "採用：案 1",
    "rationale": "完了条件に「target_discipline_path が docs/disciplines/ で始まることを機械検証」を 1 項目追加するのが、tasks レベルの要件記述として適切。案 2（スキーマ pattern 定義）は案 1 の具体的な実現手段の 1 つで排他ではなく、T-004 実装時に自然に採れる。MV-1 と併せ提案対象の限定を二重ゲートできる。",
    "case_1": 8, "case_2": 7, "confidence": 0.7,
  },
  {
    "num": 110, "finding_id": "G-004", "decision": "採用：案 1",
    "rationale": "materialization_commit_hash が空（未実体化）の場合は正常としてスキップし、値があるときだけ実在検査する、と明記するのが状態整合（承認済みだが未実体化は正常）に合う。空を fail-closed で遮断すると過剰遮断になる。案 2（MV-3 を第 1 期スコープ外）も一案だが、null 時の扱いを定義しておけば第 1 期でも部分的に機能する案 1 が勝る。機能内対処。",
    "case_1": 8, "case_2": 5, "confidence": 0.72,
  },
]


def generate() -> int:
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
    - 起草者としてのバイアス（実験プロンプトを自分が書き、その判定も自分が出すため、設計上の盲点を見落とす可能性）
    - 判定役の対処方向性を踏まえているが、議論前の暫定判断のため利用者議論で覆る可能性
  assumed_context:
    - 3 役 triad-review の所見（主役 16／敵対役独自 6）と判定役の §4.1 対処方向性を踏まえた判定
    - 過去 foundation／runtime／evaluation／analysis／workflow-management tasks の判断パターンとの整合性を考慮
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
