# 次セッション継続用メモ

最終更新：2026-05-28（セッション 37 末。本セッションの主な達成：(1) workflow-management tasks.drafting 完了（T-001〜T-011 の 11 タスク起草、コミット `626c4e2`）。(2) workflow-management tasks の 3 役 triad-review 実施（主役 Sonnet 4.6 が 20 件、敵対役 Opus 4.7 が独立発見 10 件、判定役 Opus 4.7 が must-fix 9 件／should-fix 17 件／leave-as-is 4 件と判定。must-fix のうち A-001／A-003 は遡及、A-002 は波及）。(3) 遡及所見 A-001（再オープン手続きが design 未定義）への対処の前提として、**再オープン手続きを定義・正式記録**（4 まとまり構成＝判定とフラグ差し戻し／正本修正／連鎖再実施／完了、暫定版。計画書 §5.6.1 新設／§5.24.6 構造例の reopened を 6 フェーズに／§5.24.8.1 新設、docs/operations/REOPEN_PROCEDURE.md 新設、workflow-management design.md §reopen 機械強制モデル §5、7 機能 spec.json の reopened を 6 フェーズ化、抽出対応表更新、コミット `9ffe221`）。素材 docs/coordination/workflow-repair-procedure.md の 10 ステップを現在の 5 段ワークフローに再構成。記録漏れの発見＝過去ログ調査で「素材に手続き定義があるのに ReviewCompass 正本に断片しか転記されていない」ことを確認。(4) 許可設定改善（settings.local.json に Task／Agent 起動を許可追加＋`defaultMode: auto` 設定）。(5) A-017／A-018 の WARN（コミット時の未消化所見警告）は機能横断段で消化予定の既知事項として**承知の上で続行する方針を確定**（pending-cross-feature-findings.md §2 に注記）。コミット 2 件は **push 未実施**（origin より 2 コミット先行）。次セッション 38 は **workflow-management tasks の triad-review 続き：確定した 4 まとまり手続きで A-001／A-003 を再オープン処理** から再開。詳細は git log）

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

## 1. 起動手順（セッション 37 開始時）

1. `cd /Users/Daily/Development/ReviewCompass`
2. 本 `TODO_NEXT_SESSION.md` を読む（§0 規律確認）
3. **規律本体 active 必読を Read**（一覧は `docs/disciplines/README.md`、auto memory は索引のみ load のため毎セッション必要）
4. `docs/operations/SESSION_WORKFLOW_GUIDE.md`
5. 計画書 `docs/plan/reconstruction-plan-2026-05-21.md` §5.4〜§5.8 ／ §5.9.6（マルチターンプロトコル相互参照含む、セッション 36 追記）／ §5.12 ／ §5.23 ／ §5.23.12 ／ §5.23.13 ／ §5.24
6. **実験ノート `docs/experiments/n-model-comparison.md` §3.4**（マルチターンプロトコルとプロンプト設計の規律、セッション 36 確立）
7. `.reviewcompass/pending-cross-feature-findings.md`（A-017 ／ A-018 の 2 件未消化、機能横断段で消化予定）
8. `docs/extraction-mapping.md`
9. `git log --oneline -10`／`git status` で到達点確認

### 1.1 Python 実行時の必須事項（venv 経由起動、毎セッション要確認）

`tools/api_providers/run_role.py` 経由の 7 モデル評価や `tools/experiments/_experiment_n_model.py` 等を実行する際は **必ず venv の Python を直接指定** する：

```
zsh -c 'source ~/.zshrc && /Users/Daily/Development/ReviewCompass/.venv/bin/python3 <script.py>'
```

**避けるべき形**：`python3 <script.py>`（環境変数干渉あり、PyYAML なし）／ `zsh -c 'source ~/.zshrc && python3 <script.py>'`（API キーは取れるが PyYAML なし）。理由：`subprocess.run([sys.executable, ...])` が venv 内パッケージを参照するには、起動時の Python が venv のものでなければならない。

## 2. ワークフロー上の現在位置（セッション 37 末）

実態は **spec.json の workflow_state から確認**（§0.1）：

- intent 層／feature-partitioning 層／requirements 段／design 段：全 7 機能で全段 true
- **tasks 段**：
  - foundation／runtime／evaluation／analysis：drafting＋triad-review=true（機能内対処完了）
  - **workflow-management**：drafting=true、triad-review=**false**（3 役レビューは実施済みだが、must-fix 対処と triad-review=true 更新は次セッション 38）
  - **残 2 機能（self-improvement／conformance-evaluation）：全 false**
- implementation 段：全段 false
- **注**：全 7 機能の spec.json で `reopened` を 6 フェーズ（intent／feature-partitioning を追加）に拡張済み（セッション 37、再オープン手続き定義に伴う）

## 3. 次の作業候補

