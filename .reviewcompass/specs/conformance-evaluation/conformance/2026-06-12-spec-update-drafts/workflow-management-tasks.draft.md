---
apply_status: draft_only
target_document: .reviewcompass/specs/workflow-management/tasks.md
contract_ids: [MLE-C-002, MLE-C-004, MLE-C-008]
source_conformance_record: ../2026-06-12-completed-followup-conformance.md
change_policy: minimal_existing_spec_change
---

# 草案：workflow-management tasks.md への反映候補

本草案は正本を直接書き換えない。tasks.md 本体の再作成・タスク分解の確定は conformance-evaluation の
責務外であり（Requirement 12 受入 5）、反映の要否と形は reopen 手続きで判断する。

## 1. T-004（check-workflow-action.py）の契約追記候補（additive、MLE-C-002）

T-004 の責務記述へ次を追加する。

- next サブコマンドは feature 一覧を feature-dependency.yaml の `feature_order` キーから
  探索順（`.reviewcompass/` → `stages/` → 直下）で解決する。
- kind 語彙へ `feature_definition_required` を追加する（feature 一覧が解決できない場合の
  立ち上げ案内、verdict OK）。「fail-closed の既定（`feature_order` 解決失敗の全ケースで遮断）」の
  記述は、(a) 未定義 → 立ち上げ案内（OK）、(b) 整合違反 → 遮断（DEVIATION）の 2 区分へ精密化する。
- テスト要件へ「対象アプリ独自 feature 構成で next が DEVIATION にならず stage 判定を返すこと」
  （2026-06-10 設計記録 §2-4 実験の固定化、実装済み）を追加する。

## 2. T-002（機能依存マップ）の契約現実化の選択肢（semantic_change、MLE-C-004、人間判断必須）

T-002 は `phase_order` キー・`stages/feature-dependency.schema.json`・7 機能の `features` 列挙を
要求するが、いずれも現行リポジトリに実体がない（本アドホック開発以前からの既存 gap）。
語彙は案 A（MLE-DEC-001、2026-06-12 利用者決定）により `feature_order` への一本化で確定。
残る判断は次の 2 点。

- schema の扱い：`feature_order` キー（文字列配列、必須／任意）を含む schema を新規作成するか、
  schema 契約自体を T-004 の実装検査（`resolve_feature_order`・`validate_feature_order_consistency`）
  へ置き換えるか。
- `features` 列挙：7 機能すべての `depends_on` を実体化するか、記載済み機能のみ検査する現行実装を
  契約として追認するか（現行の整合検査は記載済み依存しか検査できない点に留意）。

## 3. post-write 対象判定の実装変更候補（additive、MLE-C-008、人間判断必須）

T-004 の post-write target detection に対する実装変更候補（TODO_NEXT_SESSION.md §4 義務 2 の根本対応）。

- 内容：ツール自身の実行時生成物（`docs/logs/workflow-precheck.log`、
  `.reviewcompass/effective-prompts/`）を `is_post_write_verification_target` の対象から除外する。
- 現状の回避策：INITIAL_SETUP_LLM_GUIDE.md §8 の `.gitignore` 追記（対象アプリ側）。
- 判断点：除外規則が「検証逃れ」に転用されない安全性（除外は生成物の正確なパスに限定し、
  ワイルドカードで `docs/` を広く除外しない）。実施する場合は maintenance side track ＋ TDD。
