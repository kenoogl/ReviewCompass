# レビュー対象：reopen R-0（decision-source-lint）workflow-management requirements 変更

## 0. variant 選定理由（実行前ゲートの記録）

- 使用 variant：`implementation_review_independent_3way`（context: triad_review、API 3 社独立）
- 役割：primary=anthropic-api/claude-sonnet-4-6、adversarial=openai-api/gpt-5.5、judgment=gemini-api/gemini-3.1-pro-preview
- 選定理由：Claude Code 操縦時の API 既定（正本は SESSION_WORKFLOW_GUIDE §3.3 (a-3)）。requirements 専用の triad-review variant が無いため、前例（Req 10、2026-06-14）同様に本 variant を流用。利用者承認 2026-06-15「実行」。
- 本 run の置き場は `.reviewcompass/evidence/review-runs/`（配置規約 PLC-DEC-004・009）。

## 1. レビューの位置付け

reopen R-0（分類記録 `docs/reviews/reopen-classification-2026-06-15-wm-decision-source-lint.md`）の第3過程、workflow-management requirements フェーズの triad-review。

背景：裁定負荷対策（利用者決定の埋没防止）として、重要決定（不可逆操作・規律変更・仕様／計画変更に限定）の確定について、出典の有無・束ね・逐語一致・内容性を機械検査する lint と、機械検査を可能にする構造化した重要決定の記録形式を新設する。新しい規律ではなく既存規律 `discipline_approval_operation`（確定記述に出典必須）・`discipline_plain_explanation_each_step`（重要承認は 1 件ずつ）の機械強制であり、分類は R-0（intent・feature-partitioning は不変、既存「静的検査」Requirement 1・「不可逆操作の直前ゲート」Requirement 4 の範囲に含む）。**実装より先に仕様を確定する正順**であり、lint・記録形式の実装は design・tasks 確定後に implementation 段で TDD により行う。**現時点で実装は未着手**である（意図的）。

## 2. 変更内容（workflow-management requirements.md）

### 2.1 Requirement 11 新設

> ### Requirement 11：重要決定の出典検査（裁定負荷対策）
>
> **目的（Objective）**：保守担当者が、重要決定（不可逆操作・規律変更・仕様／計画変更に限定）の確定について、出典の有無・束ね・逐語一致・内容性を機械検査できるようにし、一括承認のなかに重要な件が埋もれて正しく裁定されないまま確定する誤り（裁定負荷）を防ぐ。本要件は新しい規律を導入するのではなく、既存規律 `discipline_approval_operation`（確定記述に出典必須・出典なし禁止・機械検査は承認の代替でない）と `discipline_plain_explanation_each_step`（重要承認は 1 件ずつ）を機械強制するものであり、Requirement 1 が定める静的検査と Requirement 4 が定める不可逆操作の直前ゲートの範囲に位置づける（新しい意図を要さない。2026-06-15 reopen R-0、利用者決定）。
>
> #### 受入基準（Acceptance Criteria）
>
> 1. 本機能は、機械検査を可能にする構造化した重要決定の記録形式を定める。記録は最低限、決定 ID、決定文言、出典（出典の引用、セッション ID、当該出典が単一決定に対応するか複数決定で共有されるかの区分）を持つ。重要種別は不可逆操作・規律変更・仕様／計画変更に限定する。本記録形式は going-forward の新規重要決定から適用し、過去の散文の決定台帳は遡及移行しない。記録形式の厳密なスキーマ（フィールド名・型・配置先）は design で確定する。
> 2. 本機能は、束ね検出を行う。複数の重要決定が同一の出典（同じ一回の承認発言）を共有している場合、それらを確定扱いにさせない。検査は機械的に検出し、fail-closed（非ゼロ終了）とする。束ねが避けられない場合に各決定を個別の出典・区分で確定させる扱いの詳細は design で確定する。
> 3. 本機能は、逐語照合を行う。各重要決定の出典の引用が、repo に取り込み済みの会話転写（層 1、`.reviewcompass/evidence/sessions/`）に逐語で存在するかを機械照合する。逐語で存在しない（言い換え・でっち上げ）場合は fail-closed とする。照合の対象範囲と許容する正規化（空白・改行等）の規則は design で確定する。
> 4. 本機能は、内容性検査を行う。「OK」「承認」等の内容を持たない返事だけを、重要決定の唯一の出典として認めない。検査は機械的に検出し fail-closed とする。内容なしとみなす語の判定基準は拡張可能なリストで管理し、その確定は design で行う。リストの拡張は規律変更扱いとし人の明示承認を要する。
> 5. 本機能は、検査（読み取り）に徹し、`spec.json`・フェーズ状態・決定記録そのものを書き換えない（Requirement 3 受入 5 の proxy_model 非代行範囲、および Requirement 4 受入 1 の不可逆操作と整合）。必要な記録が解析不能・欠落で結論不能の場合、合格や完了を主張せず、非ゼロ終了と機械可読な `status` で fail-closed とする（Requirement 2 受入 4・Requirement 7 と整合）。
> 6. 本機能の検査範囲は、出典の存在・束ね・逐語一致・内容性という機械的に判定可能なものに限定する。決定文言が利用者の意図を正しく汲んでいるかという意味一致の最終判断は機械で行わず、人または判定役（会話転写との突き合わせ）に委ねる。本機能は意味一致を「検証可能化」する（突き合わせに必要な出典と転写を提示する）ところまでを担う。
> 7. 本機能は、本検査を Requirement 2 の検査スクリプトのサブコマンドとして提供し、かつ／または Requirement 4 の不可逆操作の直前ゲート（commit 直前検査）へ組み込む。具体的な接続点（サブコマンド名、直前ゲートへの組み込み可否と発火条件）は design で確定する。
>
> 由来：裁定負荷対策（利用者決定の埋没防止）。動機事例は PLC-DEC-007 の誤記録（…）。方針は 2026-06-13 利用者決定「(b) で対応」、検査方針の確定は 2026-06-14 利用者決定。分類は 2026-06-15 reopen R-0。実装は仕様確定後に TDD で行う正順の手続きとする。

