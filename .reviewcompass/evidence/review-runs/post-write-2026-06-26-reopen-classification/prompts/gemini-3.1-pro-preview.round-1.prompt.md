prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.1-pro-preview

# Task
Review the target document for the requested phase and criteria.

# Phase
post_write_verification

# Criteria
# Post-write Review Target

criteria_id: reopen-classification-review
phase: post_write_verification
generated_at: 2026-06-26T12:24:44.281123+00:00

## Change Summary

MWP-0: next --json の kind 値を41種類から7種類へ整理する reopen R-0 の分類根拠ファイルを新規作成した。

## Review Question

分類根拠ファイルの内容は、MWP-0（next --json kind 再設計）の reopen R-0 分類として正確・妥当か。分類種別・影響範囲・再実施対象の判断に誤りや見落としはないか。

## Target Files

- docs/reviews/reopen-classification-2026-06-26-wm-next-json-kind-redesign.md sha256=0b4af4b70d5c4ce53d46cf652498e3448a3e124d56bff4ca181040e130e612dd

## Source Materials

### .reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md

content_mode: full_text
content_sha256: 7a4698ec32170ced27d6f7dad1910a4e5a9b64d4639c74892c37cf60cee999a8

```text
# API Review Prompt Quality

最終更新：2026-06-23

本文書は、API 経由の review-run を開始する前に、レビュー用プロンプト自体を品質確認するための運用手順である。

この手順は、特定 feature や特定 phase に閉じない。各 review-run は、この共通手順に phase / gate / feature 固有の上流接続要件を差し込んで使う。

利用者が任意の場面で API review を依頼する場合は、利用者が伝えたレビュー要件を `User Review Requirements` として保持し、criteria 作成・prompt quality review・実 review-run の全段で照合する。

## 1. 目的

API review-run の品質は、モデルや provider だけでなく、プロンプトの作り方に強く依存する。

レビュー用プロンプトの監査は、高リスク時だけの追加確認ではなく、API review-run の標準ゲートである。プロンプトが target / source / scope / output contract を誤ると、その後の raw response、parsed YAML、triage、proxy decision、実装修正がすべて誤った入力に基づく。したがって、prompt audit にかかるコストはレビュー外の余分なコストではなく、レビュー品質を成立させるための本体コストとして扱う。

特に、次の失敗を防ぐ。

- `--target` が実際の審査対象本文ではなく、作成者の要約になっている
- `--criteria-file` と `--target` が同一の author-written summary になっている
- source materials が path-only で、モデルが本文を読めない
- review target / source materials / out of scope が分離されていない
- 上流意図伝達レビューで、上流の目的・責務境界・受入条件・禁止事項が prompt に含まれていない
- 利用者が指定したレビュー目的、重視点、範囲、禁止事項が main によって狭められる、広げられる、または別の問いに置き換えられる
- output contract が曖昧で parser / triage に載らない
- プロンプトが結論を誘導している

## 2. 役割

APIレビュー用プロンプト品質確認は、次の 2 者レビュー体制で行う。

| 役割 | 担当 | 目的 |
|---|---|---|
| main | 操縦中の LLM | API review criteria 素案を作る |
| adversarial | 別モデル | 素案の欠落、誘導、対象違い、材料不足、範囲ミスを探す |
| judgment | 別モデル | adversarial 所見の反映後、その prompt を実 review-run に使ってよいか判定する |

ここでいう 2 者レビュー体制は、作成者である main を除き、adversarial と judgment の 2 者で品質確認する運用を指す。

## 3. 入力分離

API review-run では、criteria と target を分離する。

- `User Review Requirements`: 利用者が指定したレビュー目的、判断対象、重視点、範囲、禁止事項、必要出力
- `--criteria-file`: レビュー目的、背景、上流材料、必須チェック、範囲外、finding policy を含む
- `--target`: 実際に審査する本文

`User Review Requirements` は criteria の上位入力であり、criteria 作成時に失われてはならない。main は、利用者要件を criteria に構造化して写し、どの要件がどの review task / required check / out of scope / finding policy に対応するかを確認できる形にする。

禁止:

- criteria と target に同じ review wrapper / author-written summary を渡す
- target manifest が実審査対象を含まない状態で gate 完了根拠にする
- target 本文を入れず、target の要約だけで review-run を実行する
- 利用者が求めたレビュー範囲を、合意なく狭める、広げる、または別目的の review に置き換える

## 4. User Review Requirements

利用者が任意の場面で review を依頼する場合、main は prompt 作成前に次を整理する。

1. review purpose: 欠陥検出、採否判断、上流接続確認、回帰確認、比較評価など
2. review object: artifact、prompt、設計案、修正案、実装差分など
3. review focus: API設計、互換性、セキュリティ、運用境界、上流要件、実装可能性など
4. scope boundaries: 含める範囲、含めない範囲、まだ判断しない下流工程
5. source materials: 根拠にする要件、設計、過去判断、制約、禁止事項
6. output requirements: findings、severity、採否、懸念点、修正案、比較軸など
7. prohibited actions: commit、push、phase 完了、人間承認代行、未合意の仕様変更など

利用者要件が曖昧な場合でも、main が勝手に確定しない。作業可能な仮定として扱う場合は、criteria に仮定を明記し、prompt quality review で妥当性を確認させる。

## 5. API 送信可能材料の基準

API review-run / proxy_model 判断では、判断に必要な ReviewCompass リポジトリ内の仕様、設計、タスク、レビュー所見、構造化要約、証跡パスを prompt に含めてよい。

これは、次の条件を満たす場合に限る。

1. 利用者が当該 API review-run / proxy_model 判断の実行を明示承認している。
2. API key、token、password、nonce などの秘密値を含めない。
3. メールアドレス、電話番号など個人識別情報を含めない。
4. 第三者との契約上、外部送信できない非公開情報を含めない。
5. 判断に不要な全文ログや周辺ファイルを含めず、判断項目に必要な抜粋または構造化要約に絞る。

単にリポジトリ内の未公開仕様・設計・レビュー要約であることだけを理由に、API 送信を禁止しない。ReviewCompass の API review / proxy_model 運用では、それらは通常のレビュー材料である。

ただし、利用者が外部送信を避ける方針を示した場合、または上記 2〜4 に該当する情報が含まれる場合は、伏字化、抽象化、または外部 API を使わない判断へ切り替える。

## 6. Main が作る criteria の必須要素

criteria file は、少なくとも次を持つ。

1. review task
2. why this review exists
3. user review requirements
4. required disciplines
5. review target
6. source materials
7. required checks
8. out of scope
9. finding policy

source materials は path-only にしない。必要な本文抜粋または構造化要約を、モデルが読める形で criteria に含める。

front matter に path を置く場合は、provenance なのか model-readable material なのかを明示する。

criteria は、利用者要件を単に引用するだけでなく、review task / required checks / out of scope / finding policy へ反映する。

## 6.1 Main Preanalysis

main は criteria 素案を書く前に、対象 review requirement と source materials を直接検討し、判断に必要な材料、判断項目、分割要否、未読資料、機微情報リスクを整理する。

main preanalysis は、prompt 作成のための材料揃えと判断点発見であり、reviewer に対する正解ではない。preanalysis を後続の監査や prompt に含める場合は、仮説・source discovery aid として明示し、reviewer に source materials から独立再構成させる。

main preanalysis には少なくとも次を含める。

- 読んだ source materials と使用目的
- 判断項目と、それぞれの target / source / out of scope
- 複数 prompt に分割すべき独立判断の有無
- prompt に含めるべき model-readable source material
- 送信してはいけない、または最小化すべき機微情報
- 未解決・未読・推測に留まる事項

preanalysis 内の所見は、`open`、`resolved`、`superseded`、`used_for_context` など現在性を区別できる形で扱う。解決済み所見を open な欠陥として prompt bundle に残すと、reviewer を誤誘導するためである。

### 6.2 Behavior-Path Claim の材料選定

review requirement が「あるトリガーから、意図した機械手順へ進むか」「短い利用者指示が gate を bypass しないか」「特定の guard が必ず作動するか」のような behavior-path claim / 実行経路 claim を含む場合、main preanalysis は変更文書だけを target/source にしてはならない。

この場合、source materials には少なくとも次を含める。

- trigger resolver または利用者発話を operation に写像する map
- operation preflight、guard、gate、runner など実行経路上の制御実装
- その経路を固定するテスト、または存在しない場合は「未固定」と分かる証跡
- 変更対象文書、effective prompt、plan / TODO / checklist など経路上の入力成果物
- 期待される停止点、禁止 bypass、許可される次操作

対象が「文書の整合性」ではなく「動作上の強制」なら、変更された guidance / prompt だけを target にした review-run は不足である。文書に要件が書かれていても、trigger resolver、operation preflight、runner、test がその要件を読んでいなければ behavior-path claim は成立しない。

### 6.3 Review Question Decomposition

main は criteria 作成前に review question decomposition を行う。整合性確認だけの一括質問にしない。

分解では、利用者要件または workflow 要件を要求 claim ごとの required check に写す。各 required check は、次を明示する。

1. 何を成立させる claim か
2. どの target / source material で判定するか
3. finding にすべき失敗条件は何か
4. out of scope は何か

例: 「ショートリクエストが bridge を bypass しない」を検証するなら、単に「prompt と map が整合しているか」と聞かない。`次へ`、`進める`、`継続` などの短い発話がどの trigger resolver / operation preflight / effective prompt に到達し、どこで plan materialization status、TODO/checklist coverage、quality audit を確認するかを required check に分解する。

review question が複数 claim を含む場合は、claim ごとに prompt を分けるか、少なくとも required checks を分離して reviewer が各 claim を個別に pass/fail できる形にする。

## 7. Phase 別の上流接続

`.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review` が適用される review では、phase ごとに次を確認する。

| phase | target | source materials |
|---|---|---|
| requirements | `requirements.md` | upstream decision materials, reopen classification, planning notes, user decisions |
| design | `design.md` | `requirements.md` |
| tasks | `tasks.md` | `requirements.md`, `design.md` |
| implementation | implementation artifacts | `requirements.md`, `design.md`, `tasks.md` |

source materials は背景・意図伝達確認のために使う。現在 phase の correctness だけを target として判定し、下流 phase の correctness を同時に判定しない。

利用者が指定した review focus が phase 標準の観点と異なる場合は、両者の関係を criteria に明記する。phase 標準の必須検査を外す必要がある場合は、利用者合意なしに外してはならない。

## 8. Prompt Quality Review

main が criteria 素案を作ったら、実 review-run の前に preanalysis sufficiency audit と prompt quality review を行う。

標準手順は次の順序とする。

1. main preanalysis
2. preanalysis sufficiency audit
3. API review criteria draft
4. prompt quality review
5. 実 review-run
6. raw / parsed / model summary / triage
7. 必要に応じて proxy_model decision

通常の prompt quality review の前に、`templates/review/main_preanalysis_sufficiency_audit_criteria_template.md` を使って preanalysis sufficiency audit を行う。この監査では、reviewer に source materials から judgment item を独立再構成させたうえで、main preanalysis を仮説として比較させる。main preanalysis を正解として渡してはならない。

preanalysis sufficiency audit では、target bundle に次を含める。

- 利用者または workflow の review requirement
- 判断に必要な source materials の本文または構造化抜粋
- main session LLM の preanalysis
- proposed API review criteria または prompt

監査結果の `required_prompt_changes` を反映してから、通常の `templates/review/api_review_prompt_quality_criteria_template.md` による prompt quality review へ進む。

preanalysis sufficiency audit は、次の欠陥を検出するための標準ゲートである。

- source selection の漏れ
- source summary と原文対応の不足
- main preanalysis の stale / resolved 所見による anchoring
- 複数の独立判断を 1 prompt に押し込む粒度誤り
- 誤検出防止文言が、重要な欠陥検出まで抑制する framing bias
- output contract と runner / parser の不一致
- behavior-path claim に必要な trigger resolver / operation preflight / runner / test の欠落
- review question decomposition の不足による、整合性確認だけの一括質問化

review question は 1 prompt につき原則 1 つにする。複数の独立した採否判断、クラスタ判断、設計論点判断を 1 つの prompt に押し込まない。

複数判断がある場合は、判断項目ごとに prompt を分ける。各 prompt は、その判断に必要な source findings、上流材料、対象本文要約、out of scope、output contract だけを持つ。共通背景を入れる場合も、個別判断の焦点を曖昧にしない量に抑える。

adversarial には、`templates/review/api_review_prompt_quality_criteria_template.md` を criteria として渡し、criteria 素案を target としてレビューさせる。

利用者要件がある場合、prompt quality review では次も確認する。

- 利用者要件が criteria に保持されている
- 利用者要件が review task / required checks / out of scope / finding policy に反映されている
- main が利用者要件を合意なく狭めたり広げたりしていない
- 利用者が禁止した操作や判断代行が prompt に混入していない
- 複数の独立判断を 1 prompt に押し込んでおらず、判断項目ごとに注意が分散しない粒度になっている

adversarial の所見を main が反映した後、judgment に同じ quality criteria と adversarial 所見を渡し、使用可否を判定させる。

judgment が `findings: []` を返した場合だけ、実 review-run へ進める。

judgment が finding を返した場合は、prompt を再修正し、必要に応じて再度 judgment へ回す。

高リスクまたは実行経路 claim を含む review では、single-model findings: [] を単独の完了根拠にしない。根拠説明なしの 0 件、特に raw response が `findings: []` のみの場合は、対象材料と問いが狭すぎる可能性を疑い、次のいずれかを行う。

- 3-way の独立 review に切り替える
- reviewer に claim ごとの pass/fail rationale と参照 material を出力させる
- main preanalysis sufficiency audit へ戻り、source selection と review question decomposition をやり直す

## 9. 実 Review-Run

prompt quality review を通過した後、実 review-run を実行する。

複数 prompt に分けた場合は、各 prompt の prompt quality review 通過証跡と実 review-run / proxy decision 結果を判断項目ごとに保存する。一括 summary は後段で作ってよいが、個別判断の raw / parsed / decision 証跡を上書きしない。

実行時には次を確認する。

- `target-manifest.yaml` に実審査対象が入っている
- `rounds.yaml` の criteria は使用可判定済み criteria である
- raw / parsed / model-result-summary / triage が生成されている
- 利用者提示ゲート前に、raw 結果概要、モデル別 summary、同根クラスタ、三段階トリアージ案をまとめる
- 実 review-run の結果を、利用者要件に含まれていない操作承認や phase 完了根拠へ拡張しない

## 10. 成果物配置

推奨配置:

```text
.reviewcompass/specs/<feature>/reviews/<date>-<feature>-<phase>-<topic>-prompt-quality-run/
  api-review-criteria.md
  prompt-quality-review-criteria.md
  variant-role-assignment.yaml
  raw/
  parsed/
  prompts/
  rounds.yaml
  model-result-summary.yaml
  prompt-quality-summary.md
