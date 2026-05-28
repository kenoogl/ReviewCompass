# 次セッション継続用メモ

最終更新：2026-05-29（セッション 38 末。主な達成：(1) 確定済みの再オープン手続き（種別 A-2）を **初運用** して遡及所見 A-001／A-003 を処理、手続き単位の語彙を「まとまり」→「過程」に統一（`2f5ee06`）。(2) 波及所見 A-002 を `pending-cross-feature-findings.md` に A-019 として登録（`a7e0496`）。(3) workflow-management tasks の **7 モデル比較実験** を実施、機能内 must-fix 6 件＋should-fix 17 件＝23 topic を評価、人評価 23 件を記録（`baf2c66`）。**起草者バイアスを構造的に検出**（私 Opus は全 23 件で案 1 を出したが、7 件で他モデル・利用者が「徹底修正側」を採用し覆った）。(4) 統合レビュー記録を作成（`2e46c98`）。(5) **確定 23 件を tasks.md／design.md に反映、workflow-management tasks の triad-review=true に更新**（`2fe42b2`）。**ここまで全て origin/main に push 済み**。**workflow-management tasks の triad-review 段が完了**。次セッション 39 は **依存マップ順で self-improvement tasks 段**（drafting → triad-review、§3.1 の標準手順）から。その後 conformance-evaluation tasks 段、全機能 tasks 完了後は機能横断段（§3.3）。詳細は git log と §3.0／§4）

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

7 モデル比較実験の進行中は「analysis tasks の修正議論」と並行して「**実験データ採取**」が動いていることを常に意識する。具体的には：

- 各議論ごとに `tools/experiments/results/topic-NN-human.yaml` を保存（人本人判定の実験データ）
- 統合レビュー記録 §4.2 に議論履歴を記録
- 説明姿勢は「両論を対称的に提示してバイアス最小化」、推奨を強く押し出さない
- 私（起草者）が孤立判断を出した場合は **起草者バイアスの兆候** として認識

<!-- TEMPLATE_HEADER_END -->

---

## 最重要案件（毎セッション必読、ブートストラップ完了後に対応）

**ワークフロー手続きのナビゲーション問題** — LLM がワークフロー処理手続きを正しく把握しないまま提案する失敗が繰り返されている。根本解は「手続きを問い合わせ可能な機械的ナビゲータに集約し、規律を N→1 のメタ規律に畳む」＝ workflow-management の実装そのもの。現状はブートストラップ期の症状。当面は利用者がガイドする（2026-05-29 セッション 39 利用者決定）。

本体（背景・真因・根本解・着手トリガー）：[docs/notes/2026-05-29-workflow-navigation-bootstrap-issue.md](docs/notes/2026-05-29-workflow-navigation-bootstrap-issue.md)

---

## 1. 起動手順（次セッション開始時）

1. `cd /Users/Daily/Development/ReviewCompass`
2. 本 `TODO_NEXT_SESSION.md` を読む（§0 規律確認）
3. **規律本体 active 必読を Read**（一覧は `docs/disciplines/README.md`、auto memory は索引のみ load のため毎セッション必要）
4. `docs/operations/SESSION_WORKFLOW_GUIDE.md`
5. 計画書 `docs/plan/reconstruction-plan-2026-05-21.md` §5.4〜§5.8 ／ §5.9.6（マルチターンプロトコル相互参照含む、セッション 36 追記）／ §5.12 ／ §5.23 ／ §5.23.12 ／ §5.23.13 ／ §5.24
6. **実験ノート `docs/experiments/n-model-comparison.md` §3.4**（マルチターンプロトコルとプロンプト設計の規律、セッション 36 確立）
7. `.reviewcompass/pending-cross-feature-findings.md`（A-017 ／ A-018 ／ A-019 の 3 件未消化、機能横断段で消化予定）
8. `docs/extraction-mapping.md`
9. `git log --oneline -10`／`git status` で到達点確認

### 1.1 Python 実行時の必須事項（venv 経由起動、毎セッション要確認）

`tools/api_providers/run_role.py` 経由の 7 モデル評価や `tools/experiments/_experiment_n_model.py` 等を実行する際は **必ず venv の Python を直接指定** する：

```
zsh -c 'source ~/.zshrc && /Users/Daily/Development/ReviewCompass/.venv/bin/python3 <script.py>'
```

**避けるべき形**：`python3 <script.py>`（環境変数干渉あり、PyYAML なし）／ `zsh -c 'source ~/.zshrc && python3 <script.py>'`（API キーは取れるが PyYAML なし）。理由：`subprocess.run([sys.executable, ...])` が venv 内パッケージを参照するには、起動時の Python が venv のものでなければならない。

## 2. ワークフロー上の現在位置（セッション 38 末）

実態は **spec.json の workflow_state から確認**（§0.1）：

