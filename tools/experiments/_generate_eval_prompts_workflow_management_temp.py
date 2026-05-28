"""tools/experiments/_generate_eval_prompts_workflow_management_temp.py

workflow-management tasks の 7 モデル比較実験用プロンプト（topic-76〜topic-98、23 件）を生成する一時スクリプト。
セッション 38（2026-05-28）の workflow-management tasks 7 モデル比較実験で使用、後で削除予定。

各 topic は次の構造（analysis topic-53〜75 と同形式）：
- 文脈（共通、workflow-management 用）
- 判定対象：所見番号と判定
- 概要 ／ 事実 ／ 候補案 ／ 深掘り
- あなたへの依頼 ／ 対話の進め方 ／ 出力形式

内容の出典：workflow-management tasks 段の 3 役 triad-review（セッション 37、ID 3e297d96）の生ログ
- 主役レビュー（Sonnet 4.6、20 件、F-001〜F-020）
- 敵対役レビュー（Opus 4.7、10 件、A-001〜A-010、counter_status 含む）
- 判定役レビュー（Opus 4.7、30 件統合判定、must-fix 9／should-fix 17／leave-as-is 4）

実験対象：機能内 must-fix 6 件（F-006／F-008／F-009／F-012／F-015／A-004）＋ should-fix 17 件 ＝ 23 件。
遡及 2 件（A-001／A-003）と波及 1 件（A-002＝pending-cross-feature-findings A-019）は再オープン処理／持ち越しで別途対処済みのため本実験対象から除外。
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
- **判定役**：提案役と反論役の全所見（合計で 10〜30 件程度）を一括で読み、各所見について次の 2 つを決める。(1) 修正必要性の判定：「必ず直す（must-fix）」「直した方がよい（should-fix）」「直さなくてよい（leave-as-is）」の 3 段階に分類。(2) 波及種別の判定：「機能内対処（当該文書だけ直せばよい）」「波及（他機能の文書にも影響する）」「遡及（上流の文書を直す必要がある）」「延期（将来の段階で対処）」のいずれかに分類。判定役は「採否と影響範囲を決める」立場で、利用者と議論すべき重要な所見を明示する

現在、workflow-management（仕様駆動開発のワークフロー自体を管理する機能。各段階の段集合を YAML で静的定義し、不可逆操作（仕様の承認書き込み・コミット・プッシュ・段階移行）の事前検査スクリプト、やり直し（再オープン）手続きの機械強制、機能依存マップの管理などを担う）の「設計を実装作業に分解する段階（tasks 段）」で 3 役レビューが完了しました。判定役は所見 30 件を判定し、「必ず直す」9 件・「直した方がよい」17 件・「直さなくてよい」4 件と分類しました。

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
  # ===== 機能内 must-fix 6 件（F-006／F-008／F-009／F-012／F-015／A-004）=====
  {
    "num": 76,
    "finding_id": "F-006",
    "judgment_text": "必ず直す（must-fix）",
    "summary": "T-007（reopen 機械強制）の前提タスクに T-005（front-matter 検査）が欠落しており、やり直し解決器が「起草者と判定者の分離」の述語を呼べない依存順の穴がある",
    "facts": """- tasks.md T-007 の前提タスク（L154）は「T-003、T-004、T-006」で、T-005（front_matter_checker）が含まれない
- T-007 の責務（L153）：`actor_resolution: per_target_stage` で各段の担当者（actor）を動的に解決し、`actor=human` の段で停止する仕組みを実装する
- 再実施対象の段が triad-review 段を含む場合、その完了判定述語は `artifact_exists_and_sections_present_and_author_reviewer_distinct`（起草者と判定者が別人であることを含む）であり、T-005 の front_matter_checker.py を内部から呼ぶ必要がある（design.md §reopen 機械強制モデル §2、§起草者と判定者の分離モデル §1）
- T-005 が未完了のまま T-007 を実装すると、この述語の判定が実行時に不成立になる
- 反論役（敵対役）も同型の依存欠落を独立に指摘""",
    "cases": """- **案 1**：T-007 の前提タスクに T-005 を追加し、「T-003／T-004／T-005／T-006」とする。依存閉包を前提表に明示し、実装順（T-005 → T-007）を機械的に保証する
- **案 2**：前提タスク欄は現状維持とし、T-007 の本文に「述語 `..._author_reviewer_distinct` の判定は T-005 の front_matter_checker に委譲する。T-005 未完了時は当該段を結論不能（DEVIATION）として扱う」と依存経路を注記する（実行時のフォールバックで安全性を担保）""",
    "deep_analysis": """- 関連所見 F-007（T-008 の前提に T-007 が欠落）と合わせると、T-005 → T-007 → T-008 の依存チェーンが前提表の上で切断されており、実装順を正しく保証できていない
- 案 1 は前提表で依存閉包を明示するため実装者が依存を即座に把握できるが、T-007 の着手が T-005 完了まで遅れ、並列実装の自由度が下がる
- 案 2 は前提表を最小に保ち、実行時の DEVIATION で安全性を担保するが、実装順の静的な保証は弱くなる
- 依存関係そのものは上流 design に由来するため、tasks.md の修正のみで吸収できる機能内対処""",
  },
  {
    "num": 77,
    "finding_id": "F-008",
    "judgment_text": "必ず直す（must-fix）",
    "summary": "T-010 の前提タスク「T-003（cross-spec-alignment.yaml または別途 discipline-update.yaml の枠）」が二択の曖昧表記で、着手可能かどうかを機械的に確定できない",
    "facts": """- tasks.md T-010 の前提タスク（L203）：「T-003（`stages/cross-spec-alignment.yaml` または別途 `stages/discipline-update.yaml` の枠）、T-004」