### 2.2 Change Intent への追記

> - 2026-06-15 の reopen R-0（decision-source-lint）により、Requirement 11 を新設し、重要決定の出典検査（束ね検出・逐語照合・内容性）と構造化した重要決定の記録形式を要件化した。既存規律 `discipline_approval_operation`／`discipline_plain_explanation_each_step` の機械強制であり、意図文書を改めず既存「静的検査」（Requirement 1）と「不可逆操作の直前ゲート」（Requirement 4）の範囲に含める R-0 とした。動機事例は PLC-DEC-007 の誤記録（裁定負荷）。本改訂は仕様確定後に TDD で実装する正順の手続きである。

## 3. レビュー観点（criteria: requirements_r11_decision_source_lint）

1. **要件の妥当性・明確さ**：受入 1〜7 が、実装者が検証可能な形で書かれているか。曖昧・多義な語がないか。特に「重要種別＝不可逆操作・規律変更・仕様／計画変更」の境界が判定可能か。
2. **既存要件との整合**：Requirement 1（静的列挙）・Requirement 2（検査スクリプト・next・fail-closed）・Requirement 3（起草者と判定者の分離）・Requirement 4（不可逆操作の直前ゲート）との重複・矛盾がないか。「Requirement 2 のサブコマンド and/or Requirement 4 の直前ゲート」という接続の書き方は責務境界として適切か。
3. **責務の越境がないか**：受入 5 の「検査に徹し spec.json・フェーズ状態・決定記録を書き換えない」が、Requirement 3 受入 5・Requirement 4 受入 1 と整合し、本検査が書き込み権を持たないことを担保できているか。受入 6 の「意味一致の最終判断は人・判定役に委ね、機械は検証可能化まで」という線引きが、機械検査と人判断の責務分離として適切か（既存規律の「機械検査は承認の代替でない」と整合するか）。
4. **検査内容の網羅性・実現可能性**：受入 2〜4（束ね検出・逐語照合・内容性）が、動機事例（PLC-DEC-007 の一括承認による埋没）を実際に捕捉できるか。逐語照合の対象を層 1 転写（`.reviewcompass/evidence/sessions/`）に置く前提は妥当か（取り込み前の決定をどう扱うかの抜けがないか）。
5. **fail-closed の整合**：受入 2〜5 の fail-closed（非ゼロ終了・機械可読 status）が、Requirement 2 受入 4・Requirement 7（多層防御の第 1 層）と矛盾しないか。
6. **適用範囲の明確さ**：受入 1 の「going-forward 適用・過去散文台帳は遡及移行しない」が、要件として明確で、下流（design／tasks／implementation）が誤って遡及移行を実装しないよう十分に縛れているか。
7. **下流への波及**：design・tasks・implementation で追従すべき事項の漏れが requirements 側の文言から生じないか（例：記録形式スキーマ・接続点・内容なし語リスト・逐語照合の正規化規則）。