セッション 37 末で workflow-management tasks.drafting 完了、3 役 triad-review 実施、A-001 対処の前提として再オープン手続きを定義・記録。次セッション 38 は **workflow-management tasks の triad-review の続き** から再開。

### 3.0 セッション 38 起点の具体作業（workflow-management tasks の triad-review 続き）

3 役レビューの結果（次の §4 に詳細）を踏まえ、次の順で進める：

1. **A-001／A-003 の再オープン処理**（確定した 4 まとまり手続き＝計画書 §5.6.1 ／ REOPEN_PROCEDURE.md を**実地で初めて使う**）：
   - A-001（遡及）：tasks.md T-003／T-007 の「reopen-procedure.yaml の 10 ステップ静的列挙」という記述を「4 まとまり構成の段集合」に修正（design.md は §reopen 機械強制モデル §5 で対処済み）
   - A-003（遡及、A-018 同根）：requirements.md 行 32 の旧 foundation 語彙 4 件（run_status／validator_status／human_signoff_status／evidence_class）を現行 foundation 正本に修正し、tasks.md 行 27 の 7 件記述と整合
   - **注意**：これは再オープン手続きの初運用。4 まとまりの停止点（まとまり 1 のフラグ差し戻し承認、各コミット、各 approval）を実地で試す。運用してみて手続きに不具合があれば §5.6.1 を見直す（暫定版のため）
2. **残りの must-fix 7 件の対処**（F-006／F-008／F-009／F-012／F-015＝機能内対処、A-002＝波及、A-004＝機能内対処）：規律 must-fix-discussion-obligation に従い 1 件ずつ利用者と議論
3. **7 モデル比較実験 1 回目**（§3.1 の標準手順、must-fix＋should-fix を topic に。事前に API キー確認＋ Opus 4.7 起草者判断の一括生成、§0.4 実験意識）
4. **統合レビュー記録の作成**：`.reviewcompass/specs/workflow-management/reviews/2026-05-NN-tasks-triad-review.md`（セッション 37 の 3 役レビュー結果を記録。生ログは `~/.claude/projects/.../<セッション 37 の ID>/subagents/` に残存、復元可能）
5. **A-002（波及）を pending-cross-feature-findings.md に追記**
6. **tasks.md／design.md 反映**、grep で機械的照合
7. **spec.json の tasks.triad-review=true 更新**（明示承認＋ workflow-precheck）
8. **コミット → push**（明示承認）

その後、依存マップ順で **self-improvement → conformance-evaluation の tasks 段**。

### 3.1 各機能の標準進め方（analysis tasks で確立した手順、踏襲）

各機能で次の流れ：

1. **tasks.drafting**：foundation／runtime／evaluation／analysis の方針を継承、要件追跡表を Req 受入単位 × 担当タスク単位で構成、DVT 必要なら登録
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

- **analysis 完全一致 15 件の人本人判定の遡及保存**：`tools/experiments/results/topic-{54〜75}-human.yaml` のうち、セッション 36 で未保存の 15 件分（topic-54 F-015、topic-55 F-008、topic-56 A-006、topic-60 A-003、topic-62 F-011、topic-63 A-004、topic-64 F-001、topic-65 F-003、topic-66 F-005、topic-68 F-010、topic-69 F-012、topic-70 F-016、topic-72 A-009、topic-73 A-010、topic-74 A-011）
- **集計表の更新と実験ノート §5 への追記**：両軸 2 表構成を実験ノート §5 第 3 回ケース（analysis tasks）として追記、§6 観点別考察に起草者バイアス検出の重要観察を追加
- **§5.12 改訂の準備**：全機能 tasks 段完了後の機能横断段で §5.12.11 アサイン権限の具体設計と §5.23.13.3 末尾「残り 27 件」（セッション 34 のアドホック変更 23 件 ＋ セッション 35 縦整合チェック 4 件）の統合的取り込み

### 3.3 全機能 tasks 段完了後の機能横断段（review-wave）

- **7 モデル評価 2 回目**：同根問題と機能横断波及（A-017 ／ A-018 ／ F-013 ／ A-005 ／ §5.23.13.3 残り 27 件）の一括評価
- **DVT 解除**：evaluation DVT-001 ／ analysis DVT-A001 ／ DVT-A002 ／ DVT-A003（残 3 機能で追加 DVT が出る可能性）
- **§5.12 改訂統合**：§5.12.11 アサイン権限新設、計画書 §5.9.6 ／ §5.9.7 ／ §5.12 への正本化（実験ノート §3.4 マルチターンプロトコルも統合）

---

## 4. 直近の確定事項

