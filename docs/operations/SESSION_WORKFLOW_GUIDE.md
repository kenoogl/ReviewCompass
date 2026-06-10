# SESSION_WORKFLOW_GUIDE：セッション運営ガイドライン

最終更新：2026-06-09（作業完了時レポート契約を正本化）／2026-06-04（review-run 後の proxy_model 判断代行手順を正本化、セッション記録の作成手順を正本化）／2026-06-03（Codex adapter migration：Claude Code 固定の作業環境記述を adapter 方針へ整理）／2026-05-30（セッション 41：§4.2 モデル割り当てを計画書 §5.9.1・実態に整合。「主役＝メインセッション」の誤記を訂正し、メイン LLM は 3 役のいずれにもならないことを明記、モデル能力配分規律へ更新）／2026-05-23（セッション 21：用語「遡及／波及」の二軸的定義への訂正、段集合の責務分離による 5 段化を反映）

本文書は ReviewCompass の開発セッションを確実に回すための運用ガイドラインである。セッション 19 で発覚した「ワークフロー把握不足のまま着手」「用語混同（遡及／波及）」等の失態と検討不足を踏まえ、次セッション以降が同じ失敗を繰り返さないよう手順と判断指針を明示する。

本文書は運用文書（`docs/operations/` 配下）であり、計画書（`docs/plan/`）の方針を**実行可能な手順**に落とし込んだもの。計画書の改定なしに本文書だけを更新できる位置付け。

## 1. セッション開始時の必読フロー（5 分以内）

セッション開始時は **作業着手前に必ず**次を順番に確認する。確認なしの着手は失態の原因となる（セッション 19 §0 の経験）。

### 1.1 必読 5 件

順序は重要：

1. **`TODO_NEXT_SESSION.md`**（最新進捗）
   - 前セッション末尾の到達点、次の作業候補、未消化所見
   - 「§0 重要事項」「§1 起動手順」「§3 次の作業候補」を最低限読む
   - 直近の `docs/sessions/session-*.md` も併読し、TODO に圧縮された経緯の詳細を確認する

2. **計画書 §5.4〜§5.7**（ワークフロー手続き）
   - §5.4：軽量化方針（思想は継承、実装は 1／10）
   - §5.5：9 ファイル体制と段階層構造（drafting → triad-review → review-wave → alignment → approval の 5 段、責務分離による 5 段化が確定済み 2026-05-23。計画書改定は第 2 段階で実施）
   - §5.6：reopen 手続きの機械強制（手戻り種別の二次元表記）
   - §5.7：session 跨ぎ時の状態管理（`stages/in-progress/`）

3. **計画書 §5.23 と §5.23.12**（dogfooding ／ サブエージェント方式）
   - §5.23：手動 dogfooding 計画
   - §5.23.12：サブエージェント方式（中間経路、`subagent_mediated`）の運用条件

4. **`learning/workflow/carry-forward-register/reviewcompass-import.yaml`**（持ち越し所見の正本）
   - 機能横断波及所見の未消化件数と内容を把握
   - ReviewCompass 旧 Markdown 台帳は `learning/workflow/carry-forward-register/sources/reviewcompass-pending-cross-feature-findings.md` に履歴 source として残す
   - 要件 review-wave／alignment／approval で対処予定の件（過去のセッション 19 で旧 alignment-gate として実施した分は完了済み）

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

### 2.1 全体構造（責務分離による 5 段化、2026-05-23 利用者明示承認）

```
intent 層（人間担当）
  ↓
機能分離（§3.1 で 7 機能体制を確定済み）
  ↓
requirements 段：drafting → triad-review → review-wave → alignment → approval
  ↓
design 段：drafting → triad-review → review-wave → alignment → approval
  ↓
tasks 段：drafting → triad-review → review-wave → alignment → approval
  ↓
implementation 段：drafting → triad-review → review-wave → alignment → approval
```

旧記述（drafting → review-wave → alignment-gate の 3 段）は次の 2 段階の改定により旧式化：

