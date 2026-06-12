# レビュー対象：reopen R-0（parse-error-failclosed）implementation 変更

## 0. variant 選定理由（実行前ゲートの記録）

- 使用 variant：`implementation_review_independent_3way`（context: triad_review、API 3 社独立）
- 役割：primary=anthropic-api/claude-sonnet-4-6、adversarial=openai-api/gpt-5.5、judgment=gemini-api/gemini-3.1-pro-preview
- 選定理由：本日の各 triad-review と同一構成（正本は SESSION_WORKFLOW_GUIDE §3.3 (a-3)）。

## 1. レビューの位置付け

reopen R-0（docs/reviews/reopen-classification-2026-06-12-parse-error-failclosed.md）第3過程の
implementation フェーズ triad-review。requirements（受入 8・9）・design（§7）・tasks（T-004）は
利用者 approval 済み。本レビューは TDD 実装（失敗テスト 3 件先行 → 実装 → 全テスト通過）が
承認済み仕様と一致しているかを検証する。

## 2. 実装内容（tools/check-workflow-action.py、差分 49 行）

### 2.1 load_feature_dependency の変更

戻り値を `(data, relative_path)` から `(data, relative_path, load_error)` へ拡張。
探索で最初に存在した 1 ファイルについて：

- YAML パース例外（OSError／YAMLError）→ `load_error: "unreadable"`（従来は握りつぶして {} を返していた）
- 読めたが None（空ファイル）→ `load_error: "empty"`
- 読めたが最上位が連想配列でない → `load_error: "not_mapping"`
- 正常 → `load_error: None`

### 2.2 resolve_feature_order の変更

`load_error` がある場合、立ち上げ案内（guidance_reason）ではなく遮断系の理由
（consistency_reasons）を返す：

- unreadable：「{パス} を YAML として読めません（破損の可能性）。ファイルの内容を確認してください」
- empty：「{パス} が空です。feature-partitioning の承認結果（依存の根拠と順序の導出を含む）を
  feature_order キーに記録してください」
- not_mapping：「{パス} の最上位が連想配列ではありません。ファイルの内容を確認してください」

ファイル不在・`feature_order` キー未定義の立ち上げ案内（OK）は従来どおり維持。

### 2.3 feature_definition_next_state の変更

`load_error` がある場合の `next_action.reason` を「feature-dependency.yaml が読めません
（破損または内容不正の可能性）」とし、`kind: unknown`・`reasons` 列挙・DEVIATION（exit 2）を返す
（整合違反と同じ遮断経路。reason 文言のみ区別）。

## 3. テスト（tests/tools/test_check_workflow_action.py、差分 44 行、TDD）

T-004 テスト要件どおり、実装前に失敗を確認した 3 件：

1. `test_unreadable_file_is_deviation`：壊れた YAML → kind unknown・DEVIATION・exit 2・
   reasons に対象パスと「内容を確認」
2. `test_empty_file_is_deviation_with_record_guidance_reason`：空ファイル → 同上＋
   reasons に「空」「feature_order」「記録」
3. `test_non_mapping_top_level_is_deviation`：最上位がリスト → 同上＋「内容を確認」

既存の案内維持テスト（不在 `test_missing_file_returns_bootstrap_guidance`、未定義
`test_missing_key_returns_bootstrap_guidance_with_distinct_reason`：kind feature_definition_required・
OK・exit 0）は無変更のまま通過。結果：tools 160 件・全テスト群 876 件通過、開発リポジトリの
`next` 判定に回帰なし。

## 4. レビュー観点

1. 実装が承認済み受入 9（1 ファイル限定・パース不能・空・非連想配列の遮断・判定順・理由の最低要素）と
   一致しているか。
2. 案内維持（不在・未定義 → OK）が壊れていないことの担保は十分か。
3. 例外処理の範囲（OSError／YAMLError）と分類（unreadable／empty／not_mapping）に漏れはないか。
4. テストが T-004 のテスト要件（kind・verdict・exit code・理由文の内容検証）を満たしているか。
