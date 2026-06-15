# implementation triad-review ターゲット：Req 11 実装（reopen R-0 2026-06-15）

## レビュー対象

feature: workflow-management
phase: implementation
reopen: R-0（decision-source-lint）
実装内容: decision-source-lint サブコマンド・stages/decision-source-lint-config.yaml・commit ゲート統合

## 成果物

1. `tools/check_workflow_action/decision_source_lint.py`：コアロジック
   - `load_decision_source_lint_config(cwd)`: 設定ファイル読み取り（内蔵デフォルト 11 件）
   - `normalize_text(text)`: NFC・連続空白→1スペース・前後除去
   - `is_empty_content(excerpt, config)`: 句読点除去→トークン化→全一致判定
   - `validate_decision_schema(data)`: 必須フィールド・enum・型検査
   - `check_bundle_exception(data, cwd)`: 束ね例外 3 条件確認
   - `verify_excerpt_in_session(excerpt, session_path)`: 全文逐語照合
   - `collect_decision_files(cwd)`: decisions/ 直下のみ収集（bundle-exceptions/ 除外）
   - `lint_decision_file(path, cwd, config)`: 1 ファイル lint
   - `run_decision_source_lint_all(cwd)`: --all モード
   - `run_verify_pending(cwd)`: --verify-pending モード（2 フィールドのみ更新）

2. `tools/check-workflow-action.py` への追加：
   - `cmd_decision_source_lint(args)`: サブコマンドエントリポイント
   - `decision-source-lint` サブコマンド登録（--all / --verify-pending / positional）
   - `cmd_commit` への統合（DEVIATION/WARN 判定）

3. `stages/decision-source-lint-config.yaml`: 初期内容なし語リスト 11 件

4. `tests/tools/test_decision_source_lint.py`: 61 件テスト（全 pass）

## レビュー観点

1. design §1〜§6 との整合（スキーマ・照合・束ね例外・内容なし語・サブコマンド・委譲事項）
2. TDD テスト要件(1)〜(11)がすべてカバーされているか
3. design §6 委譲事項（--verify-pending 安全性・差分表示・既存関数統合）
4. commit ゲート統合の正確性（pending=WARN・unverifiable=DEVIATION）
5. --all が bundle-exceptions/ を除外する実装の正確性
6. --verify-pending が verification_status・verified_at の 2 フィールドのみを更新する実装の正確性
