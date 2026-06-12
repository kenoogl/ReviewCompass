# レビュー対象：reopen D-0（placement-p1-path-contracts）workflow-management tasks 変更

## 0. variant 選定理由（実行前ゲートの記録）

- 使用 variant：`implementation_review_independent_3way`（context: triad_review、API 3 社独立）
- 役割：primary=anthropic-api/claude-sonnet-4-6、adversarial=openai-api/gpt-5.5、judgment=gemini-api/gemini-3.1-pro-preview
- 選定理由：本 reopen の design triad-review と同一構成（利用者承認 2026-06-12「承認承認」、design approval は「承認」）

## 1. レビューの位置付け

reopen D-0（分類記録 `docs/reviews/reopen-classification-2026-06-12-placement-p1-path-contracts.md`）の第3過程、
workflow-management tasks フェーズの triad-review。上流 design は gate 連鎖を完了し利用者承認済み。
確定した design 上流契約の要点：

- 実行時生成物 3 パスの新配置：検査ログ `.reviewcompass/runtime/logs/workflow-precheck.log`、
  effective prompt `.reviewcompass/runtime/effective-prompts/`、commit 承認記録 `.reviewcompass/runtime/approvals/commit-approval.json`
- 凍結期共通契約（design §全体構造「実行時生成物の凍結期（P3 まで）の扱い」が正本）：書き込み常時新配置・既存分は旧置き場で
  凍結（効力発生は P1 実装反映コミット＝書き込み先切替と同時）・旧パス読み取り互換は 3 パスとも P3 まで維持（新→旧の順）・
  互換の終了は P3 の専用 reopen における設計改訂（暗黙の終了はない）

現時点で実装は旧パスへ書く挙動のまま（意図的・正順）。implementation 段で TDD により書き込み先変更と読み取り互換を実装する。

## 2. レビュー観点

1. tasks の修正 4 箇所（T-001 の README 注記、T-004 責務の effective prompt・検査ログ・commit 承認記録、T-004 テスト要件 5）が
   design 確定契約と一致しているか
2. design の新機構（凍結期共通契約：書き込み常時新配置・凍結・効力発生時点・新→旧読み取り互換・凍結違反の扱い）が
   tasks のタスク責務・テスト要件へ翻訳されているか（ce reopen では同種の指摘 C7 が must-fix になった先行事例がある）
3. 変更漏れ：tasks 内に旧 3 パスへの現役参照（由来注記以外）が残っていないか
4. テスト要件が凍結期挙動（新配置書き込み・旧配置への新規書き込み禁止・読み取り互換）を機械検証可能な粒度で要求しているか
5. 例外系・境界条件（凍結の効力発生時点、互換の終了条件、旧パスにしか記録がない場合の読み取り）

## 2.5 round-2 注記：round-1 所見の適用（proxy_model 判断、2026-06-12）

round-1 の 11 所見（同根クラスタ X1＝design 凍結期共通契約の tasks 翻訳欠落、ERROR5/WARN4/INFO2）は proxy_model
（gemini-3.1-pro-preview、委任出典＝利用者発言「proxy_modelで自律実行」）が全件 must-fix・案 A で判断した
（証跡 `proxy-decisions/`・`approval-proxy-2026-06-12.yaml`）。適用内容：

- T-004 責務へ凍結期責務を追記：実行時生成物 3 パスの書き込み常時新配置・旧配置（3 つの旧パスを明記）への新規書き込み禁止・
  効力発生＝P1 実装反映コミットと同時・互換終了＝P3 専用 reopen（暗黙終了なし）・読み取りは新→旧の順のフォールバック。
  commit 承認記録の旧パスもファイルパスまで明示
- 完了条件 5 を 3 パス × 3 観点の凍結期挙動の機械検証へ拡張
- テスト要件へ凍結期挙動テスト（3 パス × 3 観点＝計 9 観点、TDD 先行）を追加

round-2 は適用後本文の収束確認である。

## 2.6 round-3 注記：round-2 所見の適用（proxy_model 判断、2026-06-12）

round-2 の 3 所見（判定役ゼロ）は proxy_model が判断した（証跡 `proxy-decisions/round-2/`・
`approval-proxy-2026-06-12-round-2.yaml`）。Y1＝should-fix 適用：凍結期挙動テストへ境界条件の明示
（観点 2 が効力発生時点の検証を兼ねる・観点 3 の互換が暗黙に無効化されないことの検証）。Y2＝should-fix 適用：
責務へ「新旧いずれにも記録がない場合は各ツールの既存挙動に従い本変更はそれを変えない」を追記。Y3＝leave-as-is。
round-3 は適用後本文の収束確認である。

