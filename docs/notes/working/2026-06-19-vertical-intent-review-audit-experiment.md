# 縦方向意図監査レビューの比較実験メモ

作成日：2026-06-19

## 目的

本メモは、後続の論文・報告で利用できるように、`workflow-management` tasks review における「縦方向の意図伝達監査」導入前後の差分を、実験方法・条件・結果として記録する。

検証した問いは次である。

> phase review に「上流成果物からの意図伝達」を必須検査として入れると、通常の task granularity review では見えにくい欠陥を検出できるか。

ここでいう縦方向の意図伝達とは、`requirements.md → design.md → tasks.md` の流れで、上流の目的・責務境界・受入条件・禁止事項が、対象成果物へ欠落・弱体化・逸脱・未根拠追加なく引き継がれているかを確認することである。

## 対象

- feature：`workflow-management`
- phase：`tasks`
- gate：`stages/tasks.yaml#triad-review`
- 対象タスク：T-016〜T-019
- 対象上流要件：Requirement 13〜16
- 主な対象ファイル：
  - `.reviewcompass/specs/workflow-management/requirements.md`
  - `.reviewcompass/specs/workflow-management/design.md`
  - `.reviewcompass/specs/workflow-management/tasks.md`
  - `.reviewcompass/specs/workflow-management/spec.json`
  - `stages/in-progress/reopen-procedure-2026-06-19.yaml`

## 実験条件

### 共通条件

2 回の review-run は、同一 feature、同一 phase、同一 gate、同一 3 役 variant で実施した。

- variant：`implementation_review_independent_3way_codex_operator`
- primary：`openai-api / gpt-5.4`
- adversarial：`anthropic-api / claude-opus-4-8`
- judgment：`gemini-api / gemini-3.1-pro-preview`
- parse failure：両 run とも 0
- 操縦 LLM：Codex
- 実行日：2026-06-19

### Baseline 条件

Baseline は、従来の tasks granularity review として実行した。主眼は、T-016〜T-019 が implementation drafting へ直接入れる粒度になっているか、実装対象ファイル・最初に書く失敗テスト・実装順序・完了条件などを持つかであった。

Baseline review-run：

- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-granularity-regeneration-review-run.baseline-before-vertical-intent`

Baseline の比較用 summary：

- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-granularity-regeneration-review-run.baseline-before-vertical-intent/raw-review-triage-summary.md`

### 介入条件

介入として、レビュー規律に「上流意図伝達の必須検査」を追加した。

追加箇所：

- `docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`
- `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml`

追加した規律の要点：

- `design review`：`requirements.md → design.md` を確認する。
- `tasks review`：`requirements.md → design.md → tasks.md` を確認する。
- `implementation review`：`requirements.md → design.md → tasks.md → implementation` を確認する。
- triad-review / review-wave / alignment では、上流の目的・責務境界・受入条件・禁止事項が、対象成果物へ欠落・弱体化・逸脱・未根拠追加なく引き継がれているかを review prompt に含める。

介入後、T-016 / T-017 / T-019 に「上流意図継承」節と追加 red tests / completion conditions を入れ、再レビューした。

再レビュー run：

- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run`

再レビューの比較用 summary：

- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run/raw-review-triage-summary.md`

## 実験手順

1. Baseline tasks review を実施し、3 役モデルの raw / parsed / summary / triage を保存した。
2. Baseline 結果を `.baseline-before-vertical-intent` 付きディレクトリに退避した。
3. `SESSION_WORKFLOW_GUIDE.md` と `WORKFLOW_DISCIPLINE_MAP.yaml` に縦方向意図監査規律を追加した。
4. `next --json` で、新規律が required disciplines / required inputs / effective prompt source refs に出ることを確認した。
5. 新規律に合わせて T-016 / T-017 / T-019 を再生成した。
6. Baseline と同じ 3 役 variant で、縦方向意図監査を明示した review-target を使って再レビューした。
7. 2 つの review-run を、同根クラスタ単位で比較した。

## 結果

### モデル別件数

Baseline：

| model | findings | severity |
| --- | ---: | --- |
| gpt-5.4 | 3 | WARN:3 |
| claude-opus-4-8 | 9 | WARN:1, INFO:8 |
| gemini-3.1-pro-preview | 0 | - |

縦方向意図監査後：

| model | findings | severity |
| --- | ---: | --- |
| gpt-5.4 | 9 | ERROR:4, WARN:3, INFO:2 |
| claude-opus-4-8 | 5 | WARN:2, INFO:3 |
| gemini-3.1-pro-preview | 0 | - |

件数だけでは改善・悪化は判断しない。重要なのは、所見の種類が「task 粒度不足」から「上流 design authority との整合」へ変わったことである。

### Baseline 所見

Baseline では、主に次の 4 クラスタが得られた。

| cluster | triage | 内容 |
| --- | --- | --- |
| C1 | should-fix | T-016 の operation contract / registry 所有境界が曖昧 |
| C2 | should-fix | T-017 の approval / side track / snapshot の保存先・mutation boundary が曖昧 |
| C3 | should-fix | T-019 の human-required predicate が未固定 |
| C4 | leave-as-is | tasks 粒度、追跡性、状態ファイル整合は概ね良好 |

