# 次セッション継続用メモ

最終更新：2026-05-29（セッション 40 末。主な達成：**tasks フェーズの機能横断段（review-wave）で機能横断所見 3 件をすべて消化＋DVT 2 件を解除**。(1) round-2 7 モデル比較実験（topic-121 A-018／topic-122 A-019）を実施・データ保存（`ad253fe`）。(2) **A-018**（must-fix、foundation 語彙正本件数の自己矛盾）：別案を採用。foundation/design.md 内部のみの自己矛盾で下流 analysis 7／evaluation 6 は各機能の正しい参照範囲と確定。**正規再オープン（種別 A-1、4 過程）**で foundation design を再オープン・修正・再承認（`361317d`／`e5f8167`）。(3) **A-019**（must-fix）：案1、workflow-management T-010 の独自スキーマ・項目名を廃止し self-improvement §8.4 を唯一の定義元として参照（`f17813c`）。(4) **A-017**（should-fix）：案1、節を持たない 3 機能の tasks.md に「機能横断段への持ち越し事項」節を追記し全 7 機能で統一（`3e8b8ba`）。(5) DVT-S001／DVT-C002 を解除（`e2a7387`）。未消化所見 0 件。**さらに同セッションで tasks フェーズを完了**：ワークフロー現在位置の確認を機に tasks 機能横断段（review-wave）を締め、**2軸整合性監査（縦軸＝各機能 intent→tasks の 7 並列検証＋横軸＝機能間）を新規実施**。検出した本物の断層を対処（evaluation design 再オープンで manifest 13項目統一＝#3／手戻り種別14→15＝#4／discipline-update 文言＝#5／design 先送り論点を DVT 転記＝T-1／編集起因の誤り2件＝B群、`622865c`／`8328873`／`de7ef8a`）。全7機能の tasks.review-wave／alignment／approval を承認（`b04ae8d`）＝**tasks フェーズ完了。仕様4段階（intent／requirements／design／tasks）すべてが全7機能で承認済み**。監査記録：docs/reviews/tasks-alignment-audit-2026-05-29.md。**次セッション 41 は §5.12 改訂に着手**（利用者決定 2026-05-29 セッション40 末）。検討項目 6 件＝(1) §5.12.11 アサイン権限新設／(2) 残り 27 件統合的取り込み／(3) N モデル比較プロトコル正本化／(4) マルチターン対話プロトコル統合／(5) 2軸整合性監査の正本化／(6) 実験データ §6.14・§6.15 を §5.12.11 設計に反映。詳細は §3.1。実装フェーズは §5.12 改訂後。**§5.12 改訂しても workflow-management 実装まで利用者の監視は必要**（最重要案件ノート §4）。実験データ統合のための新規ファイル＝実験ノート §6.14／§6.15（追記）、`docs/experiments/triad-review-summary-2026-05-29.md`（新規・三役レビュー集計＝レビュー生成の質）、`docs/experiments/evaluation-index-for-external-review.md`（新規・外部 AI 評価者向け）も §5.12 改訂で使う）

作業ディレクトリ：`/Users/Daily/Development/ReviewCompass/`、リポジトリ：`git@github.com:kenoogl/ReviewCompass.git`（main ブランチ）

---

<!-- TEMPLATE_HEADER_START：本ヘッダは templates/todo/TODO_NEXT_SESSION.template.md から派生。 -->

## 0. ReviewCompass 利用にあたる重要規律

毎セッション開始時に確認し、毎作業前に守る。

### 0.1 提案前必須確認

「次の作業」「次のステップ」を利用者に提案する前に、次を機械的に確認し応答内で明示宣言：

1. **`workflow_state` を必ず読む**：対象機能の `.reviewcompass/specs/<機能>/spec.json` の `workflow_state` を Read。要約や記憶を根拠にしない。本 TODO §3 や §4 は要約に過ぎず正本は spec.json
2. **規律と照合**：運営ガイド `docs/operations/SESSION_WORKFLOW_GUIDE.md` §2.3 と照合、「approval を得てから次フェーズに進む」前提を毎回確認
3. **正本と照合**：TODO・設計メモ・要約文を信頼の根拠にせず、提案前に spec.json／計画書／運営ガイド／git log の正本と照合

### 0.2 利用者明示承認が必要な不可逆操作

