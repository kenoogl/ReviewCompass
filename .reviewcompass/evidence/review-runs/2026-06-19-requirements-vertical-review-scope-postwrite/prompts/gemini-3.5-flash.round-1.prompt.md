prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.5-flash

# Task
Review the target document for the requested phase and criteria.

# Phase
post_write_verification

# Criteria
# Post-write Review Target

criteria_id: requirements_vertical_review_scope_post_write
phase: post_write_verification
generated_at: 2026-06-19T13:17:48.951278+00:00

## Change Summary

requirements triad-review の縦方向監査で、審査対象を requirements.md に限定し、design.md/tasks.md を参照資料として扱う規律と機械参照マップを追加した

## Review Question

今回の変更は、requirements review の review target/source materials/out of scope を明確にし、上流判断材料から requirements.md への意図伝達を検査する規律として十分か。design.md/tasks.md を誤って審査対象に含める余地、既存 design/tasks/implementation review 規律への退行、または workflow discipline map との不整合がないかを確認してください。

## Target Files

- docs/operations/SESSION_WORKFLOW_GUIDE.md sha256=dc879a5cc1565096854be2b8ae2120c79593fc0ee4c936b054f9fbf3ccdec246
- docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml sha256=6c6985ecc0741f138365e8c0a0a665ee4efda49d667946c05a197161205a2364

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
The top-level key must be exactly findings.
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

If there are no findings, return exactly:

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
docs/operations/SESSION_WORKFLOW_GUIDE.md
docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml

# Target document
## docs/operations/SESSION_WORKFLOW_GUIDE.md

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

2. **`docs/operations/WORKFLOW_NAVIGATION.md`**（次 action 判定）
   - `tools/check-workflow-action.py next --json` の読み方
   - 判定点ごとの required disciplines / required inputs / effective prompt の扱い

3. **`docs/operations/WORKFLOW_PRECHECK.md`**（機械判定の入口）
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
- **approval**：人間または別モデルによる承認段（actor=human または proxy_model）

drafting と triad-review を別段にする理由は、誰が何をしたかを段単位で明確に記録し、草案作成者と判定者の分離を機械検査可能にするためである。

<a id="vertical-intent-transfer-review"></a>

### 2.2.1 上流意図伝達の必須検査

各 phase の triad-review／review-wave／alignment では、対象 phase の成果物だけでなく、上流成果物または上流判断材料からの意図伝達を必須検査項目とする。review prompt は、少なくとも「上流の目的・責務境界・受入条件・禁止事項が、対象成果物へ欠落・弱体化・逸脱・未根拠追加なく引き継がれているか」を問わなければならない。

- **requirements review**：`上流判断材料 → requirements.md` を確認し、reopen 分類根拠、利用者判断、計画メモ、設計メモなどの目的・責務境界・受入条件・禁止事項が要件へ欠落なく落ちているかを検査する。design.md / tasks.md は参照資料であり、審査対象ではない
- **design review**：`requirements.md → design.md` を確認し、要件の目的・境界・受入条件が設計へ欠落なく落ちているかを検査する
- **tasks review**：`requirements.md → design.md → tasks.md` を確認し、要件と設計の意図が implementation-ready なタスク粒度へ落ちているかを検査する
- **implementation review**：`requirements.md → design.md → tasks.md → implementation` を確認し、実装がタスクだけでなく上流意図から逸脱していないかを検査する

review prompt は、review target / source materials / out of scope を明示する。審査対象は現在 phase の成果物に限定し、source materials は背景・意図伝達確認のための参照資料として扱う。下流 phase の成果物が source materials に含まれる場合でも、その correctness を現在 phase の review で判定してはならない。

tasks review では、単に tasks.md の粒度や項目数を見るだけでは不十分である。たとえば T-016〜T-019 を審査する場合は、Requirement 13〜16 の意図が design.md の設計判断を経由して、欠落・弱体化・勝手な追加なしに implementation-ready な作業単位へ落ちているかを必須で確認する。

### 2.3 段の進め方の規律

