# レビュー対象：reopen D-0（placement-p1-path-contracts）workflow-management design 変更

## 0. variant 選定理由（実行前ゲートの記録）

- 使用 variant：`implementation_review_independent_3way`（context: triad_review、API 3 社独立）
- 役割：primary=anthropic-api/claude-sonnet-4-6、adversarial=openai-api/gpt-5.5、judgment=gemini-api/gemini-3.1-pro-preview
- 選定理由：同じ配置規約 P1 の ce reopen（requirements〜implementation）と同一構成（利用者承認 2026-06-12「承認承認」。正本は SESSION_WORKFLOW_GUIDE §3.3 (a-3)）

## 1. レビューの位置付け

reopen D-0（分類記録 `docs/reviews/reopen-classification-2026-06-12-placement-p1-path-contracts.md`）の
第3過程、workflow-management design フェーズの triad-review。第2過程（正本修正、コミット 41720094）で
design 5 箇所のパス契約を runtime 区画へ変更済み。requirements は 3 パスのいずれにも言及せず不変（分類記録のとおり）。

変更の趣旨（配置規約 PLC-DEC-004〜005・009〜011）：実行時生成物を `.reviewcompass/runtime/` 区画へ集約する。

- 検査ログ：`docs/logs/workflow-precheck.log` → `.reviewcompass/runtime/logs/workflow-precheck.log`
- effective prompt（判定点ごとの統合プロンプト）：`.reviewcompass/effective-prompts/` → `.reviewcompass/runtime/effective-prompts/`
- commit 承認記録：`.reviewcompass/approvals/commit-approval.json` → `.reviewcompass/runtime/approvals/commit-approval.json`
- いずれも由来注記付き、既存分は旧置き場で凍結、旧パス読み取り互換は P3 まで維持（暗黙の終了はない）

現時点で実装は旧パスへ書く挙動のまま（意図的・正順）。implementation 段で TDD により書き込み先変更と
読み取り互換を実装する（ce reopen と同じ進め方。ce 側は完了済み＝コミット dc5708fa・289cc00c が先行事例）。

## 2. レビュー観点

1. 5 箇所の変更が配置規約の決定（PLC-DEC-004〜005・009〜011）と一致しているか
2. 由来注記・凍結・読み取り互換（P3 まで）の明記が一貫しているか（ce reopen で確定した形式との整合）
3. 変更漏れ：design 内に旧パス（docs/logs／.reviewcompass/effective-prompts／.reviewcompass/approvals）への
   現役参照（由来注記以外）が残っていないか
4. 機械検査・運用文書・テストへの波及が implementation 段の TDD で受けられる範囲に閉じているか
5. 例外系・境界条件（凍結の効力発生時点、読み取り互換の終了条件）

## 2.5 round-2 注記：round-1 所見の適用（proxy_model 判断、2026-06-12）

round-1 の 7 所見（3 同根クラスタ）は proxy_model（gemini-3.1-pro-preview、委任出典＝利用者発言「proxy_modelで自律実行」）が判断した
（証跡 `proxy-decisions/`・`approval-proxy-2026-06-12.yaml`）。

- W1（must-fix、ERROR3/WARN1/INFO1 同根）＝案 A 適用：design §全体構造に「実行時生成物の凍結期（P3 まで）の扱い」を新設し、
  3 パス共通の凍結契約（書き込み常時新配置・既存分凍結・効力発生＝P1 実装反映コミットと同時・3 パスとも P3 読み取り互換・
  暗黙終了なし）を正本化。3 箇所の由来注記から本節を参照し、effective prompt の注記には互換維持の文言を補記
- W2（leave-as-is）：PLC-DEC-005 は決定台帳の定義により「実行時ログ」専用で、effective prompt・commit 承認記録への
  非適用は正しい（現行の決定番号引用は正しい。「不一致」の見かけはレビュー対象文書 §1 の趣旨説明の不正確さに起因）
- W3（leave-as-is）：図ラベルの由来注記は本文注記を正本とする

round-2 は適用後本文の収束確認である。

