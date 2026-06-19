prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.5-flash

# Task
Review the target document for the requested phase and criteria.

# Phase
post_write_verification

# Criteria
# Post-write Review Target

criteria_id: codex_commit_and_user_report_discipline_post_write
phase: post_write_verification
generated_at: 2026-06-19T15:31:54.516042+00:00

## Change Summary

Codex のコミット実行環境と利用者向け報告文の規律を明確化した

## Review Question

変更した運用文書が、Codex のコミットは最初から許可された実行環境で行うこと、および利用者向け報告を自然な日本語で書くことを矛盾なく規律化しているか。既存手順との衝突や不足があれば指摘すること。

## Target Files

- docs/operations/COMMIT_OPERATION_CARD.md sha256=afde19bc53d79558f0cc44988daec39e7a8b3de1c45426d8810d4ebe90234d23
- docs/operations/SESSION_WORKFLOW_GUIDE.md sha256=3d35d9924e08e199700a45d8a6f083da1c168a74ec2560890b6fd054c78ca755
- docs/operations/WORKFLOW_NAVIGATION_FOR_CODEX.md sha256=d7e259963e7bc784b793313974bc237a6f78bb56c2026e19e47e1e02a6032ca3
- docs/operations/WORKFLOW_PRECHECK_DETAILS.md sha256=85fbf5b6bd8d63ab99b2756e44973ec2dbbac6bea3872fa85df000bb65d3a7cd

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
docs/operations/COMMIT_OPERATION_CARD.md
docs/operations/SESSION_WORKFLOW_GUIDE.md
docs/operations/WORKFLOW_NAVIGATION_FOR_CODEX.md
docs/operations/WORKFLOW_PRECHECK_DETAILS.md

# Target document
## docs/operations/COMMIT_OPERATION_CARD.md

<a id="commit-operation-card"></a>

# COMMIT_OPERATION_CARD

commit 操作カード

最終更新: 2026-06-20

このカードは commit 直前に読む短い実行手順である。仕様説明ではなく、操作事故を防ぐための実行カードとして扱う。詳細契約は `WORKFLOW_PRECHECK.md` と `WORKFLOW_PRECHECK_DETAILS.md` を参照する。

## 手順

1. 利用者の単発 commit 指示を commit 操作の開始条件として扱う。
2. `git add` 後、staged 対象を確認する。
3. `.venv/bin/python3 tools/check-workflow-action.py commit-approval prepare --json` を単独で実行する。
4. `commit-approval prepare` と `commit --json` precheck を並列実行しない。
5. 返された nonce を使い、すぐに `tools/guarded-git-commit.py --approval-nonce <nonce> --approval-source-text-line-stdin` を起動する。
6. challenge 作成後は、staged index や承認状態を変え得る別コマンドを挟まない。
7. `--approval-source-text-line-stdin` は TTY からの対話入力でだけ使う。
8. 空 stdin、pipe、heredoc、redirect、LLM が生成した `printf` 等の承認文では実行しない。
9. guarded commit が承認入力待ちになってから、直近の利用者発話で明示された commit 指示を 1 行として渡す。この 1 行は staged 内容承認と LLM commit 実行代行承認の source である。
10. 失敗時は、まず承認入力経路、challenge 状態、staged digest の一致を確認する。

## Codex

Codex で `--approval-source-text-line-stdin` を使う場合は、PTY で guarded commit を起動し、入力待ちになってから、直近の利用者発話で明示された commit 指示だけを `write_stdin` で渡す。この 1 行を staged 内容承認と LLM commit 実行代行承認として扱う。利用者発話なしに Codex / Claude / LLM が承認文を生成してはならない。Codex の `workspace-write` sandbox では、commit wrapper 本体を最初から sandbox 外（`require_escalated`）で実行する。これは guard を迂回する手順ではなく、承認レコード、staged 内容照合、commit gate を同じ wrapper 内で通したうえで、git index 書き込みだけを許可された実行面で行うための運用である。先に sandbox 内で失敗させてから再実行する手順を標準にしない。

## Claude Code

Claude Code で `--approval-source-text-line-stdin` を使う場合は、TTY からの対話入力でのみ使う。直近の利用者発話で明示された commit 指示は staged 内容承認と LLM commit 実行代行承認として扱い、別の承認語の再入力を求めない。空 stdin での実行は challenge invalidation（承認無効化）を起こすため、非対話・空入力で実行しない。

## 禁止

- challenge 作成後に、承認 record や staged index を変える別コマンドを挟む。
- `--approval-source-text-line-stdin` を stdin なし、pipe、heredoc、redirect で実行する。
- LLM が `printf` 等で承認文を生成して commit approval / execution delegation を作る。
- commit 実行後に結果確認なしで完了扱いにする。


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