次は利用者の **明示承認** なしに実行しない：

- spec.json の `workflow_state.<フェーズ>.<段>` を true に変更／フェーズ移行
- git commit／git push
- 計画書の方針変更／大規模な再設計（複数機能にまたがる責務分担変更等）
- 規律ファイルの追加・変更（docs/disciplines/ 配下、軽量移送手続き経由）

承認の判定基準：「承認」「OK」「採用」「進めて」「はい」「案 ア」等の明示的肯定発言、または AskUserQuestion 等での明示選択のみ。議論継続・停止・方法論指示・沈黙は承認とみなさない。

### 0.3 起草者と判定者の分離（計画書 §5.4）

drafting 段は actor=human または llm（草案作成のみ）、triad-review 段は actor=llm（主役・敵対役・判定役の 3 役、サブエージェント方式 §5.23.12）。**同一の actor が起草と判定を兼ねない**。レビュー記録 front-matter に `author.identity` と `reviewer.identity` を異名必須記載、機械検査対象。

### 0.4 実験意識の保持（2026-05-28 セッション 36 規律）

7 モデル比較実験の進行中は「修正議論」と並行して「**実験データ採取**」が動いていることを常に意識する：

- 各議論ごとに `tools/experiments/results/topic-NN-human.yaml` を保存（人本人判定の実験データ）
- 統合レビュー記録 §4.2 に議論履歴を記録
- 説明姿勢は「両論を対称的に提示してバイアス最小化」、推奨を強く押し出さない
- 私（起草者）が孤立判断を出した場合は **起草者バイアスの兆候** として認識

<!-- TEMPLATE_HEADER_END -->

---

## 最重要案件（毎セッション必読、ブートストラップ完了後に対応）

**ワークフロー手続きのナビゲーション問題** — LLM がワークフロー処理手続きを正しく把握しないまま提案する失敗が繰り返されている。根本解は「手続きを問い合わせ可能な機械的ナビゲータに集約し、規律を N→1 のメタ規律に畳む」＝ workflow-management の実装そのもの。現状はブートストラップ期の症状。当面は利用者がガイドする（2026-05-29 セッション 39 利用者決定）。

本体（背景・真因・根本解・着手トリガー、§7.1 に「複数機能の同時再オープンの挙動」論点を追記）：[docs/notes/2026-05-29-workflow-navigation-bootstrap-issue.md](docs/notes/2026-05-29-workflow-navigation-bootstrap-issue.md)

---

## 1. 起動手順（次セッション開始時）

1. `cd /Users/Daily/Development/ReviewCompass`
2. 本 `TODO_NEXT_SESSION.md` を読む（§0 規律確認）
3. **規律本体 active 必読を Read**（一覧は `docs/disciplines/README.md`、auto memory は索引のみ load のため毎セッション必要）
4. `docs/operations/SESSION_WORKFLOW_GUIDE.md` と `docs/operations/REOPEN_PROCEDURE.md`（再オープン手続きの 4 過程）
5. 計画書 `docs/plan/reconstruction-plan-2026-05-21.md` §5.4〜§5.8 ／ §5.9.6 ／ §5.12 ／ §5.23 ／ §5.23.12 ／ §5.23.13 ／ §5.24
6. **実験ノート `docs/experiments/n-model-comparison.md` §3.4**（マルチターンプロトコルとプロンプト設計の規律）
7. `git log --oneline -10`／`git status` で到達点確認

### 1.1 Python 実行時の必須事項（venv 経由起動、毎セッション要確認）

`tools/experiments/_experiment_n_model.py` 等を実行する際は **必ず venv の Python を直接指定** する：

```
zsh -c 'source ~/.zshrc && /Users/Daily/Development/ReviewCompass/.venv/bin/python3 <script.py>'
```

**避けるべき形**：`python3 <script.py>`（環境変数干渉あり、PyYAML なし）／ `zsh -c 'source ~/.zshrc && python3 <script.py>'`（API キーは取れるが PyYAML なし）。理由：`subprocess.run([sys.executable, ...])` が venv 内パッケージを参照するには起動時の Python が venv のものでなければならない。

## 2. ワークフロー上の現在位置（セッション 40 末）

実態は **spec.json の workflow_state から確認**（§0.1）：