- **drafting 段の草案完成** → 当該機能の triad-review 段に進む（機能単位で逐次進行）
- **triad-review 段で 3 役レビューと機能内対処** を完了 → 当該機能の drafting／triad-review がそろう
- **全機能で drafting ＋ triad-review を完了** してから review-wave に進む（部分的に review-wave を始めない）
- **review-wave の所見を消化** してから alignment に進む
- **alignment で LLM 自動判定** を通過してから approval に進む
- **approval で利用者または別モデル承認** を得てから次フェーズに進む

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
4. メインセッション LLM は proxy_model の raw response を保存し、`proxy-decisions/<finding-id>.decision.yaml` と `approval-proxy-<日付>.yaml` に構造化する
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
- `proxy-decisions/<finding-id>.prompt.md` を作成する前に、[[llm-as-judge-prompting]] の手順（材料揃え → 問い設計 → 選択肢なし分析）でプロンプトを設計する
- `proxy-decisions/<finding-id>.prompt.md` に、元 review raw 参照、問題説明、候補案セット、推薦案、判断してほしい最終ラベルを保存する
- `proxy-decisions/<finding-id>.decision.yaml` には、`candidate_options`、`source_raw_paths`、`decision_prompt_path`、採用案、棄却案理由、判断理由、最終ラベルを保存する
- proxy_model が元 review raw を読めない形の判断材料しか受け取っていない場合、その decision は実装着手の承認証跡として扱わない
- 現行の軽量ガードは、proxy_model_id の文字列一致、decision file の finding_id 一致、final_label 一致、prompt/raw/候補案証跡の存在を検査する。API 署名や暗号学的な生成元証明は将来課題とする

**証跡配置**：

- `raw/`：各モデルの生応答
- `triage.yaml`：メインセッション LLM による三段階トリアージ
- `proxy-decisions/<finding-id>.prompt.md`：proxy_model に渡した判断材料
- `proxy-decisions/<finding-id>.raw.txt`：proxy_model の生応答
- `proxy-decisions/<finding-id>.decision.yaml`：採用案、判断理由、最終ラベル、棄却案理由
- `approval-proxy-<日付>.yaml`：実装着手を許可する proxy approval record

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
`docs/operations/INITIAL_SETUP_LLM_GUIDE.md` にあり、本節と整合させて保守する。

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

### 7.1 進捗説明の平易化

進捗説明では、内部処理名をそのまま主文にせず、利用者が理解しやすい作業状態で述べる。まず次の順で短く示す：

1. 今どの段階か
2. 何をしたか
3. 次に何をするか

必要な場合だけ、内部用語を括弧で補足する。

避ける表現：

- 停止点を消費
- gate を通過
- required_action
- pending_gate
- workflow_state を更新

言い換え例：

- 「tasks approval の停止点を消費」ではなく「tasks 段の承認を完了済みとして記録」
- 「implementation drafting を完了」ではなく「implementation 段のコードとテストを作成」
- 「次の required_action は run_reopen_pending_gate」ではなく「次は現在の段のレビュー作業」

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
- 抽出進捗：[../extraction-mapping.md](../extraction-mapping.md)
- 機能横断波及所見：正本 [../../learning/workflow/carry-forward-register/reviewcompass-import.yaml](../../learning/workflow/carry-forward-register/reviewcompass-import.yaml)、履歴 source [../../learning/workflow/carry-forward-register/sources/reviewcompass-pending-cross-feature-findings.md](../../learning/workflow/carry-forward-register/sources/reviewcompass-pending-cross-feature-findings.md)
- レビュー記録雛形：[../../templates/review/manual_dogfooding_review_template.md](../../templates/review/manual_dogfooding_review_template.md)
- TODO：[../../TODO_NEXT_SESSION.md](../../TODO_NEXT_SESSION.md)

## 10. 本ガイドラインの改訂規律

- 本ガイドラインは運用文書として更新可能
- セッションの経緯記録は `docs/sessions/` に残し、本文書には現行の運用契約だけを置く
- 規律変更（§2〜§8）は利用者明示承認後に反映
- 改訂時は最終更新日付を更新


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
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
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
        - docs/disciplines/discipline_approval_operation.md
      effective_prompt_policy: one_effective_prompt_per_decision_point
    - id: proxy_decision_file
      prompt_source_refs:
        - docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
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