- 規律変更の手続き用に、既存の cross-spec-alignment.yaml を流用するか、新規に discipline-update.yaml を作るかが未確定のまま、前提タスクに「または」という分岐が埋め込まれている
- DVT-W003（L317、宿題項目）で「後続セッションで段集合を確定」と整理されているが、前提が「または」表記だと、T-003 が完了していても T-010 が着手可能かを人手で判断する必要が残る
- tasks.md 冒頭の方針（L26）は「着手可能性を機械的に判定可能とする」""",
    "cases": """- **案 1**：規律変更専用に `stages/discipline-update.yaml` を新設する方に確定する。T-010 の前提を「T-003（discipline-update.yaml の枠）、T-004」に一意化し、DVT-W003 と整合させる
- **案 2**：既存の `stages/cross-spec-alignment.yaml`（機能横断整合用）を流用する方に確定する。別途新設はせず、T-010 の前提を「T-003（cross-spec-alignment.yaml）、T-004」に一意化する""",
    "deep_analysis": """- どちらに確定しても、段集合の本体は DVT-W003 で後続セッションに確定が委ねられる（枠だけ先に決める）
- 案 1（専用ファイル新設）は規律変更の責務を独立したファイルに分離でき可読性が高いが、stages/ 配下の YAML ファイルが 1 つ増える
- 案 2（流用）はファイル数を抑えられるが、機能横断整合用のファイルに規律変更の責務を相乗りさせるため、ファイルの責務が混在する
- T-010 は self-improvement の approved-updates 経路（git mv で受け取る）と接合する。この接合面のスキーマ整合（持ち越し所見 A-019）とも関連するため、どちらのファイルに置くかは self-improvement との境界設計にも影響する""",
  },
  {
    "num": 78,
    "finding_id": "F-009",
    "judgment_text": "必ず直す（must-fix）",
    "summary": "T-005 の完了条件 3「DVT（宿題項目）に登録する」が人手判断の作業であり、機械検証する手段がなく、文書冒頭の「完了条件は機械判定可能」という方針に違反している",
    "facts": """- tasks.md T-005 完了条件 3（L131）：「既存レビュー記録 7 件以上に本検査を走らせ、grandfathering（既存分の救済）を採るか別途判断する論点を DVT に登録（DVT-W002）」
- tasks.md 冒頭の方針（L26）：完了条件は grep ／ Read ／ JSON Schema 検証 ／ pytest 等で「機械的に判定可能」とする
- 「DVT に登録する」という行為の完了を機械検証する手段（DVT 表に該当行が存在することを grep で確認する等）が記述されていない
- 「grandfathering を採るか」は利用者承認を要する判断事項であり、実装作業と判断作業が 1 つの完了条件に混在している""",
    "cases": """- **案 1**：完了条件 3 から人手判断の部分を分離し、「DVT-W002 のエントリが DVT 表に存在することを grep で確認する」という機械判定可能な記述に置き換える（判断そのものは DVT 項目として残す）
- **案 2**：完了条件 3 を完全に削除し、grandfathering の是非判断は完了条件ではなく DVT 管理項目（別表）として扱う。T-005 の完了条件は検査スクリプトの実装と単体テストのみに絞る""",
    "deep_analysis": """- 関連所見 A-007（grandfathering 判断の責務帰属の曖昧さ、同根問題）と連動する。両者を整合した方針で処理するのが自然
- 案 1 は DVT エントリの存在を機械検証することで方針違反を解消しつつ、論点を記録に残せる
- 案 2 は完了条件から判断を完全に排除でき、よりクリーンだが、grandfathering の追跡先が別表に移る
- fail-closed（安全側に倒す）方針の下では、grandfathering 未確定のまま検査を走らせると既存 7 件が DEVIATION を返し、本機能自身のコミットゲートが全停止する自己ロックのリスクがある（A-007 で詳述）""",
  },
  {
    "num": 79,
    "finding_id": "F-012",
    "judgment_text": "必ず直す（must-fix）",
    "summary": "T-010 は self-improvement が git mv で配置する YAML を入力経路とするが、その外部依存のモック／スタブ化がテスト要件・成果物のどちらにも書かれておらず、統合テストが実行不能になる穴がある",
    "facts": """- tasks.md T-010 完了条件 2（L212）：「self-improvement から `git mv` で配置された YAML を本機能が読み、所定手続きを経て規律ファイルの実体変更を完了する」という外部依存を持つ統合フローを要求
- tasks.md T-011 のテスト継承記述（L274）：「統合テスト → T-006 ／ T-007 ／ T-010 個別」
- self-improvement との境界（git mv によるファイル投入）をどうモック化・スタブ化するかが、T-010 の成果物・テスト要件（L214）のどちらにも記述されていない
- このため T-010 の統合テストを単体で実行できるかが不明""",
    "cases": """- **案 1**：T-010 のテスト要件・成果物に「git mv 外部依存をモック／スタブ化した統合テスト（approved-updates/ ディレクトリへの YAML 投入を擬似的に再現）」を追加する
