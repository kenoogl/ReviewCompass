prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.1-pro-preview

# Task
Review the target document for the requested phase and criteria.

# Phase
post_write_verification

# Criteria
# Post-write Review Target

criteria_id: plan_to_todo_boundaries_post_write
phase: post_write_verification
generated_at: 2026-06-23T09:01:27.630680+00:00

## Change Summary

Plan-to-TODO bridge prompt now defines artifact boundaries and TODO conversion rules for PTC-1/PTC-2.

## Review Question

Verify that the added artifact boundaries and TODO conversion rules accurately reflect the source TODO, do not overreach beyond the agreed workflow intent, and remain internally consistent with the existing plan-to-TODO bridge prompt.

## Target Files

- .reviewcompass/guidance/effective-prompts/user-initiated-plan-to-todo-bridge.prompt.md sha256=fcba123ccdb6d099a2d4e413504becdd4574760bb8b26ae766f18db9765d400e

## Source Materials

### .reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md

content_mode: full_text
content_sha256: 03a9b994c6b5fb4b99ebbbf169e48d76568c5b6190716bbe9e5e181844c9450d

```text
# API Review Prompt Quality

最終更新：2026-06-20

本文書は、API 経由の review-run を開始する前に、レビュー用プロンプト自体を品質確認するための運用手順である。

この手順は、特定 feature や特定 phase に閉じない。各 review-run は、この共通手順に phase / gate / feature 固有の上流接続要件を差し込んで使う。

利用者が任意の場面で API review を依頼する場合は、利用者が伝えたレビュー要件を `User Review Requirements` として保持し、criteria 作成・prompt quality review・実 review-run の全段で照合する。

## 1. 目的

API review-run の品質は、モデルや provider だけでなく、プロンプトの作り方に強く依存する。

レビュー用プロンプトの監査は、高リスク時だけの追加確認ではなく、API review-run の標準ゲートである。プロンプトが target / source / scope / output contract を誤ると、その後の raw response、parsed YAML、triage、proxy decision、実装修正がすべて誤った入力に基づく。したがって、prompt audit にかかるコストはレビュー外の余分なコストではなく、レビュー品質を成立させるための本体コストとして扱う。

特に、次の失敗を防ぐ。

- `--target` が実際の審査対象本文ではなく、作成者の要約になっている
- `--criteria-file` と `--target` が同一の author-written summary になっている
- source materials が path-only で、モデルが本文を読めない
- review target / source materials / out of scope が分離されていない
- 上流意図伝達レビューで、上流の目的・責務境界・受入条件・禁止事項が prompt に含まれていない
- 利用者が指定したレビュー目的、重視点、範囲、禁止事項が main によって狭められる、広げられる、または別の問いに置き換えられる
- output contract が曖昧で parser / triage に載らない
- プロンプトが結論を誘導している

## 2. 役割

APIレビュー用プロンプト品質確認は、次の 2 者レビュー体制で行う。

| 役割 | 担当 | 目的 |
|---|---|---|
| main | 操縦中の LLM | API review criteria 素案を作る |
| adversarial | 別モデル | 素案の欠落、誘導、対象違い、材料不足、範囲ミスを探す |
| judgment | 別モデル | adversarial 所見の反映後、その prompt を実 review-run に使ってよいか判定する |

ここでいう 2 者レビュー体制は、作成者である main を除き、adversarial と judgment の 2 者で品質確認する運用を指す。

## 3. 入力分離

API review-run では、criteria と target を分離する。

- `User Review Requirements`: 利用者が指定したレビュー目的、判断対象、重視点、範囲、禁止事項、必要出力
- `--criteria-file`: レビュー目的、背景、上流材料、必須チェック、範囲外、finding policy を含む
- `--target`: 実際に審査する本文

`User Review Requirements` は criteria の上位入力であり、criteria 作成時に失われてはならない。main は、利用者要件を criteria に構造化して写し、どの要件がどの review task / required check / out of scope / finding policy に対応するかを確認できる形にする。

禁止:

- criteria と target に同じ review wrapper / author-written summary を渡す
- target manifest が実審査対象を含まない状態で gate 完了根拠にする
- target 本文を入れず、target の要約だけで review-run を実行する
- 利用者が求めたレビュー範囲を、合意なく狭める、広げる、または別目的の review に置き換える

## 4. User Review Requirements

利用者が任意の場面で review を依頼する場合、main は prompt 作成前に次を整理する。

1. review purpose: 欠陥検出、採否判断、上流接続確認、回帰確認、比較評価など
2. review object: artifact、prompt、設計案、修正案、実装差分など
3. review focus: API設計、互換性、セキュリティ、運用境界、上流要件、実装可能性など
4. scope boundaries: 含める範囲、含めない範囲、まだ判断しない下流工程
5. source materials: 根拠にする要件、設計、過去判断、制約、禁止事項
6. output requirements: findings、severity、採否、懸念点、修正案、比較軸など
7. prohibited actions: commit、push、phase 完了、人間承認代行、未合意の仕様変更など

利用者要件が曖昧な場合でも、main が勝手に確定しない。作業可能な仮定として扱う場合は、criteria に仮定を明記し、prompt quality review で妥当性を確認させる。

## 5. API 送信可能材料の基準

API review-run / proxy_model 判断では、判断に必要な ReviewCompass リポジトリ内の仕様、設計、タスク、レビュー所見、構造化要約、証跡パスを prompt に含めてよい。

これは、次の条件を満たす場合に限る。

1. 利用者が当該 API review-run / proxy_model 判断の実行を明示承認している。
2. API key、token、password、nonce などの秘密値を含めない。
3. メールアドレス、電話番号など個人識別情報を含めない。
4. 第三者との契約上、外部送信できない非公開情報を含めない。
5. 判断に不要な全文ログや周辺ファイルを含めず、判断項目に必要な抜粋または構造化要約に絞る。

単にリポジトリ内の未公開仕様・設計・レビュー要約であることだけを理由に、API 送信を禁止しない。ReviewCompass の API review / proxy_model 運用では、それらは通常のレビュー材料である。

ただし、利用者が外部送信を避ける方針を示した場合、または上記 2〜4 に該当する情報が含まれる場合は、伏字化、抽象化、または外部 API を使わない判断へ切り替える。

## 6. Main が作る criteria の必須要素

criteria file は、少なくとも次を持つ。

1. review task
2. why this review exists
3. user review requirements
4. required disciplines
5. review target
6. source materials
7. required checks
8. out of scope
9. finding policy

source materials は path-only にしない。必要な本文抜粋または構造化要約を、モデルが読める形で criteria に含める。

front matter に path を置く場合は、provenance なのか model-readable material なのかを明示する。

criteria は、利用者要件を単に引用するだけでなく、review task / required checks / out of scope / finding policy へ反映する。

## 6.1 Main Preanalysis

main は criteria 素案を書く前に、対象 review requirement と source materials を直接検討し、判断に必要な材料、判断項目、分割要否、未読資料、機微情報リスクを整理する。

main preanalysis は、prompt 作成のための材料揃えと判断点発見であり、reviewer に対する正解ではない。preanalysis を後続の監査や prompt に含める場合は、仮説・source discovery aid として明示し、reviewer に source materials から独立再構成させる。

main preanalysis には少なくとも次を含める。

- 読んだ source materials と使用目的
- 判断項目と、それぞれの target / source / out of scope
- 複数 prompt に分割すべき独立判断の有無
- prompt に含めるべき model-readable source material
- 送信してはいけない、または最小化すべき機微情報
- 未解決・未読・推測に留まる事項

preanalysis 内の所見は、`open`、`resolved`、`superseded`、`used_for_context` など現在性を区別できる形で扱う。解決済み所見を open な欠陥として prompt bundle に残すと、reviewer を誤誘導するためである。

## 7. Phase 別の上流接続

`.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review` が適用される review では、phase ごとに次を確認する。

| phase | target | source materials |
|---|---|---|
| requirements | `requirements.md` | upstream decision materials, reopen classification, planning notes, user decisions |
| design | `design.md` | `requirements.md` |
| tasks | `tasks.md` | `requirements.md`, `design.md` |
| implementation | implementation artifacts | `requirements.md`, `design.md`, `tasks.md` |

source materials は背景・意図伝達確認のために使う。現在 phase の correctness だけを target として判定し、下流 phase の correctness を同時に判定しない。

利用者が指定した review focus が phase 標準の観点と異なる場合は、両者の関係を criteria に明記する。phase 標準の必須検査を外す必要がある場合は、利用者合意なしに外してはならない。

## 8. Prompt Quality Review

main が criteria 素案を作ったら、実 review-run の前に preanalysis sufficiency audit と prompt quality review を行う。

標準手順は次の順序とする。

1. main preanalysis
2. preanalysis sufficiency audit
3. API review criteria draft
4. prompt quality review
5. 実 review-run
6. raw / parsed / model summary / triage
7. 必要に応じて proxy_model decision

通常の prompt quality review の前に、`templates/review/main_preanalysis_sufficiency_audit_criteria_template.md` を使って preanalysis sufficiency audit を行う。この監査では、reviewer に source materials から judgment item を独立再構成させたうえで、main preanalysis を仮説として比較させる。main preanalysis を正解として渡してはならない。

preanalysis sufficiency audit では、target bundle に次を含める。

- 利用者または workflow の review requirement
- 判断に必要な source materials の本文または構造化抜粋
- main session LLM の preanalysis
- proposed API review criteria または prompt

監査結果の `required_prompt_changes` を反映してから、通常の `templates/review/api_review_prompt_quality_criteria_template.md` による prompt quality review へ進む。

preanalysis sufficiency audit は、次の欠陥を検出するための標準ゲートである。

- source selection の漏れ
- source summary と原文対応の不足
- main preanalysis の stale / resolved 所見による anchoring
- 複数の独立判断を 1 prompt に押し込む粒度誤り
- 誤検出防止文言が、重要な欠陥検出まで抑制する framing bias
- output contract と runner / parser の不一致

review question は 1 prompt につき原則 1 つにする。複数の独立した採否判断、クラスタ判断、設計論点判断を 1 つの prompt に押し込まない。

複数判断がある場合は、判断項目ごとに prompt を分ける。各 prompt は、その判断に必要な source findings、上流材料、対象本文要約、out of scope、output contract だけを持つ。共通背景を入れる場合も、個別判断の焦点を曖昧にしない量に抑える。

adversarial には、`templates/review/api_review_prompt_quality_criteria_template.md` を criteria として渡し、criteria 素案を target としてレビューさせる。

利用者要件がある場合、prompt quality review では次も確認する。

- 利用者要件が criteria に保持されている
- 利用者要件が review task / required checks / out of scope / finding policy に反映されている
- main が利用者要件を合意なく狭めたり広げたりしていない
- 利用者が禁止した操作や判断代行が prompt に混入していない
- 複数の独立判断を 1 prompt に押し込んでおらず、判断項目ごとに注意が分散しない粒度になっている

adversarial の所見を main が反映した後、judgment に同じ quality criteria と adversarial 所見を渡し、使用可否を判定させる。

judgment が `findings: []` を返した場合だけ、実 review-run へ進める。

judgment が finding を返した場合は、prompt を再修正し、必要に応じて再度 judgment へ回す。

## 9. 実 Review-Run

prompt quality review を通過した後、実 review-run を実行する。

複数 prompt に分けた場合は、各 prompt の prompt quality review 通過証跡と実 review-run / proxy decision 結果を判断項目ごとに保存する。一括 summary は後段で作ってよいが、個別判断の raw / parsed / decision 証跡を上書きしない。

実行時には次を確認する。

- `target-manifest.yaml` に実審査対象が入っている
- `rounds.yaml` の criteria は使用可判定済み criteria である
- raw / parsed / model-result-summary / triage が生成されている
- 利用者提示ゲート前に、raw 結果概要、モデル別 summary、同根クラスタ、三段階トリアージ案をまとめる
- 実 review-run の結果を、利用者要件に含まれていない操作承認や phase 完了根拠へ拡張しない

## 10. 成果物配置

推奨配置:

```text
.reviewcompass/specs/<feature>/reviews/<date>-<feature>-<phase>-<topic>-prompt-quality-run/
  api-review-criteria.md
  prompt-quality-review-criteria.md
  variant-role-assignment.yaml
  raw/
  parsed/
  prompts/
  rounds.yaml
  model-result-summary.yaml
  prompt-quality-summary.md