## 2.6 round-3 注記：round-2 所見の適用（proxy_model 判断、2026-06-12）

round-2 の 3 所見（主役 INFO のみ、敵対役・判定役ゼロ）は proxy_model が判断した（証跡 `proxy-decisions/round-2/`・
`approval-proxy-2026-06-12-round-2.yaml`）。V2＝should-fix 適用：検査ログ注記の「上書き可能」に語義分離の補足
（ログ自体の再生成可否を指し、旧配置対象の凍結契約とはスコープが異なる旨）。V1・V3＝leave-as-is。
round-3 は適用後本文の収束確認である。

## 3. 変更差分（git diff 27bc45ec..working tree、design.md、round-2 所見適用後）

```diff
diff --git a/.reviewcompass/specs/workflow-management/design.md b/.reviewcompass/specs/workflow-management/design.md
index 6c43089a..451358a5 100644
--- a/.reviewcompass/specs/workflow-management/design.md
+++ b/.reviewcompass/specs/workflow-management/design.md
@@ -61,7 +61,7 @@
 │   ├── in-progress/                     # 進行中状態ファイル（Req 6、session 跨ぎ用）
 │   └── completed/                       # 完了済み手続きの記録
 ├── tools/check-workflow-action.py       # 検査スクリプト本体（Req 2、補助層 C 段階 2）
-├── docs/logs/workflow-precheck.log      # 検査結果のログ書き出し先（Req 2 受入 5 補強）
+├── .reviewcompass/runtime/logs/workflow-precheck.log  # 検査結果のログ書き出し先（Req 2 受入 5 補強。旧 docs/logs/ からの変更は 2026-06-12 配置規約 PLC-DEC-004〜005・009〜011 反映。凍結・読み取り互換は §実行時生成物の凍結期（P3 まで）の扱いを正本とする）
 ├── docs/reviews/reopen-classification-<日付>.md  # reopen 種別判定の根拠（Req 5 受入 5）
 ├── docs/operations/WORKFLOW_MANAGEMENT.md        # アプリ側規約（T-001 で配置、F-019 対処 2026-05-28）
 ├── docs/operations/WORKFLOW_PRECHECK.md          # ワークフロー事前検査の運用契約
@@ -82,12 +82,21 @@ graph TD
     Verdict -->|OK| Pass["不可逆操作の実行を許可"]
     Verdict -->|WARN| Warn["警告して継続"]
     Verdict -->|DEVIATION| Block["fail-closed で遮断<br>（Req 4 受入 3）"]
-    Pass --> Log["docs/logs/workflow-precheck.log<br>に検査結果を追記"]
+    Pass --> Log[".reviewcompass/runtime/logs/workflow-precheck.log<br>に検査結果を追記"]
     Block --> Log
 ```
 
 検査スクリプトは段集合 YAML、進行中状態ファイル、spec.json、持ち越し所見レジスタの 4 つを入力として読み、verdict（判定結果）を返す。verdict には OK／WARN／DEVIATION の 3 値を使う（actor=human の段で承認待ちのときは DEVIATION で止め、警告のみで継続できる軽微な未整合は WARN とする）。語彙と出力契約の正本は `docs/operations/WORKFLOW_PRECHECK.md` と `docs/operations/WORKFLOW_PRECHECK_DETAILS.md`、および検査スクリプト本体 `tools/check-workflow-action.py` の実装で、本設計は実装に合わせる方向で語彙を確定する。
 