- **案 2**：git mv をモックする統合テストは T-011（統合テスト集約タスク）に集約し、T-010 は単体テストのみを持つ。機能境界をまたぐテストの所有を T-011 に一元化する""",
    "deep_analysis": """- 持ち越し所見 A-019（T-010 の approved_update スキーマが self-improvement §8.4 正本と不一致）と関連する。スキーマ整合が取れてからモックの中身（擬似 YAML の形）が確定する依存がある
- 案 1 は T-010 内でテストが完結し、テストの所有が明確
- 案 2 は機能境界をまたぐ統合テストを T-011 に集約でき、self-improvement 側（producer 側）のテストとの二重実装を避けやすい
- どちらでも、self-improvement 側のテスト責務との分担を明確にする調整が必要""",
  },
  {
    "num": 80,
    "finding_id": "F-015",
    "judgment_text": "必ず直す（must-fix）",
    "summary": "T-003 の `stage_schema.json`（段集合 YAML の共通スキーマ）の完了条件に、完了判定述語（completion_predicate）の値域 7 値のバリデーションが明示されておらず、T-004 での実装漏れリスクを生む",
    "facts": """- design.md §軽量版検査スクリプトモデル §3（L271-284）：`completion_predicate` の値域は 7 値（`artifact_exists` 等）に確定しており、それ以外の値は fail-closed（DEVIATION）とする方針が設計判断 3 に基づいて定められている
- tasks.md T-003 は `stage_schema.json` を成果物に持つ（L89）が、完了条件（L91-95）に「`completion_predicate` を 7 値に値域制限すること、7 値以外が DEVIATION を引き起こすこと」の機械検証が欠落している
- この漏れは T-004 実装時に `stage_schema.json` の値域チェックが見落とされるリスクを生む""",
    "cases": """- **案 1**：T-003 の完了条件に「`stage_schema.json` が `completion_predicate` を 7 値（`artifact_exists` 等）に値域制限（enum）し、JSON Schema 検証でそれ以外の値を弾くこと」を追加する（スキーマ層で値域を縛る）
- **案 2**：値域チェックの責務は T-004（predicates.py の実装）に集約する。T-003 の `stage_schema.json` は 7 値の enum 列挙のみとし、機械検証の完了条件は T-004 側に明示する（実装層で検査する）""",
    "deep_analysis": """- 関連所見 A-004（actor の値域に proxy_model が欠落）と同型の「値域の機械検査漏れ」問題であり、整合した方針が望ましい
- 案 1 はスキーマ層で値域を宣言的に縛るため、T-004 の実装漏れに強い
- 案 2 は predicates.py（実装層）に検査を集約し、スキーマは enum 宣言のみとする。二層で重複しない代わりに、スキーマ単独では値域を保証しない
- T-004（述語の実装）と T-003（スキーマ）の責務分担をどう引くかが核心""",
  },
  {
    "num": 81,
    "finding_id": "A-004",
    "judgment_text": "必ず直す（must-fix）",
    "summary": "design は段の担当者（actor）の値域を 3 値（human／llm／proxy_model）とするが、tasks.md は 2 値（human／llm）しか扱わず、スキーマの値域検査・テストに proxy_model（代理モデルによる承認）が一切現れない",
    "facts": """- design.md §段集合 §1（L125）・approval 段の例（L186-190）・§3（L359）：actor の値域は `human` ／ `llm` ／ `proxy_model` の 3 値
- design.md L455：reopen 連鎖で「参照先段の actor が `proxy_model`：`reviewcompass.yaml#human_proxy.proxy_allowed` の許可条件を満たす場合のみ代行」と機械判定経路を要求
- tasks.md：`stage_schema.json`（L89）の actor 値域に proxy_model を含めず、T-005 のテスト要件（L132）の値域テストも human／llm のみ
- approval 段の完了述語 `explicit_human_approval_recorded` が proxy_model による承認をどう判定するかが未割当""",
    "cases": """- **案 1**：tasks.md（T-003 の段定義の actor 値域、T-005 の値域テスト、`stage_schema.json`）に proxy_model を追加し、design の 3 値に揃える
- **案 2**：proxy_model を含む完全対応（proxy_allowed 条件の解決ロジックを含む）は、代理承認（human_proxy）機構の実装フェーズに延期する。現フェーズは human／llm のみ実装し、proxy_model 対応を DVT に登録する""",
    "deep_analysis": """- design が actor 値域の正本なので、tasks.md を design に揃えるのは機能内対処で吸収できる
- 案 1 は値域を design に完全一致させ宣言的な整合を確保するが、proxy_allowed 条件の解決ロジックを実装するタスクが別途必要になる
- 案 2 は段階的実装で当面の範囲を絞れるが、design との値域不一致が残り、関連所見 F-015（completion_predicate の値域検査）の方針と矛盾しうる
- F-015 と同型の値域検査問題であり、整合した判断が望ましい""",
  },
  # ===== should-fix 17 件（機能内対処）=====
  {
    "num": 82,
    "finding_id": "F-001",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "要件追跡表で Requirement 1 受入 6（機能横断段 review-wave の 7 モデル比較実験 2 回方式）の対応タスクが不完全で、段集合定義・完了述語がどこに符号化されるか追跡が切れている",
    "facts": """- requirements.md Req 1 受入 6（L49）：機能横断段 review-wave の 7 モデル比較実験 2 回方式が、受入基準として番号付きで明示されている