```

実 review-run は別ディレクトリに分ける。

```text
.reviewcompass/specs/<feature>/reviews/<date>-<feature>-<phase>-<topic>-review-run/
```

prompt-quality-run は、実 review-run の gate 完了根拠ではない。実 review-run の criteria を使ってよいことを示す補助証跡である。

## 11. 今回の事例から得た規則

2026-06-20 の `workflow-management` design triad-review では、旧 run が `review-target.md` を criteria と target の両方に使い、`findings: []` になった。

その後、prompt quality review を挟み、`design.md` を実 target として再実行した v2 run では 15 件の所見が出た。

同日の `workflow-management` implementation Req14 approval gate prompt audit では、preanalysis sufficiency audit により、source summary の原文対応不足と、誤検出防止文言が approval gate bypass 検出を鈍らせる framing bias が検出された。これは、prompt audit が形式確認ではなく、実 review-run の欠陥検出力そのものを左右することを示す。

この差分から、次を標準規則とする。

- 実審査対象本文を target にしない review-run は、gate 完了根拠として弱い
- author-written summary は criteria または source-material summary として使えるが、target 本文の代替にしない
- 上流接続 review では、source materials と target を明示的に分離する
- source summary には原文または構造化抜粋に加え、必要に応じて source cross-reference を持たせる
- main preanalysis は有用だが、仮説として扱い、reviewer に独立再構成させる
- 1 prompt に複数の独立判断を押し込まない
- prompt 自体の adversarial / judgment レビューを実行前に挟む

## 12. 停止点

prompt quality review は、実 review-run の開始許可であり、次の操作を自動許可しない。

- `spec.json` 更新
- phase / gate 完了
- proxy_model 判断
- design / requirements / tasks / implementation 本文修正
- commit
- push

これらはそれぞれの workflow gate と利用者承認に従う。
```