+### 実行時生成物の凍結期（P3 まで）の扱い（2026-06-12 配置規約 P1）
+
+本機能の実行時生成物 3 パス（検査ログ `.reviewcompass/runtime/logs/workflow-precheck.log`〔旧 `docs/logs/workflow-precheck.log`〕、effective prompt `.reviewcompass/runtime/effective-prompts/`〔旧 `.reviewcompass/effective-prompts/`〕、commit 承認記録 `.reviewcompass/runtime/approvals/commit-approval.json`〔旧 `.reviewcompass/approvals/`〕）の凍結期共通契約を本節の正本とする：
+
+- **書き込みは常に新配置**。旧配置への新規書き込みは行わない（凍結契約）
+- **既存分は旧置き場で凍結**する（移動・上書き・追記をしない）。凍結の効力発生は P1 実装反映コミット（書き込み先切替）と同時であり、それ以前の旧配置への書き込みは現行実装の正規動作として凍結対象に含まれる
+- **旧パス読み取り互換は 3 パスとも P3 まで維持**する（新 → 旧の順）。既存証跡（rounds.yaml 等）が記録する旧 `effective_prompt_path` の参照は凍結された旧配置で解決できる
+- **互換の終了は P3 の専用 reopen における本設計の改訂として扱う**（暗黙の終了はない）
+
 ### 責務境界の明確化（Boundary Clarification）
 
 本機能が所有するのは **手続きの完了規則と検査スクリプト** であり、各機能の業務 artifact の所有権は持たない。
@@ -320,7 +329,7 @@ next サブコマンドは、`workflow_state` が全完了を示す場合でも
 
 next サブコマンドは、feature 一覧が解決できない場合（`feature-dependency.yaml` 不在または `feature_order` 未定義、対象アプリの初期状態を想定）は `feature_definition_required`（verdict OK）を返して intent／feature-partitioning の実施を案内し、`feature_order` と `depends_on` の整合違反（依存先行違反・循環）は `kind: unknown`／DEVIATION で遮断する（§機能依存マップモデル 7、2026-06-12 反映）。
 
-`docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml` は、判定点ごとに読み込む規律文書と入力資料の機械可読マップである。`default`、`by_kind`、`by_stage` は `next_action.required_disciplines` の元資料を定義し、`required_inputs` は対象 feature 文書、reopen 状態、review-run bundle、carry-forward register などの入力資料を定義する。`next` はこのマップを読み、現在の判定点に対応する `required_disciplines` と `required_inputs` を JSON に含める。判定点ごとの `effective prompt` は、このマップが示す元資料を 1 本へ束ねる生成物であり、マップ自体は複数元資料の正本である。`next` は生成した prompt を `.reviewcompass/effective-prompts/` に保存し、`next_action.effective_prompt` に `effective_prompt_path`、`effective_prompt_sha256`、`effective_prompt_loaded` を含める。元資料が読めない場合は `effective_prompt_loaded: false` として `DEVIATION` を返し、通常作業へ進ませない。API review-run では `run_role.py`／`run_review.py` が `rounds.yaml` に `effective_prompt_path` と `effective_prompt_sha256` を記録し、後続の raw response・triage・proxy decision と同じ review-run 証跡として追跡できるようにする。マップにない判定点は、規律読み込み規約が未定義の判定点として扱い、追加時は本マップへ登録する。
+`docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml` は、判定点ごとに読み込む規律文書と入力資料の機械可読マップである。`default`、`by_kind`、`by_stage` は `next_action.required_disciplines` の元資料を定義し、`required_inputs` は対象 feature 文書、reopen 状態、review-run bundle、carry-forward register などの入力資料を定義する。`next` はこのマップを読み、現在の判定点に対応する `required_disciplines` と `required_inputs` を JSON に含める。判定点ごとの `effective prompt` は、このマップが示す元資料を 1 本へ束ねる生成物であり、マップ自体は複数元資料の正本である。`next` は生成した prompt を `.reviewcompass/runtime/effective-prompts/` に保存し（旧 `.reviewcompass/effective-prompts/` からの変更は 2026-06-12 配置規約 PLC-DEC-004・009〜011 反映。実行時生成物の runtime 区画集約。旧パス読み取り互換は P3 まで維持し、凍結・互換の正本は §実行時生成物の凍結期（P3 まで）の扱い）、`next_action.effective_prompt` に `effective_prompt_path`、`effective_prompt_sha256`、`effective_prompt_loaded` を含める。元資料が読めない場合は `effective_prompt_loaded: false` として `DEVIATION` を返し、通常作業へ進ませない。API review-run では `run_role.py`／`run_review.py` が `rounds.yaml` に `effective_prompt_path` と `effective_prompt_sha256` を記録し、後続の raw response・triage・proxy decision と同じ review-run 証跡として追跡できるようにする。マップにない判定点は、規律読み込み規約が未定義の判定点として扱い、追加時は本マップへ登録する。
 
 post-write target detection と manifest verification は、`next` と `commit` の双方が参照する実装契約である。post-write-verification 対象の未コミット変更がある場合、`next` は通常 workflow ではなく post-write-verification pending を返す。completed manifest は `target_files` と現在内容の `target_sha256` が一致し、`required_verifiers` の各 verifier が `verifications[]` の単一エントリで全対象ファイルと同じ sha を覆い、`unresolved_substantive_findings` が 0 である場合だけ完了とみなす。
 