- tasks.md 要件追跡表（L235）：この受入の対応タスクが「T-003（cross-spec-alignment.yaml 枠）＋ T-009（運用文書）」と記載
- T-003 の責務記述（L78-96）に 7 モデル比較実験への言及はなく、cross-spec-alignment.yaml は枠のみ確保で段集合が未確定（DVT-W004）
- このため受入基準を達成する実装経路が現時点では存在しない""",
    "cases": """- **案 1**：要件追跡表の Req 1 受入 6 の行に「段集合本体は DVT-W004 で延期。cross-spec-alignment.yaml の段集合確定後に符号化する」と注記し、追跡の空白を明示する
- **案 2**：T-003 の責務に「7 モデル 2 回方式の段集合定義（cross-spec-alignment.yaml 内）」を明記し、追跡先を実体のタスクに対応付ける""",
    "deep_analysis": """- DVT-W004（cross-spec-alignment.yaml の段集合の後続確定）が前提であり、本受入の実装経路は現時点で枠のみ
- 案 1 は延期を明示して追跡の整合を保つ（実装は後続フェーズ）
- 案 2 は責務を前倒しで書くが、DVT-W004 が未解決のため記述が宙に浮くリスクがある
- 関連所見 F-002 系（追跡表の受入別粒度問題）と同系統""",
  },
  {
    "num": 83,
    "finding_id": "F-003",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "要件追跡表で Requirement 8 受入 4「機能依存マップは 1 箇所修正で完結」の追跡先に T-009（多層防御の運用文書整備）が含まれる根拠が示されていない",
    "facts": """- requirements.md Req 8 受入 4（L129）：「機能の追加・削除や依存関係の変更は本ファイル 1 箇所の修正で完結する」
- tasks.md 要件追跡表（L266）：対応先が「T-002（運用文書）＋ T-009」
- T-009 の責務記述（L187-195）に、機能依存マップの 1 箇所修正完結への言及はない
- 多層防御の運用文書整備タスクである T-009 が、この受入の追跡先に含まれる根拠が tasks.md 本文に示されておらず、誤追跡の疑いがある""",
    "cases": """- **案 1**：追跡表から T-009 を外し、Req 8 受入 4 の追跡先を T-002 のみにする
- **案 2**：T-009 がこの受入に寄与する根拠（運用文書での 1 箇所修正原則の説明など）を T-009 の責務文に明記して残す""",
    "deep_analysis": """- 案 1 は誤追跡を解消し、追跡の精度が上がる
- 案 2 は T-009 の寄与を明示できれば追跡として正当化されるが、寄与が薄ければ冗長になる
- 追跡表の正確性は T-011（双方向整合テスト）の検証対象であり、ここでの誤追跡は後段で表面化しうる""",
  },
  {
    "num": 84,
    "finding_id": "F-004",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "T-009 と T-010 がともに運用文書（WORKFLOW_PRECHECK.md ／ WORKFLOW_MANAGEMENT.md）を更新するが、規律変更ゲートの説明をどちらが追記するのかが明記されていない",
    "facts": """- T-009 の成果物（L190-191）：`docs/operations/WORKFLOW_PRECHECK.md`（§第 1 層の限界ほか）と `docs/operations/WORKFLOW_MANAGEMENT.md`（§多層防御位置付け節）
- T-010 は規律変更の接合面の実装タスクだが、完了後に WORKFLOW_PRECHECK.md へ規律変更ゲートの説明を追記するかが未規定
- T-010 の成果物リスト（L204-208）に WORKFLOW_PRECHECK.md は登場しない
- 規律変更ゲートの説明追記が T-009 と T-010 のどちらのタスクなのかが不明確""",
    "cases": """- **案 1**：規律変更ゲートの説明追記を T-010 の責務・成果物に明記する（WORKFLOW_PRECHECK.md を T-010 の成果物に追加）。実装者が説明も書く
- **案 2**：運用文書全般は T-009 が担うので、規律変更ゲートの説明追記も T-009 の責務に集約する（T-009 が T-010 の仕様を参照して記述）""",
    "deep_analysis": """- 案 1 は規律変更の実装者（T-010）が説明も書くため内容の正確性が高いが、運用文書の所有が複数タスクに分散する
- 案 2 は運用文書を T-009 に一元化でき所有が明確だが、T-010 の実装内容への追従が必要
- T-009 と T-010 の責務境界をどう引くかが論点""",
  },
  {
    "num": 85,
    "finding_id": "F-007",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "T-008（進行中状態ファイルの管理）が、やり直し待機ファイルの current_blocker フィールド等を読むなら T-007 を前提にすべきだが、T-008 の責務は一般管理であり前提化の必要性は中程度",
    "facts": """- tasks.md T-008 の前提タスク（L171）：「T-001、T-004、T-006」で、T-007 が含まれない
- T-007（reopen 機械強制）は `stages/in-progress/reopen-procedure-<日付>.yaml` に「人間承認待ち」を書き込む（design.md §reopen 機械強制モデル §3）
- T-008 が T-007 の出力形式（`current_blocker` フィールド等）を読んで自己更新の許容（T-008 完了条件 4、L180）を区別するには、T-007 が先に完了している必要がある
- ただし T-008 の責務は「進行中状態ファイル一般の管理」であり、reopen 固有ではない""",
    "cases": """- **案 1**：T-008 の前提タスクに T-007 を追加し、reopen 連動を依存閉包に反映する
