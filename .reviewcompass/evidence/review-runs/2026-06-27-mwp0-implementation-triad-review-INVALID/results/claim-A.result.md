# レビュー結果：Claim A

- **所見**：問題あり
- **重大度**：should-fix

## 根拠

`_commit_preflight_next_action` が返す `verification_pending` は `--json` 出力の `next_action.kind` に実際に出力される（内部変数に留まらない）。

コードフロー：
1. `_commit_preflight_next_action` が `kind: "verification_pending"` を返す
2. `build_commit_instruction_preflight`（L.4421）が `next_action.get("kind") == "verification_pending"` で分岐し `verdict = "DEVIATION"` を設定
3. `_build_commit_preflight_response` で `next_action` がそのまま出力に含まれる

つまり `verification_pending` は実際の JSON 出力に含まれ、`commit_preflight_response.schema.json` の enum 3値に違反している。

## 問題の本質

MWP-0 の設計意図（commit-preflight の kind を「コミット可否の分類」3値に絞り、ワークフロー状態分類と責務を分離する）が、実装レベルで完成していない。`_commit_preflight_next_action` が `next --json` と同じワークフロー状態分類ロジックを流用しており、`verification_pending` という「ワークフロー上の次の行動」概念がコミット前判定に混入している。

## テストについて

`test_commit_preflight_kind_is_always_commit_related` は許容集合に `"verification_pending"` を含まない。ただし現在のテスト環境では post-write 対象ファイルが存在しないため、`verification_pending` 経路に入らず通過している。テストが検証できていない状況は「不整合の結果」として連鎖している。

## 提案

`_build_commit_preflight_response` 内で、`next_action.kind` が commit-preflight スキーマの enum 外の値を持つ場合に変換処理を追加する。`verification_pending` の内部判定結果は `current_state.next_action` に格納しつつ、出力する `next_action.kind` はスキーマ準拠値のみとする。

テストにも `next_action.kind` のアサーションを追加し、`verification_pending` が出力されないことを明示的に確認する。
