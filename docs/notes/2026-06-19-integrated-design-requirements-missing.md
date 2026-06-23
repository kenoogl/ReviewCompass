---
date: 2026-06-19
record_type: incident-memo
status: active
topic: 統合設計メモの要件未追記の経緯
related:
  - docs/notes/2026-06-18-integrated-design-selection-execution-layers.md
  - docs/notes/2026-06-18-mechanized-workflow-execution-design.md
  - .reviewcompass/specs/workflow-management/requirements.md
---

# 統合設計メモの要件追記が未完了になった経緯

## 依頼の原文

2026-06-18 セッション（77e272a2）にて：

> 「今考えている改善案は、`docs/notes/2026-06-18-integrated-design-selection-execution-layers.md`
> と `docs/notes/2026-06-18-mechanized-workflow-execution-design.md` がもとになっている。
> これらの要件を `intent.md` とその下位フェーズの `requirements.md` に書き込み、
> ワークフローに従って開発していくやり方。」

## 何が起きたか

1. 直前の議論で「Phase 1 のうち最小限として先に確定すべきものを挙げて」という流れがあった
2. Claude がこれを受け、要件追記の対象を最小2点（AC10・AC11：スキーマ定義ファイル）だけに絞り込んだ
3. 利用者が途中で気づき「本当に2カ所だけなのか？　元文書には多数の項目がある」「やり直し」と指示
4. しかしセッションのコンテキスト（会話の記憶）が4〜5回枯渇し、やり直しが完遂されないまま AC10・AC11 のみのコミットで終わった

## 実際に追記された内容（requirements.md）

- AC10：`required_action` の19語彙スキーマ定義（`.reviewcompass/schema/required_action.schema.json`）
- AC11：`next --json` 応答スキーマ定義（`.reviewcompass/schema/next_action_response.schema.json`）

## 追記されていない内容

| 元文書の章 | 内容 |
|---|---|
| 統合設計 §3 | 19種の `required_action` と operation contract の対応（`effect_kind`・`approval_required`） |
| 統合設計 §4 Phase 0 | 選択層 TDD 実装要件（D-003 §7.1 の6テスト・`reopen-recompile`） |
| 統合設計 §4 Phase 2〜6 | `operation-list`・preflight 強制・有効プロンプト構造化・機械的ブロック・LLM 裁判官 |
| 統合設計 §5.1 | 承認ゲートの統一定義（`wait_for_human_decision`/`record_human_decision` ペア） |
| 統合設計 §5.2 | 側道スタックの統一定義（`side-track-push/pop`） |
| 統合設計 §5.3 | 状態スナップショット（`workflow-state-snapshot.yaml`） |
| 機械化設計全体 | `effect_kind`・`phase_boundary`・operation contract スキーマ・タスク分類 |

`intent.md` への追記は一切行われていない。

## 原因

1. **Claude が範囲を早期に絞りすぎた**：「最小限を挙げて」という前の発言を受けて、全体追記から最小2点への作業範囲の限定を利用者合意なしに行った
2. **コンテキスト枯渇による継続の失敗**：「やり直し」指示後にコンテキストが複数回切れ、やり直しが有効に引き継がれなかった

## 次のアクション

統合設計メモ（2本）の内容全体を `intent.md` と `requirements.md` に追記する作業が残っている。
reopen または新規の要件追記として、正式なワークフロー手続きで実施する。
