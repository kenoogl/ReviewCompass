"""tools/experiments/_generate_eval_prompts_analysis_temp.py

analysis tasks の 7 モデル比較実験用プロンプト（topic-53〜topic-75、23 件）を生成する一時スクリプト。
セッション 36（2026-05-28）の analysis tasks 7 モデル比較実験で使用、後で削除予定。

各 topic は次の構造（runtime topic-18 と同形式）：
- 文脈（共通、analysis 用）
- 判定対象：所見番号と判定
- 概要 ／ 事実 ／ 候補案 ／ 深掘り
- あなたへの依頼 ／ 対話の進め方 ／ 出力形式

内容の出典：.reviewcompass/specs/analysis/reviews/2026-05-28-tasks-triad-review.md
- §1 主役レビュー（16 件、F-001〜F-016）
- §2 敵対役レビュー（12 件、A-001〜A-012、counter_status 含む）
- §3 判定役レビュー（28 件統合判定、must-fix 13／should-fix 12／leave-as-is 3）
- §4.1 must-fix 11 件の対処方針案（機能内、機能横断 2 件は除外）

機能横断波及（F-013／A-005）の 2 件は pending-cross-feature-findings.md §A-018 として持ち越し、本実験対象から除外。
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
- **判定役**：提案役と反論役の全所見（合計で 10〜30 件程度）を一括で読み、各所見について次の 2 つを決める。(1) 修正必要性の判定：「必ず直す（must-fix）」「直した方がよい（should-fix）」「直さなくてよい（leave-as-is）」の 3 段階に分類。(2) 波及種別の判定：「機能内対処（当該文書だけ直せばよい）」「波及（他機能の文書にも影響する）」「遡及（上流の文書を直す必要がある）」「延期（将来の段階で対処）」のいずれかに分類。判定役は「採否と影響範囲を決める」立場で、利用者と議論すべき重要な所見を明示する

現在、analysis（分析機能、evaluation の成果物と conformance-evaluation の検査結果を入力に、4 出力先向けの構造化成果物を組み立てる機能）の「設計を実装作業に分解する段階（tasks 段）」で 3 役レビューが完了しました。判定役は所見 28 件を判定し、「必ず直す」13 件・「直した方がよい」12 件・「直さなくてよい」3 件と分類しました。

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
  case_2: 0〜10（案 2 への評価点）
comment_to_human:
  - （人本人への伝言、自由記述）
"""

