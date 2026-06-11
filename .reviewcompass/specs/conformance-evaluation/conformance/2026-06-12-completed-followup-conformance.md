---
type: conformance_evaluation
mode_internal: completed_followup_conformance
author: implementation
reviewer: conformance-evaluation
status: gap_found
target_commit: 67de747
evaluated_commit_range: 702c00c..3730571
related_artifacts:
  runtime: []
  evaluation:
    - config/api-settings.yaml
  workflow_management:
    - tools/check-workflow-action.py
    - tests/tools/test_check_workflow_action.py
    - stages/feature-dependency.yaml
    - stages/completed/maintenance-2026-06-11-feature-order-generalization.yaml
    - templates/entry/AGENT_ENTRY.template.md
    - templates/hooks/pre-bash-precheck.sh.template
    - templates/hooks/claude-settings.json.template
    - templates/hooks/codex-hooks.json.template
    - templates/specs/feature-dependency.yaml.template
    - deploy-manifest.yaml
    - docs/operations/DEPLOYMENT.md
    - docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md
    - docs/operations/INITIAL_SETUP_LLM_GUIDE.md
    - docs/notes/2026-06-10-deployment-multi-llm-entry-design.md
  self_improvement:
    - learning/workflow/proposals/WP-001-finding-cause-attribution.yaml
---

# 配布側複数 LLM 入口整備（アドホック開発）の completed follow-up conformance 評価

## 目的（Purpose）

本記録は、全 7 feature の workflow_state が `completed` に到達した後にアドホック開発で実施された
「配布側複数 LLM 入口整備」（設計記録 `docs/notes/2026-06-10-deployment-multi-llm-entry-design.md`、
実装計画ステップ 1〜5 ＋ 論点 5）の成果物が、既存の正本仕様
（workflow-management／evaluation の requirements・design・tasks）と適合しているかを評価する。

評価の位置付けは通常の feature workflow ではなく、completed 到達後の実装先行作業に対する
conformance 評価である（先例：`2026-06-09-completed-followup-conformance.md`）。
TODO_NEXT_SESSION.md §4 の未完了義務 1「conformance-evaluation を起動し、アドホック開発した内容の
差分を workflow-management 等の仕様へ反映する」に対応する。

Requirement 9・12 に従い、本記録は requirements.md／design.md／tasks.md を直接書き換えない。
仕様更新は draft-only 草案（`2026-06-12-spec-update-drafts/`）と reopen 引き渡しパッケージ
（`2026-06-12-reopen-handoff-package.yaml`）として出力し、正式な正本更新は workflow-management の
reopen 手続き（triad-review／review-wave／alignment／approval）に引き渡す。

## 評価対象（Evaluated Scope）

| ステップ | 内容 | コミット |
| --- | --- | --- |
| 1 | 設計記録の作成と post-write 検証 | 702c00c |
| 2 | ツール一般化（feature_order 外出し・立ち上げ案内・整合検査） | cde1f5c |
| 3 | テンプレート群（入口・hook・feature-dependency）と deploy-manifest 追加 | c2903df |
| 論点 5 | 操縦 LLM 別の API 既定 variant | 635afad |
| 4 | ガイド 3 文書の更新 | 800ccc3 |
| 5 | 配布物再生成・smoke・模擬対象アプリ実証（後続：gitignore 手順追記） | 3730571（実験はテストとして cde1f5c に固定化） |

ステップ 2 は `stages/completed/maintenance-2026-06-11-feature-order-generalization.yaml` の
maintenance side track として実施された（workflow-management の reopen 手続きは経ていない）。
同記録の out_of_scope_note が、本 conformance 評価を別義務として明示している。

## 判定（Verdict）

判定：`gap_found`。

成果物は実装・テスト・検証証跡のレベルでは設計記録の意図に適合している
（TDD テスト先行、回帰確認、post-write 検証、模擬対象アプリでの実証）。
しかし実装先行のため、実装契約が正本仕様（workflow-management／evaluation の
requirements・design・tasks）より強くなっており、仕様側に未反映の契約と
1 件の語彙衝突（feature_order ／ phase_order）が残っている。

## 適合マトリクス（Conformance Matrix）

