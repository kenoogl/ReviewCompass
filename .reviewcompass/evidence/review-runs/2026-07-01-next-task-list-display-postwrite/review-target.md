# Post-write Review Target

criteria_id: next_task_list_display_guidance
phase: post_write_verification
generated_at: 2026-07-01T00:27:34.773214+00:00

## Change Summary

completed状態の完了報告で次タスク候補を5件ほど、短い説明つきで表示する規律へ変更する。

## Review Question

利用者合意どおり、completed状態の次タスク表示が5件ほどの説明つき候補リストになっており、1件表示は明示された場合だけに限定され、next --jsonのcompleted解釈やbacklog candidate確認規律と矛盾していないか。

## Target Files

- .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md sha256=49044ad500177cd2bd401ebce77b0b8de88293d570c5bdeaa319614d1b01ca1f
- .reviewcompass/guidance/WORKFLOW_NAVIGATION.md sha256=f264a762f6bde2e6a2702a5c9219d89b611ced5328be4db65e66ccba23a4c269

## Source Materials

### .reviewcompass/backlog/plans/plan-2026-07-01-next-task-list-display.yaml

content_mode: full_text
content_sha256: 681f634ab29b2cade2040d44beefaabde5574f02bb4e4ac5f975dbe83e489191

```text
schema_version: reviewcompass-backlog-item-v1
id: plan-2026-07-01-next-task-list-display
kind: plan
title: Show completed-state next-task candidates as a short list
status: completed
source_unit_id: main-completed
created_at: '2026-07-01T00:00:00+09:00'
completed_at: '2026-07-01T00:00:00+09:00'
index_path: .reviewcompass/backlog/index.yaml
provenance:
  created_by: llm
  source_ref: conversation:user:次タスクの表示が期待していたものとは違う
  reason: >
    completed 状態の完了報告で次タスクを 1 件だけ示すと、利用者が期待する
    候補選択の導線にならないため、候補を 5 件ほど説明つきで表示する規律へ
    修正する。
summary: >
  `next --json` が completed の場合、通常 workflow 上の次 action はないが、
  完了報告では `TODO_NEXT_SESSION.md` と backlog の candidate 状態を照合し、
  次に選べる作業候補を 5 件ほど、短い説明つきで表示するように規律を更新する。
related:
  - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md
  - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
  - TODO_NEXT_SESSION.md
remaining_work:
  - id: NTL-1
    title: Clarify completed-state next-task list display
    status: completed
    tasks:
      - SESSION_WORKFLOW_GUIDE.md の completed 時の次タスク取得規律を、候補 5 件ほどのリスト表示に変更する。
      - 1 件表示は、利用者が明示的に 1 件だけを求めた場合に限る。
      - WORKFLOW_NAVIGATION.md の completed 節も、候補提示は選択肢リストであることを補足する。
    acceptance:
      - completed 状態の完了報告で、次候補を 5 件ほど短い説明つきで表示する規律になっている。
      - 候補は `TODO_NEXT_SESSION.md` の推奨順を起点にし、backlog で `status: candidate` を確認してから表示する。
      - 候補は開始済み作業ではなく、利用者が次に選べる作業として説明される。
    note: >
      SESSION_WORKFLOW_GUIDE.md の completed 時次タスク取得規律を 5 件ほどの
      説明つきリスト表示へ変更し、WORKFLOW_NAVIGATION.md の completed 節から
      表示件数と候補確認規律を参照するようにした。
non_goals:
  - '`next --json` の機械状態を変更しない。'
  - backlog 候補の自動開始はしない。
  - '`TODO_NEXT_SESSION.md` の候補順そのものは変更しない。'
decisions: []
```

### .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md

content_mode: full_text
content_sha256: 49044ad500177cd2bd401ebce77b0b8de88293d570c5bdeaa319614d1b01ca1f

```text
# SESSION_WORKFLOW_GUIDE：セッション運営ガイドライン

最終更新：2026-06-10（現行のセッション運営契約として整理）

本文書は ReviewCompass の開発セッションを確実に回すための運用ガイドラインである。作業開始、レビュー、利用者判断、コミット、完了報告の共通手順を定める。

本文書は運用文書（`docs/operations/` 配下）であり、ReviewCompass の実行時手順を定める。仕様・設計・タスクの正本と矛盾する場合は、該当正本を確認し、必要に応じて reopen 手続きに乗せる。

## 1. セッション開始時の必読フロー（5 分以内）

セッション開始時は **作業着手前に必ず**次を順番に確認する。記憶や前回会話だけを根拠に作業へ入らない。

### 1.1 必読 5 件

順序は重要：

1. **`TODO_NEXT_SESSION.md`**（最新進捗）
   - 前セッション末尾の到達点、次の作業候補、未消化所見
   - 「§0 重要事項」「§1 起動手順」「§3 次の作業候補」を最低限読む
   - 直近の `docs/sessions/session-*.md` も併読し、TODO に圧縮された経緯の詳細を確認する

2. **`.reviewcompass/guidance/WORKFLOW_NAVIGATION.md`**（次 action 判定）
   - `tools/check-workflow-action.py next --json` の読み方
   - 判定点ごとの required disciplines / required inputs / effective prompt の扱い

3. **`.reviewcompass/guidance/WORKFLOW_PRECHECK.md`**（機械判定の入口）
   - `spec-set`、`commit`、`push`、`next`、`reopen-start` の実行前条件
   - 機械判定で停止した場合の扱い

4. **`learning/workflow/carry-forward-register/reviewcompass-import.yaml`**（持ち越し所見の正本）
   - 機能横断波及所見の未消化件数と内容を把握
   - 正本と履歴 source を混同しない

5. **`docs/extraction-mapping.md`**（抽出進捗）
   - 各機能の状態（未着手／抽出中／抽出済／確認済）
   - 機能ごとの実施履歴

### 1.2 確認後の git 状態把握

- `git log --oneline -10`：直近のコミット履歴
- `git status`：未コミット変更の有無

### 1.3 ワークフロー上の現在位置の確認

- 現在どのフェーズか（intent ／ requirements ／ design ／ tasks ／ implementation）
- 現在どの段か（drafting ／ triad-review ／ review-wave ／ alignment ／ approval の 5 段）
- 残機能と消化予定所見

## 2. ワークフロー段の役割と順序

### 2.1 全体構造

```
intent 層（人間担当）
  ↓
機能分離
  ↓
requirements 段：drafting → triad-review → review-wave → alignment → approval
  ↓
design 段：drafting → triad-review → review-wave → alignment → approval
  ↓
tasks 段：drafting → triad-review → review-wave → alignment → approval
  ↓
implementation 段：drafting → triad-review → review-wave → alignment → approval
```

各フェーズは drafting／triad-review／review-wave／alignment／approval の 5 段で進める。

### 2.2 各段の役割（責務分離後）

- **drafting**：各機能の草案作成のみ。1 機能ずつ独立に進める。actor=llm（または human）。requirements／design／tasks の drafting は文書起草を意味する。implementation の drafting は文書起草ではなく、tasks.md に従ったテストと実装コードの生成を意味する。
- **tasks drafting の粒度**：tasks 段の drafting では、対象機能の設計書 §14 要件追跡表（Req 受入単位 × 担当タスク単位）を骨格として tasks.md を作成する。tasks.md は implementation drafting へ直接入れる粒度で書く。各タスクには、実装対象ファイル、最初に書く失敗テスト、実装順序、完了条件、検証コマンド、禁止事項、停止条件を含める。implementation-plan.md や implementation-drafting.md のような別の実装前計画文書を正本成果物として要求しない。
- **triad-review**：機能内の 3 役レビュー（主役・敵対役・判定役）と機能内対処の実施。手動 dogfooding または subagent_mediated（サブエージェント仲介方式）で実施。actor=llm
- **review-wave**：複数機能を横断する複数ラウンドレビュー。機能横断波及所見と同根所見（異なる機能で同じ性格の所見が独立に発見された組）を集約し、一貫した対処方針で全該当機能の仕様文書に反映する
- **alignment**：LLM 自動判定による整合確認段（actor=llm）
- **approval**：人間承認段（actor=human）。proxy_model は approval 段の代行主体ではなく、review-run 後の重要件判断だけを代行できる

drafting と triad-review を別段にする理由は、誰が何をしたかを段単位で明確に記録し、草案作成者と判定者の分離を機械検査可能にするためである。

<a id="vertical-intent-transfer-review"></a>

### 2.2.1 上流意図伝達の必須検査

各 phase の triad-review／review-wave／alignment では、対象 phase の成果物だけでなく、上流成果物または上流判断材料からの意図伝達を必須検査項目とする。review prompt は、少なくとも「上流の目的・責務境界・受入条件・禁止事項が、対象成果物へ欠落・弱体化・逸脱・未根拠追加なく引き継がれているか」を問わなければならない。

- **requirements review**：`上流判断材料 → requirements.md` を確認し、reopen 分類根拠、利用者判断、計画メモ、設計メモなどの目的・責務境界・受入条件・禁止事項が要件へ欠落なく落ちているかを検査する。design.md / tasks.md は参照資料であり、審査対象ではない
- **design review**：`requirements.md → design.md` を確認し、要件の目的・境界・受入条件が設計へ欠落なく落ちているかを検査する
- **tasks review**：`requirements.md → design.md → tasks.md` を確認し、要件と設計の意図が implementation-ready なタスク粒度へ落ちているかを検査する
- **implementation review**：`requirements.md → design.md → tasks.md → implementation` を確認し、実装がタスクだけでなく上流意図から逸脱していないかを検査する

review prompt は、review target / source materials / out of scope を明示する。審査対象は現在 phase の成果物に限定し、source materials は背景・意図伝達確認のための参照資料として扱う。下流 phase の成果物が source materials に含まれる場合でも、その correctness を現在 phase の review で判定してはならない。

source materials をパス名だけで列挙してはならない。縦方向監査の review prompt には、判断に必要な上流本文または要点抽出を、モデルが推測せず読める形で含める。要点抽出を使う場合は、少なくとも上流の目的、責務境界、受入条件、禁止事項、未確定事項、対象 phase へ引き継ぐべき判断を分けて記録する。上流資料を読んでいない場合は review-run を開始してはならない。prompt 内で上流資料の中身が確認できない場合も review-run を開始してはならない。

tasks review では、単に tasks.md の粒度や項目数を見るだけでは不十分である。たとえば T-016〜T-019 を審査する場合は、Requirement 13〜16 の意図が design.md の設計判断を経由して、欠落・弱体化・勝手な追加なしに implementation-ready な作業単位へ落ちているかを必須で確認する。

### 2.3 段の進め方の規律

- **drafting 段の草案完成** → 当該機能の triad-review 段に進む（機能単位で逐次進行）
- **triad-review 段で 3 役レビューと機能内対処** を完了 → 当該機能の drafting／triad-review がそろう
- **全機能で drafting ＋ triad-review を完了** してから review-wave に進む（部分的に review-wave を始めない）
- **review-wave の所見を消化** してから alignment に進む
- **alignment で LLM 自動判定** を通過してから approval に進む
- **approval で利用者の明示承認** を得てから次フェーズに進む

### 2.4 「次の機能の drafting に進むべき」状況の判断

triad-review 段で 3 役レビューを行った所見が **機能横断の波及所見**だった場合、当該機能の triad-review で対処せず、carry-forward register に持ち越して **次の機能の drafting に進む**。

## 3. 修正案件の波及種別と処理段

### 3.1 用語の使い分け

両用語は **対象方向が異なる正当な技術用語** であり、優劣はない：

- **遡及（そきゅう）**：**上流フェーズへの影響**。下流段の作業で発見された問題が、上流段（過去フェーズ）の修正を要するもの。例：実装段で発見した不整合が要件段の書き直しを要する
- **波及（はきゅう）**：**同フェーズ内の他機能（フィーチャー）への影響**。ある機能のレビューが別機能との不整合を露出させるもの。例：foundation 要件の修正が runtime／evaluation 要件にも影響する

所見を分類するときは、上流フェーズへ戻る必要があるか、同フェーズ内の他機能へ広がるかを分けて判断する。

### 3.2 修正案件の 4 種別（＋ 2 補助種別）

レビューで露出する所見は次の種別に分類する：

| 種別 | 内容 | 例 |
|---|---|---|
| **機能内対処** | 当該機能の仕様修正のみで完結 | 表現修正、機能内の語彙不統一訂正 |
| **波及（同フェーズ・横方向）** | 同フェーズ内の他機能の仕様修正も必要 | A-001：foundation 要件と runtime 要件の `not_run` 欠落 |
| **遡及（上流フェーズ・縦方向）** | 上流フェーズの仕様修正が必要 | 設計段で「要件段の Req 6 受入 8 に矛盾あり」と発見 |
| **遡及 ＋ 波及（縦 ＋ 横）** | 上流フェーズの複数機能に影響 | 設計段で発見した要件段の不整合が複数機能の要件文書に波及 |

補助種別：

- **leave-as-is（修正不要）**：判定役が「修正不要」と判断したもの、対処せず記録のみ
- **延期**：「将来フェーズで対処」と判定役が明示したもの（例：F-004 の配置時対処）

### 3.3 種別ごとの処理段と方法

#### (a) 機能内対処

- **発見されるタイミング**：drafting 段（起草者の自己発見）／ triad-review 段（3 役レビュー）
- **処理する段**：当該機能の **triad-review 段** で対処（drafting に戻して草案修正、または triad-review 段内で直接修正）
- **方法**：当該機能の仕様文書を直接修正
- **次段への進行**：当該機能の triad-review 段が `completed` 状態になってから次機能へ
- **記録先**：レビュー記録（`.reviewcompass/specs/<機能>/reviews/<日付>-<種別>.md`）の §4 統合節に「対処済み」と記録

##### (a-1) must-fix 所見の対処手順

triad-review 段で判定役が must-fix と判定した所見の対処は、起草者（LLM または人間）が独自判断で仕様文書を修正することを禁ずる。利用者と必ず議論し、各所見の対処方針を 1 件ずつ平易な日本語で説明して合意を得てから反映する。

**手順**：

1. must-fix 所見を 1 件ずつ取り上げる。複数所見が論理的に連動する場合は連動単位でまとめる（例：F-001 と F-007 が同一事象を別観点で扱う場合）
2. 各所見について、対処方針の提案を次の構造で平易に説明する：
   - その判断が必要になった経緯（要件文書や上流文書からの導出）
   - 候補案の列挙（必ず複数）
   - 各候補案の利点と弱点
   - **後段で発生し得る問題の深掘り**：下流仕様（他機能の design／tasks／implementation）、対象アプリへの配置可能性、機械検証時の挙動、実装フェーズの運用、将来の拡張性
   - 推奨案とその根拠
3. 「現状維持」を推奨する場合も、現状維持の弱点を検証してから示す
4. 一括処理（複数論点を一気に決着）を避け、各論点を個別に深掘りする
5. 利用者の判断を得てから、仕様文書を 1 件ずつ Edit で修正する
6. 各修正後に grep または Read で機械的に照合し、反映を確認する
7. レビュー記録（reviews/...）の §4 統合節に「対処方針・利用者承認の根拠・反映箇所」を記録する

**深掘りの具体内容**（推奨案を提示する際に必ず想定する事項）：

- foundation 機能の場合：対象アプリへの配置可能性、配布対象外資産との分離、リポジトリ内資産の規則との整合
- 値域・語彙の固定：将来拡張時の改訂コスト、機械検証時の不正値検出
- 責務境界：foundation と runtime（または他機能）の責務分離、上流が下流の実装方針に踏み込まない原則
- 不変性：成果物の追記性、生証拠は不変の原則
- 依存関係：他機能が当該仕様を取り込む際の参照可否

**禁則**：

- 利用者と議論せずに must-fix 所見の対処内容を独自に確定する
- 「現状維持を推奨」と表層的に提案する（弱点検証を欠く）
- 候補案を 1 つしか提示しない（代替案との比較を欠く）
- 後段影響を想定しない推奨

<a id="3.3-a-2"></a>

##### (a-2) review-run 後の proxy_model 判断代行手順

API 経由の review-run 後に、人間の個別判断を proxy_model が代行する場合も、メインセッション LLM が重要件を独自に確定して実装へ進むことを禁ずる。proxy_model 代行は「人間判断を省略する」ものではなく、判断主体を別モデルへ移す運用である。

**proxy_model 判断依頼前の利用者提示ゲート**：

API review-run が完了したら、proxy_model 判断依頼、実装修正、spec.json 更新、フェーズ移行のいずれにも進む前に、メインセッション LLM は次を利用者へ提示して停止する。この提示ゲートを完了する前に proxy_model を呼び出してはいけない。

1. 使用 variant 名
2. role ごとの path／provider／model（例：primary／adversarial／judgment の割当）
3. モデル別 raw 結果概要（parse 状態、所見数、severity 内訳、raw path）
4. 同根所見クラスタの一覧
5. `must-fix`／`should-fix`／`leave-as-is` の三段階トリアージ案
6. `must-fix` 候補ごとの平易な説明、候補案、各案の利点と弱点、後段影響、推薦案
7. proxy_model に判断させる場合の対象 finding／cluster、判断範囲、不可逆操作（commit／push／spec.json 更新／フェーズ移行）を含まないこと

variant が未確定、または role 割当が曖昧な場合は review-run を開始しない。既定 variant が CLI 経路を含む等、実行環境と合わない場合は、設定ファイルを読んで候補 variant と role 割当を利用者へ説明し、選択理由を review-run 記録に残す。

**役割分担**：

1. メインセッション LLM は raw レビューを集約し、三段階トリアージの下書きを作る。parsed YAML だけでなく raw response も読み、同根所見をまとめ、`must-fix` ／ `should-fix` ／ `leave-as-is` の候補を作る
2. メインセッション LLM は重要件ごとに、平易な問題説明、候補案、各案の利点と弱点、後段影響、推薦案を作る
3. proxy_model は重要件の採用案・判断理由・最終ラベルを決定する。実装は担当しない
4. メインセッション LLM は proxy_model の raw response を保存し、`decisions/<suffix>.yaml`（重要件ごとの裁定 file。`<suffix>` は `<model>-<role>-<連番>`）と `proxy-approval.yaml` に構造化する
5. 機械ガードは proxy decision の充足を検査する。未判断、raw 欠落、候補案欠落、採用案欠落、判断理由欠落、triage 最終ラベルとの不一致があれば実装へ進まない
6. メインセッション LLM は機械ガード通過後、採用された修正だけを TDD で実装する
7. コミット・プッシュ・spec.json 更新・フェーズ移行は人間の明示承認を要求する。proxy_model はこれらの不可逆操作を代行しない

**重要件の判定閾値**：

- `must-fix`、`ERROR`、`CRITICAL` は必ず重要件として扱う
- `should-fix` でも、上流仕様、データ契約、機械ガード、証跡保持、ワークフロー権限境界、複数モデルの同根指摘に関わるものは重要件として扱う
- 同根指摘とは、複数モデルの所見が同じ対象ファイル・同じ出力契約・同じ機械ガード・同じ証跡・同じ原因に触れているものをいう。表現が異なっても、対象または原因が一致する場合は同根として扱う
- 正本削除、機械ガード削除、重要件閾値の引き下げ、承認証跡の削除、検証対象範囲の縮小は、コミット等と同じく人間の明示承認を要する不可逆操作として扱う
- 判断に迷うものは重要件側に倒し、proxy_model 判断または人間判断へ回す

**proxy_model への入力証跡**：

- proxy_model へ渡す判断材料には、メインセッション LLM の要約だけでなく、元 review raw への参照または抜粋を必ず含める
- proxy_model への判断プロンプト（review-run 直下に保存）を作成する前に、[[llm-as-judge-prompting]] の手順（材料揃え → 問い設計 → 選択肢なし分析）でプロンプトを設計する
- 判断プロンプト（review-run 直下。既定名 `proxy-adjudication-prompt.md`、実行時に指定可）に、元 review raw 参照、問題説明、候補案セット、推薦案、判断してほしい最終ラベルを保存する
- `decisions/<suffix>.yaml`（重要件ごとの裁定 file。`<suffix>` は `<model>-<role>-<連番>`）には、`candidate_options`、`source_raw_paths`、`decision_prompt_path`、採用案、棄却案理由、判断理由、最終ラベルを保存する
- proxy_model が元 review raw を読めない形の判断材料しか受け取っていない場合、その decision は実装着手の承認証跡として扱わない
- 現行の軽量ガードは、proxy_model_id の文字列一致、decision file の finding_id 一致、final_label 一致、prompt/raw/候補案証跡の存在を検査する。API 署名や暗号学的な生成元証明は将来課題とする

**証跡配置**：

- `raw/`：各モデルの生応答
- `triage.yaml`：メインセッション LLM による三段階トリアージ
- `proxy-adjudication-prompt.md`（既定名。review-run 直下、実行時に指定可）：proxy_model に渡した判断材料
- `proxy-adjudication-response.txt`（既定名。review-run 直下、実行時に指定可）：proxy_model の生応答
- `decisions/<suffix>.yaml`：重要件ごとの採用案、判断理由、最終ラベル、棄却案理由
- `proxy-approval.yaml`：実装着手を許可する proxy approval record

**並列化可能な単位**：

- proxy_model への判断依頼は、同根所見クラスタ単位で並列化できる
- TDD 実装は、互いに同じファイルを更新しない実装単位、または入出力契約が独立しているタスク単位で並列化できる
- 共通スキーマ・共通ビルダー・同一ファイルを触る修正は直列で扱う
- 生成物、共有 helper、推移的契約、同じ出力 manifest、同じ traceability 出力を共有する修正は直列で扱う
- 並列実装の統合前に、メインセッション LLM が triage、proxy decision、テスト結果、ファイル差分を再照合する
- 並列処理で新しい判断問題が出た場合、その単位は停止し、proxy_model 判断または人間判断へ戻す
- 承認済み finding の実装中に見つけた未承認の便乗リファクタ、隣接挙動変更、対象外 cleanup は実施しない。必要なら新しい判断問題として停止する

**実装サブ担当 LLM の扱い**：

- 実装サブ担当 LLM は、原則として別スレッドかつ分離 worktree で扱う
- 同じ repo での並列実装は原則禁止し、読み取り調査または差分を残さない確認に限定する
- メインセッション LLM は、対象 finding、proxy decision、触ってよいファイル、期待テスト、禁止事項、停止条件を実装サブ担当へ渡す
- 実装サブ担当は、指定範囲外のファイル変更、判断変更、コミット、プッシュ、spec.json 更新、フェーズ移行を行わない
- 実装サブ担当が新しい判断問題、上流仕様への疑義、許可ファイル外の修正必要性を見つけた場合、その作業単位を停止してメインセッション LLM に戻す

**別スレッド生成物の扱い**：

- 別スレッド・分離 worktree で発生した生成物は、実装差分、検証結果、判断根拠、作業ノイズに分類する
- 実装差分は、メインセッション LLM が確認したうえで本線 worktree への取り込み候補にする
- 検証結果と判断根拠は、必要な要約だけを review-run、session record、または docs/notes に保存する
- 判断に影響した失敗試行、失敗パッチ、途中ログは work_noise から decision_basis へ昇格し、メインセッション LLM が要約または該当箇所を保存する
- 作業ノイズは本線 repo に取り込まない。作業ログ、一時メモ、途中のテスト出力、失敗パッチ案は原則としてサブ worktree 側に閉じる
- 本線へ戻す標準単位は、パッチ、テスト結果サマリ、未解決事項の 3 点とする

<a id="3.3-a-3"></a>

##### (a-3) 操縦 LLM 別の API 既定 variant と独立性原則（本節を正本とする）

セッションを操縦（起草・修正）する LLM と、その成果物を検証する LLM の系列を分離する。
自己レビューによる独立性低下を防ぐための原則であり、利用者承認済み
（設計記録 `docs/notes/2026-06-10-deployment-multi-llm-entry-design.md` §3.6、2026-06-11 個別承認）。
本節がこの原則と既定 variant 選択規則の正本である（仕様への昇格は実アプリ pilot 後に再検討、
MLE-DEC-004、2026-06-12 利用者決定）。

**独立性の原則**：

1. 単独検証役（1 体での post-write 検証など）は、操縦 LLM と別系列を必須とする
2. 3 役構成の adversarial（反証役）と judgment（判定役）は、操縦 LLM と別系列を必須とする
3. 3 役構成の primary（検出役）は、操縦 LLM と同系列を許容する（最終判定を持たず、
   残り 2 役の独立で全体の独立性が保たれるため）
4. proxy_model（人の判断の代行）は、操縦 LLM と別系列を必須とする

**操縦 LLM 別の既定 variant**（実体は `config/api-settings.yaml`）：

- **Claude Code 操縦時**：接尾辞なしの `*_independent_3way` 系
  （post_write_verification／yaml_audit／implementation_review の 3 用途。
  primary=anthropic/claude-sonnet-4-6、adversarial=openai/gpt-5.5、
  judgment=gemini/gemini-3.1-pro-preview）
- **Codex CLI 操縦時**：`*_independent_3way_codex_operator` 系
  （primary=openai/gpt-5.4、adversarial=anthropic/claude-opus-4-8、
  judgment=gemini/gemini-3.1-pro-preview）
- judgment（gemini-3.1-pro-preview）と小規模 1 体検証（`post_write_verification_google`）は
  両操縦で共用し、操縦を切り替えても判定基準の連続性を保つ
- 既存 variant の改名は行わない（規律文書・過去 run 記録・spec からの参照保全）。
  別の LLM が操縦する場合（将来）は同じ原則で役を回転して対応する

対象アプリ向けの同内容の案内は `templates/entry/AGENT_ENTRY.template.md` §10 と
`.reviewcompass/guidance/INITIAL_SETUP_LLM_GUIDE.md` にあり、本節と整合させて保守する。

#### (b) 波及（同フェーズ・他機能への影響）

- **発見されるタイミング**：triad-review 段（3 役が他機能との不整合に気づく）／ review-wave 段（機能横断レビュー）
- **処理する段**：**review-wave 段**（フェーズ終端の機能横断段、全機能の drafting ＋ triad-review 完了後に開始）
- **方法**：
  1. triad-review 段で波及と判定されたら **当該機能では対処せず**、carry-forward register に追記
  2. 「次の機能の drafting」に進む（個別機能の段では対処しない）
  3. 全機能の drafting ＋ triad-review が完了したら、review-wave 段で集約消化
  4. 影響を受ける全機能の仕様文書を一括修正（依存順を守る、例：foundation を先に修正してから runtime）
- **記録先**：`learning/workflow/carry-forward-register/reviewcompass-import.yaml` の各所見項目、消化後は `status: resolved` と `resolution` を更新

#### (c) 遡及（上流フェーズへの影響）

- **発見されるタイミング**：任意の下流段（triad-review／review-wave／alignment／approval のいずれか）
- **処理方法**：[REOPEN_PROCEDURE.md](REOPEN_PROCEDURE.md) の 4 過程手順を起動。当該段の作業を停止し、上流フェーズに戻る
- **手戻り種別判定**：N（intent）／R（requirements）／D（design）／A（tasks）／I（implementation）× 深さ 0〜4 の二次元表記で判定
- **再実施対象決定**：第1過程で trigger_map（再実施対象段の決定表）を参照して決める。actor=human の段（approval 等）に来たら作業を止めて承認待ち
- **記録先**：種別判定の根拠を `docs/reviews/reopen-classification-<日付>.md` に残す、機能単位 spec.json の `reopened` 履歴と `recheck` フラグを更新

#### (d) 遡及 ＋ 波及の組合せ

- **発見されるタイミング**：任意の下流段
- **処理方法**：reopen で上流フェーズに戻り、上流フェーズの review-wave 段で波及所見として集約消化、その後下流に伝播
  1. **第 1 段階**：reopen 手続きで上流フェーズに戻り、影響範囲を特定（trigger_map）
  2. **第 2 段階**：上流フェーズで carry-forward register に波及所見として追記し、当該フェーズの review-wave 段で消化
  3. **第 3 段階**：上流フェーズの alignment ＋ approval を再実施
  4. **第 4 段階**：下流フェーズの alignment ＋ approval を再実施（trigger_map で連鎖再実施対象として決定）
- **記録先**：reopen 記録 ＋ carry-forward register の両方

#### (e) leave-as-is と延期

- **leave-as-is**：判定役が「修正不要」と判断したもの。対処せず、レビュー記録に判定根拠を残すのみ
- **延期**：将来のフェーズで対処する判定。レビュー記録に延期理由と対処予定フェーズを残し、当該フェーズ着手時のチェックリストに追記

### 3.4 振り分け判断のフロー（triad-review 段で実施）

triad-review 段の判定役は、各所見について次の振り分けを行う：

```
所見発見
  ↓
