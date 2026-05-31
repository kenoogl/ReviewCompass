# 次セッション継続用メモ

最終更新：2026-05-31（セッション 41 末。主な達成：**§5.12 改訂の検討 6 項目中 5 項目＋メタ気づきから新規律（post-write-verification）を発効、合計 5 つの確定**。(1) 運営ガイド §4.2 の誤記訂正＝主役＝メインセッション誤記を計画書 §5.9.1・実態に整合（`b6bd1e4`）。(2) **項目 1＋6（アサイン権限）**：§5.12.11 を新節として起草、論点 1〜7 を §3.3 a-1 流儀で議論・確定（外形指標発火・複数モデル独立裁定・重み付けスコア・コンシェルジュ質的集約・信頼度ベース撤回・記録拡張・人への説明義務）。独立検証 8 点反映、関連 4 節を軽微更新（`fce0061`）。(3) **項目 3＋4（プロトコル正本化）**：N モデル比較＋マルチターン対話＋プロンプト設計規律を §5.9.6 に一元化、§5.12.3 は相互参照のみ。独立検証で配置見直し 6 点修正（`a66da5c`）。(4) **項目 5（alignment 段正本化）**：§5.5 alignment 段を拡張、縦軸 5 観点・横軸 4 項目・統合・完了述語・§5.6 連動を本体記述。利用者指示で **intent までの全段遡及**に強化、DVT を初出定義、独立検証 7 点修正（`ce2ba60`）。**(5) post-write-verification 規律の新設＋発効**：本セッションのメタ気づき（起草者の自己検証では捕まらない誤りが系統的に混入することの実証）を恒久的な規律として新設。論点 A〜E＋追加項目を確定後、**独立 3 系統で 5 回の検証ループを実施**。4 回目で GPT-5.5 が ALL_CLEAR、5 回目で Gemini-3.1-pro も ALL_CLEAR（独立 3 系統の発効条件達成）。Sonnet の最後の高 2 件を反映後、**正式書き込み完了**（規律ファイル `discipline_post_write_verification.md` 新設＋計画書 §5.8 補助層 D 箇条書きと独立小節＋§5.12.8 リスト＋§5.9.6 (d) 確定化＋規律 README）。利用者明示承認「OK」（2026-05-31 セッション 41 末）。**特筆**：small=1 体は起草者系統（Anthropic）と異なる Google `gemini-3.5-flash` を既定とし、同モデル衝突を構造的に予防（利用者提案）。検証経緯は `docs/notes/post-write-verification-review/` 配下に保全。**次セッション 42 の最重要案件＝§5.12 改訂の項目 2（残り 27 件統合取り込み）**。これ以降の正本書き込みは本規律（補助層 D）の適用対象＝大規模は独立 3 系統で検証必須。仕様 4 段階完了（intent／requirements／design／tasks）は変更なし、implementation フェーズは項目 2 完了後）

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

## 3. 次の作業（セッション 42 起点）

### 3.1 最重要案件：§5.12 改訂の項目 2（残り 27 件の統合的取り込み）

セッション 41 で **§5.12 改訂の検討 6 項目中 5 項目＋ post-write-verification 規律（メタ気づき発の追加項目）が完了**。残るのは項目 2（残り 27 件の統合取り込み）のみで、これが次セッション 42 の最重要案件。

**次セッション 42 の運用方針（利用者指示 2026-05-31 セッション 41 末）**：項目 2 の対応は **自律実行（proxy モード）** を試す。本セッション 41 で発効した §5.12.11 アサイン権限を本格運用し、代理役（proxy）が 27 件を自律的に判定。決められないもの（外形指標が発火したもの）だけアサイン → 集約 → 人間エスカレーション。**本セッション 41 で発効した 2 つの規律（§5.12.11 アサイン権限と post-write-verification）の最初の本格運用試行**となる重要なセッション。

**項目 2 の中身**：セッション 34 整合性確保レビューの残務 23 件＋セッション 35 縦整合チェック発見 4 件。影響度低の未反映・部分反映項目。1 件ずつ要否判断する地道な作業。多重リマインダ箇所（§5.23.13.3 末尾／§5.12.10 末尾／本 TODO）はいずれも既存記述のまま。

**実施手順**：

