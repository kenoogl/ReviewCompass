# proxy 命名整合の変更 diff（変更前→後）

下記は今回の検証対象の実変更（git diff）。target file 全文は別添だが、実際に変わったのはこの diff の範囲のみ。レビューはこの変更が「実装コードの正本形（proxy-approval.yaml / approved_by + decision_scope）」と一致するかを精査すること。

```diff
diff --git a/.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md b/.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md
index 5e5da25e..1cbb029d 100644
--- a/.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md
+++ b/.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md
@@ -203,7 +203,7 @@ variant が未確定、または role 割当が曖昧な場合は review-run を
 1. メインセッション LLM は raw レビューを集約し、三段階トリアージの下書きを作る。parsed YAML だけでなく raw response も読み、同根所見をまとめ、`must-fix` ／ `should-fix` ／ `leave-as-is` の候補を作る
 2. メインセッション LLM は重要件ごとに、平易な問題説明、候補案、各案の利点と弱点、後段影響、推薦案を作る
 3. proxy_model は重要件の採用案・判断理由・最終ラベルを決定する。実装は担当しない
-4. メインセッション LLM は proxy_model の raw response を保存し、`proxy-decisions/<finding-id>.decision.yaml` と `approval-proxy-<日付>.yaml` に構造化する
+4. メインセッション LLM は proxy_model の raw response を保存し、`proxy-decisions/<finding-id>.decision.yaml` と `proxy-approval.yaml` に構造化する
 5. 機械ガードは proxy decision の充足を検査する。未判断、raw 欠落、候補案欠落、採用案欠落、判断理由欠落、triage 最終ラベルとの不一致があれば実装へ進まない
 6. メインセッション LLM は機械ガード通過後、採用された修正だけを TDD で実装する
 7. コミット・プッシュ・spec.json 更新・フェーズ移行は人間の明示承認を要求する。proxy_model はこれらの不可逆操作を代行しない
@@ -232,7 +232,7 @@ variant が未確定、または role 割当が曖昧な場合は review-run を
 - `proxy-decisions/<finding-id>.prompt.md`：proxy_model に渡した判断材料
 - `proxy-decisions/<finding-id>.raw.txt`：proxy_model の生応答
 - `proxy-decisions/<finding-id>.decision.yaml`：採用案、判断理由、最終ラベル、棄却案理由
-- `approval-proxy-<日付>.yaml`：実装着手を許可する proxy approval record
+- `proxy-approval.yaml`：実装着手を許可する proxy approval record
 
 **並列化可能な単位**：
 
diff --git a/.reviewcompass/specs/workflow-management/design.md b/.reviewcompass/specs/workflow-management/design.md
index 89675bc8..532d943c 100644
--- a/.reviewcompass/specs/workflow-management/design.md
+++ b/.reviewcompass/specs/workflow-management/design.md
@@ -246,10 +246,10 @@ review-run 後の重要件判断は、approval 段の承認ではなく、triad-
     <finding-id>.prompt.md
     <finding-id>.raw.txt
     <finding-id>.decision.yaml
-  proxy-decision-bundle-<日付>.yaml
+  proxy-approval.yaml
 ```
 
-`proxy-decisions/<finding-id>.decision.yaml` は最低限、`finding_id`、`decided_by: proxy_model`、`proxy_model_id`、`selected_option`、`final_label`、`rationale`、`rejected_options`、`raw_response_path` を持つ。`proxy-decision-bundle-<日付>.yaml` は対象 review-run、対象 finding、参照した decision、summary/triage 提示済みフラグを束ねる。proxy decision bundle は承認 record ではなく、human-only approval、commit、push、`spec.json` 更新、phase / gate completion、reopen finalize を許可しない。
+`proxy-decisions/<finding-id>.decision.yaml` は最低限、`finding_id`、`approved_by: proxy_model`、`proxy_model_id`、`selected_option`、`final_label`、`rationale`、`rejected_options`、`raw_response_path` を持つ。`proxy-approval.yaml` は対象 review-run、対象 finding、参照した decision、summary/triage 提示済みフラグを束ねる。proxy approval は `decision_scope: proxy_allowed` の範囲（所見トリアージ・修正方針判断）に限った承認であり、human-only approval、commit、push、`spec.json` 更新、phase / gate completion、reopen finalize は許可しない。
 
 proxy decision の監査性を保つため、decision は `decision_prompt_path`、`source_raw_paths`、`candidate_options` も持つ。`decision_prompt_path` は proxy_model に渡した prompt 証跡、`source_raw_paths` は元 review raw、`candidate_options` は proxy_model に提示された候補案セットである。機械ガードは、これらの参照先が存在し、`candidate_options` が空でないことを確認する。現行の軽量ガードは、`proxy_model_id` の文字列一致、decision file の `finding_id` 一致、`final_label` 一致、prompt/raw/候補案証跡の存在を検査する。API 署名や暗号学的な生成元証明は将来課題とする。
 