当該機能の仕様修正のみで完結するか？
  ├── YES → 機能内対処（triad-review 段内で対処）
  └── NO
      ↓
  他機能の仕様修正も必要か？
  ├── YES（同フェーズ内のみ） → carry-forward register に追記、review-wave 段で処理
  ├── YES（上流フェーズに戻る必要あり、単機能） → reopen 手続きを起動
  └── YES（上流フェーズに戻る必要あり、複数機能） → reopen ＋ 上流の review-wave で集約処理
  
別判定：
  ├── 修正不要 → leave-as-is（記録のみ）
  └── 将来フェーズで対処 → 延期（チェックリスト追記）
```

### 3.5 段ごとの露出と処理段の対応表

| 段 | 主に露出する所見 | 当該段内で処理する所見 | 次段に持ち越す所見 |
|---|---|---|---|
| drafting | 起草中の自己発見 | 機能内（草案に直接反映） | なし |
| triad-review | 機能内 ／ 波及 ／ 遡及 | **機能内** のみ | 波及 → review-wave、遡及 → reopen |
| review-wave | 波及（横断ラウンド中の追加発見も） | **波及** | 遡及あり → reopen |
| alignment | 自動判定の不整合検出 | （自動判定が通過するまで前段に戻す） | 遡及あり → reopen |
| approval | 重大見落とし、利用者または別モデルによる指摘 | （承認しない） | reopen で上流戻し |

### 3.6 機能横断波及所見の管理ルール

- 各機能の triad-review 段で発見されたら、即時 carry-forward register に追記
- 追記項目：所見 ID（A-XXX 形式）、検出セッション、波及範囲（影響を受ける機能と仕様箇所）、対処方針、依存関係
- review-wave／alignment／approval の機能横断段着手時、全件を消化対象とする
- 消化後、各所見に「✅ 対処済み（YYYY-MM-DD、要件 review-wave）」ラベルを追加

## 4. サブエージェント方式の運用条件

### 4.1 位置づけ

- メインセッションは草案作成とレビュー結果の取りまとめを担う
- 3 役レビューは、メインセッションから分離された reviewer session または外部 API 検証者で実行する
- review-run の実行形は adapter と provider 設定に従う

### 4.2 モデル割り当て（規律）

3 役（主役・敵対役・判定役）は、メイン LLM から分離した実行主体が担う。メイン LLM は草案作成と三役レビュー結果の取りまとめのみを担い、3 役のいずれにもならない。

各役のモデルは `runtime/config/reviewcompass.yaml` または review-run の provider 設定で指定する。利用者が設定で変更できる。

**モデル能力配分の規律**：

- **主役と敵対役は必ず異なるモデルを使う**（敵対役の独立性確保のため）
- 判定役は主役または敵対役と同じモデルを使うことを許容する
- 敵対役と判定役には、反証生成と責務境界判断を担う十分な能力のモデルを割り当てる

### 4.3 サブエージェント呼び出し時の規律

- **プロンプトに自己完結性を持たせる**：サブエージェントは別 session で、メインの作業文脈を共有しない
- **参照文書の引用は事後検証**：サブエージェントの引用には節番号や参照先の誤りが発生しうる。メインセッションが grep やリンク検査で確認する
- **ファイル書き込みは原則禁止**：読み取りと分析のみ。例外的にレビュー記録の §2 や carry-forward register への追記提案を許容
- **モデル指定**：利用中の adapter が提供する model / provider 指定方法に従う。外部 API 経由では provider 設定を参照する

### 4.4 レビュー記録の必須フィールド

レビュー記録の front-matter に次を必須化：

```yaml
author:
  identity: <adapter_main_session>
  model: <model-id>
  role: drafter
reviewer:
  identity: <adapter_reviewer_session>
  model: <model-id>
  role: final_judgment
  separation_from_author: true