## 2.7 round-4 注記：round-3 所見の適用（proxy_model 判断、2026-06-12）

round-3 では主役（claude）所見ゼロ、敵対役（gpt-5.5）と判定役（gemini）が同根 2 クラスタを指摘し、proxy_model が判断した
（証跡 `proxy-decisions/round-3/`・`approval-proxy-2026-06-12-round-3.yaml`。なお round-3 の判定役応答は中断により欠落して
いたため、run_role.py で判定役のみ正規再実行して完成させた）。

- T1（must-fix、ERROR×2 同根）＝案 A 適用：凍結期挙動テストへ観点 4「新旧両方に記録がある競合時に新配置が採用される」
  （design 契約「新→旧の順」の直接検証）を追加、完了条件 5 を追従
- T2（should-fix、WARN×2 同根）＝案 A 適用：観点 5「凍結済み旧成果物の不変性（git 追跡履歴による変更・削除検出、
  conformance-evaluation と同一判定規則）」を追加、完了条件 5 を追従

凍結期挙動テストは 3 パス × 5 観点＝計 15 観点となった。round-4 は適用後本文の収束確認である。

## 3. 変更差分（git diff 27bc45ec..working tree、tasks.md、round-3 所見適用後）

```diff
diff --git a/.reviewcompass/specs/workflow-management/tasks.md b/.reviewcompass/specs/workflow-management/tasks.md
index f66a3c4d..513632f5 100644
--- a/.reviewcompass/specs/workflow-management/tasks.md
+++ b/.reviewcompass/specs/workflow-management/tasks.md
@@ -43,7 +43,7 @@ language: ja
   - `stages/in-progress/README.md`
   - `stages/completed/.gitkeep`
   - `stages/completed/README.md`
-  - `docs/logs/README.md`（`workflow-precheck.log` の所在説明、初版は空ログ）
+  - `docs/logs/README.md`（`workflow-precheck.log` の所在説明、初版は空ログ。ログの現行書き出し先は `.reviewcompass/runtime/logs/`、2026-06-12 配置規約 PLC-DEC-004〜005 反映。既存配置は凍結保全）
   - `docs/reviews/README.md`（`reopen-classification-<日付>.md` の所在説明）
   - `templates/review/reopen_classification_template.md`（reopen 種別判定根拠ファイルの雛形＝空の骨格を配置。内容の確定は T-007 が担い、本ファイルの成果物所有は T-001 単独、A-010 対処 案 2 2026-05-28）
   - `docs/operations/WORKFLOW_MANAGEMENT.md`（アプリ側規約節を追記、計画書 §5.4〜§5.8 由来）
@@ -100,7 +100,7 @@ language: ja
 
 - **対応設計節**：design.md §軽量版検査スクリプトモデル §1〜§4、§主要な設計判断 判断 2 ／ 判断 3 ／ 判断 8
 - **対応要件**：Requirement 2 受入 1〜5、Requirement 4 受入 2 ／ 3（fail-closed と独立走行）、Requirement 8 受入 6〜8（feature 一覧解決・整合検査・立ち上げ案内）、Requirement 9 受入 2 ／ 5（drafting-before-review と下流再展開判定）
-- **責務**：`tools/check-workflow-action.py` を Python で実装。3 サブコマンド（`spec-set <feature> <phase> <stage> <new_value> [--rationale "..."]` ／ `commit --rationale "..."` ／ `push --rationale "..."`）と next サブコマンド、`--json` 出力オプションを提供。next サブコマンドは標準のワークフロー遷移入口として `workflow_state`、`stages/in-progress/`、reopen pending、post-write-verification pending、上流成果物が下流成果物より新しい状態を読み、次作業を返す。完了済み workflow でも、intent → feature-partitioning、feature-partitioning → requirements、requirements → design、design → tasks、tasks → implementation の順で上流更新後の再展開漏れを `upstream_recheck` として返す。`docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml` を読み、判定点ごとの `required_disciplines` と `required_inputs` を `next_action` に含める。このマップは判定点ごとの `effective prompt` 生成に使う元資料の正本である。`next` は判定点ごとの元資料を 1 本の prompt に束ね、`.reviewcompass/effective-prompts/` に保存し、`next_action.effective_prompt` の `effective_prompt_path`、`effective_prompt_sha256`、`effective_prompt_loaded` として返す。元資料を読めない場合は `effective_prompt_loaded: false` とし、`DEVIATION` で fail-closed する。`tools/api_providers/run_role.py` と `tools/api_providers/run_review.py` は review-run の `rounds.yaml` に `effective_prompt_path` と `effective_prompt_sha256` を記録する。後追い intent を既存システムへ適用する reopen では、pending_gates が triad-review を指していても、対応 phase の `drafting_completed_gates` または `completed_gates` に `stages/<phase>.yaml#drafting` がなければ、next は triad-review ではなく `run_reopen_drafting` を返す。verdict 3 値（OK／WARN／DEVIATION）と exit code（0 ／ 1 ／ 2）の対応。`completion_predicate` 述語集合 7 値（`artifact_exists` ／ `artifact_exists_and_sections_present` ／ `artifact_exists_and_sections_present_and_author_reviewer_distinct` ／ `all_features_drafting_and_triad_review_completed` ／ `cross_spec_alignment_passed` ／ `explicit_human_approval_recorded` ／ `depends_on_resolves_correctly`）の判定ロジックを符号化。post-write target detection と manifest verification を実装契約として扱い、completed manifest の `target_files`、`target_sha256`、`required_verifiers`、`verifications[]`、`unresolved_substantive_findings` を検査する。feature 一覧と機能順は `feature-dependency.yaml` の `feature_order` キーから解決する（ツール実行時のカレントディレクトリ基準で `.reviewcompass/feature-dependency.yaml` → `stages/feature-dependency.yaml` → `feature-dependency.yaml` の順、最初に存在した 1 ファイルのみ、遡上探索なし。`resolve_feature_order`。design §機能依存マップモデル §7、2026-06-12 反映）。ファイル不在・`feature_order` 未定義は `next_action.kind: feature_definition_required`（verdict OK、exit 0）で intent／feature-partitioning の実施を案内し、探索で選ばれた 1 ファイルが読めない場合（パース不能・空・最上位が連想配列でない場合を含む。値の整合検査より先に判定）と `feature_order` と `depends_on` の整合違反（依存先行違反・循環、`validate_feature_order_consistency`）は `next_action.kind: unknown`・`reasons` 列挙・DEVIATION（exit 2）で遮断する（パース不能は破損ファイルのパスと内容確認を促す理由、空の場合は `feature_order` の記録を促す理由を含める）。fail-closed の既定（YAML パースエラー（段集合・feature-dependency とも） ／ 証跡欠落 ／ 必須フィールド欠落 ／ `feature_order` 整合違反で遮断。feature-dependency.yaml の不在・未定義のみ立ち上げ案内として OK）を全面採用（パース不能の遮断分離は MLE-DEC-005 により本契約へ反映、FUP-2026-06-12-001 解消、2026-06-12）。`docs/logs/workflow-precheck.log` への追記、出力形式は `[VERDICT]` ／ `[ACTION]` ／ `[REASON]` ／ `[CURRENT STATE]` の 4 ブロック大括弧付きラベル形式
+- **責務**：`tools/check-workflow-action.py` を Python で実装。3 サブコマンド（`spec-set <feature> <phase> <stage> <new_value> [--rationale "..."]` ／ `commit --rationale "..."` ／ `push --rationale "..."`）と next サブコマンド、`--json` 出力オプションを提供。next サブコマンドは標準のワークフロー遷移入口として `workflow_state`、`stages/in-progress/`、reopen pending、post-write-verification pending、上流成果物が下流成果物より新しい状態を読み、次作業を返す。完了済み workflow でも、intent → feature-partitioning、feature-partitioning → requirements、requirements → design、design → tasks、tasks → implementation の順で上流更新後の再展開漏れを `upstream_recheck` として返す。`docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml` を読み、判定点ごとの `required_disciplines` と `required_inputs` を `next_action` に含める。このマップは判定点ごとの `effective prompt` 生成に使う元資料の正本である。`next` は判定点ごとの元資料を 1 本の prompt に束ね、`.reviewcompass/runtime/effective-prompts/` に保存し（旧 `.reviewcompass/effective-prompts/` からの変更は 2026-06-12 配置規約 PLC-DEC-004・009〜011 反映、旧パス読み取り互換は P3 まで維持）、`next_action.effective_prompt` の `effective_prompt_path`、`effective_prompt_sha256`、`effective_prompt_loaded` として返す。元資料を読めない場合は `effective_prompt_loaded: false` とし、`DEVIATION` で fail-closed する。`tools/api_providers/run_role.py` と `tools/api_providers/run_review.py` は review-run の `rounds.yaml` に `effective_prompt_path` と `effective_prompt_sha256` を記録する。後追い intent を既存システムへ適用する reopen では、pending_gates が triad-review を指していても、対応 phase の `drafting_completed_gates` または `completed_gates` に `stages/<phase>.yaml#drafting` がなければ、next は triad-review ではなく `run_reopen_drafting` を返す。verdict 3 値（OK／WARN／DEVIATION）と exit code（0 ／ 1 ／ 2）の対応。`completion_predicate` 述語集合 7 値（`artifact_exists` ／ `artifact_exists_and_sections_present` ／ `artifact_exists_and_sections_present_and_author_reviewer_distinct` ／ `all_features_drafting_and_triad_review_completed` ／ `cross_spec_alignment_passed` ／ `explicit_human_approval_recorded` ／ `depends_on_resolves_correctly`）の判定ロジックを符号化。post-write target detection と manifest verification を実装契約として扱い、completed manifest の `target_files`、`target_sha256`、`required_verifiers`、`verifications[]`、`unresolved_substantive_findings` を検査する。feature 一覧と機能順は `feature-dependency.yaml` の `feature_order` キーから解決する（ツール実行時のカレントディレクトリ基準で `.reviewcompass/feature-dependency.yaml` → `stages/feature-dependency.yaml` → `feature-dependency.yaml` の順、最初に存在した 1 ファイルのみ、遡上探索なし。`resolve_feature_order`。design §機能依存マップモデル §7、2026-06-12 反映）。ファイル不在・`feature_order` 未定義は `next_action.kind: feature_definition_required`（verdict OK、exit 0）で intent／feature-partitioning の実施を案内し、探索で選ばれた 1 ファイルが読めない場合（パース不能・空・最上位が連想配列でない場合を含む。値の整合検査より先に判定）と `feature_order` と `depends_on` の整合違反（依存先行違反・循環、`validate_feature_order_consistency`）は `next_action.kind: unknown`・`reasons` 列挙・DEVIATION（exit 2）で遮断する（パース不能は破損ファイルのパスと内容確認を促す理由、空の場合は `feature_order` の記録を促す理由を含める）。fail-closed の既定（YAML パースエラー（段集合・feature-dependency とも） ／ 証跡欠落 ／ 必須フィールド欠落 ／ `feature_order` 整合違反で遮断。feature-dependency.yaml の不在・未定義のみ立ち上げ案内として OK）を全面採用（パース不能の遮断分離は MLE-DEC-005 により本契約へ反映、FUP-2026-06-12-001 解消、2026-06-12）。`.reviewcompass/runtime/logs/workflow-precheck.log` への追記（旧 `docs/logs/workflow-precheck.log` からの変更は同配置規約反映。commit 承認記録も同様に `.reviewcompass/runtime/approvals/commit-approval.json` へ〔旧 `.reviewcompass/approvals/commit-approval.json`〕）、出力形式は `[VERDICT]` ／ `[ACTION]` ／ `[REASON]` ／ `[CURRENT STATE]` の 4 ブロック大括弧付きラベル形式。**凍結期（P3 まで）の責務（2026-06-12 配置規約反映、正本は design §実行時生成物の凍結期（P3 まで）の扱い）**：実行時生成物 3 パス（検査ログ・effective prompt・commit 承認記録）の書き込みは常に新配置とし、旧配置（`docs/logs/workflow-precheck.log`・`.reviewcompass/effective-prompts/`・`.reviewcompass/approvals/commit-approval.json`）への新規書き込みを行わない（凍結契約。効力発生は P1 実装反映コミット＝書き込み先切替と同時。互換の終了は P3 の専用 reopen における設計改訂として扱い、暗黙の終了はない）。読み取りは新配置優先・旧配置フォールバック（**新→旧の順**、3 パスとも P3 まで）。新旧いずれにも記録がない場合は各ツールの既存挙動（検査ログの初回新規作成、effective prompt 元資料欠落の DEVIATION fail-closed、commit 承認記録不在のガード遮断）に従い、本配置変更はそれらの挙動を変えない
 - **前提タスク**：T-001、T-002、T-003
 - **成果物**：
   - `tools/check-workflow-action.py`（argparse 定義 ＋ 3 サブコマンド ＋ `--json` ＋ ログ追記）
