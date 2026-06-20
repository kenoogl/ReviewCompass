prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.5-flash

# Task
Review the target document for the requested phase and criteria.

# Phase
post_write_verification

# Criteria
# Post-write Review Target

criteria_id: api_review_prompt_quality_postwrite_current
phase: post_write_verification
generated_at: 2026-06-20T14:13:28.799793+00:00

## Change Summary

APIレビュー用プロンプト品質規律・運用文書・規律マップの現在内容に対するpost-write verification

## Review Question

現在の3文書は、APIレビュー用プロンプト品質に関する合意内容を正しく反映し、参照・既存記述・内部論理に矛盾がないか。

## Target Files

- docs/disciplines/discipline_llm_as_judge_prompting.md sha256=2dc7be6e2c21ade683c1736e23d2ce1943a4bc1bcda5b9edabe57ee0e9ccbc33
- docs/operations/API_REVIEW_PROMPT_QUALITY.md sha256=61d209015f56bdeca42127165c91091361cba6b25d38074c819f99499681fda4
- docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml sha256=ca6aa8ef21a672e01268f26a282b0f8fc71329592e4f0b59e2da8e7d24b598e1

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
docs/disciplines/discipline_llm_as_judge_prompting.md
docs/operations/API_REVIEW_PROMPT_QUALITY.md
docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml

# Target document
## docs/disciplines/discipline_llm_as_judge_prompting.md

---
name: llm-as-judge-prompting
description: LLM as a Judge（AIモデルを審査者として活用する）シーンでのプロンプト作成ガイドライン
metadata:
  type: feedback
---

# LLM as a Judge：プロンプト作成ガイドライン

## このガイドラインを使う場面

人間が判断しにくい設計上の問いを、複数のAIモデルに独立して審査させるとき。
特に次のような状況で有効である。

- 選択肢の優劣を客観的に評価したいが、人間が当事者に近すぎて判断が難しい
- 設計の欠陥を「見落としなく」洗い出したい
- 修正案が問題を正しく解消しているかを第三者視点で確認したい

## プロンプト作成の手順

### ステップ1：メインのLLMに問題を直接検討させる（材料揃え）

プロンプトを書く前に、まず担当のLLM自身に問題にあたらせる。

目的は2つある。
1. 問題の理解に必要な情報（背景・前提・関連する設計）を特定する
2. 判断のポイント（何が分かれば答えが決まるか）を認識する

この段階で担当LLMが「この情報がないと判断できない」と気づいた内容は、プロンプトに含める情報として確定する。

### ステップ2：プロンプトを作成する

ステップ1で揃えた材料を使ってプロンプトを作成する。プロンプトには次の3つの要素が必要である。

**適切な情報：**
問題の背景・現状・関連する設計の記述を含める。
判断に必要な情報が欠けていると、モデルが推測で回答し、的外れな結果になる。

**適切な問い：**
「何を分析してほしいか」を問いとして明示する。
問いは独立した分析を促す形で書く。答えを誘導したり、特定の方向に引っ張ったりしない。

**適切な範囲：**
分析の対象を絞りすぎず、広げすぎず設定する。
広すぎると焦点が定まらない。狭すぎると問題の核心が見えなくなる。

プロンプトを作成したら、送信前に次の確認を行う。

**送信前の確認（機微な情報のチェック）：**
プロンプトを外部のモデルに送信する前に、次の情報が含まれていないか確認する。

- APIキー・アクセストークン・パスワードなどの認証情報
- メールアドレス・電話番号など個人を特定できる情報
- 第三者に公開してはいけないプロジェクト固有の機密情報

含まれている場合は、伏字や仮の値に置き換えてから送信する。

**ReviewCompass 内部資料の扱い：**
ReviewCompass の API review-run / proxy_model 判断では、判断に必要なリポジトリ内の仕様・設計・タスク・レビュー所見・要約・証跡パスを外部 API prompt に含めることがある。これらは、上記の認証情報・個人情報・第三者非公開機密を含まない限り、利用者が API review / proxy_model 判断の実行を明示承認した場合に送信可能なレビュー材料として扱う。

ただし、送信材料は判断に必要な最小範囲に絞る。秘密値、個人情報、契約上外部送信できない第三者情報、不要な全文ログは含めない。外部送信リスクが問題になる場合は、抽象化・伏字化・ローカル判断への切り替えを利用者へ提示する。

### ステップ3：モデルに審査させる

プロンプトをAIモデルに渡し、独立して審査させる。

**複数モデルでの審査（3者レビュー）を推奨：**
同じプロンプトを複数のAIモデルに渡す。モデルが一致して指摘した内容は信頼性が高い。
モデルによって見解が分かれた内容は、設計の曖昧さを示す手がかりになる。
3者が推奨だが、1者のみでも有効である。

