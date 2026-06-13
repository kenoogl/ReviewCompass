# レビュー対象：reopen R-0（review-wave-summary-command）workflow-management design 変更

## 0. variant 選定理由

- variant：`implementation_review_independent_3way`（primary=claude-sonnet-4-6、adversarial=gpt-5.5、judgment=gemini-3.1-pro-preview）。Claude Code 操縦時の API 既定（SESSION_WORKFLOW_GUIDE §3.3 (a-3)）。利用者承認 2026-06-14「許可。自律的に進める／続けて」。

## 1. レビューの位置付け

reopen R-0（分類記録 `docs/reviews/reopen-classification-2026-06-14-wm-review-wave-summary-command.md`）の第3過程、workflow-management design フェーズの triad-review。requirements は approval 済み（Requirement 10、round-2 収束）。本変更は Requirement 10 の設計（要約コマンドのモデル節と要件対応表）を design.md に追加するもの。実装は本フェーズ確定後に tasks → implementation で TDD により行う（現時点で実装は未着手）。

## 2. 変更内容（design.md）

### 2.1 新設：§review-wave 要約コマンドモデル（Req 10）

> #### 1. 配置と原則（Req 10 受入 1・5）
> - サブコマンド `review-wave-summary` を `tools/check-workflow-action.py` に追加（next／spec-set／commit と同じ CLI 体系、Req 2 のサブコマンド）。
> - 読み取りに徹し spec.json・フェーズ状態・トリアージを書き換えない（Req 3 受入 5・Req 4 受入 1）。書き込みは自身の要約出力に限る。
>
> #### 2. 読み取り元と指標の算出定義（Req 10 受入 1・2）
> - feature coverage＝各 feature spec.json の workflow_state（全 phase×stage の true 比率・全 phase approval 済みか、FEATURE_ORDER 全 feature）。
> - phase／stage 状態＝workflow_state の真偽展開。
> - triage 未解決／draft／human_required＝review-run の triage.yaml 群（evidence/review-runs/*/triage.yaml、互換で旧 _cross_feature/reviews/*/triage.yaml）を走査、decision_status で集計（unresolved＝decided 以外）。
> - recheck 状態＝各 feature spec.json の recheck。
> - 依存状況＝feature-dependency.yaml の feature_order と未充足依存（上流未 approval）。
> - carry-forward 未消化＝learning/workflow/carry-forward-register/*.yaml の status≠resolved 件数。
> - 既存関数（load_all_feature_specs・feature_order 解決・collect_recheck_items・review_triage 集計）を再利用、二重定義回避。
>
> #### 3. 出力形式とスキーマ（Req 10 受入 3）
> - --json で JSON、既定 Markdown。同一情報源から生成し情報同等。
> - JSON 安定スキーマ（トップレベル）：schema_version, generated_at, status(ok/insufficient), features[]（name・coverage・phases・recheck）, triage（unresolved・draft・human_required）, dependencies（feature_order・unmet）, carry_forward（unresolved）, errors[]。キー名・型は固定、追加は後方互換。
>
> #### 4. fail-closed（Req 10 受入 4）
> - 記録が解析不能・欠落（範囲は Req 2 受入 4）→ status: insufficient、errors[] 列挙、非ゼロ終了コード（既定 2）、Markdown は不完全を明示。部分集計を status ok にしない。
>
> #### 5. 保存（Req 10 受入 5）
> - 既定は標準出力。--save/--out 指定時のみ _cross_feature/reviews/ へ自身の要約出力を書き出す（状態変更でない）。

### 2.2 要件と設計の対応表に Req 10 の 5 行を追加（受入 1〜5 → 上記各節）。

## 3. レビュー観点（criteria: design_r10_review_wave_summary_command）

1. requirements の Requirement 10（受入 1〜5）を設計が過不足なく実現しているか（特に受入 4 の機械可読 fail-closed シグナル＝非ゼロ終了コード＋JSON status）。
2. 読み取り元と指標の算出定義が一意で実装可能か。既存関数の再利用範囲が妥当か。
3. JSON 安定スキーマのキー・型が機械処理に十分で、Markdown と情報同等か。
4. 読み取り専用の責務境界（Req 3 受入 5・Req 4 受入 1）と保存（自身の出力のみ）の設計が破綻していないか。
5. 既存設計（§軽量版検査スクリプトモデル §4 の fail-closed、§機能依存マップモデルの feature_order）との整合。
6. tasks／implementation へ渡すべき未確定事項（スキーマの最終キー名など）の明示漏れがないか。
