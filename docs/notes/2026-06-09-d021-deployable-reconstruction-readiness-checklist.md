---
date: 2026-06-09
candidate_id: D-021
title: deployable reconstruction readiness checklist
status: checklist_ready
source: docs/notes/2026-06-05-future-development-candidates.md
last_updated: 2026-06-09
---

# D-021 Deployable Reconstruction Readiness Checklist

## 0. 位置づけ

このチェックリストは、D-021 `deployable reconstruction readiness` を進めるための作業台帳である。

通常 workflow の作業順序正本ではない。作業開始時は必ず `tools/check-workflow-action.py next --json` を確認し、`completed` が維持されている場合に限り、この台帳に従って completed 後の改善作業として進める。

D-021 の目的は、ReviewCompass が自己適用だけでなく、外部リポジトリへ安定して配置でき、複数ケースから研究用データを取得できる状態かを点検することである。

未チェックの `[ ]` 項目は、この文書の欠陥ではなく、D-021 作業で順に消化する未完了タスクを表す。この文書作成時点の完了条件は、D-021 の作業単位、証跡基準、判定値、deployment smoke 条件、escalation rules がチェックリストとして参照可能になっていることである。

front matter の `status: checklist_ready` は、チェックリスト文書自体が D-021 の作業台帳として利用可能であることを示す。D-021 本体の readiness 判定が完了したことは意味しない。現在の作業状態は Section 8 の snapshot と、作業開始時に再実行する `next --json` で確認する。

## 0.1 Checklist Creation Done Criteria

- [x] D-021 の作業単位を checklist 化した。
- [x] readiness report の出力先を確定した。
- [x] readiness verdict の使い分け条件を定義した。
- [x] deployment readiness の確認項目と証跡基準を定義した。
- [x] data acquisition readiness の確認項目と証跡基準を定義した。
- [x] deployment smoke の成功条件と失敗条件を定義した。
- [x] D-022 / D-023 / D-024 の繰り上げ条件を定義した。

## 1. 参照正本

- [x] `tools/check-workflow-action.py next --json` が `kind: completed` を返すことを確認する。
- [x] 作業ツリーが clean であることを確認する。
- [x] D-021 本文を確認する。
- [x] `docs/plan/reconstruction-plan-2026-05-21.md` の deployability / relative links / app-tool separation 方針を要約する。
- [x] D-020 / D-022 / D-023 / D-024 との関係を要約する。

Section 1 の未完了項目は、Section 2 の readiness report 本文を書く前に完了する。Section 1 が完了していない状態では、readiness report の目的、範囲、非範囲、escalation note を確定しない。

完了済み項目の証跡:

| Item | Evidence |
| --- | --- |
| `next --json` completed | 2026-06-09 に `.venv/bin/python3 tools/check-workflow-action.py next --json` を実行し、`next_action.kind == completed` を確認した。 |
| worktree clean | 2026-06-09 の checklist 作成開始時に `git status --short` が空であることを確認した。 |
| D-021 本文確認 | `docs/notes/2026-06-05-future-development-candidates.md` の D-021 節と推奨着手順を読んだ。 |
| 再構築計画の方針要約 | `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-deployable-reconstruction-readiness.md` の Source Policy Summary に記録した。 |
| 関連候補の関係要約 | `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-deployable-reconstruction-readiness.md` の Related Candidates に記録した。 |

参照:

- `docs/notes/2026-06-05-future-development-candidates.md#d-021-deployable-reconstruction-readiness-の再点検`
- `docs/notes/2026-06-05-future-development-candidates.md#8-推奨着手順`
- `docs/plan/reconstruction-plan-2026-05-21.md`

## 2. Readiness Report 作成

出力先:

- `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-deployable-reconstruction-readiness.md`

親ディレクトリ `.reviewcompass/specs/_cross_feature/reviews/` は 2026-06-09 に存在確認済みである。

チェック項目:

- [x] report の front matter を決める。
- [x] D-021 の目的、範囲、非範囲を書く。
- [x] readiness 判定値を定義する。
- [x] deployment readiness checklist を report に写す。
- [x] data acquisition readiness checklist を report に写す。
- [x] escalation note 欄を用意する。

readiness report front matter template excerpt:

```yaml
---
feature: all_features
phase: completed_follow_up
stage: deployable_reconstruction_readiness
date: 2026-06-09
status: <draft|ready|ready_with_gaps|blocked|needs_smoke_implementation>
candidate_id: D-021
record_type: readiness-report
source_checklist: docs/notes/2026-06-09-d021-deployable-reconstruction-readiness-checklist.md
---
```

判定値案:

- `ready`
- `ready_with_gaps`
- `blocked_by_D022`
- `blocked_by_D023`
- `blocked_by_D024`
- `needs_smoke_implementation`

判定値の使い分け:

| Verdict | Condition |
| --- | --- |
| `ready` | 外部配置、対象アプリ側 / ツール側分離、相対リンク、CLI app root 指定、最小データ取得の全観点が証跡付きで確認済み。D-022 / D-023 / D-024 の繰り上げ条件なし。 |
| `ready_with_gaps` | 外部配置を妨げない軽微な gap があるが、D-004 以降へ進む前提は満たす。gap は D-021 report の follow-up に記録済み。 |
| `blocked_by_D022` | 旧素材リポジトリ由来の記述、旧名、旧パス、自己適用前提が外部配置や責務分離を妨げる。 |
| `blocked_by_D023` | 絶対パス、repo root 暗黙依存、相対リンク違反、配置非依存性違反が外部配置を妨げる。 |
| `blocked_by_D024` | 再構築計画由来 backlog、スコープ外宿題、候補間重複が D-021 / D-020 の前提を妨げる。 |
| `needs_smoke_implementation` | 文書監査だけでは外部配置可否を判定できず、最小 fixture または外部サンプル repo による deployment smoke 実装が必要。 |

各判定値は report の最終結論では相互排他的に 1 つだけ採用する。複数の blocker がある場合は、外部配置を最初に妨げる blocker を最終 verdict にし、残りは `secondary_blockers` として記録する。

同時に複数 blocker が成立する場合の tie-break order:

1. `blocked_by_D023`: 配置非依存性違反は deployment smoke 自体を壊すため最優先で扱う。
2. `blocked_by_D022`: 旧素材混入・自己適用前提は責務分離を壊すため次に扱う。
3. `blocked_by_D024`: backlog 整理不足は D-020 / 後続候補へ引き継げる場合があるため三番目に扱う。
4. `needs_smoke_implementation`: 文書監査で判定不能であり、D-022 / D-023 / D-024 のいずれの blocker としてもまだ分類できない場合に採用する。

smoke 実行中に path 依存などの具体 blocker が見つかった場合、最終 verdict は `needs_smoke_implementation` ではなく該当する `blocked_by_*` に切り替える。`needs_smoke_implementation` は「追加 smoke が必要」という未判定状態であり、smoke が blocker を具体化した後の最終 blocker より優先しない。

## 3. Deployment Readiness Checklist

外部リポジトリへ配置できるかを確認する。

実行順序は Section 3 を先に完了し、その結果を踏まえて Section 4 へ進む。外部配置を妨げる blocker が Section 3 で見つかった場合は、Section 4 の詳細確認へ進まず、Section 6 の escalation rule を先に判定する。

