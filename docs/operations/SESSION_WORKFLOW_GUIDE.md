# SESSION_WORKFLOW_GUIDE：セッション運営ガイドライン

最終更新：2026-05-23（セッション 21：用語「遡及／波及」の二軸的定義への訂正、段集合の責務分離による 5 段化を反映）

本文書は ReviewCompass の開発セッションを確実に回すための運用ガイドラインである。セッション 19 で発覚した「ワークフロー把握不足のまま着手」「用語混同（遡及／波及）」等の失態と検討不足を踏まえ、次セッション以降が同じ失敗を繰り返さないよう手順と判断指針を明示する。

本文書は運用文書（`docs/operations/` 配下）であり、計画書（`docs/plan/`）の方針を**実行可能な手順**に落とし込んだもの。計画書の改定なしに本文書だけを更新できる位置付け。

## 1. セッション開始時の必読フロー（5 分以内）

セッション開始時は **作業着手前に必ず**次を順番に確認する。確認なしの着手は失態の原因となる（セッション 19 §0 の経験）。

### 1.1 必読 5 件

順序は重要：

1. **`TODO_NEXT_SESSION.md`**（最新進捗）
   - 前セッション末尾の到達点、次の作業候補、未消化所見
   - 「§0 重要事項」「§1 起動手順」「§3 次の作業候補」を最低限読む

2. **計画書 §5.4〜§5.7**（ワークフロー手続き）
   - §5.4：軽量化方針（思想は継承、実装は 1／10）
   - §5.5：9 ファイル体制と段階層構造（drafting → local-review → review-wave → aligned → approved の 5 段、責務分離による 5 段化が確定済み 2026-05-23。計画書改定は第 2 段階で実施）
   - §5.6：reopen 手続きの機械強制（手戻り種別の二次元表記）
   - §5.7：session 跨ぎ時の状態管理（`stages/in-progress/`）

3. **計画書 §5.23 と §5.23.12**（dogfooding ／ サブエージェント方式）
   - §5.23：手動 dogfooding 計画
   - §5.23.12：サブエージェント方式（中間経路、`subagent_mediated`）の運用条件

4. **`.reviewcompass/pending-cross-feature-findings.md`**（持ち越し所見）
   - 機能横断波及所見の未消化件数と内容を把握
   - 要件 review-wave／alignment-gate で対処予定の件

5. **`docs/extraction-mapping.md`**（抽出進捗）
   - 各機能の状態（未着手／抽出中／抽出済／確認済）
   - 機能ごとの実施履歴

### 1.2 確認後の git 状態把握

- `git log --oneline -10`：直近のコミット履歴
- `git status`：未コミット変更の有無

### 1.3 ワークフロー上の現在位置の確認

- 現在どのフェーズか（intent ／ requirements ／ design ／ tasks ／ implementation）
- 現在どの段か（drafting ／ local-review ／ review-wave ／ aligned ／ approved の 5 段）
- 残機能と消化予定所見

## 2. ワークフロー段の役割と順序

### 2.1 全体構造（責務分離による 5 段化、2026-05-23 利用者明示承認）

```
intent 層（人間担当）
  ↓
機能分離（§3.1 で 7 機能体制を確定済み）
  ↓
requirements 段：drafting → local-review → review-wave → aligned → approved
  ↓
design 段：drafting → local-review → review-wave → aligned → approved
  ↓
tasks 段：drafting → local-review → review-wave → aligned → approved
  ↓
implementation 段：drafting → local-review → review-wave → aligned → approved
```

旧記述（drafting → review-wave → alignment-gate の 3 段）は次の 2 段階の改定により旧式化：

- alignment-gate を aligned（LLM 自動判定）と approved（人間または別モデル承認）の 2 段に分割
- drafting と local-review を別段に分離（責務分離）

合計で 5 段化（drafting／local-review／review-wave／aligned／approved）。計画書 §5.5 の改定は第 2 段階で実施し、それまでは本ガイドラインの 5 段記述が運用上の正本。

### 2.2 各段の役割（責務分離後）

