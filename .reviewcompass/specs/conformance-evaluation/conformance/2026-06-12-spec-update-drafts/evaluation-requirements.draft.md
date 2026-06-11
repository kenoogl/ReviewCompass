---
apply_status: draft_only
target_document: .reviewcompass/specs/evaluation/requirements.md
contract_ids: [MLE-C-007]
source_conformance_record: ../2026-06-12-completed-followup-conformance.md
change_policy: minimal_existing_spec_change
---

# 草案：evaluation requirements.md への反映候補（操縦 LLM 別の API 既定 variant）

本草案は正本を直接書き換えない。反映先（evaluation 仕様へ昇格するか、運用規律文書へ留めるか）の
判断が先行する（needs_human_decision: true）。昇格する場合の追記候補は次のとおり。

## 追記候補：操縦 LLM とレビュー役の独立性（additive）

新 Requirement（または既存のレビュー実行系 Requirement への受入基準追加）として：

> **目的**：セッションを操縦（起草・修正）する LLM と、その成果物を検証する LLM の系列を分離し、
> 自己レビューによる独立性低下を防ぐ。
>
> 受入基準：
> 1. 単独検証役（1 体での post-write 検証など）は、操縦 LLM と別系列を必須とする。
> 2. 3 役構成の adversarial（反証役）と judgment（判定役）は、操縦 LLM と別系列を必須とする。
> 3. 3 役構成の primary（検出役）は、操縦 LLM と同系列を許容する（最終判定を持たず、
>    残り 2 役の独立で全体の独立性が保たれるため）。
> 4. proxy_model（人の判断の代行）は、操縦 LLM と別系列を必須とする。
> 5. 操縦 LLM 別の既定 variant を `config/api-settings.yaml` に持つ：
>    - Claude Code 操縦時：接尾辞なしの `*_independent_3way` 系
>      （primary=anthropic/claude-sonnet-4-6、adversarial=openai/gpt-5.5、
>      judgment=gemini/gemini-3.1-pro-preview）
>    - Codex CLI 操縦時：`*_independent_3way_codex_operator` 系
>      （primary=openai/gpt-5.4、adversarial=anthropic/claude-opus-4-8、
>      judgment=gemini/gemini-3.1-pro-preview）
> 6. judgment と小規模 1 体検証（`post_write_verification_google`）は両操縦で共用し、
>    操縦を切り替えても判定基準の連続性を保つ。
> 7. 既存 variant の改名は行わない（規律文書・過去 run 記録・spec からの参照保全）。
>    将来、別の LLM が操縦する場合は同じ原則で役を回転して対応する。

根拠：設計記録 `docs/notes/2026-06-10-deployment-multi-llm-entry-design.md` §3.6
（2026-06-11 追補、利用者の個別承認済み）。実体：`config/api-settings.yaml`（反映済み）、
`templates/entry/AGENT_ENTRY.template.md` §10、`docs/operations/INITIAL_SETUP_LLM_GUIDE.md`。
