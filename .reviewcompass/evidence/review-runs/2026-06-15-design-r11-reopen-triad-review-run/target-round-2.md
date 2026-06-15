# レビュー対象（round-2 収束確認）：Requirement 11 設計（round-1 修正反映後）

## 0. variant 選定理由

- variant：`implementation_review_independent_3way`（primary=claude-sonnet-4-6、adversarial=gpt-5.5、judgment=gemini-3.1-pro-preview）
- round-1 の must-fix 6 件・should-fix 4 件をすべて反映した。本 round は収束確認。

## 1. round-1 の修正内容（反映済み）

**must-fix（6 件）**：
- C1（F-002/A-001）：requirements 受入 5 に `--verify-pending` の例外明示（verification_status・verified_at の 2 フィールドのみ）。design §5 に読み取り専用例外の根拠を追記。
- C2（F-001）：design §2 の束ね例外承認手順を改訂。承認後に各決定の multiplicity を `single` に更新することを必要条件とし、lint が 3 条件（承認レコード存在・decision_id 包含・multiplicity=single）をすべて確認する。
- C3（A-002）：design §3 にステップ 5b「照合不合格は pending のまま、差分表示+非ゼロ終了」を追記。
- C4（A-003/F-007）：design §2 に束ね例外承認レコードの最低限スキーマ（bundle_exception_id・approved_by・approved_at・covered_decision_ids・rationale）を追記。design §1 に bundle_exception_id を optional フィールドとして追記。
- C5（A-004/F-006）：design §1 にターン番号の定義（## セクションを 1 から数えた順序番号）を追記。design §3 に「逐語照合はロケータを使わず全文検索、ロケータは人向け位置情報」を明記。
- C6（A-005）：design §5 の `--all` を「decisions/ 直下のみ（bundle-exceptions/ サブディレクトリ除外）」と明記。

**should-fix（4 件）**：
- C7（A-006）：design §1 に `category` 種別判定基準の表（対象例・除外例）を追記。
- C8（A-007）：design §1 に「locator のパス部分を正本、session_id は索引・メタデータ用補助」を明記。
- C9（F-003/A-008）：design §1 に `verification_status: unverifiable` の定義（lint が内部エラー時に判定、記録者が設定するのは出典が原則取得不能なケースのみ）を追記。
- C10（F-004/A-009）：design §4 に「句読点・記号除去→スペーストークン化→全トークンリストチェック」の手順を明記。

**leave-as-is（2 件）**：C11（テスト戦略）・C13（並行書き込みヒント）→ 今回未反映（tasks/implementation フェーズで対処）。

## 2. 収束確認のレビュー観点（criteria: design_r11_round2_convergence）

1. C1（受入 5 の例外明示）：requirements 受入 5 に例外が明記され、design §5 の根拠と整合しているか。`verification_status`・`verified_at` 以外のフィールドが保護されているか。
2. C2（束ね例外後の multiplicity）：lint が 3 条件（承認レコード存在・decision_id 包含・multiplicity=single）をすべて確認することで、「個別出典なしには確定させない」が機械強制されているか。
3. C3（照合不合格の遷移）：`--verify-pending` 不合格時に「pending のまま、差分表示+非ゼロ終了」が明記され、unverifiable への誤昇格がないか。
4. C4（承認レコードのスキーマ）：lint が `covered_decision_ids` を検索できるよう、5 フィールドが定義されているか。
5. C5（ロケータ・ターン番号）：ターン番号定義と「逐語照合は全文検索」の明示で、ロケータの目的と lint の動作が明確になったか。
6. C6（--all の除外）：bundle-exceptions/ サブディレクトリが明示的に除外され、誤動作が防止されているか。
7. C7〜C10：should-fix の反映が適切で、新たな矛盾を生んでいないか。
8. 新たな must-fix 級の欠陥があれば指摘する。なければ収束と判断してよい。
