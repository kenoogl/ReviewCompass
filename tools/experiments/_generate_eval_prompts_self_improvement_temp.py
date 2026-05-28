"""tools/experiments/_generate_eval_prompts_self_improvement_temp.py

self-improvement tasks の 7 モデル比較実験用プロンプト（topic-99〜topic-110、12 件）を生成する一時スクリプト。
セッション 39（2026-05-29）の self-improvement tasks 7 モデル比較実験で使用、後で削除予定。

各 topic は workflow-management topic-76〜98 と同形式：
- 文脈（共通、self-improvement 用）
- 判定対象：所見番号と判定
- 概要 ／ 事実 ／ 候補案 ／ 深掘り
- あなたへの依頼 ／ 対話の進め方 ／ 出力形式

内容の出典：self-improvement tasks 段の 3 役 triad-review（セッション 39）の統合レビュー記録
  .reviewcompass/specs/self-improvement/reviews/2026-05-29-tasks-triad-review.md
- 主役レビュー（Sonnet 4.6、16 件、F-001〜F-016）
- 敵対役レビュー（Opus 4.7、独自 6 件 G-001〜G-006、counter_status 含む）
- 判定役レビュー（Opus 4.7、15 論点群統合判定、must-fix 5／should-fix 8／leave-as-is 8）

実験対象：must-fix 5 件（G-002／G-003／F-005／F-003／G-001）＋ should-fix 7 論点群
（F-004／F-006=G-006／F-007=F-015／F-009／F-012／F-014／G-004）＝ 12 件。
推奨案はプロンプトに含めない（起草者バイアス防止、実験ノート §4.4）。
"""
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent / "prompts"

TEMPLATE = """あなたは、ソフトウェアの仕様文書のレビュー結果を踏まえ、修正方針を決める最終判断者として依頼されました。

あなた（最終判断者）の役割は、3 役レビューで集まった所見と判定結果を踏まえ、判定役が「必ず直す」または「直した方がよい」と分類した所見ごとに、具体的な修正方針を決めることです。候補案の中から最適なものを選ぶか、新たな案を提示するか、情報不足のため深掘り要求を出すかを判断します。判定役の分類結果は尊重しますが、修正方針の最終決定はあなたが行います。

# 文脈

「ReviewCompass」は、ソフトウェアの仕様文書（intent ／ requirements ／ design ／ tasks ／ implementation の 5 段階）を段階的に書きながら、各段階で複数の視点でレビューを行う仕組みのシステムです（仕様駆動レビューと呼ぶ方式）。

レビューは「3 役レビュー」と呼ぶ方法で行います。同じ文書を 3 つの異なる立場の役（提案役・反論役・判定役）が独立に読み、意見を出し合います：

- **提案役**：文書を読み、問題点を網羅的に挙げる。あらかじめ決められた観点ごとに体系的に検査し、所見には重大度（CRITICAL／ERROR／WARN／INFO の 4 段階）と事実根拠（文書内の出典行）を必ず付ける。提案役は「漏れなく見つける」ことを優先する立場
- **反論役**：提案役のレビュー結果を読み、各所見を 1 件ずつ検証する。「同意（反証材料なし）」と「反証あり」の 2 択で応じ、反証ありの場合は具体的な根拠を示す。さらに、提案役が見落とした観点を独立に発見し、追加の所見として挙げる。反論役は「提案役と異なる視点で読み直す」ことを優先する立場で、提案役と異なるモデルを使う規律がある
- **判定役**：提案役と反論役の全所見を一括で読み、各所見について次の 2 つを決める。(1) 修正必要性の判定：「必ず直す（must-fix）」「直した方がよい（should-fix）」「直さなくてよい（leave-as-is）」の 3 段階に分類。(2) 波及種別の判定：「機能内対処（当該文書だけ直せばよい）」「波及（他機能の文書にも影響する）」「遡及（上流の文書を直す必要がある）」「延期（将来の段階で対処）」のいずれかに分類。判定役は「採否と影響範囲を決める」立場で、利用者と議論すべき重要な所見を明示する

現在、self-improvement（仕様駆動開発の「規律（守るべきルール）」と「実体（実際の運用パターン）」の双方向同期を担う機能。規律違反データと運用パターンを観察し、「規律を実体に追従させる」か「実体を規律に追従させる」かを判断し、提案を YAML 形式で記述・検証・承認・履歴保管する。規律ファイルの実体変更は別機能 workflow-management の手続き経由で行い、self-improvement 自身は「提案権」のみを持つ）の「設計を実装作業に分解する段階（tasks 段）」で 3 役レビューが完了しました。判定役は所見を 15 論点群に集約し、「必ず直す」5 件・「直した方がよい」8 件・「直さなくてよい」8 件と分類しました。

今回あなたに依頼するのは、その「必ず直す」または「直した方がよい」と判定された所見のひとつについて、具体的な修正方針を最終判断することです。

# 判定対象：所見番号 {finding_id}（{judgment_text}）

## 概要

{summary}

## 事実

{facts}

## 候補案

{cases}

## 深掘り（後段への影響の検討）

{deep_analysis}

# あなたへの依頼

上記の所見について、対処方針を次の 4 つから 1 つ選び、理由を添えて回答してください：

- **採用：案 1** — 案 1 を採用する
- **採用：案 2** — 案 2 を採用する
- **別案を提示** — 案 1 とも案 2 とも違う案を新たに提案する
- **深掘り要求** — 判断するには情報不足、追加の確認や調査が必要

（候補案が 1 つだけ提示されている所見では、「採用：案 1」「別案を提示」「深掘り要求」の中から選んでください。）

# 対話の進め方

不明な点があれば、判断を出す前に質問してください。最大 5 ターンの対話を許容します。十分な情報が揃ったと思ったら判定を出してください。

# 出力形式

判定を出すときは、次の YAML 形式で答えてください：

decision: "採用：案 1" | "採用：案 2" | "別案を提示" | "深掘り要求"
rationale: |
  （判断の理由を平易な日本語で 3〜10 行）
alternative_proposal: |
  （decision が「別案を提示」のときのみ、新規案の内容）
confidence: 0.0〜1.0
turns_used: <実際に使ったターン数>
uncertainty_factors:
  - （判断に残る不確実性の要因 1）
  - （判断に残る不確実性の要因 2）
assumed_context:
  - （判断にあたって暗黙に置いた前提 1）
  - （判断にあたって暗黙に置いた前提 2）
case_scores:
  case_1: 0〜10（案 1 への評価点）
  case_2: 0〜10（案 2 への評価点、案 2 がない所見では省略可）
comment_to_human:
  - （人本人への伝言、自由記述）
"""