source materials をパス名だけで列挙してはならない。縦方向監査の review prompt には、判断に必要な上流本文または要点抽出を、モデルが推測せず読める形で含める。要点抽出を使う場合は、少なくとも上流の目的、責務境界、受入条件、禁止事項、未確定事項、対象 phase へ引き継ぐべき判断を分けて記録する。上流資料を読んでいない場合は review-run を開始してはならない。prompt 内で上流資料の中身が確認できない場合も review-run を開始してはならない。

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
- 抽出進捗：[../extraction-mapping.md](../extraction-mapping.md)
- 機能横断波及所見：正本 [../../learning/workflow/carry-forward-register/reviewcompass-import.yaml](../../learning/workflow/carry-forward-register/reviewcompass-import.yaml)、履歴 source [../../learning/workflow/carry-forward-register/sources/reviewcompass-pending-cross-feature-findings.md](../../learning/workflow/carry-forward-register/sources/reviewcompass-pending-cross-feature-findings.md)
- レビュー記録雛形：[../../templates/review/manual_dogfooding_review_template.md](../../templates/review/manual_dogfooding_review_template.md)
- TODO：[../../TODO_NEXT_SESSION.md](../../TODO_NEXT_SESSION.md)

## 10. 本ガイドラインの改訂規律

- 本ガイドラインは運用文書として更新可能
- セッションの経緯記録は `docs/sessions/` に残し、本文書には現行の運用契約だけを置く
- 規律変更（§2〜§8）は利用者明示承認後に反映
- 改訂時は最終更新日付を更新


## docs/operations/WORKFLOW_NAVIGATION_FOR_CODEX.md

# Codex 作業用：ReviewCompass ワークフローナビゲータの使い方

この文書は、Codex が ReviewCompass の開発作業を始める前に読むための adapter 手引きである。

共通の `next_action` の読み方は `docs/operations/WORKFLOW_NAVIGATION.md` を正本とする。本書は Codex 環境に固有の制約だけを補う。

## 1. 起点

作業開始前、または次に何をするかを提案する前に、必ず次を実行する。

```bash
python3 tools/check-workflow-action.py next --json
```

その後、`next_action.kind` は `docs/operations/WORKFLOW_NAVIGATION.md` に従って読む。

## 2. Codex 固有の作業規則

1. `AGENTS.md` をプロジェクト内の Codex 向け入口規律として扱う。
2. Claude memory が自動ロードされる前提を置かない。必要な規律本文は repo 内 `docs/disciplines/` を読む。
3. repo 外 memory への書き込みを前提にしない。memory 相当の永続記録が必要な場合は、まず記録先と内容を利用者へ提示し、明示承認を得る。
4. filesystem sandbox と approval の制約を守る。外部 API、ネットワーク通信、repo 外書き込み、破壊的操作は、許可が必要な場合に承認を得てから実行する。
5. commit と push は利用者の運用方針に従う。「次のコミットまで自律実行」は commit 停止点まで進めて止まる指示であり、commit 実行代行は含まない。停止点到達後、利用者の単発 commit 指示（例：`コミット`）は、提示済みまたは直後に stage する対象への staged 内容承認と LLM commit 実行代行承認として扱う。最初から commit も含めて自律実行する場合は、「コミット代行も含めて自律実行」のように commit 実行代行を含むことを明示する。commit 直前は `docs/operations/COMMIT_OPERATION_CARD.md` を読み、共通手順は同カードに従う。Codex では `commit-preflight`、stage、nonce prepare、guarded commit を同一ターンで逐次実行し、`tools/guarded-git-commit.py --approval-nonce <nonce> --approval-source-text-line-stdin` を PTY で起動する。承認入力待ちになってから、直近の利用者発話で明示された commit 指示だけを `write_stdin` で渡す。利用者発話なしに Codex が承認文を生成してはならない。Codex の `workspace-write` sandbox では、commit wrapper 本体を最初から sandbox 外（`require_escalated`）で実行する。これは guard を迂回する手順ではなく、承認レコード、staged 内容照合、commit gate を同じ wrapper 内で通したうえで、git index 書き込みだけを許可された実行面で行うための運用である。先に sandbox 内で失敗させてから再実行する手順を標準にしない。コミットメッセージは利用者指定があればそれを使い、指定がなければ staged 差分の主目的を 1 行の命令形または名詞句で要約する。
6. 通常の `next_action` と異なる side track に入るときは、作業前に `SIDE TRACK 開始: <名前>`、`本線停止理由`、`復帰条件` を利用者へ明示する。side track から抜けるときは、`SIDE TRACK 終了: <名前>`、`復帰先`、`next` の判定結果を明示する。
7. docs/ 配下や `TODO_NEXT_SESSION.md` を書いた後は、`next` を再実行して結果を報告する。`post_write_verification` が返った場合は通常ワークフローへ戻らない。
8. post-write-verification pending 中に、再発防止や反省を目的として規律、TODO、テンプレート、hook、スクリプトを勝手に変更しない。必要なら提案して利用者の承認を待つ。
9. `.codex/hooks.json` と `.codex/hooks/` は Codex 側の hook 設定である。Claude Code の `.claude/` 設定とは分けて扱う。
10. `triad-review` の API review-run を開始する前に、使用 variant と role ごとの path／provider／model を利用者へ提示する。variant や role 割当が曖昧な場合は開始しない。
11. API review-run 完了後は、`SESSION_WORKFLOW_GUIDE.md#3.3-a-2` の利用者提示ゲートを完了するまで、proxy_model 判断依頼、実装修正、spec.json 更新、フェーズ移行へ進まない。