- intent 層／feature-partitioning 層／requirements 段／design 段：全 7 機能で全段 true
- **tasks 段**：
  - foundation／runtime／evaluation／analysis／**workflow-management**：drafting＋triad-review=true（機能内対処完了。workflow-management はセッション 38 で確定 23 件反映＋triad-review=true 完了）
  - **残 2 機能（self-improvement／conformance-evaluation）：全 false**（次は self-improvement の drafting から）
- implementation 段：全段 false
- **注**：全 7 機能の spec.json で `reopened` を 6 フェーズに拡張済み（セッション 37）。workflow-management の requirements／design は A-2 再オープンで再承認済み、recheck クリア済み（セッション 38）

## 3. 次の作業候補

workflow-management tasks の triad-review 段がセッション 38 で完了（確定 23 件反映＋triad-review=true、push 済み）。次セッション 39 は **依存マップ順で self-improvement tasks 段** から。

### 3.0 セッション 39 起点の具体作業（self-improvement tasks 段）

§3.1 の標準手順（analysis／workflow-management tasks で確立）に従う：

1. **self-improvement tasks.drafting**：設計書 §14 要件追跡表（Req 受入単位 × 担当タスク単位）を骨格として tasks.md を作成する、DVT 必要なら登録
2. **tasks.triad-review（3 役レビュー）**：主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7（サブエージェント方式）
3. **統合レビュー記録の起草 → 7 モデル比較実験 → 利用者議論（人評価 topic-NN-human.yaml 保存）→ tasks.md／design.md 反映 → spec.json triad-review=true → コミット → push**（§3.1 の手順 3〜9）

その後 conformance-evaluation tasks 段。全機能 tasks 完了後は機能横断段（§3.3）。

**self-improvement の接合面に注意**：workflow-management T-010 の approved_update スキーマと self-improvement §8.4 の整合（持ち越し A-019）、および §13.5 の時系列契約（workflow-management F-016 案 3 で依存マップ駆動の自動 reopen を採用）。self-improvement 側の tasks レビューでこれらの接合面が再び論点になりうる。

**workflow-management tasks の確定 23 件の反映実績**は統合レビュー記録 `.reviewcompass/specs/workflow-management/reviews/2026-05-28-tasks-triad-review.md` §4.3 が正本（案 1 が 14／案 2 が 6／別案が 3、起草者バイアス 7 件検出を §4.2 に記録）。

### 3.1 各機能の標準進め方（analysis tasks で確立した手順、踏襲）

各機能で次の流れ：

1. **tasks.drafting**：対象機能の設計書 §14 要件追跡表（Req 受入単位 × 担当タスク単位）を骨格として tasks.md を作成する、DVT 必要なら登録
2. **tasks.triad-review（3 役レビュー）**：サブエージェント方式（主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7）。サブエージェント生ログは `~/.claude/projects/-Users-Daily-Development-ReviewCompass/<session-id>/subagents/` に残るため、結果は後セッションでも復元可能
3. **統合レビュー記録の起草**：`.reviewcompass/specs/<機能>/reviews/<日付>-tasks-triad-review.md` に front-matter ＋ 主役所見 ＋ 敵対役所見＋ counter_status ＋ 判定役判定 ＋ §4 統合節（must-fix 対処方針案、利用者議論履歴、反映箇所）
4. **機能横断波及の pending 追記**：`.reviewcompass/pending-cross-feature-findings.md` に追加（機能横断段で消化）
5. **7 モデル比較実験 1 回目**（実験ノート §2 共通フレームワーク準拠）：
   - プロンプト生成：`_generate_eval_prompts_<feature>_temp.py` 新規作成、機能内 must-fix＋should-fix を topic として展開
   - API 5 モデル並列実行：`_run_eval_experiment_<feature>_temp.py` 新規作成、必ず venv 経由起動（§1.1）
   - Sonnet 4.6 CLI 経路：Agent ツール経由で 5 並列 × N ラウンド
   - Opus 4.7（メインセッション）：起草者判断、`_generate_opus_judgments_<feature>_temp.py` で一括生成
   - 質問返し分類：`_classify_api_responses_temp.py`（decision フィールドの有無で二分）
   - マルチターン続行（必要に応じて）：`_run_eval_experiment_<feature>_multi_turn_temp.py`、proxy_responses_<feature>_temp.yaml に代理回答を 1 ファイルでまとめる（設計原則：事実情報のみ／推奨・意見・評価なし／未確定の明示、実験ノート §3.4 準拠）
   - 集計：`_aggregate_<feature>_eval_temp.py`、両軸 2 表構成（1 ターン目応答分布 ＋ 最終判定分布）
