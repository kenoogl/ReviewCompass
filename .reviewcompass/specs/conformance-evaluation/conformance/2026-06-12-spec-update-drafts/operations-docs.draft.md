---
apply_status: draft_only
target_document: docs/operations/WORKFLOW_NAVIGATION.md, docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml
contract_ids: [MLE-C-002]
source_conformance_record: ../2026-06-12-completed-followup-conformance.md
change_policy: minimal_existing_spec_change
---

# 草案：運用文書への `feature_definition_required` 追記候補

対象は reopen の対象外（運用文書）だが、更新時は post-write 検証を伴う。
仕様（T-004 の kind 契約）と同時に反映するのが望ましい。

## 1. WORKFLOW_NAVIGATION.md §2 への分岐追加（additive）

`completed` の直前または直後に次の節を追加する。

> ### `feature_definition_required`
>
> feature 一覧が解決できない（`feature-dependency.yaml` が見つからない、または
> `feature_order` キーが未定義）。対象アプリの初期状態で発生する。エラーではない
> （verdict OK）。新しい作業を始めず、intent と feature-partitioning を実施し、
> 承認された分割結果（依存の根拠と順序の導出を含む）を `.reviewcompass/feature-dependency.yaml`
> の `feature_order` キーに記録する。記録後に `next` を再実行する。

## 2. WORKFLOW_DISCIPLINE_MAP.yaml への判定点追加（additive）

`next_action_kind` 配下へ `feature_definition_required` を追加し、`required_disciplines` に
WORKFLOW_NAVIGATION.md の該当節（および初期設定ガイドの feature 立ち上げ節）を対応付ける。
これにより本 kind も「判定点ごとに 1 本の effective prompt」方針の生成対象になる
（現状、本 kind は effective prompt なしで返る）。

注意：DISCIPLINE_MAP の更新は `next --json` の出力（required_disciplines・effective prompt 生成）に
影響するため、更新後に既存 kind の回帰確認（`next --json` の再実行と差分確認）を行う。