- **案 2**：T-008 は進行中ファイルの一般管理に徹し、reopen 固有のフィールドは読まない設計とする。前提は現状維持とし、本文に「`current_blocker` 等の reopen 固有解釈は T-007 側の責務」と明示する""",
    "deep_analysis": """- 関連所見 F-006 と合わせると、T-005 → T-007 → T-008 の依存チェーンの整合性問題になる
- 案 1 は依存を厚くして実装順を保証するが、T-008 の着手が遅れる
- 案 2 は T-008 の責務を一般管理に絞って独立性を保ち、reopen 連動は T-007 側で吸収する
- T-008 の責務範囲をどう定めるか（reopen 固有まで踏み込むか）という設計判断次第""",
  },
  {
    "num": 86,
    "finding_id": "F-010",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "T-003 完了条件 5「テンプレート変数の展開規則が stage_schema.json のコメントまたは運用文書に明示される」が、grep 対象キーワードを示しておらず機械判定が困難",
    "facts": """- T-003 完了条件 5（L95）：「テンプレート変数 `{feature}` ／ `{phase}` ／ `{日付}` の展開元と解決規則が `stage_schema.json` のコメントまたは別途運用文書に明示される」
- 「コメントに明示される」を機械検証するには特定キーワードの grep が必要だが、何を grep すれば充足とみなすかが記述されていない
- design.md L197-205 は展開規則を詳細に記述しているが、その記述が成果物に正しく反映されているかを机上で判断する部分が残る""",
    "cases": """- **案 1**：完了条件 5 に grep 対象キーワード（「テンプレート変数」「{feature}」「{phase}」「{日付}」等）を明示する
- **案 2**：展開規則を `stage_schema.json` の構造化フィールド（例：`required_template_vars` や `template_vars_doc`）に格納し、そのフィールドの存在を検証する形に変更する""",
    "deep_analysis": """- 案 1 は最小修正で grep キーワードを足すだけだが、「コメント内の自由記述」を grep する方式は文言変更に脆い
- 案 2 は構造化により機械検証が堅牢になるが、スキーマ設計の追加が必要
- 関連所見 F-011（T-009 の grep キーワード未明示）と同型であり、整合した方針が望ましい""",
  },
  {
    "num": 87,
    "finding_id": "F-011",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "T-009 のテスト要件「文書内容の grep 検査」の具体的キーワードが未明示で、テスト実装者が自由に解釈できる余地が残る",
    "facts": """- T-009 は「実装ではなく運用文書の整備が主、機械検査の対象ではない」（L187）と明示している
- しかしテスト要件（L196）では「文書内容の grep 検査（4 点キーワード、第 2〜5 層キーワード、補助層 A／B／C キーワード）」を規定している
- grep するキーワードが具体的に何か（日本語か英語か、どの語か）が tasks.md に明示されておらず、完了条件の機械判定可能性に曖昧さが残る""",
    "cases": """- **案 1**：T-009 の完了条件・テスト要件に grep 対象キーワードの具体語（「第 1 層の限界」「中身の空疎」「文脈圧力」等）を列挙する
- **案 2**：T-009 を「運用文書の整備が主で機械検査の対象外」と位置づけ直し、grep のテスト要件自体を削除する（完了条件は必須節の存在のみとする）""",
    "deep_analysis": """- 案 1 は grep を具体化して機械検証可能にするが、運用文書の文言変更に追従が必要
- 案 2 は「運用文書は機械検査対象外」という T-009 自身の位置づけと整合し、テスト要件の矛盾を解消する
- 関連所見 F-010 と同型であり、整合した判断が望ましい""",
  },
  {
    "num": 88,
    "finding_id": "F-013",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "T-004 のテスト要件に `--rationale`（変更理由）必須化のテストはあるが、spec-set サブコマンドで任意の `--rationale` を省略した場合のログ記録動作のテストが欠落している",
    "facts": """- T-004 の成果物記述（L105）：spec-set の `--rationale` は「任意」（design.md L257 も「任意、ログ記録用」と一致）
- commit と push の `--rationale` は必須（L114 完了条件 4）
- T-004 のテスト要件（L116）：「`--rationale` 必須化テスト」とのみ記述
- spec-set の `--rationale` を省略した場合にログ記録が正しく行われるか（省略時のログ形式）のテストケースが明示されていない""",
    "cases": """- **案 1**：T-004 のテスト要件に「spec-set の `--rationale` 省略時のログ記録動作テスト（省略時のログ形式の検証）」を追加する
- **案 2**：spec-set の `--rationale` も必須化し、省略のケース自体をなくす（任意→必須への設計変更、design.md への遡及）""",
    "deep_analysis": """- 案 1 は機能内対処でテストケースの追加のみ。任意引数の挙動を網羅できる
- 案 2 は design.md への遡及（任意→必須）が必要。3 サブコマンドで `--rationale` を統一できるが、省略の利便性は失われる
- spec-set は commit／push より軽い操作のためログ記録用の任意引数とした、という設計意図の尊重が論点""",
  },
  {
    "num": 89,
    "finding_id": "F-016",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "T-010 完了条件 4 が self-improvement の設計 §13.5 との整合を機械検証とするが、§13.5 の内容が変わったときの追従手段（再評価のきっかけ）が規定されていない",
    "facts": """- T-010 完了条件 4（L213）：「self-improvement design §13.5 との時系列契約の整合が機械検証される（DVT-W003：規律変更の所定手続きの段集合の詳細確定後に最終確認）」