- **drafting**：各機能の草案作成のみ。1 機能ずつ独立に進める。actor=llm（または human）
- **local-review**：機能内の 3 役レビュー（主役・敵対役・判定役）と機能内対処の実施。手動 dogfooding または subagent_mediated（サブエージェント仲介方式）で実施。actor=llm
- **review-wave**：複数機能を横断する複数ラウンドレビュー。機能横断波及所見の集約・対処
- **aligned**：LLM 自動判定による整合確認段（旧 alignment-gate を分割した前半、actor=llm）
- **approved**：人間または別モデル（§5.12 人間代役機構）による承認段（旧 alignment-gate を分割した後半、actor=human または proxy_model）

drafting と local-review を別段にする理由：誰が何をしたかを段単位で明確に記録するため。草案作成者と判定者を分ける規律（§5.4）が段の構造上で機械検査可能になる。

### 2.3 段の進め方の規律

- **drafting 段の草案完成** → 当該機能の local-review 段に進む（機能単位で逐次進行）
- **local-review 段で 3 役レビューと機能内対処** を完了 → 当該機能の drafting／local-review がそろう
- **全機能で drafting ＋ local-review を完了** してから review-wave に進む（部分的に review-wave を始めない）
- **review-wave の所見を消化** してから aligned に進む
- **aligned で LLM 自動判定** を通過してから approved に進む
- **approved で利用者または別モデル承認** を得てから次フェーズに進む

### 2.4 「次の機能の drafting に進むべき」状況の判断

local-review 段で 3 役レビューを行った所見が **機能横断の波及所見**だった場合、当該機能の local-review で対処せず、`pending-cross-feature-findings.md` に持ち越して **次の機能の drafting に進む**。これがセッション 19 の中盤で確立された運用パターン。

## 3. 修正案件の波及種別と処理段

### 3.1 用語の使い分け（二軸的定義、2026-05-23 訂正）

両用語は **対象方向が異なる正当な技術用語** であり、優劣はない：

- **遡及（そきゅう）**：**上流フェーズへの影響**。下流段の作業で発見された問題が、上流段（過去フェーズ）の修正を要するもの。例：実装段で発見した不整合が要件段の書き直しを要する
- **波及（はきゅう）**：**同フェーズ内の他機能（フィーチャー）への影響**。ある機能のレビューが別機能との不整合を露出させるもの。例：foundation 要件の修正が runtime／evaluation 要件にも影響する

セッション 19 中盤で、私（メインセッション）が「foundation の遡及修正」と表現したことを利用者が「波及であり alignment wave の範囲」と訂正した。これは A-001 が **同フェーズ内（要件段）の他機能（foundation／runtime）への影響** であって、上流フェーズへの修正ではない、という意味だった。私はこれを「遡及は悪、波及は善」と誤一般化していたが、後のセッションで利用者から再訂正があり、本ガイドラインを二軸的定義に書き直した（2026-05-23）。

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

- **発見されるタイミング**：drafting 段（起草者の自己発見）／ local-review 段（3 役レビュー）
- **処理する段**：当該機能の **local-review 段** で対処（drafting に戻して草案修正、または local-review 段内で直接修正）
- **方法**：当該機能の仕様文書を直接修正
- **次段への進行**：当該機能の local-review 段が `completed` 状態になってから次機能へ
- **記録先**：レビュー記録（`.reviewcompass/specs/<機能>/reviews/<日付>-<種別>.md`）の §4 統合節に「対処済み」と記録

#### (b) 波及（同フェーズ・他機能への影響）

- **発見されるタイミング**：local-review 段（3 役が他機能との不整合に気づく）／ review-wave 段（機能横断レビュー）
- **処理する段**：**review-wave 段**（フェーズ終端の機能横断段、全機能の drafting ＋ local-review 完了後に開始）
- **方法**：
  1. local-review 段で波及と判定されたら **当該機能では対処せず**、`.reviewcompass/pending-cross-feature-findings.md` に追記
  2. 「次の機能の drafting」に進む（個別機能の段では対処しない）
  3. 全機能の drafting ＋ local-review が完了したら、review-wave 段で集約消化
  4. 影響を受ける全機能の仕様文書を一括修正（依存順を守る、例：foundation を先に修正してから runtime）
- **記録先**：`pending-cross-feature-findings.md` の各所見項目、消化後は「✅ 対処済み（日付）」追記

#### (c) 遡及（上流フェーズへの影響）