6. **利用者議論段階**（規律 [must-fix-discussion-obligation]）：
   - 完全一致は一括承認可能（7 モデル全員一致なら議論短縮）
   - 割れ／分散は 1 件ずつ平易な日本語で説明（§0.4 実験意識を保持、両論を対称的に提示してバイアス最小化）
   - **私（起草者）が孤立判断を出した場合は起草者バイアスの兆候**（analysis F-007 ／ F-002 で検出済み、§6 観点別考察への重要観察）
   - 各議論ごとに `tools/experiments/results/topic-NN-human.yaml` を保存
   - 統合レビュー §4.2 に議論履歴記録
7. **tasks.md ／ design.md 反映**（必要なら軽量再オープン手続き、§5.23.13）、grep で機械的照合
8. **spec.json の tasks.triad-review=true 更新**（利用者明示承認必要、workflow-precheck spec-set）
9. **コミット → push**（利用者明示承認必要、workflow-precheck commit／push）

### 3.2 残作業の補完項目（次セッション以降の任意）

- **analysis 完全一致 15 件の人本人判定の遡及保存**：`topic-{54〜75}-human.yaml` のうちセッション 36 で未保存の 15 件分（詳細は git log のセッション 36 記録）
- **実験ノート §5／§6 への追記**：両軸 2 表構成を §5 のケースとして追記、§6 観点別考察に起草者バイアス検出の観察を追加（analysis tasks ＋ workflow-management tasks の 2 ケース分）
- **§5.12 改訂の準備**：全機能 tasks 段完了後の機能横断段で §5.12.11 アサイン権限の具体設計と §5.23.13.3 末尾「残り 27 件」の統合的取り込み

### 3.3 全機能 tasks 段完了後の機能横断段（review-wave）

- **7 モデル評価 2 回目**：同根問題と機能横断波及（A-017 ／ A-018 ／ F-013 ／ A-005 ／ §5.23.13.3 残り 27 件）の一括評価
- **DVT 解除**：evaluation DVT-001 ／ analysis DVT-A001 ／ DVT-A002 ／ DVT-A003（残 3 機能で追加 DVT が出る可能性）
- **§5.12 改訂統合**：§5.12.11 アサイン権限新設、計画書 §5.9.6 ／ §5.9.7 ／ §5.12 への正本化（実験ノート §3.4 マルチターンプロトコルも統合）

---

## 4. 直近の確定事項

- **セッション 38（2026-05-28）の総括**：(1) 確定済み再オープン手続き（A-2）を初運用し A-001／A-003 を処理、語彙を「過程」に統一（コミット `2f5ee06`）。(2) A-002 を A-019 として pending に登録（`a7e0496`）。(3) workflow-management tasks の 7 モデル比較実験＋人評価 23 件（`baf2c66`）。確定：案 1 が 14／案 2 が 6／別案が 3（§3.0.1）。起草者バイアスを構造的に検出（私 Opus 全件案 1 → 7 件で覆る）。**未 push**（origin より複数コミット先行）。仕上げ（統合記録・反映・spec.json・push）は §3.0
- **セッション 37（2026-05-28）の総括**：workflow-management tasks.drafting 完了（`626c4e2`）、3 役 triad-review 実施（主役 20／敵対役 10／判定役 must-fix 9・should-fix 17・leave 4）、再オープン手続きを定義・記録（`9ffe221`）。3 役レビューの所見詳細・判定は本セッション 38 で生ログから回収済み（統合レビュー記録に反映予定、§3.0 手順 2）。生ログはセッション 37 ID `3e297d96` の `subagents/`
- セッション 36 以前の確定事項は git log および [docs/archive/todo/](docs/archive/todo/) 配下の snapshot を参照

## 5. 関連参照

- 計画書：`docs/plan/reconstruction-plan-2026-05-21.md`（§5.9.6 マルチターンプロトコル相互参照はセッション 36 追記、§5.23.13 軽量手続き許容はセッション 34 新設）
- 運営ガイド：`docs/operations/SESSION_WORKFLOW_GUIDE.md`
- 雛形：`templates/`（todo、specs、review 配下）
- 持ち越し所見：`.reviewcompass/pending-cross-feature-findings.md`（A-017 ／ A-018 ／ A-019 の 3 件未消化、機能横断段で消化予定）
- 抽出進捗：`docs/extraction-mapping.md`
- 7 モデル比較実験ノート：`docs/experiments/n-model-comparison.md`（§2 共通フレームワーク、§3.4 マルチターンプロトコルとプロンプト設計の規律（セッション 36 新設）、§6 観点別考察）
- 規律ファイル本体：`docs/disciplines/`（一覧は同ディレクトリ README.md、avoid-compound-bash は active 必読 13 件目）
- 過去 TODO snapshot：`docs/archive/todo/` 配下

セッション終了時の自動記録：`python3 tools/session-log-converter.py --latest ~/.claude/projects/-Users-Daily-Development-ReviewCompass docs/sessions/session-<NN>-<YYYY-MM-DD>.md`