| Item | Status | Evidence standard |
| --- | --- | --- |
| 対象アプリ側に置くものとツール側に置くものを分類する | [x] | report に app-side / tool-side / shared / unclear の分類表を置く。 |
| `.reviewcompass/specs/` が対象アプリ側状態として扱われているか確認する | [x] | 該当する docs / tools / templates の参照と、外部 repo fixture での配置案を記録する。 |
| 設定ファイルの配置先と責務を確認する | [x] | `config/`、`.reviewcompass/config.yaml`、API 設定、対象 app 設定の責務境界を表にする。 |
| テンプレートの配置先と責務を確認する | [x] | `templates/` と対象 app 側に複製される記入用テンプレートを分けて記録する。 |
| review-run 出力の配置先と責務を確認する | [x] | `.reviewcompass/specs/<feature>/reviews/` と `docs/notes/review-runs/` の使い分け、feature-local pointer 要否を記録する。 |
| `reviewcompass` 相当の CLI 経路が対象 app root を明示できるか確認する | [x] | CLI / tool コマンドの app root 引数、cwd 前提、出力先の検査結果を記録する。 |
| ReviewCompass 自身の repo root に暗黙依存した処理を棚卸しする | [x] | `rg` コマンド、対象範囲、検出件数、代表例、許容 / 要修正分類を記録する。 |
| `/Users/...` などの絶対パス参照を棚卸しする | [x] | `rg` コマンド、検出件数、正当なローカル作業記録か外部配置 blocker かの分類を記録する。 |
| 旧素材リポジトリ名、旧パス、自己適用前提語彙を棚卸しする | [x] | 旧名・旧パス・自己適用前提語彙ごとの検出件数と D-022 繰り上げ要否を記録する。 |
| 相対リンク・配置非依存性のリスクを記録する | [x] | D-023 繰り上げ要否と、相対リンク検査の不足を report に記録する。 |

## 4. Data Acquisition Readiness Checklist

複数ケースから同じ形式で研究用データを取れるかを確認する。

Section 4 は、Section 3 で外部配置の blocker がない、または blocker を D-021 report で扱う方針が決まった後に実施する。

最低限の共通データ項目:

| Data area | Minimum fields for D-021 report |
| --- | --- |
| review-run | run id, target path, phase, criteria id, variant, role assignments, raw paths, parsed paths, summary path |
| triage | finding id, source model, severity, final label, decision status, decision actor, decision reason |
| decision / approval | approved by, approval source, approved finding ids, proxy decision refs if any, approval record path |
| fix / tests | changed files, linked finding ids, test commands, test result, commit ref if available |
| cost | available / missing, provider, model, request count or cost source if recorded |
| elapsed time | available / missing, started at, completed at, duration source if recorded |
| model assignment | variant name, role, provider, model, path, assignment rationale if recorded |

| Item | Status | Evidence standard |
| --- | --- | --- |
| review-run 記録を同じ形式で取得できるか確認する | [x] | 既存 review-run directory の代表例を 2 件以上読み、必須項目の有無を表にする。 |
| triage 記録を同じ形式で取得できるか確認する | [x] | `triage.yaml` の代表例を読み、D-004 へ渡す schema gap を記録する。 |
| decision / approval 記録を同じ形式で取得できるか確認する | [x] | approval record と proxy decision record の代表例を読み、欠落項目を記録する。 |
| fix / changed files / tests の証跡を同じ形式で取得できるか確認する | [x] | commit / test evidence の現状を確認し、D-005 / D-025 へ渡す gap を記録する。 |
| cost 記録の現状と欠落を確認する | [x] | cost が記録済みか、未記録なら D-019 gap として記録する。 |
| elapsed time 記録の現状と欠落を確認する | [x] | elapsed time が記録済みか、未記録なら D-019 gap として記録する。 |
| model assignment 記録の現状と欠落を確認する | [x] | `review_summary.md` / `rounds.yaml` から model assignment を復元できるか記録する。 |
| D-004 / D-005 / D-008 / D-019 / D-020 へ渡す未整備項目を整理する | [x] | downstream handoff table を report に置く。 |

## 5. Deployment Smoke 最小 Fixture 案

外部 repo をすぐ使わず、まず最小 fixture で配置可能性を確認する案を作る。

- [x] fixture の置き場所を決める。
- [x] fixture に必要な最小 app code を決める。
- [x] fixture に必要な `.reviewcompass/config.yaml` を決める。
- [x] fixture に必要な `.reviewcompass/specs/<feature>/` 最小構成を決める。
- [x] deployment smoke で実行するコマンド候補を列挙する。
- [x] smoke が生成または検査すべき出力を列挙する。
- [x] fixture を実装するか、D-021 report では未実装 gap として残すか判断する。