- **発見されるタイミング**：任意の下流段（local-review／review-wave／aligned／approved のいずれか）
- **処理方法**：**reopen 手続き（10 ステップ、§5.6）** を起動。当該段の作業を停止し、上流フェーズに戻る
- **手戻り種別判定**：N（intent）／R（requirements）／D（design）／A（tasks）／I（implementation）× 深さ 0〜4 の二次元表記で判定
- **再実施対象決定**：第 7 ステップで `stages/reopen-procedure.yaml` の trigger_map（再実施対象段の決定表）を参照して機械決定。actor=human の段（approved 等）に来たら作業を止めて承認待ち
- **記録先**：種別判定の根拠を `docs/reviews/reopen-classification-<日付>.md` に残す、機能単位 spec.json の `reopened` 履歴と `recheck` フラグを更新

#### (d) 遡及 ＋ 波及の組合せ

- **発見されるタイミング**：任意の下流段
- **処理方法**：reopen で上流フェーズに戻り、上流フェーズの review-wave 段で波及所見として集約消化、その後下流に伝播
  1. **第 1 段階**：reopen 手続きで上流フェーズに戻り、影響範囲を特定（trigger_map）
  2. **第 2 段階**：上流フェーズで `pending-cross-feature-findings.md` に波及所見として追記し、当該フェーズの review-wave 段で消化
  3. **第 3 段階**：上流フェーズの aligned ＋ approved を再実施
  4. **第 4 段階**：下流フェーズの aligned ＋ approved を再実施（trigger_map で連鎖再実施対象として決定）
- **記録先**：reopen 記録 ＋ `pending-cross-feature-findings.md` の両方

#### (e) leave-as-is と延期

- **leave-as-is**：判定役が「修正不要」と判断したもの。対処せず、レビュー記録に判定根拠を残すのみ
- **延期**：将来のフェーズで対処する判定。レビュー記録に延期理由と対処予定フェーズを残し、当該フェーズ着手時のチェックリストに追記

### 3.4 振り分け判断のフロー（local-review 段で実施）

local-review 段の判定役は、各所見について次の振り分けを行う：

```
所見発見
  ↓
当該機能の仕様修正のみで完結するか？
  ├── YES → 機能内対処（local-review 段内で対処）
  └── NO
      ↓
  他機能の仕様修正も必要か？
  ├── YES（同フェーズ内のみ） → pending-cross-feature-findings.md に追記、review-wave 段で処理
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
| local-review | 機能内 ／ 波及 ／ 遡及 | **機能内** のみ | 波及 → review-wave、遡及 → reopen |
| review-wave | 波及（横断ラウンド中の追加発見も） | **波及** | 遡及あり → reopen |
| aligned | 自動判定の不整合検出 | （自動判定が通過するまで前段に戻す） | 遡及あり → reopen |
| approved | 重大見落とし、利用者または別モデルによる指摘 | （承認しない） | reopen で上流戻し |

### 3.6 機能横断波及所見の管理ルール

- 各機能の local-review 段で発見されたら、即時 `pending-cross-feature-findings.md` に追記
- 追記項目：所見 ID（A-XXX 形式）、検出セッション、波及範囲（影響を受ける機能と仕様箇所）、対処方針、依存関係
- review-wave／aligned／approved の機能横断段着手時、全件を消化対象とする
- 消化後、各所見に「✅ 対処済み（YYYY-MM-DD、要件 review-wave）」ラベルを追加

## 4. サブエージェント方式の運用条件

### 4.1 採用根拠（計画書 §5.23.12 由来）

- メインセッションが主役、サブエージェントが敵対役・判定役を担う中間経路
- 手動 dogfooding と実行時経由の中間に位置
- フェーズ 1 から運用可能、追加料金なし（セッション 19 で実証）

### 4.2 モデル割り当て（規律）

- **主役（primary）**：メインセッション Opus 4.7
- **敵対役（adversarial）**：サブエージェント Sonnet 4.6
- **判定役（judgment）**：サブエージェント Haiku 4.5

3 役で異なるモデルファミリーを使うことでモデル多様化規律（§5.9.1）を満たす。

### 4.3 サブエージェント呼び出し時の規律

- **プロンプトに自己完結性を持たせる**：サブエージェントは別 session で、メインの作業文脈を共有しない
- **計画書引用は事後検証**：サブエージェントの計画書引用には §番号誤りが発生しうる（セッション 19 で実証）。メインセッションが grep で確認する
- **ファイル書き込みは原則禁止**：読み取りと分析のみ。例外的にレビュー記録の §2 や `pending-cross-feature-findings.md` への直接追記を許容
- **モデル指定**：Agent ツールの `model` パラメータで `"sonnet"`／`"haiku"` を指定

### 4.4 レビュー記録の必須フィールド（§5.4 起草者と判定者の分離）

レビュー記録の front-matter に次を必須化：

```yaml
author:
  identity: claude_code_main_session
  model: claude-opus-4-7
  role: drafter