diff --git a/.reviewcompass/specs/workflow-management/tasks.md b/.reviewcompass/specs/workflow-management/tasks.md
index b599f1fa..9dec1090 100644
--- a/.reviewcompass/specs/workflow-management/tasks.md
+++ b/.reviewcompass/specs/workflow-management/tasks.md
@@ -125,7 +125,7 @@ language: ja
   4. `--rationale` が `commit` ／ `push` で必須引数として強制される（省略時はエラー）。`spec-set` の `--rationale`（任意）を省略した場合もログ記録が正しく行われる（F-013 対処 2026-05-28）
   5. ログ追記が `.reviewcompass/runtime/logs/workflow-precheck.log` に発生し、4 ブロックラベル形式と JSON 形式の両方が正しく出力される。実行時生成物 3 パス（検査ログ・effective prompt・commit 承認記録）それぞれについて、(1) 新配置への書き込み、(2) 旧配置への新規書き込みが発生しないこと、(3) 旧パスにしか記録がない場合の新→旧フォールバック読み取り、(4) 新旧両方に記録がある競合時に新配置が採用されること（design 契約「新→旧の順」の直接検証）、(5) 凍結済み旧成果物の不変性（P1 実装反映コミット以降に旧既存ファイルが変更・削除されていないこと）、の凍結期挙動が機械検証される（2026-06-12 配置規約反映、観点 4・5 は triad-review round-3 所見の適用）
   6. `explicit_human_approval_recorded` 述語は `actor=proxy_model` の場合 `reviewcompass.yaml#human_proxy.proxy_allowed` を参照して代行可否を機械判定する（条件を満たさなければ DEVIATION）。`depends_on_resolves_correctly` 述語は値域チェック（依存先の解決可能性）のみを担い、依存先の変更検知と recheck 更新発火は別機構（フェーズ 2 宿題、DVT-W007）であることを境界テストで明示する（A-004／A-006 対処 2026-05-28）
-  7. review-run の proxy_model 判断代行ゲートは、`approval-proxy-<日付>.yaml`、`proxy-decisions/<finding-id>.decision.yaml`、decision prompt、元 review raw、raw response、候補案、採用案、判断理由、最終ラベルを検査し、欠落または triage との不一致があれば DEVIATION にする。proxy_model 代行は実装方針判断に限定し、コミット・プッシュ・spec.json 更新・フェーズ移行には使わない
+  7. review-run の proxy_model 判断代行ゲートは、`proxy-approval.yaml`、`proxy-decisions/<finding-id>.decision.yaml`、decision prompt、元 review raw、raw response、候補案、採用案、判断理由、最終ラベルを検査し、欠落または triage との不一致があれば DEVIATION にする。proxy_model 代行は実装方針判断に限定し、コミット・プッシュ・spec.json 更新・フェーズ移行には使わない
   8. post-write-verification pending の検出、completed manifest の sha 一致、verifier ごとの全対象 coverage、未解決本質的指摘 0 件が機械検証される
   9. triad-review が pending でも drafting が未完了なら、next が `run_reopen_drafting` を返し、review を先に実施しない
   10. `WORKFLOW_DISCIPLINE_MAP.yaml` から判定点ごとの `required_disciplines` と `required_inputs` を返せる
diff --git a/tests/tools/test_session_record_contract.py b/tests/tools/test_session_record_contract.py
index df1dd31b..241828e6 100644
--- a/tests/tools/test_session_record_contract.py
+++ b/tests/tools/test_session_record_contract.py
@@ -88,7 +88,7 @@ def test_proxy_review_decision_workflow_is_canonicalized():
 
   assert "review-run 後の proxy_model 判断代行" in requirements
   assert "proxy decision" in design
-  assert "approval-proxy-<日付>.yaml" in design
+  assert "proxy-approval.yaml" in design
   assert "candidate_options" in design
   assert "source_raw_paths" in design
   assert "proxy_model 判断代行ゲート" in tasks

```