**1者への審査（proxy_model）の場合：**
proxy_model（個別の所見の採否判断を別のモデルに委ねる運用）でも、ステップ1〜2の手順は同じである。
プロンプトの品質が採否判断の質に直結するため、材料揃え・問い設計・機微情報チェックを省略しない。

## 避けるべきこと

### 閉じた選択を強制しない

複数の案を比較評価させることは問題ない。問題なのは「AかBかCの中から選べ」という問いの設計である。この形にすると、モデルは「選択モード」になり、選択肢の外にある可能性（新たな案・前提の誤り・全案の否定）が出にくくなる。分析が浅くなる。

問題の状況と比較したい対象を説明し、モデルが枠を超えた分析をできるようにする。必要であれば「選択肢の枠を超えて考えてよい」と明示する。

### プロンプトを考えずに即時投げない

問題を整理する前にすぐAPIに渡すと、情報が不足してモデルが的外れな内容を回答する。担当LLMが問題を理解してから投げることで、回答の質が大きく変わる。

## 発展：複数ターンの活用

1回のレビューで答えが出なかった場合、前の回答を参照しながら2回目のレビューを実施できる。
前の回答で「深掘りすべき論点」が明らかになった場合は、その論点だけに絞った新しいプロンプトを作成する。

複数ターンの場合も、各ターンのプロンプトは「ステップ1〜3」の手順で作成する。
前のターンの回答をそのまま次のプロンプトに貼り付けるのではなく、担当LLMが整理した上で次の問いを設計する。


## docs/operations/API_REVIEW_PROMPT_QUALITY.md

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

`docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review` が適用される review では、phase ごとに次を確認する。

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


## docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml

# next_action ごとの直前必読規律マップ。
# `tools/check-workflow-action.py next --json` はこの内容を
# `next_action.required_disciplines` として返す。
# 作業対象の状態台帳や持ち越し一覧は規律ではないため、
# `required_inputs` の抽象入力として返す。
# `decision_points` は機械可読な判定点の全体カタログである。
# `by_kind`、`by_stage`、`required_inputs` は既存実装が読む実行時マップとして維持する。
default:
  - docs/operations/WORKFLOW_NAVIGATION.md
default_prompt_length_bounds:
  min_chars: 400
  max_chars: 20000
  failure_verdict: WARN
decision_points:
  next_action_kind:
    - id: stage
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/disciplines/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: cross_feature_stage
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/disciplines/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: commit_stop_point
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#commit_stop_point
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: upstream_recheck
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_classification_required
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: completed
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: unknown
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: feature_definition_required
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#feature_definition_required
        - docs/operations/INITIAL_SETUP_LLM_GUIDE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_verification
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_verification
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: lightweight_self_check
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#lightweight_self_check
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_policy_violation
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_policy_violation
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_human_decision_required
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_human_decision_required
        - docs/disciplines/discipline_post_write_verification.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_in_progress
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: maintenance_in_progress
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#maintenance_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: resume_in_progress
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#resume_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_started
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#reopen-start
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#commit
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_start_failed
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#reopen-start
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#commit
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  workflow_stage:
    - id: candidate-proposal
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - stages/feature-partitioning/2026-05-24-proposal.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: review
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - stages/intent.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: drafting
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/disciplines/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: triad-review
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        - docs/operations/API_REVIEW_PROMPT_QUALITY.md
        - docs/disciplines/discipline_llm_as_judge_prompting.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
      prompt_length_bounds:
        min_chars: 1200
        max_chars: 60000
        failure_verdict: DEVIATION
    - id: review-wave
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        - learning/workflow/carry-forward-register/reviewcompass-import.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: alignment
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        - docs/disciplines/discipline_workflow_state_truth_source.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: approval
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/WORKFLOW_PRECHECK.md#spec-set
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#spec-set
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
      prompt_length_bounds:
        min_chars: 400
        max_chars: 12000
        failure_verdict: DEVIATION
  precheck_subcommand:
    - id: spec-set
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#spec-set
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#spec-set
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: commit
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#commit
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#commit
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: push
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#push
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#push
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-plan
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#autonomous-plan
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-plan-template
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#autonomous-plan-template
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-plan-record-integration
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#autonomous-plan-record-integration
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: autonomous-ledger-audit
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#autonomous-ledger-audit
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: audit-commit
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#audit-commit
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#audit-commit
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: next
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen-start
      prompt_source_refs:
        - docs/operations/WORKFLOW_PRECHECK.md#reopen-start
        - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#commit
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  operation_prompt:
    - id: commit
      prompt_source_refs:
        - docs/operations/COMMIT_OPERATION_CARD.md#commit-operation-card
      effective_prompt_policy: one_effective_prompt_per_decision_point
  reopen_required_action:
    - id: classify_and_rollback_flags
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: repair_canonical_documents
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: rerun_alignment_approval_chain
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: run_reopen_pending_gate
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: run_reopen_drafting
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: wait_for_human_approval
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: finalize_reopen
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_completed
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: inspect_reopen_state
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#reopen_in_progress
        - docs/operations/REOPEN_PROCEDURE.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  review_run_triage_command:
    - id: list-pending
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: decide
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: manifest-template
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: write-manifest
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: assert-apply-fixes-ready
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: assert-review-report-ready
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: generate-review-report
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
  post_write_manifest_gate:
    - id: post_write_manifest_completed
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_verification
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_manifest_human_required
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_human_decision_required
        - docs/disciplines/discipline_post_write_verification.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_manifest_missing_or_invalid
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_verification
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: post_write_policy_violation
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md#post_write_policy_violation
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  proxy_model_decision_gate:
    - id: user_visible_triage_gate
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: proxy_decision_prompt
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/operations/API_REVIEW_PROMPT_QUALITY.md
        - docs/disciplines/discipline_llm_as_judge_prompting.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: proxy_decision_file
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/operations/API_REVIEW_PROMPT_QUALITY.md
        - docs/disciplines/discipline_llm_as_judge_prompting.md
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: proxy_approval_record
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  conformance_evaluation_gate:
    - id: mv6_prompt_isolation
      prompt_source_refs:
        - docs/operations/WORKFLOW_NAVIGATION.md
        - .reviewcompass/specs/conformance-evaluation/tasks.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: reopen_handoff_package
      prompt_source_refs:
        - docs/operations/REOPEN_PROCEDURE.md
        - .reviewcompass/specs/conformance-evaluation/design.md
        - .reviewcompass/specs/conformance-evaluation/tasks.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
  yaml_audit_gate:
    - id: yaml_audit_scope
      prompt_source_refs:
        - docs/disciplines/discipline_yaml_audit.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: yaml_audit_post_write_check
      prompt_source_refs:
        - docs/disciplines/discipline_yaml_audit.md
        - docs/disciplines/discipline_post_write_verification.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