@@ -115,7 +115,7 @@ language: ja
   2. 述語 7 値すべてが正常系で OK、異常系（証跡欠落 ／ 必須節欠落 ／ 異名不成立 等）で DEVIATION を返す
   3. YAML パースエラー時に DEVIATION（exit 2）を返す（fail-closed）
   4. `--rationale` が `commit` ／ `push` で必須引数として強制される（省略時はエラー）。`spec-set` の `--rationale`（任意）を省略した場合もログ記録が正しく行われる（F-013 対処 2026-05-28）
-  5. ログ追記が `docs/logs/workflow-precheck.log` に発生、4 ブロックラベル形式と JSON 形式の両方が正しく出力される
+  5. ログ追記が `.reviewcompass/runtime/logs/workflow-precheck.log` に発生し、4 ブロックラベル形式と JSON 形式の両方が正しく出力される。実行時生成物 3 パス（検査ログ・effective prompt・commit 承認記録）それぞれについて、(1) 新配置への書き込み、(2) 旧配置への新規書き込みが発生しないこと、(3) 旧パスにしか記録がない場合の新→旧フォールバック読み取り、(4) 新旧両方に記録がある競合時に新配置が採用されること（design 契約「新→旧の順」の直接検証）、(5) 凍結済み旧成果物の不変性（P1 実装反映コミット以降に旧既存ファイルが変更・削除されていないこと）、の凍結期挙動が機械検証される（2026-06-12 配置規約反映、観点 4・5 は triad-review round-3 所見の適用）
   6. `explicit_human_approval_recorded` 述語は `actor=proxy_model` の場合 `reviewcompass.yaml#human_proxy.proxy_allowed` を参照して代行可否を機械判定する（条件を満たさなければ DEVIATION）。`depends_on_resolves_correctly` 述語は値域チェック（依存先の解決可能性）のみを担い、依存先の変更検知と recheck 更新発火は別機構（フェーズ 2 宿題、DVT-W007）であることを境界テストで明示する（A-004／A-006 対処 2026-05-28）
   7. review-run の proxy_model 判断代行ゲートは、`approval-proxy-<日付>.yaml`、`proxy-decisions/<finding-id>.decision.yaml`、decision prompt、元 review raw、raw response、候補案、採用案、判断理由、最終ラベルを検査し、欠落または triage との不一致があれば DEVIATION にする。proxy_model 代行は実装方針判断に限定し、コミット・プッシュ・spec.json 更新・フェーズ移行には使わない
   8. post-write-verification pending の検出、completed manifest の sha 一致、verifier ごとの全対象 coverage、未解決本質的指摘 0 件が機械検証される