- intent 層／feature-partitioning 層／requirements 段／design 段：全 7 機能で全段 true
- **tasks 段：全 7 機能で完了（drafting／triad-review／review-wave／alignment／approval すべて true、セッション40）**。review-wave＝機能横断所見 A-017/18/19 消化＋DVT 解除、alignment＝2軸整合性監査、approval＝利用者承認。`pending-cross-feature-findings.md` 未消化 0 件
- **implementation 段：全段 false（次はここから）**
- → **仕様4段階（intent／requirements／design／tasks）が全7機能で承認済み。残るは implementation のみ**
- **注（再オープン履歴）**：再承認済み＝workflow-management の requirements／design（A-2、セッション 38）／self-improvement の requirements／design（A-2、セッション 39）／conformance-evaluation の design（A-1、セッション 39）／**foundation の design（A-1、A-018 対処、セッション 40）／evaluation の design（A-1、#3 manifest 統一、セッション 40）**。いずれも recheck クリア済み、`reopened.*=true` は履歴として保持

## 3. 次の作業（セッション 41 起点）

### 3.1 やること（次セッションの主作業：§5.12 改訂）

**利用者決定（2026-05-29 セッション40 末）：次セッションは §5.12 改訂に着手する**。tasks フェーズ完了（仕様4段階すべて全7機能で承認済み）＋実験データのまとめ完了で、§5.12 改訂の前提条件が揃った。

#### §5.12 改訂の検討項目（6 件、明示承認と腰を据えた作業が必要）

1. **§5.12.11 アサイン権限の新設（中核）**：論文査読システム類似。「最終判断役が他のレビュアに判定をアサインし結果を集約する」権限を §5.12.4 権限範囲に追加。案 B 路線＝§5.12.11 1 か所完結記述、§5.12.4／§5.12.5／§5.12.7 は参照のみの軽微更新。詳細論点・運用パターンは実験ノート §6.9 を統合
2. **§5.23.13.3 末尾「残り 27 件」の統合的取り込み**：内訳＝セッション34 整合性確保レビューの残務 23 件（影響度低の未反映／部分反映、git log `2509db7` 以前で追跡可能）＋セッション35 縦整合チェック発見 4 件（workflow-management 対応表行欠落 1、analysis の「12 criteria」残存 3）
3. **N モデル比較プロトコルの正本化**：§5.9.6／§5.9.7／§5.12 への組み込み。現状は実験ノートが正本＋計画書本体に軽量相互参照のみ
4. **マルチターン対話プロトコルの統合**：実験ノート §3.4（質問返し時の代理回答、最大 5 ターン、両軸 2 表構成、§3.4.2 枠組み伝染バイアス対策）を §5.9.6／§5.9.7／§5.12 へ統合
5. **2軸整合性監査の正本化（本セッション40 追加）**：alignment 段の正本手順として組み込み。具体：alignment 段の完了述語に「上流フェーズの先送り論点が解決済みか、DVT として延期理由付きで転記済みか」を含める（監査記録 §6／§7 の教訓）
6. **実験データ（本セッション40 追加）を §5.12.11 設計に反映**：起草者バイアスの数値裏付け（自起草機能 60-66%）→ 代役は独立モデル中心／代役候補序列（GPT-5.5 86%）→ アサイン先選定／confidence 較正不良 → 自己申告を権限ゲートに使わない／case_scores 小ギャップ・別案・質問返し → エスカレーション条件

#### §5.12 改訂で必読の資料

- **計画書**：`docs/plan/reconstruction-plan-2026-05-21.md` §5.12（人間代役機構）／§5.12.10 末尾（§5.12.11 起草時必須参照）／§5.9.6（実施タイミング、N モデル比較への発展）／§5.23.13.3 末尾（残り 27 件の同期記述）
- **実験ノート**：`docs/experiments/n-model-comparison.md`
  - §1〜§3：共通フレームワーク（事前登録 12 観点、§3.4 マルチターンプロトコル、§3.4.2 枠組み伝染バイアス対策）
  - **§6.13／§6.14**：foundation・runtime ／ 残り 5 機能＋機能横断 2 回目の統合集計
  - **§6.15**：事後発見の指標 8 件＋特徴的所見 8 件（5 軸フレームワークに対応づけ）
  - §6.9：観点 9 §5.12.4 権限範囲チューニングへの示唆（アサイン権限の運用パターン議論）