### .reviewcompass/backlog/todos/todo-2026-06-23-plan-to-todo-checklist-evidence.yaml

content_mode: full_text
content_sha256: 6ef2ea4e573b022ec62287178c096aaca3171e4e628ef35199a9a2c3b34346ad

```text
schema_version: reviewcompass-backlog-item-v1
id: todo-2026-06-23-plan-to-todo-checklist-evidence
kind: todo
title: Preserve plan to TODO checklist execution evidence
status: candidate
source_unit_id: main-completed
created_at: '2026-06-23T08:25:46.734782+00:00'
index_path: .reviewcompass/backlog/index.yaml
provenance:
  created_by: llm
  source_ref: conversation:user:証跡としては、todoリストやチェックリストがあった方がよいと思う
  reason: plan から直接作業を進めると、実行単位化した TODO と checklist の証跡が残らず、後から進め方と完了根拠を追跡しにくくなるため
decisions: []
summary: >
  plan の implementation_plan を読んで直接作業へ入る運用を避け、
  実行前に backlog TODO と runtime checklist へ落としてから進める。
  作業完了後は completed checklist / evidence と TODO の execution_history に
  実行証跡を残し、plan、TODO、checklist、完了証跡のつながりを追跡可能にする。
problem_statement:
- plan は方針、分解案、受け入れ条件を持つが、実行単位そのものではない。
- plan から直接作業すると、どの部分を TODO として実行対象化したかが残りにくい。
- checklist なしで進めると、作業中の進捗と完了根拠が会話履歴に寄り、後続セッションから追跡しにくい。
- 完了後に checklist を後付けすると、実行中証跡ではなく回顧メモになり、証跡の意味が曖昧になる。
required_flow:
- plan の implementation_plan / acceptance_criteria / remaining work を読む。
- 実行対象にする範囲を backlog TODO として切り出す。
- "`work-backlog start-checklist --id <todo-id>` で runtime checklist を生成する。"
- "`work-backlog audit-checklist-coverage --id <todo-id> --checklist-id <checklist-id>` で coverage を確認する。"
- checklist item を進めながら作業し、完了時に checklist を close して evidence へ移す。
- TODO 側の execution_history に checklist_id、evidence_path、completion_summary を残す。
todos:
  design_contract:
  - id: PTC-1
    title: plan、TODO、runtime checklist、evidence の責務境界を明文化する
    status: pending
    detail: plan は方針、TODO は実行単位、runtime checklist は実行中進捗、evidence は完了証跡として扱う。
  - id: PTC-2
    title: plan から作業開始する前の TODO 化ルールを定義する
    status: pending
    detail: implementation_plan の phase/task、acceptance_criteria、残作業をどの単位で TODO に切るかを定義する。
  cli:
  - id: PTC-3
    title: plan 由来 TODO の作成または確認を促す導線を追加する
    status: pending
    detail: plan から次作業を開始する場面で、既存 TODO の有無を確認し、なければ TODO 作成へ進ませる。
  - id: PTC-4
    title: TODO から checklist 生成と coverage audit までを標準手順に組み込む
    status: pending
    detail: start-checklist と audit-checklist-coverage を実行前証跡として残す。
  audit:
  - id: PTC-5
    title: plan 直接実行の逸脱を検出または記録する
    status: pending
    detail: plan 由来の作業完了に対応する TODO/checklist/evidence がない場合、follow-up または deviation として残す。
red_tests:
- id: PTC-RT-1
  title: plan 由来作業に TODO がない場合に検出する
  expected: plan の作業が完了扱いになる前に、対応 TODO がない状態を DEVIATION または follow-up として検出できる
- id: PTC-RT-2
  title: TODO から checklist coverage を確認できる
  expected: plan 由来 TODO に対して runtime checklist が生成され、coverage audit が OK/DEVIATION を返す
- id: PTC-RT-3
  title: 完了後に TODO execution_history へ証跡が戻る
  expected: checklist close 後、TODO に evidence_path と completion_summary が記録される
non_goals:
- 完了済み作業に対して、実行時から存在したかのような checklist を後付けすること
- すべての plan を即時に TODO 化すること
- plan の内容を LLM 要約だけで実行 checklist に変換すること
notes:
- 既存の `work-backlog start-checklist` は TODO から checklist への導線であり、plan から TODO への導線は別課題として扱う。
- 既に plan から直接進めた作業は、必要に応じて retrospective execution trace または deviation/follow-up note として記録する。
```


