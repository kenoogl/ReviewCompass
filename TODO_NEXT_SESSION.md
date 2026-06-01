# 次セッション継続用メモ

最終更新：2026-06-02（セッション46）。**次の作業：再オープン第3過程（requirements→design→tasks→implementation の alignment/approval 連鎖再実施）→ 完了後に runtime 機能の implementation（drafting → triad-review）**。セッション46 で triad-review 3役モデルを独立3社（Opus/GPT/Gemini）に変更確定し、review_mode 語彙正本に api_mediated を追加する R 種別再オープンの第1・第2過程を完了（コミット `5378c6d`）。第3過程が残っている。

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
3. **規律本体 active 必読を Read**（auto memory は索引のみ load のため毎セッション必要。以下 14 件を個別に Read すること。README を読むだけでは不十分）
   - `docs/disciplines/discipline_must_fix_discussion_obligation.md`
   - `docs/disciplines/discipline_intent_conformance_is_the_acceptance_gate.md`
   - `docs/disciplines/discipline_standing_directives_are_hard_constraints.md`
   - `docs/disciplines/discipline_workflow_precheck_invocation.md`
   - `docs/disciplines/discipline_approval_operation.md`
   - `docs/disciplines/discipline_facts_vs_interpretation.md`
   - `docs/disciplines/discipline_pre_action_precheck.md`
   - `docs/disciplines/discipline_workflow_state_truth_source.md`
   - `docs/disciplines/discipline_concise_complete_report.md`
   - `docs/disciplines/discipline_reopen_procedure_for_settled_topics.md`
   - `docs/disciplines/discipline_plain_japanese.md`
   - `docs/disciplines/discipline_options_presentation.md`
   - `docs/disciplines/discipline_avoid_compound_bash.md`
   - `docs/disciplines/discipline_post_write_verification.md`
4. `docs/operations/SESSION_WORKFLOW_GUIDE.md` と `docs/operations/REOPEN_PROCEDURE.md`（再オープン手続きの 4 過程）
5. 計画書 `docs/plan/reconstruction-plan-2026-05-21.md`（全 4032 行）の以下の節（行番号は計画書編集で変わる可能性あり、参考値）：§5.4（273行〜）・§5.5（310行〜）・§5.6（455行〜）・§5.7（650行〜）・§5.8（698行〜）・§5.9.6（1009行〜）・§5.12（1622行〜）・§5.23（3370行〜）・§5.23.12（3587行〜）・§5.23.13（3648行〜）・§5.24（3718行〜）
6. **実験ノート `docs/experiments/n-model-comparison.md` §3.4**（マルチターンプロトコルとプロンプト設計の規律）
7. `git log --oneline -10`／`git status` で到達点確認

### 1.1 Python 実行時の必須事項（venv 経由起動、毎セッション要確認）

`tools/experiments/_experiment_n_model.py` 等を実行する際は **必ず venv の Python を直接指定** する：

```
zsh -c 'source ~/.zshrc && /Users/Daily/Development/ReviewCompass/.venv/bin/python3 <script.py>'
```

**避けるべき形**：`python3 <script.py>`（環境変数干渉あり、PyYAML なし）／ `zsh -c 'source ~/.zshrc && python3 <script.py>'`（API キーは取れるが PyYAML なし）。理由：`subprocess.run([sys.executable, ...])` が venv 内パッケージを参照するには起動時の Python が venv のものでなければならない。

## 2. ワークフロー上の現在位置（セッション 46 末）

実態は **spec.json の workflow_state から確認**（§0.1）：

- intent 層／feature-partitioning 層：全 7 機能で全段 true
- **requirements 段／design 段／tasks 段（foundation）：drafting・triad-review・review-wave＝true、alignment・approval＝false（reopen 中、api_mediated 追加の R 種別再オープン第3過程待ち）**
- requirements 段／design 段／tasks 段（他 6 機能）：全段 true
- **implementation 段（foundation）：drafting＝true／triad-review＝true／review-wave・alignment・approval＝false**
- **implementation 段（他 6 機能）：全段 false（runtime が次）**
- **recheck**：upstream_change_pending=true、impacted=["design","tasks","implementation"]（第3過程完了でクリア）
- **注（再オープン履歴）**：再承認済み＝workflow-management requirements/design（A-2）／self-improvement requirements/design（A-2）／conformance-evaluation design（A-1）／foundation design（A-1、A-018）／evaluation design（A-1）。進行中＝foundation review_mode api_mediated 追加（R 種別、セッション46、第3過程残り）

## 3. 次の作業（セッション 46 起点）

**次の作業：§3.0 再オープン第3過程 → §3.1 runtime 機能 implementation**

### 3.0 再オープン第3過程（優先）

foundation の review_mode 語彙正本に api_mediated を追加した R 種別再オープンの第3過程が残っている。依存順（requirements → design → tasks → implementation）に alignment と approval を連鎖再実施する。各 approval は代役（複数モデル集約）に委ねる。引き金は本人（spec.json true 化）。