```

`author.identity` と `reviewer.identity` が異名であることを機械検査の対象とする。重要なのは provider 名ではなく、起草者と判定者が分離していることを記録できることである。

### 4.5 mode 値

レビュー記録の `mode` は `subagent_mediated`（正式値）。foundation のレビューモード語彙正本（Requirement 6 受入 6）の 3 値のうちのひとつ。

## 5. 利用者判断が必要な論点の見極め

### 5.1 利用者判断必須の項目

次のいずれかに該当する場合、LLM は単独で確定せず、利用者の明示承認を仰ぐ：

- **正本方針変更**：仕様・設計・タスク・運用規律の意味を変える修正
- **大規模再設計**：既存の責務境界、機械判定、成果物配置を大きく変更する場合
- **機能横断の権限分担**：複数機能にまたがる責務分担の決定（例：A-007 の self-improvement と workflow-management の権限調停）
- **判定境界の判断**：must-fix／should-fix／leave-as-is の境界が曖昧な場合
- **承認・コミット・push・フェーズ移行**：すべて利用者明示承認必須
- **作業の打ち切り・先送りの誘導**：利用者の明示承認なく「続きは次セッションで」等と作業を終了・先送りに誘導しない

### 5.2 LLM が自律的に決められる項目

- **抽出時のクリーニング作業の細部**（機能名置換、自己適用前提除去等）
- **観点 5（検証可能性）の機械判定可能な所見の指摘**
- **レビュー記録の構造化**（front-matter、節構成）

### 5.3 判断の記録規律

利用者判断の結果は次の場所に記録：

- **正本方針変更**：該当する仕様・設計・タスク・運用規律に決定日付付きで記載
- **機能横断対処方針**：carry-forward register の該当所見に対処方針として追記
- **重大論点**：レビュー記録の §1 主役レビュー、§4 統合の「利用者判断履歴」節に記録

### 5.4 セッション記録の作成規律

原則として毎セッション、セッション終了時または重要判断後に `docs/sessions/session-<N>-<YYYY-MM-DD>.md` を作成または更新する。特に、重要な判断・承認・レビュー結果・修正経緯が発生した場合は必須とする。これは会話全文の逐語ログではなく、後で経緯を確認できる要約記録とする。

`<N>` は `docs/sessions/` に存在する既存の最大セッション番号に 1 を加えた番号とする。同日の複数セッションでも番号を進め、同じ番号を再利用しない。
1 session につき 1 ファイルとし、同一 session 内で重要判断が複数回発生した場合は同じファイルへ追記する。重要判断ごとに別番号を消費しない。
並行セッションや未コミット作業により採番が衝突した場合、メインセッション LLM は既存記録・git 状態・未コミット差分を確認し、利用者が採番を確定するまで正式な新規セッション記録を作成しない。採番確定前に記録が必要な場合は、`docs/sessions/drafts/session-<YYYY-MM-DD>-<short-topic>.md` に一時草案を置き、正式番号確定後に `docs/sessions/session-<N>-<YYYY-MM-DD>.md` へ移動する。移動後は draft ファイルを残さず、正式ファイルに草案内容が統合済みであることを確認する。

メインセッション LLM はセッション記録の草案作成責任を持つ。利用者判断の引用・承認範囲・未確定事項に曖昧さがある場合は、記録前に利用者へ確認する。
コンテキスト切れや中断により当該 LLM が記録できない場合、次セッションが草案を引き継ぐ。草案がない場合は、TODO、review-run、approval record、git diff から経緯を再構成して記録する。

最低限、次を記録する：

- このセッションで実施した作業
- 利用者が承認した判断と、その対象
- API レビューや独立検証の結果と三段階トリアージ
- 修正した主要ファイルと検証結果
- 失敗・見落とし・再発防止に必要な気づき
- 次セッションへの引き継ぎ

推奨見出しは既存 session 記録と同型とし、最低限次を含める：

1. サマリ（このセッションでやったこと）
2. 気づき・特筆点
3. コミット一覧（該当する場合）
4. 次セッションへの引き継ぎ

`TODO_NEXT_SESSION.md` は次セッション向けの入口メモであり、詳細な経緯記録の正本ではない。詳細経緯は `docs/sessions/` に残し、TODO には必要な参照だけを置く。

## 6. コミット規律

### 6.1 コミット単位

- **正本文書更新 ＋ 基盤整備**：1〜2 コミット（方針確定、運用ファイル整備）
- **機能ごとに 1 コミット**：仕様文書 ＋ 運用文書 ＋ レビュー記録の 3 ファイル（または schema/template 等の関連ファイル）
- **機能横断段（review-wave／alignment／approval）**：1 コミット（複数機能の小修正をまとめる）

### 6.2 コミット順序

依存マップ順に従う：

1. foundation
2. runtime
3. evaluation
4. analysis
5. workflow-management
6. self-improvement
7. conformance-evaluation

### 6.3 コミットメッセージ規律

- **平易な日本語**：英語技術用語の連発を避け、完全な日本語の文で書く
- **題名**：機能名 ＋ 作業種別（例：「foundation 機能の requirements 抽出と 3 役レビュー」）
- **本文**：作成・更新ファイルの列挙、主な反映内容、機能横断所見の持ち越し有無
- **Co-Authored-By**：利用中の adapter と利用者方針に従う。自動付与を前提にしない

### 6.4 コミット前確認

- `git status` で対象ファイルを確認
- `git diff --cached` で内容確認（必要に応じて）
- `--no-verify` や `--no-gpg-sign` は使わない（規律）

### 6.5 不可逆操作の進行報告最小化

commit、push、spec.json workflow_state 変更、フェーズ移行などの不可逆操作では、利用者が操作を明示指示した後の正常系進行報告を原則として省く。LLM は必要な確認、stage、承認 record、guard、実操作、事後確認を実行してよいが、各内部手順を逐一会話へ説明しない。

途中報告を行うのは、利用者判断または追加承認が必要な場合に限る。例：承認 record の期限切れや対象不一致、precheck failure、post-write / reopen / in-progress による遮断、sandbox escalation が必要な場合、staged 内容が変わり再承認が必要な場合。

commit 中に、staged 内容の確定、承認内容を作り直す、既存 delegation を使い直す、nonce を更新する、といった内部再準備が必要になっても、それ自体を利用者に報告しない。これらは、承認済みの対象範囲内であり利用者判断を要しない通常手順として黙って実行する。コミット対象が増えた、staged 内容が変わった、または再承認が必要になった場合は内部再準備として隠さず、追加判断が必要な停止理由だけを短く報告する。利用者へ報告するのは、作業を続けられない異常、追加判断が必要な WARN / DEVIATION、または成功結果だけとする。

正常完了時の報告は、実行結果だけに絞る。commit なら commit hash、`git status` の clean 性、`next --json` の要点を示す。push なら push 先と結果、`git status` の clean 性を示す。詳細な手順ログ、precheck の全文、stage したファイル一覧、nonce / challenge の値は、利用者が求めた場合または失敗調査に必要な場合だけ示す。

### 6.6 push

push は **利用者明示承認**を仰いでから実行。LLM が自律的に push しない。

## 7. 作業完了時レポート

作業を終えて利用者へ返答するときは、adapter や利用モデルに依存しない会話末尾の運用契約として、最低限次を示す：

- **作業サマリ**：このターンで実施した変更、判断、未変更の範囲
- **検証結果**：実行したテスト、確認コマンド、`post_write_verification` の要否と結果
- **現在状態**：`git status` と `next --json` の要点
- **次タスク**：次に着手すべき具体的な作業、または workflow が要求する次 action

未実施・失敗・承認待ち・保留判断がある場合は、完了扱いにせず明記する。commit、push、workflow_state 更新、spec.json 更新などの不可逆または状態変更を伴う操作は、実際に成功した場合だけ作業サマリに記録する。

`next --json` が `post_write_verification`、`reopen_in_progress`、`resume_in_progress`、`unknown` など `completed` 以外を返している場合、次タスクには任意の改善候補ではなく、その workflow 状態に従う次 action を示す。

`next --json` が `completed` を返している場合、通常 workflow 上の次 action はない。このとき完了報告の次タスク欄に任意候補を書く場合は、次の順で拾う：

1. 利用者がこのターンで次作業を明示した場合は、その指示を次タスクにする。
2. 利用者指示がない場合は、`TODO_NEXT_SESSION.md` の「次にやること」にある推奨順を候補源にする。
3. 候補を表示する前に、`.reviewcompass/backlog/index.yaml` または候補ファイル本体で `status: candidate` であることを確認し、完了済み・存在しない・状態が矛盾する候補は次タスクとして出さない。
4. `TODO_NEXT_SESSION.md` の候補が古い、または候補を解決できない場合は、その旨を現在状態に書き、`.reviewcompass/backlog/index.yaml` の `status: candidate` から次候補を拾う。
5. 完了報告の次タスク欄では、確認できた候補を 5 件ほど、同じ順序でリスト表示する。各候補には、利用者が選べる程度の短い説明を 1 文で添える。
6. 利用者が「次の 1 件だけ」「最上位候補だけ」など 1 件表示を明示した場合に限り、確認できた最上位候補だけを次タスクとして示す。

completed 状態で候補を出す場合も、その候補はまだ開始済みではない。maintenance、reopen、新規 workflow、backlog TODO 実行のいずれとして開始するかは、利用者指示または開始前 preflight の結果で確定する。

### 7.1 進捗説明の平易化

進捗説明では、内部処理名をそのまま主文にせず、利用者が理解しやすい作業状態で述べる。まず次の順で短く示す：

1. 今どの段階か
2. 何をしたか
3. 次に何をするか

必要な場合だけ、内部用語を括弧で補足する。

完了報告や途中報告では、翻訳調の名詞句、英語混じりの見出し、内部状態名や英語の道具名を見出しや主語にしない。`next --json`、`commit wrapper`、`required_action`、`workflow_state` などの語は、利用者が判断するために必要な場合だけ、自然な日本語の説明の後ろへ括弧書きで添える。主文では「何を変えたか」「今どこで止まっているか」を自然な日本語で述べ、利用者が次に何をすればよいかを自然な日本語の文で示す。

避ける表現：

- 停止点を消費
- gate を通過
- required_action
- pending_gate
- workflow_state を更新
- commit wrapper を開始条件にする
- next --json は reopen_in_progress

言い換え例：

- 「tasks approval の停止点を消費」ではなく「tasks 段の承認を完了済みとして記録」
- 「implementation drafting を完了」ではなく「implementation 段のコードとテストを作成」
- 「次の required_action は run_reopen_pending_gate」ではなく「次は現在の段のレビュー作業」
- 「commit wrapper を最初から sandbox 外で実行」ではなく「コミット用の検査手順は、最初から許可された実行環境で動かす」
- 「next --json は reopen_in_progress」ではなく「やり直し手続きの途中で、次は requirements 段の確認を進める状態」

### 7.2 利用者操作が必要な停止点の表示

承認、コミット、push、判断など、利用者の短い返信で次へ進む停止点では、完了報告の末尾に次の 1 行を示す：

```text
次に必要な操作: <操作語>
```

`<操作語>` は、利用者がそのまま返信できる短い語にする。

例：

- `次に必要な操作: 承認`
- `次に必要な操作: コミット`
- `次に必要な操作: push`
- `次に必要な操作: 判断`

複数の選択肢が必要な場合だけ、候補を短く並べる。通常は候補を 1 つに絞る。内部用語、長い説明、手順ログをこの行に混ぜない。

このレポートは会話末尾の完了報告であり、workflow_state や `spec.json` の正本を代替しない。

## 8. 用語ガイド

### 8.1 「遡及」と「波及」

両用語は対象方向で使い分ける：

- **遡及（そきゅう）**：上流フェーズへの影響（時間軸＝過去方向）
- **波及（はきゅう）**：同フェーズ内の他機能への影響（横方向＝機能間）

両方とも正当な技術用語で、避けるべき／推奨という関係ではない。所見の性格を正確に表すために使い分ける。

### 8.2 判定値の使い分け

- **must-fix**：仕様の致命的または重要な欠落、修正必須
- **should-fix**：仕様の改善余地、修正推奨
- **leave-as-is**：仕様として問題なし、修正不要

### 8.3 機能内と機能横断

- **機能内対処**：当該機能の drafting 段で本セッション内に修正
- **機能横断持ち越し**：carry-forward register に集約、review-wave／alignment／approval の機能横断段で対処

### 8.4 サブエージェント関連

- **メインセッション**：作業の入口となる LLM session。草案作成とレビュー結果の取りまとめを担い、3 役レビューの判定者とは分離する
- **サブエージェント**：敵対役・判定役を実行する別 session または外部 API 検証者。利用中の adapter が利用可能な実行形に従う
- **mode = `subagent_mediated`**：サブエージェント方式のレビュー記録の mode 値

## 9. 関連文書

- ワークフローナビゲーション：[WORKFLOW_NAVIGATION.md](WORKFLOW_NAVIGATION.md)
- 事前検査：[WORKFLOW_PRECHECK.md](WORKFLOW_PRECHECK.md)
- reopen 手順：[REOPEN_PROCEDURE.md](REOPEN_PROCEDURE.md)
- 抽出進捗：[../../docs/extraction-mapping.md](../../docs/extraction-mapping.md)
- 機能横断波及所見：正本 [../../learning/workflow/carry-forward-register/reviewcompass-import.yaml](../../learning/workflow/carry-forward-register/reviewcompass-import.yaml)、履歴 source [../../learning/workflow/carry-forward-register/sources/reviewcompass-pending-cross-feature-findings.md](../../learning/workflow/carry-forward-register/sources/reviewcompass-pending-cross-feature-findings.md)
- レビュー記録雛形：[../../templates/review/manual_dogfooding_review_template.md](../../templates/review/manual_dogfooding_review_template.md)
- TODO：[../../TODO_NEXT_SESSION.md](../../TODO_NEXT_SESSION.md)

## 10. 本ガイドラインの改訂規律

- 本ガイドラインは運用文書として更新可能
- セッションの経緯記録は `docs/sessions/` に残し、本文書には現行の運用契約だけを置く
- 規律変更（§2〜§8）は利用者明示承認後に反映
- 改訂時は最終更新日付を更新
```

### .reviewcompass/guidance/WORKFLOW_NAVIGATION.md

content_mode: full_text
content_sha256: f264a762f6bde2e6a2702a5c9219d89b611ced5328be4db65e66ccba23a4c269

```text
# ReviewCompass ワークフローナビゲータ共通手引き

この文書は、`tools/check-workflow-action.py next --json` の読み方を定める共通手引きである。

## 1. 最初に実行するコマンド

作業を始める前、または次に何をするかを提案する前に、必ず次を実行する。

```bash
python3 tools/check-workflow-action.py next --json
```

出力 JSON の `next_action.kind` を、現在の作業順序・優先順位の正本として扱う。記憶、要約、TODO の候補欄だけを段取りの根拠にしない。

`next_action.required_disciplines` がある場合は、作業直前にそのファイルだけを読む。セッション開始時に長い規律群を一括で読んで記憶に頼るのではなく、機械判定された場面ごとの短い規律セットで挙動を調整する。対応表は `.reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml` を正本とし、`next --json` はその内容を機械可読に展開する。

`next_action.required_inputs` がある場合は、規律ではなく作業対象ごとの状態入力として扱う。`id`、`source_type`、`read_policy` を確認し、`path` がある場合でもファイル名そのものを一般規律に昇格しない。たとえば持ち越し台帳は、配布先プロジェクトごとに別ファイル、外部台帳、または未配置になり得るため、`unresolved_cross_scope_items` のような抽象入力として扱う。

機械可読な判定点では、判定点ごとに 1 本の effective prompt を読む。複数の元資料を直接ばらばらに読ませるのではなく、判定点に必要な規律・入力・次タスク方針を 1 本へ束ねた effective prompt を作り、その本文を LLM に読ませる。元資料は `prompt_source_refs` として保持し、実際に読ませた統合プロンプトは `effective_prompt_path`、`effective_prompt_sha256`、`effective_prompt_loaded` で記録する。全判定点で同じ巨大な共通プロンプトを使わず、各判定点に必要な短い effective prompt を使う。

## 1.1 作業モード分類の用語表（work mode taxonomy）

作業者は、maintenance、side-track、blocking unit、reopen、post-write verification を単一 enum に押し込まない。これらは同列の「作業モード」ではなく、次の軸を組み合わせて説明する。

| 用語 | 意味 |
| --- | --- |
| `current_state` | `next --json` が返す機械状態。例：`completed`、`maintenance_in_progress`、`blocking_unit_in_progress`、`post_write_verification`。 |
| `work_class` | これから行う手続きの種類。例：normal workflow、maintenance、reopen、verification。maintenance は作業区分であり、作業内容ラベルや親子関係ではない。 |
| `control_relation` | 本線・親作業との関係。例：mainline、side-track、blocking-unit、parent-resume。side-track は本線との関係であり、maintenance と同列の状態名ではない。blocking unit は親作業に束縛された制御構造である。 |
| `permitted_scope` | 作業宣言の属性。`allowed_scope`、`allowed_files`、`completion_conditions` で、どこまで触ってよいかと戻る条件を表す。 |
| `work_context` | workflow state が `completed` でも残り得る実作業上の文脈。active anchor、side-track stack、return target など、戻り先や親子関係を会話記憶ではなく構造化記録から説明するために使う。 |

例：`next --json` が `completed` を返していても、利用者が検査器の局所修正を求めた場合は、`current_state=completed`、`work_class=maintenance`、`control_relation=mainline` または `side-track`、`permitted_scope=allowed_files と completion_conditions` と分けて説明する。`audit` のような作業内容ラベルを、`current_state` や `control_relation` の値として扱わない。

## 2. 判定結果の共通分岐

<a id="resume_in_progress"></a>

### `resume_in_progress`

`stages/in-progress/` に進行中手続きがある。新しい作業を始めず、`next_action.file` に示された進行中ファイルを読む。

<a id="parent_resume_pending"></a>

### `parent_resume_pending`

blocking unit が完了し、戻り先の parent unit へ復帰する必要が残っている。新しい作業を始めず、`next_action.parent_unit_id` と `next_action.completed_unit_id` を確認し、まず parent unit の作業文脈へ戻る。

`parent_resume_pending` が出ている状態で、利用者から別作業への明示的な割り込み指示があった場合は、開始前に次を実行して、active unit と resume pending の有無を機械的に確認する。

```bash
python3 tools/check-workflow-action.py work-unit preflight-start \
  --proposed-unit-id <開始候補 unit ID> \
  --title "<開始候補の題名>" \
  --reason "<開始候補の理由>" \
  --json
