---
date: 2026-06-20
record_type: working-memo
status: active
topic: APIレビュー用プロンプト品質レビュー side-track 方針
related:
  - docs/disciplines/discipline_llm_as_judge_prompting.md
  - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
  - docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml
  - .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run/
---

# APIレビュー用プロンプト品質レビュー side-track 方針

## 背景

`workflow-management` の reopen R-0 では、Requirement 13〜16 を基点に requirements / design / tasks / implementation へ上流意図を縦方向に再伝達する作業を進めている。

2026-06-20 の design triad-review では、API 経由の 3 役レビューを実施し、`gpt-5.4`、`claude-sonnet-4-6`、`gemini-3.1-pro-preview` の全 role が `findings: []` を返した。

しかし、その後の利用者確認で、レビュー結果そのものより前に、API レビュー用プロンプトの品質が課題として露出した。

## 何が問題だったか

今回作成した review-run では、`--criteria-file` と `--target` に同じ `review-target.md` を渡していた。

そのため、生成された API prompt は、criteria と target の両方で作成者が書いたレビュー用要約を含んでいた。一方、実際に審査すべき `design.md` 本体は target として提示されていなかった。

この構成では、モデルが `design.md` を独立に審査するのではなく、作成者の要約が自己整合しているかを審査する危険がある。

## 利用者判断

利用者は、APIレビュー用プロンプト作成には次の 2 系統の要件を総合する必要があると指摘した。

1. 一般的な API レビュー / LLM-as-Judge プロンプト要件
2. 今回の場面固有の上流接続レビュー要件

一般要件は `docs/disciplines/discipline_llm_as_judge_prompting.md` にある。

場面固有要件は `docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review` にあり、`docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml` の `triad-review` にも prompt source として接続されている。

この接続が今回の作業では弱く、プロンプト作成時の明示的な品質チェックが漏れた。

## 方針

今後、この種の API review-run を開始する前に、作成済みプロンプト自体をレビュー対象にする。

レビュー体制は次の 2 者レビュー体制とする。

| 役割 | 担当 | 目的 |
|---|---|---|
| main | Codex 本体 | APIレビュー用プロンプト素案を作成する |
| adversarial | `claude-sonnet-4-6` | プロンプト素案の欠落、誘導、範囲ミス、材料不足、上流接続不足をレビューする |
| judgment | `gemini-3.1-pro-preview` | adversarial の指摘を踏まえ、そのプロンプトを実レビューに使ってよいか判定する |

ここでいう「2者レビュー体制」は、作成者である main を除き、adversarial と judgment の 2 者でプロンプト品質を確認する運用を指す。

`claude-opus-4-8` は、利用者判断により当面不採用とする。

## プロンプト品質レビューで見る観点

### 一般的な API レビュー要件

`discipline_llm_as_judge_prompting.md` に従い、少なくとも次を確認する。

1. main が問題を直接検討し、判断材料を揃えているか
2. 判断に必要な情報が prompt に含まれているか
3. 問いが独立分析を促し、特定の結論へ誘導していないか
4. 対象範囲が広すぎず狭すぎないか
5. 出力形式が後続処理可能な形で固定されているか
6. API に送る前の機微情報チェックが行われているか

### 今回の場面固有要件

`SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review` に従い、少なくとも次を確認する。

1. review target / source materials / out of scope が明示されているか
2. 審査対象は現在 phase の成果物に限定されているか
3. source materials は背景・意図伝達確認の参照資料として扱われているか
4. 上流資料がパス名だけで列挙されていないか
5. 上流の目的、責務境界、受入条件、禁止事項、未確定事項、対象 phase へ引き継ぐべき判断が、モデルが読める形で含まれているか
6. 対象成果物本文または該当抜粋が、要約だけでなく審査可能な材料として提示されているか
7. 下流 phase の correctness を現在 phase の review で判定させていないか

## side-track で実施する作業

1. 現在の不十分な review-run を、design triad-review 完了根拠として使わないことを明示する。
2. APIレビュー用プロンプト品質レビューのための side-track を開始する。
3. main が修正版 design review prompt 素案を作る。
4. adversarial に prompt 素案をレビューさせる。
5. 必要に応じて main が prompt 素案を修正する。
6. judgment に「この prompt を実レビューに使ってよいか」を判定させる。
7. judgment が使用可と判断した prompt で、改めて design triad-review API run を実施する。
8. その結果を通常の raw / parsed / triage / user-visible gate に載せる。

## 完了条件

- prompt 品質レビューの raw response、判定、反映結果が review-run または side-track 記録に保存されている。
- 修正版 API review prompt が、一般要件と上流接続要件の両方を満たすことを確認済みである。
- 修正版 prompt の target manifest が、少なくとも実際の審査対象である `design.md` を含んでいる。
- 旧 no-findings run を design triad-review 完了根拠として扱わないことが記録されている。

## 停止点

このメモは side-track 開始前の方針記録である。

side-track の開始、API 呼び出し、`spec.json` 更新、reopen gate 前進、commit / push は、このメモだけでは許可されない。利用者の明示指示に従って別途実施する。
