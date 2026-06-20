# GPT primary 001/002 post-fix recheck: registry / contract / precheck authority boundary

## 対象所見

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-001`
- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-002`

## 指摘内容

- 001: Requirement 12 §1 が `stages/operation-registry.yaml` を operation contract schema の配置先のように読め、全体構造・Requirement 13 §3 の `stages/operation-contracts.yaml` 正本と矛盾していた。
- 002: precheck vocabulary / output contract の正本が `WORKFLOW_PRECHECK.md`、`WORKFLOW_PRECHECK_DETAILS.md`、script implementation にあるように読め、registry / contract 境界を弱めていた。

## 修正内容

- Requirement 12 §1 を `operation registry / preflight binding schema` として明確化し、`stages/operation-registry.yaml` は registry 固有メタデータと preflight binding の正本であり、operation contract field / semantics の正本ではないと定義した。
- operation contract の物理正本を Requirement 13 の `stages/operation-contracts.yaml` と明記した。
- registry schema が `effect_kind`、`approval_required`、`phase_boundary`、preconditions / postconditions、side effects、branching、max effect などの contract field を構造的に受け付けないと明記した。
- 軽量 precheck 節で、`WORKFLOW_PRECHECK_DETAILS.md` と script argparse が正本とするのは precheck CLI の呼び出し形式・表示・ログ形式に限ると明記した。
- `required_action` 語彙、operation contract field、preconditions / postconditions、出力・副作用 contract は `.reviewcompass/schema/`、`stages/operation-contracts.yaml`、Requirement 12〜13 の registry / contract 境界を正本とすると明記した。

## 再点検結果

- 001 の矛盾は、registry と operation contract の物理正本を分離し、registry を contract 参照・投影・binding に限定したことで解消した。
- 002 の drift risk は、precheck docs / script の正本性を CLI surface に限定し、contract 語彙・semantics の正本から外したことで解消した。
- C8 の registry schema 禁止キー補強と整合しており、registry 側が contract authority field を再定義する余地は設計上閉じられている。

## 残リスク

- 実装段階では、`operation_registry.schema.json` と `operation_contract.schema.json` の分離、および registry 禁止キー fixture を TDD で追加する必要がある。
- 既存の precheck 実装が required_action や output semantics をコード内定義している場合は、Phase 1 以降で schema 参照へ寄せる必要がある。