by_kind:
  stage:
    - docs/disciplines/discipline_workflow_state_truth_source.md
  cross_feature_stage:
    - docs/disciplines/discipline_workflow_state_truth_source.md
  post_write_verification:
    - docs/operations/WORKFLOW_NAVIGATION.md#post_write_verification
    - docs/disciplines/discipline_post_write_verification.md
  lightweight_self_check:
    - docs/operations/WORKFLOW_NAVIGATION.md#lightweight_self_check
  post_write_policy_violation:
    - docs/operations/WORKFLOW_NAVIGATION.md#post_write_policy_violation
    - docs/disciplines/discipline_post_write_verification.md
  post_write_human_decision_required:
    - docs/operations/WORKFLOW_NAVIGATION.md#post_write_human_decision_required
    - docs/disciplines/discipline_post_write_verification.md
    - docs/disciplines/discipline_approval_operation.md
  reopen_in_progress:
    - docs/operations/REOPEN_PROCEDURE.md
    - docs/disciplines/discipline_approval_operation.md
  maintenance_in_progress:
    - docs/operations/WORKFLOW_NAVIGATION.md#maintenance_in_progress
  resume_in_progress:
    - docs/operations/WORKFLOW_NAVIGATION.md#resume_in_progress
  feature_definition_required:
    - docs/operations/WORKFLOW_NAVIGATION.md#feature_definition_required
    - docs/operations/INITIAL_SETUP_LLM_GUIDE.md
by_stage:
  drafting:
    - docs/operations/REOPEN_PROCEDURE.md
    - docs/disciplines/discipline_workflow_state_truth_source.md
  triad-review:
    - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
    - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
    - docs/operations/API_REVIEW_PROMPT_QUALITY.md
    - docs/disciplines/discipline_llm_as_judge_prompting.md
    - docs/disciplines/discipline_approval_operation.md
  review-wave:
    - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
  alignment:
    - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
    - docs/disciplines/discipline_workflow_state_truth_source.md
  approval:
    - docs/disciplines/discipline_approval_operation.md
    - docs/operations/WORKFLOW_PRECHECK.md#spec-set
    - docs/operations/WORKFLOW_PRECHECK_DETAILS.md#spec-set
