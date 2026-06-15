# レビュー対象：Requirement 11 設計（design.md §Req 11 設計モデル追加）

## 0. variant 選定理由

- variant：`implementation_review_independent_3way`（primary=claude-sonnet-4-6、adversarial=gpt-5.5、judgment=gemini-3.1-pro-preview）
- Claude Code 操縦時の API 既定。2026-06-15 reopen R-0（decision-source-lint）における design フェーズ再実施。

## 1. 今回の変更内容

design.md に `§Requirement 11 設計モデル：重要決定の出典検査（Req 11）` を新設した。Requirement 11 が requirements フェーズで「design で確定」とした 6 事項の内容：

1. **記録スキーマ**（Req 11 受入 1）：配置先 `.reviewcompass/decisions/{decision_id}.yaml`（1 決定 = 1 ファイル）。フィールド：`decision_id`・`category`（3 値 enum）・`statement`・`source`（`excerpt`・`session_id`・`locator`・`multiplicity`）・`verification_status`（3 値 enum）・`verified_at`。

2. **束ね例外の扱い**（Req 11 受入 2）：機械は `multiplicity: bundled` を検出して fail-closed。例外承認時は `bundle_exception_id` フィールドを追加し、人の明示承認レコード `.reviewcompass/decisions/bundle-exceptions/{id}.yaml` が存在する場合のみ通過。

3. **逐語照合・正規化・保留管理**（Req 11 受入 3）：正規化規則は NFC・連続空白→1スペース・前後除去の 3 段。保留管理は `pending`→転写取り込み（SessionStart フック）→`--verify-pending` 再照合→`verified` の順序。タイムアウト昇格なし。

4. **内容なし語リスト**（Req 11 受入 4）：設定ファイル `stages/decision-source-lint-config.yaml` に初期 11 語（OK・ok・承認・了解・はい・Yes・yes・LGTM・✓・◯・○）。拡張は規律変更扱い（人承認必須）。

5. **サブコマンドと接続点**（Req 11 受入 5・7）：サブコマンド名 `decision-source-lint`。呼び出し形式は `--all` / `<file>` / `--verify-pending` の 3 形式。commit 直前ゲートへ組み込む（pending=WARN・unverifiable=DEVIATION・bundled 無承認=DEVIATION）。

6. **implementation 委譲事項**：並行書き込み防止・採番細部・差分表示形式・既存関数統合の 4 つを実装段へ委譲。

## 2. レビュー観点（criteria: design_r11）

1. 記録スキーマが Req 11 受入 1 の「最低限持つべきフィールド」をすべて包括しているか。`decision_id` 命名則・フィールド型・配置先の設計が実装可能か。
2. 束ね例外の承認レコードの仕組み（`bundle_exception_id` + 承認 YAML）が Req 11 受入 2 の「人の明示承認」契約を満たし、fail-closed を維持しているか。
3. 正規化規則（NFC・空白・前後除去）が十分か。過剰に厳しくなく、かつ実際の会話転写に対して逐語照合が機能するか。保留管理の順序制御が AC3（デッドロック回避と fail-closed 両立）と矛盾しないか。
4. 内容なし語リストの設定ファイル配置と拡張管理（規律変更扱い）が Req 11 受入 4 と整合しているか。初期リストは代表的な一括承認語を網羅しているか。
5. commit ゲートへの組み込み（pending=WARN）が Req 11 受入 3 の「直前ゲートは作業をブロックしない」と整合しているか。unverifiable=DEVIATION が Req 11 受入 5 の fail-closed と整合しているか。
6. implementation 委譲事項の範囲が適切か。設計で固定すべきことを実装に先送りしていないか。
7. 新たな must-fix 級の欠陥があれば指摘する。なければ収束と判断してよい。