```

実 review-run は別ディレクトリに分ける。

```text
.reviewcompass/specs/<feature>/reviews/<date>-<feature>-<phase>-<topic>-review-run/
```

prompt-quality-run は、実 review-run の gate 完了根拠ではない。実 review-run の criteria を使ってよいことを示す補助証跡である。

## 11. 今回の事例から得た規則

2026-06-20 の `workflow-management` design triad-review では、旧 run が `review-target.md` を criteria と target の両方に使い、`findings: []` になった。

その後、prompt quality review を挟み、`design.md` を実 target として再実行した v2 run では 15 件の所見が出た。

同日の `workflow-management` implementation Req14 approval gate prompt audit では、preanalysis sufficiency audit により、source summary の原文対応不足と、誤検出防止文言が approval gate bypass 検出を鈍らせる framing bias が検出された。これは、prompt audit が形式確認ではなく、実 review-run の欠陥検出力そのものを左右することを示す。

2026-06-23 の plan-todo-checklist materialization PTC-4 post-write review では、prompt が「updated effective prompts and discipline map の整合性確認」に寄りすぎ、短い `次へ` / `進める` から plan-to-TODO bridge へ到達する実行経路を検証できなかった。target は guidance / effective prompt に寄り、trigger resolver、operation preflight、runner、経路テストを含めなかったため、single-model findings: [] が返っても behavior-path claim の完了根拠としては弱かった。

この差分から、次を標準規則とする。

- 実審査対象本文を target にしない review-run は、gate 完了根拠として弱い
- author-written summary は criteria または source-material summary として使えるが、target 本文の代替にしない
- 上流接続 review では、source materials と target を明示的に分離する
- source summary には原文または構造化抜粋に加え、必要に応じて source cross-reference を持たせる
- main preanalysis は有用だが、仮説として扱い、reviewer に独立再構成させる
- 1 prompt に複数の独立判断を押し込まない
- prompt 自体の adversarial / judgment レビューを実行前に挟む
- behavior-path claim では、変更文書だけでなく trigger resolver / operation preflight / runner / test を source materials に含める
- review question は要求 claim ごとの required check に分解し、整合性確認だけの一括質問にしない
- 高リスクまたは実行経路 claim では、根拠説明なしの single-model findings: [] を完了根拠にしない

## 12. 停止点

prompt quality review は、実 review-run の開始許可であり、次の操作を自動許可しない。

- `spec.json` 更新
- phase / gate 完了
- proxy_model 判断
- design / requirements / tasks / implementation 本文修正
- commit
- push

これらはそれぞれの workflow gate と利用者承認に従う。
```