- 進行中状態：recheck.upstream_change_pending=true、impacted=["design","tasks","implementation"]
- 完了条件：requirements/design/tasks/implementation の alignment・approval が true、recheck クリア（upstream_change_pending=false、impacted=[]）
- 第3過程完了後にコミット（本人承認）

### 3.1 runtime 機能の implementation 着手

第3過程完了後、依存順で次は **runtime**。各機能の implementation を drafting → triad-review まで進め、review-wave 以降は全機能の triad-review 完了後に機能横断で実施する（運営ガイド §2.3）。

**進め方（案1：機能ごとにセッション分割、セッション45利用者決定「区切る」）**：

1. 1 セッションで 1〜2 機能を「実装（drafting）→ 3 役レビュー（triad-review）→ 所見対処」まで進める
2. 状態の真実源は spec.json の `workflow_state`。セッションをまたいでも spec.json を読めば再開できる（計画書 §5.7／§5.24）
3. 残り順序：runtime → evaluation → analysis → workflow-management → self-improvement → conformance-evaluation
4. **workflow-management** は §5.12 改訂で確定した論点（cross-spec-alignment 段集合・§5.12.11 アサイン権限・DVT-W003 規律変更段集合）を実装する側のため、他機能の後に着手するのが安全

**実装で確立した手順（runtime 以降も踏襲）**：

- TDD（テスト先行で赤を確認 → 実装で緑）。コミットは依存グループ単位＋テスト/実装の 2 段（CLAUDE.md 優先）
- 実装レビュー観点は 5 点（タスク文書整合・要件追跡・テスト網羅性・配置命名規約・機能横断波及）。暫定のため過不足が判明したら暫定改訂可。本体は [docs/notes/2026-06-01-implementation-phase-approach.md](docs/notes/2026-06-01-implementation-phase-approach.md)
- **triad-review は独立 API 経由 3 役（主役 `claude-opus-4-8` ／ 敵対役 `gpt-5.5` ／ 判定役 `gemini-3.1-pro-preview`）**（セッション46確定、agent ツールは Claude のみのため API スクリプト経由で実施、mode 値 `api_mediated`）。GPT-5.5 は `--timeout-seconds 300` を必ず指定
- **所見の調停（must-fix 含む）は LLM が行う**（セッション46確定）。上位判断（規律変更・大方針転換・遡及）は本人留保
- **書き込み後検証**：docs/ 配下等の正本文書を更新したら独立系統（OpenAI／Google）で検証。API スクリプト（`tools/api_providers/`）経由で実施
- 各段完了で spec.json を true 化（不可逆操作・本人承認）

### 3.2 セッション46 の完了内容

- triad-review 3役モデルを独立3社へ変更確定（主役 Opus 4.8／敵対役 GPT-5.5／判定役 Gemini-3.1-pro、runtime 以降適用）
- 実装自律の範囲確定（所見調停は LLM、上位判断は本人留保、チェックポイントは本人）
- review_mode 語彙正本に api_mediated 追加（R 種別再オープン第1・第2過程完了、コミット `5378c6d`）
- `_experiment_n_model.py` に `--timeout-seconds` 引数追加（GPT-5.5 タイムアウトの根本対処）
- セッション記録 [docs/sessions/session-46-2026-06-02.md](docs/sessions/session-46-2026-06-02.md)

### 3.3 foundation implementation の完了内容（セッション45）

- drafting：全 10 タスク（T-001〜T-010）を TDD で実装。テスト緑 120 件、完成判定スクリプト 6 項目 pass
- triad-review：3 役レビューで 12 所見（must-fix 1・should-fix 5・leave-as-is 6）を検出・対処。レビュー記録 `.reviewcompass/specs/foundation/reviews/2026-06-01-implementation-triad-review.md`
- コミット 15 件（`3764055`〜`f9190bb`）＋セッション記録 `7c12a79`。セッション記録 [docs/sessions/session-45-2026-06-01.md](docs/sessions/session-45-2026-06-01.md)
- 新規依存：`jsonschema`（meta-schema 検証用、pyproject.toml に追加）

### 3.3 完了済み（セッション 41〜44）

- セッション 41〜42 の完了済み項目（§5.12 改訂全7項目・規律新設等）：git 履歴（`fce0061`／`a66da5c`／`ce2ba60`／`7417585`／`7684402`／`fa089c0`）と `docs/archive/todo/` 参照
- **書き込み後検証の収束基準を新設・動作仕様ファイルへ移設（セッション 43）**：コミット `59a0a6c`
- **§3.6 規律の計画書参照デプロイ問題を対処完了（セッション 44）**：コミット `4c50e4b`

### 3.4 残作業の補完項目（任意・低優先）

- **analysis 完全一致 15 件の人本人判定の遡及保存**：`topic-{54〜75}-human.yaml` のうちセッション 36 で未保存の 15 件分（詳細は git log のセッション 36 記録）
- **実験ノート §5／§6 への追記**：両軸 2 表構成を §5 のケースに、§6 観点別考察に起草者バイアス検出の観察を追加

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

セッション終了時の自動記録：`python3 tools/session-log-converter.py --latest ~/.claude/projects/-Users-Daily-Development-ReviewCompass docs/sessions/session-46-<YYYY-MM-DD>.md`
