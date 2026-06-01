---
date: 2026-06-01
classifier: claude_code_main_session
classification: R 起点（requirements 正本修正、下流 design/tasks/implementation 連鎖再実施）
trigger_source: triad-review の 3 役モデル割り当てを独立 3 社（Opus/GPT/Gemini）へ変更する方針に伴い、独立 API 経由のレビュー記録を区別する新レビューモード値 api_mediated が必要となったため、foundation のレビューモード語彙正本を拡張する遡及
feature: foundation
findings: [review-mode-api_mediated]
---

## 分類根拠

本再オープンは、triad-review の 3 役モデル割り当てを Anthropic 単独（主役 Sonnet 4.6 ／ 敵対役 Opus ／ 判定役 Opus）から独立 3 社（主役 `claude-opus-4-8` ／ 敵対役 `gpt-5.5` ／ 判定役 `gemini-3.1-pro-preview`）へ変更する方針決定（2026-06-01 セッション 46、利用者明示承認）に伴い発生した。独立 API 経由のレビュー記録は Agent ツール経由（`subagent_mediated`）と区別する必要があり、新レビューモード値 `api_mediated` を foundation の語彙正本に追加する。

レビューモード語彙正本は foundation の要件 Req 6 受入 6 が所有する（requirements.md 行 131）。要件本文は「本語彙は今後の経路追加に対応する拡張余地を持つ」と明記し、過去 `subagent_mediated` 追加時は要件本文に名指しした前例（Change Intent 行 156、2026-05-22 確定）がある。利用者は本前例に倣い、要件正本に明示追加する **R 起点** を選択した（2026-06-01 セッション 46、利用者選択「R種別（requirements起点）」）。

発見契機は実装段の手法変更であり下流の欠陥ではないが、修正対象正本が要件であるため、要件から実装までの縦一列を連鎖再実施対象とする。

## 問題の事実

foundation のレビューモード語彙正本は現在 3 値で、次の 5 箇所に現れる：

- requirements.md 行 131（Req 6 受入 6）：`manual_dogfooding` ／ `runtime_mediated` を最低限、`subagent_mediated` を追加値として正本保持
- design.md 行 278-281（§3）：3 値を列挙
- runtime/foundation/metadata_contract.yaml 行 69-73：機械正本、3 値を列挙
- tests/foundation/test_t003_metadata.py 行 50：3 値固定でテスト（期待値配列）
- tasks.md 行 70（T-003 テスト要件）：3 値を列挙

独立 API 経由（複数プロバイダーの API を直接呼ぶ経路）の triad-review は、これら 3 値のいずれにも該当しない経路であり、新値 `api_mediated` が必要。

## requirements まで戻る所見（R 起点）

- **review-mode-api_mediated**：foundation の語彙正本に `api_mediated`（独立 API 経由＝複数プロバイダーの API を直接呼ぶレビュー記録）を第 4 の正規値として追加する

## trigger_map による連鎖再実施対象（計画書 §5.6、REOPEN_PROCEDURE §4）

要件の問題 → requirements を修正 → 下流（design ／ tasks ／ implementation）を reopen 対象 → 依存順に連鎖再実施。再実施対象は各フェーズの alignment と approval（drafting ／ triad-review ／ review-wave は正本を手修正のうえ整合確認・承認のみ再実施）：

- requirements：alignment ／ approval
- design：alignment ／ approval
- tasks：alignment ／ approval
- implementation：alignment ／ approval（現在 false、通常フローで段通過）

## spec.json フラグ差し戻し（第 1 過程ステップ 6、承認後に実行）

foundation/spec.json：

- `reopened.requirements`：false → **true**
- `workflow_state.requirements.alignment`：true → **false**
- `workflow_state.requirements.approval`：true → **false**
- `workflow_state.design.alignment`：true → **false**
- `workflow_state.design.approval`：true → **false**
- `workflow_state.tasks.alignment`：true → **false**
- `workflow_state.tasks.approval`：true → **false**
- `recheck.upstream_change_pending`：false → **true**
- `recheck.impacted_downstream_phases`：[] → **["design","tasks","implementation"]**

注：`reopened.design` は A-018（2026-05-29）で既に true のため維持。implementation は `impacted_downstream_phases` に含むが、その alignment ／ approval は既に false のため差し戻し操作は不要であり、連鎖再実施は第 3 過程の通常フロー（review-wave → alignment → approval）で段通過する。各段の drafting ／ triad-review ／ review-wave は現状を維持する。

## 正本修正の対象（第 2 過程で実施）

1. **requirements.md 行 131（Req 6 受入 6）**：`subagent_mediated` の記述に続けて、独立 API 経由を区別する `api_mediated` を追加正規値として明記
2. **requirements.md Change Intent（行 156 付近）**：「レビューモード語彙に独立 API 経由（`api_mediated`）を正式値として追加（2026-06-01 セッション 46、triad-review 3 役の独立 3 社化に伴う）」を追記
3. **design.md §3（行 278-281）**：列挙に `api_mediated`（独立 API 経由のレビュー記録）を追加
4. **runtime/foundation/metadata_contract.yaml（行 69-73）**：`review_mode` 列挙に `api_mediated` を追加
5. **tasks.md 行 70（T-003 テスト要件）**：`review_mode` の値テスト列挙に `api_mediated` を追加
6. **tests/foundation/test_t003_metadata.py 行 50**：期待値配列に `api_mediated` を追加

## 適用範囲の注記

本変更は後方互換（既存 3 値は有効のまま、第 4 値を追加）。下流機能（runtime ／ evaluation ／ analysis 等）はレビューモード語彙を参照するのみで再定義していないため、機能横断の波及（他機能の正本修正）は発生しない。runtime 以降の triad-review が `api_mediated` を使用する。foundation の既済 implementation triad-review は `subagent_mediated` のまま据え置く（利用者決定 2026-06-01 セッション 46、foundation はモデル変更の対象外）。