### docs/notes/2026-06-26-next-json-kind-redesign.md

content_mode: full_text
content_sha256: a2539c18675124a968b96a5b1f8792f5f9ad84d20b304556429df9a516096d92

```text
# `next --json` の kind 再設計（議論記録）

最終更新：2026-06-26（詳細フィールド設計を追記）。

## 動機

`next --json` の本来の役割は「ワークフロー作業の中のどの地点にいるかを返す」こと。
地点が分かれば次のアクションが機械的に決まり、LLM の手作業が減り動作がセキュアになる。

現状の `kind` 値は41種類あり、次の問題がある：

- 「作業状態」「手続きの内部ステップ追跡」「コミット操作の確認」が同じ `kind` に混在
- `maintenance_in_progress` と `blocking_unit_in_progress` は意味が同じだが別の `kind`
- reopen のサブステップ13種類が `kind` に詰め込まれている

## 決定：7種類への整理

| `kind` | 意味 |
|--------|------|
| `completed` | 全作業完了。次の作業を始められる |
| `in_progress` | 通常の作業中（フェーズ終端のコミット待ちも `stage: commit_stop_point` で表現） |
| `blocking_in_progress` | 本線とは別の作業中。完了後は親または次判定へ戻る |
| `verification_pending` | 書き込み後の検証（post-write verification）待ち |
| `reopen_in_progress` | 再開手続き中（サブステップは詳細フィールドで返す） |
| `feature_definition_required` | プロジェクト立ち上げ時の初期設定未完了（特殊ケース・verdict: OK） |
| `unknown` | 想定外のエラー状態（ファイル破損・整合違反など・verdict: DEVIATION） |

`feature_definition_required` と `unknown` の区別：同じ設定ファイル問題でも、前者は「正常な未完了」（修復方法が明確）、後者は「壊れた異常状態」（調査が必要）。

## 新旧対照表

| 旧 `kind` | 新 `kind` |
|-----------|-----------|
| `stage` | `in_progress` |
| `cross_feature_stage` | `in_progress` |
| `upstream_recheck` | `in_progress`（`upstream_phase` フィールドを追加） |
| `commit_stop_point` | `in_progress`（`stage: commit_stop_point`） |
| `maintenance_in_progress` | `blocking_in_progress` |
| `blocking_unit_in_progress` | `blocking_in_progress` |
| `blocking_unit_required` | `blocking_in_progress` |
| `parent_resume_pending` | `blocking_in_progress` |
| `resume_in_progress` | `blocking_in_progress` |
| `post_write_verification` | `verification_pending` |
| `post_write_policy_violation` | `verification_pending` |
| `post_write_human_decision_required` | `verification_pending` |
| `reopen_in_progress` + サブステップ13種類 | `reopen_in_progress`（詳細はフィールドへ） |
| `completed` | `completed`（変わらず） |
| `feature_definition_required` | `feature_definition_required`（変わらず） |
| `unknown` | `unknown`（変わらず） |
| `commit_candidate` / `commit_mixing_risk` / `commit_unit_stale` | `next --json` から除外 → `commit --preflight` へ移動（検討中） |
| `phase_approval_complete` / `human_decision_recorded` / `record_human_decision_failed` | 元から `next --json` の kind ではなかった（別サブコマンドの出力・入れ子フィールド） |
| `next_action_template` / `project_state` / `subthread` / `human` / `operation_prompt` / `lightweight_self_check` | 元から `next --json` の kind ではなかった（コード内部のデータ構造） |

## 詳細フィールドの設計（確定）

### 全 `kind` 共通フィールド

| フィールド | 役割 |
|-----------|------|
| `kind` | 現在地のカテゴリ |
| `required_action` | 次にすべき操作の名前（機械が読む） |
| `reason` | 状態の説明（人間が読む） |

### `in_progress`

| フィールド | 説明 |
|-----------|------|
| `feature` | 対象機能名（cross_feature_stage では `"all_features"` 固定） |
| `phase` | 現在のフェーズ |
| `stage` | 現在のステージ（`commit_stop_point` を含む） |
| `upstream_phase` | 上流フェーズ名（upstream_recheck の場合のみ） |

### `blocking_in_progress`

`blocking_phase` サブフィールドで段階を区別する（3値）：

| `blocking_phase` | 意味 | 統合された旧 `kind` |
|-----------------|------|-------------------|
| `required` | blocking 作業の開始が必要 | `blocking_unit_required` |
| `in_progress` | blocking 作業中 | `blocking_unit_in_progress` / `maintenance_in_progress` / `resume_in_progress` |
| `return_pending` | blocking 完了・親への復帰待ち | `parent_resume_pending` |

`resuming` は廃止。`in_progress`（`unit_id` / `parent_unit_id` が null）として吸収。

| フィールド | `required` | `in_progress` | `return_pending` | 説明 |
|-----------|:---:|:---:|:---:|------|
| `blocking_phase` | ✓ | ✓ | ✓ | 段階の区別 |
| `title` | ✓ | ✓ | — | 作業の名前 |
| `unit_id` | ✓ | ✓ | — | blocking unit の識別子（種別不明時は null） |
| `parent_unit_id` | ✓ | ✓ | ✓ | 親への戻り先 |
| `return_conditions` | ✓ | ✓ | — | 戻る条件（旧 `completion_conditions` と統一） |
| `allowed_scope` | — | ✓ | — | 許可された操作の種類 |
| `allowed_files` | — | ✓ | — | 許可されたファイル |
| `file` | — | ✓ | — | 進行中ファイルのパス（ファイルベース管理の場合） |
| `completed_unit_id` | — | — | ✓ | 完了した unit の識別子 |

廃止するフィールド：`resuming`（`blocking_phase` 値）/ `completion_conditions`（`return_conditions` に統一）/ `process_id`（`blocking_phase` で代替）/ `maintenance_action`（`required_action` で代替）/ `blocked_normal_workflow`（`blocking_phase: in_progress` で暗示）/ `mainline_blocked_by`（`completed` 開始の maintenance に戻り先はないという整理から不要）/ `action_parameters`（他フィールドの重複コピー）/ `active_gate`（maintenance では常に null）

### `verification_pending`

`verification_type` サブフィールドで種類を区別する：

| `verification_type` | 意味 | 次のアクション |
|--------------------|------|--------------|
| `pending` | 検証待ち・未着手 | 検証を実施する |
| `policy_violation` | 禁止変更が混入 | 違反を解消する |
| `human_decision_required` | 未解決の重大所見あり | 人間が判断する |

| フィールド | `pending` | `policy_violation` | `human_decision_required` | 説明 |
|-----------|:---:|:---:|:---:|------|
| `verification_type` | ✓ | ✓ | ✓ | 種類の区別 |
| `target_files` | ✓ | ✓ | ✓ | 検証対象ファイル |
| `manifest` | ✓ | — | ✓ | 封印ファイルのパス |
| `forbidden_files` | — | ✓ | — | ルール違反のファイル |
| `codes` | ✓（任意） | — | — | 検証コード |

### `reopen_in_progress`

廃止するフィールド：`next_drafting_gate`（`active_gate` で代替・手引き改修が必要）/ `feature`（`required_feature_scope` で代替）/ `direct_features` / `indirect_features` / `feature_impact_scope_basis`（手引きに参照なし）

残すフィールド：`file` / `next_step` / `step_number` / `completed_steps` / `pending_gates` / `next_pending_gate` / `active_gate` / `current_blocker` / `required_action` / `blocked_by` / `approval_record_path` / `required_feature_scope` / `phase` / `stage` / `reason` / `repair_reasons`（任意）

## 決定：`commit --preflight` への移動

`commit_candidate` / `commit_mixing_risk` / `commit_unit_stale` の3種類を `next --json` から除外し、`commit-preflight` サブコマンドの判定に集約する。

根拠：
- `commit-preflight` は既にコミット前の必須確認として手引きに定義されている（手順：commit-preflight → git add → guarded commit）
- これら3種類は「コミット操作の前確認」であり「作業の現在地」ではない
- 利用者の操作手順は変わらない（`commit-preflight` を実行する点は同じ）
- 手引きの `commit_mixing_risk` / `commit_unit_stale` の説明箇所を `commit-preflight` の文脈に移す改修が必要

## 未決定・残作業

- `next_drafting_gate` 廃止に伴う `WORKFLOW_NAVIGATION.md` の手引き改修
- 実装変更の優先順位・着手時期

## 関連

- [2026-06-25-workflow-state-simplification.md](2026-06-25-workflow-state-simplification.md)（前日の状態整理）
- [2026-06-25-work-mode-taxonomy-related-work-index.md](2026-06-25-work-mode-taxonomy-related-work-index.md)（関連作業索引）
- [plan-2026-06-23-maintenance-workflow-protocol.yaml](../../.reviewcompass/backlog/plans/plan-2026-06-23-maintenance-workflow-protocol.yaml)（MWP-0〜MWP-3）
```


