---
date: 2026-06-15
gate: stages/implementation.yaml#alignment
feature: workflow-management
reopen: R-0（decision-source-lint）
decision: existing_sufficient
---

# implementation alignment（整合確認）：Req 11 実装（reopen R-0 2026-06-15）

## 実装と design §1〜§6 の整合確認

| 設計節 | 実装 | 整合判定 |
| --- | --- | --- |
| §1 記録スキーマ | `validate_decision_schema()` が必須フィールド・category 3 値 enum・multiplicity 2 値・verification_status 3 値・空文字列を検査。スキーマフィールドは design §1 と一致。 | 整合 |
| §2 束ね例外 | `check_bundle_exception()` が 3 条件（承認レコード存在・covered_decision_ids 含む・multiplicity=single）を確認。部分満足も fail-closed。 | 整合 |
| §3 逐語照合 | `verify_excerpt_in_session()` が NFC 正規化・連続空白→単一スペース・前後除去を行い、転写ファイル全文を対象に検索。ターン番号での絞り込みなし。 | 整合 |
| §4 内容なし語リスト | `is_empty_content()` が句読点除去→スペーストークン化→全一致で fail-closed。設定ファイルからリストを読み込み、欠落時は内蔵デフォルト 11 件を使用。 | 整合 |
| §5 サブコマンド接続点 | `decision-source-lint` サブコマンドが `--all` / `--verify-pending` / positional を実装。`cmd_commit` から `run_decision_source_lint_all()` を呼び出し、pending=WARN・unverifiable=DEVIATION に統合。 | 整合 |
| §6 実装委譲事項 | `--verify-pending` でアトミック書き込み（tmp ファイル経由 replace）、差分表示（excerpt 正規化後の出力）を実装。bundle_exception_id 採番は命名則に従いテストで検証。既存関数との統合は `run_decision_source_lint_all()` を `cmd_commit` から直接呼び出す方式で実現。 | 整合 |

## design §1〜§6 の完了条件（T-013）確認

| 完了条件 | 実装確認 |
| --- | --- |
| design §6 の実装委譲 4 事項が確定 | 安全書き込み: tmp_path.replace(path)・差分表示: excerpt 正規化後出力・採番命名則: テストで BEX-WM-001 形式を確認・既存関数統合: cmd_commit 直接呼び出し | 整合 |
| commit 直前ゲート統合済み（pending=WARN・unverifiable=DEVIATION） | `cmd_commit` 内の dsl_result 統合で確認 | 整合 |
| --all が bundle-exceptions/ を除外 | `collect_decision_files()` が `decisions/` 直下のみ返す | 整合 |
| --verify-pending が 2 フィールドのみ更新 | `run_verify_pending()` が verification_status・verified_at のみ更新し他フィールドを不変とする。テストで確認。 | 整合 |

## 判定

- **decision：existing_sufficient**（実装は design §1〜§6 と整合し、未解決の整合所見なし）