required_inputs:
  by_stage:
    drafting:
      - id: target_feature_documents
        role: stage_entry_context
        source_type: feature_document_set
        purpose: Read the current feature state and phase documents before updating the phase artifact.
        resolver:
          kind: next_action_template
          paths:
            - .reviewcompass/specs/{feature}/spec.json
            - .reviewcompass/specs/{feature}/requirements.md
            - .reviewcompass/specs/{feature}/design.md
            - .reviewcompass/specs/{feature}/tasks.md
        read_policy: current_feature_documents
      - id: reopen_procedure_state
        role: workflow_state_context
        source_type: reopen_in_progress_file
        purpose: Read the reopen state and downstream impact decisions before drafting.
        resolver:
          kind: next_action_template
          paths:
            - "{file}"
        read_policy: reopen_state
    triad-review:
      - id: target_feature_documents
        role: stage_entry_context
        source_type: feature_document_set
        purpose: Read the current feature state and phase documents before starting triad-review, including upstream intent transfer from requirements to design to tasks to implementation as applicable.
        resolver:
          kind: next_action_template
          paths:
            - .reviewcompass/specs/{feature}/spec.json
            - .reviewcompass/specs/{feature}/requirements.md
            - .reviewcompass/specs/{feature}/design.md
            - .reviewcompass/specs/{feature}/tasks.md
        read_policy: current_feature_documents
      - id: triad_review_run_artifacts
        role: review_run_context
        source_type: review_run_artifact_set
        purpose: Prepare or read the review-run bundle, raw responses, model summaries, variant/role assignments, same-root finding clusters, and three-level triage records for this triad-review. Before proxy_model, implementation edits, spec.json updates, or phase movement, present the user-visible triage gate described in SESSION_WORKFLOW_GUIDE.md#3.3-a-2 and stop.
        resolver:
          kind: next_action_template
          base_path_pattern: .reviewcompass/specs/{feature}/reviews/*-{feature}-{phase}-review-run
        required_artifacts:
          - review-target.md
          - raw/
          - rounds.yaml
          - model-result-summary.yaml
          - triage.yaml
          - raw-review-triage-summary.md
          - variant-role-assignment
          - user-visible-triage-gate
        read_policy: review_run_bundle_and_triage
      - id: vertical_intent_transfer_check
        role: review_prompt_requirement
        source_type: upstream_intent_transfer_contract
        purpose: Ensure triad-review checks that upstream purpose, responsibility boundaries, acceptance criteria, and forbidden actions are inherited into the target phase without omission, weakening, unsupported additions, or drift.
        resolver:
          kind: static_reference
          path: docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        phase_chains:
          requirements:
            - upstream_decision_materials
            - requirements.md
          design:
            - requirements.md
            - design.md
          tasks:
            - requirements.md
            - design.md
            - tasks.md
          implementation:
            - requirements.md
            - design.md
            - tasks.md
            - implementation
        review_target_by_phase:
          requirements:
            review_target: requirements.md
            source_materials:
              - upstream_decision_materials
              - reopen_classification_record
              - planning_notes
              - user_decisions
            out_of_scope:
              - downstream_artifacts_not_review_target
              - design.md correctness
              - tasks.md correctness
        prompt_materialization_contract:
          source_materials_must_not_be_path_only: true
          required_prompt_material:
            - upstream_excerpt_or_structured_summary
            - target_phase_artifact_excerpt
            - review_target
            - out_of_scope
          upstream_summary_fields:
            - purpose
            - responsibility_boundaries
            - acceptance_criteria
            - forbidden_actions
            - unresolved_or_design_deferred_items
            - intended_target_phase_transfer
          blocking_conditions:
            - block_review_run_when_upstream_material_unread
            - block_review_run_when_prompt_contains_only_source_paths
            - block_review_run_when_upstream_summary_omits_required_fields
        required_question: upstream目的・責務境界・受入条件・禁止事項が対象成果物へ欠落・弱体化・逸脱・未根拠追加なく引き継がれているか。
        read_policy: include_in_review_prompt
    review-wave:
      - id: cross_feature_stage_artifacts
        role: stage_output_contract
        source_type: artifact_location_contract
        purpose: Record cross-feature stage evidence under the cross-feature namespace instead of any single feature. Standard path is .reviewcompass/specs/_cross_feature/reviews/{date}-{phase}-{stage}.md.
        resolver:
          kind: static_path_template
          path: .reviewcompass/specs/_cross_feature/reviews/{date}-{phase}-{stage}.md
        read_policy: create_or_update_stage_artifact
      - id: unresolved_cross_scope_items
        role: stage_entry_context
        source_type: carry_forward_register
        purpose: Read unresolved items carried forward from prior reviews or adjacent scopes before starting this stage.
        resolver:
          kind: project_state
          path: learning/workflow/carry-forward-register/reviewcompass-import.yaml
        read_policy: unresolved_items_only
      - id: vertical_intent_transfer_check
        role: review_prompt_requirement
        source_type: upstream_intent_transfer_contract
        purpose: Ensure review-wave preserves upstream intent while resolving cross-feature findings, and does not weaken or add unsupported requirements when carrying fixes across features.
        resolver:
          kind: static_reference
          path: docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
        required_question: 上流の目的・責務境界・受入条件・禁止事項が、横断対処後の対象成果物へ欠落・弱体化・逸脱・未根拠追加なく引き継がれているか。
        read_policy: include_in_review_prompt