| 対象 | 適合結果 | 証跡 |
| --- | --- | --- |
| ステップ 1：設計記録 | 適合（post-write 検証済み） | `docs/notes/2026-06-10-deployment-multi-llm-entry-design.md`；review-run `2026-06-11-entry-design-topic5-postwrite`（r1・r2） |
| ステップ 2：ツール一般化 | 実装・テストレベルで適合、仕様レベルで gap | maintenance 記録（TDD 失敗テスト 10 件先行、回帰 155／599／108／119 件）；`tests/tools/test_check_workflow_action.py`；MLE-GAP-001〜003 |
| ステップ 3：テンプレート群 | 成果物レベルで適合、仕様所有者が未確定 | `templates/entry/`・`templates/hooks/`・`templates/specs/feature-dependency.yaml.template`；`deploy-manifest.yaml` allowlist 追加；MLE-GAP-004 |
| 論点 5：操縦 LLM 別 variant | 設定・テンプレートレベルで適合、仕様レベルで gap | `config/api-settings.yaml`；`templates/entry/AGENT_ENTRY.template.md` §10；review-run `2026-06-11-entry-design-topic5-postwrite-r2`；MLE-GAP-005 |
| ステップ 4：ガイド更新 | 適合（post-write 検証済み） | review-run `2026-06-11/12-{setup-guide,user-guide,deployment-adapter-row}-postwrite`（r1〜r3、approval.yaml 含む）；ただし規律文書側は MLE-GAP-001 に含む |
| ステップ 5：実証と回避策 | 適合（実験はテスト固定化済み）、根本対応が未実装 | 対象アプリ独自 feature 構成での next 動作テスト（cde1f5c）；`INITIAL_SETUP_LLM_GUIDE.md` §8 gitignore 手順（3730571）；MLE-GAP-006 |

## 実装由来契約の ownership map（Requirement 9 受入 1）

| contract_id | claim（実装が定めた契約） | classification | primary_owner_candidate | secondary_owner_candidate | contract_refs / evidence_refs |
| --- | --- | --- | --- | --- | --- |
| MLE-C-001 | feature 一覧は feature-dependency.yaml の `feature_order` キーから解決し、探索順は `.reviewcompass/` → `stages/` → 直下 | spec_update_candidate | workflow-management requirements（Req 8） | workflow-management design | `tools/check-workflow-action.py`（FEATURE_DEPENDENCY_SEARCH_PATHS、resolve_feature_order）；test 同名 |
| MLE-C-002 | `feature_order` 未定義時は `kind: feature_definition_required`（verdict OK）で intent／feature-partitioning の実施と記録を案内する | spec_update_candidate | workflow-management tasks（T-004 の kind 語彙） | docs/operations/WORKFLOW_NAVIGATION.md・WORKFLOW_DISCIPLINE_MAP.yaml | `feature_definition_next_state`；`INITIAL_SETUP_LLM_GUIDE.md`・`INITIAL_DEPLOYMENT_USER_GUIDE.md` |
| MLE-C-003 | `feature_order` と `depends_on` の整合検査（依存される機能が先、循環依存の検出）。違反時は `kind: unknown`／DEVIATION（fail-closed） | spec_update_candidate | workflow-management requirements（Req 8） | workflow-management tasks（T-004） | `validate_feature_order_consistency` |
| MLE-C-004 | 機能順のキー名は `feature_order`。仕様の `phase_order`（`feature-dependency.yaml#phase_order` 参照）とは別語彙 | design_conflict_candidate | workflow-management requirements（Req 1 受入 4・Req 8 受入 3）・tasks（T-002・T-003） | workflow-management design | `stages/feature-dependency.yaml`；`stages/feature-partitioning/2026-05-24-proposal.md` の phase_order |
| MLE-C-005 | 対象アプリ入口規律は `.reviewcompass/AGENT_ENTRY.md`（テンプレート配布、§10 に LLM 別の注意、§11 に挿入行定型文）。配布 allowlist に entry／hooks／feature-dependency テンプレートを含む | spec_update_candidate | workflow-management（配布契約の所有者候補） | docs/operations/DEPLOYMENT.md §4 | `templates/entry/AGENT_ENTRY.template.md`；`deploy-manifest.yaml` |
| MLE-C-006 | hook はプレースホルダ 2 値（`{{REVIEWCOMPASS_PYTHON}}`・`{{REVIEWCOMPASS_DIR}}`、絶対パス必須）で配布し、未置換・実体欠落を自己診断して「hook 設定不備」の明確な理由で fail-closed する。`.claude/hooks/` と `.codex/hooks/` へ同一内容で複製 | spec_update_candidate | workflow-management（配布契約の所有者候補） | docs/operations/INITIAL_SETUP_LLM_GUIDE.md | `templates/hooks/pre-bash-precheck.sh.template`；同 claude-settings／codex-hooks |
| MLE-C-007 | 操縦 LLM 別の API 既定 variant：Claude 操縦時は `*_independent_3way` 系（adversarial を gpt-5.5 へ強化）、Codex 操縦時は新設 `*_independent_3way_codex_operator` 系。独立性原則（単独検証役・adversarial・judgment・proxy_model は操縦 LLM と別系列必須、primary は同系列許容）。judgment と小規模 1 体検証は両操縦で共用 | spec_update_candidate | evaluation requirements／design（api_providers の所有 feature） | docs/operations の review 規律文書 | `config/api-settings.yaml`；`AGENT_ENTRY.template.md` §10；設計記録 §3.6 |
| MLE-C-008 | ツール実行時生成物（`docs/logs/workflow-precheck.log`、`.reviewcompass/effective-prompts/`）が対象アプリで post-write 検証対象に拾われる問題は、初期設定ガイド §8 の `.gitignore` 追記で回避（根本対応は未実装） | implementation_change_candidate | workflow-management tasks／implementation（T-004 の post-write target detection） | docs/operations/INITIAL_SETUP_LLM_GUIDE.md §8 | 2026-06-12 ステップ 5 実験で発見（TODO_NEXT_SESSION.md §4-2） |