## Target File Contents

### docs/reviews/reopen-classification-2026-06-26-wm-next-json-kind-redesign.md

content_mode: full_text
content_sha256: 0b4af4b70d5c4ce53d46cf652498e3448a3e124d56bff4ca181040e130e612dd

```text
---
date: 2026-06-26
classifier: claude_session
classification: R-0（workflow-management）
trigger_source: 2026-06-26 セッションで `next --json` の kind 値が 41 種類あり「作業状態」「手続き内部ステップ」「コミット操作確認」が混在していることを確認。設計文書 `docs/notes/2026-06-26-next-json-kind-redesign.md` で 7 種類への整理設計が確定。利用者指示により reopen 正式手続きへ進む。
feature: workflow-management
finding: next-json-kind-redesign
---

## 分類根拠

`next --json` が返す `kind` 値を 41 種類から 7 種類へ整理する。現状の `kind` には「作業の現在地」「手続き内部のサブステップ追跡」「コミット操作の前確認」が同一フィールドに混在しており、機械的な次アクション決定が困難になっている。整理後は `kind` が「作業の現在地カテゴリ」のみを示し、サブ情報はサブフィールドで返す設計とする。

手戻り種別：**R-0（requirements 起点。intent・feature-partitioning へは遡らない）**。

- intent（意図）：workflow-management の意図は「段集合 YAML による静的検査、所定手続きの階層構造、不可逆操作の直前ゲート、修復手続きの機械強制を担う」ことである。`next --json` の kind 整理は既存の「次アクション通知」の出力形式改善であり、新しい意図を導入しない。意図文書の改訂は不要。
- feature-partitioning（機能分割）：対象は `workflow-management` の `next --json` 出力インターフェイスであり、機能分割・責務境界の再定義は不要。

## 事実

- 設計文書：`docs/notes/2026-06-26-next-json-kind-redesign.md` に新旧対照表・詳細フィールド設計・廃止フィールド一覧が確定済み。
- 現状の kind 種類：41 種類。うち `maintenance_in_progress` と `blocking_unit_in_progress` は意味が同一だが別 kind として実装されており、reopen のサブステップ 13 種類が `kind` に詰め込まれている。
- 変更後の kind：7 種類（`completed` / `in_progress` / `blocking_in_progress` / `verification_pending` / `reopen_in_progress` / `feature_definition_required` / `unknown`）。
- commit 関連の kind 移動：`commit_candidate` / `commit_mixing_risk` / `commit_unit_stale` の 3 種類を `next --json` から除外し `commit-preflight` サブコマンドへ集約する。
- 手引き改修：`WORKFLOW_NAVIGATION.md` の `next_drafting_gate` 廃止に伴う記述改修が必要。

## feature impact 判定

| feature | decision | impact_basis | rationale |
| --- | --- | --- | --- |
| workflow-management | reopen_existing_feature | contract_ownership | `next --json` の出力インターフェイスと `commit-preflight` の判定ロジックを所有する。kind 整理・commit 関連 kind 移動・手引き改修の requirements / design / tasks / implementation を所有するため。 |
| foundation | no_reopen_existing_feature | no_implementation_impact | 共通語彙・共通スキーマに変更なし。 |
| runtime | no_reopen_existing_feature | no_implementation_impact | session 記録や hook 実行契約に変更なし。 |
| evaluation | no_reopen_existing_feature | no_implementation_impact | レビュー評価契約に変更なし。 |
| analysis | no_reopen_existing_feature | no_implementation_impact | 分析・可視化・報告機能に変更なし。 |
| self-improvement | no_reopen_existing_feature | no_implementation_impact | 自己改善提案や規律本文に変更なし。 |
| conformance-evaluation | no_reopen_existing_feature | no_implementation_impact | 実装照合・逸脱検出に変更なし。 |

新 feature 判定：no_new_feature。

## 再実施対象

- **workflow-management（R-0）**：requirements に `next --json` kind 再設計・`commit-preflight` への移動・手引き改修の受入基準を追記または更新する。requirements は drafting 相当の本文修正後に triad-review / review-wave / alignment / approval を再実施する。
- **design**：7 種類の kind 定義・サブフィールド設計・廃止フィールド・`commit-preflight` 集約の設計を更新する。
- **tasks**：kind 変更に対応するテスト要件と実装作業を追記する。
- **implementation**：TDD で失敗テストを先に作成し、kind 整理を実装する。

impacted_downstream_phases：design／tasks／implementation。

## 停止点

reopen-start により in-progress ファイルを発行し、spec.json のフラグ差し戻し（workflow-management：requirements 以降の alignment・approval を false、recheck＝upstream_change_pending を true・impacted_downstream_phases に design／tasks／implementation を設定）を行ったうえで、第1過程停止点として差し戻し内容の利用者承認を待つ。
```