fixture 実装判断ルール:

- 文書監査だけで `ready` / `ready_with_gaps` / `blocked_by_*` のいずれかを証跡付きで判定できる場合、fixture 実装は D-021 report の follow-up に残してよい。
- 文書監査だけでは外部配置可否を判定できない場合、最終 verdict は `needs_smoke_implementation` とし、fixture 実装を D-004 より前の次タスク候補にする。
- fixture 実装に入る場合は、このチェックリスト上で Section 1 と Section 2 の report 骨子を先に完了させる。
- fixture 実装を follow-up に残す場合は、readiness report の `Follow-Up / Handoff` 節に、理由、必要な fixture、想定コマンド、D-020 への引き継ぎ可否を記録する。

deployment smoke の成功条件:

- fixture repo root を明示してコマンドを実行できる。
- fixture 側 `.reviewcompass/specs/<feature>/` を discovery できる。
- tool 側設定・テンプレートと fixture 側状態が混ざらない。
- review-run / triage / approval / test evidence の少なくとも最小サンプルを同じ出力規約で保存できる、または未実装 gap として report に記録できる。
- 実行後に ReviewCompass 本体 repo の workflow_state を変更しない。

deployment smoke の失敗条件:

- ReviewCompass 本体 repo root に暗黙依存し、fixture root を指定できない。
- 絶対パスや固定 repo 名が必要になる。
- fixture 側に置くべき状態と tool 側に置くべきコード / template が混在する。
- データ取得項目の欠落が D-004 / D-005 / D-008 / D-019 / D-020 の前提を妨げるが、handoff gap として記録されない。

## 6. Escalation Rules

D-021 の結果により、推奨着手順を変更する条件を記録する。

- [x] 旧素材混入が外部配置を妨げる場合、D-022 を D-004 より前へ繰り上げる。
- [x] 絶対パス、repo root 暗黙依存、相対リンク違反が外部配置を妨げる場合、D-023 を D-004 より前へ繰り上げる。
- [x] スコープ外宿題や再構築計画由来 backlog が D-021 / D-020 の前提を妨げる場合、D-024 を D-004 より前へ繰り上げる。
- [x] D-020 と重複する adapter checklist / same-schema metrics は、D-021 report から D-020 replication plan へ引き継ぐ。

## 7. Task Management Rules

- 作業開始時に、このチェックリストの該当項目を確認する。
- 完了した項目は `[x]` に更新する。
- 判断だけで完了する項目は、根拠ファイルまたは確認コマンドを report 側へ記録する。
- 実装変更が必要になった場合は、D-021 report に gap として記録し、別タスク化してから着手する。
- `spec.json` の workflow_state 変更、commit、push は、利用者の明示承認なしに行わない。

## 8. Status Snapshot

- `next --json`: `completed`
- worktree: clean at checklist creation start
- current task: D-021 minimal app-root smoke implemented; readiness verdict ready_with_gaps
- next task: D-004 normalized finding schema
- last status refresh: 2026-06-09, after minimal app-root smoke

この section は時点依存の snapshot であり、D-021 の永続的な判断根拠ではない。実際の作業判断は、作業開始時の `next --json`、作業ツリー状態、readiness report の証跡表で更新する。post-write manifest は検証完了後に `.reviewcompass/post-write-verification/post-write-YYYY-MM-DD-NNN.yaml` として生成し、その具体 path は commit 前の最終報告と commit approval record で参照する。

更新ルール:

- この checklist を編集した場合、最後に `last status refresh` と `current task` を更新する。
- D-021 readiness report を作成し始めた後は、最新状態を report 側へ記録し、この section は初期 snapshot として扱う。
- commit 前の正本は、この section ではなく `tools/check-workflow-action.py next --json`、`git status --short`、post-write manifest とする。