- **セッション 37（2026-05-28）の総括と 3 役レビュー結果**：(1) workflow-management tasks.drafting 完了（T-001〜T-011、コミット `626c4e2`）。(2) workflow-management tasks の 3 役 triad-review 実施（配置：主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7）。**3 役レビュー結果**：主役 20 件（CRITICAL 1／ERROR 6／WARN 13）、敵対役独立発見 10 件（CRITICAL 1／ERROR 3／WARN 4／INFO 2）、判定役 must-fix 9 件・should-fix 17 件・leave-as-is 4 件。**must-fix 9 件**＝F-006（T-007 前提に T-005 欠落、reopen 解決器が front-matter 検査を呼べない）／F-008（T-010 前提「T-003 または別途…」の曖昧表記）／F-009（T-005 完了条件 3 が人手判断で機械判定不可）／F-012（T-010 の git mv 外部依存テストが未記述）／F-015（T-003 の completion_predicate 値域 7 値検証が完了条件に未明示）／A-001（reopen 10 ステップが design 未定義、**遡及**）／A-002（T-010 の approved_update schema が self-improvement §8.4 正本と不一致、**波及**）／A-003（requirements 行 32 旧語彙 4 件 vs tasks 行 27 の 7 件、**遡及**、A-018 同根）／A-004（actor 値域に proxy_model 欠落、機能内）。波及種別：機能内対処 23／波及 1／遡及 2。(3) A-001 対処の前提として再オープン手続きを定義・正式記録（4 まとまり構成、暫定版、コミット `9ffe221`。詳細はヘッダ）。(4) 許可設定改善（settings.local.json に Task／Agent ＋ defaultMode auto）、A-017／A-018 の WARN 承知続行方針を確定。**3 役レビューの生ログは今セッション（ID `3e297d96`）の `subagents/` に残存、復元可能**。統合レビュー記録は次セッション 38 で作成予定。**push 未実施**（origin より 2 コミット先行）
- **セッション 36（2026-05-28）の総括**：(1) analysis tasks の triad-review 機能内対処 23 件すべて完了（完全一致 15 件＋割れ 5 件＋分散 3 件、tasks.md 33 マーカー＋design.md 4 マーカー反映、コミット `e4b0258` ／ `5cc030d`）。(2) 7 モデル比較実験 1 回目（analysis）を実施、161 件 ＋ マルチターン続行 15 件 final ＋ 人本人判定 8 件保存（コミット `7b6aec8` ／ `170cc18` ／ `f726239` ／ `4cbd526`）。(3) マルチターン対話プロトコルとプロンプト設計の規律確立、実験ノート §3.4 新設＋計画書 §5.9.6 軽量相互参照（コミット `2c22155`）。(4) 規律 avoid-compound-bash 軽量移送（コミット `5a8308e`）。(5) セッション 35 ログ変換（コミット `de635fc`）。(6) `.codex/` を `.gitignore` に追加（コミット `a36f28c`）。(7) analysis 3 役 triad-review 統合レビュー記録起草＋ A-018 pending 追記（コミット `328491e`）。コミット 11 件すべて push 済み。**重要な観察**：F-007 ／ F-002 で起草者バイアスを構造的に検出（私 Opus 4.7 のみが孤立判断、他 6 モデルすべて／5 モデルが反対方向）、§6 観点別考察への重要観察
- セッション 25〜35 の確定事項は [docs/archive/todo/TODO_NEXT_SESSION-2026-05-28-snapshot.md](docs/archive/todo/TODO_NEXT_SESSION-2026-05-28-snapshot.md) に退避
- セッション 22〜24 以前：[docs/archive/todo/](docs/archive/todo/) 配下の過去 snapshot

## 5. 関連参照

- 計画書：`docs/plan/reconstruction-plan-2026-05-21.md`（§5.9.6 マルチターンプロトコル相互参照はセッション 36 追記、§5.23.13 軽量手続き許容はセッション 34 新設）
- 運営ガイド：`docs/operations/SESSION_WORKFLOW_GUIDE.md`
- 雛形：`templates/`（todo、specs、review 配下）
- 持ち越し所見：`.reviewcompass/pending-cross-feature-findings.md`（A-017 ／ A-018 の 2 件未消化、機能横断段で消化予定）
- 抽出進捗：`docs/extraction-mapping.md`
- 7 モデル比較実験ノート：`docs/experiments/n-model-comparison.md`（§2 共通フレームワーク、§3.4 マルチターンプロトコルとプロンプト設計の規律（セッション 36 新設）、§6 観点別考察）
- 規律ファイル本体：`docs/disciplines/`（一覧は同ディレクトリ README.md、avoid-compound-bash は active 必読 13 件目）
- 過去 TODO snapshot：`docs/archive/todo/` 配下

セッション終了時の自動記録：`python3 tools/session-log-converter.py --latest ~/.claude/projects/-Users-Daily-Development-ReviewCompass docs/sessions/session-<NN>-<YYYY-MM-DD>.md`