```

`start_allowed: false` の場合は、`blocking_reasons` を利用者へ示して停止する。理由を見ずに通常 workflow、maintenance、新しい blocking unit へ進まない。

<a id="blocking_unit_required"></a>

### `blocking_unit_required`

別作業として切り出すべき作業が検出されている。通常 workflow や親作業を続けず、`next_action.proposed_unit` の `unit_id`、`title`、`reason`、`parent_unit_id`、`return_conditions` を確認してから、利用者の明示的な開始指示を待つ。

機械化が完全に揃うまでは、blocking unit の開始を暗黙に扱わない。開始前に、少なくとも次を会話上で明示する。

- blocking unit に入ること。
- 親作業の識別子。
- blocking unit の目的。
- blocking unit で変更してよい allowed files。
- 親作業へ戻るための完了条件。

宣言形式は次の形にそろえる。項目名を変えたり、本文中に散らして書いたりしない。

```text
blocking unit に入ります
- unit_id: <blocking unit ID>
- parent_unit_id: <親作業 ID>
- title: <短い題名>
- reason: <なぜ別作業として切り出すか>
- allowed_files: <変更してよいファイルまたはディレクトリ>
- return_conditions: <親作業へ戻るための完了条件>
```

`allowed_files` は必須であり、空欄や「必要な範囲」「関連ファイル」などの曖昧な指定では開始しない。開始時点で想定できるファイルまたはディレクトリを列挙し、途中で範囲を広げる必要が出た場合は、変更前に allowed files の追加を利用者へ明示する。親作業全体やリポジトリ全体を覆う指定は、混線防止の目的に反するため使わない。

`return_conditions` も必須であり、空欄や「完了したら」「必要なところまで」などの主観的な指定では開始しない。親作業へ戻ってよいかを確認できる条件を列挙し、少なくとも成果物、検証、commit または evidence の扱いを含める。blocking unit を出るときは、各条件を満たしたか、未達なら何を残件として親作業へ戻すかを明示する。

<a id="blocking_unit_in_progress"></a>

### `blocking_unit_in_progress`

blocking unit が active である。`next_action.unit_id` の作業だけを扱い、親作業の commit、push、post-write verification、TODO 整理へ横滑りしない。

機械化が完全に揃うまでは、作業者は次を手動で守る。

- 作業開始時と再開時に、現在の active blocking unit を確認する。
- commit 前に、commit unit が active blocking unit の `unit_id` と一致することを確認する。
- blocking unit 完了前に親作業の成果物を同じ commit に混ぜない。
- 親作業の commit は、blocking unit の完了条件を満たし、必要な commit または evidence を残し、親作業へ戻る宣言を終えるまで実行しない。
- blocking unit を出るときは、完了条件を満たしたこと、残件、親作業への戻り先を明示する。

<a id="reopen_in_progress"></a>

### `reopen_in_progress`

reopen 手続きが進行中である。通常ワークフローや post-write-verification より優先する。`next_action.file`、`next_step`、`completed_steps`、`pending_gates`、`current_blocker`、`required_action` を確認し、`required_action` に従う。

代表的な `required_action`：

- `draft_reopen_classification`：第1過程。種別判定・根拠記録。進行中ファイル発行と spec.json フラグ差し戻しは後続操作（`run_reopen_start`・`apply_approved_reopen_plan`）が担う。
- `repair_canonical_documents`：第2過程。上流フェーズの正本文書修正。
- `run_reopen_drafting`：第3過程。`next_pending_gate` が triad-review でも、同じ phase の drafting 完了が `drafting_completed_gates` または `completed_gates` に記録されていないため、先に正本文書を更新する。`active_gate`、`phase`、`stage: drafting`、`required_feature_scope` を確認し、レビューを開始しない。
- `run_reopen_pending_gate`：第3過程。drafting 完了記録がある、または次 gate が triad-review 以外であるため、`next_pending_gate` の gate を実行する。alignment / approval 連鎖の再実施を含む。
- `wait_for_human_decision`：人間の判断待ち。判断なしに進めない。
- `finalize_reopen`：第4過程。最終確認、recheck クリア、in-progress の完了処理。
- `repair_workflow_state`：判定不能または状態破損。推測で進めず利用者へ報告する。

<a id="maintenance_in_progress"></a>

### `maintenance_in_progress`

通常ワークフローではなく、ワークフロー制御・運用規律・検査器などの保守作業が進行中である。`next_action.file` を読み、`required_action`、`allowed_scope`、`completion_conditions` に従う。通常の `stage` や `upstream_recheck` へ戻るのは、maintenance の完了条件を満たし、進行中ファイルを `stages/completed/` へ移してからである。

`next_action` と異なる作業へ入る場合、または `next` 判定自体の欠陥を直す場合は、ファイル編集前に `stages/in-progress/maintenance-<日付>-<短い名前>.yaml` を作成する。少なくとも `trigger`、`mainline_blocked_by`、`work_class`、`control_relation`、`allowed_scope`、`allowed_files`、`completion_conditions` を記録し、side track であることを明示する。保守作業を side-track として始める場合は `work_class: maintenance`、`control_relation: side-track` を使う。これを省略すると、本筋の作業順序を守るための修復作業自体が、記録されない手順逸脱になる。

maintenance の進行中ファイルは、必要に応じて `workflow_steps`、`required_reviews`、`review_evidence`、`post_write_verification`、`completion_criteria` を持つ。`workflow_steps` は作業工程の完了状態、`required_reviews` は変更内容そのものに対する必要レビュー、`review_evidence` はそのレビューや確認の証跡、`post_write_verification` は正本文書などの書き込み後検証、`completion_criteria` は maintenance を完了へ移せる条件を表す。変更内容レビューと post-write verification は別工程として記録し、docs note だけの記録作業は code / SDD / guidance 変更と同じ厳格検証として扱わない。

`required_reviews` に未完了項目があれば `next --json` は `maintenance_review_required` を返す。`required_reviews` が完了し、`post_write_verification.status` が未完了なら `maintenance_post_write_required` を返す。これらが完了し、`completion_criteria` が記録されている場合は `maintenance_completion_required` を返し、maintenance ファイルを完了側へ移す作業へ進む。

本線 reopen 中の maintenance 完了 commit は、`stages/completed/maintenance-*.yaml` の `mainline_blocked_by` が現在の reopen in-progress ファイルを覆うことで許可される。本線 `stages/in-progress/reopen-*.yaml` は、maintenance のためだけに同伴 stage しない。

**maintenance を始める前の事前調査（in-progress YAML を作成する前に実施する）**

1. 変更対象ファイルと依存関係を確認し、影響範囲を特定する。
2. フィーチャー横断の影響がないことを確認する。
3. 先に解決すべきブロッカー（別の問題）が潜んでいないことを確認する。

事前調査の結果として次の開始条件をすべて満たした場合のみ maintenance を始める。

- 変更が局所的である（既存仕様境界を変えず、workflow 機構・承認・状態機械・`next --json` の意味を変えない）。
- 影響範囲が対象フィーチャーに閉じている。

いずれかを満たさない場合：

- 中核変更（仕様境界・workflow 機構を変える）の場合は reopen または新規 workflow として扱う。
- フィーチャー横断の影響がある場合は利用者にエスカレーションする。

開始条件を満たした場合、in-progress YAML を作成した後に最初に次の 3 行を宣言する。

```
変更分類: 局所
理由: <影響範囲と既存仕様境界への影響の説明>
手順: TDD 主導 / 文書のみ（lightweight self-check）
```

コード変更を伴う局所変更は TDD 主導（テスト先行）で進める。文書のみの変更は lightweight self-check で確認する。

### `reopen_classification_required`

完了済み workflow で、`intent`、feature-partitioning、`requirements`、`design`、`tasks` などの上流正本が後続成果物より新しい。単なる再確認として下流へ進めず、意味変更の有無と reopen 種別を分類する。`next_action.reopen_trigger` が候補を示す場合も、分類根拠を保存して `reopen-start` へ進む。

<a id="post_write_verification"></a>

### `post_write_verification`

書き込み後検証の対象となる未コミット変更がある。通常ワークフローへ進まず、`next_action.target_files` 全体を対象として検証する。

検証 manifest は `.reviewcompass/post-write-verification/*.yaml` に置く。`target_files`、`target_sha256`、`required_verifiers`、`completed_verifiers`、`unresolved_substantive_findings` を記録する。`verifications[]` がある場合、各 verifier は `target_files` 全体と対応する `target_sha256` を単一エントリで覆る必要がある。ファイルごとの分業は独立多重チェックではない。

API 経由の複数モデル検証を行う場合の標準手順：

```bash
.venv/bin/python3 tools/api_providers/prepare_post_write_review.py \
  --target <target-file> \
  [--target <target-file-2> ...] \
  --source-material .reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md \
  [--source-material <additional-source-material> ...] \
  --review-run-dir .reviewcompass/evidence/review-runs/<run-id> \
  --criteria-id <criteria-id> \
  --change-summary "<change-summary>" \
  --review-question "<review-question>"

.venv/bin/python3 tools/api_providers/run_review.py \
  --variant post_write_verification_google \
  --target <target-file> \
  [--target <target-file-2> ...] \
  --phase post_write_verification \
  --criteria-file .reviewcompass/evidence/review-runs/<run-id>/review-target.md \
  --prompt-manifest-path .reviewcompass/evidence/review-runs/<run-id>/prompt-manifest.yaml \
  --review-run-dir .reviewcompass/evidence/review-runs/<run-id>

.venv/bin/python3 tools/api_providers/review_triage.py list-pending \
  --review-run-dir .reviewcompass/evidence/review-runs/<run-id>

.venv/bin/python3 tools/api_providers/review_triage.py decide \
  --review-run-dir .reviewcompass/evidence/review-runs/<run-id> \
  --finding-id <finding-id> \
  --final-label must-fix \
  --decision-reason "<reason>" \
  --decision-actor human \
  --approval-record .reviewcompass/evidence/review-runs/<run-id>/approval.yaml

.venv/bin/python3 tools/api_providers/review_triage.py write-manifest \
  --review-run-dir .reviewcompass/evidence/review-runs/<run-id> \
  --out auto \
  --approval-record .reviewcompass/evidence/review-runs/<run-id>/approval.yaml

.venv/bin/python3 tools/check-workflow-action.py next --json
```

API 呼び出し起動手順の正本は、先に `.venv/bin/python3 tools/api_providers/prepare_post_write_review.py ...` で review-target と prompt manifest を生成し、その後 `.venv/bin/python3 tools/api_providers/run_review.py ... --criteria-file <review-target.md> --prompt-manifest-path <prompt-manifest.yaml>` を実行することである。外側から `zsh -c` で包まない。API key は配布物や設定ファイルへ書かず、利用者の shell 初期化で読み込まれる環境変数から渡す。Claude Code などの操縦実行面では、子プロセスの `ANTHROPIC_API_KEY` と `GEMINI_API_KEY` が空文字列へ上書きされることが確認済みである。一方、`OPENAI_API_KEY` は同じ確認では上書きされていない。このため `run_review.py` / `run_role.py` entrypoint 内で、環境変数が未設定の場合に `~/.zshrc` を読み直して API key を補完する。補完後も key が得られない場合は API key 未設定として fail-closed する。

`prepare_post_write_review.py` は `review-target.md`、`review-target.yaml`、`prompt-manifest.yaml` を同じ `--review-run-dir` に生成する。`review-target.md` には criteria ID、変更要約、検査質問、target files、source materials、target file contents、scope / out-of-scope、finding policy、機微情報チェック結果を含める。`prompt-manifest.yaml` には `review_prompt_materials.target_files` と `review_prompt_materials.source_materials` を `content_mode: full_text` と `content_sha256` 付きで記録する。機微情報らしい文字列を検出した場合、または prompt manifest audit が DEVIATION の場合は fail-closed し、外部 API review へ進まない。

`next_action.target_files` が複数ある場合は、`prepare_post_write_review.py` と `run_review.py` の両方で `--target` を複数回指定して同じ review-run に束ねる。API review-run の成否確認は、`review-target.md`、`review-target.yaml`、`prompt-manifest.yaml`、`review_summary.md`、`rounds.yaml`、`model-result-summary.yaml`、`raw/`、`parsed/`、`prompts/`、`target-manifest.yaml` が同じ `--review-run-dir` に生成され、`rounds.yaml` の `target_files`、`criteria_source_path`、`prompt_manifest_path`、provider、model、prompt/raw/parsed path が今回の対象と一致することで行う。

API 呼び出しが失敗した場合は、まず上の正本手順を再確認する。`import` エラー、`argparse` エラー、引数不一致は起動手順または実装の問題であり、外部送信ポリシーや provider 側障害と混同しない。`ConnectError`、名前解決失敗、接続不能が出た場合は sandbox network 制限の可能性を先に疑い、同じ正本コマンドをネットワーク実行が許可された実行面で再実行する。API key 未設定のエラーは `~/.zshrc` から対象 provider の環境変数が読み込まれているかを確認する。

`post_write_verification` では API 経路の variant を明示する。小規模既定は `--variant post_write_verification_google`、大規模または 3 系統検証が必要な場合は `--variant <post-write-api-variant>` として、`config/api-settings.yaml` の `context: post_write_verification` かつ API provider だけで構成された variant を選ぶ。CLI 経路を含む default variant に暗黙フォールバックしてはいけない。

API レビュー結果を得た場合は、raw 参照、モデル別要約、三段階トリアージ（`must-fix`／`should-fix`／`leave-as-is`）を利用者へまとめて提示する。`ERROR`／`CRITICAL` または最終判断 `must-fix` の重要件を `decide` する場合、または重要件を含む run から manifest を生成する場合は、承認を記録した `--approval-record` が必須である。承認レコードには `approved_by: user` または `approved_by: proxy_model`、`review_run_id`、`summary_presented_to_user: true`、`triage_presented_to_user: true`、`approved_finding_ids`、必要に応じて `approved_final_labels` を含める。`approved_by: proxy_model` の場合は、`proxy_model_id` と finding ごとの `proxy_decisions` を含め、各 decision file が raw response、候補案、採用案、判断理由、最終ラベルを保持する。

`write-manifest --out auto` は `.reviewcompass/post-write-verification/post-write-YYYY-MM-DD-NNN.yaml` の次番号を作る。manifest は post-write validation の途中記録ではなく、commit 直前の最終封印である。`triage.yaml` に `decision_status: human_required` が残る場合、重要件の利用者承認が確認できない場合、または review-run の target set に含まれない未コミット post-write target が残る場合は manifest を生成しない。manifest 作成後は対象ファイルを編集せず、stage / approval / commit へ直行する。

この生成停止条件は、現在の review-run から新しい最終 manifest を作る場合の規則である。既存の post-write manifest が現在の対象ファイルと一致し、かつ未解決の本質的指摘を含む場合は、`next --json` が `post_write_human_decision_required` と `next_action.manifest` を返す。

<a id="lightweight_self_check"></a>

### `lightweight_self_check`

notes / 履歴 / 判断材料の未コミット変更がある。通常ワークフローへ進まず、`next_action.target_files` を API post-write verification ではなく軽量自己精査で確認する。

軽量自己精査の対象は `docs/notes/` 配下と、単独変更の `TODO_NEXT_SESSION.md` とする。`docs/notes/` は議論記録、判断経緯、過去メモ、参考情報を置く場所として扱い、正本仕様・運用規律・レビュー判定そのものではないため、API review ではなく自己検査で確認する。`docs/operations/`、`docs/disciplines/`、`docs/reviews/`、`stages/completed/` は正本または完了記録として厳格に扱う。notes から正本へ昇格する内容は、該当する正本ファイルへ移した時点で strict な `post_write_verification` 対象とする。

`TODO_NEXT_SESSION.md` は更新頻度が高い次セッション導線であり、進捗整理・次タスク・現在状態の更新だけなら API review ではなく軽量自己精査で扱う。ただし、同じ未コミット差分に strict な `post_write_verification` 対象が含まれる場合は、TODO も同じ strict 検証の `target_files` に同梱する。

軽量自己精査では、API review を呼ばず、次だけを確認する。

1. 利用者の指摘内容を落としていないか。
2. 事実、推測、方針案、未実装事項が区別されているか。
3. 後で見たときに次の判断材料になるか。
4. 作業範囲を超えて仕様化していないか。
5. API review が必要な正本へ昇格していないか。

完了記録は `.reviewcompass/post-write-verification/*.yaml` に置き、`required_verifiers` と `completed_verifiers` は `lightweight_self_check` とする。`target_files` と `target_sha256` は通常の post-write manifest と同じく対象全体を覆う。

`post_write_verification` 対象と `lightweight_self_check` 対象が混在する場合は、`post_write_verification` を優先する。strict 側が完了した後、軽量対象が残っていれば `lightweight_self_check` を返す。

<a id="post_write_policy_violation"></a>

### `post_write_policy_violation`

post-write-verification pending 中に禁止変更がある。通常ワークフローへ進まず、`next_action.forbidden_files` を報告して停止する。禁止ファイルを勝手に削除・修正してはいけない。

現行実装では、post-write-verification 対象ファイルが未コミット変更に含まれる状態で、`tools/*.py`、`templates/`、または他の post-write 対象と混ざった `docs/disciplines/` 配下の変更があると逸脱になる。

<a id="post_write_human_decision_required"></a>

### `post_write_human_decision_required`

既存の post-write manifest に未解決の本質的指摘がある。通常ワークフローへ戻らず、`next_action.target_files` と `next_action.manifest` を確認し、利用者判断を待つ。

これは、現在の review-run で `triage.yaml` に `decision_status: human_required` が残ったまま新しい最終 manifest を生成する状態ではない。その場合は manifest 生成前に停止し、triage の判断または承認を先に解決する。

### `stage`

通常ワークフロー上の次タスクが決まっている。`feature`、`phase`、`stage` の示す作業だけを扱う。

`stage` が `triad-review` の場合、review-run の開始前に使用 variant と role ごとの path／provider／model を確定し、曖昧なまま開始しない。review-run に使うプロンプトは [[llm-as-judge-prompting]] の手順（材料揃え → 問い設計 → 選択肢なし分析）で設計する。API review-run 完了後は、proxy_model 判断依頼、実装修正、spec.json 更新、フェーズ移行のいずれにも進む前に、raw 参照、モデル別要約、同根所見クラスタ、`must-fix`／`should-fix`／`leave-as-is` の三段階トリアージ案、重要件の平易な説明を利用者へ提示して停止する。詳細手順は `.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2` を正本とする。

### `cross_feature_stage`

機能横断段に進む。`feature` は `all_features` になる。`recheck_items` がある場合は上流変更の織り込みを含める。`required_inputs` に `unresolved_cross_scope_items` があり、`unresolved_count` が 0 より大きい場合は、`read_policy` に従って未消化の持ち越し所見だけを確認する。ReviewCompass では互換情報として `pending_cross_feature_findings` も返るが、一般化された判断根拠は `required_inputs` とする。

自律・並列で機能横断段を試行する場合は、通常の review-wave 完了判定に入る前に `autonomous-plan` を作成し、`tools/check-workflow-action.py autonomous-plan <plan.yaml>` で検査する。計画には `recheck_items` と `stages/feature-dependency.yaml` から分かる依存を明示し、上流 recheck 対象を下流判断より先に置く。同じ worktree で並列化してよいのは読取調査または差分を残さない確認に限る。新しい依存、暗黙依存、未記録依存、または上流 recheck の下流反映が必要だと分かった場合、その作業単位は停止し、機能横断段の実施記録に blocked として記録してから統合判断へ戻す。

機能横断段の実施記録は、単一 feature 配下に置かず `.reviewcompass/specs/_cross_feature/reviews/` に置く。標準ファイル名は `.reviewcompass/specs/_cross_feature/reviews/{date}-{phase}-{stage}.md` とし、`feature: all_features`、対象 phase/stage、確認した feature 範囲、持ち越し件数、recheck 結果、実行した検証コマンド、判断結果を記録する。`_cross_feature` は実 feature ではなく、横断段成果物だけの名前空間である。

<a id="commit_stop_point"></a>

### `commit_stop_point`

通常 workflow の phase 終端または reopen 手続き上の停止点に到達している。`required_action: commit_stop_point` の場合、次 phase / 次 gate へ進まず、利用者の明示的な commit 指示を待つ。

利用者の短い操作語（例: `コミット`、`push`、`次へ`）を受けた場合は、mutation の前に `.venv/bin/python3 tools/check-workflow-action.py operation-trigger-resolve --trigger-text <text> --json` を実行し、`operation_id`、`operation_card_path`、`first_readonly_command`、`mutation_allowed_after` を確認する。`resolution_status: stop-and-ask` または `unknown_operation` の場合は、低レベルコマンドを推測実行せず利用者確認で停止する。

利用者が commit を指示した直後は、Git index への追加（`git add`）や approval record を作る前に `.venv/bin/python3 tools/check-workflow-action.py commit-preflight --json` を実行する。`DEVIATION` の場合は何も作らず停止し、理由と次に許可されている action だけを報告する。

通常 workflow では、`intent.approval` または `feature-partitioning.approval` が全 feature で完了し、該当 phase の workflow_state または成果物に未コミット変更がある場合に返る。`blocked_by.phase`、`blocked_by.stage`、`blocked_by.dirty_paths` を確認する。`commit-preflight` が `OK` を返した後に対象差分を `git add` し、guarded commit の通常手順へ進む。commit 後に作業ツリーが clean であれば、同じ停止点を返し続けず次 phase の action へ進む。

reopen 手続きでは、`reopen_in_progress` の `required_action: commit_stop_point` として返る。`blocked_by.kind` と `blocked_by.gate` を確認し、reopen 手続きファイルを含む停止点 commit を行う。

<a id="commit_mixing_risk"></a>

### `commit_mixing_risk`

commit unit が固定した対象外の staged file が混入している。通常 workflow、post-write verification、guarded commit へ進まず、`next_action.target_files`、`extra_staged_files`、`path` を確認する。

利用者に、対象外ファイルを別 commit unit / blocking unit へ分けるか、現在の commit unit を再作成してよいかを確認する。対象外ファイルを理由なしに同じ commit へ混ぜない。

<a id="commit_unit_stale"></a>

### `commit_unit_stale`

commit unit が現在の staged 内容と一致していない。通常 workflow、post-write verification、guarded commit へ進まず、`next_action.target_files` と `path` を確認する。

staged 内容を commit unit に合わせて戻すか、現在の staged 内容に合わせて commit unit を再作成する。古い commit unit のまま承認 record や commit execution delegation を作らない。

### `upstream_recheck`

完了済み workflow であっても、上流成果物が下流成果物より新しいため、下流へ進む前に再確認が必要である。`upstream_phase`、`phase`、`stage` を確認し、`phase.stage` に示された作業を次作業として扱う。たとえば intent 更新後は feature-partitioning の確認、requirements 更新後は design の再確認、tasks 更新後は implementation の再確認を先に行う。

この kind が返った場合、記憶や直前の会話から requirements、design、tasks、implementation へ飛ばない。必ず `next_action.phase` と `next_action.stage` に従い、上流から下流へ順に反映する。

<a id="feature_definition_required"></a>

### `feature_definition_required`

feature 一覧が解決できない（`feature-dependency.yaml` が見つからない、または `feature_order` キーが未定義）。対象アプリの初期状態で発生する。エラーではない（verdict OK）。

`next_action.reason`（立ち上げ案内の本文）と `current_state.feature_dependency_source`（解決元）を確認する。`feature_dependency_source` が null ならファイル自体が探索順（`.reviewcompass/feature-dependency.yaml` → `stages/feature-dependency.yaml` → `feature-dependency.yaml`）のどこにも存在せず、ファイルパスが入っていればそのファイルはあるが `feature_order` キーが未定義または不正である。前者は分割結果の記録から、後者は既存ファイルへの `feature_order` キーの追記から始める。

新しい作業を始めず、intent と feature-partitioning を実施し、承認された分割結果（機能ごとの依存の主張と理由、順序の導出を含む）を `.reviewcompass/feature-dependency.yaml` の `feature_order` キーに記録する。記録後に `next` を再実行する。feature 立ち上げの手順は `.reviewcompass/guidance/INITIAL_SETUP_LLM_GUIDE.md` を正本とする。

なお、`feature_order` と `depends_on` の整合違反（依存される機能が先に並んでいない、循環依存がある）は本 kind ではなく `unknown`／DEVIATION（fail-closed）になる。理由に従って `feature-dependency.yaml` を修正する。

### `completed`

全 workflow_state が完了している。通常の次タスクはない。

完了報告で「次タスク」を示す必要がある場合、ここでいう「通常の次タスクはない」とは、workflow_state が要求する次 action がないという意味である。backlog 候補、maintenance 候補、reopen 候補を提示してよいが、それらは workflow の自動継続ではなく、利用者が次に選べる作業候補として扱う。

候補を拾う順序と表示件数は `.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#7-作業完了時レポート` の completed 時の次タスク取得規律に従う。`TODO_NEXT_SESSION.md` の推奨順を候補源にする場合でも、候補が現在も `status: candidate` であることを `.reviewcompass/backlog/index.yaml` または候補ファイル本体で確認してから表示する。完了報告では、利用者が 1 件表示を明示した場合を除き、5 件ほどを短い説明つきの選択肢として示す。

利用者指示により maintenance、reopen、または新規 workflow を開始できる。別作業を開始する前には、原則として `work-unit preflight-start` を実行し、`start_allowed` と `blocking_reasons` を確認する。maintenance を始める場合は、その後に `maintenance_in_progress` の事前調査と開始条件を確認する。

**completed からの作業開始分類**

| 分類 | 使う条件 |
| --- | --- |
| maintenance | 局所的な運用・検査器・手引き補修で、既存仕様境界や workflow 機構の意味を変えない。 |
| reopen | 既存正本の意味変更や下流再実施が必要で、既存 feature の責務内に収まる。 |
| 新規 workflow | 既存 feature の責務境界に収まらない新しい責務を導入する。 |

判断が分かれる場合は候補だけを提示し、人間判断を待つ。候補のまま `stages/in-progress/maintenance-*.yaml` を作成したり、reopen-start や新規 workflow の正本作成へ進んだりしない。

### `unknown`

状態判定できない。推測で進めず、`reasons` と `current_state` を利用者へ報告する。

## 3. 共通禁止事項

- `next` を実行せずに次作業を提案しない。
- `resume_in_progress`、`parent_resume_pending`、`reopen_in_progress`、`post_write_verification`、`post_write_policy_violation`、`post_write_human_decision_required` を通常ワークフローより後回しにしない。
- `lightweight_self_check` を通常ワークフローより後回しにしない。
- `reopen_classification_required` を「再確認で足りる」と独断して下流成果物を更新しない。
- `next_action` と異なる side track に入る場合、または `next` 判定自体を修復する場合は、maintenance in-progress を作らずに編集を始めない。
- 事前調査を省略して maintenance を始めない。影響範囲・依存関係・ブロッカーの確認が済んでいない状態で in-progress YAML を作成しない。
- spec.json の workflow_state 変更、commit、push は不可逆操作として扱い、対応する precheck サブコマンドを実行する。
- 検証者は `target_files` 全体を見る。ファイルごとの分業を独立多重チェックとして扱わない。
- 本質的指摘を独断で逐語的指摘に落とさない。迷う場合は利用者へ上げる。
```

### .reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md

content_mode: full_text
content_sha256: 7a4698ec32170ced27d6f7dad1910a4e5a9b64d4639c74892c37cf60cee999a8

```text
# API Review Prompt Quality

最終更新：2026-06-23

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

### 6.2 Behavior-Path Claim の材料選定

review requirement が「あるトリガーから、意図した機械手順へ進むか」「短い利用者指示が gate を bypass しないか」「特定の guard が必ず作動するか」のような behavior-path claim / 実行経路 claim を含む場合、main preanalysis は変更文書だけを target/source にしてはならない。

この場合、source materials には少なくとも次を含める。

- trigger resolver または利用者発話を operation に写像する map
- operation preflight、guard、gate、runner など実行経路上の制御実装
- その経路を固定するテスト、または存在しない場合は「未固定」と分かる証跡
- 変更対象文書、effective prompt、plan / TODO / checklist など経路上の入力成果物
- 期待される停止点、禁止 bypass、許可される次操作

対象が「文書の整合性」ではなく「動作上の強制」なら、変更された guidance / prompt だけを target にした review-run は不足である。文書に要件が書かれていても、trigger resolver、operation preflight、runner、test がその要件を読んでいなければ behavior-path claim は成立しない。

### 6.3 Review Question Decomposition

main は criteria 作成前に review question decomposition を行う。整合性確認だけの一括質問にしない。

分解では、利用者要件または workflow 要件を要求 claim ごとの required check に写す。各 required check は、次を明示する。

1. 何を成立させる claim か
2. どの target / source material で判定するか
3. finding にすべき失敗条件は何か
4. out of scope は何か

例: 「ショートリクエストが bridge を bypass しない」を検証するなら、単に「prompt と map が整合しているか」と聞かない。`次へ`、`進める`、`継続` などの短い発話がどの trigger resolver / operation preflight / effective prompt に到達し、どこで plan materialization status、TODO/checklist coverage、quality audit を確認するかを required check に分解する。

review question が複数 claim を含む場合は、claim ごとに prompt を分けるか、少なくとも required checks を分離して reviewer が各 claim を個別に pass/fail できる形にする。

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
- behavior-path claim に必要な trigger resolver / operation preflight / runner / test の欠落
- review question decomposition の不足による、整合性確認だけの一括質問化

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

高リスクまたは実行経路 claim を含む review では、single-model findings: [] を単独の完了根拠にしない。根拠説明なしの 0 件、特に raw response が `findings: []` のみの場合は、対象材料と問いが狭すぎる可能性を疑い、次のいずれかを行う。

- 3-way の独立 review に切り替える
- reviewer に claim ごとの pass/fail rationale と参照 material を出力させる
- main preanalysis sufficiency audit へ戻り、source selection と review question decomposition をやり直す

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

2026-06-23 の plan-todo-checklist materialization PTC-4 post-write review では、prompt が「updated effective prompts and discipline map の整合性確認」に寄りすぎ、短い `次へ` / `進める` から plan-to-TODO bridge へ到達する実行経路を検証できなかった。target は guidance / effective prompt に寄り、trigger resolver、operation preflight、runner、経路テストを含めなかったため、single-model findings: [] が返っても behavior-path claim の完了根拠としては弱かった。

この差分から、次を標準規則とする。

- 実審査対象本文を target にしない review-run は、gate 完了根拠として弱い
- author-written summary は criteria または source-material summary として使えるが、target 本文の代替にしない
- 上流接続 review では、source materials と target を明示的に分離する
- source summary には原文または構造化抜粋に加え、必要に応じて source cross-reference を持たせる
- main preanalysis は有用だが、仮説として扱い、reviewer に独立再構成させる
- 1 prompt に複数の独立判断を押し込まない
- prompt 自体の adversarial / judgment レビューを実行前に挟む
- behavior-path claim では、変更文書だけでなく trigger resolver / operation preflight / runner / test を source materials に含める
- review question は要求 claim ごとの required check に分解し、整合性確認だけの一括質問にしない
- 高リスクまたは実行経路 claim では、根拠説明なしの single-model findings: [] を完了根拠にしない

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

### .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md

content_mode: full_text
content_sha256: 49044ad500177cd2bd401ebce77b0b8de88293d570c5bdeaa319614d1b01ca1f

```text
# SESSION_WORKFLOW_GUIDE：セッション運営ガイドライン

最終更新：2026-06-10（現行のセッション運営契約として整理）

本文書は ReviewCompass の開発セッションを確実に回すための運用ガイドラインである。作業開始、レビュー、利用者判断、コミット、完了報告の共通手順を定める。

本文書は運用文書（`docs/operations/` 配下）であり、ReviewCompass の実行時手順を定める。仕様・設計・タスクの正本と矛盾する場合は、該当正本を確認し、必要に応じて reopen 手続きに乗せる。

## 1. セッション開始時の必読フロー（5 分以内）

セッション開始時は **作業着手前に必ず**次を順番に確認する。記憶や前回会話だけを根拠に作業へ入らない。

### 1.1 必読 5 件

順序は重要：

1. **`TODO_NEXT_SESSION.md`**（最新進捗）
   - 前セッション末尾の到達点、次の作業候補、未消化所見
   - 「§0 重要事項」「§1 起動手順」「§3 次の作業候補」を最低限読む
   - 直近の `docs/sessions/session-*.md` も併読し、TODO に圧縮された経緯の詳細を確認する

2. **`.reviewcompass/guidance/WORKFLOW_NAVIGATION.md`**（次 action 判定）
   - `tools/check-workflow-action.py next --json` の読み方
   - 判定点ごとの required disciplines / required inputs / effective prompt の扱い

3. **`.reviewcompass/guidance/WORKFLOW_PRECHECK.md`**（機械判定の入口）
   - `spec-set`、`commit`、`push`、`next`、`reopen-start` の実行前条件
   - 機械判定で停止した場合の扱い

4. **`learning/workflow/carry-forward-register/reviewcompass-import.yaml`**（持ち越し所見の正本）
   - 機能横断波及所見の未消化件数と内容を把握
   - 正本と履歴 source を混同しない

5. **`docs/extraction-mapping.md`**（抽出進捗）
   - 各機能の状態（未着手／抽出中／抽出済／確認済）
   - 機能ごとの実施履歴

### 1.2 確認後の git 状態把握

- `git log --oneline -10`：直近のコミット履歴
- `git status`：未コミット変更の有無

### 1.3 ワークフロー上の現在位置の確認

- 現在どのフェーズか（intent ／ requirements ／ design ／ tasks ／ implementation）
- 現在どの段か（drafting ／ triad-review ／ review-wave ／ alignment ／ approval の 5 段）
- 残機能と消化予定所見

## 2. ワークフロー段の役割と順序

### 2.1 全体構造

```
intent 層（人間担当）
  ↓
機能分離
  ↓
requirements 段：drafting → triad-review → review-wave → alignment → approval
  ↓
design 段：drafting → triad-review → review-wave → alignment → approval
  ↓
tasks 段：drafting → triad-review → review-wave → alignment → approval
  ↓
implementation 段：drafting → triad-review → review-wave → alignment → approval
```

各フェーズは drafting／triad-review／review-wave／alignment／approval の 5 段で進める。

### 2.2 各段の役割（責務分離後）

- **drafting**：各機能の草案作成のみ。1 機能ずつ独立に進める。actor=llm（または human）。requirements／design／tasks の drafting は文書起草を意味する。implementation の drafting は文書起草ではなく、tasks.md に従ったテストと実装コードの生成を意味する。
- **tasks drafting の粒度**：tasks 段の drafting では、対象機能の設計書 §14 要件追跡表（Req 受入単位 × 担当タスク単位）を骨格として tasks.md を作成する。tasks.md は implementation drafting へ直接入れる粒度で書く。各タスクには、実装対象ファイル、最初に書く失敗テスト、実装順序、完了条件、検証コマンド、禁止事項、停止条件を含める。implementation-plan.md や implementation-drafting.md のような別の実装前計画文書を正本成果物として要求しない。
- **triad-review**：機能内の 3 役レビュー（主役・敵対役・判定役）と機能内対処の実施。手動 dogfooding または subagent_mediated（サブエージェント仲介方式）で実施。actor=llm
- **review-wave**：複数機能を横断する複数ラウンドレビュー。機能横断波及所見と同根所見（異なる機能で同じ性格の所見が独立に発見された組）を集約し、一貫した対処方針で全該当機能の仕様文書に反映する
- **alignment**：LLM 自動判定による整合確認段（actor=llm）
- **approval**：人間承認段（actor=human）。proxy_model は approval 段の代行主体ではなく、review-run 後の重要件判断だけを代行できる

drafting と triad-review を別段にする理由は、誰が何をしたかを段単位で明確に記録し、草案作成者と判定者の分離を機械検査可能にするためである。

<a id="vertical-intent-transfer-review"></a>

### 2.2.1 上流意図伝達の必須検査

各 phase の triad-review／review-wave／alignment では、対象 phase の成果物だけでなく、上流成果物または上流判断材料からの意図伝達を必須検査項目とする。review prompt は、少なくとも「上流の目的・責務境界・受入条件・禁止事項が、対象成果物へ欠落・弱体化・逸脱・未根拠追加なく引き継がれているか」を問わなければならない。

- **requirements review**：`上流判断材料 → requirements.md` を確認し、reopen 分類根拠、利用者判断、計画メモ、設計メモなどの目的・責務境界・受入条件・禁止事項が要件へ欠落なく落ちているかを検査する。design.md / tasks.md は参照資料であり、審査対象ではない
- **design review**：`requirements.md → design.md` を確認し、要件の目的・境界・受入条件が設計へ欠落なく落ちているかを検査する
- **tasks review**：`requirements.md → design.md → tasks.md` を確認し、要件と設計の意図が implementation-ready なタスク粒度へ落ちているかを検査する
- **implementation review**：`requirements.md → design.md → tasks.md → implementation` を確認し、実装がタスクだけでなく上流意図から逸脱していないかを検査する

review prompt は、review target / source materials / out of scope を明示する。審査対象は現在 phase の成果物に限定し、source materials は背景・意図伝達確認のための参照資料として扱う。下流 phase の成果物が source materials に含まれる場合でも、その correctness を現在 phase の review で判定してはならない。

source materials をパス名だけで列挙してはならない。縦方向監査の review prompt には、判断に必要な上流本文または要点抽出を、モデルが推測せず読める形で含める。要点抽出を使う場合は、少なくとも上流の目的、責務境界、受入条件、禁止事項、未確定事項、対象 phase へ引き継ぐべき判断を分けて記録する。上流資料を読んでいない場合は review-run を開始してはならない。prompt 内で上流資料の中身が確認できない場合も review-run を開始してはならない。

tasks review では、単に tasks.md の粒度や項目数を見るだけでは不十分である。たとえば T-016〜T-019 を審査する場合は、Requirement 13〜16 の意図が design.md の設計判断を経由して、欠落・弱体化・勝手な追加なしに implementation-ready な作業単位へ落ちているかを必須で確認する。

### 2.3 段の進め方の規律

- **drafting 段の草案完成** → 当該機能の triad-review 段に進む（機能単位で逐次進行）
- **triad-review 段で 3 役レビューと機能内対処** を完了 → 当該機能の drafting／triad-review がそろう
- **全機能で drafting ＋ triad-review を完了** してから review-wave に進む（部分的に review-wave を始めない）
- **review-wave の所見を消化** してから alignment に進む
- **alignment で LLM 自動判定** を通過してから approval に進む
- **approval で利用者の明示承認** を得てから次フェーズに進む

### 2.4 「次の機能の drafting に進むべき」状況の判断

triad-review 段で 3 役レビューを行った所見が **機能横断の波及所見**だった場合、当該機能の triad-review で対処せず、carry-forward register に持ち越して **次の機能の drafting に進む**。

## 3. 修正案件の波及種別と処理段

### 3.1 用語の使い分け

両用語は **対象方向が異なる正当な技術用語** であり、優劣はない：

- **遡及（そきゅう）**：**上流フェーズへの影響**。下流段の作業で発見された問題が、上流段（過去フェーズ）の修正を要するもの。例：実装段で発見した不整合が要件段の書き直しを要する
- **波及（はきゅう）**：**同フェーズ内の他機能（フィーチャー）への影響**。ある機能のレビューが別機能との不整合を露出させるもの。例：foundation 要件の修正が runtime／evaluation 要件にも影響する

所見を分類するときは、上流フェーズへ戻る必要があるか、同フェーズ内の他機能へ広がるかを分けて判断する。

### 3.2 修正案件の 4 種別（＋ 2 補助種別）

レビューで露出する所見は次の種別に分類する：

| 種別 | 内容 | 例 |
|---|---|---|
| **機能内対処** | 当該機能の仕様修正のみで完結 | 表現修正、機能内の語彙不統一訂正 |
| **波及（同フェーズ・横方向）** | 同フェーズ内の他機能の仕様修正も必要 | A-001：foundation 要件と runtime 要件の `not_run` 欠落 |
| **遡及（上流フェーズ・縦方向）** | 上流フェーズの仕様修正が必要 | 設計段で「要件段の Req 6 受入 8 に矛盾あり」と発見 |
| **遡及 ＋ 波及（縦 ＋ 横）** | 上流フェーズの複数機能に影響 | 設計段で発見した要件段の不整合が複数機能の要件文書に波及 |

補助種別：

- **leave-as-is（修正不要）**：判定役が「修正不要」と判断したもの、対処せず記録のみ
- **延期**：「将来フェーズで対処」と判定役が明示したもの（例：F-004 の配置時対処）

### 3.3 種別ごとの処理段と方法

#### (a) 機能内対処

- **発見されるタイミング**：drafting 段（起草者の自己発見）／ triad-review 段（3 役レビュー）
- **処理する段**：当該機能の **triad-review 段** で対処（drafting に戻して草案修正、または triad-review 段内で直接修正）
- **方法**：当該機能の仕様文書を直接修正
- **次段への進行**：当該機能の triad-review 段が `completed` 状態になってから次機能へ
- **記録先**：レビュー記録（`.reviewcompass/specs/<機能>/reviews/<日付>-<種別>.md`）の §4 統合節に「対処済み」と記録

##### (a-1) must-fix 所見の対処手順

triad-review 段で判定役が must-fix と判定した所見の対処は、起草者（LLM または人間）が独自判断で仕様文書を修正することを禁ずる。利用者と必ず議論し、各所見の対処方針を 1 件ずつ平易な日本語で説明して合意を得てから反映する。

**手順**：

1. must-fix 所見を 1 件ずつ取り上げる。複数所見が論理的に連動する場合は連動単位でまとめる（例：F-001 と F-007 が同一事象を別観点で扱う場合）
2. 各所見について、対処方針の提案を次の構造で平易に説明する：
   - その判断が必要になった経緯（要件文書や上流文書からの導出）
   - 候補案の列挙（必ず複数）
   - 各候補案の利点と弱点
   - **後段で発生し得る問題の深掘り**：下流仕様（他機能の design／tasks／implementation）、対象アプリへの配置可能性、機械検証時の挙動、実装フェーズの運用、将来の拡張性
   - 推奨案とその根拠
3. 「現状維持」を推奨する場合も、現状維持の弱点を検証してから示す
4. 一括処理（複数論点を一気に決着）を避け、各論点を個別に深掘りする
5. 利用者の判断を得てから、仕様文書を 1 件ずつ Edit で修正する
6. 各修正後に grep または Read で機械的に照合し、反映を確認する
7. レビュー記録（reviews/...）の §4 統合節に「対処方針・利用者承認の根拠・反映箇所」を記録する

**深掘りの具体内容**（推奨案を提示する際に必ず想定する事項）：

- foundation 機能の場合：対象アプリへの配置可能性、配布対象外資産との分離、リポジトリ内資産の規則との整合
- 値域・語彙の固定：将来拡張時の改訂コスト、機械検証時の不正値検出
- 責務境界：foundation と runtime（または他機能）の責務分離、上流が下流の実装方針に踏み込まない原則
- 不変性：成果物の追記性、生証拠は不変の原則
- 依存関係：他機能が当該仕様を取り込む際の参照可否

**禁則**：

- 利用者と議論せずに must-fix 所見の対処内容を独自に確定する
- 「現状維持を推奨」と表層的に提案する（弱点検証を欠く）
- 候補案を 1 つしか提示しない（代替案との比較を欠く）
- 後段影響を想定しない推奨

<a id="3.3-a-2"></a>

##### (a-2) review-run 後の proxy_model 判断代行手順

API 経由の review-run 後に、人間の個別判断を proxy_model が代行する場合も、メインセッション LLM が重要件を独自に確定して実装へ進むことを禁ずる。proxy_model 代行は「人間判断を省略する」ものではなく、判断主体を別モデルへ移す運用である。

**proxy_model 判断依頼前の利用者提示ゲート**：

API review-run が完了したら、proxy_model 判断依頼、実装修正、spec.json 更新、フェーズ移行のいずれにも進む前に、メインセッション LLM は次を利用者へ提示して停止する。この提示ゲートを完了する前に proxy_model を呼び出してはいけない。

1. 使用 variant 名
2. role ごとの path／provider／model（例：primary／adversarial／judgment の割当）
3. モデル別 raw 結果概要（parse 状態、所見数、severity 内訳、raw path）
4. 同根所見クラスタの一覧
5. `must-fix`／`should-fix`／`leave-as-is` の三段階トリアージ案
6. `must-fix` 候補ごとの平易な説明、候補案、各案の利点と弱点、後段影響、推薦案
7. proxy_model に判断させる場合の対象 finding／cluster、判断範囲、不可逆操作（commit／push／spec.json 更新／フェーズ移行）を含まないこと

variant が未確定、または role 割当が曖昧な場合は review-run を開始しない。既定 variant が CLI 経路を含む等、実行環境と合わない場合は、設定ファイルを読んで候補 variant と role 割当を利用者へ説明し、選択理由を review-run 記録に残す。

**役割分担**：

1. メインセッション LLM は raw レビューを集約し、三段階トリアージの下書きを作る。parsed YAML だけでなく raw response も読み、同根所見をまとめ、`must-fix` ／ `should-fix` ／ `leave-as-is` の候補を作る
2. メインセッション LLM は重要件ごとに、平易な問題説明、候補案、各案の利点と弱点、後段影響、推薦案を作る
3. proxy_model は重要件の採用案・判断理由・最終ラベルを決定する。実装は担当しない
4. メインセッション LLM は proxy_model の raw response を保存し、`decisions/<suffix>.yaml`（重要件ごとの裁定 file。`<suffix>` は `<model>-<role>-<連番>`）と `proxy-approval.yaml` に構造化する
5. 機械ガードは proxy decision の充足を検査する。未判断、raw 欠落、候補案欠落、採用案欠落、判断理由欠落、triage 最終ラベルとの不一致があれば実装へ進まない
6. メインセッション LLM は機械ガード通過後、採用された修正だけを TDD で実装する
7. コミット・プッシュ・spec.json 更新・フェーズ移行は人間の明示承認を要求する。proxy_model はこれらの不可逆操作を代行しない

**重要件の判定閾値**：

- `must-fix`、`ERROR`、`CRITICAL` は必ず重要件として扱う
- `should-fix` でも、上流仕様、データ契約、機械ガード、証跡保持、ワークフロー権限境界、複数モデルの同根指摘に関わるものは重要件として扱う
- 同根指摘とは、複数モデルの所見が同じ対象ファイル・同じ出力契約・同じ機械ガード・同じ証跡・同じ原因に触れているものをいう。表現が異なっても、対象または原因が一致する場合は同根として扱う
- 正本削除、機械ガード削除、重要件閾値の引き下げ、承認証跡の削除、検証対象範囲の縮小は、コミット等と同じく人間の明示承認を要する不可逆操作として扱う
- 判断に迷うものは重要件側に倒し、proxy_model 判断または人間判断へ回す

**proxy_model への入力証跡**：

- proxy_model へ渡す判断材料には、メインセッション LLM の要約だけでなく、元 review raw への参照または抜粋を必ず含める
- proxy_model への判断プロンプト（review-run 直下に保存）を作成する前に、[[llm-as-judge-prompting]] の手順（材料揃え → 問い設計 → 選択肢なし分析）でプロンプトを設計する
- 判断プロンプト（review-run 直下。既定名 `proxy-adjudication-prompt.md`、実行時に指定可）に、元 review raw 参照、問題説明、候補案セット、推薦案、判断してほしい最終ラベルを保存する
- `decisions/<suffix>.yaml`（重要件ごとの裁定 file。`<suffix>` は `<model>-<role>-<連番>`）には、`candidate_options`、`source_raw_paths`、`decision_prompt_path`、採用案、棄却案理由、判断理由、最終ラベルを保存する
- proxy_model が元 review raw を読めない形の判断材料しか受け取っていない場合、その decision は実装着手の承認証跡として扱わない
- 現行の軽量ガードは、proxy_model_id の文字列一致、decision file の finding_id 一致、final_label 一致、prompt/raw/候補案証跡の存在を検査する。API 署名や暗号学的な生成元証明は将来課題とする

**証跡配置**：

- `raw/`：各モデルの生応答
- `triage.yaml`：メインセッション LLM による三段階トリアージ
- `proxy-adjudication-prompt.md`（既定名。review-run 直下、実行時に指定可）：proxy_model に渡した判断材料
- `proxy-adjudication-response.txt`（既定名。review-run 直下、実行時に指定可）：proxy_model の生応答
- `decisions/<suffix>.yaml`：重要件ごとの採用案、判断理由、最終ラベル、棄却案理由
- `proxy-approval.yaml`：実装着手を許可する proxy approval record

**並列化可能な単位**：

- proxy_model への判断依頼は、同根所見クラスタ単位で並列化できる
- TDD 実装は、互いに同じファイルを更新しない実装単位、または入出力契約が独立しているタスク単位で並列化できる
- 共通スキーマ・共通ビルダー・同一ファイルを触る修正は直列で扱う
- 生成物、共有 helper、推移的契約、同じ出力 manifest、同じ traceability 出力を共有する修正は直列で扱う
- 並列実装の統合前に、メインセッション LLM が triage、proxy decision、テスト結果、ファイル差分を再照合する
- 並列処理で新しい判断問題が出た場合、その単位は停止し、proxy_model 判断または人間判断へ戻す
- 承認済み finding の実装中に見つけた未承認の便乗リファクタ、隣接挙動変更、対象外 cleanup は実施しない。必要なら新しい判断問題として停止する

**実装サブ担当 LLM の扱い**：

- 実装サブ担当 LLM は、原則として別スレッドかつ分離 worktree で扱う
- 同じ repo での並列実装は原則禁止し、読み取り調査または差分を残さない確認に限定する
- メインセッション LLM は、対象 finding、proxy decision、触ってよいファイル、期待テスト、禁止事項、停止条件を実装サブ担当へ渡す
- 実装サブ担当は、指定範囲外のファイル変更、判断変更、コミット、プッシュ、spec.json 更新、フェーズ移行を行わない
- 実装サブ担当が新しい判断問題、上流仕様への疑義、許可ファイル外の修正必要性を見つけた場合、その作業単位を停止してメインセッション LLM に戻す

**別スレッド生成物の扱い**：

- 別スレッド・分離 worktree で発生した生成物は、実装差分、検証結果、判断根拠、作業ノイズに分類する
- 実装差分は、メインセッション LLM が確認したうえで本線 worktree への取り込み候補にする
- 検証結果と判断根拠は、必要な要約だけを review-run、session record、または docs/notes に保存する
- 判断に影響した失敗試行、失敗パッチ、途中ログは work_noise から decision_basis へ昇格し、メインセッション LLM が要約または該当箇所を保存する
- 作業ノイズは本線 repo に取り込まない。作業ログ、一時メモ、途中のテスト出力、失敗パッチ案は原則としてサブ worktree 側に閉じる
- 本線へ戻す標準単位は、パッチ、テスト結果サマリ、未解決事項の 3 点とする

<a id="3.3-a-3"></a>

##### (a-3) 操縦 LLM 別の API 既定 variant と独立性原則（本節を正本とする）

セッションを操縦（起草・修正）する LLM と、その成果物を検証する LLM の系列を分離する。
自己レビューによる独立性低下を防ぐための原則であり、利用者承認済み
（設計記録 `docs/notes/2026-06-10-deployment-multi-llm-entry-design.md` §3.6、2026-06-11 個別承認）。
本節がこの原則と既定 variant 選択規則の正本である（仕様への昇格は実アプリ pilot 後に再検討、
MLE-DEC-004、2026-06-12 利用者決定）。

**独立性の原則**：

1. 単独検証役（1 体での post-write 検証など）は、操縦 LLM と別系列を必須とする
2. 3 役構成の adversarial（反証役）と judgment（判定役）は、操縦 LLM と別系列を必須とする
3. 3 役構成の primary（検出役）は、操縦 LLM と同系列を許容する（最終判定を持たず、
   残り 2 役の独立で全体の独立性が保たれるため）
4. proxy_model（人の判断の代行）は、操縦 LLM と別系列を必須とする

**操縦 LLM 別の既定 variant**（実体は `config/api-settings.yaml`）：

- **Claude Code 操縦時**：接尾辞なしの `*_independent_3way` 系
  （post_write_verification／yaml_audit／implementation_review の 3 用途。
  primary=anthropic/claude-sonnet-4-6、adversarial=openai/gpt-5.5、
  judgment=gemini/gemini-3.1-pro-preview）
- **Codex CLI 操縦時**：`*_independent_3way_codex_operator` 系
  （primary=openai/gpt-5.4、adversarial=anthropic/claude-opus-4-8、
  judgment=gemini/gemini-3.1-pro-preview）
- judgment（gemini-3.1-pro-preview）と小規模 1 体検証（`post_write_verification_google`）は
  両操縦で共用し、操縦を切り替えても判定基準の連続性を保つ
- 既存 variant の改名は行わない（規律文書・過去 run 記録・spec からの参照保全）。
  別の LLM が操縦する場合（将来）は同じ原則で役を回転して対応する

対象アプリ向けの同内容の案内は `templates/entry/AGENT_ENTRY.template.md` §10 と
`.reviewcompass/guidance/INITIAL_SETUP_LLM_GUIDE.md` にあり、本節と整合させて保守する。

#### (b) 波及（同フェーズ・他機能への影響）

- **発見されるタイミング**：triad-review 段（3 役が他機能との不整合に気づく）／ review-wave 段（機能横断レビュー）
- **処理する段**：**review-wave 段**（フェーズ終端の機能横断段、全機能の drafting ＋ triad-review 完了後に開始）
- **方法**：
  1. triad-review 段で波及と判定されたら **当該機能では対処せず**、carry-forward register に追記
  2. 「次の機能の drafting」に進む（個別機能の段では対処しない）
  3. 全機能の drafting ＋ triad-review が完了したら、review-wave 段で集約消化
  4. 影響を受ける全機能の仕様文書を一括修正（依存順を守る、例：foundation を先に修正してから runtime）
- **記録先**：`learning/workflow/carry-forward-register/reviewcompass-import.yaml` の各所見項目、消化後は `status: resolved` と `resolution` を更新

#### (c) 遡及（上流フェーズへの影響）

- **発見されるタイミング**：任意の下流段（triad-review／review-wave／alignment／approval のいずれか）
- **処理方法**：[REOPEN_PROCEDURE.md](REOPEN_PROCEDURE.md) の 4 過程手順を起動。当該段の作業を停止し、上流フェーズに戻る
- **手戻り種別判定**：N（intent）／R（requirements）／D（design）／A（tasks）／I（implementation）× 深さ 0〜4 の二次元表記で判定
- **再実施対象決定**：第1過程で trigger_map（再実施対象段の決定表）を参照して決める。actor=human の段（approval 等）に来たら作業を止めて承認待ち
- **記録先**：種別判定の根拠を `docs/reviews/reopen-classification-<日付>.md` に残す、機能単位 spec.json の `reopened` 履歴と `recheck` フラグを更新

#### (d) 遡及 ＋ 波及の組合せ

- **発見されるタイミング**：任意の下流段
- **処理方法**：reopen で上流フェーズに戻り、上流フェーズの review-wave 段で波及所見として集約消化、その後下流に伝播
  1. **第 1 段階**：reopen 手続きで上流フェーズに戻り、影響範囲を特定（trigger_map）
  2. **第 2 段階**：上流フェーズで carry-forward register に波及所見として追記し、当該フェーズの review-wave 段で消化
  3. **第 3 段階**：上流フェーズの alignment ＋ approval を再実施
  4. **第 4 段階**：下流フェーズの alignment ＋ approval を再実施（trigger_map で連鎖再実施対象として決定）
- **記録先**：reopen 記録 ＋ carry-forward register の両方

#### (e) leave-as-is と延期

- **leave-as-is**：判定役が「修正不要」と判断したもの。対処せず、レビュー記録に判定根拠を残すのみ
- **延期**：将来のフェーズで対処する判定。レビュー記録に延期理由と対処予定フェーズを残し、当該フェーズ着手時のチェックリストに追記

### 3.4 振り分け判断のフロー（triad-review 段で実施）

triad-review 段の判定役は、各所見について次の振り分けを行う：

```
所見発見
  ↓
当該機能の仕様修正のみで完結するか？
  ├── YES → 機能内対処（triad-review 段内で対処）
  └── NO
      ↓
  他機能の仕様修正も必要か？
  ├── YES（同フェーズ内のみ） → carry-forward register に追記、review-wave 段で処理
  ├── YES（上流フェーズに戻る必要あり、単機能） → reopen 手続きを起動
  └── YES（上流フェーズに戻る必要あり、複数機能） → reopen ＋ 上流の review-wave で集約処理
  
別判定：
  ├── 修正不要 → leave-as-is（記録のみ）
  └── 将来フェーズで対処 → 延期（チェックリスト追記）
```

### 3.5 段ごとの露出と処理段の対応表

| 段 | 主に露出する所見 | 当該段内で処理する所見 | 次段に持ち越す所見 |
|---|---|---|---|
| drafting | 起草中の自己発見 | 機能内（草案に直接反映） | なし |
| triad-review | 機能内 ／ 波及 ／ 遡及 | **機能内** のみ | 波及 → review-wave、遡及 → reopen |
| review-wave | 波及（横断ラウンド中の追加発見も） | **波及** | 遡及あり → reopen |
| alignment | 自動判定の不整合検出 | （自動判定が通過するまで前段に戻す） | 遡及あり → reopen |
| approval | 重大見落とし、利用者または別モデルによる指摘 | （承認しない） | reopen で上流戻し |

### 3.6 機能横断波及所見の管理ルール

- 各機能の triad-review 段で発見されたら、即時 carry-forward register に追記
- 追記項目：所見 ID（A-XXX 形式）、検出セッション、波及範囲（影響を受ける機能と仕様箇所）、対処方針、依存関係
- review-wave／alignment／approval の機能横断段着手時、全件を消化対象とする
- 消化後、各所見に「✅ 対処済み（YYYY-MM-DD、要件 review-wave）」ラベルを追加

## 4. サブエージェント方式の運用条件

### 4.1 位置づけ

- メインセッションは草案作成とレビュー結果の取りまとめを担う
- 3 役レビューは、メインセッションから分離された reviewer session または外部 API 検証者で実行する
- review-run の実行形は adapter と provider 設定に従う

### 4.2 モデル割り当て（規律）

3 役（主役・敵対役・判定役）は、メイン LLM から分離した実行主体が担う。メイン LLM は草案作成と三役レビュー結果の取りまとめのみを担い、3 役のいずれにもならない。

各役のモデルは `runtime/config/reviewcompass.yaml` または review-run の provider 設定で指定する。利用者が設定で変更できる。

**モデル能力配分の規律**：

- **主役と敵対役は必ず異なるモデルを使う**（敵対役の独立性確保のため）
- 判定役は主役または敵対役と同じモデルを使うことを許容する
- 敵対役と判定役には、反証生成と責務境界判断を担う十分な能力のモデルを割り当てる

### 4.3 サブエージェント呼び出し時の規律

- **プロンプトに自己完結性を持たせる**：サブエージェントは別 session で、メインの作業文脈を共有しない
- **参照文書の引用は事後検証**：サブエージェントの引用には節番号や参照先の誤りが発生しうる。メインセッションが grep やリンク検査で確認する
- **ファイル書き込みは原則禁止**：読み取りと分析のみ。例外的にレビュー記録の §2 や carry-forward register への追記提案を許容
- **モデル指定**：利用中の adapter が提供する model / provider 指定方法に従う。外部 API 経由では provider 設定を参照する

### 4.4 レビュー記録の必須フィールド

レビュー記録の front-matter に次を必須化：

```yaml
author:
  identity: <adapter_main_session>
  model: <model-id>
  role: drafter
reviewer:
  identity: <adapter_reviewer_session>
  model: <model-id>
  role: final_judgment
  separation_from_author: true
```

`author.identity` と `reviewer.identity` が異名であることを機械検査の対象とする。重要なのは provider 名ではなく、起草者と判定者が分離していることを記録できることである。

### 4.5 mode 値

レビュー記録の `mode` は `subagent_mediated`（正式値）。foundation のレビューモード語彙正本（Requirement 6 受入 6）の 3 値のうちのひとつ。

## 5. 利用者判断が必要な論点の見極め

### 5.1 利用者判断必須の項目

次のいずれかに該当する場合、LLM は単独で確定せず、利用者の明示承認を仰ぐ：

- **正本方針変更**：仕様・設計・タスク・運用規律の意味を変える修正
- **大規模再設計**：既存の責務境界、機械判定、成果物配置を大きく変更する場合
- **機能横断の権限分担**：複数機能にまたがる責務分担の決定（例：A-007 の self-improvement と workflow-management の権限調停）
- **判定境界の判断**：must-fix／should-fix／leave-as-is の境界が曖昧な場合
- **承認・コミット・push・フェーズ移行**：すべて利用者明示承認必須
- **作業の打ち切り・先送りの誘導**：利用者の明示承認なく「続きは次セッションで」等と作業を終了・先送りに誘導しない

### 5.2 LLM が自律的に決められる項目

- **抽出時のクリーニング作業の細部**（機能名置換、自己適用前提除去等）
- **観点 5（検証可能性）の機械判定可能な所見の指摘**
- **レビュー記録の構造化**（front-matter、節構成）

### 5.3 判断の記録規律

利用者判断の結果は次の場所に記録：

- **正本方針変更**：該当する仕様・設計・タスク・運用規律に決定日付付きで記載
- **機能横断対処方針**：carry-forward register の該当所見に対処方針として追記
- **重大論点**：レビュー記録の §1 主役レビュー、§4 統合の「利用者判断履歴」節に記録

### 5.4 セッション記録の作成規律

原則として毎セッション、セッション終了時または重要判断後に `docs/sessions/session-<N>-<YYYY-MM-DD>.md` を作成または更新する。特に、重要な判断・承認・レビュー結果・修正経緯が発生した場合は必須とする。これは会話全文の逐語ログではなく、後で経緯を確認できる要約記録とする。

`<N>` は `docs/sessions/` に存在する既存の最大セッション番号に 1 を加えた番号とする。同日の複数セッションでも番号を進め、同じ番号を再利用しない。
1 session につき 1 ファイルとし、同一 session 内で重要判断が複数回発生した場合は同じファイルへ追記する。重要判断ごとに別番号を消費しない。
並行セッションや未コミット作業により採番が衝突した場合、メインセッション LLM は既存記録・git 状態・未コミット差分を確認し、利用者が採番を確定するまで正式な新規セッション記録を作成しない。採番確定前に記録が必要な場合は、`docs/sessions/drafts/session-<YYYY-MM-DD>-<short-topic>.md` に一時草案を置き、正式番号確定後に `docs/sessions/session-<N>-<YYYY-MM-DD>.md` へ移動する。移動後は draft ファイルを残さず、正式ファイルに草案内容が統合済みであることを確認する。

メインセッション LLM はセッション記録の草案作成責任を持つ。利用者判断の引用・承認範囲・未確定事項に曖昧さがある場合は、記録前に利用者へ確認する。
コンテキスト切れや中断により当該 LLM が記録できない場合、次セッションが草案を引き継ぐ。草案がない場合は、TODO、review-run、approval record、git diff から経緯を再構成して記録する。

最低限、次を記録する：

- このセッションで実施した作業
- 利用者が承認した判断と、その対象
- API レビューや独立検証の結果と三段階トリアージ
- 修正した主要ファイルと検証結果
- 失敗・見落とし・再発防止に必要な気づき
- 次セッションへの引き継ぎ

推奨見出しは既存 session 記録と同型とし、最低限次を含める：

1. サマリ（このセッションでやったこと）
2. 気づき・特筆点
3. コミット一覧（該当する場合）
4. 次セッションへの引き継ぎ

`TODO_NEXT_SESSION.md` は次セッション向けの入口メモであり、詳細な経緯記録の正本ではない。詳細経緯は `docs/sessions/` に残し、TODO には必要な参照だけを置く。

## 6. コミット規律

### 6.1 コミット単位

- **正本文書更新 ＋ 基盤整備**：1〜2 コミット（方針確定、運用ファイル整備）
- **機能ごとに 1 コミット**：仕様文書 ＋ 運用文書 ＋ レビュー記録の 3 ファイル（または schema/template 等の関連ファイル）
- **機能横断段（review-wave／alignment／approval）**：1 コミット（複数機能の小修正をまとめる）

### 6.2 コミット順序

依存マップ順に従う：

1. foundation
2. runtime
3. evaluation
4. analysis
5. workflow-management
6. self-improvement
7. conformance-evaluation

### 6.3 コミットメッセージ規律

- **平易な日本語**：英語技術用語の連発を避け、完全な日本語の文で書く
- **題名**：機能名 ＋ 作業種別（例：「foundation 機能の requirements 抽出と 3 役レビュー」）
- **本文**：作成・更新ファイルの列挙、主な反映内容、機能横断所見の持ち越し有無
- **Co-Authored-By**：利用中の adapter と利用者方針に従う。自動付与を前提にしない

### 6.4 コミット前確認

- `git status` で対象ファイルを確認
- `git diff --cached` で内容確認（必要に応じて）
- `--no-verify` や `--no-gpg-sign` は使わない（規律）

### 6.5 不可逆操作の進行報告最小化

commit、push、spec.json workflow_state 変更、フェーズ移行などの不可逆操作では、利用者が操作を明示指示した後の正常系進行報告を原則として省く。LLM は必要な確認、stage、承認 record、guard、実操作、事後確認を実行してよいが、各内部手順を逐一会話へ説明しない。

途中報告を行うのは、利用者判断または追加承認が必要な場合に限る。例：承認 record の期限切れや対象不一致、precheck failure、post-write / reopen / in-progress による遮断、sandbox escalation が必要な場合、staged 内容が変わり再承認が必要な場合。

commit 中に、staged 内容の確定、承認内容を作り直す、既存 delegation を使い直す、nonce を更新する、といった内部再準備が必要になっても、それ自体を利用者に報告しない。これらは、承認済みの対象範囲内であり利用者判断を要しない通常手順として黙って実行する。コミット対象が増えた、staged 内容が変わった、または再承認が必要になった場合は内部再準備として隠さず、追加判断が必要な停止理由だけを短く報告する。利用者へ報告するのは、作業を続けられない異常、追加判断が必要な WARN / DEVIATION、または成功結果だけとする。

正常完了時の報告は、実行結果だけに絞る。commit なら commit hash、`git status` の clean 性、`next --json` の要点を示す。push なら push 先と結果、`git status` の clean 性を示す。詳細な手順ログ、precheck の全文、stage したファイル一覧、nonce / challenge の値は、利用者が求めた場合または失敗調査に必要な場合だけ示す。

### 6.6 push

push は **利用者明示承認**を仰いでから実行。LLM が自律的に push しない。

## 7. 作業完了時レポート

作業を終えて利用者へ返答するときは、adapter や利用モデルに依存しない会話末尾の運用契約として、最低限次を示す：

- **作業サマリ**：このターンで実施した変更、判断、未変更の範囲
- **検証結果**：実行したテスト、確認コマンド、`post_write_verification` の要否と結果
- **現在状態**：`git status` と `next --json` の要点
- **次タスク**：次に着手すべき具体的な作業、または workflow が要求する次 action

未実施・失敗・承認待ち・保留判断がある場合は、完了扱いにせず明記する。commit、push、workflow_state 更新、spec.json 更新などの不可逆または状態変更を伴う操作は、実際に成功した場合だけ作業サマリに記録する。

`next --json` が `post_write_verification`、`reopen_in_progress`、`resume_in_progress`、`unknown` など `completed` 以外を返している場合、次タスクには任意の改善候補ではなく、その workflow 状態に従う次 action を示す。

`next --json` が `completed` を返している場合、通常 workflow 上の次 action はない。このとき完了報告の次タスク欄に任意候補を書く場合は、次の順で拾う：

1. 利用者がこのターンで次作業を明示した場合は、その指示を次タスクにする。
2. 利用者指示がない場合は、`TODO_NEXT_SESSION.md` の「次にやること」にある推奨順を候補源にする。
3. 候補を表示する前に、`.reviewcompass/backlog/index.yaml` または候補ファイル本体で `status: candidate` であることを確認し、完了済み・存在しない・状態が矛盾する候補は次タスクとして出さない。
4. `TODO_NEXT_SESSION.md` の候補が古い、または候補を解決できない場合は、その旨を現在状態に書き、`.reviewcompass/backlog/index.yaml` の `status: candidate` から次候補を拾う。
5. 完了報告の次タスク欄では、確認できた候補を 5 件ほど、同じ順序でリスト表示する。各候補には、利用者が選べる程度の短い説明を 1 文で添える。
6. 利用者が「次の 1 件だけ」「最上位候補だけ」など 1 件表示を明示した場合に限り、確認できた最上位候補だけを次タスクとして示す。

completed 状態で候補を出す場合も、その候補はまだ開始済みではない。maintenance、reopen、新規 workflow、backlog TODO 実行のいずれとして開始するかは、利用者指示または開始前 preflight の結果で確定する。

### 7.1 進捗説明の平易化

進捗説明では、内部処理名をそのまま主文にせず、利用者が理解しやすい作業状態で述べる。まず次の順で短く示す：

1. 今どの段階か
2. 何をしたか
3. 次に何をするか

必要な場合だけ、内部用語を括弧で補足する。

完了報告や途中報告では、翻訳調の名詞句、英語混じりの見出し、内部状態名や英語の道具名を見出しや主語にしない。`next --json`、`commit wrapper`、`required_action`、`workflow_state` などの語は、利用者が判断するために必要な場合だけ、自然な日本語の説明の後ろへ括弧書きで添える。主文では「何を変えたか」「今どこで止まっているか」を自然な日本語で述べ、利用者が次に何をすればよいかを自然な日本語の文で示す。

避ける表現：

- 停止点を消費
- gate を通過
- required_action
- pending_gate
- workflow_state を更新
- commit wrapper を開始条件にする
- next --json は reopen_in_progress

言い換え例：

- 「tasks approval の停止点を消費」ではなく「tasks 段の承認を完了済みとして記録」
- 「implementation drafting を完了」ではなく「implementation 段のコードとテストを作成」
- 「次の required_action は run_reopen_pending_gate」ではなく「次は現在の段のレビュー作業」
- 「commit wrapper を最初から sandbox 外で実行」ではなく「コミット用の検査手順は、最初から許可された実行環境で動かす」
- 「next --json は reopen_in_progress」ではなく「やり直し手続きの途中で、次は requirements 段の確認を進める状態」

### 7.2 利用者操作が必要な停止点の表示

承認、コミット、push、判断など、利用者の短い返信で次へ進む停止点では、完了報告の末尾に次の 1 行を示す：

```text
次に必要な操作: <操作語>
```

`<操作語>` は、利用者がそのまま返信できる短い語にする。

例：

- `次に必要な操作: 承認`
- `次に必要な操作: コミット`
- `次に必要な操作: push`
- `次に必要な操作: 判断`

複数の選択肢が必要な場合だけ、候補を短く並べる。通常は候補を 1 つに絞る。内部用語、長い説明、手順ログをこの行に混ぜない。

このレポートは会話末尾の完了報告であり、workflow_state や `spec.json` の正本を代替しない。

## 8. 用語ガイド

### 8.1 「遡及」と「波及」

両用語は対象方向で使い分ける：

- **遡及（そきゅう）**：上流フェーズへの影響（時間軸＝過去方向）
- **波及（はきゅう）**：同フェーズ内の他機能への影響（横方向＝機能間）

両方とも正当な技術用語で、避けるべき／推奨という関係ではない。所見の性格を正確に表すために使い分ける。

### 8.2 判定値の使い分け

- **must-fix**：仕様の致命的または重要な欠落、修正必須
- **should-fix**：仕様の改善余地、修正推奨
- **leave-as-is**：仕様として問題なし、修正不要

### 8.3 機能内と機能横断

- **機能内対処**：当該機能の drafting 段で本セッション内に修正
- **機能横断持ち越し**：carry-forward register に集約、review-wave／alignment／approval の機能横断段で対処

### 8.4 サブエージェント関連

- **メインセッション**：作業の入口となる LLM session。草案作成とレビュー結果の取りまとめを担い、3 役レビューの判定者とは分離する
- **サブエージェント**：敵対役・判定役を実行する別 session または外部 API 検証者。利用中の adapter が利用可能な実行形に従う
- **mode = `subagent_mediated`**：サブエージェント方式のレビュー記録の mode 値

## 9. 関連文書

- ワークフローナビゲーション：[WORKFLOW_NAVIGATION.md](WORKFLOW_NAVIGATION.md)
- 事前検査：[WORKFLOW_PRECHECK.md](WORKFLOW_PRECHECK.md)
- reopen 手順：[REOPEN_PROCEDURE.md](REOPEN_PROCEDURE.md)
- 抽出進捗：[../../docs/extraction-mapping.md](../../docs/extraction-mapping.md)
- 機能横断波及所見：正本 [../../learning/workflow/carry-forward-register/reviewcompass-import.yaml](../../learning/workflow/carry-forward-register/reviewcompass-import.yaml)、履歴 source [../../learning/workflow/carry-forward-register/sources/reviewcompass-pending-cross-feature-findings.md](../../learning/workflow/carry-forward-register/sources/reviewcompass-pending-cross-feature-findings.md)
- レビュー記録雛形：[../../templates/review/manual_dogfooding_review_template.md](../../templates/review/manual_dogfooding_review_template.md)
- TODO：[../../TODO_NEXT_SESSION.md](../../TODO_NEXT_SESSION.md)

## 10. 本ガイドラインの改訂規律

- 本ガイドラインは運用文書として更新可能
- セッションの経緯記録は `docs/sessions/` に残し、本文書には現行の運用契約だけを置く
- 規律変更（§2〜§8）は利用者明示承認後に反映
- 改訂時は最終更新日付を更新
```

### .reviewcompass/guidance/WORKFLOW_NAVIGATION.md

content_mode: full_text
content_sha256: f264a762f6bde2e6a2702a5c9219d89b611ced5328be4db65e66ccba23a4c269

```text
# ReviewCompass ワークフローナビゲータ共通手引き

この文書は、`tools/check-workflow-action.py next --json` の読み方を定める共通手引きである。

## 1. 最初に実行するコマンド

作業を始める前、または次に何をするかを提案する前に、必ず次を実行する。

```bash
python3 tools/check-workflow-action.py next --json
```

出力 JSON の `next_action.kind` を、現在の作業順序・優先順位の正本として扱う。記憶、要約、TODO の候補欄だけを段取りの根拠にしない。

`next_action.required_disciplines` がある場合は、作業直前にそのファイルだけを読む。セッション開始時に長い規律群を一括で読んで記憶に頼るのではなく、機械判定された場面ごとの短い規律セットで挙動を調整する。対応表は `.reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml` を正本とし、`next --json` はその内容を機械可読に展開する。

`next_action.required_inputs` がある場合は、規律ではなく作業対象ごとの状態入力として扱う。`id`、`source_type`、`read_policy` を確認し、`path` がある場合でもファイル名そのものを一般規律に昇格しない。たとえば持ち越し台帳は、配布先プロジェクトごとに別ファイル、外部台帳、または未配置になり得るため、`unresolved_cross_scope_items` のような抽象入力として扱う。

機械可読な判定点では、判定点ごとに 1 本の effective prompt を読む。複数の元資料を直接ばらばらに読ませるのではなく、判定点に必要な規律・入力・次タスク方針を 1 本へ束ねた effective prompt を作り、その本文を LLM に読ませる。元資料は `prompt_source_refs` として保持し、実際に読ませた統合プロンプトは `effective_prompt_path`、`effective_prompt_sha256`、`effective_prompt_loaded` で記録する。全判定点で同じ巨大な共通プロンプトを使わず、各判定点に必要な短い effective prompt を使う。

## 1.1 作業モード分類の用語表（work mode taxonomy）

作業者は、maintenance、side-track、blocking unit、reopen、post-write verification を単一 enum に押し込まない。これらは同列の「作業モード」ではなく、次の軸を組み合わせて説明する。

| 用語 | 意味 |
| --- | --- |
| `current_state` | `next --json` が返す機械状態。例：`completed`、`maintenance_in_progress`、`blocking_unit_in_progress`、`post_write_verification`。 |
| `work_class` | これから行う手続きの種類。例：normal workflow、maintenance、reopen、verification。maintenance は作業区分であり、作業内容ラベルや親子関係ではない。 |
| `control_relation` | 本線・親作業との関係。例：mainline、side-track、blocking-unit、parent-resume。side-track は本線との関係であり、maintenance と同列の状態名ではない。blocking unit は親作業に束縛された制御構造である。 |
| `permitted_scope` | 作業宣言の属性。`allowed_scope`、`allowed_files`、`completion_conditions` で、どこまで触ってよいかと戻る条件を表す。 |
| `work_context` | workflow state が `completed` でも残り得る実作業上の文脈。active anchor、side-track stack、return target など、戻り先や親子関係を会話記憶ではなく構造化記録から説明するために使う。 |

例：`next --json` が `completed` を返していても、利用者が検査器の局所修正を求めた場合は、`current_state=completed`、`work_class=maintenance`、`control_relation=mainline` または `side-track`、`permitted_scope=allowed_files と completion_conditions` と分けて説明する。`audit` のような作業内容ラベルを、`current_state` や `control_relation` の値として扱わない。

## 2. 判定結果の共通分岐

<a id="resume_in_progress"></a>

### `resume_in_progress`

`stages/in-progress/` に進行中手続きがある。新しい作業を始めず、`next_action.file` に示された進行中ファイルを読む。

<a id="parent_resume_pending"></a>

### `parent_resume_pending`

blocking unit が完了し、戻り先の parent unit へ復帰する必要が残っている。新しい作業を始めず、`next_action.parent_unit_id` と `next_action.completed_unit_id` を確認し、まず parent unit の作業文脈へ戻る。

`parent_resume_pending` が出ている状態で、利用者から別作業への明示的な割り込み指示があった場合は、開始前に次を実行して、active unit と resume pending の有無を機械的に確認する。

```bash
python3 tools/check-workflow-action.py work-unit preflight-start \
  --proposed-unit-id <開始候補 unit ID> \
  --title "<開始候補の題名>" \
  --reason "<開始候補の理由>" \
  --json
```

`start_allowed: false` の場合は、`blocking_reasons` を利用者へ示して停止する。理由を見ずに通常 workflow、maintenance、新しい blocking unit へ進まない。

<a id="blocking_unit_required"></a>

### `blocking_unit_required`

別作業として切り出すべき作業が検出されている。通常 workflow や親作業を続けず、`next_action.proposed_unit` の `unit_id`、`title`、`reason`、`parent_unit_id`、`return_conditions` を確認してから、利用者の明示的な開始指示を待つ。

機械化が完全に揃うまでは、blocking unit の開始を暗黙に扱わない。開始前に、少なくとも次を会話上で明示する。

- blocking unit に入ること。
- 親作業の識別子。
- blocking unit の目的。
- blocking unit で変更してよい allowed files。
- 親作業へ戻るための完了条件。

宣言形式は次の形にそろえる。項目名を変えたり、本文中に散らして書いたりしない。

```text
blocking unit に入ります
- unit_id: <blocking unit ID>
- parent_unit_id: <親作業 ID>
- title: <短い題名>
- reason: <なぜ別作業として切り出すか>
- allowed_files: <変更してよいファイルまたはディレクトリ>
- return_conditions: <親作業へ戻るための完了条件>
```

`allowed_files` は必須であり、空欄や「必要な範囲」「関連ファイル」などの曖昧な指定では開始しない。開始時点で想定できるファイルまたはディレクトリを列挙し、途中で範囲を広げる必要が出た場合は、変更前に allowed files の追加を利用者へ明示する。親作業全体やリポジトリ全体を覆う指定は、混線防止の目的に反するため使わない。

`return_conditions` も必須であり、空欄や「完了したら」「必要なところまで」などの主観的な指定では開始しない。親作業へ戻ってよいかを確認できる条件を列挙し、少なくとも成果物、検証、commit または evidence の扱いを含める。blocking unit を出るときは、各条件を満たしたか、未達なら何を残件として親作業へ戻すかを明示する。

<a id="blocking_unit_in_progress"></a>

### `blocking_unit_in_progress`

blocking unit が active である。`next_action.unit_id` の作業だけを扱い、親作業の commit、push、post-write verification、TODO 整理へ横滑りしない。

機械化が完全に揃うまでは、作業者は次を手動で守る。

- 作業開始時と再開時に、現在の active blocking unit を確認する。
- commit 前に、commit unit が active blocking unit の `unit_id` と一致することを確認する。
- blocking unit 完了前に親作業の成果物を同じ commit に混ぜない。
- 親作業の commit は、blocking unit の完了条件を満たし、必要な commit または evidence を残し、親作業へ戻る宣言を終えるまで実行しない。
- blocking unit を出るときは、完了条件を満たしたこと、残件、親作業への戻り先を明示する。

<a id="reopen_in_progress"></a>

### `reopen_in_progress`

reopen 手続きが進行中である。通常ワークフローや post-write-verification より優先する。`next_action.file`、`next_step`、`completed_steps`、`pending_gates`、`current_blocker`、`required_action` を確認し、`required_action` に従う。

代表的な `required_action`：

- `draft_reopen_classification`：第1過程。種別判定・根拠記録。進行中ファイル発行と spec.json フラグ差し戻しは後続操作（`run_reopen_start`・`apply_approved_reopen_plan`）が担う。
- `repair_canonical_documents`：第2過程。上流フェーズの正本文書修正。
- `run_reopen_drafting`：第3過程。`next_pending_gate` が triad-review でも、同じ phase の drafting 完了が `drafting_completed_gates` または `completed_gates` に記録されていないため、先に正本文書を更新する。`active_gate`、`phase`、`stage: drafting`、`required_feature_scope` を確認し、レビューを開始しない。
- `run_reopen_pending_gate`：第3過程。drafting 完了記録がある、または次 gate が triad-review 以外であるため、`next_pending_gate` の gate を実行する。alignment / approval 連鎖の再実施を含む。
- `wait_for_human_decision`：人間の判断待ち。判断なしに進めない。
- `finalize_reopen`：第4過程。最終確認、recheck クリア、in-progress の完了処理。
- `repair_workflow_state`：判定不能または状態破損。推測で進めず利用者へ報告する。

<a id="maintenance_in_progress"></a>

### `maintenance_in_progress`

通常ワークフローではなく、ワークフロー制御・運用規律・検査器などの保守作業が進行中である。`next_action.file` を読み、`required_action`、`allowed_scope`、`completion_conditions` に従う。通常の `stage` や `upstream_recheck` へ戻るのは、maintenance の完了条件を満たし、進行中ファイルを `stages/completed/` へ移してからである。

`next_action` と異なる作業へ入る場合、または `next` 判定自体の欠陥を直す場合は、ファイル編集前に `stages/in-progress/maintenance-<日付>-<短い名前>.yaml` を作成する。少なくとも `trigger`、`mainline_blocked_by`、`work_class`、`control_relation`、`allowed_scope`、`allowed_files`、`completion_conditions` を記録し、side track であることを明示する。保守作業を side-track として始める場合は `work_class: maintenance`、`control_relation: side-track` を使う。これを省略すると、本筋の作業順序を守るための修復作業自体が、記録されない手順逸脱になる。

maintenance の進行中ファイルは、必要に応じて `workflow_steps`、`required_reviews`、`review_evidence`、`post_write_verification`、`completion_criteria` を持つ。`workflow_steps` は作業工程の完了状態、`required_reviews` は変更内容そのものに対する必要レビュー、`review_evidence` はそのレビューや確認の証跡、`post_write_verification` は正本文書などの書き込み後検証、`completion_criteria` は maintenance を完了へ移せる条件を表す。変更内容レビューと post-write verification は別工程として記録し、docs note だけの記録作業は code / SDD / guidance 変更と同じ厳格検証として扱わない。

`required_reviews` に未完了項目があれば `next --json` は `maintenance_review_required` を返す。`required_reviews` が完了し、`post_write_verification.status` が未完了なら `maintenance_post_write_required` を返す。これらが完了し、`completion_criteria` が記録されている場合は `maintenance_completion_required` を返し、maintenance ファイルを完了側へ移す作業へ進む。

本線 reopen 中の maintenance 完了 commit は、`stages/completed/maintenance-*.yaml` の `mainline_blocked_by` が現在の reopen in-progress ファイルを覆うことで許可される。本線 `stages/in-progress/reopen-*.yaml` は、maintenance のためだけに同伴 stage しない。

**maintenance を始める前の事前調査（in-progress YAML を作成する前に実施する）**

1. 変更対象ファイルと依存関係を確認し、影響範囲を特定する。
2. フィーチャー横断の影響がないことを確認する。
3. 先に解決すべきブロッカー（別の問題）が潜んでいないことを確認する。

事前調査の結果として次の開始条件をすべて満たした場合のみ maintenance を始める。

- 変更が局所的である（既存仕様境界を変えず、workflow 機構・承認・状態機械・`next --json` の意味を変えない）。
- 影響範囲が対象フィーチャーに閉じている。

いずれかを満たさない場合：

- 中核変更（仕様境界・workflow 機構を変える）の場合は reopen または新規 workflow として扱う。
- フィーチャー横断の影響がある場合は利用者にエスカレーションする。

開始条件を満たした場合、in-progress YAML を作成した後に最初に次の 3 行を宣言する。

```
変更分類: 局所
理由: <影響範囲と既存仕様境界への影響の説明>
手順: TDD 主導 / 文書のみ（lightweight self-check）
```

コード変更を伴う局所変更は TDD 主導（テスト先行）で進める。文書のみの変更は lightweight self-check で確認する。

### `reopen_classification_required`

完了済み workflow で、`intent`、feature-partitioning、`requirements`、`design`、`tasks` などの上流正本が後続成果物より新しい。単なる再確認として下流へ進めず、意味変更の有無と reopen 種別を分類する。`next_action.reopen_trigger` が候補を示す場合も、分類根拠を保存して `reopen-start` へ進む。

<a id="post_write_verification"></a>

### `post_write_verification`

書き込み後検証の対象となる未コミット変更がある。通常ワークフローへ進まず、`next_action.target_files` 全体を対象として検証する。

検証 manifest は `.reviewcompass/post-write-verification/*.yaml` に置く。`target_files`、`target_sha256`、`required_verifiers`、`completed_verifiers`、`unresolved_substantive_findings` を記録する。`verifications[]` がある場合、各 verifier は `target_files` 全体と対応する `target_sha256` を単一エントリで覆る必要がある。ファイルごとの分業は独立多重チェックではない。

API 経由の複数モデル検証を行う場合の標準手順：

```bash
.venv/bin/python3 tools/api_providers/prepare_post_write_review.py \
  --target <target-file> \
  [--target <target-file-2> ...] \
  --source-material .reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md \
  [--source-material <additional-source-material> ...] \
  --review-run-dir .reviewcompass/evidence/review-runs/<run-id> \
  --criteria-id <criteria-id> \
  --change-summary "<change-summary>" \
  --review-question "<review-question>"

.venv/bin/python3 tools/api_providers/run_review.py \
  --variant post_write_verification_google \
  --target <target-file> \
  [--target <target-file-2> ...] \
  --phase post_write_verification \
  --criteria-file .reviewcompass/evidence/review-runs/<run-id>/review-target.md \
  --prompt-manifest-path .reviewcompass/evidence/review-runs/<run-id>/prompt-manifest.yaml \
  --review-run-dir .reviewcompass/evidence/review-runs/<run-id>

.venv/bin/python3 tools/api_providers/review_triage.py list-pending \
  --review-run-dir .reviewcompass/evidence/review-runs/<run-id>

.venv/bin/python3 tools/api_providers/review_triage.py decide \
  --review-run-dir .reviewcompass/evidence/review-runs/<run-id> \
  --finding-id <finding-id> \
  --final-label must-fix \
  --decision-reason "<reason>" \
  --decision-actor human \
  --approval-record .reviewcompass/evidence/review-runs/<run-id>/approval.yaml

.venv/bin/python3 tools/api_providers/review_triage.py write-manifest \
  --review-run-dir .reviewcompass/evidence/review-runs/<run-id> \
  --out auto \
  --approval-record .reviewcompass/evidence/review-runs/<run-id>/approval.yaml

.venv/bin/python3 tools/check-workflow-action.py next --json
```

API 呼び出し起動手順の正本は、先に `.venv/bin/python3 tools/api_providers/prepare_post_write_review.py ...` で review-target と prompt manifest を生成し、その後 `.venv/bin/python3 tools/api_providers/run_review.py ... --criteria-file <review-target.md> --prompt-manifest-path <prompt-manifest.yaml>` を実行することである。外側から `zsh -c` で包まない。API key は配布物や設定ファイルへ書かず、利用者の shell 初期化で読み込まれる環境変数から渡す。Claude Code などの操縦実行面では、子プロセスの `ANTHROPIC_API_KEY` と `GEMINI_API_KEY` が空文字列へ上書きされることが確認済みである。一方、`OPENAI_API_KEY` は同じ確認では上書きされていない。このため `run_review.py` / `run_role.py` entrypoint 内で、環境変数が未設定の場合に `~/.zshrc` を読み直して API key を補完する。補完後も key が得られない場合は API key 未設定として fail-closed する。

`prepare_post_write_review.py` は `review-target.md`、`review-target.yaml`、`prompt-manifest.yaml` を同じ `--review-run-dir` に生成する。`review-target.md` には criteria ID、変更要約、検査質問、target files、source materials、target file contents、scope / out-of-scope、finding policy、機微情報チェック結果を含める。`prompt-manifest.yaml` には `review_prompt_materials.target_files` と `review_prompt_materials.source_materials` を `content_mode: full_text` と `content_sha256` 付きで記録する。機微情報らしい文字列を検出した場合、または prompt manifest audit が DEVIATION の場合は fail-closed し、外部 API review へ進まない。

`next_action.target_files` が複数ある場合は、`prepare_post_write_review.py` と `run_review.py` の両方で `--target` を複数回指定して同じ review-run に束ねる。API review-run の成否確認は、`review-target.md`、`review-target.yaml`、`prompt-manifest.yaml`、`review_summary.md`、`rounds.yaml`、`model-result-summary.yaml`、`raw/`、`parsed/`、`prompts/`、`target-manifest.yaml` が同じ `--review-run-dir` に生成され、`rounds.yaml` の `target_files`、`criteria_source_path`、`prompt_manifest_path`、provider、model、prompt/raw/parsed path が今回の対象と一致することで行う。

API 呼び出しが失敗した場合は、まず上の正本手順を再確認する。`import` エラー、`argparse` エラー、引数不一致は起動手順または実装の問題であり、外部送信ポリシーや provider 側障害と混同しない。`ConnectError`、名前解決失敗、接続不能が出た場合は sandbox network 制限の可能性を先に疑い、同じ正本コマンドをネットワーク実行が許可された実行面で再実行する。API key 未設定のエラーは `~/.zshrc` から対象 provider の環境変数が読み込まれているかを確認する。

`post_write_verification` では API 経路の variant を明示する。小規模既定は `--variant post_write_verification_google`、大規模または 3 系統検証が必要な場合は `--variant <post-write-api-variant>` として、`config/api-settings.yaml` の `context: post_write_verification` かつ API provider だけで構成された variant を選ぶ。CLI 経路を含む default variant に暗黙フォールバックしてはいけない。

API レビュー結果を得た場合は、raw 参照、モデル別要約、三段階トリアージ（`must-fix`／`should-fix`／`leave-as-is`）を利用者へまとめて提示する。`ERROR`／`CRITICAL` または最終判断 `must-fix` の重要件を `decide` する場合、または重要件を含む run から manifest を生成する場合は、承認を記録した `--approval-record` が必須である。承認レコードには `approved_by: user` または `approved_by: proxy_model`、`review_run_id`、`summary_presented_to_user: true`、`triage_presented_to_user: true`、`approved_finding_ids`、必要に応じて `approved_final_labels` を含める。`approved_by: proxy_model` の場合は、`proxy_model_id` と finding ごとの `proxy_decisions` を含め、各 decision file が raw response、候補案、採用案、判断理由、最終ラベルを保持する。

`write-manifest --out auto` は `.reviewcompass/post-write-verification/post-write-YYYY-MM-DD-NNN.yaml` の次番号を作る。manifest は post-write validation の途中記録ではなく、commit 直前の最終封印である。`triage.yaml` に `decision_status: human_required` が残る場合、重要件の利用者承認が確認できない場合、または review-run の target set に含まれない未コミット post-write target が残る場合は manifest を生成しない。manifest 作成後は対象ファイルを編集せず、stage / approval / commit へ直行する。

この生成停止条件は、現在の review-run から新しい最終 manifest を作る場合の規則である。既存の post-write manifest が現在の対象ファイルと一致し、かつ未解決の本質的指摘を含む場合は、`next --json` が `post_write_human_decision_required` と `next_action.manifest` を返す。

<a id="lightweight_self_check"></a>

### `lightweight_self_check`

notes / 履歴 / 判断材料の未コミット変更がある。通常ワークフローへ進まず、`next_action.target_files` を API post-write verification ではなく軽量自己精査で確認する。

軽量自己精査の対象は `docs/notes/` 配下と、単独変更の `TODO_NEXT_SESSION.md` とする。`docs/notes/` は議論記録、判断経緯、過去メモ、参考情報を置く場所として扱い、正本仕様・運用規律・レビュー判定そのものではないため、API review ではなく自己検査で確認する。`docs/operations/`、`docs/disciplines/`、`docs/reviews/`、`stages/completed/` は正本または完了記録として厳格に扱う。notes から正本へ昇格する内容は、該当する正本ファイルへ移した時点で strict な `post_write_verification` 対象とする。

`TODO_NEXT_SESSION.md` は更新頻度が高い次セッション導線であり、進捗整理・次タスク・現在状態の更新だけなら API review ではなく軽量自己精査で扱う。ただし、同じ未コミット差分に strict な `post_write_verification` 対象が含まれる場合は、TODO も同じ strict 検証の `target_files` に同梱する。

軽量自己精査では、API review を呼ばず、次だけを確認する。

1. 利用者の指摘内容を落としていないか。
2. 事実、推測、方針案、未実装事項が区別されているか。
3. 後で見たときに次の判断材料になるか。
4. 作業範囲を超えて仕様化していないか。
5. API review が必要な正本へ昇格していないか。

完了記録は `.reviewcompass/post-write-verification/*.yaml` に置き、`required_verifiers` と `completed_verifiers` は `lightweight_self_check` とする。`target_files` と `target_sha256` は通常の post-write manifest と同じく対象全体を覆う。

`post_write_verification` 対象と `lightweight_self_check` 対象が混在する場合は、`post_write_verification` を優先する。strict 側が完了した後、軽量対象が残っていれば `lightweight_self_check` を返す。

<a id="post_write_policy_violation"></a>

### `post_write_policy_violation`

post-write-verification pending 中に禁止変更がある。通常ワークフローへ進まず、`next_action.forbidden_files` を報告して停止する。禁止ファイルを勝手に削除・修正してはいけない。

現行実装では、post-write-verification 対象ファイルが未コミット変更に含まれる状態で、`tools/*.py`、`templates/`、または他の post-write 対象と混ざった `docs/disciplines/` 配下の変更があると逸脱になる。

<a id="post_write_human_decision_required"></a>

### `post_write_human_decision_required`

既存の post-write manifest に未解決の本質的指摘がある。通常ワークフローへ戻らず、`next_action.target_files` と `next_action.manifest` を確認し、利用者判断を待つ。

これは、現在の review-run で `triage.yaml` に `decision_status: human_required` が残ったまま新しい最終 manifest を生成する状態ではない。その場合は manifest 生成前に停止し、triage の判断または承認を先に解決する。

### `stage`

通常ワークフロー上の次タスクが決まっている。`feature`、`phase`、`stage` の示す作業だけを扱う。

`stage` が `triad-review` の場合、review-run の開始前に使用 variant と role ごとの path／provider／model を確定し、曖昧なまま開始しない。review-run に使うプロンプトは [[llm-as-judge-prompting]] の手順（材料揃え → 問い設計 → 選択肢なし分析）で設計する。API review-run 完了後は、proxy_model 判断依頼、実装修正、spec.json 更新、フェーズ移行のいずれにも進む前に、raw 参照、モデル別要約、同根所見クラスタ、`must-fix`／`should-fix`／`leave-as-is` の三段階トリアージ案、重要件の平易な説明を利用者へ提示して停止する。詳細手順は `.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2` を正本とする。

### `cross_feature_stage`

機能横断段に進む。`feature` は `all_features` になる。`recheck_items` がある場合は上流変更の織り込みを含める。`required_inputs` に `unresolved_cross_scope_items` があり、`unresolved_count` が 0 より大きい場合は、`read_policy` に従って未消化の持ち越し所見だけを確認する。ReviewCompass では互換情報として `pending_cross_feature_findings` も返るが、一般化された判断根拠は `required_inputs` とする。

自律・並列で機能横断段を試行する場合は、通常の review-wave 完了判定に入る前に `autonomous-plan` を作成し、`tools/check-workflow-action.py autonomous-plan <plan.yaml>` で検査する。計画には `recheck_items` と `stages/feature-dependency.yaml` から分かる依存を明示し、上流 recheck 対象を下流判断より先に置く。同じ worktree で並列化してよいのは読取調査または差分を残さない確認に限る。新しい依存、暗黙依存、未記録依存、または上流 recheck の下流反映が必要だと分かった場合、その作業単位は停止し、機能横断段の実施記録に blocked として記録してから統合判断へ戻す。

機能横断段の実施記録は、単一 feature 配下に置かず `.reviewcompass/specs/_cross_feature/reviews/` に置く。標準ファイル名は `.reviewcompass/specs/_cross_feature/reviews/{date}-{phase}-{stage}.md` とし、`feature: all_features`、対象 phase/stage、確認した feature 範囲、持ち越し件数、recheck 結果、実行した検証コマンド、判断結果を記録する。`_cross_feature` は実 feature ではなく、横断段成果物だけの名前空間である。

<a id="commit_stop_point"></a>

### `commit_stop_point`

通常 workflow の phase 終端または reopen 手続き上の停止点に到達している。`required_action: commit_stop_point` の場合、次 phase / 次 gate へ進まず、利用者の明示的な commit 指示を待つ。

利用者の短い操作語（例: `コミット`、`push`、`次へ`）を受けた場合は、mutation の前に `.venv/bin/python3 tools/check-workflow-action.py operation-trigger-resolve --trigger-text <text> --json` を実行し、`operation_id`、`operation_card_path`、`first_readonly_command`、`mutation_allowed_after` を確認する。`resolution_status: stop-and-ask` または `unknown_operation` の場合は、低レベルコマンドを推測実行せず利用者確認で停止する。

利用者が commit を指示した直後は、Git index への追加（`git add`）や approval record を作る前に `.venv/bin/python3 tools/check-workflow-action.py commit-preflight --json` を実行する。`DEVIATION` の場合は何も作らず停止し、理由と次に許可されている action だけを報告する。

通常 workflow では、`intent.approval` または `feature-partitioning.approval` が全 feature で完了し、該当 phase の workflow_state または成果物に未コミット変更がある場合に返る。`blocked_by.phase`、`blocked_by.stage`、`blocked_by.dirty_paths` を確認する。`commit-preflight` が `OK` を返した後に対象差分を `git add` し、guarded commit の通常手順へ進む。commit 後に作業ツリーが clean であれば、同じ停止点を返し続けず次 phase の action へ進む。

reopen 手続きでは、`reopen_in_progress` の `required_action: commit_stop_point` として返る。`blocked_by.kind` と `blocked_by.gate` を確認し、reopen 手続きファイルを含む停止点 commit を行う。

<a id="commit_mixing_risk"></a>

### `commit_mixing_risk`

commit unit が固定した対象外の staged file が混入している。通常 workflow、post-write verification、guarded commit へ進まず、`next_action.target_files`、`extra_staged_files`、`path` を確認する。

利用者に、対象外ファイルを別 commit unit / blocking unit へ分けるか、現在の commit unit を再作成してよいかを確認する。対象外ファイルを理由なしに同じ commit へ混ぜない。

<a id="commit_unit_stale"></a>

### `commit_unit_stale`

commit unit が現在の staged 内容と一致していない。通常 workflow、post-write verification、guarded commit へ進まず、`next_action.target_files` と `path` を確認する。

staged 内容を commit unit に合わせて戻すか、現在の staged 内容に合わせて commit unit を再作成する。古い commit unit のまま承認 record や commit execution delegation を作らない。

### `upstream_recheck`

完了済み workflow であっても、上流成果物が下流成果物より新しいため、下流へ進む前に再確認が必要である。`upstream_phase`、`phase`、`stage` を確認し、`phase.stage` に示された作業を次作業として扱う。たとえば intent 更新後は feature-partitioning の確認、requirements 更新後は design の再確認、tasks 更新後は implementation の再確認を先に行う。

この kind が返った場合、記憶や直前の会話から requirements、design、tasks、implementation へ飛ばない。必ず `next_action.phase` と `next_action.stage` に従い、上流から下流へ順に反映する。

<a id="feature_definition_required"></a>

### `feature_definition_required`

feature 一覧が解決できない（`feature-dependency.yaml` が見つからない、または `feature_order` キーが未定義）。対象アプリの初期状態で発生する。エラーではない（verdict OK）。

`next_action.reason`（立ち上げ案内の本文）と `current_state.feature_dependency_source`（解決元）を確認する。`feature_dependency_source` が null ならファイル自体が探索順（`.reviewcompass/feature-dependency.yaml` → `stages/feature-dependency.yaml` → `feature-dependency.yaml`）のどこにも存在せず、ファイルパスが入っていればそのファイルはあるが `feature_order` キーが未定義または不正である。前者は分割結果の記録から、後者は既存ファイルへの `feature_order` キーの追記から始める。

新しい作業を始めず、intent と feature-partitioning を実施し、承認された分割結果（機能ごとの依存の主張と理由、順序の導出を含む）を `.reviewcompass/feature-dependency.yaml` の `feature_order` キーに記録する。記録後に `next` を再実行する。feature 立ち上げの手順は `.reviewcompass/guidance/INITIAL_SETUP_LLM_GUIDE.md` を正本とする。

なお、`feature_order` と `depends_on` の整合違反（依存される機能が先に並んでいない、循環依存がある）は本 kind ではなく `unknown`／DEVIATION（fail-closed）になる。理由に従って `feature-dependency.yaml` を修正する。

### `completed`

全 workflow_state が完了している。通常の次タスクはない。

完了報告で「次タスク」を示す必要がある場合、ここでいう「通常の次タスクはない」とは、workflow_state が要求する次 action がないという意味である。backlog 候補、maintenance 候補、reopen 候補を提示してよいが、それらは workflow の自動継続ではなく、利用者が次に選べる作業候補として扱う。

候補を拾う順序と表示件数は `.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#7-作業完了時レポート` の completed 時の次タスク取得規律に従う。`TODO_NEXT_SESSION.md` の推奨順を候補源にする場合でも、候補が現在も `status: candidate` であることを `.reviewcompass/backlog/index.yaml` または候補ファイル本体で確認してから表示する。完了報告では、利用者が 1 件表示を明示した場合を除き、5 件ほどを短い説明つきの選択肢として示す。

利用者指示により maintenance、reopen、または新規 workflow を開始できる。別作業を開始する前には、原則として `work-unit preflight-start` を実行し、`start_allowed` と `blocking_reasons` を確認する。maintenance を始める場合は、その後に `maintenance_in_progress` の事前調査と開始条件を確認する。

**completed からの作業開始分類**

| 分類 | 使う条件 |
| --- | --- |
| maintenance | 局所的な運用・検査器・手引き補修で、既存仕様境界や workflow 機構の意味を変えない。 |
| reopen | 既存正本の意味変更や下流再実施が必要で、既存 feature の責務内に収まる。 |
| 新規 workflow | 既存 feature の責務境界に収まらない新しい責務を導入する。 |

判断が分かれる場合は候補だけを提示し、人間判断を待つ。候補のまま `stages/in-progress/maintenance-*.yaml` を作成したり、reopen-start や新規 workflow の正本作成へ進んだりしない。

### `unknown`

状態判定できない。推測で進めず、`reasons` と `current_state` を利用者へ報告する。

## 3. 共通禁止事項

- `next` を実行せずに次作業を提案しない。
- `resume_in_progress`、`parent_resume_pending`、`reopen_in_progress`、`post_write_verification`、`post_write_policy_violation`、`post_write_human_decision_required` を通常ワークフローより後回しにしない。
- `lightweight_self_check` を通常ワークフローより後回しにしない。
- `reopen_classification_required` を「再確認で足りる」と独断して下流成果物を更新しない。
- `next_action` と異なる side track に入る場合、または `next` 判定自体を修復する場合は、maintenance in-progress を作らずに編集を始めない。
- 事前調査を省略して maintenance を始めない。影響範囲・依存関係・ブロッカーの確認が済んでいない状態で in-progress YAML を作成しない。
- spec.json の workflow_state 変更、commit、push は不可逆操作として扱い、対応する precheck サブコマンドを実行する。
- 検証者は `target_files` 全体を見る。ファイルごとの分業を独立多重チェックとして扱わない。
- 本質的指摘を独断で逐語的指摘に落とさない。迷う場合は利用者へ上げる。
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
