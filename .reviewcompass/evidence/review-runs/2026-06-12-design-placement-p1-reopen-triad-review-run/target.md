# レビュー対象：reopen R-0（placement-p1-path-contracts）conformance-evaluation design 変更

## 0. variant 選定理由（実行前ゲートの記録）

- 使用 variant：`implementation_review_independent_3way`（context: triad_review、API 3 社独立）
- 役割：primary=anthropic-api/claude-sonnet-4-6、adversarial=openai-api/gpt-5.5、judgment=gemini-api/gemini-3.1-pro-preview
- 選定理由：本 reopen の requirements triad-review と同一構成（利用者承認 2026-06-12「開始」。正本は SESSION_WORKFLOW_GUIDE §3.3 (a-3)）

## 1. レビューの位置付け

reopen R-0（分類記録 `docs/reviews/reopen-classification-2026-06-12-placement-p1-path-contracts.md`）の
第3過程、conformance-evaluation design フェーズの triad-review。上流の requirements は triad-review
2 round（must-fix 1・should-fix 3 適用）→ review-wave（波及なし）→ alignment → approval（利用者承認）を
完了済み。確定した上流契約は「conformance 成果物（評価記録・spec update 草案・reopen handoff 成果物）の
配置ルート契約＝ `<対象アプリ>/.reviewcompass/evidence/features/<feature>/conformance/`。評価記録の
ファイル名形式は `<日付>-<mode>.md`（評価記録に限る）。`reviews/` との分離契約は evidence 配下でも維持。
既存記録は凍結、旧パス読み取り互換は P3 まで（終了は P3 の専用 reopen における仕様改訂）」である。

実装より先に仕様を確定する正順であり、**現時点で実装は旧パスへ書く挙動のまま**（意図的）。

## 2. 変更内容（conformance-evaluation design.md、12 箇所）

### 2.1 一括置換（11 箇所、意味は requirements 受入 2 への追従）

`<対象アプリ>/.reviewcompass/specs/<feature>/conformance/` → `<対象アプリ>/.reviewcompass/evidence/features/<feature>/conformance/`

対象節：設計方針一覧（§冒頭）、照合チェックモードのデータフロー図（…<日付>-check.md）、文書生成モードの
データフロー図（…<日付>-generation.md）、推定根拠の参照形式、両モードの実行記録保管、比較結果の出力、
所見 ID の採番手順（配下の最大番号＋1）、評価記録の配置先（§12.2）、draft-only spec update artifacts の
出力先、Boundary Context 対応表、機械検査 MV-1 の対象パス。

### 2.2 由来注記（設計方針一覧の配置先項へ追記）

> - **評価記録の type 値 `conformance_evaluation`** と配置先 `<対象アプリ>/.reviewcompass/evidence/features/<feature>/conformance/<日付>-<mode>.md` を機械可読に確定（Req 6。旧配置 `specs/<feature>/conformance/` からの変更は 2026-06-12 配置規約 PLC-DEC-003〜005・009〜011 反映。既存記録は旧置き場で凍結、旧パス読み取り互換は P3 まで維持。`conformance/`／`reviews/` の分離契約は evidence 配下でも維持）

## 2.3 round-2 注記：round-1 所見の適用（利用者承認 2026-06-12「承認」）

round-1 の同根クラスタ 3 件（C1 must-fix＝機械検査の凍結期スコープ、C2 should-fix＝読み取り互換の挙動、
C3 should-fix＝handoff 配置）を適用し、design.md へ次の 3 項を追加した。round-2 は適用後本文の収束確認である。

> **凍結期（P3 まで）の検査範囲**（§18 機械検査表の直後）：MV-1〜MV-3 の検査ルートは新配置
> `<対象アプリ>/.reviewcompass/evidence/features/<feature>/conformance/` を正とし、旧配置
> `specs/<feature>/conformance/` の凍結済み既存記録も読み取り互換の対象として検査範囲に含める
> （既存記録の構造検査は引き続き有効）。**新規記録が旧配置に現れた場合は違反として検出する**
> （凍結契約への違反）。新旧の二重カウントは記録ファイルの実体パスで区別する。

> **読み取り互換の挙動**（§12.2、P3 まで）：読み取りは新配置を優先し、見つからない場合に旧配置
> `specs/<feature>/conformance/` へフォールバックする（新→旧の順）。両方に同名記録が存在する場合は
> 新配置を正とし、警告を報告する。**書き込みは常に新配置**。互換の終了は P3 の専用 reopen における
> 本設計の改訂として扱う（暗黙の終了はない）

> **handoff の物理配置**（§13.9）：requirements 受入 2 のルート契約（`<対象アプリ>/.reviewcompass/evidence/features/<feature>/conformance/`）に従い、ファイル名形式は tasks の
> 成果物定義（`<日付>-reopen-handoff.yaml`・`<日付>-reopen-handoff.prompt.md`）が定める。

## 2.4 round-3 注記：round-2 所見の適用（利用者承認 2026-06-12「承認」）

round-2 の must-fix 2 件を適用し、design.md へ次の 2 項を追加した。round-3 は適用後本文の収束確認である。
なお round-2 の handoff 完全パス指摘は、design 本文が完全パスを明記済みで本 target の引用省略が原因だったため、
上記 §2.3 の引用を補正した（本文変更なし）。

> **採番手順への追記**（§比較結果の出力）：凍結期（P3 まで）は新旧両配置（evidence 配下と凍結された
> `specs/<feature>/conformance/` 配下）を走査して最大番号を統合算出し、ID の一意性は新旧合算のスコープで
> 担保する（旧凍結記録との ID 重複・リセットを防ぐ）

> **凍結集合の判定基準**（§18 凍結期段落への追記）：git 追跡履歴を正本とする。P1 実装反映コミットの時点で
> 旧配置に存在したファイルを凍結集合とし、それ以降に旧配置へ追加・変更されたファイルを違反として検出する
> （`git log` により再現可能。凍結集合の一覧固定は不要で、履歴が判定の正本）

## 3. レビュー観点（criteria: design_placement_p1_evidence_path_change）

1. **上流追従の完全性**：12 箇所の置換が、確定済み requirements（受入 2 のルート契約）と矛盾なく追従しているか
2. **取りこぼし**：design 内に旧パスを前提とする記述（図・採番・検査手順）が残っていないか
3. **MV-1／MV-3 検査の整合**：機械検査の対象パス変更後も検査の意味（type 値確認・ディレクトリ分離）が保たれるか
4. **実装ガイダンスの十分性**：implementation 段（ツールの書き込み先変更＋旧パス読み取り互換の TDD）に必要な設計情報が揃っているか