<a id="3-commit"></a>

## 3. commit

commit 直前は `docs/operations/COMMIT_OPERATION_CARD.md` を読む。Codex では利用者の単発 commit 指示を staged 内容承認と LLM commit 実行代行承認として扱い、`tools/guarded-git-commit.py --approval-nonce <nonce> --approval-source-text-line-stdin` を PTY で起動する。承認入力待ちになってから、直近の利用者発話で明示された commit 指示だけを `write_stdin` で渡す。利用者発話なしに Codex が承認文を生成してはならない。Codex の `workspace-write` sandbox では、commit wrapper 本体を最初から sandbox 外（`require_escalated`）で実行する。これは guard を迂回する手順ではなく、承認レコード、staged 内容照合、commit gate を同じ wrapper 内で通したうえで、git index 書き込みだけを許可された実行面で行うための運用である。先に sandbox 内で失敗させてから再実行する手順を標準にしない。

## 4. post-write-verification の扱い

Codex は `next_action.target_files` 全体を確認する。複数ファイルがある場合でも、ファイルごとの分業を独立多重チェックとして扱わない。

外部 API を使う検証は、利用者の明示承認または既に許可された既存コマンドがある場合だけ実行する。実行できない場合は、検証対象、必要な検証者数、実行しようとした手段、実行できない理由を報告して停止する。

## 5. Claude 固有資産の扱い

Claude 用の手引き、memory、`.claude/` hook、Claude Code session log converter は削除しない。Claude Code で再検証・比較実行するための adapter 資産として残す。

Codex 作業時に修正すべきなのは、「現在の作業者が必ず Claude Code である」と読める入口記述である。triad-review のモデル名としての `claude-*` や、過去セッション記録内の Claude 記述は履歴・モデル識別子として扱う。


## docs/operations/WORKFLOW_PRECHECK_DETAILS.md

# WORKFLOW_PRECHECK 詳細仕様

本文書は `tools/check-workflow-action.py`、`tools/commit-from-current-staged.py`、`tools/guarded-git-commit.py` の詳細仕様を定める。運用時に読む短い契約は [WORKFLOW_PRECHECK.md](WORKFLOW_PRECHECK.md) を正とし、本書は実装・保守・テストで必要な詳細を補う。

## 1. サブコマンド

```bash
tools/check-workflow-action.py spec-set <feature> <phase> <stage> <new-value> [--rationale "<理由>"]
tools/check-workflow-action.py commit-preflight
tools/check-workflow-action.py commit-approval prepare --json
tools/check-workflow-action.py commit-approval record --nonce <nonce> (--source-text-stdin|--no-source-text) [--json]
tools/check-workflow-action.py commit-approval delegate-execution --nonce <nonce> --source-text-stdin [--json]
tools/check-workflow-action.py commit-approval invalidate [--json]
tools/check-workflow-action.py commit --rationale "<理由>" [--execution-actor llm|human]
tools/check-workflow-action.py push --rationale "<理由>"
tools/check-workflow-action.py audit-commit <commit-ish>
tools/check-workflow-action.py reopen-advance-step --file <path> --from-step 1|2 --completed-step "<説明>" --rationale "<理由>" --evidence <path> [--evidence <path> ...]
tools/check-workflow-action.py reopen-advance-gate --file <path> --gate stages/<phase>.yaml#<stage> --decision <decision> --feature-scope <feature> --rationale "<理由>" --evidence <path> [--evidence <path> ...] [--completed-step "<説明>"] [--set-spec FEATURE PHASE STAGE VALUE]
tools/check-workflow-action.py reopen-set-blocker --file <path> --gate stages/<phase>.yaml#approval --actor human|proxy_model --rationale "<理由>" --evidence <path> [--evidence <path> ...]
tools/check-workflow-action.py reopen-finalize --file <path> --impacted-downstream-phase <phase> --feature-impact FEATURE DECISION IMPACT_BASIS RATIONALE EVIDENCE --new-feature-decision DECISION RATIONALE EVIDENCE [--completed-step "<説明>"]
tools/check-workflow-action.py autonomous-plan <plan.yaml>
tools/check-workflow-action.py autonomous-plan-template --run-id <run-id> --out <plan.yaml>
tools/check-workflow-action.py autonomous-plan-record-integration --ledger <ledger.yaml> --status <status> --tests "<tests>" --decision "<decision>"
tools/commit-from-current-staged.py -m "<commit message>" --rationale "<理由>"
tools/guarded-git-commit.py -m "<commit message>" --rationale "<理由>"
tools/guarded-git-commit.py -m "<commit message>" --rationale "<理由>" --approval-nonce <nonce> --approval-source-text-line-stdin
```

共通オプション：

- `--json`：機械可読 JSON を出力する
- `--log-path <path>`：判定ログの出力先を上書きする
- `--help`：使い方を表示する

<a id="spec-set"></a>