## Scope

- Check whether the changed target files clearly state the intended contract.
- Check whether related instructions are mutually consistent across targets.
- Check whether the documented procedure is actionable before API review, triage, manifest, or commit steps continue.

## Out Of Scope

- Do not request unrelated refactors or style-only rewrites.
- Do not judge files that are not listed in Target Files.
- Do not treat missing implementation work as a document defect unless the target text claims it already exists.

## Finding Policy

- Report must-fix findings for contradictions, missing required gates, or instructions that would allow an unsafe workflow action.
- Report should-fix findings for ambiguity that could cause repeated manual judgment or unnecessary API review loops.
- Return findings: [] when the target files are internally consistent for this review question.

## Sensitive Information Check

- status: passed
- External API review must not proceed if this section reports potential secrets.


# Output contract
Return YAML only.
The response must include the top-level key findings.
Additional top-level keys are allowed only when the criteria explicitly defines them.
Do not add wrapper keys such as review, result, metadata, or summary.
Do not wrap the YAML in Markdown code fences.
Do not write prose before or after the YAML.

Each finding must include these keys:
- severity
- target_location
- description
- rationale

Use only these severity values:
- CRITICAL
- ERROR
- WARN
- INFO

If there are no findings and the criteria does not define additional top-level keys, return exactly:

findings: []

Valid shape example:

findings:
  - severity: WARN
    target_location: "path or section"
    description: "Plain finding summary"
    rationale: "Why this matters"

# Prior findings
なし

# Target path
docs/reviews/reopen-classification-2026-06-26-wm-next-json-kind-redesign.md

# Target document
---
date: 2026-06-26
classifier: claude_session
classification: R-0（workflow-management）
trigger_source: 2026-06-26 セッションで `next --json` の kind 値が 41 種類あり「作業状態」「手続き内部ステップ」「コミット操作確認」が混在していることを確認。設計文書 `docs/notes/2026-06-26-next-json-kind-redesign.md` で 7 種類への整理設計が確定。利用者指示により reopen 正式手続きへ進む。
feature: workflow-management
finding: next-json-kind-redesign
---

## 分類根拠

`next --json` が返す `kind` 値を 41 種類から 7 種類へ整理する。現状の `kind` には「作業の現在地」「手続き内部のサブステップ追跡」「コミット操作の前確認」が同一フィールドに混在しており、機械的な次アクション決定が困難になっている。整理後は `kind` が「作業の現在地カテゴリ」のみを示し、サブ情報はサブフィールドで返す設計とする。

手戻り種別：**R-0（requirements 起点。intent・feature-partitioning へは遡らない）**。