- §13.5 の内容は tasks.md の管理外であり、その仕様が変更された場合に DVT-W003 の再評価が誰の責任でいつ実行されるかが tasks.md 上に記述されていない
- design.md 判断 7（L726）で §13.5 との相互参照は合意済みだが、これが機械判定可能かは「別文書の特定節を人が読んで整合判断する」に依存している""",
    "cases": """- **案 1**：T-010 完了条件 4 に「§13.5 変更時の追従手段（変更を検知したら DVT に再登録、または整合検査を再実行する）」を追記する
- **案 2**：§13.5 との整合検証は DVT-W003 に一本化し、完了条件 4 からは外す（DVT の解除条件として管理する）""",
    "deep_analysis": """- 持ち越し所見 A-019（approved_update スキーマの不一致）と同じ self-improvement との接合面の問題
- 案 1 は追従手段を完了条件に明記し、変更検知の責務を明確にする
- 案 2 は DVT に集約して完了条件をシンプルに保つが、追従の保証は DVT 運用の確実性に依存する
- 機能横断の双方向整合（A-019）と合わせた処理が論点""",
  },
  {
    "num": 90,
    "finding_id": "F-017",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "T-001 の成果物に tests/ の .gitkeep はあるが tools/ の .gitkeep や README.md が無く、tools/ ディレクトリの Git 追跡保全が tests/ と非対称になっている",
    "facts": """- design.md §全体構造（L47-64）の配置ツリーに `tools/check-workflow-action.py` が配置されている
- T-001 の責務（L38）：tools/ ディレクトリを新設し、「各ディレクトリに配置目的を記す README を置く」
- T-001 の成果物リスト（L41-50）に `tools/.gitkeep` や `tools/README.md` が含まれない。一方 `tests/workflow-management/.gitkeep`（L50）は計上されている
- 完了条件 1（L52）にも tools/ ディレクトリの確認が含まれていない""",
    "cases": """- **案 1**：T-001 の成果物に `tools/README.md`（または `tools/.gitkeep`）を追加し、完了条件で存在を確認する（tests/ と対称化する）
- **案 2**：tools/ は T-004 の .py ファイル配置で自然に作られるため空ディレクトリの保全は不要とし、整合のため tests/.gitkeep の扱いも見直す（両方とも置かない方向）""",
    "deep_analysis": """- 案 1 は配置宣言の対称性・明示性を高め、責務文（各ディレクトリに README を置く）とも整合する
- 案 2 は最小主義だが、T-004 着手前に tools/ が Git に追跡されない期間が生じる
- 関連所見 F-019（WORKFLOW_MANAGEMENT.md の配置）などの配置整合系と同系統""",
  },
  {
    "num": 91,
    "finding_id": "F-018",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "T-008 の成果物 stages/in_progress.schema.json（アンダースコア区切り）が design のディレクトリ名 in-progress/（ハイフン区切り）と命名不一致で、かつ design の配置ツリーに記載がない",
    "facts": """- T-008 の成果物（L174）：`stages/in_progress.schema.json`（アンダースコア区切り）
- design.md §全体構造（L59）：`stages/in-progress/`（ハイフン区切りのディレクトリ名）
- 命名規則が混在：T-002 の成果物（L65）は `feature-dependency.schema.json`（ハイフン）、T-003 の成果物（L89）は `stage_schema.json`（アンダースコア）
- design.md の配置ツリーに `in_progress.schema.json` の記載が存在せず、設計に無いパスを tasks.md が導入している""",
    "cases": """- **案 1**：命名をハイフンに統一（`in-progress.schema.json`）し、design の配置ツリーにスキーマファイルを追記する
- **案 2**：アンダースコアのまま（スキーマファイルは別の命名規則と整理）とし、design の配置ツリーへの追記のみ行う""",
    "deep_analysis": """- 既存の命名混在（feature-dependency.schema.json はハイフン、stage_schema.json はアンダースコア）が背景にあり、命名規則そのものが未統一
- 案 1 はディレクトリ名（in-progress/）と揃えて一貫性を高めるが、命名規則の全体統一は別論点として残る
- 案 2 は最小修正で配置ツリー追記のみ。命名混在は残る
- 関連所見 F-019 ／ F-020（配置ツリー外のパス）と同系統の配置整合問題""",
  },
  {
    "num": 92,
    "finding_id": "F-019",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "T-001 が新設する docs/operations/WORKFLOW_MANAGEMENT.md が、design.md の配置ツリーに存在しない",
    "facts": """- T-001 の成果物（L49）：`docs/operations/WORKFLOW_MANAGEMENT.md` を新設すると記載
- design.md §全体構造の配置ツリー（L47-64）には docs/operations/ 配下として `docs/logs/workflow-precheck.log` と `docs/reviews/reopen-classification-<日付>.md` のみが示され、WORKFLOW_MANAGEMENT.md も WORKFLOW_PRECHECK.md も配置ツリーに明示されていない
- 設計文書の配置ツリーと tasks.md の成果物の間に記述粒度の乖離がある""",
    "cases": """- **案 1**：tasks.md 側に「design 配置ツリー外の運用文書追加」と注記し、機能内で吸収する（design は遡及しない）