## Target File Contents

### .reviewcompass/guidance/effective-prompts/user-initiated-plan-to-todo-bridge.prompt.md

content_mode: full_text
content_sha256: fcba123ccdb6d099a2d4e413504becdd4574760bb8b26ae766f18db9765d400e

```text
# Effective Prompt: User-Initiated Plan To TODO Bridge

## Decision Point
- group: operation_prompt
- id: user_initiated_plan_to_todo_bridge

## Purpose
ユーザが backlog plan または plan 内の一部作業を実行しようとしたときに読む。plan を実行単位へ変換する直前で、plan から直接実作業に入らず、backlog TODO、runtime checklist、coverage / quality audit、必要時の review materials へ接続する。

## Trigger Boundary
- ユーザが「次へ」「進める」「この plan を進める」など、plan 由来の実作業開始を指示した。
- `next --json` が completed で、次作業を backlog plan から選ぶ状態になった。
- plan の `implementation_plan`、`acceptance_criteria`、remaining work を読んで実装、整理、移行、監査へ入ろうとしている。
- plan の一部 phase / task だけを実行しようとしている。

plan を読むだけ、説明するだけ、優先順位を相談するだけの場合は、この bridge を開始しない。

## Required Inputs
- 対象 plan id または plan path。
- `.reviewcompass/backlog/index.yaml`
- 対象 plan 本文。
- 対応する既存 backlog TODO の有無。
- 現在の work unit stack。

## Artifact Boundaries
- plan は方針、分解案、受け入れ条件、残作業を保持する。実行対象そのものではなく、どこを TODO 化するかを判断する上流材料である。
- TODO は実行対象化した最小の追跡単位である。1 つの TODO は、同じ目的、同じ完了条件、同じ検証単位で閉じる範囲だけを扱う。
- runtime checklist は実行中の進捗証跡である。TODO の task / implementation_plan / todos / red_tests から生成し、作業中の active / pending / done を保持する。
- evidence checklist は完了後の固定証跡である。runtime checklist を後から作業中だったかのように補う場所ではなく、完了時点の checklist と検証結果を残す。
- TODO の execution_history は、完了した checklist_id、evidence_path、completion_summary を TODO 正本へ戻す索引である。

## TODO Conversion Rules
- 同時に完了判定できる範囲だけを 1 TODO にする。複数の独立した成果物、検証、判断待ちを含む場合は TODO を分ける。
- plan の一部だけを実行する場合、TODO には source_plan_id または source_plan_path と、対象 phase / task / acceptance_criteria / red_tests の対応を記録する。
- acceptance_criteria は TODO の完了条件へ落とす。受け入れ条件に対応しない checklist item だけで実作業へ進まない。
- red_tests は実装前の確認項目として TODO または checklist に残す。赤テストが不要な文書作業では lightweight self-check の理由を明示する。
- 既存 TODO がある場合は、対象範囲、完了条件、検証単位が plan の実行範囲を覆るかを確認してから再利用する。
- 対応が曖昧な場合は TODO を新規作成または分割し、曖昧なまま既存 TODO に押し込まない。

## Mechanical Steps
1. 対象 plan を読み、実行しようとしている範囲を特定する。
2. `.reviewcompass/backlog/index.yaml` と backlog TODO を確認し、同じ範囲を扱う既存 TODO があるかを見る。
3. 対応 TODO がなければ `work-backlog add-todo` で plan 由来 TODO を作成する。
4. 作成または選択した TODO を `work-backlog show --id <todo-id> --json` で読む。
5. `work-backlog start-checklist --id <todo-id>` で runtime checklist を生成する。
6. `work-backlog audit-checklist-coverage --id <todo-id> --checklist-id <checklist-id>` を実行する。
7. `task-quality-check audit --backlog-id <todo-id> --checklist-id <checklist-id>` を実行する。
8. audit が DEVIATION の場合は実作業へ進まず、TODO または checklist の修正に戻る。
9. audit が WARN または高リスクの場合、`task-quality-check prepare-review-materials --backlog-id <todo-id> --checklist-id <checklist-id> --output-dir <dir>` で review materials を作る。
10. review materials を作った場合、外部 API review に進むか、ローカル判断に留めるかを利用者に確認する。
11. coverage / quality が OK で、WARN または高リスクが解消または明示判断済みの場合だけ、checklist item を active にして実作業へ進む。

## High-Risk Signals
- plan から複数の独立作業を切り出す必要がある。
- TODO の粒度や順序に迷いがある。
- `task-quality-check audit` が WARN を返した。
- red test の位置づけ、レビュー要否、または実行順序に判断が必要である。
- plan と既存 TODO/checklist の対応が曖昧である。

## LLM Scope
- ユーザの自然言語指示がどの plan 範囲に対応するかを読む。
- 既存 TODO が plan の対象範囲を十分に覆うかを説明する。
- WARN または高リスクの理由を利用者に平易に説明する。
- review materials を作る場合、送信前に認証情報、個人情報、不要な全文ログ、外部送信不可情報が含まれないか確認する。

## Prohibitions
- TODO/checklist がないまま plan から実作業へ進まない。
- plan 本文を読まずに path-only で TODO 化しない。
- plan の広い範囲を 1 つの曖昧な TODO に押し込まない。
- 3者レビューを常に必須化しない。
- WARN または高リスクを無視して実作業へ進まない。

## Stop Conditions
- 対象 plan または実行範囲が一意に定まらない。
- 対応 TODO が複数あり、どれを使うべきか判断できない。
- `work-backlog audit-checklist-coverage` が DEVIATION。
- `task-quality-check audit` が DEVIATION。
- WARN または高リスクについて、review materials 作成または明示判断が未了。
```