## 2. spec-set

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `<feature>` | 必須 | 対象機能名。`stages/feature-dependency.yaml` の `features` キーと一致する |
| `<phase>` | 必須 | 対象フェーズ |
| `<stage>` | 必須 | 対象段。フェーズにより有効値が異なる |
| `<new-value>` | 必須 | `true` または `false` |
| `--rationale` | 任意 | 変更理由。ログ記録用であり判定値には影響しない |

`<new-value>` が `true` の場合、次を検査する。

- 同フェーズ内で当該段より前の段が完了していること
- 上流フェーズの最終段が完了していること
- `recheck.upstream_change_pending=true` の影響対象 phase を完了扱いに戻していないこと
- `intent` と `feature-partitioning` のような機能横断段で、単一 feature だけを不整合に変えていないこと

`<new-value>` が `false` の場合、reopen 手続きの一部として原則許容する。ただし、完了済み段を戻す場合は警告を返す。

<a id="commit"></a>

## 3. commit

<a id="commit-preflight"></a>

### 3.0 commit-preflight

`commit-preflight` は、利用者が commit を指示した直後、stage / approval challenge / approval record / execution delegation record / guarded commit のいずれかを作る前に実行する read-only 入口検査である。利用者の単発 commit 指示は staged 内容承認と LLM commit 実行代行承認の出典にできるが、LLM が利用者発話なしに承認文を生成してはならない。

出力は少なくとも次を持つ。

- `verdict`: `OK` または `DEVIATION`
- `allowed_to_stage`
- `allowed_to_prepare_approval`
- `allowed_to_delegate_execution`
- `allowed_to_run_guarded_commit`
- `next_required_action`
- `reasons`
- `current_state.next_action`

判定順序：

1. `stages/in-progress/` がある場合、現在位置が構造化された reopen `commit_stop_point` かを確認する。
2. `commit_stop_point` でない reopen / maintenance / resume 途中状態なら `DEVIATION` とし、stage / approval 作成へ進まない。
3. ただし、本線 reopen 中に対応する `stages/completed/maintenance-*.yaml` が未コミット差分にあり、その `mainline_blocked_by` が全 in-progress reopen を覆う場合は、maintenance 完了 commit 候補として stage / approval 作成を許可する。この場合、本線 `stages/in-progress/reopen-*.yaml` は commit 対象に含めない。side-track 完了 commit のために本線 state を人工的に変更しない。
4. post-write-verification 対象の未完了変更がある場合は `DEVIATION` とし、stage / approval 作成へ進まない。
5. 通常 workflow の phase 終端停止点、reopen の構造化停止点、maintenance 完了 commit 候補では stage / approval 作成を許可する。
6. `allowed_to_run_guarded_commit` は、staged ファイルがあり、commit approval と execution delegation が現在の staged 内容に対して有効な場合だけ `true` にする。

`DEVIATION` の場合、LLM は stage、approval challenge、approval record、execution delegation record、guarded commit のいずれにも進まない。

### 3.1 commit-approval

`commit-approval` は、`commit-preflight` が commit 準備を許可した後、Git index への追加（`git add`）済みの staged exact index に束縛して approval 系 record を作る。

サブコマンド：

| サブコマンド | 役割 |
|---|---|
| `prepare --json` | staged exact index から nonce challenge を作る |
| `record --nonce <nonce> (--source-text-stdin|--no-source-text) [--json]` | nonce に対応する commit 内容承認を保存する |
| `delegate-execution --nonce <nonce> --source-text-stdin [--json]` | LLM による commit 実行代行承認を保存する |
| `invalidate [--json]` | challenge と承認レコードを無効化する |

`prepare` 後は staged index を変更しない。内容承認と実行代行承認は同じ nonce / target digest に束縛され、guarded commit で照合される。

### 3.2 commit

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `--rationale` | 必須 | commit 理由。人による承認の出典を含めることを推奨する |
| `--execution-actor` | 任意 | commit 実行主体。`llm` または `human`。既定は `llm` |

`--execution-actor llm` の場合、通常の commit 内容承認とは別に、LLM による実行代行承認を必要とする。

承認レコードの最小形：

```json
{
  "approved_action": "commit",
  "approved_by": "user",
  "approved_at": "2026-06-03T00:00:00+09:00",
  "rationale": "人がコミットを明示承認",
  "target_files": ["path/to/file.md"],
  "execution_delegation": {
    "delegated_to": "llm",
    "approved_by": "user",
    "approved_at": "2026-06-03T00:00:00+09:00",
    "explicit_instruction": "コミット",
    "rationale": "人が単発 commit 実行を明示指示"
  },
  "expires_after_commit": true,
  "consumed": false
}
```

判定対象：

- commit 承認レコード（新配置 `.reviewcompass/runtime/approvals/commit-approval.json`、旧配置 `.reviewcompass/approvals/commit-approval.json`）が存在し、形式が正しく、未消費であること。読み取りは新→旧の順で解決する
- staged ファイルが `target_files` の範囲内であること
- LLM 実行時は `execution_delegation` があること
- staged ファイルに post-write-verification 対象がある場合、現在 sha256 を覆う completed manifest があること
- staged された `spec.json` に reopen 印がある場合、同じ commit に reopen 手続き記録が含まれること
- reopen 完了記録が含まれる場合、feature impact 判定、下流影響判定、影響フェーズ網羅が記録されていること
- 持ち越し所見の件数を確認し、未消化所見があれば警告すること
- staged ファイルを通常変更、要注意変更、危険変更に分類すること
- staged 文書の Markdown リンク、アンカー、既知の意味的組み合わせを `tools/document_link_lint.py` で検査すること