TOPICS = [
  # ===== must-fix 11 件（機能内対処、機能横断波及 F-013／A-005 は除外）=====
  # 優先 1：3 件（A-001、F-015、F-008）
  {
    "num": 53,
    "finding_id": "A-001",
    "judgment_text": "必ず直す（must-fix）",
    "summary": "`analysis_manifest.yaml`（design.md で正本宣言）の作成・配置タスクが全 11 タスクのどこにも明記されていない",
    "facts": """- design.md 行 114 で `analysis/shared/manifests/analysis_manifest.yaml` が「本機能の論理版と入力被覆を記録」する必須成果物として明示宣言されている
- design.md 行 248 で `source_analysis_manifest_ref` フィールドが `evidence_register` の必須項目として参照されている
- tasks.md 全 11 タスクの成果物欄・責務欄を `grep` した結果、`analysis_manifest` は 1 件もヒットしない（敵対役 Opus 4.7 が確認）
- T-009 の出力先別 manifest（`destinations/<出力先>/manifest.yaml`）とは別物で、`shared/manifests/` 配下に置く本機能全体の論理版を記録する成果物
- `analysis_logic_version` の確定タスクが不明""",
    "cases": """- **案 1**：T-002（取り込み）の成果物欄に `analysis/shared/manifests/analysis_manifest.yaml` と `analysis_manifest.schema.json` を追加。責務に「`analysis_logic_version` ／ 入力被覆 ／ 生成日時の記録」を明記し、T-002 完了条件にスキーマ検証を追加
- **案 2**：T-001（共通レイアウト）で `shared/manifests/` ディレクトリ準備時に空の `analysis_manifest.yaml` 雛形を生成し、T-002 で内容（取り込み結果に基づく入力被覆）を書き込み。スキーマ定義は T-001 で行い、書き込みは T-002 で行う 2 タスク分担方式""",
    "deep_analysis": """- design.md §配置の正本宣言（行 114）と tasks.md の成果物列の双方向整合は、T-011（双方向整合テスト）の機械検証対象だが、宣言された必須成果物そのものが tasks.md に欠落していると T-011 まで実装する段階で初めて検出される
- `analysis_logic_version` は本機能の派生方針の版管理に直結し、`evidence_register` の各エントリが参照する。manifest の生成タスクが特定されないと、誰がどの時点で `analysis_logic_version` を確定するかが不明
- 案 1 は単一タスク（T-002）で完結し責務が集約。案 2 はスキーマ定義（T-001）と内容書き込み（T-002）を分離し、共通レイアウト準備の自然な拡張になる。foundation T-001／evaluation T-001 の方針継承との整合が高い
- 案 1 を採れば T-002 完了条件と T-002 成果物のスキーマ検証で機械的に検出可能。案 2 は T-001 完了条件にも対応行を追加する必要がある""",
  },
  {
    "num": 54,
    "finding_id": "F-015",
    "judgment_text": "必ず直す（must-fix）",
    "summary": "`intake_failure_report.json` の書き出し先（`analysis/shared/manifests/`）が T-002 本文に明示なし、実装者が誤認するリスク",
    "facts": """- design.md 行 115 で `intake_failure_report.json` の配置先は `analysis/shared/manifests/intake_failure_report.json` と定義されている
- tasks.md T-002 の成果物欄（行 60-61）には `analysis/intake/intake_reader.py` と `analysis/intake/intake_failure_report.schema.json` のみ列挙
- 実体 JSON ファイル（書き出し先）が `analysis/shared/manifests/` であることが T-002 本文に明示されていない
- スキーマファイル（`schema.json`）と実体（`.json`）の配置場所が異なる構造""",
    "cases": """- **案 1**：T-002 成果物欄に `analysis/shared/manifests/intake_failure_report.json`（実体ファイル）を明示追加。スキーマ（`analysis/intake/intake_failure_report.schema.json`）と実体（`analysis/shared/manifests/intake_failure_report.json`）の配置差を本文で説明
- **案 2**：design.md §配置を見直し、スキーマと実体を同一ディレクトリ（`analysis/shared/manifests/`）に統一する遡及修正""",
    "deep_analysis": """- 案 1 は機能内対処で完結、tasks.md の修正のみで済む
- 案 2 は design.md への遡及修正（軽量再オープン）が必要。スキーマと実体の配置を分離する設計判断の根拠（共通参照書式と本機能専用データの責務分離）を覆すかどうかの議論が必要
- foundation T-002 ／ evaluation T-002 では類似の「実体は別ディレクトリ」パターンを採用していない（要確認）
- 案 1 採用なら T-002 完了条件に「`intake_failure_report.json` が `analysis/shared/manifests/` 配下に書き出される」を機械検証として追加""",
  },
  {
    "num": 55,
    "finding_id": "F-008",
    "judgment_text": "必ず直す（must-fix）",
    "summary": "T-001 完了条件 2「人間レビューで承認されている」が機械判定不可、本文書冒頭の規律と矛盾",
    "facts": """- tasks.md T-001 完了条件 2（行 47-48）に「README または ANALYSIS.md の人間レビューで承認されている」と記述
- 本文書冒頭の規律：「完了条件は grep ／ Read ／ JSON Schema 検証 ／ pytest 等で機械的に判定可能であること」
- foundation T-001 の同等条文には「承認の記録方法」を運用で担保する旨が注記されている（参照可能）が、analysis T-001 にはこの注記が存在しない
- 敵対役 Opus 4.7 も同意：機械判定不可で本文書冒頭の規律と直接矛盾""",
    "cases": """- **案 1**：T-001 完了条件 2 を機械判定可能な式に置換：「README または ANALYSIS.md が存在し、必須 N 節（規約／配置／インデックス等）を含む」を grep で検証
- **案 2**：foundation T-001 と同形式の注記を追加：「人間レビューでの承認は運用で担保。完了条件の機械判定は省略し、規約の存在と必須節の充足のみを機械検証」と完了条件と注記を分離""",
    "deep_analysis": """- 案 1 は機械検証を厳格化、grep で必須節の存在を検査するため自動化可能。ただし「承認」の意味は失われ、文書が存在すれば誰でも完了とできる
- 案 2 は foundation T-001 の方針を踏襲し整合性が高い。注記の明示で「承認の運用担保」を文書化、運用と機械検証の責務分離が明確
- T-001 は共通レイアウト準備で、後続タスクの基盤。完了条件が機械判定で曖昧になると、後続タスクの前提が不安定化
- 案 2 採用の場合、foundation／runtime／evaluation T-001 と analysis T-001 の整合が取れる""",
  },
  # 優先 2：3 件（A-006、F-007、F-002）
  {
    "num": 56,
    "finding_id": "A-006",
    "judgment_text": "必ず直す（must-fix）",
    "summary": "T-004 完了条件と T-004 スキーマ範囲の内部矛盾（`final_label` がスキーマに登場しない）",
    "facts": """- tasks.md T-004 完了条件（行 87）に「foundation 4 語彙（`evidence_class` ／ `review_mode` ／ `counter_status` ／ `final_label`）を再定義せず参照のみで使用」と記述
- T-004 責務記述（行 81）は `evidence_class` ／ `review_mode` の参照のみを明示
- T-004 スキーマには `final_label` が登場しない
- `final_label` は `evidence_register` のフィールドとして design.md §証拠台帳モデル §2 必須／任意区分（行 261-263）に列挙されていない
- 「再定義禁止」の検証対象が空集合になる構造""",
    "cases": """- **案 1**：T-004 完了条件から `final_label` を削除（実装と整合）。foundation 3 語彙（`evidence_class` ／ `review_mode` ／ `counter_status`）を再定義せず参照のみと記述
- **案 2**：T-004 スキーマに `final_label` を追加して整合させる。`evidence_register` の各エントリに `final_label` フィールドを必須または任意として追加""",
    "deep_analysis": """- 案 1 は実装と整合、T-004 スキーマの責務範囲を素直に表現。foundation の `final_label`（3 値）はレビュー所見の最終判定値であり、`evidence_register` の証拠管理とは目的が異なるため、参照不要との解釈は妥当
- 案 2 は `evidence_register` に `final_label` を導入する設計変更。design.md §証拠台帳モデルの再オープンが必要、要件側との整合確認も必要
- T-011 双方向整合チェック実装時、T-004 完了条件の「`final_label` 参照のみ」が機械検証されると、スキーマに `final_label` が登場しないため検証が失敗する
- 案 1 が機能内対処で済み、設計変更の波及が最小""",
  },
  {
    "num": 57,
    "finding_id": "F-007",
    "judgment_text": "必ず直す（must-fix）",
    "summary": "T-008 前提に T-004 欠落、T-007 前提に T-005 を入れない根拠不明",
    "facts": """- tasks.md T-008 前提タスク（行 136）：「T-002（取り込み）、T-003（参照書式）」のみ
- T-008 の `conformance_intake.json` スキーマ（行 141）の必須 6 項目には `maturity_label` を持たない
- T-007 前提タスク（行 124）：「T-002、T-003、T-004」が列挙、T-005（caveat_register）を含まない
- design.md §収束可視化モデル §1 の `role_diff.json` エントリには `evidence_refs` フィールドがあり、証拠台帳への参照が必要になる可能性
- 敵対役 Opus 4.7：T-008 で `source_artifact_refs` を経由するなら T-004 完了が必要""",
    "cases": """- **案 1**：T-008 前提に T-004（証拠台帳）を追加。T-007 前提に T-005（caveat_register）を追加。両方とも前提を完全化
- **案 2**：T-008 前提は現状維持（`maturity_label` 不要のため T-004 不要）、T-007 前提に「T-005 不要根拠」を本文に明示（`role_diff.json` は `evidence_refs` を経由しないため）""",
    "deep_analysis": """- 案 1 は前提行を厚くする方向。実装者が依存閉包を即座に把握できる利点があるが、過剰前提による並列実装の阻害も
- 案 2 は前提行は現状の依存閉包に絞り、本文で前提除外の根拠を明示。設計判断の透明性が高い
- T-008 の `conformance_intake.json` は判定不干渉が責務で、`maturity_label` は本機能の証拠台帳側の概念。T-004 を前提に入れない判断は設計上正当
- T-007 の `role_diff.json` で `evidence_refs` を扱うかは design.md §収束可視化モデル §1 の規定次第。設計を再確認して T-005 不要の根拠を文書化するのが筋""",
  },
  {
    "num": 58,
    "finding_id": "F-002",
    "judgment_text": "必ず直す（must-fix）",
    "summary": "Req 2 受入 2／3／4／5 が追跡表に個別示されない、T-006 で一括記載",
    "facts": """- tasks.md 要件追跡表（行 189）の Req 2 行は T-006／T-010 の 2 行に束ねられている
- T-006 の対応要件欄（行 107）は「Req 2 受入 1〜5」と一括記載
- requirements.md §Requirement 2 受入 2〜5 はそれぞれに具体的な合否判定基準が存在
- 受入 2：`evaluation` 出力への来歴連結の要求
- 受入 3：分析向け成果物を生証拠と `evaluation` 出力から分離して保持
- 受入 4：再生成支援
- 受入 5：書式都合によるスキーマ変更強制禁止
- 受入基準粒度のトレーサビリティが失われている""",
    "cases": """- **案 1**：要件追跡表の T-006 行を Req 2 受入別に 4 行に分解。各受入の担当成果物（`source_artifact_refs` ／ `derivation_contract_version` ／ `fragment_builder.py` 等）を個別に明記
- **案 2**：T-006 責務文の中で「受入 1 ＝ 図表束、受入 2 ＝ 来歴連結、受入 3 ＝ 分離保持、受入 4 ＝ 再生成支援、受入 5 ＝ スキーマ変更禁止」と受入別の担当成果物を明示。追跡表行は現状維持""",
    "deep_analysis": """- 案 1 は追跡表の機械検証性を高める。T-011 双方向整合テストで受入別の担当タスクが個別に検出可能
- 案 2 は責務文を厚くし、追跡表行はコンパクト。閲覧時の見やすさは案 2 の方が高いが、機械検証の精度は案 1 の方が高い
- foundation／runtime／evaluation tasks の追跡表は受入別個別行と一括行が混在。案 1 採用の場合、他機能との整合性確認が必要
- 受入 5（書式都合によるスキーマ変更強制禁止）は派生方針版管理（T-009 の `derivation_contract_version`）と直結。追跡表の Req 2 行に T-009 を含めるか、別系統で扱うかも論点""",
  },
  # 優先 3：3 件（A-002、A-003、A-008）
  {
    "num": 59,
    "finding_id": "A-002",
    "judgment_text": "必ず直す（must-fix）",
    "summary": "T-007 完了条件「`evaluation` のメトリクス契約を上書きしないことが構造的に保証される」の機械検証手順未定義",
    "facts": """- tasks.md T-007 完了条件（行 130）に「本機能の可視化結果が `evaluation` のメトリクス契約を上書きしないことが構造的に保証される」
- 「構造的に保証される」は形容的で具体的判定不能
- design.md 判断 7（行 675-677）も同様に曖昧
- 何を測定すれば「上書きしない」と判定できるかの基準が不在
- 候補となる機械検証手法：差分集合の禁止リスト ／ 書き込み先パス検査 ／ スキーマ重複検出""",
    "cases": """- **案 1**：T-007 完了条件に「書き込み先パスが `analysis/destinations/` 配下に限定されること」と「`evaluation` 配下への書き込みがないこと」を grep または AST 検査で機械検証を明記
- **案 2**：T-007 完了条件に「`evaluation` のメトリクス契約に対応するスキーマフィールドを本機能の `role_diff.json` ／ `mode_diff.json` が再定義していないこと」をスキーマ重複検査として機械検証を明記""",
    "deep_analysis": """- 案 1 は書き込み先パス検査で実装が単純。CI に組み込みやすい
- 案 2 はスキーマ重複検査で意味的な不干渉を担保。実装はやや複雑だが、Req 4 受入 4「判定不干渉」の本質を捉える
- 両案併記も可能（書き込み先 ＋ スキーマ重複の二段検査）
- T-011 双方向整合テストでも同等検査を実装する可能性。案 1 ／ 案 2 と T-011 の責務分担が論点""",
  },
  {
    "num": 60,
    "finding_id": "A-003",
    "judgment_text": "必ず直す（must-fix）",
    "summary": "T-005／T-009 の `caveat_register` 書き戻し方向に責務分離なく循環参照可能性",
    "facts": """- tasks.md T-005 成果物（行 99）：`analysis/caveat_register/mixed_review_mode_detector.py`
- T-009 完了条件（行 151）：「`mixed_review_mode` 検知時は `caveat_register` に自動付与（T-005 と連動）」
- 「連動」の方向（T-009 が書き手 ／ T-005 が読み手）が不明
- design.md §証拠台帳モデル §3 受入 4（行 274-278）：「派生段（destination deriver）が検知主体」
- T-005 → T-009 → T-005 の循環参照になりうる
- 書き戻し方向（追加のみ ／ 上書き不可）が責務として未分離""",
    "cases": """- **案 1**：T-005 責務に「`mixed_review_mode_detector` を提供（書き戻し責任は T-009 が持つ）」と明記。T-009 完了条件に「`caveat_register` への書き込みは追加のみで上書き禁止」を機械検証として追加
- **案 2**：T-009 が detector も含めて全責任を持ち、T-005 から `mixed_review_mode_detector.py` を移動。T-005 は注意点台帳の構造定義のみに集中し責務を完全分離""",
    "deep_analysis": """- 案 1 は T-005 が detector ロジックを提供、T-009 が呼び出し ＋ 書き戻し。design.md §305 の「派生段が検知主体」と整合
- 案 2 は責務を完全分離。T-005 が構造、T-009 が検知 ＋ 書き戻し。実装の依存関係は単純になるが、`mixed_review_mode_detector.py` を T-009 配下に置く違和感
- 案 1 の方が design.md §305 の規定に近い。「detector の所有」と「呼び出し」は別概念で、所有が T-005 で構造的にも妥当
- 書き戻しが「追加のみ ／ 上書き禁止」を機械検証する手段（JSON ファイルの差分検査、append-only モードでの書き込み等）の明示が必要""",
  },
  {
    "num": 61,
    "finding_id": "A-008",
    "judgment_text": "必ず直す（must-fix）",
    "summary": "T-008 完了条件「必須 6 項目」と design.md 行 630「必須 9 件」の関係が混同を招く",
    "facts": """- tasks.md T-008 完了条件（行 144）：`conformance_intake.json` の必須 6 項目
- design.md 行 630：`conformance-evaluation` 設計 §14.5 の必須 9 件（取り込み元データ）
- 6 項目は本機能の取り込み成果物スキーマ
- 9 件は元データ（`conformance-evaluation` 側）のスキーマ
- 数の食い違いの説明が両文書に欠落""",
    "cases": """- **案 1**：T-008 完了条件に「`conformance_intake.json` の必須 6 項目と上流 `conformance-evaluation §14.5` の必須 9 件の対応マッピング」を明示記述。例：「9 件のうち集約後 6 項目に統合される」「3 件は集約過程で別フィールドへ統合」など
- **案 2**：design.md 行 626-633 の §14.5 参照節に「取り込み元 9 件 ↔ 取り込み先 6 件」の対応表を追加（design.md への軽量再オープン）""",
    "deep_analysis": """- 案 1 は機能内対処で完結、T-008 完了条件の中で対応マッピングを明示
- 案 2 は design.md への遡及（軽量再オープン）。設計文書側で対応表を持つため、複数のタスク／検証で参照可能
- 両案併記が望ましい（T-008 完了条件と design.md 参照節の両方）
- 対応マッピングの具体内容（9 件のうちどれが集約されるか）は本実験では詳細不明、別途設計確認が必要""",
  },
  # 優先 4：2 件（F-011、A-004）
  {
    "num": 62,
    "finding_id": "F-011",
    "judgment_text": "必ず直す（must-fix）",
    "summary": "T-011 のテストファイル 10 件に「無声昇格検出」の統合版が割り当てられていない",
    "facts": """- tasks.md T-011（行 175-183）のテストファイル一覧 10 件
- design.md §テスト戦略 §2（行 726-733）「無声昇格の検出」：`shared/evidence_register.json` の `maturity_label` と `evidence_class` を取得し束縛規則表と照合
- T-004 完了条件（行 87）でも束縛規則検証を扱い、二層検証の意図が読み取れる
- T-011 のどのテストファイルが統合版を担うか不明確（`test_evidence_register.py` か `test_traceability.py` か）
- evaluation T-011 は `test_integration_pipeline.py` ／ `test_downstream_interface.py` で経路統合検証を T-003 単体と二層とする意図を明示していた""",
    "cases": """- **案 1**：T-011 テストファイル一覧の `test_evidence_register.py` 担務に「無声昇格検出統合版（design.md §テスト戦略 §2 由来）」を明記。T-004 単体テストと T-011 統合テストの二層意図を T-011 責務文に明示
- **案 2**：T-011 に専用テストファイル `test_maturity_label_promotion.py` を追加し、無声昇格検出に特化したテストとして配置""",
    "deep_analysis": """- 案 1 はテストファイル数を増やさず、既存 `test_evidence_register.py` に担務追加で完結
- 案 2 はテストファイルが 1 件増えるが、無声昇格検出の責務が分離され可読性が高い
- 無声昇格検出は `evidence_register.json` の検査が中心、`test_evidence_register.py` に集約する方が責務一貫性は高い
- T-011 の現在のテストファイル数（10 件）が方針として固定されているかどうかが論点""",
  },
  {
    "num": 63,
    "finding_id": "A-004",
    "judgment_text": "必ず直す（must-fix）",
    "summary": "T-003 単体テストと T-011 統合テストの「証拠追跡性」責務分担（境界／重複／包含）未定義",
    "facts": """- tasks.md design.md テスト戦略「証拠追跡性の機械検証」は T-003 ／ T-011 連携
- T-003 完了条件：「`supporting_artifact_refs` の構造化参照が `evaluation` の成果物配置に対して機械的に解決できる」
- T-011 のテストファイル一覧（行 181）に `test_traceability.py` が独立して挙げられている
- T-003 で既に解決可能性検証がある場合、T-011 は何を追加するのか不明
- 二重実装または抜けの両方が起こりうる""",
    "cases": """- **案 1**：T-011 責務文に「T-003 単体テストは個別 finding の参照解決可能性、T-011 統合テスト（`test_traceability.py`）は全証拠の追跡経路を通すスモーク」と責務境界明示
- **案 2**：T-003 と T-011 の責務を統合し、`test_traceability.py` を T-003 配下に移動。T-011 から `test_traceability.py` を削除""",
    "deep_analysis": """- 案 1 は二層検証（単体 ＋ 統合）の意図を明示。foundation／evaluation T-011 と同型の責務分担
- 案 2 は T-011 のテストファイル数が減るが、統合段の証拠追跡テストが消える。実装段で経路統合の検証が困難になる可能性
- 案 1 採用なら T-003 単体テストの粒度（finding 単位）と T-011 統合テストの粒度（全証拠の一括検証）の差別化が機械検証の信頼性を高める""",
  },
  # ===== should-fix 12 件（機能内対処）=====
  {
    "num": 64,
    "finding_id": "F-001",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "Req 1 受入 2／3 が要件追跡表に個別エントリで現れない、受入基準粒度のトレーサビリティ欠落",
    "facts": """- tasks.md 要件追跡表 行 185-196 で Requirement 1 受入 2（実行と分析の来歴を保持する）と受入 3（直接証拠と注意点付き証拠を区別する）が追跡表の個別エントリとして現れない
- T-004 で design §証拠台帳モデル §2（来歴フィールド）と §1（maturity_label）を扱っている
- 追跡表の T-004 欄は「受入 1〜3 ／ 5」と括られている
- 受入 2・受入 3 の個別担当タスクが特定できない""",
    "cases": """- **案 1**：要件追跡表 Req 1 行を受入別に個別行に分解。受入 2 ＝ T-004（来歴フィールド）、受入 3 ＝ T-004（証拠区別）、受入 5 ＝ T-004／T-005（注意点付き証拠）を個別に明記
- **案 2**：T-004 責務文の中で「受入 1 ＝ maturity_label、受入 2 ＝ 来歴、受入 3 ＝ 証拠区別、受入 5 ＝ caveat 参照」と受入別の担当を明示。追跡表行は現状維持""",
    "deep_analysis": """- 案 1 は追跡表の機械検証性を高め、T-011 双方向整合テストで受入別の担当タスクが個別に検出可能
- 案 2 は責務文で説明、追跡表行はコンパクトなまま
- 影響度は中程度（must-fix の F-002 と同型問題の小規模版）""",
  },
  {
    "num": 65,
    "finding_id": "F-003",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "Req 3 受入 1／3／4 が T-005 追跡表行で個別現れない",
    "facts": """- tasks.md 要件追跡表 行 190 で Requirement 3 受入 1（証拠源に関連する注意点メタデータの保持）／受入 3（手作業で読み直さずに注意点参照）／受入 4（予備ラベル付与の支援）が追跡表の T-005 に対応付けされていない
- T-005 の「対応要件」欄は「Requirement 3 受入 1〜5」と記載
- 追跡表欄は「T-005（caveat_register、4 値 limitation_type）」のみ
- 受入基準粒度の根拠が示されない""",
    "cases": """- **案 1**：要件追跡表 Req 3 行を受入別に個別行に分解。受入 1／3／4 を T-005 に個別マッピング
- **案 2**：T-005 責務文の中で「受入 1 ＝ caveat メタデータ、受入 3 ＝ 参照機構、受入 4 ＝ 予備ラベル支援」と受入別の担当を明示""",
    "deep_analysis": """- F-001 と同型問題、Req 3 版。同じ判断方針が望ましい
- 案 1 採用なら F-001 と整合性が高い""",
  },
  {
    "num": 66,
    "finding_id": "F-005",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "T-001 成果物に `shared/conformance/` ／ `shared/convergence/` ／ `shared/manifests/` のサブディレクトリ列挙が欠落",
    "facts": """- tasks.md T-001（行 33-50）成果物欄に `shared/` 配下サブディレクトリ未列挙
- T-001 責務文（行 37）は「5 サブディレクトリ（`conformance/` ／ `convergence/` ／ `manifests/`、加えて直下 3 ファイル）」と列挙
- 成果物欄（行 40-45）に README が列挙されない
- foundation T-001 ／ evaluation T-001 の方針継承をうたいながら、`shared/` 配下の全サブディレクトリが T-001 の責務範囲として明示されていない""",
    "cases": """- **案 1**：T-001 成果物欄に `analysis/shared/conformance/README.md` ／ `analysis/shared/convergence/README.md` ／ `analysis/shared/manifests/README.md` を追加
- **案 2**：T-001 責務文の最後に「`shared/conformance/` ／ `shared/convergence/` ／ `shared/manifests/` のディレクトリ作成も含む」と明示し、成果物欄は現状維持""",
    "deep_analysis": """- 案 1 は配置宣言の明示性を高め、機械検証時の網羅性が向上
- 案 2 は成果物欄はコンパクト、責務文で補足
- foundation T-001 の方針との整合性は案 1 の方が高い（README 配置を成果物として明示する慣行）""",
  },
  {
    "num": 67,
    "finding_id": "F-009",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "T-002 の「`runtime` 生証拠の一次参照経路が存在しないことが機械検証される」の機械的判定手段が曖昧",
    "facts": """- tasks.md T-002 完了条件（行 61）：「`runtime` 生証拠の一次参照経路が存在しないことが機械検証される」
- T-002 テスト要件（行 62）：「`runtime` 生証拠への一次参照がないことの構造検査」
- 「構造検査」の具体的手法を示していない
- 候補手法：grep ／ AST 解析 ／ インポート検査
- evaluation T-004 では同種の「参照のみ使用の機械検証」を具体的手法（foundation 語彙ハッシュ照合）で明示している""",
    "cases": """- **案 1**：T-002 テスト要件に「`experiments/runtime/` 配下の文字列が成果物コードに登場しないことを grep で検査」を明示
- **案 2**：T-002 テスト要件に「Python AST 解析で `experiments/runtime/` を含む文字列リテラルやファイルパスの import を検出する」を明示（より厳密だが実装複雑）""",
    "deep_analysis": """- 案 1 は実装が単純、grep のみで完結
- 案 2 はより厳密だが実装複雑、CI 時間が長くなる可能性
- evaluation T-004 が grep 系を採用しているなら、案 1 の方が整合性が高い""",
  },
  {
    "num": 68,
    "finding_id": "F-010",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "T-009 「`derivation_contract_version` の更新が `superseded` 履歴と整合」の機械判定方法不明",
    "facts": """- tasks.md T-009 完了条件（行 160）：「`derivation_contract_version` の更新が `superseded` 履歴と整合」
- 「整合」の機械判定方法が示されていない
- `superseded` 履歴がどのファイル・フィールドを指すか不明（`manifest.yaml` の特定フィールドか、別ファイルか）
- design.md §出力先別の派生モデル §1（行 435）：「派生方針が変わった場合は `derivation_contract_version` を更新し、過去の派生成果物は `superseded` として保持する」
- `superseded` を表現するスキーマ定義が T-009 成果物に含まれていない""",
    "cases": """- **案 1**：T-009 完了条件に「`derivation_contract_version` の前版 ref が `manifest.yaml` の `superseded_versions` フィールドに記録され、版番号が単調増加することを機械検証」を明示
- **案 2**：T-009 成果物に専用ファイル `derivation_version_history.json` を追加し、版変更履歴を独立に管理。`manifest.yaml` から参照する 2 ファイル構成""",
    "deep_analysis": """- 案 1 は manifest 単一ファイル方式、構造単純
- 案 2 は履歴管理を分離、版数増加に応じて履歴ファイルが肥大化する場合に有利
- 派生方針の変更頻度が低いと想定すれば案 1 で十分""",
  },
  {
    "num": 69,
    "finding_id": "F-012",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "混在レビューモード検知の統合テスト集約先（`test_destinations.py` か `test_caveat_register.py` か）が不明確",
    "facts": """- tasks.md design.md §テスト戦略 §3（行 735-738）「混在レビューモードの注意点検証」：T-005 ／ T-009 ／ T-011 の 3 タスク連携
- T-011 成果物ファイル列（行 181）に `test_destinations.py` は含まれている
- 混在検知（T-009 の `review_mode_mixed` フィールドと T-005 の自動付与の連動）を統合的に検証するテストファイルが `test_destinations.py` に集約されるか `test_caveat_register.py` に分散するか不明
- T-009 テスト要件（行 161）では「`review_mode_mixed` 検知時の `caveat_register` 自動付与テスト（T-005 連動）」と書かれており、T-009 単体でも当該テストが走る""",
    "cases": """- **案 1**：T-011 責務文に「混在レビューモード検知の統合テストは `test_destinations.py` で実施、T-009 単体テストとの責務分担：単体は付与ロジック、統合は出力先全体での一貫性」と明示
- **案 2**：T-011 のテストファイル一覧に専用 `test_mixed_review_mode_integration.py` を追加し、混在検知の統合テストを分離""",
    "deep_analysis": """- 案 1 は既存 `test_destinations.py` への責務追加で完結
- 案 2 はテストファイル数が増えるが、混在検知の責務が明示的に分離
- F-011 と類似の判断構造、整合性のある決定が望ましい""",
  },
  {
    "num": 70,
    "finding_id": "F-016",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "`analysis/fragments/` ディレクトリが design.md の配置ツリーに存在しない",
    "facts": """- tasks.md T-006 成果物（行 109-115）：`analysis/fragments/fragment.schema.json` ／ `analysis/fragments/fragment_builder.py`
- design.md §分析向け成果物配置（行 103-141）に `analysis/fragments/` ディレクトリが存在しない
- `figures_tables/` は存在するが `fragments/` は省略または未定義""",
    "cases": """- **案 1**：design.md §分析向け成果物配置ツリー（行 102-141）に `analysis/fragments/` ディレクトリを追加（軽量再オープン）
- **案 2**：T-006 成果物の `fragments/` を `figures_tables/fragments/` に移動し、既存ディレクトリツリー内に配置（tasks.md のみ修正）""",
    "deep_analysis": """- 案 1 は design.md への遡及（軽量再オープン）が必要だが、設計の表現の正確性が向上
- 案 2 は tasks.md のみ修正で完結、設計変更不要
- 報告断片（fragment）は図表束（figures_tables）と兄弟関係であって従属関係でないとすれば、案 1 の方が責務階層を正しく表現""",
  },
  {
    "num": 71,
    "finding_id": "A-007",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "T-006 の報告断片の `text_stub`／`applicable_destinations` の符号化が責務文に欠落",
    "facts": """- tasks.md T-006（行 103-117）は「図表束」と「報告断片」の 2 つの責務領域を 1 タスクに統合
- design.md §報告断片モデルで `fragment.schema.json` の必須 6 項目（`fragment_id` ／ `fragment_type` ／ `source_artifact_refs` ／ `maturity_label` ／ `text_stub` ／ `applicable_destinations`、design.md 行 363）
- T-006 責務文は図表束の必須 5 項目を中心に記述
- `text_stub` ／ `applicable_destinations` の符号化が責務文に欠落""",
    "cases": """- **案 1**：T-006 責務文に「報告断片の必須 6 項目すべて（`fragment_id` ／ `fragment_type` ／ `source_artifact_refs` ／ `maturity_label` ／ `text_stub` ／ `applicable_destinations`）を符号化」と明示追加
- **案 2**：T-006 を「T-006a 図表束」「T-006b 報告断片」の 2 タスクに分割（粒度を細かくする）""",
    "deep_analysis": """- 案 1 は責務文を厚くする方向、tasks 数は維持
- 案 2 はタスク数が増えるが、責務分離が明確
- 一気通貫粒度方針（1 タスク ＝ 1 責務領域）からは案 2 も妥当だが、図表束と報告断片の責務領域は密接で 1 タスクに統合する判断も理解可能
- 既存方針の継承を優先するなら案 1""",
  },
  {
    "num": 72,
    "finding_id": "A-009",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "T-009 `audit_writer.py` と T-008 `derived_audit_writer.py` の `conformance_violations_detail.json` 書き手重複",
    "facts": """- tasks.md T-008（行 142）：`derived_audit_writer.py`
- T-009（行 154-158）：`audit_writer.py` 出力に `conformance_violations_detail.json` を含む
- 両者とも `destinations/audit/` 配下成果物
- design.md §`conformance-evaluation` 取り込みモデル §2（行 484-486）：T-008 が「正本の加工版を別名で配置」
- T-009 が「派生段全体」の担い手で重複""",
    "cases": """- **案 1**：T-009 の `audit_writer.py` から `conformance_violations_detail.json` を削除し、T-008 が単独所有として明示
- **案 2**：T-008 と T-009 の責務分担を T-008 ＝ 取り込み加工 ／ T-009 ＝ 派生集約として明示分離、`conformance_violations_detail.json` は両者が異なる用途で書き出す（T-008 ＝ 加工版、T-009 ＝ 集約結果）""",
    "deep_analysis": """- 案 1 は書き手単一化、責務重複の解消
- 案 2 は責務分離の明示で重複を許容、ただし出力ファイル名で区別が必要
- 「書き手単一」原則からは案 1 が筋
- `conformance_violations_detail.json` の用途を確認して、本当に 1 ファイルに集約されるべきか、複数ファイルに分かれるべきかを設計で決める必要""",
  },
  {
    "num": 73,
    "finding_id": "A-010",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "analysis 所有 4 正本（`maturity_label`／`limitation_type`／`fragment_type`／`regeneration_status`）の下流参照禁止／許容宣言が不在",
    "facts": """- tasks.md 行 27（contract consumer 原則）
- design.md 行 595-597
- T-005 ／ T-006 ／ T-010 が新規確定する正本：`maturity_label` 3 値 ／ `limitation_type` 4 値 ／ `fragment_type` 5 値 ／ `regeneration_status` 4 値
- 下流機能（`self-improvement`）が参照禁止かどうかの宣言が tasks.md にも design.md にも不在
- foundation 判断 7 と同型の「下流参照禁止」明示がない""",
    "cases": """- **案 1**：design.md の analysis 所有 4 正本節に「下流機能（`self-improvement`）は再定義禁止で参照のみ使用」を明示追加（design.md 軽量再オープン）
- **案 2**：tasks.md の T-005 ／ T-006 ／ T-010 完了条件に下流参照禁止を明示し、design.md への波及は次フェーズで処理""",
    "deep_analysis": """- 案 1 は設計文書側で正本所有規律を明示、tasks 側は参照のみ
- 案 2 は tasks 側で完結、設計変更不要
- foundation の正本所有規律と同型の表現を維持するなら案 1
- analysis は最下流に近く下流参照は限定的だが、`self-improvement` 等への明示宣言は望ましい""",
  },
  {
    "num": 74,
    "finding_id": "A-011",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "Req 4 受入 5（下流叙述変換の明示・版管理）が追跡表で個別行不在",
    "facts": """- tasks.md 行 192（追跡表 Req 4 行）：「受入 1〜3 ＝逆流禁止」「受入 4 ＝判定不干渉」と分解
- 受入 5（「下流の叙述変換を明示的かつ版管理可能とする」）が分解されないまま T-002 ／ T-008 に対応付け
- 受入 5 は T-009 の `derivation_contract_version` の版管理が実装担当のはず
- requirements.md 行 84 の受入 5 は T-009 の派生方針版管理（design.md 行 422）に対応""",
    "cases": """- **案 1**：要件追跡表 Req 4 行に受入 5 ＝ T-009（`derivation_contract_version`／`manifest.yaml`）を個別に追加
- **案 2**：受入 5 を Req 4 から独立させ、別 Req 行として追跡表に追加（受入基準の独立性を高める）""",
    "deep_analysis": """- 案 1 は追跡表の Req 4 行に T-009 を追加するシンプルな修正
- 案 2 は受入 5 の独立性を高めるが、追跡表の構造が大きく変わる
- F-001 ／ F-003 と同型問題、案 1 の判断と整合性を取るのが望ましい""",
  },
  {
    "num": 75,
    "finding_id": "A-012",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "T-010 「再生成対象の登録条件 3 件が機械検証される」の検出機構（poll／hook／timestamp 比較）未定義",
    "facts": """- tasks.md T-010 完了条件（行 172）：「再生成対象の登録条件 3 件が機械検証される」
- 3 件のそれぞれの発火条件：`evaluation` の `staleness_register.json` 新規エントリ ／ 依存成果物の `stale` 変化 ／ `conformance-evaluation` 検査結果の更新
- 検出方法（poll／hook／timestamp 比較）が未定義
- design.md 行 581-587 も同様に列挙のみで検出機構を実装に委ねている""",
    "cases": """- **案 1**：T-010 完了条件に「timestamp 比較ベースの検出機構（再生成側成果物の生成時刻が入力側成果物の最終更新時刻より古い場合に登録）」を明示
- **案 2**：T-010 完了条件に「hash 比較ベースの検出機構（入力側成果物の hash 変化を検知して登録）」を明示""",
    "deep_analysis": """- 案 1（timestamp）は実装が単純、CI で動かしやすい。クロック差で誤検出のリスク
- 案 2（hash）は厳密だが実装複雑、hash 計算コスト発生
- 一気通貫検証の規模が小さければ案 1 で十分
- 両案併記（基本は timestamp、必要なら hash）も可能""",
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