- alignment-gate を alignment（LLM 自動判定）と approval（人間または別モデル承認）の 2 段に分割
- drafting と triad-review を別段に分離（責務分離）

合計で 5 段化（drafting／triad-review／review-wave／alignment／approval）。計画書 §5.5 の改定は第 2 段階で実施し、それまでは本ガイドラインの 5 段記述が運用上の正本。

### 2.2 各段の役割（責務分離後）

- **drafting**：各機能の草案作成のみ。1 機能ずつ独立に進める。actor=llm（または human）。tasks 段の drafting では、対象機能の設計書 §14 要件追跡表（Req 受入単位 × 担当タスク単位）を骨格として tasks.md を作成する。
- **triad-review**：機能内の 3 役レビュー（主役・敵対役・判定役）と機能内対処の実施。手動 dogfooding または subagent_mediated（サブエージェント仲介方式）で実施。actor=llm
- **review-wave**：複数機能を横断する複数ラウンドレビュー。機能横断波及所見の集約・対処、および **7 モデル比較実験の 2 回目（同根問題評価）と同根問題集約**（2026-05-27 セッション 34 追記、(ニ) (Q2) 採用、2026-05-28 セッション 35 で 2 回方式に訂正）。7 モデル比較実験は **2 回方式** で実施し、1 回目は機能ごとの triad-review 段で機能内 must-fix／should-fix を評価して機能内対処を完了させ、2 回目（本段）は全機能の triad-review 完了後に機能横断波及所見と同根所見（異なる機能で同じ性格の所見が独立に発見された組）を評価して一貫した対処方針で全該当機能の仕様文書に反映する。詳細は計画書 §5.5 機能横断段の作業内容 ／ §5.9.6 N モデル比較実験の実施タイミングを参照
- **alignment**：LLM 自動判定による整合確認段（旧 alignment-gate を分割した前半、actor=llm）
- **approval**：人間または別モデル（§5.12 人間代役機構）による承認段（旧 alignment-gate を分割した後半、actor=human または proxy_model）

drafting と triad-review を別段にする理由：誰が何をしたかを段単位で明確に記録するため。草案作成者と判定者を分ける規律（§5.4）が段の構造上で機械検査可能になる。

### 2.3 段の進め方の規律

- **drafting 段の草案完成** → 当該機能の triad-review 段に進む（機能単位で逐次進行）
- **triad-review 段で 3 役レビューと機能内対処** を完了 → 当該機能の drafting／triad-review がそろう
- **全機能で drafting ＋ triad-review を完了** してから review-wave に進む（部分的に review-wave を始めない）
- **review-wave の所見を消化** してから alignment に進む
- **alignment で LLM 自動判定** を通過してから approval に進む
- **approval で利用者または別モデル承認** を得てから次フェーズに進む

### 2.4 「次の機能の drafting に進むべき」状況の判断

triad-review 段で 3 役レビューを行った所見が **機能横断の波及所見**だった場合、当該機能の triad-review で対処せず、carry-forward register に持ち越して **次の機能の drafting に進む**。この運用はセッション 19 の中盤で旧 Markdown 台帳として確立し、現在は抽象レジスタへ移行している。

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

- **発見されるタイミング**：drafting 段（起草者の自己発見）／ triad-review 段（3 役レビュー）
- **処理する段**：当該機能の **triad-review 段** で対処（drafting に戻して草案修正、または triad-review 段内で直接修正）
- **方法**：当該機能の仕様文書を直接修正
- **次段への進行**：当該機能の triad-review 段が `completed` 状態になってから次機能へ
- **記録先**：レビュー記録（`.reviewcompass/specs/<機能>/reviews/<日付>-<種別>.md`）の §4 統合節に「対処済み」と記録

##### (a-1) must-fix 所見の対処手順（2026-05-25 セッション 25 規律、深掘り議論の義務化）

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
7. レビュー記録（reviews/...）の §4 統合節に「対処方針・利用者承認の出典・反映箇所」を記録する

**深掘りの具体内容**（推奨案を提示する際に必ず想定する事項）：