## Scope

- Check whether the changed target files clearly state the intended contract.
- Check whether related instructions are mutually consistent across targets.
- Check whether the documented procedure is actionable before API review, triage, manifest, or commit steps continue.

## Out Of Scope

- Do not request unrelated refactors or style-only rewrites.
- Do not judge files that are not listed in Target Files.
- Do not treat missing implementation work as a document defect unless the target text claims it already exists.

## Finding Policy

- Report must-fix findings for contradictions, missing required gates, or instructions that would allow an unsafe workflow action.
- Report should-fix findings for ambiguity that could cause repeated manual judgment or unnecessary API review loops.
- Return findings: [] when the target files are internally consistent for this review question.

## Sensitive Information Check

- status: passed
- External API review must not proceed if this section reports potential secrets.


# Output contract
Return YAML only.
The response must include the top-level key findings.
Additional top-level keys are allowed only when the criteria explicitly defines them.
Do not add wrapper keys such as review, result, metadata, or summary.
Do not wrap the YAML in Markdown code fences.
Do not write prose before or after the YAML.

Each finding must include these keys:
- severity
- target_location
- description
- rationale

Use only these severity values:
- CRITICAL
- ERROR
- WARN
- INFO

If there are no findings and the criteria does not define additional top-level keys, return exactly:

findings: []

Valid shape example:

findings:
  - severity: WARN
    target_location: "path or section"
    description: "Plain finding summary"
    rationale: "Why this matters"

# Prior findings
なし

# Target path
.reviewcompass/guidance/effective-prompts/user-initiated-plan-to-todo-bridge.prompt.md

# Target document
# Effective Prompt: User-Initiated Plan To TODO Bridge

## Decision Point
- group: operation_prompt
- id: user_initiated_plan_to_todo_bridge

## Purpose
ユーザが backlog plan または plan 内の一部作業を実行しようとしたときに読む。plan を実行単位へ変換する直前で、plan から直接実作業に入らず、backlog TODO、runtime checklist、coverage / quality audit、必要時の review materials へ接続する。

## Trigger Boundary
- ユーザが「次へ」「進める」「この plan を進める」など、plan 由来の実作業開始を指示した。
- `next --json` が completed で、次作業を backlog plan から選ぶ状態になった。
- plan の `implementation_plan`、`acceptance_criteria`、remaining work を読んで実装、整理、移行、監査へ入ろうとしている。
- plan の一部 phase / task だけを実行しようとしている。

plan を読むだけ、説明するだけ、優先順位を相談するだけの場合は、この bridge を開始しない。

## Required Inputs
- 対象 plan id または plan path。
- `.reviewcompass/backlog/index.yaml`
- 対象 plan 本文。
- 対応する既存 backlog TODO の有無。
- 現在の work unit stack。