@@ -123,7 +123,7 @@ language: ja
   10. `WORKFLOW_DISCIPLINE_MAP.yaml` から判定点ごとの `required_disciplines` と `required_inputs` を返せる
   11. `next` は `effective_prompt_path`、`effective_prompt_sha256`、`effective_prompt_loaded` を返し、元資料欠落時は `DEVIATION` で fail-closed する
   12. review-run は `rounds.yaml` に `effective_prompt_path` と `effective_prompt_sha256` を記録できる
-- **テスト要件**：3 サブコマンド × 各 verdict 3 値 = 9 ケース、`next` サブコマンドの通常 workflow／reopen pending／post-write-verification pending／upstream_recheck ケース、述語 7 値の正常系 ／ 異常系テスト、YAML パースエラーの fail-closed テスト、`--rationale` 必須化テスト（commit／push）＋ `spec-set` 省略時ログ記録テスト（F-013）、ログ追記テスト、4 ブロックラベル形式 ／ JSON 出力テスト、`explicit_human_approval_recorded` の proxy_model 代行可否テスト（proxy_allowed 満たす／満たさないの 2 ケース、A-004）、`depends_on_resolves_correctly` の境界テスト（値域チェックのみで変更検知しないことの確認、A-006）、post-write target detection と manifest verification の正常系／sha 不一致／coverage 不足／未解決本質的指摘ありテスト、proxy_model 判断代行ゲートの正常系／raw 欠落／候補案欠落／採用案欠落／判断理由欠落／triage 不一致の fail-closed テスト、intent 更新後に feature-partitioning 確認を返すテスト、requirements 更新後に design 再確認を返すテスト、tasks 更新後に implementation 再確認を返すテスト、triad-review pending かつ drafting 未完了なら `run_reopen_drafting` を返すテスト、`WORKFLOW_DISCIPLINE_MAP.yaml` の `required_disciplines`／`required_inputs` 反映テスト、`effective_prompt_path`／`effective_prompt_sha256`／`effective_prompt_loaded` の JSON 出力テスト、effective prompt 元資料欠落時の fail-closed テスト、`rounds.yaml` への effective prompt 記録テスト、feature_order 外出し・探索順・立ち上げ案内（feature_definition_required）・整合検査・対象アプリ独自 feature 構成での next 動作テスト（2026-06-12 反映、cde1f5c で実装済み）、feature-dependency.yaml パース不能・空・非連想配列の遮断テスト（`next_action.kind: unknown`・verdict DEVIATION・exit 2 を検証し、`reasons` に対象ファイルパスと、パース不能・非連想配列では内容確認を促す文言、空では `feature_order` の記録を促す文言が含まれることを検証）と、不在・未定義の案内維持テスト（`next_action.kind: feature_definition_required`・verdict OK・exit 0 を検証）（MLE-DEC-005、仕様確定後に TDD で実装。検証粒度の明記は triad-review 同根所見対処）
+- **テスト要件**：3 サブコマンド × 各 verdict 3 値 = 9 ケース、`next` サブコマンドの通常 workflow／reopen pending／post-write-verification pending／upstream_recheck ケース、述語 7 値の正常系 ／ 異常系テスト、YAML パースエラーの fail-closed テスト、`--rationale` 必須化テスト（commit／push）＋ `spec-set` 省略時ログ記録テスト（F-013）、ログ追記テスト、4 ブロックラベル形式 ／ JSON 出力テスト、`explicit_human_approval_recorded` の proxy_model 代行可否テスト（proxy_allowed 満たす／満たさないの 2 ケース、A-004）、`depends_on_resolves_correctly` の境界テスト（値域チェックのみで変更検知しないことの確認、A-006）、post-write target detection と manifest verification の正常系／sha 不一致／coverage 不足／未解決本質的指摘ありテスト、proxy_model 判断代行ゲートの正常系／raw 欠落／候補案欠落／採用案欠落／判断理由欠落／triage 不一致の fail-closed テスト、intent 更新後に feature-partitioning 確認を返すテスト、requirements 更新後に design 再確認を返すテスト、tasks 更新後に implementation 再確認を返すテスト、triad-review pending かつ drafting 未完了なら `run_reopen_drafting` を返すテスト、`WORKFLOW_DISCIPLINE_MAP.yaml` の `required_disciplines`／`required_inputs` 反映テスト、`effective_prompt_path`／`effective_prompt_sha256`／`effective_prompt_loaded` の JSON 出力テスト、effective prompt 元資料欠落時の fail-closed テスト、`rounds.yaml` への effective prompt 記録テスト、**凍結期挙動テスト（実行時生成物 3 パス × 5 観点＝計 15 観点：新配置への書き込み／旧配置への新規書き込みが発生しないこと／旧パスにしか記録がない場合の新→旧フォールバック読み取り／新旧両方に記録がある競合時に新配置が採用されること〔新旧に異なる内容を置き、新配置の内容が採用されることを 3 パスそれぞれで検証。design 契約「新→旧の順」の直接検証〕／凍結済み旧成果物の不変性〔P1 実装反映コミット以降に旧 3 パスの既存ファイルが変更・削除されていないことを git 追跡履歴で検出。conformance-evaluation の凍結違反検出と同一判定規則〕。境界条件として、観点 2 が凍結の効力発生時点〔P1 実装反映コミット以後の旧書き込み不在〕の検証を兼ねること、観点 3 のフォールバックが設定・条件分岐等で暗黙に無効化されないことを検証対象に含める。2026-06-12 配置規約反映、観点 4・5 は triad-review round-3 所見の適用、TDD 先行）**、feature_order 外出し・探索順・立ち上げ案内（feature_definition_required）・整合検査・対象アプリ独自 feature 構成での next 動作テスト（2026-06-12 反映、cde1f5c で実装済み）、feature-dependency.yaml パース不能・空・非連想配列の遮断テスト（`next_action.kind: unknown`・verdict DEVIATION・exit 2 を検証し、`reasons` に対象ファイルパスと、パース不能・非連想配列では内容確認を促す文言、空では `feature_order` の記録を促す文言が含まれることを検証）と、不在・未定義の案内維持テスト（`next_action.kind: feature_definition_required`・verdict OK・exit 0 を検証）（MLE-DEC-005、仕様確定後に TDD で実装。検証粒度の明記は triad-review 同根所見対処）
 
 ### T-005：起草者と判定者の分離 機械検査
 
```