危険変更がある場合は逸脱とする。要注意変更は警告とする。

`tools/commit-from-current-staged.py` は、TTY からの対話的な stdin 承認 1 行を検査してから `commit_approval.prepare()` を呼び、現在の staged exact index に束縛した challenge を作る。古い runtime approval/delegation は `prepare()` により invalidated になる。返された nonce は同じ process 内で内容承認と実行代行承認に使い、子プロセスへ承認文を pipe しない。stdin 承認文が非 TTY、空、UTF-8 でない、複数行、または許可文言外の場合は challenge 作成前に停止する。承認文は直近の利用者発話または利用者による対話入力に限る。利用者の単発 commit 指示を使う場合、その 1 行を staged 内容承認と LLM commit 実行代行承認の source として扱い、LLM が `printf` 等で生成して渡してはならない。LLM が利用者発話なしに承認文を生成してはならない。

`tools/guarded-git-commit.py` は `commit --execution-actor llm` を先に実行し、exit 2 なら commit しない。exit 1 は既定では停止し、人の判断で続行する場合だけ `--allow-warn` を付ける。commit 成功後、期限付き承認レコードは消費済みにする。

Codex の `workspace-write` sandbox では、`commit-from-current-staged.py` または `guarded-git-commit.py` が最終的に `.git/index.lock` へ書き込む段階で sandbox に拒否され得る。このため Codex から commit を実行する場合は、commit wrapper 本体を最初から sandbox 外（`require_escalated`）で実行する。これは guard を迂回する手順ではなく、承認レコード、staged 内容照合、commit gate を同じ wrapper 内で通したうえで、git index 書き込みだけを許可された実行面で行うための運用である。先に sandbox 内で失敗させてから再実行する手順を標準にしない。

通常 workflow の `intent.approval` / `feature-partitioning.approval` 完了後の停止点は、`next --json` が `kind: commit_stop_point` として検出する。これらは `stages/in-progress/` を使わない通常 commit であるため、commit guard 側では特別な in-progress 例外を要求せず、通常どおり承認レコード、staged 範囲、post-write-verification、文書 lint を検査する。

通常の nonce challenge 付き commit 手順は、次の順序で逐次実行する。

1. `.venv/bin/python3 tools/check-workflow-action.py commit-preflight --json` を実行し、`OK` を確認する。
2. `git add ...` で対象を stage する。
3. `.venv/bin/python3 tools/commit-from-current-staged.py -m "<commit message>" --rationale "<理由>"` を TTY で起動し、直近の利用者発話で明示された commit 指示を 1 行として渡す。

低レベル手順として `commit-approval prepare` と `guarded-git-commit.py --approval-nonce` を直接使う場合も、`commit-approval prepare` と `commit --json` precheck を並列化しない。`prepare` 後の challenge は staged exact index と承認状態に束縛されるため、guarded commit 以外の承認系コマンドを挟まない。`--approval-source-text-line-stdin` は TTY からの対話入力だけを受け付ける。直近の利用者発話で明示された commit 指示を承認 1 行として渡し、空 stdin、pipe、heredoc、redirect、LLM が生成した `printf` 等の承認文では実行してはいけない。

<a id="next"></a>

## 3-a. next

`next --json` は通常 workflow の次 action を返す前に、cross-feature phase 終端の未コミット変更を確認する。

判定：

- `intent.approval` が全 feature で `true` であり、`intent` phase の workflow_state または intent 成果物に未コミット変更がある場合、`kind: commit_stop_point`、`required_action: commit_stop_point`、`blocked_by.type: workflow_phase_end`、`blocked_by.phase: intent` を返す
- `feature-partitioning.approval` が全 feature で `true` であり、`feature-partitioning` phase の workflow_state または feature-partitioning 成果物に未コミット変更がある場合、`kind: commit_stop_point`、`required_action: commit_stop_point`、`blocked_by.type: workflow_phase_end`、`blocked_by.phase: feature-partitioning` を返す
- 対象 phase の終端変更が commit 済みで作業ツリーが clean な場合、停止点を返し続けず、次 phase の通常 action へ進む
- post-write-verification、lightweight self-check、reopen/maintenance/resume の in-progress は従来どおり通常 workflow の停止点判定より優先する

<a id="push"></a>

## 4. push

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `--rationale` | 必須 | push 理由。人による承認の出典を含めることを推奨する |

判定対象：

- 作業ツリーが clean であること
- `origin/main` からのローカル先行コミット数を出力すること
- 直近コミットの題名要約を出力すること
- ローカル先行 commit がある場合、HEAD に対応する commit 事前検査記録があること
- `origin/main` 以外への push が要求されていれば警告すること