## Artifact Boundaries
- plan は方針、分解案、受け入れ条件、残作業を保持する。実行対象そのものではなく、どこを TODO 化するかを判断する上流材料である。
- TODO は実行対象化した最小の追跡単位である。1 つの TODO は、同じ目的、同じ完了条件、同じ検証単位で閉じる範囲だけを扱う。
- runtime checklist は実行中の進捗証跡である。TODO の task / implementation_plan / todos / red_tests から生成し、作業中の active / pending / done を保持する。
- evidence checklist は完了後の固定証跡である。runtime checklist を後から作業中だったかのように補う場所ではなく、完了時点の checklist と検証結果を残す。
- TODO の execution_history は、完了した checklist_id、evidence_path、completion_summary を TODO 正本へ戻す索引である。

## TODO Conversion Rules
- 同時に完了判定できる範囲だけを 1 TODO にする。複数の独立した成果物、検証、判断待ちを含む場合は TODO を分ける。
- plan の一部だけを実行する場合、TODO には source_plan_id または source_plan_path と、対象 phase / task / acceptance_criteria / red_tests の対応を記録する。
- acceptance_criteria は TODO の完了条件へ落とす。受け入れ条件に対応しない checklist item だけで実作業へ進まない。
- red_tests は実装前の確認項目として TODO または checklist に残す。赤テストが不要な文書作業では lightweight self-check の理由を明示する。
- 既存 TODO がある場合は、対象範囲、完了条件、検証単位が plan の実行範囲を覆るかを確認してから再利用する。
- 対応が曖昧な場合は TODO を新規作成または分割し、曖昧なまま既存 TODO に押し込まない。