Baseline のレビューは、tasks.md が実装可能粒度になっているかを見るには有効だった。一方で、tasks が design にない判断を追加していないか、または上流 design が未確定な領域を tasks が勝手に固定していないかは、明示的には露出しにくかった。

### 縦方向意図監査後の所見

縦方向意図監査後は、次の 5 クラスタが得られた。

| cluster | triage | 内容 |
| --- | --- | --- |
| C1 | must-fix | T-016 の registry / contract 分離が、design 未確定の二正本分離を tasks 側で追加している可能性 |
| C2 | should-fix | T-017 は改善したが、pop 後の return 条件、staged overlap、repair / stop 条件がまだ不足 |
| C3 | must-fix | proxy / human 境界が Requirement 14 / 16 / approval 規律間の上流整合問題として露出 |
| C4 | should-fix | T-018 は概ね健全だが、machine-task leakage の red test 拡張余地あり |
| C5 | leave-as-is | 新規律の wiring と基本的な tasks 粒度は確認済み |

## 観察された効果

### 1. 欠陥の種類が変わった

Baseline では、C1 / C2 / C3 は「tasks をもっと具体化すればよい」ように見えていた。

縦方向意図監査後は、C1 / C3 がより深い問題として再分類された。

- C1：registry / contract の二正本分離は、tasks 側で追加した設計判断かもしれない。
- C3：proxy / human boundary は、T-019 の文言不足だけでなく、Requirement 14 / Requirement 16 / approval discipline の間で上流設計が必要な問題かもしれない。

これは、縦方向監査が「詳細化不足」と「上流未確定の設計判断」を分離する効果を持つことを示す。

### 2. 改善した箇所と未解決箇所を分けられた

再生成後の T-017 は、read-only vs mutating operation、snapshot non-canonical、side track push / pop / current などを明示したため、Baseline C2 は広い曖昧さから狭い edge-case 問題へ縮小した。

一方で、T-016 と T-019 は追加の具体化によって、逆に「その具体化は上流 design に根拠があるか」という新しい検査対象になった。

### 3. 規律の機械配線も検証できた

`next --json` は、縦方向意図監査を required discipline / required input / effective prompt source refs として返すようになった。

確認された required input：

- `vertical_intent_transfer_check`

確認された参照：

- `docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`

これにより、規律が人間向け文書に留まらず、次回以降の review prompt 生成に載る経路を持つことが確認できた。

## 解釈

この単一ケースでは、縦方向意図監査は「所見数を減らす」ための介入ではなかった。むしろ、レビューの焦点を変え、より根の深い問題を露出させた。

Baseline は、タスク粒度と実装可能性を見るには十分だった。しかし、上流意図との整合、特に「tasks が design を勝手に補っていないか」を見るには弱かった。

縦方向意図監査は、次の区別を可能にした。

- tasks に情報が足りない問題
- tasks に情報はあるが、上流 design に根拠がない問題
- design 側で境界を確定すべき問題
- tasks の red test / completion condition だけで修正できる問題

論文上の仮説としては、次のように表現できる。

> Review prompt に upstream intent transfer を明示すると、成果物単体の詳細度評価ではなく、phase 間の設計権限・意図継承・未根拠追加を検出するレビューへ移行できる。

## 限界

- 単一 feature / 単一 phase / 単一日付のケースであり、統計的な一般化はできない。
- 介入後は tasks.md 自体も再生成しているため、review prompt の変更効果と task artifact の変更効果は完全には分離できない。
- 同じ 3 役 variant を使ったが、外部モデルの出力は非決定的である。
- Gemini は両 run とも no findings であり、比較上の主な差分は GPT と Claude の出力に依存している。
- severity はモデルごとの自己申告に依存しており、同一尺度として厳密比較できない。

## 後続で使う場合の参照単位

論文や報告で使う場合は、次の evidence set を 1 単位として扱う。

Baseline evidence：

- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-granularity-regeneration-review-run.baseline-before-vertical-intent/review-target.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-granularity-regeneration-review-run.baseline-before-vertical-intent/model-result-summary.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-granularity-regeneration-review-run.baseline-before-vertical-intent/triage.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-granularity-regeneration-review-run.baseline-before-vertical-intent/raw-review-triage-summary.md`

Intervention evidence：

- `docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`
- `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml`
- `.reviewcompass/specs/workflow-management/tasks.md`

Post-intervention evidence：

- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run/review-target.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run/model-result-summary.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run/triage.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run/raw-review-triage-summary.md`

## 結論

縦方向意図監査は、レビューの検出対象を「タスクが十分に細かいか」から「上流意図が正しく、かつ権限を越えずに伝達されているか」へ拡張した。

本ケースでは、baseline の should-fix だった論点の一部が、post-intervention では must-fix 相当の vertical integrity issue として再分類された。これは、縦方向監査が単なる文言追加ではなく、phase 間の設計責任境界を検出する実用的効果を持つことを示す evidence として扱える。