- intent（意図）：workflow-management の意図は「段集合 YAML による静的検査、所定手続きの階層構造、不可逆操作の直前ゲート、修復手続きの機械強制を担う」ことである。`next --json` の kind 整理は既存の「次アクション通知」の出力形式改善であり、新しい意図を導入しない。意図文書の改訂は不要。
- feature-partitioning（機能分割）：対象は `workflow-management` の `next --json` 出力インターフェイスであり、機能分割・責務境界の再定義は不要。

## 事実

- 設計文書：`docs/notes/2026-06-26-next-json-kind-redesign.md` に新旧対照表・詳細フィールド設計・廃止フィールド一覧が確定済み。
- 現状の kind 種類：41 種類。うち `maintenance_in_progress` と `blocking_unit_in_progress` は意味が同一だが別 kind として実装されており、reopen のサブステップ 13 種類が `kind` に詰め込まれている。
- 変更後の kind：7 種類（`completed` / `in_progress` / `blocking_in_progress` / `verification_pending` / `reopen_in_progress` / `feature_definition_required` / `unknown`）。
- commit 関連の kind 移動：`commit_candidate` / `commit_mixing_risk` / `commit_unit_stale` の 3 種類を `next --json` から除外し `commit-preflight` サブコマンドへ集約する。
- 手引き改修：`WORKFLOW_NAVIGATION.md` の `next_drafting_gate` 廃止に伴う記述改修が必要。