@@ -330,7 +339,7 @@ post-write target detection と manifest verification は、`next` と `commit`
 - `1`：WARN（警告を出すが継続可、利用者判断で進める）
 - `2`：DEVIATION（fail-closed で遮断、不可逆操作を許可しない）
 
-出力形式は人間可読の既定形式と、`--json` 指定時の JSON 形式の 2 種類。出力構造とログ形式は `docs/operations/WORKFLOW_PRECHECK_DETAILS.md` を正本参照する。人間可読既定の書式は `[VERDICT] OK ／ WARN ／ DEVIATION（exit N）` のように **大括弧付きラベル形式** で、`[VERDICT]`／`[ACTION]`／`[REASON]`／`[CURRENT STATE]` の 4 ブロックを順に出力する。判定結果はログ（`docs/logs/workflow-precheck.log`、上書き可能）に追記する。
+出力形式は人間可読の既定形式と、`--json` 指定時の JSON 形式の 2 種類。出力構造とログ形式は `docs/operations/WORKFLOW_PRECHECK_DETAILS.md` を正本参照する。人間可読既定の書式は `[VERDICT] OK ／ WARN ／ DEVIATION（exit N）` のように **大括弧付きラベル形式** で、`[VERDICT]`／`[ACTION]`／`[REASON]`／`[CURRENT STATE]` の 4 ブロックを順に出力する。判定結果はログ（`.reviewcompass/runtime/logs/workflow-precheck.log`、上書き可能＝ログファイル自体の再生成可否を指す。旧配置を対象とする凍結契約〔§実行時生成物の凍結期（P3 まで）の扱い〕とはスコープが異なる）に追記する。
 
 ### 3. 完了判定の述語集合（completion_predicate 値域）
 
@@ -1061,7 +1070,7 @@ self-improvement design §13.5 で本機能との接合面の詳細が定義さ
 2026-06-08 の機能横断 conformance check で、workflow-management の post-write verification、commit approval、audit trail、autonomous ledger に関する契約が、運用文書・規律・ゲート実装・テストにまたがって具体化されていることを確認した。本設計はその差分を実装由来契約として採用する。
 
 - post-write verification は、対象ファイルと検証結果の対応を commit 前に確認し、必要な検証記録がない変更を不可逆操作へ進ませないための境界である
-- commit approval は、利用者の明示指示、対象ファイル、ハッシュ、rationale を `.reviewcompass/approvals/commit-approval.json` に固定し、ガード付き commit の入力として扱う
+- commit approval は、利用者の明示指示、対象ファイル、ハッシュ、rationale を `.reviewcompass/runtime/approvals/commit-approval.json` に固定し、ガード付き commit の入力として扱う（旧 `.reviewcompass/approvals/` からの変更は 2026-06-12 配置規約 PLC-DEC-004・009〜011 反映。凍結・読み取り互換は §実行時生成物の凍結期（P3 まで）の扱いを正本とする）
 - audit trail は `check-workflow-action.py` と `guarded-git-commit.py` の verdict、理由、staged files、承認レコード状態を観測可能な証跡として残す
 - autonomous ledger は、進行中状態・未消化所見・承認済み不可逆操作を workflow の状態判断に反映し、自律進行と人間承認境界を混同しない
 
```