TOPICS = [
  # ===== must-fix 5 件（G-002／G-003／F-005／F-003／G-001）=====
  {
    "num": 99,
    "finding_id": "G-002",
    "judgment_text": "必ず直す（must-fix）",
    "summary": "提案 ID の採番手順が「proposals/ ディレクトリ内の最大番号＋1」だが、承認・却下された提案は別ディレクトリへ移動するため、proposals/ には提案中のものしか残らず、過去の番号が消えて採番が重複する欠陥がある",
    "facts": """- 設計 §8.5：「採番手順：新規提案作成時に `learning/workflow/proposals/` 配下の最大番号＋1 を採用」
- 設計 §8.5：「通番リセット：なし（時系列で通番増加、年度／フェーズで振り直さない）」と明記
- 設計 §10.5：状態が変わると提案ファイルを git mv で移動する。approved → `approved-updates/`、rejected → `rejected-updates/`、superseded → `approved-updates/`。`proposals/` には pending（提案中）のものだけが残る
- つまり、承認・却下された過去の提案番号が `proposals/` から消えるため、「proposals/ の最大番号＋1」は過去に使った番号と衝突しうる
- tasks T-004 完了条件 4 もこの「proposals/ の最大番号＋1」を継承している
- ID が重複すると、履歴連結（T-007 が `target_proposal_id` で提案→承認→ロールバックを追跡する仕組み）が壊れる
- ロールバック採番（RB-NNN）も同型の問題を持つ可能性がある""",
    "cases": """- **案 1**：採番時の走査対象を全 4 ディレクトリ（proposals/ ／ approved-updates/ ／ rejected-updates/ ／ rollback/）に拡張し、その中の最大番号＋1 を採用する。設計 §8.5 と tasks T-004 完了条件 4 の両方を修正する
- **案 2**：採番台帳ファイル（例：`learning/workflow/.id-counter`）を単一の真実源として導入し、ディレクトリ走査をやめて台帳の値を増やす方式にする""",
    "deep_analysis": """- 案 1 は最小修正で、設計意図「通番リセットなし（時系列で増加）」に忠実。全ディレクトリ走査のコストは第 1 期の小規模・手動運用ではほぼ無視できる
- 案 2 は採番の真実源が単一で堅牢だが、新規ファイルの追加と、複数同時採番時の競合管理（ファイルロック等）が必要。第 1 期の手動運用には過剰になりうる
- どちらを選んでも、ロールバック採番（RB-NNN）にも同じ方式を一貫適用する必要がある
- 影響は設計 §8.5（上流文書＝遡及）と tasks の継承箇所の両方に及ぶ""",
  },
  {
    "num": 100,
    "finding_id": "G-003",
    "judgment_text": "必ず直す（must-fix）",
    "summary": "規律の格上げ提案（aspirational → enforced）が必須とする統計的証拠（statistical_evidence）を生成するのは検証モデル（T-005）だが、タスクの実装順は提案モデル（T-004）が先で、必須化が生成より先に来る依存の前後関係が論点",
    "facts": """- 設計 §8：status_change（aspirational → enforced、規律を「努力目標」から「強制」に格上げ）の提案は statistical_evidence（遵守率の証拠）を必須付与する
- 設計 §9.2：過去データへの遡及シミュレーション（過去のレビュー記録に新規律を当てて違反率を計算する手法）が statistical_evidence を生成・記録する。これは検証モデル（T-005）の責務
- tasks の実装順：T-004（提案モデル）→ T-005（検証モデル）
- T-004 完了条件 5：status_change で statistical_evidence が必須であることを機械検証する
- T-005 完了条件 1：遡及シミュレーションが statistical_evidence に記録する
- 論点の整理：T-004 は「提案の型（スキーマ）と検証ロジック」を作るタスク、T-005 は「検証手段」を作るタスク。コードを組む順序としては T-004 → T-005 で破綻しない（T-004 は statistical_evidence の「存在チェック」をするだけで、中身の値は生成しない）。一方、実行時に実際の格上げ提案を完成させるには T-005 の生成物が要る""",
    "cases": """- **案 1**：実装順は現状維持（T-004 → T-005）とし、tasks に「T-004 は statistical_evidence の存在検証のみを担い、中身の生成は T-005 の責務」と責務の境界を一文明記する。設計 §8.9／§9.2 の責務分担も明確化する
- **案 2**：T-004 の前提タスクに T-005 を追加し、実装順を T-005 → T-004 に逆転させる（生成手段を先に作ってから必須化する）""",
    "deep_analysis": """- 案 1 は最小修正。実装は現行の依存順（データの流れ §5.1「提案 → 検証」）どおり進む。「コードを組む順序」と「実行時のデータの流れ」を分けて考える立場
- 案 2 はデータの流れ（提案 → 検証）と逆行し、依存順の基本原則を崩す。提案モデルが検証モデルに依存する不自然な構造になる
- 格上げ提案（status_change）は 5 種別のうちの 1 つで、他の 4 種別（新規規律／更新／撤廃／統合）は statistical_evidence 必須ではないため、T-004 の大部分は T-005 なしで完成する
- 判定役は「依存逆転」と強く表現して must-fix としたが、責務境界の明文化だけで解消するなら should-fix 相当ではないか、という severity 自体も論点（起草者は「過大評価の疑い」と見ている。先入観を排して判断してほしい）""",
  },
  {
    "num": 101,
    "finding_id": "F-005",
    "judgment_text": "必ず直す（must-fix）",
    "summary": "効果測定の出力先ディレクトリ learning/workflow/metrics/ が、設計のディレクトリ配置図（§11.1）に記載されていないため、配置タスク（T-001）の完了条件が自己矛盾する",
    "facts": """- 設計 §11.1 の配置図（ディレクトリツリー）：learning/workflow/ 配下は proposals/ ／ approved-updates/ ／ rejected-updates/ ／ rollback/ の 4 つのみ。metrics/ が無い
- 設計 §12.3／§12.4／§17.3：効果測定の出力先・時系列保管先として `learning/workflow/metrics/<日付>.yaml` を明示的に使用している
- tasks T-001 完了条件 1：metrics/ を含む 5 ディレクトリの存在を要求
- tasks T-001 完了条件 3：「設計 §11.1 の配置図と一致する」を判定基準とする
- 結果：T-001 の完了条件 1（metrics 必須）と完了条件 3（§11.1 と一致＝metrics なし）が両立しない。実装時に配置検査が必ず失敗する""",
    "cases": """- **案 1**：設計 §11.1 の配置図に metrics/ ディレクトリを追記し、§12.3 の使用と整合させる（単純な記載漏れの補完）""",
    "deep_analysis": """- §12.3 が明示的に metrics/ を出力先と定めているため、§11.1 の配置図への記載漏れは単純な章間の不整合であり、代替案は考えにくい
- 影響は設計 §11.1（上流文書＝遡及修正）。設計は既に「承認（approval）」まで完了済みのため、確定済み文書を直すには「再オープン手続き」（一度確定した内容を変更する正式な手順、軽量版が §5.23.13 にある）を踏む必要があるかが論点
- 深掘りの主眼は「再オープン手続きをどう踏むか」と「§11.1 以外に同種の配置漏れがないか」""",
  },
  {
    "num": 102,
    "finding_id": "F-003",
    "judgment_text": "必ず直す（must-fix）",
    "summary": "提案の採用率の計算式が、設計内の 2 箇所で食い違っている（分子に superseded＝上書き済みの過去承認を含めるか否か）",
    "facts": """- 設計 §12.1：採用率 ＝ approved ÷（approved ＋ rejected ＋ superseded）。分子は approved のみ
- 設計 §8.6：「採用率の分母は approved ＋ rejected ＋ superseded（pending は分母から除外、決定済み提案のうちの採用率を計算する設計意図）」。分子は approved 相当
- 設計 §12.5 手順 3：「採用率を（approved ＋ superseded）÷（approved ＋ rejected ＋ superseded）で算出」。分子に superseded を含んでいる
- tasks T-008 完了条件 2：採用率の分母が approved ＋ rejected ＋ superseded で計算されることを機械検証（分子は approved の立場）
- tasks T-008 完了条件 5：§12.5 の 4 ステップが再現可能であることを要求（＝誤った式を継承してしまう）
- superseded の意味（§8.6）：後続提案で上書きされ、無効化された過去の承認""",
    "cases": """- **案 1**：設計 §12.5 手順 3 の分子を approved のみに修正し、§12.1 に統一する
- **案 2**：逆に §12.1 を §12.5 に合わせ、分子を approved ＋ superseded にする（superseded も採用に数える）""",
    "deep_analysis": """- superseded は「無効化された過去の承認」（§8.6）であり、これを採用に数えるのは意味的に不自然。§12.1（分子 approved）が設計意図に合う
- 案 2 を採ると、過去の F-013 対処（pending を分母から除外して「決定済み提案のうちの採用率」を計算するという設計意図）と整合が取りにくくなる
- §12.1 は複数箇所（§8.6、tasks T-008 完了条件 2）と一貫しており、§12.5 だけが孤立した誤記と見られる
- 影響は設計 §12.5（上流文書＝遡及修正）。確定済み設計のため再オープン手続きの要否が論点""",
  },
  {
    "num": 103,
    "finding_id": "G-001",
    "judgment_text": "必ず直す（must-fix）",
    "summary": "設計書の本文が、既に対処済みの横断所見（A-011／A-016）を「未対処・対処予定」と古いまま記述しており、tasks の「対処済み」という記述と矛盾している",
    "facts": """- 横断所見の正本（pending-cross-feature-findings.md）166 行：A-011 は「✅ 対処済み（2026-05-26、セッション 28）」、evaluation の設計に role_diff_report.json（3 役の差分報告ファイル）を実際に新設済み
- 同 247 行：A-016 も「✅ 対処済み（セッション 28）」
- 設計 §13.3（611 行）：「role_diff_report.json、A-011 対処で evaluation 設計に追加予定、本機能の design.alignment は A-011 消化に依存」（セッション 27 時点の古い記述のまま）
- 設計 §19.3（923 行）：「A-011（既存、design レビュー波段で消化予定）……A-011 消化が本機能の design.alignment の前提」（古い記述のまま）
- tasks T-010：A-011／A-016 を「対処済み」と正しく記述している
- 3 役レビューで提案役は古い設計本文だけを見て「tasks が偽の完了宣言をしている」と最重大（CRITICAL）認定したが、反論役が正本を参照して反証（陳腐化しているのは設計側）した経緯がある""",
    "cases": """- **案 1**：設計 §13.3・§19.3 を「A-011 対処済み（セッション 28、evaluation に role_diff_report.json 新設済み）」に更新する。§19.3 の「design.alignment の前提」という記述も「対処済みのため前提充足」に直す（正本に合わせるだけ）""",
    "deep_analysis": """- 「tasks は正しく、設計が古い」という構造。tasks の完了基準（設計 §20 の整合検査に通ること）を満たすには、設計本文の整合が必要
- 影響は設計 §13.3・§19.3（上流文書＝遡及修正）。設計は承認まで完了済みのため再オープン手続きの要否が論点
- 代替案が考えにくいため、深掘りの主眼は「再オープン手続きをどう踏むか」「§13.3・§19.3 以外に同種の陳腐化記述が残っていないか」""",
  },
  # ===== should-fix 7 論点群 =====
  {
    "num": 104,
    "finding_id": "F-004",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "入力データの来歴に付ける source（出所の種別）の値域が、要件（3 種類）と設計（4 種類）で食い違っているが、その差分を追跡する仕組み（遅延確認事項テーブル＝未確定事項の管理表）に登録されていない",
    "facts": """- 要件 Req 4 受入 2：motivating_evidence.source（提案の動機づけ根拠の出所）の値域を review_record ／ compliance_report ／ user_audit の 3 種類で定義
- 設計 §6.2：F-007 対処として observation_pattern（実体運用パターン）を追加し、4 種類に拡張
- tasks T-002：設計に従い 4 種類を採用
- 要件（3 種類）と設計（4 種類）の差分を追跡する遅延確認事項テーブル（DVT）の項目が無い
- 反論役の評価：下流（設計・tasks）が上流（要件）の拡張に追従する正方向で、実装上の内部整合は取れている""",
    "cases": """- **案 1**：tasks の遅延確認事項テーブルに「要件 Req 4 受入 2（source 3 種類）と設計 §6.2（4 種類）の差分。設計側が上位互換で拡張済み、要件側の追従は機能横断段で確認」を 1 項目追加する
- **案 2**：要件 Req 4 受入 2 自体を 4 種類に更新する（要件への遡及修正）""",
    "deep_analysis": """- 案 1 は tasks 内の追記で完結する（機能内対処）。要件の更新は機能横断段や別途で扱う
- 案 2 は要件への遡及修正となり、要件は承認完了済みのため再オープン手続きが必要
- source の値域不一致は実装（T-002 は 4 種類）では既に解決済みで、本質は文書間の追跡記録の問題""",
  },
  {
    "num": 105,
    "finding_id": "F-006",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "ツール類のファイル名が、アンダースコア区切りとハイフン区切りで混在しており、命名のルールが文書化されていない",
    "facts": """- tools/self_improvement/ 配下の Python ファイル（input_model.py 等、T-002〜T-008）：アンダースコア区切りのパッケージ（他から import して使うモジュール群）
- tools/self-improvement-check.py（T-009）：ハイフン区切りのスクリプト（単独で実行する CLI ツール）
- 設計には明示的な命名ルールの記述が無い
- 反論役（G-006）：パッケージはアンダースコア（import 対象）、CLI スクリプトはハイフン（import されない）として機能的に両立可能。重大度を ERROR から WARN へ緩和できる余地がある
- 既存の別機能 workflow-management の check-workflow-action.py も同型（ハイフン区切りの CLI）""",
    "cases": """- **案 1**：tasks に命名ルールを一文明記する。「import 対象の Python パッケージ／モジュールはアンダースコア区切り（tools/self_improvement/）、import されない単独実行 CLI スクリプトはハイフン区切り（tools/self-improvement-check.py）」
- **案 2**：すべてアンダースコアに統一し、CLI スクリプトも tools/self_improvement_check.py にする""",
    "deep_analysis": """- 案 1 は既存の workflow-management（check-workflow-action.py）と一貫し、Python の慣行（パッケージ vs スクリプト）に沿う
- 案 2 は完全統一で分かりやすいが、既存の補助ツールの命名（ハイフン）と不一致になる
- 機能的な破綻は無く、文書化不足の解消が主眼。機能内対処""",
  },
  {
    "num": 106,
    "finding_id": "F-007",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "スキーマ定義ファイル（データの形式を定める設計図）の置き場所が、tools/ 配下と learning/ 配下に分散しており、配置のルールが明文化されていない",
    "facts": """- T-002 の provenance.schema.json、T-003 の signal.schema.json：tools/self_improvement/ 配下に配置
- T-004 の proposal.schema.json、T-007 の rollback.schema.json、T-008 の metrics.schema.json：learning/workflow/ 配下に配置
- 設計 §11.1 の配置図にスキーマファイルの置き場所の記述が無い
- 関連所見 F-015：proposal／rollback／metrics の 3 スキーマが learning/workflow/ の直下に置かれ、その下のサブディレクトリにあるデータ YAML と混在する。別機能 workflow-management が approved-updates/ を読むときに誤って参照する懸念がある""",
    "cases": """- **案 1**：tasks に配置ルールを一文明記する。「ツール内部の中間スキーマ（provenance／signal）は tools/self_improvement/ 配下、永続データの正本スキーマ（proposal／rollback／metrics）は learning/workflow/ 配下」。スキーマは learning/workflow/ の直下、データは各サブディレクトリ配下で階層を分ける
- **案 2**：すべてのスキーマを tools/self_improvement/schemas/ に集約する""",
    "deep_analysis": """- 案 1 はデータとスキーマを「正本性」で分ける考え方。永続データの正本スキーマをデータの近く（learning/）に置く
- 案 2 は全スキーマを 1 箇所に集約して管理しやすいが、データとスキーマが物理的に離れる
- 誤参照リスク（F-015）は階層分離（スキーマは直下、データはサブディレクトリ）で実害は限定的。機能内対処""",
  },
  {
    "num": 107,
    "finding_id": "F-009",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "他機能との接合面を整えるタスク（T-010）の完了条件が、効果測定タスク（T-008）の成果に依存すると明記されているのに、前提タスクの一覧に T-008 が含まれていない",
    "facts": """- tasks T-010 の前提タスク：T-004、T-006 のみ
- T-010 完了条件 3：「analysis 向け出力が learning/workflow/metrics/<日付>.yaml に機械可読形式で書かれる（T-008 連動）」と T-008 への依存を明記
- 設計 §13.2（runtime からの入力消費）は T-002（入力モデル）の読み取り経路にも依存する
- 反論役：T-010 は接合面の整備で、T-008 の完了を厳密に待たなくても起草できる。依存順の明示漏れに留まる""",
    "cases": """- **案 1**：T-010 の前提タスクに T-008 を追加する（T-004／T-006／T-008）
- **案 2**：前提タスクは現状維持とし、T-010 完了条件 3 から「T-008 連動」の依存記述を外して、metrics 出力の検証は T-008 側に委ねる""",
    "deep_analysis": """- 案 1 は依存関係を前提表に明示し、実装者が把握しやすいが、T-010 の着手が T-008 完了まで遅れる
- 案 2 は前提表を最小に保つが、完了条件と前提の不整合が残る
- T-002（入力モデル）への依存も完了条件 2（evaluation 入力読み取り）にあり、前提に含めるか同様の論点。機能内対処""",
  },
  {
    "num": 108,
    "finding_id": "F-012",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "提案の種別ごとに必要な追加テストが、5 種別のうち 3 種別しか列挙されておらず、更新（update）と新規規律（new_discipline）のテストが欠落している",
    "facts": """- 設計 §8.8：update（更新）種別には「変更箇所の差分（または変更前後の対照表）」、new_discipline（新規規律）には「ドラフト＋関係の明示」を追加要件として定義
- tasks T-004 のテスト要件：「種別別追加要件テスト（consolidation ／ archive ／ status_change）」の 3 種別のみ列挙
- update ／ new_discipline の種別固有のテストが明示されていない""",
    "cases": """- **案 1**：T-004 のテスト要件に update（差分／対照表）と new_discipline（ドラフト＋関係明示）の種別固有テストを追加し、§8.8 の全 5 種別を網羅する""",
    "deep_analysis": """- §8.8 が 5 種別すべてに追加要件を定めているなら、テストも 5 種別を網羅するのが望ましい
- 実装段で補える範囲のため should-fix。機能内対処
- 深掘りの主眼：new_discipline の「関係の明示」が機械的に検証できる形か（grep できるキーワードがあるか）""",
  },
  {
    "num": 109,
    "finding_id": "F-014",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "提案の対象を「本機能が所有する規律のみ」に限定する要件に対し、対象パス（target_discipline_path）が規律フォルダ docs/disciplines/ 配下であることを機械的に検証する完了条件が無い",
    "facts": """- 要件 Req 3 受入 2：提案対象を本機能が所有する規律のみとする
- 要件 Req 3 受入 4：target_discipline_path（対象規律のパス）を明示する
- 設計 §8.2：提案対象の限定
- tasks T-004 完了条件 2：必須フィールドの存在のみ検証（値の範囲＝パス制約には踏み込まない）
- target_discipline_path が docs/disciplines/ で始まることの機械検証（grep またはスキーマの pattern 制約）が完了条件に無い""",
    "cases": """- **案 1**：T-004 完了条件に「target_discipline_path が docs/disciplines/ で始まることを機械検証（スキーマの pattern 制約または grep）」を 1 項目追加する
- **案 2**：proposal.schema.json の target_discipline_path に正規表現の pattern（例：^docs/disciplines/discipline_.*\\.md$）を定義し、スキーマ検証で担保する""",
    "deep_analysis": """- 案 1 と案 2 は排他ではなく、案 2（スキーマの pattern）は案 1（完了条件への明記）の具体的な実現手段の 1 つ
- MV-1（規律ファイルへの直接書き込み検出）と併せると、提案対象の限定を二重にゲートできる
- 機能内対処""",
  },
  {
    "num": 110,
    "finding_id": "G-004",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "機械検査 MV-3 が検査する materialization_commit_hash（規律変更が実際にコミットされた時の git のコミット識別子）は他機能 workflow-management が書き込むため、第 1 期は常に空となり、検査が素通りする扱いが未定義",
    "facts": """- tasks T-009 の MV-3：materialization_commit_hash が git の履歴で実在するコミットを指すことを `git cat-file -e` で検査
- 設計 §13.5：materialization_commit_hash の書き込み主体は workflow-management（規律変更の完了通知時に書く）。self-improvement の所有外
- 第 1 期は workflow-management 側が未実装のため、materialization_commit_hash は常に空（null）
- 設計 §17.3：fail-closed 方針（検査に失敗したら処理を遮断する）
- 空（null）のときに MV-3 が「検査対象ゼロで素通り（vacuously pass）」するのか「スキップ」するのかが未定義""",
    "cases": """- **案 1**：MV-3 に「materialization_commit_hash が空（未 materialized＝まだ実体化されていない）の場合は正常としてスキップし、値があるときだけ実在検査する」と明記する。tasks T-009 と設計 §17.1 に追記
- **案 2**：第 1 期は MV-3 を「未実装（フェーズ 4 以降）」と明示し、検査自動化の遅延確認事項（DVT-S003）に統合する""",
    "deep_analysis": """- 案 1 は空（null）を「未実体化の正常な状態」と定義し、実体化された後のみ検査する。状態（承認済みだが未実体化は正常）との整合が取れる
- 案 2 は MV-3 自体を第 1 期のスコープ外とし、自動化と同時に実装する
- fail-closed 原則との関係：空（null）を「結論不能」として遮断すると過剰な遮断になるため、空を正常扱いとするのが妥当か、が論点
- 機能内対処""",
  },
]


def generate_prompts() -> int:
  OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
  for topic in TOPICS:
    prompt = TEMPLATE.format(
      finding_id=topic["finding_id"],
      judgment_text=topic["judgment_text"],
      summary=topic["summary"],
      facts=topic["facts"],
      cases=topic["cases"],
      deep_analysis=topic["deep_analysis"],
    )
    output_file = OUTPUT_DIR / f"topic-{topic['num']}.txt"
    output_file.write_text(prompt, encoding="utf-8")
    print(f"  wrote topic-{topic['num']} ({topic['finding_id']}, {topic['judgment_text'][:8]})")
  print(f"\n生成完了：{len(TOPICS)} 件")
  return 0


if __name__ == "__main__":
  raise SystemExit(generate_prompts())