作業ツリーが dirty の場合、HEAD の commit 事前検査記録がない場合、または deployable artifact の配置非依存 lint が失敗する場合は逸脱とする。`stages/in-progress/` が存在するだけでは push を遮断しない。in-progress は次 action 判定の状態であり、clean な作業ツリー上の push 済み候補 commit を危険にする直接条件ではない。

<a id="audit-commit"></a>

## 5. audit-commit

`audit-commit <commit-ish>` は、指定 commit の変更ファイルを読み、post-write-verification 対象だけを抽出する。

判定：

- 対象なし：OK
- 対象あり、commit 内ファイル内容 sha256 を覆う completed manifest がある：OK
- 対象あり、manifest がない、sha256 不一致、coverage matrix 不足、または未解決本質的指摘がある：逸脱
- `<commit-ish>` が解決できない：逸脱

この監査は、対象 commit 時点に manifest が存在したことを証明するものではない。現在のリポジトリ状態で、その commit 内容に対応する検証記録が存在するかを確認する是正監査である。

<a id="reopen-advance-step"></a>

## 6. reopen-advance-step

`reopen-advance-step` は、reopen 手続きファイルの第1過程・第2過程を機械的に進める更新コマンドである。第1過程の完了では第2過程の正本修正へ進め、第2過程の完了では停止点コミット状態へ進める。

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `--file` | 必須 | 対象の reopen 手続き YAML |
| `--from-step` | 必須 | 完了扱いにする過程番号。`1` または `2` |
| `--completed-step` | 必須 | `completed_steps` に追記する完了ステップ |
| `--rationale` | 必須 | 判断理由 |
| `--evidence` | 必須 | 判断根拠。複数指定可 |

判定と更新：

- 対象 YAML が存在し、`process_id: reopen-procedure` であることを要求する
- `--from-step` は `1` または `2` のみを許可する
- 対象 YAML の `step_number` は `--from-step` と一致する必要がある。不一致は逸脱とする
- `--completed-step`、`--rationale`、`--evidence` が空の更新は逸脱とする
- `completed_steps` に `--completed-step` を追記する
- `reopen_step_records` に `from_step`、`completed_step`、`rationale`、`evidence` を追記する
- `--from-step 1` の成功時は `step_number: 2`、`next_step: 第2過程：正本修正`、`current_blocker: null` を保存する
- `--from-step 2` の成功時は `step_number: 2`、`next_step: 第2過程：停止点コミット`、`current_blocker: null`、`commit_stop_point: true`、`commit_stop_point_step: 2`、`commit_stop_point_kind: canonical_update_complete`、`commit_stop_point_reason: 第2過程の正本修正完了` を保存する
- commit guard は構造化された停止点だけを許可する。第2過程は `canonical_update_complete`、第3過程は `drafting_complete` または review 系 gate 完了（`triad_review_complete` / `review_wave_complete` / `alignment_complete` / `approval_complete`）、第4過程は implementation approval 完了の `approval_complete` を許可する。
- 成功時は exit 0、上記の前提違反や入力不正は DEVIATION として exit 2 を返す

<a id="reopen-advance-gate"></a>

## 7. reopen-advance-gate

`reopen-advance-gate` は、reopen 手続きファイルの `pending_gates` を 1 件進める更新コマンドである。`spec-set` は in-progress reopen が存在する状態を通常作業として遮断するため、reopen 第3過程の gate 完了更新では本コマンドを使う。

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `--file` | 必須 | 対象の reopen 手続き YAML |
| `--gate` | 必須 | 完了扱いにする gate。`pending_gates` 内と同じ文字列で指定する。標準の gate 文字列は `stages/<phase>.yaml#<stage>` 形式。例：`stages/requirements.yaml#alignment` |
| `--decision` | 必須 | 下流影響判断 |
| `--feature-scope` | 必須 | 判断対象の feature |
| `--rationale` | 必須 | 判断理由 |
| `--evidence` | 必須 | 判断根拠。複数指定可 |
| `--completed-step` | 任意 | `completed_steps` に追記する完了ステップ |
| `--set-spec` | 任意 | `FEATURE PHASE STAGE VALUE` の 4 値で `spec.json` も同時更新する。指定は 1 回のみ。`VALUE` は `true` または `false` |

判定と更新：