- **案 2**：design の配置ツリーに WORKFLOW_MANAGEMENT.md（および WORKFLOW_PRECHECK.md）を追記する（design への遡及）""",
    "deep_analysis": """- 配置ツリーが運用文書を網羅していない（記述粒度の問題）
- 案 1 は機能内で吸収し design を触らず軽量だが、設計と実装の配置記述の乖離が残る
- 案 2 は設計の正確性を高めるが、遡及（軽量再オープン）が必要
- 関連所見 F-020（learning/ の配置）と同型であり、整合した判断が望ましい""",
  },
  {
    "num": 93,
    "finding_id": "F-020",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "T-010 が新設する learning/workflow/approved-updates/ が design の配置ツリーに無く、判断 7 の接合面記述でのみ言及されている",
    "facts": """- T-010 の成果物（L204-207）：`learning/workflow/approved-updates/.gitkeep` と `approved_update.schema.json` を新設
- design.md §全体構造（L47-64）・§責務境界の明確化（L90-103）のどこにも learning/ ディレクトリが登場しない
- design.md 判断 7（L733）で「self-improvement が承認済み提案 YAML を `git mv` で `learning/workflow/approved-updates/` に配置」という接合面記述はあるが、これは本機能の配置ツリー設計の一部ではない
- self-improvement design §13.5（L638）にはディレクトリ記述があり、機能横断では整合している""",
    "cases": """- **案 1**：tasks.md に「self-improvement §13.5 で配置記述があり機能横断では整合。本機能 design の配置ツリー外の追加」と出典注記し、機能内で吸収する
- **案 2**：design の配置ツリーに learning/ を追記する（design への遡及）""",
    "deep_analysis": """- self-improvement 側に正本があるため、機能横断では整合済み（持ち越し所見 A-019 と同じ接合面）
- 案 1 は出典注記で吸収し、self-improvement を正本とする責務分離と整合する
- 案 2 は本機能 design にも明記するが、接合面の所有が self-improvement 側にあるため二重記述になりうる
- 関連所見 F-019 と同型であり、整合した判断が望ましい""",
  },
  {
    "num": 94,
    "finding_id": "A-005",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "design の先送り論点 9 件のうち DVT（宿題項目）に登録されたのは 4 件のみで、論点 8（規律変更手続きの実装と参照層 5 件の memory→repo 移管要否）と論点 9（運営ガイド等の現行規律本体の改廃手続きを本機能の対象に含めるか）が DVT 未登録",
    "facts": """- design.md L807-808：先送り論点 8・9 を明記
- tasks.md DVT に登録されたのは 4 件（DVT-W001〜W004＝論点 5・4・6・7）のみ
- tasks.md L303：「先送り論点を DVT で集約管理する」を変更意図に掲げているが、論点 8・9 を網羅していない
- 特に論点 8 は T-010（規律変更の所定手続き）の前提であり、参照層 5 件が repo に未移管なら本機能の機械検査が効かない構造問題が残る（design.md L100-102 の指摘と同根）""",
    "cases": """- **案 1**：tasks.md の DVT に論点 8・9 を 2 件追加する（DVT-W005 ／ W006 として登録）
- **案 2**：論点 8・9 は本機能の対象外（memory→repo 移管や運営ガイドの改廃手続きは self-improvement など別機能の領域）として、DVT ではなく注記で対象外であることを明示する""",
    "deep_analysis": """- T-011 の完了条件「DVT に未解除の項目がない」というゲートが、未登録の 2 論点を見逃す穴を持つ
- 案 1 は「先送り論点を DVT で集約管理する」という変更意図（L303）と整合し、漏れを解消する
- 案 2 は対象外を明示して責務範囲を絞るが、論点 8 が T-010 の前提という指摘との整合確認が必要
- 論点 8 は self-improvement との接合面（規律変更手続き）と関連する""",
  },
  {
    "num": 95,
    "finding_id": "A-006",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "design §6 の「depends_on_resolves_correctly 述語は値域チェックのみを担い、依存先の変更検知は別機構（フェーズ 2 の宿題）」という二重性が tasks.md に反映されておらず、境界テストも DVT 登録もない",
    "facts": """- design.md L694：「`depends_on_resolves_correctly` 述語は値域チェックのみを担い、依存先の変更検知と recheck の更新発火は別の機構（tasks 段で実装、本設計時点ではフェーズ 2 以降の宿題）が担う」
- tasks.md は T-004 で 7 つの述語を一律「正常系で OK」とのみ扱い、この述語の限定的な責務（値域は判定するが変更検知はしない）の境界テストを欠く
- 変更検知の先送りが DVT に登録されていない""",
    "cases": """- **案 1**：T-004 に「`depends_on_resolves_correctly` は値域チェックのみ」という境界テストを追加し、変更検知の先送りを DVT に登録する
- **案 2**：tasks.md の該当タスクの責務文にこの二重性を注記するのみとし、境界テストや DVT 登録は追加しない""",
    "deep_analysis": """- 案 1 は述語の限定責務を機械検証し、先送りを DVT で追跡できる。フェーズ 2 への引き継ぎが明確になる
