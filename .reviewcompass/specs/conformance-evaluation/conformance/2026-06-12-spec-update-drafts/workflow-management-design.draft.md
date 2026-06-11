---
apply_status: draft_only
target_document: .reviewcompass/specs/workflow-management/design.md
contract_ids: [MLE-C-001, MLE-C-002, MLE-C-005, MLE-C-006]
source_conformance_record: ../2026-06-12-completed-followup-conformance.md
change_policy: minimal_existing_spec_change
---

# 草案：workflow-management design.md への反映候補

本草案は正本を直接書き換えない。反映は reopen 手続きで行う。

## 1. 機能依存マップの解決規則（additive、MLE-C-001）

設計の所有テーブル（design.md の「機能依存マップ（`stages/feature-dependency.yaml`）」行）と
配置図へ、次の設計事実を追記する。

- `next` サブコマンドは feature 一覧を `FEATURE_DEPENDENCY_SEARCH_PATHS`
  （`.reviewcompass/feature-dependency.yaml` → `stages/feature-dependency.yaml` →
  `feature-dependency.yaml`）の探索順で解決する（`resolve_feature_order`）。
- ソース直書きの `FEATURE_ORDER` 定数は既定値であり、`next` では解決結果で上書きされる。
- 解決失敗（ファイル不在・キー未定義）は立ち上げ案内（`feature_definition_required`）、
  整合違反（依存先行違反・循環）は fail-closed（DEVIATION）と、失敗の種類で挙動を分ける。

## 2. next 判定の状態遷移への追記（additive、MLE-C-002）

next 判定の kind 一覧へ `feature_definition_required` を追加する。

- 発生条件：feature 一覧が解決できない（対象アプリの初期状態を想定）。
- 返却値：verdict OK／exit 0、`current_state.feature_dependency_source` に解決元（不在時 null）。
- 案内内容：intent／feature-partitioning の実施と、承認された分割結果の記録先。
- 留意：本 kind は判定点として `WORKFLOW_DISCIPLINE_MAP.yaml` に登録し、effective prompt の
  生成対象とする（現状未登録。運用文書側の更新は reopen 対象外、post-write 検証を伴う）。

## 3. 配布テンプレート契約の設計境界（additive、MLE-C-005・C-006、所有者確定が前提）

配布物関連の設計境界として次を記録する（所有者を workflow-management に確定した場合）。

- 対象アプリ入口規律：`templates/entry/AGENT_ENTRY.template.md` を配布し、対象アプリの
  `.reviewcompass/AGENT_ENTRY.md` として実体化する。LLM 別差分は §10 に同居（別ファイル化しない）。
  既存入口（CLAUDE.md／AGENTS.md）への合流は承認つき 1 行追記（§11 の定型文）。
- hook 配布：`templates/hooks/pre-bash-precheck.sh.template` 1 本を配布し、プレースホルダは
  `{{REVIEWCOMPASS_PYTHON}}`・`{{REVIEWCOMPASS_DIR}}` の 2 つ（いずれも絶対パス必須）。
  初期設定時に実パスへ置換し、`.claude/hooks/` と `.codex/hooks/` の両方へ同一内容で複製する。
  hook は未置換トークンと検査ツールの存在を起動時に自己診断し、不備時は「hook 設定不備」という
  明確な理由で commit／push を拒否する（fail-closed）。
- 登録雛形：`.claude/settings.json` 断片と `.codex/hooks.json` 雛形を配布する。
- 配布 allowlist：`deploy-manifest.yaml` に entry／hooks／feature-dependency テンプレートを含める。
