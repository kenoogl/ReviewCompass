# proxy_model 裁定依頼：workflow-management requirements（Requirement 11）triad-review 所見

あなたは人の判断を代行する proxy_model である。操縦 LLM（Claude）とは別系統として、各所見の最終ラベルを決める。

## 文脈

- 対象は workflow-management requirements への新要件 Requirement 11（重要決定の出典検査＝束ね検出・逐語照合・内容性、および構造化した重要決定の記録形式）の追加。reopen 分類 R-0。
- 現フェーズは requirements。requirements は「何を満たすか（受入基準）」を定め、スキーマ・パス・終了コード等の実装詳細は design 以降で確定してよい。ただし再現性・契約・fail-closed・要件間の責務境界に関わる事項は requirements で担保すべき。
- ラベル定義：must-fix=要件として欠陥・不足があり修正必須／should-fix=改善として反映が望ましい／leave-as-is=対処不要（情報提供・軽微・design 委譲で足りる）。

## 受入基準の要旨（Requirement 11）

1. 構造化記録（決定ID・決定文言・出典〔引用＋セッションID＋個別/束ね区分〕）。going-forward 適用、過去散文台帳は遡及移行しない。スキーマは design。
2. 束ね検出：同一出典を共有する複数決定は確定させない、fail-closed。束ねが避けられない場合の扱いは design。
3. 逐語照合：出典の引用が層1転写（.reviewcompass/evidence/sessions/）に逐語であるか機械照合、無ければ fail-closed。正規化は design。
4. 内容性：「OK」等の中身なし返事だけを唯一の出典にしない。語リストは design、拡張は規律変更扱い。
5. 読み取りに徹し書き換えない／結論不能は非ゼロ終了・機械可読 status で fail-closed。
6. 意味一致の最終判断は人・判定役に委ね、機械は「検証可能化」まで。
7. 接続は Requirement 2 のサブコマンド and/or Requirement 4 の commit 直前ゲート。接続点は design。

## 所見一覧（finding_id・severity・要旨・操縦 LLM の提案ラベル）

1. claude-sonnet-4-6-primary-001（WARN）受入2：「束ねが避けられない場合」が要件レベルで未定義。提案=should-fix
2. claude-sonnet-4-6-primary-002（WARN）受入3：取り込み未完了の状態で重要決定の確定操作が行われた場合の扱いが未記述。提案=must-fix
3. claude-sonnet-4-6-primary-003（WARN）受入7：「かつ／または」が両方必須か一方で足りるか曖昧。提案=must-fix
4. claude-sonnet-4-6-primary-004（INFO）受入4：リスト拡張を「規律変更扱い」とする根拠・経路（どの規律・どの承認）が未記述。提案=should-fix
5. claude-sonnet-4-6-primary-005（INFO）受入1：重要種別の境界が本要件内に未記述、既存要件（Req 1・4）参照も無い。提案=should-fix
6. gpt-5.5-adversarial-001（ERROR）受入1：構造化記録の最低項目に「重要種別」と出典発言を一意特定するロケータが無い。提案=must-fix
7. gpt-5.5-adversarial-002（ERROR）受入7：接続点の必須達成条件が一意に定まらない。提案=must-fix
8. gpt-5.5-adversarial-003（WARN）受入1：「仕様／計画変更」の範囲が広く、重要決定の境界が要件上で判定可能になっていない。提案=should-fix
9. gpt-5.5-adversarial-004（ERROR）受入3・5：会話転写が取り込み済みでない新規決定をどう扱うかのワークフロー要件が不足。提案=must-fix
10. gpt-5.5-adversarial-005（WARN）受入2：束ね検出を fail-closed としつつ「束ねが避けられない場合」を design に委ね、例外の可否が要件上で曖昧。提案=should-fix
11. gpt-5.5-adversarial-006（WARN）受入1：going-forward 適用の開始点が明確でない。提案=should-fix
12. gemini-3.1-pro-preview-judgment-001（WARN）受入3：現セッション内で下された決定を直前ゲートで検査する際にデッドロック（順序依存）が生じる抜け。提案=must-fix
13. gemini-3.1-pro-preview-judgment-002（INFO）受入1：「仕様／計画変更」の境界がやや多義的で軽微なタスク変更との線引きが曖昧。提案=should-fix

なお finding 2・9・12 は同根（取り込み前／現セッション決定の順序依存・デッドロック）、finding 3・7 は同根（接続点の曖昧）、finding 5・8・13 は同根（重要種別の境界）、finding 1・10 は同根（束ね例外）。

## 返答形式（厳守）

各 finding について、次の YAML だけを返すこと（説明文や markdown のコードフェンスは付けない）。must-fix とした finding には rejected_options（他2ラベルを却下した一言理由）を必ず付ける。

decisions:
  - finding_id: claude-sonnet-4-6-primary-001
    final_label: should-fix
    rationale: <一言>
  - finding_id: gpt-5.5-adversarial-001
    final_label: must-fix
    rationale: <一言>
    rejected_options:
      should-fix: <一言>
      leave-as-is: <一言>
  # …全 13 件
