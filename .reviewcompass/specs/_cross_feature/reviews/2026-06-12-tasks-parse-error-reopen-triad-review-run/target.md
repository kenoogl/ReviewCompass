# レビュー対象：reopen R-0（parse-error-failclosed）tasks 変更

## 0. variant 選定理由（実行前ゲートの記録）

- 使用 variant：`implementation_review_independent_3way`（context: triad_review、API 3 社独立）
- 役割：primary=anthropic-api/claude-sonnet-4-6、adversarial=openai-api/gpt-5.5、judgment=gemini-api/gemini-3.1-pro-preview
- 選定理由：本日の各 triad-review と同一構成（正本は SESSION_WORKFLOW_GUIDE §3.3 (a-3)）。

## 1. レビューの位置付け

reopen R-0（docs/reviews/reopen-classification-2026-06-12-parse-error-failclosed.md）第3過程の
tasks フェーズ triad-review。requirements（受入 8・9）と design（§7 パース不能の遮断項）は
利用者 approval 済み。本レビューは T-004 のタスク契約が承認済み仕様と整合し、次の implementation 段の
TDD 実装の作業指示として十分かを検証する。tasks.md 本体の再作成・タスク分解の確定は行っていない
（既存 T-004 の契約文言とテスト要件の更新のみ）。

## 2. 変更内容（workflow-management tasks.md T-004）

### 2.1 契約文言（責務記述）の更新

> ファイル不在・`feature_order` 未定義は `next_action.kind: feature_definition_required`
> （verdict OK、exit 0）で intent／feature-partitioning の実施を案内し、探索で選ばれた 1 ファイルが
> 読めない場合（パース不能・空・最上位が連想配列でない場合を含む。値の整合検査より先に判定）と
> `feature_order` と `depends_on` の整合違反（依存先行違反・循環、`validate_feature_order_consistency`）は
> `next_action.kind: unknown`・`reasons` 列挙・DEVIATION（exit 2）で遮断する（パース不能は破損ファイルの
> パスと内容確認を促す理由、空の場合は `feature_order` の記録を促す理由を含める）。fail-closed の既定
> （YAML パースエラー（段集合・feature-dependency とも） ／ 証跡欠落 ／ 必須フィールド欠落 ／
> `feature_order` 整合違反で遮断。feature-dependency.yaml の不在・未定義のみ立ち上げ案内として OK）を
> 全面採用（パース不能の遮断分離は MLE-DEC-005 により本契約へ反映、FUP-2026-06-12-001 解消、2026-06-12）。

### 2.2 テスト要件の更新

> feature-dependency.yaml パース不能・空・非連想配列の遮断（DEVIATION・理由に破損ファイルパス、
> 空は記録促し）テストと不在・未定義の案内維持テスト（MLE-DEC-005、仕様確定後に TDD で実装）

## 3. 根拠と証跡

- 承認済み requirements 受入 8・9 と design §7（いずれも 2026-06-12 利用者 approval、各 triad-review 済み）
- 実装は旧挙動のまま（意図的）。本 tasks 契約のテスト要件が、次の implementation 段の
  TDD（失敗テスト→実装→全テスト通過）の作業指示となる

## 4. レビュー観点

1. T-004 の契約文言が承認済み受入 8・9・design §7 と意味で一致しているか。
2. テスト要件が実装の検証に十分か（遮断 3 ケース＝パース不能・空・非連想配列、案内維持 2 ケース＝
   不在・未定義、理由文の内容確認）。
3. 既存の T-004 の他の記述（fail-closed の既定、探索順、立ち上げ案内）と矛盾しないか。
4. タスク分解の再構成（境界外の行為）になっていないか。