## Conformance Gaps

各 gap の `classification` は conformance-evaluation Requirement 10 受入 3 の基本値を使う。

### MLE-GAP-001：判定種別 `feature_definition_required` が規律文書と仕様に未反映

- 対応契約：MLE-C-002（MLE-C-001 の立ち上げ挙動を含む）
- 実装は新しい `next_action.kind`（`feature_definition_required`、verdict OK／exit 0）を追加したが、
  次の正本に存在しない：
  - `docs/operations/WORKFLOW_NAVIGATION.md` §2（判定結果の共通分岐の一覧）
  - `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml` の `next_action_kind` 判定点
  - workflow-management tasks.md T-004（next サブコマンドの kind 契約）
- 付随する観察：この kind は effective prompt（`next_action.effective_prompt`）なしで返る。
  WORKFLOW_NAVIGATION.md §1 の「判定点ごとに 1 本の effective prompt」方針と、
  DISCIPLINE_MAP に判定点が未登録であることの両方に関わる。
- change_type：additive。needs_human_decision：false（追記内容は実装から一意に導ける）。

### MLE-GAP-002：feature 一覧の外出しと探索順が Requirement 8 と未整合

- 対応契約：MLE-C-001・MLE-C-003
- workflow-management requirements.md Requirement 8 受入 1 は
  「`stages/feature-dependency.yaml` を機能間処理順と依存関係の一元保管先とする」と定めるが、
  実装は探索順 `.reviewcompass/feature-dependency.yaml` → `stages/feature-dependency.yaml` →
  `feature-dependency.yaml` で解決する（対象アプリでは `.reviewcompass/` 配置が正、
  開発リポジトリでは従来どおり `stages/` 配置で互換）。
- 整合検査（依存先行・循環検出、違反時 DEVIATION）も Requirement 8 に存在しない新契約。
- change_type：additive（開発リポジトリでの既存挙動は不変。「一元保管先」の主張に
  対象アプリ側の解決規則を追記する形）。needs_human_decision：false。

### MLE-GAP-003：`feature_order` と仕様語彙 `phase_order` の衝突

- 対応契約：MLE-C-004
- 仕様の語彙：requirements.md Requirement 1 受入 4・Requirement 8 受入 3、tasks.md T-002・T-003 は
  機能順を `feature-dependency.yaml#phase_order` で参照し、段集合 YAML 側のフィールド名を
  `feature_order:`（参照先 = phase_order）とする。
