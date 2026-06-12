# レビュー対象：reopen R-0（parse-error-failclosed）design 変更

## 0. variant 選定理由（実行前ゲートの記録）

- 使用 variant：`implementation_review_independent_3way`（context: triad_review、API 3 社独立）
- 役割：primary=anthropic-api/claude-sonnet-4-6、adversarial=openai-api/gpt-5.5、judgment=gemini-api/gemini-3.1-pro-preview
- 選定理由：本日の各 triad-review と同一構成（正本は SESSION_WORKFLOW_GUIDE §3.3 (a-3)）。

## 1. レビューの位置付け

reopen R-0（docs/reviews/reopen-classification-2026-06-12-parse-error-failclosed.md）第3過程の
design フェーズ triad-review。requirements（受入 8 の限定・受入 9 の新設＝パース不能・空・構造異常の
遮断）は利用者 approval 済み。本レビューは design の記述が承認済み requirements と整合し、
implementation 段の TDD 実装の指針として十分かを検証する。**実装は旧挙動のまま**（仕様確定後に
TDD で実装する正順。解消条件は tasks T-004 テスト要件と reopen 進行記録に明示済み）。

## 2. 変更内容（workflow-management design.md §機能依存マップモデル §7）

### 2.1 立ち上げ案内の限定

> - **立ち上げ案内**：ファイル不在または `feature_order` 未定義の場合、エラーではなく
>   `next_action.kind: feature_definition_required`（verdict OK／exit 0）を返し、
>   intent／feature-partitioning の実施と、承認された分割結果（依存の根拠と順序の導出を含む）の
>   記録先を案内する。`current_state.feature_dependency_source` に解決元（不在時 null）を含める。
>   （以下、判断 3 との両立説明：本案内はいかなる操作も許可せず作業を進ませないため fail-closed が
>   守る対象に抵触しない。パース不能は未定義と区別して遮断するため、破損が案内で覆い隠される弱点は
>   解消済みである（MLE-DEC-005）。）

### 2.2 「パース不能の遮断」項の新設（受入 9 の確定文言へ追従済み）

> - **パース不能の遮断**：探索で選ばれた（最初に存在した）1 ファイルが、YAML として読めない、
>   空（内容なし）、または最上位が連想配列でない場合、未定義と区別して `next_action.kind: unknown`
>   （既存の判定種別。整合検査と同じ kind）を返し、破損ファイルのパスと内容確認を促す理由
>   （空の場合は `feature_order` の記録を促す理由）を `reasons` 配列に列挙して DEVIATION
>   （exit code 2、fail-closed）とする。これはファイルそのものの破損・構造異常の検査であり、
>   読み込み後の値の整合検査（次項）より先に判定する。破損を立ち上げ案内で覆い隠さない。

### 2.3 整合検査の挙動分け更新

> 失敗の種類で挙動を分ける：不在・未定義 → 案内（OK）、パース不能・整合違反 → 遮断（DEVIATION）。

### 2.4 変更意図への追記

reopen R-0（parse-error-failclosed、MLE-DEC-005）の経緯と「仕様確定後に TDD で実装する正順」を 1 項目追加。

## 3. 根拠と証跡

- 承認済み requirements：Requirement 8 受入 8・9（2026-06-12 利用者 approval。triad-review で
  境界 4 点——型違反の位置づけと判定順・unknown の出どころ・1 ファイル限定・空ファイルは遮断——を精密化済み）
- 実装方針：`load_feature_dependency` がパース不能・空・非連想配列を「未定義」と区別して通知し、
  `resolve_feature_order`／`feature_definition_next_state` が遮断系の戻りを返す改修を
  implementation 段で TDD 実施予定

## 4. レビュー観点

1. design §7 の「パース不能の遮断」項が、承認済み受入 9 と意味で一致しているか。
2. 実装の指針として十分か（遮断の判定位置＝読み込み時、整合検査より先、という設計が
   実装者に一義に伝わるか）。
3. 両立説明（判断 3 との関係）の更新が、遮断分離後の状態を正しく述べているか。
4. §7 内の他項（探索順・立ち上げ案内・整合検査・判定点の登録）との間に矛盾がないか。