- **2軸整合性監査記録**：`docs/reviews/tasks-alignment-audit-2026-05-29.md`（§6 対処方針、§7 手続き上の教訓）
- **三役レビュー集計サマリ**：`docs/experiments/triad-review-summary-2026-05-29.md`（レビュー生成の質、§6.14/§6.15 と別レイヤー）
- **外部 AI 評価インデックス**：`docs/experiments/evaluation-index-for-external-review.md`（2 つの評価レイヤーの整理）
- **重要案件ノート**：`docs/notes/2026-05-29-workflow-navigation-bootstrap-issue.md`（§7.1 同時再オープン論点も含む）

#### 進行順序の制約（既に満たされた）

- 「全機能 tasks 段完了後」（2026-05-27 セッション32 利用者判断）→ ✅ セッション40 で達成
- 利用者明示判断「現時点では、レビューを優先。この議論は task 段終了後に検討・機能実装。ReviewCompass の実装段でテスト」（2026-05-27 セッション32）

### 3.2 §5.12 改訂後に残る作業

- **implementation（実装）フェーズ**：仕様4段階承認済み。依存順（`feature-dependency.yaml#phase_order`）で実装に着手。各機能 implementation の drafting → triad-review → review-wave → alignment → approval を回す。**workflow-management の実装は §5.12 改訂で確定する論点（cross-spec-alignment 段集合・§5.12.11 アサイン権限・DVT-W003 規律変更段集合）を実装する側のため、§5.12 改訂後に着手**。他 6 機能は §5.12 改訂とほぼ独立で、§5.12 改訂と並行も可
- **ブートストラップ期の根本案件（ワークフロー・ナビゲーション問題）の根本解＝workflow-management の実装**は、この implementation フェーズで対応（最重要案件ノート §5）。**§5.12 改訂しても workflow-management 実装まで利用者の監視は必要**という認識を持って進める

### 3.2 残作業の補完項目（任意・低優先）

- **analysis 完全一致 15 件の人本人判定の遡及保存**：`topic-{54〜75}-human.yaml` のうちセッション 36 で未保存の 15 件分（詳細は git log のセッション 36 記録）
- **実験ノート §5／§6 への追記**：両軸 2 表構成を §5 のケースに、§6 観点別考察に起草者バイアス検出の観察を追加

> 完了済みの作業手順の詳細（各機能 tasks の標準進め方、機能横断段 review-wave の参照元・todo）は本セッション 40 で役目を終えた。必要時は git 履歴と `docs/archive/todo/` の snapshot を参照。

---

## 4. 直近の確定事項

- セッション 40：機能横断所見 3 件消化＋DVT 2 件解除＋**2軸整合性監査＋tasks フェーズ完了**（冒頭サマリ参照）。再オープン記録は [foundation A-018](docs/reviews/reopen-classification-2026-05-29-foundation-a018.md)／[evaluation #3 manifest](docs/reviews/reopen-classification-2026-05-29-evaluation-manifest.md)、監査記録は [tasks-alignment-audit](docs/reviews/tasks-alignment-audit-2026-05-29.md)
- セッション 36〜39 以前の確定事項は git log および [docs/archive/todo/](docs/archive/todo/) 配下の snapshot を参照

## 5. 関連参照

- 計画書：`docs/plan/reconstruction-plan-2026-05-21.md`
- 運営ガイド：`docs/operations/SESSION_WORKFLOW_GUIDE.md`、再オープン手続き：`docs/operations/REOPEN_PROCEDURE.md`
- 雛形：`templates/`（todo、specs、review 配下）
- 持ち越し所見：`.reviewcompass/pending-cross-feature-findings.md`（未消化 0 件、対処済み所見の記録）
- 7 モデル比較実験ノート：`docs/experiments/n-model-comparison.md`（§2 共通フレームワーク、§3.4 マルチターンプロトコル、§6 観点別考察）
- 規律ファイル本体：`docs/disciplines/`（一覧は同ディレクトリ README.md）
- 過去 TODO snapshot：`docs/archive/todo/` 配下

セッション終了時の自動記録：`python3 tools/session-log-converter.py --latest ~/.claude/projects/-Users-Daily-Development-ReviewCompass docs/sessions/session-<NN>-<YYYY-MM-DD>.md`
