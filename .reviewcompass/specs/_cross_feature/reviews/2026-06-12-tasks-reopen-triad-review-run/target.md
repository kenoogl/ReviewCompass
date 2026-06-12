# レビュー対象：reopen R-0 tasks 変更（配布側複数 LLM 入口契約のタスク仕様反映）

## 0. variant 選定理由（実行前ゲートの記録）

- 使用 variant：`implementation_review_independent_3way`（context: triad_review、API 3 社独立）
- 役割：primary=anthropic-api/claude-sonnet-4-6、adversarial=openai-api/gpt-5.5、judgment=gemini-api/gemini-3.1-pro-preview
- 選定理由：requirements・design フェーズの triad-review と同一構成（利用者承認済みの
  「Claude Code 操縦時の API 既定」）。

## 1. レビューの位置付け

reopen R-0（docs/reviews/reopen-classification-2026-06-12-multi-llm-entry-spec-reflection.md）第3過程の
tasks フェーズ triad-review。requirements・design は利用者 approval 済み。tasks.md の変更が、
承認済みの requirements（Requirement 8 受入 1〜3・6〜8）・design（§機能依存マップモデル §7、
XDI-WM-003）と整合し、タスク契約として検証可能かを確認する。実装コードの変更は含まない
（実装先行の追認）。tasks.md 本体の再作成・タスク分解の確定は行っていない（既存タスクの契約文言の
更新のみ。conformance-evaluation Requirement 12 受入 5 の境界に従う）。

## 2. 変更内容（workflow-management tasks.md）

### 2.1 T-002（機能依存マップ）の契約変更

- 語彙：`phase_order` → `feature_order`（旧称の由来注記参照を付記）
- スキーマ契約の代替（**MLE-DEC-002、2026-06-12 利用者決定**）：成果物
  「`stages/feature-dependency.schema.json`（パース仕様の正本）」を廃し、次へ置換：

> パース仕様の正本：`tools/check-workflow-action.py` の解決・整合検査の実装
> （`resolve_feature_order`・`validate_feature_order_consistency`・`depends_on` 解釈）と
> そのテスト（単純リスト構造 ／ 連想配列構造の許容、値域 `hard` ／ `review` の 2 値、
> それ以外は結論不能）。独立した JSON Schema ファイルは作成しない（MLE-DEC-002、
> 2026-06-12 利用者決定。当初計画の `stages/feature-dependency.schema.json` を実装検査で代替）

- 完了条件 3・4 を「スキーマで機械検証」から「検査ツールの実装とテストで機械検証」へ変更
- テスト要件の先頭を「スキーマ検証」から「パース仕様の実装検査テスト」へ変更
- 補足：7 機能の `features` 列挙は MLE-DEC-003（利用者決定）により
  `stages/feature-dependency.yaml` で実体化済み（T-002 完了条件 1 は現実と一致）

### 2.2 T-003（段集合 YAML）の参照語彙

`feature_order: feature-dependency.yaml#phase_order` 参照 2 箇所を `#feature_order` へ統一（意味不変）。

### 2.3 T-004（検査スクリプト本体）の契約追記

- 対応要件へ「Requirement 8 受入 6〜8（feature 一覧解決・整合検査・立ち上げ案内）」を追加
- 責務へ次を追加（requirements・design の確定文言と整合）：

> feature 一覧と機能順は `feature-dependency.yaml` の `feature_order` キーから解決する
> （ツール実行時のカレントディレクトリ基準で `.reviewcompass/feature-dependency.yaml` →
> `stages/feature-dependency.yaml` → `feature-dependency.yaml` の順、最初に存在した 1 ファイルのみ、
> 遡上探索なし。`resolve_feature_order`。design §機能依存マップモデル §7、2026-06-12 反映）。
> ファイル不在・`feature_order` 未定義・ファイルが YAML として読めない場合は
> `next_action.kind: feature_definition_required`（verdict OK、exit 0）で intent／feature-partitioning
> の実施を案内し（パース不能の遮断分離は実装改善候補 FUP-2026-06-12-001）、`feature_order` と
> `depends_on` の整合違反（依存先行違反・循環、`validate_feature_order_consistency`）は
> `next_action.kind: unknown`・`reasons` 列挙・DEVIATION（exit 2）で遮断する。
> fail-closed の既定（段集合 YAML パースエラー ／ 証跡欠落 ／ 必須フィールド欠落 ／
> `feature_order` 整合違反で遮断。feature-dependency.yaml の未定義・パース不能のみ
> 立ち上げ案内として OK）を全面採用。

- テスト要件へ「feature_order 外出し・探索順・立ち上げ案内（feature_definition_required）・
  整合検査・対象アプリ独自 feature 構成での next 動作テスト（cde1f5c で実装済み）」を追加

### 2.4 T-005（直前ゲート）の参照語彙

フェーズ移行検査の `feature-dependency.yaml#phase_order` を `#feature_order` へ統一（意味不変）。

### 2.5 対応表

「Requirement 8 受入 2：features ＋ feature_order、2 形式の depends_on」へ語彙統一。

## 3. 変更内容（conformance-evaluation tasks.md）

T-010 の責務・完了条件 5・テスト要件・対応表の `phase_order` 表記 4 箇所を `feature_order` へ
文言追従（意味不変）。

## 4. 根拠と証跡

- 承認済み requirements・design（2026-06-12 利用者 approval。各 2 巡の triad-review 済み）
- 利用者決定：MLE-DEC-002（スキーマ契約は実装検査で代替）・MLE-DEC-003（7 機能実体化）
- 実装とテスト：`tools/check-workflow-action.py`・`tests/tools/test_check_workflow_action.py`
  （TDD 失敗テスト 10 件先行、155 件＋全群 871 件通過）
- T-002 が参照していたスキーマは一度も実体化されておらず（conformance 評価 2026-06-12 で確認）、
  本変更は「紙の上にしか存在しない契約」を「動いている検査の実体」へ置き換えるもの

## 5. レビュー観点

1. T-002 のスキーマ契約代替が、検証可能性を弱めていないか（JSON Schema を廃しても、同じ検査が
   実装とテストで担保されることが文言から確認できるか）。
2. T-004 の追記が承認済み requirements 受入 6〜8・design §7 と意味で一致しているか。
3. 既存の T-002／T-004 の他の完了条件・テスト要件と、今回の変更が矛盾しないか
   （特に DVT-C002 など他 feature からの参照）。
4. conformance-evaluation tasks の文言追従が意味不変か。
5. tasks.md の変更が「既存タスクの契約更新」に留まり、タスク分解の再構成（conformance-evaluation
   Requirement 12 受入 5 の境界外の行為）になっていないか。