- 実装の語彙：feature-dependency.yaml の最上位キー `feature_order` が機能順の実体である。
  現行の `stages/feature-dependency.yaml` に `phase_order` キーは存在しない。
- すなわち仕様上の「`feature_order`（参照フィールド名）→ `phase_order`（実体）」と
  実装上の「`feature_order`（実体）」が同名異義で衝突している。
- 既存の関連 gap（本アドホック開発以前から存在、原因帰属のため区別して記録）：
  - `stages/feature-dependency.yaml` に `phase_order` がそもそも実体化されていない
  - T-002 の `stages/feature-dependency.schema.json`（パース仕様の正本）が未作成
  - T-003 の段集合 YAML 8 ファイルが `stages/` に存在しない
  - `features` マップには conformance-evaluation の 1 件しかなく（T-002 は 7 機能を要求）、
    新設の整合検査は記載済み依存しか検査できない
- change_type：semantic_change（どちらの語彙へ寄せるかの判断で既存契約の意味が変わる）。
  existing_contract_changed：true。human_escalation_required：true。
  downstream_reopen_required：true（採否により design・tasks へ波及）。

### MLE-GAP-004：テンプレート群と配布 allowlist の仕様所有者が未確定

- 対応契約：MLE-C-005・MLE-C-006
- 入口テンプレート（AGENT_ENTRY、§10 LLM 別の注意、§11 挿入行定型文）、hook テンプレート 3 点
  （プレースホルダ規則・fail-closed 自己診断・両 LLM への複製）、feature-dependency テンプレート、
  deploy-manifest への allowlist 追加は、requirements／design レベルの所有 feature を持たない
  （`pre-bash`・`deploy-manifest`・`配布物` は全 feature の requirements・design・tasks に出現しない）。
- 先例（2026-06-09 評価の D-021／D-023）でも配布関連成果物は workflow_management に分類されており、
  本記録も workflow-management を所有者候補とするが、確定は人間判断とする。
- change_type：additive。needs_human_decision：true（所有者の確定）。

### MLE-GAP-005：操縦 LLM 別の API 既定 variant が evaluation 仕様に未反映

- 対応契約：MLE-C-007
- `config/api-settings.yaml` に新設された `*_independent_3way_codex_operator` 系 variant、
  Claude 操縦既定の adversarial 強化（gpt-5.4 → gpt-5.5）、および独立性原則
  （単独検証役・adversarial・judgment・proxy_model は操縦 LLM と別系列必須、primary は同系列許容、
  judgment と小規模 1 体検証は両操縦で共用）は、利用者が個別承認した設計判断（設計記録 §3.6）だが、
  evaluation の requirements／design に variant・操縦 LLM の概念がそもそも存在しない。
- 既定 variant の選択規則は現状、設計記録・AGENT_ENTRY テンプレート §10・初期設定ガイドにのみある。
- change_type：additive。needs_human_decision：true（evaluation 仕様へ昇格するか、
  運用規律文書へ留めるかの判断）。

### MLE-GAP-006：ツール実行時生成物の post-write 対象除外が未実装（根本対応候補）

- 対応契約：MLE-C-008。TODO_NEXT_SESSION.md §4 義務 2 の根本対応に対応する。
- `next` 実行で生成される `docs/logs/workflow-precheck.log` と `.reviewcompass/effective-prompts/` が、
  対象アプリでは post-write 検証対象（`docs/` 配下）として拾われ、通常作業を阻害する。
  現状は初期設定ガイド §8 の `.gitignore` 追記（3730571）で回避している。
- 根本対応候補：ツールが自分の実行時生成物を post-write 対象判定
  （`is_post_write_verification_target`）から除外する。
- classification：implementation_change_candidate。change_type：additive。
  needs_human_decision：true（回避策維持か根本対応かの判断、および除外規則の安全性確認）。

## Non-Gaps（gap でないことの確認）

- ステップ 2 は TDD（失敗テスト 10 件先行）と回帰確認（合計 981 件、改修起因の失敗ゼロ）を満たし、
  maintenance side track 記録（trigger／allowed_scope／completion_conditions）も規律どおり残っている。
- 文書変更（設計記録・ガイド 3 文書・gitignore 手順）はすべて post-write 検証
  （review-run・triage・manifest・重要件の approval）を経ている。
