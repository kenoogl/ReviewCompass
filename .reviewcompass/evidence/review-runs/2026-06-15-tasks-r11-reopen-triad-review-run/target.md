# tasks triad-review ターゲット：Req 11 タスク追記（reopen R-0 2026-06-15）

## レビュー対象

feature: workflow-management
phase: tasks
reopen: R-0（decision-source-lint）
追記内容: T-013 タスク定義・要件追跡表 Req 11 行（7 行）・変更意図 Req 11 追記

## 前提資料

- requirements.md §Requirement 11（受入 1〜7）
- design.md §Req 11 設計モデル §1〜§6

## 追記テキスト（tasks.md diff 相当）

### T-013 タスク定義

```
### T-013：重要決定の出典検査（decision-source-lint サブコマンド、Req 11、reopen R-0 2026-06-15）

- **対応設計節**：design.md §Req 11 設計モデル §1〜§6
- **対応要件**：Requirement 11 受入 1〜7
- **責務**：`tools/check-workflow-action.py` に `decision-source-lint` サブコマンドを追加し、`.reviewcompass/decisions/` 直下の重要決定記録 YAML を逐語照合・束ね検出・内容性検査する。①`stages/decision-source-lint-config.yaml` の生成（内容なし語リスト初期値 11 件）。②決定記録スキーマの機械検査（必須フィールド・category 3 値 enum・multiplicity 制約・verification_status 3 値 enum）。③逐語照合：source.locator のパス部分に対応する転写ファイル全文に対して NFC 正規化・連続空白→単一スペース・前後除去の正規化を両辺に適用し `source.excerpt` が含まれるかを検索（ターン番号は絞り込みに使わない）。④束ね例外の 3 条件確認（承認レコードが存在し・当該 decision_id が covered_decision_ids に含まれ・multiplicity が single）。⑤内容なし語リスト判定（句読点除去→スペース区切りトークン化→全トークンがリスト一致で fail-closed）。⑥commit 直前ゲートへの統合（`cmd_commit` から `decision-source-lint --all` を呼び出し、pending=WARN・unverifiable=DEVIATION・multiplicity:bundled かつ承認なし=DEVIATION）。⑦`--verify-pending` フラグ（verification_status: pending の決定を再照合し合格なら verified に更新・verified_at に現在日時を記録。書き換えるのは verification_status・verified_at の 2 フィールドのみ。照合不合格時はファイル不変・差分表示・非ゼロ終了）。
- **前提タスク**：T-001（配置）、T-004（検査スクリプト本体）
- **成果物**：`tools/check-workflow-action.py` の `decision-source-lint` サブコマンド、`stages/decision-source-lint-config.yaml`（初期内容なし語リスト）、`tests/tools/` のテストファイル
- **完了条件**：design §1〜§6 を満たす。TDD（赤→緑→全テスト通過、回帰なし）。commit 直前ゲートへの統合済み（`pending=WARN`・`unverifiable=DEVIATION`）。`--all` が `bundle-exceptions/` サブディレクトリを除外する。`--verify-pending` が `verification_status`・`verified_at` の 2 フィールドのみを更新し他フィールドを書き換えない。
- **テスト要件（TDD：先に失敗テストを書く）**：(1) 必須フィールドと category 3 値 enum の検査（欠落・不正値で DEVIATION）、(2) multiplicity: bundled → fail-closed（承認レコードなし）、束ね例外 3 条件チェック（承認レコード有＋covered_decision_ids 含む＋multiplicity=single で通過）、(3) 逐語照合正常系（正規化後 excerpt が転写ファイル全文に含まれる → verified 判定）、(4) 逐語照合不合格系（転写ファイルに excerpt なし → pending 維持・差分表示・非ゼロ終了）、(5) verification_status: pending → WARN（commit 遮断しない）、verification_status: unverifiable → DEVIATION、(6) 内容なし語リスト正常系（全トークンが empty_content_words に一致 → fail-closed）と不合格系（一部不一致 → 通過）、(7) `--all` で `decisions/` 直下のみ（`bundle-exceptions/` YAML は検査対象外）、(8) `--verify-pending` 正常系（pending → verified・verified_at 記録・他フィールド不変）、(9) `--verify-pending` 不合格系（ファイル内容不変・差分表示・非ゼロ終了）、(10) commit ゲート統合（`cmd_commit` が `decision-source-lint --all` を呼び出し、決定が unverifiable の場合に DEVIATION に昇格）、(11) 設定ファイル `stages/decision-source-lint-config.yaml` の読み取り（リストの内容が正しく反映される）。全 pytest が pass、回帰なし。
```

### 要件追跡表への追記（7 行）

```
| Requirement 11 受入 1：決定記録スキーマ・category 種別判定基準・going-forward 適用 | T-013 |
| Requirement 11 受入 2：multiplicity:bundled の fail-closed・束ね例外 3 条件 | T-013 |
| Requirement 11 受入 3：逐語照合・正規化規則・保留管理・照合不合格時 pending 維持 | T-013 |
| Requirement 11 受入 4：内容なし語リスト・判定ロジック・設定ファイル配置 | T-013 |
| Requirement 11 受入 5：サブコマンド呼び出し形式・--all（bundle-exceptions/ 除外）・読み取り専用例外（--verify-pending） | T-013 |
| Requirement 11 受入 6：lint が内部エラー時に unverifiable 判定・人が設定するのは口頭合意等の場合のみ | T-013 |
| Requirement 11 受入 7：commit 直前ゲート組み込み（pending=WARN・unverifiable=DEVIATION） | T-013 |
```

### 変更意図への追記

```
- **2026-06-15 reopen R-0（decision-source-lint）Req 11 への対応**：重要決定の出典検査・束ね検出・逐語照合・内容性検査と構造化決定記録の新設を T-013 として追加。decision-source-lint サブコマンドを commit 直前ゲートに統合し、pending=WARN・unverifiable=DEVIATION で fail-closed を保証する。
```

## レビュー観点

1. T-013 の責務・成果物・前提タスク・完了条件が requirements Req 11 受入 1〜7 と design §1〜§6 の全事項をカバーしているか
2. テスト要件（TDD）が設計の境界条件・異常系・正常系を十分に網羅しているか
3. 要件追跡表 7 行が受入基準と T-013 の対応を正確に反映しているか
4. 既存タスク（T-001〜T-012）との責務重複・依存違反がないか
5. 完成判定基準（T-001〜T-013）への更新が正しいか