1. 多重リマインダ 3 箇所の正本（§5.23.13.3 末尾）を読み、残り 27 件のリスト性質を確認
2. git log（`2509db7` 以前）で各件の経緯を追跡可能
3. 各件について「現状取り込み済み／要取り込み／不要（軽微で却下）」を判定
4. 取り込みが必要な件を反映、不要と判断した件は理由付きで multiple リマインダから消化
5. 取り込み後は **post-write-verification 規律（補助層 D）に従い、独立 3 系統で検証**してから書き込み・コミット

**前提**：post-write-verification 規律が発効済み（コミット `<セッション41で確定>`）。次セッション以降の正本書き込みは**本規律の適用対象**となる（大規模書き込みは独立 3 系統での検証必須、小規模は Gemini-3.5-flash で 1 体検証）。

### 3.2 完了済み（セッション 41）

- **§5.12 改訂の項目 1＋6（§5.12.11 アサイン権限）**：コミット `fce0061`
- **§5.12 改訂の項目 3＋4（プロトコル正本化）**：コミット `a66da5c`
- **§5.12 改訂の項目 5（alignment 段 2 軸整合性監査の正本化）**：コミット `ce2ba60`
- **post-write-verification 規律の新設（メタ気づき発）**：本セッション末でコミット予定
  - 規律ファイル：`docs/disciplines/discipline_post_write_verification.md`
  - 計画書 §5.8 補助層 D（箇条書き＋独立小節）
  - 計画書 §5.12.8 多層防御リスト更新
  - 計画書 §5.9.6 (d) 確定化
  - 規律 README 更新
  - 独立 3 系統での 5 回検証ループ実証（OpenAI／Google で ALL_CLEAR）
  - 検証経緯ファイル：`docs/notes/post-write-verification-review/`（プロンプト＋ 5 回分の結果）

### 3.4 §5.12 改訂後の実装フェーズ

- **implementation（実装）フェーズ**：仕様4段階承認済み。依存順（`feature-dependency.yaml#phase_order`）で実装に着手。各機能 implementation の drafting → triad-review → review-wave → alignment → approval を回す。**workflow-management の実装は §5.12 改訂で確定する論点（cross-spec-alignment 段集合・§5.12.11 アサイン権限・DVT-W003 規律変更段集合）を実装する側のため、§5.12 改訂後に着手**。他 6 機能は §5.12 改訂とほぼ独立で、§5.12 改訂と並行も可
- **ブートストラップ期の根本案件（ワークフロー・ナビゲーション問題）の根本解＝workflow-management の実装**は、この implementation フェーズで対応（最重要案件ノート §5）。**§5.12 改訂しても workflow-management 実装まで利用者の監視は必要**という認識を持って進める

### 3.4 残作業の補完項目（任意・低優先）

- **analysis 完全一致 15 件の人本人判定の遡及保存**：`topic-{54〜75}-human.yaml` のうちセッション 36 で未保存の 15 件分（詳細は git log のセッション 36 記録）
- **実験ノート §5／§6 への追記**：両軸 2 表構成を §5 のケースに、§6 観点別考察に起草者バイアス検出の観察を追加

### 3.5 次セッション開始時に必読の資料

- 本 TODO（§0 規律確認）
- 規律本体 active 必読（一覧は `docs/disciplines/README.md`）
- `docs/notes/2026-05-31-discipline-post-write-verification-drafts.md`（検証待ち草案、最重要案件）
- 議論ログ `docs/notes/2026-05-30-section-5-12-revision-log.md`（§5.12 改訂の経緯と決定事項）
- 計画書 §5.12 全体（§5.12.11 アサイン権限）／§5.9.6（N モデル比較プロトコル正本化）／§5.5 alignment 段（2 軸整合性監査）
- 既存実験基盤：`tools/experiments/_experiment_n_model.py` 等の使い方を確認

> 完了済みの作業手順の詳細（各機能 tasks の標準進め方、機能横断段 review-wave の参照元・todo、§5.12 改訂の論点議論）は本セッション 41 で役目を終えた。必要時は git 履歴（コミット `b6bd1e4`／`fce0061`／`a66da5c`／`ce2ba60`）と `docs/archive/todo/` の snapshot を参照。

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