- foundation 機能の場合：対象アプリへの配置可能性、計画書非配置、要件 7（リポジトリ内資産の規則）との整合
- 値域・語彙の固定：将来拡張時の改訂コスト、機械検証時の不正値検出
- 責務境界：foundation と runtime（または他機能）の責務分離、上流が下流の実装方針に踏み込まない原則
- 不変性：成果物の追記性、生証拠は不変の原則
- 依存関係：他機能が当該仕様を取り込む際の参照可否

**禁則**：

- 利用者と議論せずに must-fix 所見の対処内容を独自に確定する
- 「現状維持を推奨」と表層的に提案する（弱点検証を欠く）
- 候補案を 1 つしか提示しない（代替案との比較を欠く）
- 後段影響を想定しない推奨

本規律の出典：2026-05-25 セッション 25 の foundation／design must-fix 対処での手順違反事例（利用者の問いかけ「foundationのmust_fixについては、議論しなくて良いのか」と「(イ)で後段に問題発生はないか」「一連の提案は、表層的で深掘りされていない。先ほどの指摘がなければ、下流でreopen案件になっていた」）。詳細は当該セッションのレビュー記録 [.reviewcompass/specs/foundation/reviews/2026-05-25-design-triad-review.md](../../.reviewcompass/specs/foundation/reviews/2026-05-25-design-triad-review.md) を参照。

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
- **処理方法**：**reopen 手続き（10 ステップ、§5.6）** を起動。当該段の作業を停止し、上流フェーズに戻る
- **手戻り種別判定**：N（intent）／R（requirements）／D（design）／A（tasks）／I（implementation）× 深さ 0〜4 の二次元表記で判定
- **再実施対象決定**：第 7 ステップで `stages/reopen-procedure.yaml` の trigger_map（再実施対象段の決定表）を参照して機械決定。actor=human の段（approval 等）に来たら作業を止めて承認待ち
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

### 4.1 採用根拠（計画書 §5.23.12 由来）

- メインセッションが主役、サブエージェントが敵対役・判定役を担う中間経路
- 手動 dogfooding と実行時経由の中間に位置
- フェーズ 1 から運用可能、追加料金なし（セッション 19 で実証）

### 4.2 モデル割り当て（規律）

3 役（主役・敵対役・判定役）はすべて独立したサブエージェントが担い、**メイン LLM（コンシェルジュ＝起草者）は 3 役のいずれにもならない**（計画書 §5.9.1、起草者と判定者の分離規律 §0.3）。メイン LLM は草案作成と三役レビュー結果の取りまとめのみを担う。

各役のモデルは `reviewcompass.yaml` で指定する。**推奨既定**：主役 Opus 4.7 ／ 敵対役 Sonnet 4.6 ／ 判定役 Opus 4.7（計画書 §5.9.1）。利用者が yaml で変更可能。

**モデル能力配分の規律（計画書 §5.9.1、2026-05-25 セッション 25 の foundation／design triad-review 実験により制定）**：

- **主役と敵対役は必ず異なるモデルを使う**（敵対役の独立性確保のため）
- 判定役は主役または敵対役と同じモデルを使うことを許容する
- 敵対役と判定役には、反証生成と責務境界判断を担う十分な能力のモデルを割り当てる

旧規律「3 役で異なるモデルファミリーを使う（モデル多様化）」「同モデル使用は禁止」は **撤回された**。モデル多様化単独ではバイアス低減効果が限定的で、能力配分の方が重要と判明したため（実験記録 [../notes/2026-05-25-triad-review-model-allocation-experiment.md](../notes/2026-05-25-triad-review-model-allocation-experiment.md) 由来）。

**実態の配置例**：foundation tasks triad-review（2026-05-26）では「主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7」（実験(エ)継続、design triad-review と同配置）。いずれの役もサブエージェントで、メインセッション（起草者 Opus 4.7）は 3 役のいずれにも入っていない。

### 4.3 サブエージェント呼び出し時の規律