- 模擬対象アプリ実験（設計記録 §2-4 の DEVIATION 問題）は、対象アプリ独自 feature 構成で
  `next` が stage 判定を返すことのテストとして `tests/tools/test_check_workflow_action.py` に
  固定化されており、再発を機械検知できる。
- 配布物のビルド成果物（`build/deploy/`）は追跡対象外として整理済みで、成果物の二重管理はない。

## 付随観察（本評価の対象外だが記録する）

- `tools/conformance_evaluation/schemas/evaluation_record.schema.json` の `mode_internal` は
  `generation`／`check` の 2 値 enum であり、先例 2026-06-09 記録と本記録の
  `completed_followup_conformance` を許容しない。Requirement 11 が先例記録を正式化済みのため、
  スキーマ側の追従が必要（スキーマは `tools/` 配下のため、修正は別途の実装作業）。
- 検討材料として `learning/workflow/proposals/WP-001-finding-cause-attribution.yaml`
  （外れ所見の原因分類軸）が記録済み。本記録では gap の原因帰属（アドホック開発由来か既存由来か）を
  MLE-GAP-003 で区別しており、同提案の趣旨と整合する。

## Spec update proposals（Requirement 9 受入 3）

| 対象文書 | contract_ids | 要旨 | needs_human_decision |
| --- | --- | --- | --- |
| `.reviewcompass/specs/workflow-management/requirements.md` | MLE-C-001・C-002・C-003・C-004 | Requirement 8 へ feature_order 外出し・探索順・立ち上げ案内・整合検査を追記。受入 3／Req 1 受入 4 の `phase_order` 語彙の調停 | true（語彙調停が semantic_change） |
| `.reviewcompass/specs/workflow-management/design.md` | MLE-C-001・C-002・C-005・C-006 | 所有テーブル・配置図への探索順と新 kind の追記、配布テンプレート契約の設計境界 | true（配布契約の所有者確定に依存） |
| `.reviewcompass/specs/workflow-management/tasks.md` | MLE-C-002・C-004・C-008 | T-004 の kind 語彙と post-write 対象除外の実装変更候補、T-002 の schema／phase_order 契約の現実化 | true |
| `.reviewcompass/specs/evaluation/requirements.md`（design.md 含む） | MLE-C-007 | 操縦 LLM 別の既定 variant と独立性原則の外部可視契約化 | true（昇格先の判断） |
| `docs/operations/WORKFLOW_NAVIGATION.md`・`WORKFLOW_DISCIPLINE_MAP.yaml` | MLE-C-002 | `feature_definition_required` 分岐の追加と判定点登録（reopen 対象外の運用文書。更新時は post-write 検証） | false |

draft-only 草案：`2026-06-12-spec-update-drafts/`（各草案は `apply_status: draft_only` を持ち、
正本を直接書き換えない）。

## Reopen 引き渡し（Requirement 12）

reopen handoff package：`2026-06-12-reopen-handoff-package.yaml`。
`change_policy: minimal_existing_spec_change` を方針とし、MLE-GAP-003 のみ
`change_type: semantic_change`（human_escalation_required: true）、他は `additive`。
各 gap は reopen 後の対象 phase が triad-review／review-wave／alignment／approval を完了するまで
resolved 扱いにしない。

## 推奨される後始末（Recommended Remediation）

1. 利用者判断：MLE-GAP-003 の語彙調停（案 A：仕様を実装語彙 `feature_order` へ寄せる ／
   案 B：実装を仕様語彙 `phase_order` へ寄せる ／ 案 C：両者併存の対応規則を明文化）。
2. 利用者承認のうえ workflow-management の reopen を起動し、requirements → design → tasks の順で
   草案を反映、`triad-review / review-wave / alignment / approval` で整合確認する。
3. evaluation 仕様への MLE-C-007 の昇格要否を判断する（昇格しない場合は運用規律文書側の正本を確定）。
4. 規律文書（WORKFLOW_NAVIGATION.md・WORKFLOW_DISCIPLINE_MAP.yaml）へ
   `feature_definition_required` を追記する（post-write 検証を伴う通常文書更新）。
5. MLE-GAP-006 の根本対応（実行時生成物の post-write 対象除外）の実施可否を判断する
   （実施する場合は maintenance side track ＋ TDD）。
