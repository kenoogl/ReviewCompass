prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.1-pro-preview

# Task
Review the target document for the requested phase and criteria.

# Phase
post_write_verification

# Criteria
# Post-write Review Target

criteria_id: initial_setup_guide_deployment_reference_post_write
phase: post_write_verification
generated_at: 2026-06-23T08:14:52.242155+00:00

## Change Summary

Remove stale deployment user guide dependency from initial setup guidance.

## Review Question

Does the updated initial setup guide accurately reflect the deployment package contents without introducing broken references or contradictory setup instructions?

## Target Files

- .reviewcompass/guidance/INITIAL_SETUP_LLM_GUIDE.md sha256=5389ced551bb681b3e521903293cf11b284c5735c4a9d6201f4f1d44737237cc

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


## Target File Contents

### .reviewcompass/guidance/INITIAL_SETUP_LLM_GUIDE.md

content_mode: full_text
content_sha256: 5389ced551bb681b3e521903293cf11b284c5735c4a9d6201f4f1d44737237cc

```text
# 初期設定 LLM 指示書

最終更新：2026-06-16（§10 手順 6 の Codex TODO hook を runtime 下書き保存と正式昇格方式へ更新）

本文書は、ReviewCompass 配布物を使って初期設定を行う LLM のための指示書である。利用者がターミナルで Python コマンドを直接実行する前提ではなく、LLM が必要な確認と設定を案内または代行する。

本文書は初期設定時に LLM が読む手順の正本であり、利用者向け説明は設定作業中の確認と完了報告で補う。

## 1. 役割

あなたは ReviewCompass 初期設定を支援する LLM である。利用者に確認すべき点を平易に説明し、必要なファイル確認、設定作成、ReviewCompass ツール実行を代行する。

初期設定では、次を守る。

1. 対象アプリの既存ファイルを不用意に変更しない。
2. 対象アプリに書き込む前に、書き込み先を利用者へ説明する。
3. ReviewCompass 配布物ディレクトリと対象アプリ root を混同しない。
4. API key、token、password などの秘密値をファイルへ書き込まない。
5. 実行した確認、作成したファイル、残タスクを最後に報告する。

## 2. 最初に確認すること

利用者から次を確認する。

| 項目 | 確認内容 |
| --- | --- |
| 起動パターン | パターン 1、2、3 のどれで進めるか。 |
| 操縦 LLM | この設定作業と以後の運用をどの LLM で行うか（Claude Code か Codex CLI か。それ以外の LLM の場合は §11 のフォールバックに従う）。review-run の既定 variant 選択（§11）に使う。 |
| ReviewCompass 配布物ディレクトリ | ReviewCompass の配布物が置かれている場所（絶対パス）。 |
| 対象アプリ root | ReviewCompass を適用する対象アプリの root。未定なら対象アプリへは書き込まない。 |
| 初期設定の範囲 | 配布物単体確認までか、対象アプリ側設定まで行うか。 |
| API 秘密値の渡し方 | 環境変数など、配布物外の方法で渡すこと。 |
| hook 導入 | commit／push の事前検査 hook を導入するか（強く推奨、§10）。見送る場合は利用者の明示判断として完了報告に記録する。 |

不足している情報がある場合は、推測で進めず、利用者に確認する。

## 3. パターン別の進め方

### 3.1 パターン 1：ReviewCompass 配布物側で起動して対象アプリも設定する

このパターンでは、現在の作業ディレクトリが ReviewCompass 配布物ディレクトリであることを確認する。対象アプリ root は利用者から指定される。

進め方：

1. ReviewCompass 配布物に `tools/`、`runtime/`、`templates/`、`config/api-settings.yaml` があることを確認する。
2. 対象アプリ root が存在することを確認する。
3. 対象アプリ root に `.reviewcompass/` があるか確認する。
4. `.reviewcompass/` がなければ、作成前に利用者へ説明する。
5. 対象アプリ側の設定テンプレートを作成または確認する。
6. 入口の合流（§8）と hook 導入（§10、強く推奨）を行う。
7. workflow next、review-run smoke、conformance-evaluation など、利用者が選んだ初期確認へ進む。

### 3.2 パターン 2：対象アプリ側で起動して ReviewCompass 配布物を指定する

このパターンでは、現在の作業ディレクトリが対象アプリ root であることを確認する。ReviewCompass 配布物ディレクトリは利用者から指定される。

進め方：

1. 現在のディレクトリが対象アプリ root か確認する。
2. ReviewCompass 配布物ディレクトリに `tools/`、`runtime/`、`templates/`、`config/api-settings.yaml` があることを確認する。
3. 対象アプリ root に `.reviewcompass/` があるか確認する。
4. `.reviewcompass/` がなければ、作成前に利用者へ説明する。
5. 対象アプリ側の `.reviewcompass/config.yaml` を作成または確認する。
6. 入口の合流（§8）と hook 導入（§10、強く推奨）を行う。
7. 配布済み ReviewCompass のツールを使い、対象アプリ側の workflow next を確認する（feature 未確定なら `feature_definition_required` の案内が返る。§9）。

通常利用を始める場合は、このパターンを基本とする。

### 3.3 パターン 3：配布物側だけ先に確認し、対象アプリ側設定は後で行う

このパターンでは、まず ReviewCompass 配布物ディレクトリだけを確認する。対象アプリ root が未定、または利用者がまだ対象アプリへ書き込みたくない場合は、この範囲で止める。

配布物側で確認すること：

1. `tools/`、`runtime/`、`templates/`（入口・hook・feature-dependency の雛形を含む）、`config/api-settings.yaml` があること。
2. `config/api-settings.yaml` に秘密値が含まれていないこと。
3. `runtime/config/config.yaml.template` があること。
4. `.reviewcompass/guidance/INITIAL_SETUP_LLM_GUIDE.md` があること。
5. ReviewCompass の Python ツールを実行できる環境か確認すること。

対象アプリが決まったら、対象アプリ root で新しい LLM セッションを立ち上げ、パターン 2 として初期設定を続ける。

## 4. 対象アプリ側に作成または確認するもの

対象アプリ側では、次を確認する。

| パス | 扱い |
| --- | --- |
| `.reviewcompass/` | 対象アプリ側の ReviewCompass 作業領域。なければ作成候補。 |
| `.reviewcompass/config.yaml` | 対象アプリ固有の設定。テンプレートから作成候補。 |
| `.reviewcompass/specs/` | 仕様、設計、タスク、review-run 記録の置き場。 |
| `.reviewcompass/AGENT_ENTRY.md` | LLM セッションの入口規律。テンプレートから実体化する（§8）。 |
| `.reviewcompass/feature-dependency.yaml` | feature 一覧・開発順・依存の定義。feature-partitioning 承認後に作成する（§9）。 |
| `CLAUDE.md`／`AGENTS.md` | 既存入口ファイルへの参照 1 行の追記（§8）。 |
| `.claude/`／`.codex/` | commit／push 事前検査 hook と設定（§10、強く推奨）。 |

既存の `.reviewcompass/` がある場合は、上書きせず、内容を確認してから進める。

## 5. 秘密値の扱い

`config/api-settings.yaml` や対象アプリ側の `.reviewcompass/config.yaml` に API key、token、password などを書き込まない。

秘密値が必要な場合は、利用者に次のように説明する。

```text
API key は設定ファイルに書かず、環境変数など配布物外の方法で渡してください。
この初期設定では、秘密値そのものは表示・保存しません。
```

## 6. 初期確認の最小セット

対象アプリ側まで設定する場合は、最低限次を確認する。

1. ReviewCompass 配布物ディレクトリを参照できる。
2. 対象アプリ root に書き込みできる。
3. 対象アプリ側の `.reviewcompass/` の作成または既存確認が済んでいる。
4. 対象アプリ側の `.reviewcompass/config.yaml` の作成または既存確認が済んでいる。
5. 入口の合流（§8）が済んでいる。
6. workflow next を確認できる（feature 未確定の段階では `feature_definition_required` の案内が返ることを確認する）。
7. review-run 記録の出力先を対象アプリ側に指定できる。

## 7. 完了報告

初期設定が終わったら、利用者へ次を報告する。

1. 選択した起動パターンと操縦 LLM。
2. ReviewCompass 配布物ディレクトリ。
3. 対象アプリ root。
4. 作成または変更した対象アプリ側ファイル。
5. hook 導入の有無（見送った場合は、利用者の明示判断であることと理由）。
6. 実行した確認。
7. 未実施の確認。
8. 次に行うべき作業。

対象アプリへ何も書き込んでいない場合は、そのことを明示する。

## 8. 入口の合流（AGENT_ENTRY の実体化と参照 1 行）

対象アプリで複数の LLM（Claude Code、Codex CLI）を同じ規律で使うための入口を作る。

1. 配布物の `templates/entry/AGENT_ENTRY.template.md` を、対象アプリの `.reviewcompass/AGENT_ENTRY.md` として実体化する。冒頭の記入欄（実体化日、実体化元の配布物）と §2 の「配布物の場所」（**絶対パス**）を記入する。
2. 既存の入口ファイルへ、利用者承認のうえ参照 1 行を末尾に追記する。追記の前に、書き込み先・挿入する行・挿入位置を利用者へ提示する。書き込むのは次の枠内の文字列**だけ**である（枠外の説明文を書き込まない）。

   `CLAUDE.md` へ追記する 1 行：

   ```text
   @.reviewcompass/AGENT_ENTRY.md
   ```

   `AGENTS.md` へ追記する 1 行：

   ```text
   ReviewCompass を使う作業では、最初に `.reviewcompass/AGENT_ENTRY.md` を読み、その規律に従う。
   ```
3. 入口ファイルが存在しない場合は、その 1 行だけの新規ファイルを作る（これも承認のうえ）。同じ行が既にある場合は何もしない。既存の記述は変更しない。
4. 既存入口の規律と AGENT_ENTRY の規律が衝突している場合（例：既存入口が「commit は自動で実行してよい」と指示しているが、AGENT_ENTRY §5 は利用者の明示承認を求める、というように両立しない指示）は、作業を進めず利用者へ提示する。優先順位は自動で決めず、利用者判断で AGENT_ENTRY 側を調整する。
5. 対象アプリの `.gitignore` へ、ReviewCompass ツールの実行時生成物の除外 1 行を利用者承認のうえ追記する（除外がないと、2 回目以降の `next` がツール自身の実行記録を未検証の文書変更として誤検出し、`post_write_verification` を返し続ける）。実行時生成物（検査ログ・effective prompt・commit 承認レコード）は `.reviewcompass/runtime/` 区画に集約されている（2026-06-12 配置規約 PLC-DEC-004 反映。旧 3 パスの個別除外は不要になった）。

   ```text
   .reviewcompass/runtime/
   ```

## 9. feature 一覧の立ち上げ

対象アプリの workflow 管理は、`.reviewcompass/feature-dependency.yaml` の `feature_order` キーに基づいて動く。

1. feature 一覧が未確定の段階では、`next` は `feature_definition_required` を返し、intent と feature-partitioning の実施を案内する。これはエラーではなく正常な立ち上げ状態である。
2. feature-partitioning の提案には、機能ごとの依存の主張と理由、順序の導出を必須で含める（人が根拠を検討できるようにする）。
3. 承認された分割結果を、配布物の `templates/specs/feature-dependency.yaml.template` から実体化した `.reviewcompass/feature-dependency.yaml` に記録する。依存される機能を先に並べる。
4. `feature_order` が `depends_on` と矛盾する場合（依存先が後ろ、依存先が一覧にない、循環依存）、`next` は理由つきの逸脱を返す。

## 10. hook 導入（強く推奨）

commit／push の事前検査 hook を対象アプリへ導入する。LLM が規律を読み忘れても、不可逆操作だけは機械が止める防衛線になる。初期設定の標準手順として導入し、見送る場合は利用者の明示判断として完了報告に記録する。

1. 配布物の `templates/hooks/pre-bash-precheck.sh.template`、`templates/hooks/session-record-capture-current-on-todo.sh.template`、`templates/hooks/session-record-promote-previous-draft.sh.template` のプレースホルダを**絶対パス**へ置換する。
   - `{{REVIEWCOMPASS_PYTHON}}`：依存（PyYAML 等）導入済みの Python 実行系
   - `{{REVIEWCOMPASS_DIR}}`：配布物 root
2. 置換後のファイルを、対象アプリの `.claude/hooks/pre-bash-precheck.sh` と `.codex/hooks/pre-bash-precheck.sh` の両方へ同一内容で複製する。同名の既存ファイルがある場合は上書きせず、既存内容と置換後の内容を利用者へ提示して扱いを確認する。
3. 置換後の `session-record-capture-current-on-todo.sh.template` と `session-record-promote-previous-draft.sh.template` は、対象アプリの `.codex/hooks/` に配置する。同名の既存ファイルがある場合は上書きせず、既存内容と置換後の内容を利用者へ提示して扱いを確認する。
4. `templates/hooks/claude-settings.json.template` と `templates/hooks/codex-hooks.json.template` から、`.claude/settings.json` と `.codex/hooks.json` を作る。いずれも既存ファイルがある場合は上書きせず、hooks キーだけを既存へ合流させる（合流して書き込む内容を、書き込み前に利用者へ提示する）。
5. 静的チェック：複製した hook ファイルに未置換トークン（`{{`）が残っていないこと、置換先のパスが実在すること、`jq` が利用できることを確認する。
6. Codex 側の環境設定：Codex の非 managed command hook は、配置しただけでは実行されない。Codex の GUI 設定画面または CLI の `/hooks` で、対象アプリのプロジェクト hook が認識されていることを確認し、利用者が内容を確認したうえで信頼する。未信頼のままでは hook 一覧に出ても Active 0 / review 待ちになり、`PreToolUse` も `PostToolUse` も実行されない。hook ファイルや `.codex/hooks.json` を変更した場合は、定義 hash が変わるため再度 review / trust が必要になる。
7. Codex の現セッション下書き hook は `PostToolUse` に登録し、`TODO_NEXT_SESSION.md` の内容 hash が前回保存時から変わった場合だけ、現セッション rollout を `.reviewcompass/runtime/session-record-drafts/codex-<session_id>.md` へ下書き保存する。下書き先はテスト時に `RC_SESSION_DRAFT_DIR` で差し替えられる。現セッション途中版を `.reviewcompass/evidence/sessions/` と `docs/sessions/` へ直接作らない。`UserPromptSubmit` は発話ごとに呼ばれ得るため使用しない。動作確認では、対象アプリの `.reviewcompass/runtime/session-record-capture-current-on-todo.jsonl` を確認する。`todo_changed`、`selected`、`drafted`、`draft_failed`、`todo_unchanged`、`baseline_recorded` などが出る。`ignored_event` が出た場合は、`PostToolUse` 以外へ誤登録されているため hook 設定を修正する。
8. Codex の前セッション正式化 hook は `SessionStart` に matcher = `startup|resume` で登録し、現 `session_id` と異なる runtime 下書きを新しい順に確認して、検証できた最初の 1 件を正式 2 層記録へ昇格する。正式化前に下書き frontmatter `source_sha256` と現在の元 rollout の sha256 を比較し、一致した場合だけ昇格する。不一致なら `previous_draft_in_progress`、検証不能なら `previous_draft_unverifiable` を記録し、次候補へ進む。複数の終了済み下書きが溜まっている場合も、この hook が 1 回の `SessionStart` で昇格するのは 1 件だけであり、残りは次回 `SessionStart` または明示 backfill の対象とする。動作確認では、対象アプリの `.reviewcompass/runtime/session-record-promote-previous-draft.jsonl` を確認する。`selected` と `promoted` があれば正式化成功、`missing_jq` は jq 不在、`no_current_session_id` は current session_id 不在、`no_cwd` は cwd 不在、`no_draft_dir` は下書きディレクトリ不在、`no_previous_draft` は昇格対象なし、`previous_draft_in_progress` は下書き作成後に rollout が伸びた可能性があるため安全側でスキップ、`previous_draft_unverifiable` は hash 確認情報不足、`no_promote_tool` は昇格 helper 不在、`promote_failed` はその他の昇格失敗である。`Stop` は turn scope のためセッション終了 hook として使わない。
9. TODO を更新しないセッション、クラッシュ、hook 失敗、または Codex の `session_id` が取れない場合は、自動 fallback を追加せず、終了済みの対象 rollout を指定して `tools/session-record-backfill.py --session <jsonl> --source codex` を明示実行する。
10. 復旧手順：hook が「hook 設定不備」を理由に拒否する場合は、プレースホルダの置換値を確認して再置換する（テンプレートから作り直してよい）。Codex で hook が発火しない場合は、まず GUI 設定または `/hooks` で対象 hook が信頼済みか確認する。

## 11. 操縦 LLM 別の既定 variant

review-run の variant（モデルの組）は、起草者（操縦 LLM）と検証者の独立を保つため、操縦 LLM に応じた既定を使う。

| 操縦 LLM | 3 役 review-run の既定 | 小規模 1 体検証の既定 |
| --- | --- | --- |
| Claude Code | 接尾辞なしの `*_independent_3way` 系 | `post_write_verification_google`（共通） |
| Codex CLI | `*_independent_3way_codex_operator` 系 | 同上（共通） |

proxy_model（人の判断を代行させる場合のモデル）も、操縦 LLM と別系列のモデルを選ぶ。

上記以外の LLM で操縦する場合は、独断で進めず利用者に確認し、「起草者（操縦 LLM）と同系列のモデルを反証役・判定役・単独検証役に置かない」という独立性の原則に従って variant を選ぶ。その操縦 LLM 向けの既定 variant の追加は、第3者配布時の再検討事項とする。
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
.reviewcompass/guidance/INITIAL_SETUP_LLM_GUIDE.md

# Target document
# 初期設定 LLM 指示書

最終更新：2026-06-16（§10 手順 6 の Codex TODO hook を runtime 下書き保存と正式昇格方式へ更新）

本文書は、ReviewCompass 配布物を使って初期設定を行う LLM のための指示書である。利用者がターミナルで Python コマンドを直接実行する前提ではなく、LLM が必要な確認と設定を案内または代行する。

本文書は初期設定時に LLM が読む手順の正本であり、利用者向け説明は設定作業中の確認と完了報告で補う。

## 1. 役割

あなたは ReviewCompass 初期設定を支援する LLM である。利用者に確認すべき点を平易に説明し、必要なファイル確認、設定作成、ReviewCompass ツール実行を代行する。

初期設定では、次を守る。

1. 対象アプリの既存ファイルを不用意に変更しない。
2. 対象アプリに書き込む前に、書き込み先を利用者へ説明する。
3. ReviewCompass 配布物ディレクトリと対象アプリ root を混同しない。
4. API key、token、password などの秘密値をファイルへ書き込まない。
5. 実行した確認、作成したファイル、残タスクを最後に報告する。

## 2. 最初に確認すること

利用者から次を確認する。

| 項目 | 確認内容 |
| --- | --- |
| 起動パターン | パターン 1、2、3 のどれで進めるか。 |
| 操縦 LLM | この設定作業と以後の運用をどの LLM で行うか（Claude Code か Codex CLI か。それ以外の LLM の場合は §11 のフォールバックに従う）。review-run の既定 variant 選択（§11）に使う。 |
| ReviewCompass 配布物ディレクトリ | ReviewCompass の配布物が置かれている場所（絶対パス）。 |
| 対象アプリ root | ReviewCompass を適用する対象アプリの root。未定なら対象アプリへは書き込まない。 |
| 初期設定の範囲 | 配布物単体確認までか、対象アプリ側設定まで行うか。 |
| API 秘密値の渡し方 | 環境変数など、配布物外の方法で渡すこと。 |
| hook 導入 | commit／push の事前検査 hook を導入するか（強く推奨、§10）。見送る場合は利用者の明示判断として完了報告に記録する。 |

不足している情報がある場合は、推測で進めず、利用者に確認する。

## 3. パターン別の進め方

### 3.1 パターン 1：ReviewCompass 配布物側で起動して対象アプリも設定する

このパターンでは、現在の作業ディレクトリが ReviewCompass 配布物ディレクトリであることを確認する。対象アプリ root は利用者から指定される。

進め方：

1. ReviewCompass 配布物に `tools/`、`runtime/`、`templates/`、`config/api-settings.yaml` があることを確認する。
2. 対象アプリ root が存在することを確認する。
3. 対象アプリ root に `.reviewcompass/` があるか確認する。
4. `.reviewcompass/` がなければ、作成前に利用者へ説明する。
5. 対象アプリ側の設定テンプレートを作成または確認する。
6. 入口の合流（§8）と hook 導入（§10、強く推奨）を行う。
7. workflow next、review-run smoke、conformance-evaluation など、利用者が選んだ初期確認へ進む。

### 3.2 パターン 2：対象アプリ側で起動して ReviewCompass 配布物を指定する

このパターンでは、現在の作業ディレクトリが対象アプリ root であることを確認する。ReviewCompass 配布物ディレクトリは利用者から指定される。

進め方：

1. 現在のディレクトリが対象アプリ root か確認する。
2. ReviewCompass 配布物ディレクトリに `tools/`、`runtime/`、`templates/`、`config/api-settings.yaml` があることを確認する。
3. 対象アプリ root に `.reviewcompass/` があるか確認する。
4. `.reviewcompass/` がなければ、作成前に利用者へ説明する。
5. 対象アプリ側の `.reviewcompass/config.yaml` を作成または確認する。
6. 入口の合流（§8）と hook 導入（§10、強く推奨）を行う。
7. 配布済み ReviewCompass のツールを使い、対象アプリ側の workflow next を確認する（feature 未確定なら `feature_definition_required` の案内が返る。§9）。

通常利用を始める場合は、このパターンを基本とする。

### 3.3 パターン 3：配布物側だけ先に確認し、対象アプリ側設定は後で行う

このパターンでは、まず ReviewCompass 配布物ディレクトリだけを確認する。対象アプリ root が未定、または利用者がまだ対象アプリへ書き込みたくない場合は、この範囲で止める。

配布物側で確認すること：

1. `tools/`、`runtime/`、`templates/`（入口・hook・feature-dependency の雛形を含む）、`config/api-settings.yaml` があること。
2. `config/api-settings.yaml` に秘密値が含まれていないこと。
3. `runtime/config/config.yaml.template` があること。
4. `.reviewcompass/guidance/INITIAL_SETUP_LLM_GUIDE.md` があること。
5. ReviewCompass の Python ツールを実行できる環境か確認すること。

対象アプリが決まったら、対象アプリ root で新しい LLM セッションを立ち上げ、パターン 2 として初期設定を続ける。

## 4. 対象アプリ側に作成または確認するもの

対象アプリ側では、次を確認する。

| パス | 扱い |
| --- | --- |
| `.reviewcompass/` | 対象アプリ側の ReviewCompass 作業領域。なければ作成候補。 |
| `.reviewcompass/config.yaml` | 対象アプリ固有の設定。テンプレートから作成候補。 |
| `.reviewcompass/specs/` | 仕様、設計、タスク、review-run 記録の置き場。 |
| `.reviewcompass/AGENT_ENTRY.md` | LLM セッションの入口規律。テンプレートから実体化する（§8）。 |
| `.reviewcompass/feature-dependency.yaml` | feature 一覧・開発順・依存の定義。feature-partitioning 承認後に作成する（§9）。 |
| `CLAUDE.md`／`AGENTS.md` | 既存入口ファイルへの参照 1 行の追記（§8）。 |
| `.claude/`／`.codex/` | commit／push 事前検査 hook と設定（§10、強く推奨）。 |

既存の `.reviewcompass/` がある場合は、上書きせず、内容を確認してから進める。

## 5. 秘密値の扱い

`config/api-settings.yaml` や対象アプリ側の `.reviewcompass/config.yaml` に API key、token、password などを書き込まない。

秘密値が必要な場合は、利用者に次のように説明する。

```text
API key は設定ファイルに書かず、環境変数など配布物外の方法で渡してください。
この初期設定では、秘密値そのものは表示・保存しません。
```

## 6. 初期確認の最小セット

対象アプリ側まで設定する場合は、最低限次を確認する。

1. ReviewCompass 配布物ディレクトリを参照できる。
2. 対象アプリ root に書き込みできる。
3. 対象アプリ側の `.reviewcompass/` の作成または既存確認が済んでいる。
4. 対象アプリ側の `.reviewcompass/config.yaml` の作成または既存確認が済んでいる。
5. 入口の合流（§8）が済んでいる。
6. workflow next を確認できる（feature 未確定の段階では `feature_definition_required` の案内が返ることを確認する）。
7. review-run 記録の出力先を対象アプリ側に指定できる。

## 7. 完了報告

初期設定が終わったら、利用者へ次を報告する。

1. 選択した起動パターンと操縦 LLM。
2. ReviewCompass 配布物ディレクトリ。
3. 対象アプリ root。
4. 作成または変更した対象アプリ側ファイル。
5. hook 導入の有無（見送った場合は、利用者の明示判断であることと理由）。
6. 実行した確認。
7. 未実施の確認。
8. 次に行うべき作業。

対象アプリへ何も書き込んでいない場合は、そのことを明示する。

## 8. 入口の合流（AGENT_ENTRY の実体化と参照 1 行）

対象アプリで複数の LLM（Claude Code、Codex CLI）を同じ規律で使うための入口を作る。

1. 配布物の `templates/entry/AGENT_ENTRY.template.md` を、対象アプリの `.reviewcompass/AGENT_ENTRY.md` として実体化する。冒頭の記入欄（実体化日、実体化元の配布物）と §2 の「配布物の場所」（**絶対パス**）を記入する。
2. 既存の入口ファイルへ、利用者承認のうえ参照 1 行を末尾に追記する。追記の前に、書き込み先・挿入する行・挿入位置を利用者へ提示する。書き込むのは次の枠内の文字列**だけ**である（枠外の説明文を書き込まない）。

   `CLAUDE.md` へ追記する 1 行：

   ```text
   @.reviewcompass/AGENT_ENTRY.md
   ```

   `AGENTS.md` へ追記する 1 行：

   ```text
   ReviewCompass を使う作業では、最初に `.reviewcompass/AGENT_ENTRY.md` を読み、その規律に従う。
   ```
3. 入口ファイルが存在しない場合は、その 1 行だけの新規ファイルを作る（これも承認のうえ）。同じ行が既にある場合は何もしない。既存の記述は変更しない。
4. 既存入口の規律と AGENT_ENTRY の規律が衝突している場合（例：既存入口が「commit は自動で実行してよい」と指示しているが、AGENT_ENTRY §5 は利用者の明示承認を求める、というように両立しない指示）は、作業を進めず利用者へ提示する。優先順位は自動で決めず、利用者判断で AGENT_ENTRY 側を調整する。
5. 対象アプリの `.gitignore` へ、ReviewCompass ツールの実行時生成物の除外 1 行を利用者承認のうえ追記する（除外がないと、2 回目以降の `next` がツール自身の実行記録を未検証の文書変更として誤検出し、`post_write_verification` を返し続ける）。実行時生成物（検査ログ・effective prompt・commit 承認レコード）は `.reviewcompass/runtime/` 区画に集約されている（2026-06-12 配置規約 PLC-DEC-004 反映。旧 3 パスの個別除外は不要になった）。

   ```text
   .reviewcompass/runtime/
   ```

## 9. feature 一覧の立ち上げ

対象アプリの workflow 管理は、`.reviewcompass/feature-dependency.yaml` の `feature_order` キーに基づいて動く。

1. feature 一覧が未確定の段階では、`next` は `feature_definition_required` を返し、intent と feature-partitioning の実施を案内する。これはエラーではなく正常な立ち上げ状態である。
2. feature-partitioning の提案には、機能ごとの依存の主張と理由、順序の導出を必須で含める（人が根拠を検討できるようにする）。
3. 承認された分割結果を、配布物の `templates/specs/feature-dependency.yaml.template` から実体化した `.reviewcompass/feature-dependency.yaml` に記録する。依存される機能を先に並べる。
4. `feature_order` が `depends_on` と矛盾する場合（依存先が後ろ、依存先が一覧にない、循環依存）、`next` は理由つきの逸脱を返す。

## 10. hook 導入（強く推奨）

commit／push の事前検査 hook を対象アプリへ導入する。LLM が規律を読み忘れても、不可逆操作だけは機械が止める防衛線になる。初期設定の標準手順として導入し、見送る場合は利用者の明示判断として完了報告に記録する。

1. 配布物の `templates/hooks/pre-bash-precheck.sh.template`、`templates/hooks/session-record-capture-current-on-todo.sh.template`、`templates/hooks/session-record-promote-previous-draft.sh.template` のプレースホルダを**絶対パス**へ置換する。
   - `{{REVIEWCOMPASS_PYTHON}}`：依存（PyYAML 等）導入済みの Python 実行系
   - `{{REVIEWCOMPASS_DIR}}`：配布物 root
2. 置換後のファイルを、対象アプリの `.claude/hooks/pre-bash-precheck.sh` と `.codex/hooks/pre-bash-precheck.sh` の両方へ同一内容で複製する。同名の既存ファイルがある場合は上書きせず、既存内容と置換後の内容を利用者へ提示して扱いを確認する。
3. 置換後の `session-record-capture-current-on-todo.sh.template` と `session-record-promote-previous-draft.sh.template` は、対象アプリの `.codex/hooks/` に配置する。同名の既存ファイルがある場合は上書きせず、既存内容と置換後の内容を利用者へ提示して扱いを確認する。
4. `templates/hooks/claude-settings.json.template` と `templates/hooks/codex-hooks.json.template` から、`.claude/settings.json` と `.codex/hooks.json` を作る。いずれも既存ファイルがある場合は上書きせず、hooks キーだけを既存へ合流させる（合流して書き込む内容を、書き込み前に利用者へ提示する）。
5. 静的チェック：複製した hook ファイルに未置換トークン（`{{`）が残っていないこと、置換先のパスが実在すること、`jq` が利用できることを確認する。
6. Codex 側の環境設定：Codex の非 managed command hook は、配置しただけでは実行されない。Codex の GUI 設定画面または CLI の `/hooks` で、対象アプリのプロジェクト hook が認識されていることを確認し、利用者が内容を確認したうえで信頼する。未信頼のままでは hook 一覧に出ても Active 0 / review 待ちになり、`PreToolUse` も `PostToolUse` も実行されない。hook ファイルや `.codex/hooks.json` を変更した場合は、定義 hash が変わるため再度 review / trust が必要になる。
7. Codex の現セッション下書き hook は `PostToolUse` に登録し、`TODO_NEXT_SESSION.md` の内容 hash が前回保存時から変わった場合だけ、現セッション rollout を `.reviewcompass/runtime/session-record-drafts/codex-<session_id>.md` へ下書き保存する。下書き先はテスト時に `RC_SESSION_DRAFT_DIR` で差し替えられる。現セッション途中版を `.reviewcompass/evidence/sessions/` と `docs/sessions/` へ直接作らない。`UserPromptSubmit` は発話ごとに呼ばれ得るため使用しない。動作確認では、対象アプリの `.reviewcompass/runtime/session-record-capture-current-on-todo.jsonl` を確認する。`todo_changed`、`selected`、`drafted`、`draft_failed`、`todo_unchanged`、`baseline_recorded` などが出る。`ignored_event` が出た場合は、`PostToolUse` 以外へ誤登録されているため hook 設定を修正する。
8. Codex の前セッション正式化 hook は `SessionStart` に matcher = `startup|resume` で登録し、現 `session_id` と異なる runtime 下書きを新しい順に確認して、検証できた最初の 1 件を正式 2 層記録へ昇格する。正式化前に下書き frontmatter `source_sha256` と現在の元 rollout の sha256 を比較し、一致した場合だけ昇格する。不一致なら `previous_draft_in_progress`、検証不能なら `previous_draft_unverifiable` を記録し、次候補へ進む。複数の終了済み下書きが溜まっている場合も、この hook が 1 回の `SessionStart` で昇格するのは 1 件だけであり、残りは次回 `SessionStart` または明示 backfill の対象とする。動作確認では、対象アプリの `.reviewcompass/runtime/session-record-promote-previous-draft.jsonl` を確認する。`selected` と `promoted` があれば正式化成功、`missing_jq` は jq 不在、`no_current_session_id` は current session_id 不在、`no_cwd` は cwd 不在、`no_draft_dir` は下書きディレクトリ不在、`no_previous_draft` は昇格対象なし、`previous_draft_in_progress` は下書き作成後に rollout が伸びた可能性があるため安全側でスキップ、`previous_draft_unverifiable` は hash 確認情報不足、`no_promote_tool` は昇格 helper 不在、`promote_failed` はその他の昇格失敗である。`Stop` は turn scope のためセッション終了 hook として使わない。
9. TODO を更新しないセッション、クラッシュ、hook 失敗、または Codex の `session_id` が取れない場合は、自動 fallback を追加せず、終了済みの対象 rollout を指定して `tools/session-record-backfill.py --session <jsonl> --source codex` を明示実行する。
10. 復旧手順：hook が「hook 設定不備」を理由に拒否する場合は、プレースホルダの置換値を確認して再置換する（テンプレートから作り直してよい）。Codex で hook が発火しない場合は、まず GUI 設定または `/hooks` で対象 hook が信頼済みか確認する。

## 11. 操縦 LLM 別の既定 variant

review-run の variant（モデルの組）は、起草者（操縦 LLM）と検証者の独立を保つため、操縦 LLM に応じた既定を使う。

| 操縦 LLM | 3 役 review-run の既定 | 小規模 1 体検証の既定 |
| --- | --- | --- |
| Claude Code | 接尾辞なしの `*_independent_3way` 系 | `post_write_verification_google`（共通） |
| Codex CLI | `*_independent_3way_codex_operator` 系 | 同上（共通） |

proxy_model（人の判断を代行させる場合のモデル）も、操縦 LLM と別系列のモデルを選ぶ。

上記以外の LLM で操縦する場合は、独断で進めず利用者に確認し、「起草者（操縦 LLM）と同系列のモデルを反証役・判定役・単独検証役に置かない」という独立性の原則に従って variant を選ぶ。その操縦 LLM 向けの既定 variant の追加は、第3者配布時の再検討事項とする。