- **プロンプトに自己完結性を持たせる**：サブエージェントは別 session で、メインの作業文脈を共有しない
- **計画書引用は事後検証**：サブエージェントの計画書引用には §番号誤りが発生しうる（セッション 19 で実証）。メインセッションが grep で確認する
- **ファイル書き込みは原則禁止**：読み取りと分析のみ。例外的にレビュー記録の §2 や carry-forward register への追記提案を許容
- **モデル指定**：利用中の adapter が提供する model / provider 指定方法に従う。Claude Code では Agent ツールの `model` パラメータで `"sonnet"`／`"haiku"` を指定していた。Codex や外部 API 経由では、各 adapter の手引きと `config/api-settings.yaml` の provider 設定を参照する

### 4.4 レビュー記録の必須フィールド（§5.4 起草者と判定者の分離）

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

`author.identity` と `reviewer.identity` が異名であることを機械検査の対象とする。

Claude Code 運用時の例では `claude_code_main_session` / `claude_code_subagent` を使っていた。Codex 運用時は `codex_main_session`、外部 API 検証者、または各 adapter が定義する識別子を使う。重要なのは provider 名ではなく、起草者と判定者が分離していることを記録できること。

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
- **作業の打ち切り・先送りの誘導**：利用者の明示承認なく「続きは次セッションで」等と作業を終了・先送りに誘導しない（2026-05-31 セッション 42 追記）

### 5.2 LLM が自律的に決められる項目

- **抽出時のクリーニング作業の細部**（機能名置換、自己適用前提除去等）
- **観点 5（検証可能性）の機械判定可能な所見の指摘**
- **レビュー記録の構造化**（front-matter、節構成）

### 5.3 判断の記録規律

利用者判断の結果は次の場所に記録：

- **計画書方針変更**：計画書の該当節に決定日付付きで記載
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

- **計画書更新 ＋ 基盤整備**：1〜2 コミット（セッション冒頭の方針確定、運用ファイル整備）
- **機能ごとに 1 コミット**：仕様文書 ＋ 運用文書 ＋ レビュー記録の 3 ファイル（または schema/template 等の関連ファイル）
- **機能横断段（review-wave／alignment／approval）**：1 コミット（複数機能の小修正をまとめる）

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
- **Co-Authored-By**：利用中の adapter と利用者方針に従う。Claude Code 運用時の履歴では `Claude Opus 4.7 (1M context) <noreply@anthropic.com>` を使っていたが、Codex 運用では自動付与を前提にしない

### 6.4 コミット前確認

- `git status` で対象ファイルを確認
- `git diff --cached` で内容確認（必要に応じて）
- `--no-verify` や `--no-gpg-sign` は使わない（規律）

### 6.5 push

push は **利用者明示承認**を仰いでから実行。LLM が自律的に push しない。

## 7. 作業完了時レポート

作業を終えて利用者へ返答するときは、adapter や利用モデルに依存しない会話末尾の運用契約として、最低限次を示す：

- **作業サマリ**：このターンで実施した変更、判断、未変更の範囲
- **検証結果**：実行したテスト、確認コマンド、`post_write_verification` の要否と結果
- **現在状態**：`git status` と `next --json` の要点
- **次タスク**：次に着手すべき具体的な作業、または workflow が要求する次 action

未実施・失敗・承認待ち・保留判断がある場合は、完了扱いにせず明記する。commit、push、workflow_state 更新、spec.json 更新などの不可逆または状態変更を伴う操作は、実際に成功した場合だけ作業サマリに記録する。

`next --json` が `post_write_verification`、`reopen_in_progress`、`resume_in_progress`、`unknown` など `completed` 以外を返している場合、次タスクには任意の改善候補ではなく、その workflow 状態に従う次 action を示す。

このレポートは会話末尾の完了報告であり、workflow_state や `spec.json` の正本を代替しない。

## 8. 用語ガイド

### 8.1 「遡及」と「波及」（二軸的定義、2026-05-23 訂正）

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
- **サブエージェント**：敵対役・判定役を実行する別 session または外部 API 検証者。Claude Code では Agent ツール経由、Codex 運用では adapter が利用可能な実行形に従う
- **mode = `subagent_mediated`**：サブエージェント方式のレビュー記録の mode 値

