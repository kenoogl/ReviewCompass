# レビュー対象：reopen R-0 requirements 変更（配布側複数 LLM 入口契約の仕様反映）

改訂：round-1（2026-06-12）の triad-review 所見（クラスタ A must-fix・B/C/D should-fix、利用者承認済み）を
requirements.md へ反映済み。本書 §2.3 の引用は修正後の本文。round-2 は修正の妥当性確認を目的とする。

## 0. variant 選定理由（実行前ゲートの記録）

- 使用 variant：`implementation_review_independent_3way`（context: triad_review、API 3 社独立）
- 役割：primary=anthropic-api/claude-sonnet-4-6、adversarial=openai-api/gpt-5.5、judgment=gemini-api/gemini-3.1-pro-preview
- 選定理由：triad_review の default variant は CLI 経路を含み本実行環境と合わない。利用者承認済みの
  「Claude Code 操縦時の API 既定」（設計記録 2026-06-10 §3.6、config/api-settings.yaml）である
  接尾辞なし `*_independent_3way` 系を採用。2026-06-09 の requirements reopen 三役レビューと同系構成。

## 1. レビューの位置付け

これは reopen R-0（分類記録 `docs/reviews/reopen-classification-2026-06-12-multi-llm-entry-spec-reflection.md`）
の第3過程、requirements フェーズの triad-review である。実装が先行して完成しており
（コミット cde1f5c・c2903df・635afad、TDD テスト・回帰 871 件通過、模擬対象アプリ実証済み）、
本 reopen は仕様を実装へ追認させる方向の改訂である。実装コードの変更は含まない。

レビュー対象は requirements フェーズの変更のみ。design・tasks の変更は後続フェーズの
triad-review で扱う。

## 2. 変更内容（workflow-management requirements.md）

### 2.1 Requirement 8 受入 1 の改訂（保管先の対象アプリ対応）

> 1. 本機能は `feature-dependency.yaml` を機能間処理順と依存関係の一元保管先とする。開発リポジトリでは
> `stages/feature-dependency.yaml` に置く。対象アプリでは feature-partitioning の承認結果を
> `.reviewcompass/feature-dependency.yaml` として実体化する（設計記録
> `docs/notes/2026-06-10-deployment-multi-llm-entry-design.md` §3.5 由来、2026-06-12 反映）。

### 2.2 Requirement 8 受入 2 の改訂（語彙統一と由来注記）

`phase_order` を `feature_order` へ改め、次の由来注記を追加：

> **由来注記**：旧称 `phase_order`（計画書 §5.5 および `stages/feature-partitioning/2026-05-24-proposal.md`
> の表記）は `feature_order` と同一物である。過去記録（レビュー記録・分割提案書・計画書）は書き換えず、
> 本注記で読み解く（語彙調停 案 A、MLE-DEC-001、2026-06-12 利用者決定）。

### 2.3 Requirement 8 受入 6〜8 の新設（実装契約の追認）

> 6. 検査ツール（Requirement 2）は feature 一覧と機能順を `feature-dependency.yaml` の `feature_order`
> キーから解決する。探索はツール実行時のカレントディレクトリを基準に、相対パス
> `.reviewcompass/feature-dependency.yaml` → `stages/feature-dependency.yaml` →
> `feature-dependency.yaml` の順で行い、最初に存在したファイル 1 つだけを読む。親ディレクトリへの
> 遡上探索は行わない。「一元保管先」（受入 1）とは、この探索で選ばれる実行文脈ごとの単一ファイルを
> 指し、同一実行で複数ファイルを併読しない。ソース直書きの既定機能順は `next` 判定では解決結果で
> 上書きされる（2026-06-12 反映、MLE-C-001。探索基準の精密化は triad-review クラスタ A 対処）。
>
> 7. 検査ツールは `feature_order` が `depends_on` と矛盾しない順序であること（依存元の機能より
> 依存先の機能が先に並ぶこと。例：runtime が foundation に依存する場合、foundation を runtime より
> 先に置く）、および循環依存がないことを機械検査する。違反時、`next` は `next_action.kind: unknown`
> を返し、違反内容を出力の `reasons` 配列に理由として列挙し、verdict は DEVIATION（exit code 2、
> fail-closed）とする（2026-06-12 反映、MLE-C-003。出力形式の明記は triad-review クラスタ B・D 対処）。
>
> 8. feature 一覧が解決できない場合（`feature-dependency.yaml` 不在、または `feature_order` 未定義）、
> 検査ツールはエラーではなく `next_action.kind: feature_definition_required`（verdict OK、exit code 0）
> を返し、intent／feature-partitioning の実施と、承認された分割結果（依存の根拠と順序の導出を含む）の
> `feature-dependency.yaml` への記録を案内する（2026-06-12 反映、MLE-C-002）。