- 案 2 は注記のみで軽量だが、境界が機械検証されず実装漏れのリスクが残る
- 関連所見 F-015（completion_predicate の値域）と関連し、述語の値域・責務の機械検証という共通テーマを持つ""",
  },
  {
    "num": 96,
    "finding_id": "A-007",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "T-005 完了条件 3 が「検査を走らせる」実装作業と「grandfathering（既存分の救済）を採るか判断する」（利用者承認事項）を混在させ、判断未確定のまま検査を走らせると既存 7 件が DEVIATION を返して本機能自身のコミットゲートが全停止する自己ロックのリスクがある",
    "facts": """- T-005 完了条件 3（L131）：「既存レビュー記録 7 件以上に本検査を走らせ、grandfathering を採るか別途判断する論点を DVT に登録（DVT-W002）」
- design.md L792：「既存のレビュー記録 7 件…はフェーズ 2 の検査スクリプト導入時に遡及検査の対象に含めるか、grandfathering として扱うかを別途決定」
- fail-closed を全面採用（design L706 判断 3）している下で、既存 7 件に「起草者と判定者が別人（separation_from_author=true）」の記録が無ければ、commit/push ゲートが常時 DEVIATION を返す""",
    "cases": """- **案 1**：完了条件 3 から判断部分を分離し、「検査の実装」と「grandfathering の判断（DVT-W002）」を別記する。判断が確定するまで既存 7 件を検査対象から除外する順序を明示する（関連所見 F-009 と同根、同じ方針）
- **案 2**：grandfathering を「既存 7 件に separation_from_author=true を後付けする移行スクリプト」として T-005 の成果物に追加し、自己ロックを構造的に回避する""",
    "deep_analysis": """- 関連所見 F-009（T-005 完了条件 3 の機械判定不可）と同根であり、両者を整合して処理するのが自然
- 案 1 は判断と実装を分離して順序問題（自己ロック）を回避し、判断は利用者承認事項として DVT に残す
- 案 2 は移行スクリプトで既存記録を救済し自己ロックを構造的に解決するが、grandfathering の是非判断を先取りすることになる
- fail-closed 方針と、本機能を自分自身に適用する（dogfooding）ときの緊張が核心""",
  },
  {
    "num": 97,
    "finding_id": "A-008",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "design の境界条件は複数の進行中ファイル（reopen-procedure-*.yaml）の並存を要求するが、T-008 のテスト要件は単数前提で、テスト戦略継承表（T-008 に複数並存を割当）と T-008 本文が自己矛盾している",
    "facts": """- design.md L840：境界条件として「進行中状態ファイルが複数存在する場合（複数の reopen-procedure-*.yaml 並存）の扱い」を明記
- design.md L505：reopen をやり直す際「旧ファイルは削除せず証跡として保全する」とあり、複数並存が正常に発生する設計
- tasks.md L277（テスト戦略継承表）：T-008 に「複数 in-progress 並存」を割り当てている
- tasks.md T-008 のテスト要件（L181）：「in-progress あり状態での不可逆操作遮断」を単数前提で記述しており、複数並存時の挙動が未記載""",
    "cases": """- **案 1**：T-008 のテスト要件に複数並存のケース（どれを優先完了対象とするか、複数の blocker の解決順）を追記し、継承表との矛盾を解消する
- **案 2**：複数並存を「異常系（fail-closed で全停止）」と位置づけ、T-008 のテストに「複数並存時は DEVIATION を返す」を追加する""",
    "deep_analysis": """- reopen のやり直しで複数の reopen-procedure-*.yaml が並ぶのは設計上の正常系（L505 の証跡保全）
- 案 1 は複数並存を正常系として扱い、優先順位ロジックをテストする。設計の意図（証跡保全）と整合する
- 案 2 は安全側に倒して複数並存を一律遮断する。実装は単純だが、reopen やり直しの正常運用を妨げる可能性がある
- 複数並存を正常系とみなすか異常系とみなすかが核心""",
  },
  {
    "num": 98,
    "finding_id": "A-010",
    "judgment_text": "直した方がよい（should-fix）",
    "summary": "reopen_classification_template.md（やり直し種別の判定根拠の雛形）が T-001 の成果物（雛形配置）と T-007 の成果物（内容確定）の両方に列挙され、成果物の完了主体の一意性が紛らわしい",
    "facts": """- tasks.md T-001 の成果物（L48）：`templates/review/reopen_classification_template.md`（雛形配置）
- tasks.md T-007 の成果物（L158）：同じパス（「T-001 で配置した雛形、本タスクで内容確定」）
- 同一ファイルパスが 2 つのタスクの成果物リストに登場している
- tasks.md の粒度方針「1 タスク＝1 所有領域」（L22）と「成果物配置の一意性」との緊張がある""",
    "cases": """- **案 1**：T-007 側の成果物記述を「T-001 で配置済み、本タスクで内容を確定する」と注記で明確化する（既存 L158 の記述を強化する）。二重列挙は許容する
- **案 2**：成果物リストの重複を解消し、T-001 は「雛形（空ファイル）の配置」、T-007 は「内容の確定」を別の表現で区別する（例：T-001 は雛形配置のみを成果物とし、T-007 は内容を完了条件に移す）""",
    "deep_analysis": """- 配置（T-001）と内容確定（T-007）を分離する意図そのものは妥当
- 案 1 は注記で完了主体を明示する最小修正。T-011 の成果物配置整合チェックで一意性を読み取れるようにする
- 案 2 は成果物リストから重複を除いて機械判定の一意性を高めるが、記述の再構成が必要
- 処理済みの A-001（reopen 段集合の未定義、遡及）と同じ reopen 周辺の整合""",
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