### 8.5 計画書の節番号

- 計画書（`docs/plan/reconstruction-plan-2026-05-21.md`）の節番号は §X.Y 形式
- 引用時は **メインセッションで grep 確認**してから記述（サブエージェントの §番号誤り対策）

## 9. セッション 19 で得られた教訓（参考）

本ガイドラインは次の経験を反映している：

### 9.1 ワークフロー確認の失態

セッション 19 開始時、私（メインセッション）は計画書 §5.4〜§5.7 を読まずに foundation requirements の抽出を始めた。中盤で利用者が「ワークフローを再度読む」と指摘し、intent 段の所在（過去セッションで作成済み）、dogfeeding の §5.23 での既存記述、機能横断レビューの段位置（review-wave／alignment-gate）を確認することになった。**着手前の必読フロー（§1）はこの失態の再発防止策**。

### 9.2 用語混同（遡及／波及）

セッション 19 中盤で A-001（foundation の `not_run` 欠落）発見時、私が「foundation の遡及修正」と表現した。利用者が「遡及ではなく波及。本来は alignment wave の範囲」と訂正。**§3.1 の用語の使い分けはこの訂正を反映**。

### 9.3 機能横断波及所見の集約管理ファイルの新設

A-001 発見時、利用者の指示で ReviewCompass 固有の Markdown 台帳を新設して集約管理する運用パターンが確立した。これ以降、A-003／A-004／A-005／A-007／A-008 が同ファイルに追記され、要件 review-wave で一括消化された。現在は同 Markdown を履歴 source として `learning/workflow/carry-forward-register/sources/` に移し、正本は `reviewcompass-import.yaml` に移行している。

### 9.4 サブエージェントの計画書引用誤り

セッション 19 中盤、敵対役（Sonnet 4.6）が計画書 §5.18.11 を引用したが、実体は §5.18.2 周辺の別箇所だった（引用内容自体は正当）。**§4.3 の事後検証はこの経験を反映**。

### 9.5 サブエージェントの直接書き込みパターン

セッション 19 後半、敵対役が自発的に旧 Markdown 台帳へ直接追記するパターンを確立した。現在は、同じ効率化を維持する場合でも carry-forward register への構造化追記として扱う。

### 9.6 利用者判断の見極め不足

セッション 19 中で、サブエージェント方式の正式採用、A-007 の権限調停（案 1／案 2）、解釈論点 α／う など、利用者判断が必要な論点が複数発生した。**§5 の利用者判断必須項目はこの経験を反映**。

## 10. 関連文書

- 計画書：[../plan/reconstruction-plan-2026-05-21.md](../plan/reconstruction-plan-2026-05-21.md)（§5.4〜§5.8 ワークフロー、§5.23／§5.23.12 dogfooding／サブエージェント方式、§5.19.6 利用者判断の運用ルール）
- 抽出進捗：[../extraction-mapping.md](../extraction-mapping.md)
- 機能横断波及所見：正本 [../../learning/workflow/carry-forward-register/reviewcompass-import.yaml](../../learning/workflow/carry-forward-register/reviewcompass-import.yaml)、履歴 source [../../learning/workflow/carry-forward-register/sources/reviewcompass-pending-cross-feature-findings.md](../../learning/workflow/carry-forward-register/sources/reviewcompass-pending-cross-feature-findings.md)
- レビュー記録雛形：[../../templates/review/manual_dogfooding_review_template.md](../../templates/review/manual_dogfooding_review_template.md)
- TODO：[../../TODO_NEXT_SESSION.md](../../TODO_NEXT_SESSION.md)

## 11. 本ガイドラインの改訂規律

- 本ガイドラインは運用文書であり、計画書の改定なしに更新可能
- 各セッションの経験から新たな教訓が得られた場合、§9 に追記
- 規律変更（§2〜§8）は利用者明示承認後に反映
- 改訂時は最終更新日付を更新