### 2.4 Requirement 1 受入 4 の参照修正

> 4. 機能横断段の場合、`feature_order` フィールドで `feature-dependency.yaml#feature_order` を参照する
> （旧称 `phase_order`。Requirement 8 受入 2 の由来注記を参照）。

### 2.5 Requirement 8 受入 3 の参照修正

参照を `feature_order: <feature-dependency.yaml#feature_order>` へ統一（意味不変）。

### 2.6 Change Intent への追記

2026-06-12 の reopen R-0 による上記変更の経緯（conformance 評価の gap 反映、語彙調停 案 A、
実装先行の追認である旨）を 1 項目追加。

## 3. 変更内容（conformance-evaluation requirements.md）

### 3.1 Requirement 7 受入 5 の文言追従（意味不変）

> 5. 本機能は feature_order（機能間処理順。旧称 phase_order、workflow-management Requirement 8 受入 2 の
> 由来注記参照）の最後に位置付ける（依存先がすべて先に完了する前提）。

### 3.2 Change Intent への追記

2026-06-12 の語彙統一（意味不変の文言追従）の経緯を 1 項目追加。

## 4. 根拠と証跡

- conformance 評価記録：`.reviewcompass/specs/conformance-evaluation/conformance/2026-06-12-completed-followup-conformance.md`
  （gap_found。MLE-GAP-001〜003 が本 requirements 変更に対応）
- 利用者決定：MLE-DEC-001（語彙調停 案 A）、MLE-DEC-002（スキーマ契約は実装検査で代替）、
  MLE-DEC-003（features 7 機能実体化）。reopen handoff package に記録済み
- 実装：`tools/check-workflow-action.py` の `resolve_feature_order`／`validate_feature_order_consistency`／
  `feature_definition_next_state`（maintenance side track、TDD 失敗テスト 10 件先行。回帰は 2026-06-11 保守記録の合計 981 件、2026-06-12 の pytest tests/ 全群では 871 件通過＝母集合が異なる別計数）
- 実体：`stages/feature-dependency.yaml`（feature_order キー＋ 7 機能の depends_on）、
  `templates/specs/feature-dependency.yaml.template`
- 運用文書：WORKFLOW_NAVIGATION.md に `feature_definition_required` 分岐を追加済み、
  WORKFLOW_DISCIPLINE_MAP.yaml に判定点登録済み（post-write 検証 3 系統で完了、
  manifest post-write-2026-06-12-004）

## 5. レビュー観点（この triad-review で検証してほしいこと）

1. 受入 6〜8 の新設文言が、実装の実挙動（探索順・立ち上げ案内 OK・整合違反 DEVIATION）を
   正確かつ検証可能に記述しているか。実装と矛盾する記述、検証不能な記述はないか。
2. 受入 1 の「開発リポジトリ／対象アプリ」の二重規定が、既存の「一元保管先」の主張と
   矛盾なく読めるか。
3. 由来注記方式（旧称 phase_order を過去記録に残し、注記で読み解く）が要件として
   一義に読めるか。既存の Requirement 1 受入 4・Requirement 8 受入 3 との整合が取れているか。
4. conformance-evaluation Requirement 7 受入 5 の文言追従が意味不変に留まっているか。
5. 既存の他 Requirement（特に Requirement 2 の next 判定責務）との重複・矛盾がないか。
