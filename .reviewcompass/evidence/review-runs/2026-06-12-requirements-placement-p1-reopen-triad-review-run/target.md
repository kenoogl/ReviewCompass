# レビュー対象：reopen R-0（placement-p1-path-contracts）conformance-evaluation requirements 変更

## 0. variant 選定理由（実行前ゲートの記録）

- 使用 variant：`implementation_review_independent_3way`（context: triad_review、API 3 社独立）
- 役割：primary=anthropic-api/claude-sonnet-4-6、adversarial=openai-api/gpt-5.5、judgment=gemini-api/gemini-3.1-pro-preview
- 選定理由：Claude Code 操縦時の API 既定（正本は SESSION_WORKFLOW_GUIDE §3.3 (a-3)）。利用者承認 2026-06-12「開始」。
- 本 run の置き場 `.reviewcompass/evidence/review-runs/` は、配置規約 PLC-DEC-004・009（新規生成分から evidence 区画へ）の最初の適用例である。

## 1. レビューの位置付け

reopen R-0（分類記録 `docs/reviews/reopen-classification-2026-06-12-placement-p1-path-contracts.md`）の
第3過程、conformance-evaluation requirements フェーズの triad-review。

背景：文書配置規約の策定（利用者決定 PLC-DEC-001〜012、2026-06-12）により、証跡記録は
`.reviewcompass/evidence/`、実行時生成物は `.reviewcompass/runtime/` へ集約することが決まった。
本変更は conformance-evaluation の評価記録・草案の配置契約を evidence 区画へ改めるもの。
**実装より先に仕様を確定する正順**であり、ツールの書き込み先変更（旧パス読み取り互換付き）は
仕様確定後に implementation 段で TDD により行う。**現時点で実装は旧パスへ書く挙動のまま**である（意図的）。
既存の記録は旧置き場で凍結保全し、移動しない（PLC-DEC-009）。

## 2. 変更内容（conformance-evaluation requirements.md、5 箇所＋改訂注記）

### 2.1 Boundary Context（行 19）

> - 評価記録の出力（`<対象アプリ>/.reviewcompass/evidence/features/<feature>/conformance/`。2026-06-12 配置規約 PLC-DEC-003・004 反映）

### 2.2 Requirement 2 受入 7（文書生成モードの記録）

> 7. 本機能は文書生成モードの実行記録を `<対象アプリ>/.reviewcompass/evidence/features/<feature>/conformance/<日付>-generation.md` として保管する（配置の正本は Requirement 6 受入 2）。

### 2.3 Requirement 3 受入 8（照合チェックモードの記録）

> 8. 本機能は照合チェックモードの実行記録を `<対象アプリ>/.reviewcompass/evidence/features/<feature>/conformance/<日付>-check.md` として保管する（配置の正本は Requirement 6 受入 2）。

### 2.4 Requirement 6 受入 2（配置の正本。由来注記をここに集約）

**round-2 注記**：round-1 の F1（gpt-5.5・ERROR、must-fix）と F2（claude・WARN、should-fix）を利用者承認のうえ適用済み。受入 2 は評価記録ファイルの配置から conformance 成果物全体の配置ルート契約へ拡張し、互換終了の条件を明記した。round-2 は適用後本文の収束確認である。

> 2. 本機能は conformance 成果物（評価記録・spec update 草案・reopen handoff 成果物）の配置**ルート契約**を `<対象アプリ>/.reviewcompass/evidence/features/<feature>/conformance/` とする。評価記録のファイル名形式は `<日付>-<mode>.md`、その他の成果物のファイル・ディレクトリ名形式は各 Requirement（Requirement 2 受入 7・Requirement 3 受入 8・Requirement 12 受入 4 ほか）が定める。`reviews/` ディレクトリとは別ディレクトリ（分離契約は `evidence/features/<feature>/` 配下でも維持）。**由来注記**：旧配置 `specs/<feature>/conformance/` は 2026-06-12 の配置規約（PLC-DEC-003・004・009、`docs/notes/2026-06-12-document-placement-stage2-decisions.md`）により evidence 区画へ変更。既存記録は旧置き場で凍結保全し、新規生成分から適用する。旧パスの読み取り互換は最終形移行（P3、PLC-DEC-011）まで維持し、互換の終了は P3 の専用 reopen における本仕様の改訂として扱う（暗黙の終了はない）。

### 2.5 Requirement 12 受入 4（draft-only 草案の配置）

> 4. 本機能は draft-only spec update artifacts を `<対象アプリ>/.reviewcompass/evidence/features/<feature>/conformance/<日付>-spec-update-drafts/` に出力する（配置の正本は Requirement 6 受入 2）。草案は `apply_status: draft_only` を持ち、requirements.md, design.md, tasks.md を直接書き換えない。

### 2.6 Change Intent への追記（改訂注記）

> - 2026-06-12 の reopen R-0（placement-p1-path-contracts、配置規約 PLC-DEC-003〜005・009〜011）により、評価記録・草案・実行記録の配置先を `specs/<feature>/conformance/` から `evidence/features/<feature>/conformance/` へ変更した（Requirement 6 受入 2 の由来注記を正本とし、Requirement 2 受入 7・Requirement 3 受入 8・Requirement 12 受入 4・Boundary Context を追従）。既存記録は旧置き場で凍結保全、新規生成分から適用、旧パスの読み取り互換は P3 まで維持。本改訂は実装先行ではなく、仕様確定後に TDD で実装する正順の手続きである。

## 3. レビュー観点（criteria: requirements_placement_p1_evidence_path_change）

1. **受入間の整合**：5 箇所の変更が互いに矛盾しないか。「配置の正本は Requirement 6 受入 2」への集約は適切か
2. **契約の意味保全**：`conformance/`／`reviews/` の分離契約（Requirement 8 受入 4・MV-3）が evidence 配下でも維持されると読めるか
3. **凍結・互換の明確さ**：既存記録の凍結（PLC-DEC-009）と旧パス読み取り互換（P3 まで、PLC-DEC-011）が、実装者・読み手に誤解なく伝わるか
4. **対象アプリ二重基準**：`<対象アプリ>/` 前置の表記が、開発リポジトリと対象アプリの両文脈で破綻しないか
5. **下流への波及**：design・tasks・implementation で追従すべき事項の漏れが requirements 側の文言から生じないか