## feature impact 判定

| feature | decision | impact_basis | rationale |
| --- | --- | --- | --- |
| workflow-management | reopen_existing_feature | contract_ownership | `next --json` の出力インターフェイスと `commit-preflight` の判定ロジックを所有する。kind 整理・commit 関連 kind 移動・手引き改修の requirements / design / tasks / implementation を所有するため。 |
| foundation | no_reopen_existing_feature | no_implementation_impact | 共通語彙・共通スキーマに変更なし。 |
| runtime | no_reopen_existing_feature | no_implementation_impact | session 記録や hook 実行契約に変更なし。 |
| evaluation | no_reopen_existing_feature | no_implementation_impact | レビュー評価契約に変更なし。 |
| analysis | no_reopen_existing_feature | no_implementation_impact | 分析・可視化・報告機能に変更なし。 |
| self-improvement | no_reopen_existing_feature | no_implementation_impact | 自己改善提案や規律本文に変更なし。 |
| conformance-evaluation | no_reopen_existing_feature | no_implementation_impact | 実装照合・逸脱検出に変更なし。 |

新 feature 判定：no_new_feature。

## 再実施対象

- **workflow-management（R-0）**：requirements に `next --json` kind 再設計・`commit-preflight` への移動・手引き改修の受入基準を追記または更新する。requirements は drafting 相当の本文修正後に triad-review / review-wave / alignment / approval を再実施する。
- **design**：7 種類の kind 定義・サブフィールド設計・廃止フィールド・`commit-preflight` 集約の設計を更新する。
- **tasks**：kind 変更に対応するテスト要件と実装作業を追記する。
- **implementation**：TDD で失敗テストを先に作成し、kind 整理を実装する。

impacted_downstream_phases：design／tasks／implementation。

## 停止点

reopen-start により in-progress ファイルを発行し、spec.json のフラグ差し戻し（workflow-management：requirements 以降の alignment・approval を false、recheck＝upstream_change_pending を true・impacted_downstream_phases に design／tasks／implementation を設定）を行ったうえで、第1過程停止点として差し戻し内容の利用者承認を待つ。