- 対象 YAML が存在し、`process_id: reopen-procedure` であることを要求する
- `--gate` は `pending_gates` の先頭文字列と完全一致する必要がある。先頭文字列との不一致は逸脱とする
- `pending_gates` の全要素は、標準の `stages/<phase>.yaml#<stage>` 形式で、かつ既知 phase の review 系 gate（`triad-review`／`review-wave`／`alignment`／`approval`）として解釈できる必要がある。壊れた gate 文字列や `drafting` gate が 1 件でもあれば逸脱とする
- `--evidence` が 1 件も無い更新は逸脱とする
- 完了した gate を `pending_gates` から除去し、`completed_gates` へ追加する
- `downstream_impact_decisions` に `gate`、`feature_scope`、`decision`、`rationale`、`evidence` を追記する
- `--completed-step` があれば `completed_steps` へ追記する
- `--set-spec` があれば、対象 feature の `spec.json` の該当 workflow_state を同時更新する
- gate 完了後は `current_blocker` を `null` にする。本コマンドは approval gate の承認待ち blocker を新規作成しない
- 残る pending gate があれば `step_number: 3` を維持し、`next_step` を次 gate に更新する。無ければ `step_number: 4` と `next_step: 第4過程：完了` へ進める
- 完了した gate について、`commit_stop_point: true`、`commit_stop_point_step`、`commit_stop_point_kind`、`commit_stop_point_gate`、`commit_stop_point_reason` を保存する。kind は `triad-review` → `triad_review_complete`、`review-wave` → `review_wave_complete`、`alignment` → `alignment_complete`、`approval` → `approval_complete` とする。これにより requirements / design / tasks / implementation の各 review 系 gate 完了後を再開可能な停止点コミットとして扱う。
- 成功時は exit 0、上記の前提違反や入力不正は DEVIATION として exit 2 を返す

<a id="reopen-set-blocker"></a>

## 8. reopen-set-blocker

`reopen-set-blocker` は、reopen 第3過程で approval gate の承認待ちに到達したとき、`current_blocker` を構造化して設定する更新コマンドである。承認待ちを自由記述で手編集する代わりに、対象 gate、承認主体、理由、根拠を機械可読に保存する。

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `--file` | 必須 | 対象の reopen 手続き YAML |
| `--gate` | 必須 | 承認待ちにする gate。`pending_gates` 先頭と同じ `stages/<phase>.yaml#approval` 形式 |
| `--actor` | 必須 | 承認主体。`human` または `proxy_model` |
| `--rationale` | 必須 | 承認待ちにする理由 |
| `--evidence` | 必須 | 判断根拠。複数指定可 |

判定と更新：

- 対象 YAML が存在し、`process_id: reopen-procedure` であることを要求する
- `--gate` は `pending_gates` の先頭文字列と完全一致する必要がある。先頭文字列との不一致は逸脱とする
- `pending_gates` の全要素は、標準の `stages/<phase>.yaml#<stage>` 形式で、かつ既知 phase の review 系 gate として解釈できる必要がある
- `--gate` は `approval` gate でなければならない。`alignment` など approval 以外への blocker 設定は逸脱とする
- `--actor` は `human` または `proxy_model` のみを許可する
- `--rationale`、`--evidence` が空の更新は逸脱とする
- 成功時は `current_blocker` に `blocker_type: approval_gate`、`gate`、`actor`、`status: waiting_for_approval`、`rationale`、`evidence` を保存する
- 成功時は exit 0、上記の前提違反や入力不正は DEVIATION として exit 2 を返す

<a id="reopen-finalize"></a>

## 9. reopen-finalize

`reopen-finalize` は、reopen 第4過程で `stages/in-progress/` の手続き YAML を `stages/completed/` へ移す更新コマンドである。完了 YAML の必須項目を手編集で埋める代わりに、構造化引数から `feature_impact_decisions`、`new_feature_decision`、`impacted_downstream_phases`、`completed_steps` を更新する。対象 feature の `spec.json` が存在する場合は、同じ操作で `recheck.upstream_change_pending=false`、`recheck.impacted_downstream_phases=[]` にクリアし、第4過程完了の `reopen_step_records` も追加する。

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `--file` | 必須 | `stages/in-progress/` 配下の reopen 手続き YAML |
| `--impacted-downstream-phase` | 必須 | `impacted_downstream_phases` に記録する phase。複数指定可 |
| `--feature-impact` | 必須 | `FEATURE DECISION IMPACT_BASIS RATIONALE EVIDENCE` の 5 値で feature impact 判定を追加する。既存 feature すべてについて指定する |
| `--new-feature-decision` | 必須 | `DECISION RATIONALE EVIDENCE` の 3 値で new feature 判定を記録する |
| `--completed-step` | 任意 | `completed_steps` に追記する完了ステップ |

判定と更新：

- 対象 YAML が存在し、`process_id: reopen-procedure` であることを要求する
- 対象 YAML は `stages/in-progress/` 配下でなければならない
- `step_number` は `4`、`pending_gates` は空、`current_blocker` は `null` でなければならない
- `--feature-impact` は既存 feature すべてを覆う必要がある
- feature impact の `decision`、`impact_basis`、`rationale`、`evidence` は commit 前検査の完了 YAML 検査と同じ条件で検査する
- `--new-feature-decision` は `decision`、`rationale`、`evidence` を必須とする
- `--impacted-downstream-phase` は既知 phase 名だけを許可する
- 成功時は `step_number: 4`、`next_step: 完了`、`pending_gates: []`、`current_blocker: null` を保存し、対象 feature の `spec.json` の recheck をクリアし、第4過程完了の `reopen_step_records` を追加したうえで、同名ファイルを `stages/completed/` へ作成して元の in-progress ファイルを削除する
- completed 側に同名ファイルが既にある場合は上書きせず DEVIATION とする
- 成功時は exit 0、上記の前提違反や入力不正は DEVIATION として exit 2 を返す