reviewer:
  identity: claude_code_subagent
  model: claude-haiku-4-5-20251001
  role: final_judgment
  separation_from_author: true
```

`author.identity` と `reviewer.identity` が異名であることを機械検査の対象とする。

### 4.5 mode 値（計画書 §5.23.12.5 由来）

レビュー記録の `mode` は `subagent_mediated`（正式値）。foundation のレビューモード語彙正本（Requirement 6 受入 6）の 3 値のうちのひとつ。

## 5. 利用者判断が必要な論点の見極め

### 5.1 利用者判断必須の項目

次のいずれかに該当する場合、LLM は単独で確定せず、利用者の明示承認を仰ぐ：

- **計画書方針変更**：計画書の節追加・修正（例：§5.18.13 への記述追加、§5.23.12 新節）
- **大規模再設計**：素材から大幅に削減・再構成する場合（例：workflow-management の 156 行 9 要件 → 8 要件）
- **機能横断の権限分担**：複数機能にまたがる責務分担の決定（例：A-007 の self-improvement と workflow-management の権限調停）
- **判定境界の判断**：must-fix／should-fix／leave-as-is の境界が曖昧な場合
- **承認・コミット・push・フェーズ移行**：すべて利用者明示承認必須（計画書 §5.19.6 由来）

### 5.2 LLM が自律的に決められる項目

- **抽出時のクリーニング作業の細部**（機能名置換、自己適用前提除去等）
- **観点 5（検証可能性）の機械判定可能な所見の指摘**
- **レビュー記録の構造化**（front-matter、節構成）

### 5.3 判断の記録規律

利用者判断の結果は次の場所に記録：

- **計画書方針変更**：計画書の該当節に決定日付付きで記載
- **機能横断対処方針**：`pending-cross-feature-findings.md` の該当所見に対処方針として追記
- **重大論点**：レビュー記録の §1 主役レビュー、§4 統合の「利用者判断履歴」節に記録

## 6. コミット規律

### 6.1 コミット単位

- **計画書更新 ＋ 基盤整備**：1〜2 コミット（セッション冒頭の方針確定、運用ファイル整備）
- **機能ごとに 1 コミット**：仕様文書 ＋ 運用文書 ＋ レビュー記録の 3 ファイル（または schema/template 等の関連ファイル）
- **機能横断段（review-wave／aligned／approved）**：1 コミット（複数機能の小修正をまとめる）

### 6.2 コミット順序

依存マップ順（計画書 §3.1 phase_order）に従う：

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
- **Co-Authored-By**：`Claude Opus 4.7 (1M context) <noreply@anthropic.com>`

### 6.4 コミット前確認

- `git status` で対象ファイルを確認
- `git diff --cached` で内容確認（必要に応じて）
- `--no-verify` や `--no-gpg-sign` は使わない（規律）

### 6.5 push

push は **利用者明示承認**を仰いでから実行。LLM が自律的に push しない。

## 7. 用語ガイド

### 7.1 「遡及」と「波及」（二軸的定義、2026-05-23 訂正）

両用語は対象方向で使い分ける：

- **遡及（そきゅう）**：上流フェーズへの影響（時間軸＝過去方向）
- **波及（はきゅう）**：同フェーズ内の他機能への影響（横方向＝機能間）

両方とも正当な技術用語で、避けるべき／推奨という関係ではない。所見の性格を正確に表すために使い分ける。

### 7.2 判定値の使い分け

- **must-fix**：仕様の致命的または重要な欠落、修正必須
- **should-fix**：仕様の改善余地、修正推奨
- **leave-as-is**：仕様として問題なし、修正不要

### 7.3 機能内と機能横断

- **機能内対処**：当該機能の drafting 段で本セッション内に修正
- **機能横断持ち越し**：`pending-cross-feature-findings.md` に集約、review-wave／aligned／approved の機能横断段で対処

### 7.4 サブエージェント関連

- **メインセッション**：主役レビューを実行する Claude Code の主 session（Opus 4.7）
- **サブエージェント**：敵対役・判定役を実行する別 session（Agent ツール経由、Sonnet／Haiku）
- **mode = `subagent_mediated`**：サブエージェント方式のレビュー記録の mode 値

### 7.5 計画書の節番号

- 計画書（`docs/plan/reconstruction-plan-2026-05-21.md`）の節番号は §X.Y 形式
- 引用時は **メインセッションで grep 確認**してから記述（サブエージェントの §番号誤り対策）

## 8. セッション 19 で得られた教訓（参考）

本ガイドラインは次の経験を反映している：

### 8.1 ワークフロー確認の失態

セッション 19 開始時、私（メインセッション）は計画書 §5.4〜§5.7 を読まずに foundation requirements の抽出を始めた。中盤で利用者が「ワークフローを再度読む」と指摘し、intent 段の所在（過去セッションで作成済み）、dogfeeding の §5.23 での既存記述、機能横断レビューの段位置（review-wave／alignment-gate）を確認することになった。**着手前の必読フロー（§1）はこの失態の再発防止策**。

### 8.2 用語混同（遡及／波及）

セッション 19 中盤で A-001（foundation の `not_run` 欠落）発見時、私が「foundation の遡及修正」と表現した。利用者が「遡及ではなく波及。本来は alignment wave の範囲」と訂正。**§3.1 の用語の使い分けはこの訂正を反映**。

### 8.3 機能横断波及所見の集約管理ファイルの新設

A-001 発見時、利用者の指示で `.reviewcompass/pending-cross-feature-findings.md` を新設して集約管理する運用パターンが確立した。これ以降、A-003／A-004／A-005／A-007／A-008 が同ファイルに追記され、要件 review-wave で一括消化された。

### 8.4 サブエージェントの計画書引用誤り

セッション 19 中盤、敵対役（Sonnet 4.6）が計画書 §5.18.11 を引用したが、実体は §5.18.2 周辺の別箇所だった（引用内容自体は正当）。**§4.3 の事後検証はこの経験を反映**。

### 8.5 サブエージェントの直接書き込みパターン

セッション 19 後半、敵対役が自発的に `pending-cross-feature-findings.md` に直接追記するパターンを確立。メインセッションを介さない効率化として、後続セッションでも継続予定。

### 8.6 利用者判断の見極め不足

セッション 19 中で、サブエージェント方式の正式採用、A-007 の権限調停（案 1／案 2）、解釈論点 α／う など、利用者判断が必要な論点が複数発生した。**§5 の利用者判断必須項目はこの経験を反映**。

## 9. 関連文書

- 計画書：[../plan/reconstruction-plan-2026-05-21.md](../plan/reconstruction-plan-2026-05-21.md)（§5.4〜§5.8 ワークフロー、§5.23／§5.23.12 dogfooding／サブエージェント方式、§5.19.6 利用者判断の運用ルール）
- 抽出進捗：[../extraction-mapping.md](../extraction-mapping.md)
- 機能横断波及所見：[../../.reviewcompass/pending-cross-feature-findings.md](../../.reviewcompass/pending-cross-feature-findings.md)
- レビュー記録雛形：[../../templates/review/manual_dogfooding_review_template.md](../../templates/review/manual_dogfooding_review_template.md)
- TODO：[../../TODO_NEXT_SESSION.md](../../TODO_NEXT_SESSION.md)

## 10. 本ガイドラインの改訂規律

- 本ガイドラインは運用文書であり、計画書の改定なしに更新可能
- 各セッションの経験から新たな教訓が得られた場合、§8 に追記
- 規律変更（§2〜§7）は利用者明示承認後に反映
- 改訂時は最終更新日付を更新