## Mechanical Steps
1. 対象 plan を読み、実行しようとしている範囲を特定する。
2. `.reviewcompass/backlog/index.yaml` と backlog TODO を確認し、同じ範囲を扱う既存 TODO があるかを見る。
3. 対応 TODO がなければ `work-backlog add-todo` で plan 由来 TODO を作成する。
4. 作成または選択した TODO を `work-backlog show --id <todo-id> --json` で読む。
5. `work-backlog start-checklist --id <todo-id>` で runtime checklist を生成する。
6. `work-backlog audit-checklist-coverage --id <todo-id> --checklist-id <checklist-id>` を実行する。
7. `task-quality-check audit --backlog-id <todo-id> --checklist-id <checklist-id>` を実行する。
8. audit が DEVIATION の場合は実作業へ進まず、TODO または checklist の修正に戻る。
9. audit が WARN または高リスクの場合、`task-quality-check prepare-review-materials --backlog-id <todo-id> --checklist-id <checklist-id> --output-dir <dir>` で review materials を作る。
10. review materials を作った場合、外部 API review に進むか、ローカル判断に留めるかを利用者に確認する。
11. coverage / quality が OK で、WARN または高リスクが解消または明示判断済みの場合だけ、checklist item を active にして実作業へ進む。

## High-Risk Signals
- plan から複数の独立作業を切り出す必要がある。
- TODO の粒度や順序に迷いがある。
- `task-quality-check audit` が WARN を返した。
- red test の位置づけ、レビュー要否、または実行順序に判断が必要である。
- plan と既存 TODO/checklist の対応が曖昧である。

## LLM Scope
- ユーザの自然言語指示がどの plan 範囲に対応するかを読む。
- 既存 TODO が plan の対象範囲を十分に覆うかを説明する。
- WARN または高リスクの理由を利用者に平易に説明する。
- review materials を作る場合、送信前に認証情報、個人情報、不要な全文ログ、外部送信不可情報が含まれないか確認する。

## Prohibitions
- TODO/checklist がないまま plan から実作業へ進まない。
- plan 本文を読まずに path-only で TODO 化しない。
- plan の広い範囲を 1 つの曖昧な TODO に押し込まない。
- 3者レビューを常に必須化しない。
- WARN または高リスクを無視して実作業へ進まない。

## Stop Conditions
- 対象 plan または実行範囲が一意に定まらない。
- 対応 TODO が複数あり、どれを使うべきか判断できない。
- `work-backlog audit-checklist-coverage` が DEVIATION。
- `task-quality-check audit` が DEVIATION。
- WARN または高リスクについて、review materials 作成または明示判断が未了。