<a id="autonomous-plan"></a>
<a id="autonomous-plan-template"></a>
<a id="autonomous-plan-record-integration"></a>
<a id="autonomous-ledger-audit"></a>

## 10. autonomous-plan 系

`autonomous-plan` は実行計画 YAML を fail-closed で検査する。最低限、次を確認する。

- `mode: autonomous_parallel`
- `run_id`
- `authorization.approved_by`
- レビュー結果サマリと三段階トリアージの提示済み記録
- 各 task の `source_finding_ids`、`allowed_paths`、`expected_tests`、停止条件
- 並列 task 間の `allowed_paths` 衝突がないこと
- `integration_gate` の確認項目
- 作業ノイズを本線 repo に取り込まない出力方針
- 履歴台帳パス、タスク割当記録、判断根拠記録、統合結果記録、保存方針

検査に通った場合も、通らなかった場合も、台帳パスが妥当なら判定履歴を記録する。

`autonomous-plan-template` は最小テンプレートを生成する。`autonomous-plan-record-integration` は統合後に既存の履歴台帳へ `integration_result` を追記する。

## 11. 出力形式

終了コード：

- `0`：問題なし
- `1`：警告あり
- `2`：逸脱検出

人間可読出力は、正常系では判定結果と対象サブコマンドだけの最小出力にする。判定理由や現在状態の詳細は、逸脱・警告・非定型処理・調査が必要な場合だけ表示する。

JSON 出力は、少なくとも次のキーを含む。

```json
{
  "verdict": "OK | WARN | DEVIATION",
  "exit_code": 0,
  "action": {
    "subcommand": "commit",
    "args": {}
  },
  "reasons": [],
  "current_state": {}
}
```

## 12. ログ

判定ログは JSON Lines 形式で記録する。`--json` 出力と同等の構造に `timestamp` を追加する。

既定パス：

- `.reviewcompass/runtime/logs/workflow-precheck.log`（旧 `docs/logs/workflow-precheck.log` からの変更は
  2026-06-12 配置規約 PLC-DEC-004〜005・009〜011 反映。旧ログは凍結、読み取り互換は P3 まで）

`--log-path` でテスト用の隔離パスへ上書きできる。

### 12.1 実行時生成物の凍結期（P3 まで）の扱い

検査ログ・effective prompt（`.reviewcompass/runtime/effective-prompts/`、旧 `.reviewcompass/effective-prompts/`）・
commit 承認レコード（`.reviewcompass/runtime/approvals/commit-approval.json`、旧 `.reviewcompass/approvals/commit-approval.json`）の
3 パスは、書き込みを常に新配置（runtime 区画、原則 git 無視）へ行い、読み取りは新→旧の順でフォールバックする
（新旧競合時は新配置を正とする）。契約の正本は workflow-management design §実行時生成物の凍結期（P3 まで）の扱い。
定数と読み取り解決の実装正本は `tools/check_workflow_action/runtime_paths.py`。

凍結検査の手動実行手順（ゲートへの自動統合は行わず、手動運用とする）：

1. 凍結境界（P1 実装反映コミット＝書き込み先切替のコミット）を特定する。例：

   ```bash
   git log --reverse --format=%H -S "runtime/logs/workflow-precheck" -- tools/check_workflow_action/runtime_paths.py | head -1
   ```

2. 旧 3 パスへの凍結違反（追加・変更・削除）を検出する。例：

   ```bash
   PYTHONPATH=. .venv/bin/python3 -c "
   from tools.check_workflow_action.placement_freeze import check_runtime_placement_freeze
   for v in check_runtime_placement_freeze('.', '<freeze-commit>'):
     print(v)
   "
   ```

   注記：ReviewCompass 自身では旧 3 パスは gitignore 対象（未追跡）のため、git 履歴で不変性を立証できるのは
   旧配置を追跡している構成（対象アプリ等）に限る。未追跡の旧成果物の凍結は書き込み経路のテスト
   （`tests/tools/test_runtime_placement_freeze.py`）で担保する。

## 13. テスト観点

主要な判定条件は `tests/tools/test_check_workflow_action.py` で検証する。最低限、次を覆う。

- `spec-set` の正常系、reopen 警告、段順序逸脱
- `commit` の承認レコード、post-write-verification、reopen 手続き、危険変更、文書リンクの検査
- `push` の clean 性検査
- `audit-commit` の manifest 対応検査
- `reopen-advance-step` の第1・第2過程更新、根拠なし更新拒否、現在 step 不一致拒否
- `reopen-advance-gate` の先頭 gate 更新、spec.json 同時更新、非先頭 gate 拒否
- `reopen-set-blocker` の構造化 blocker 設定、非先頭 gate 拒否、非 approval gate 拒否、根拠なし更新拒否
- `reopen-finalize` の完了 YAML 生成、in-progress 削除、第4過程未到達と feature impact 不足の拒否
- `guarded-git-commit.py` の commit 遮断と承認レコード消費
- `autonomous-plan` 系サブコマンドの構造検査

実装変更時は、期待される入出力に基づくテストを先に用意し、失敗確認後に実装を更新する。

