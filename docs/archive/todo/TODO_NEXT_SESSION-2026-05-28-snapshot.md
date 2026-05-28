# 次セッション継続用メモ

最終更新：2026-05-28（セッション 35 末。本セッションでの主な達成：(1) 縦整合チェック実施（全 7 機能の要件 → 設計（→ タスク）、軽微な不整合 4 件発見、§5.12 改訂時に統合的に対処、多重リマインダ 23→27 件同期更新、コミット 0cc2aa4）。(2) analysis tasks.drafting 完了（T-001〜T-011 の 11 タスク 257 行、DVT 2 件登録、コミット c742eac）。(3) analysis tasks の 3 役 triad-review 完了（主役 Sonnet 4.6 16 件＋敵対役 Opus 4.7 独立 12 件＋判定役 Opus 4.7 統合判定、must-fix 13／should-fix 12／leave-as-is 3、波及 2 件は機能横断段持ち越し）。(4) 7 モデル評価を 2 回方式に再オープン訂正（4 文書 6 箇所同期、コミット d259f3a）：1 回目＝機能ごとの triad-review 段で機能内対処、2 回目＝機能横断段で同根問題集約。コミット 3 件全 push 済み。次セッション 36 は analysis triad-review の 7 モデル評価（1 回目）と機能内対処から再開。詳細は git log）
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

- spec.json の `workflow_state.<フェーズ>.approval` を true に変更／フェーズ移行
- git commit／git push
- 計画書の方針変更／大規模な再設計（複数機能にまたがる責務分担変更等）

承認の判定基準：「承認」「OK」「採用」「進めて」「はい」等の明示的肯定発言、または AskUserQuestion 等での明示選択のみ。議論継続・停止・方法論指示・沈黙は承認とみなさない。

### 0.3 起草者と判定者の分離（計画書 §5.4）

drafting 段は actor=human または llm（草案作成のみ）、triad-review 段は actor=llm（主役・敵対役・判定役の 3 役、サブエージェント方式 §5.23.12）。**同一の actor が起草と判定を兼ねない**。レビュー記録 front-matter に `author.identity` と `reviewer.identity` を異名必須記載、機械検査対象。

<!-- TEMPLATE_HEADER_END -->

---

## 1. 起動手順（セッション 36 開始時）

1. `cd /Users/Daily/Development/ReviewCompass`
2. 本 `TODO_NEXT_SESSION.md` を読む（§0 規律確認）
3. **規律本体 active 必読を Read**（一覧は `docs/disciplines/README.md`、auto memory は索引のみ load のため毎セッション必要）
4. `docs/operations/SESSION_WORKFLOW_GUIDE.md`
5. 計画書 `docs/plan/reconstruction-plan-2026-05-21.md` §5.4〜§5.8 ／ §5.12 ／ §5.23 ／ §5.23.12 ／ §5.23.13（軽量手続き許容、セッション 34 新設）／ §5.24（spec.json 正本スキーマ）
6. `.reviewcompass/pending-cross-feature-findings.md`（A-017 1 件未消化）
7. `docs/extraction-mapping.md`
8. `git log --oneline -10`／`git status` で到達点確認

### 1.1 Python 実行時の必須事項（venv 経由起動、毎セッション要確認）

ReviewCompass の Python スクリプト（特に `tools/api_providers/run_role.py` 経由の 7 モデル評価、`tools/experiments/_experiment_n_model.py` 等）を実行する際は **必ず venv の Python を直接指定** すること。理由：

- `subprocess.run([sys.executable, ...])` が venv 内パッケージ（PyYAML 等）を参照するには、起動時の Python が `/Users/Daily/Development/ReviewCompass/.venv/bin/python3` でなければならない
- `zsh -c 'source ~/.zshrc && python3 ...'` だけでは `python3` がシステム Python に解決され `ModuleNotFoundError: No module named 'yaml'` で全件 returncode=1 失敗となる（2026-05-28 セッション 36 で発生、115 件即時失敗）
- API キー取得（`ANTHROPIC_API_KEY` ／ `GEMINI_API_KEY` の Claude Code 干渉回避）は別途必要（実験ノート §3.1 案 A）

**正しい起動コマンド**：

```
zsh -c 'source ~/.zshrc && /Users/Daily/Development/ReviewCompass/.venv/bin/python3 <script.py>'
```

**避けるべき形**：

- `python3 <script.py>`（環境変数干渉あり、PyYAML なし）
- `zsh -c 'source ~/.zshrc && python3 <script.py>'`（API キーは取れるが PyYAML なし）

**注記**：本項目は毎セッション同じミスを繰り返してきたため起動手順に明記。

## 2. ワークフロー上の現在位置（セッション 35 末）

実態は **spec.json の workflow_state から確認**（§0.1）：

- intent 層／feature-partitioning 層／requirements 段／design 段：全 7 機能で全段 true
- **tasks 段**：
  - foundation／runtime／evaluation：drafting＋triad-review=true（機能内対処完了）
  - **analysis：drafting=true（セッション 35 で起草完了 c742eac）、triad-review=false（3 役レビュー完了済みだが機能内対処未完了、7 モデル評価 1 回目から再開）**
  - 残 3 機能（workflow-management／self-improvement／conformance-evaluation）：全 false
- implementation 段：全段 false

## 3. 次の作業候補

セッション 35 末で analysis tasks.drafting 完了（c742eac）と 3 役 triad-review 完了（未コミット）。次セッション 36 は **analysis triad-review の続き（7 モデル評価 1 回目 → 機能内対処）から再開**：

1. **analysis triad-review の機能内対処**（最優先、本セッション 35 で 3 役レビュー完了済み）：
   - **統合レビュー記録の起草**：`.reviewcompass/specs/analysis/reviews/2026-05-28-tasks-triad-review.md` に front-matter ＋ 主役 16 件 ＋ 敵対役 12 件 ＋ counter_status ＋ 判定役判定を統合（過去 foundation/runtime/evaluation の tasks-triad-review レビュー記録と同型）
   - **7 モデル評価の 1 回目実施**（セッション 35 で確定した 2 回方式、コミット d259f3a）：機能内 must-fix 13 件＋should-fix 12 件＝25 topic を 7 モデル評価（5 API モデル＋Sonnet 4.6 CLI＋Opus 4.7 既出推奨流用＝175 件）。実験ノート `docs/experiments/n-model-comparison.md` §2 共通フレームワーク／§4 のパターン踏襲
   - **利用者議論と機能内対処**：規律 [must-fix-discussion-obligation] に従い 1 件ずつ平易な日本語で対処方針提案、合意後に tasks.md 修正
   - **機能横断波及（F-013 ／ A-005）を pending に持ち越し**：foundation 語彙正本件数の同根問題、機能横断段で 2 回目評価
   - **DVT 2 件登録済み**：DVT-A001（workflow-management 接合面）／DVT-A002（mixed_review_mode 過渡的対処）、T-011 完了条件でゲート化
   - spec.json の `tasks.triad-review=true` 更新（利用者明示承認必要）→ コミット → push
2. **残 3 機能の tasks 段**（5/7〜7/7）：workflow-management → self-improvement → conformance-evaluation。各機能で tasks.drafting → triad-review → 7 モデル評価 1 回目 → 機能内対処（**2 回方式** の 1 回目を機能ごとに実施、コミット d259f3a で確定）
3. **全機能 tasks 段完了後**：機能横断段（tasks review-wave）で **7 モデル評価 2 回目**（同根問題と機能横断波及）／同根問題集約／A-017／F-013／A-005 一括対処／DVT 解除（evaluation DVT-001／analysis DVT-A001／DVT-A002）／design 軽量再オープン（F-001、F-015 関連）／§5.12 改訂（§5.12.11 アサイン権限新設、case B 路線）

**§5.12 改訂時の必須参照**：§5.12.11 起草時に計画書 §5.23.13.3 末尾「セッション 34 整合性確保レビューの結果」の **残り 27 件**（セッション 34 のアドホック変更レビュー由来 23 件 ＋ セッション 35 縦整合チェック追加発見 4 件、影響度低の未反映 ／ 部分反映項目 ／ 軽量再オープン下流波及漏れ）もあわせて統合的に取り込む（多重リマインダ：§5.23.13.3 末尾／§5.12.10 末尾／本 TODO §3）。利用者明示承認「案 W」（セッション 34）／「案 ア、ただし、コミットまで。その後、案イへ」「多重リマインダ 3 箇所すべて同期更新」（セッション 35）

---

## 4. 直近の確定事項

- **セッション 35（2026-05-28）の総括**：
  - (1) 縦整合チェック実施（全 7 機能の要件 → 設計（→ タスク）、軽微な不整合 4 件発見＝workflow-management Req 1 受入 6 が対応表に欠落 ／ analysis に旧表現「12 criteria／12 基準」残存 3 件、§5.12 改訂時統合と判断、多重リマインダ 23→27 件同期更新、コミット `0cc2aa4`）
  - (2) analysis tasks.drafting 完了（T-001〜T-011 の 11 タスク 257 行、要件追跡表 Req 1〜8 並列対応、DVT 2 件登録 DVT-A001／DVT-A002、コミット `c742eac`）
  - (3) analysis tasks の 3 役 triad-review 完了（主役 Sonnet 4.6 16 件 ＋ 敵対役 Opus 4.7 独立 12 件 ＋ 判定役 Opus 4.7 統合判定、合計 28 件、must-fix 13／should-fix 12／leave-as-is 3、機能横断波及 2 件＝F-013／A-005 は同根問題として機能横断段持ち越し）。**統合レビュー記録の起草と機能内対処は次セッション 36 へ持ち越し**
  - (4) 7 モデル評価を **2 回方式** に再オープン訂正（4 文書 6 箇所同期、コミット `d259f3a`）：1 回目＝機能ごとの triad-review 段で機能内対処、2 回目＝機能横断段で同根問題集約。セッション 34 (Q2) 採用反映が狭すぎた点を訂正
  - コミット 3 件（`0cc2aa4` ／ `c742eac` ／ `d259f3a`）すべて push 済み
- **セッション 34（2026-05-27〜28）の総括**：(1) アドホック変更整合性確保レビュー（47 項目調査、重要 8 件反映、残り 23 件は §5.12 改訂時統合と判断、3 重リマインダで予約）。(2) 計画書 §5.23.13 軽量手続き許容節を新設（6 サブ節、本 dogfooding をトライアル位置付け）。(3) TODO スリム化（198 → 約 90 行、§0.4 ／ §0.5 ／ §1.5 撤廃）。(4) 同根問題のワークフロー修正（(Q2)/(ニ) 採用）を 4 段階で反映：計画書 §5.5 ／ §5.9.6 ／ §5.9.7.1 ／ 運営ガイド §2.2 ／ workflow-management 要件 Req 1 受入 6 ／ 同設計 §3。コミット範囲 `24e9fb8`〜`1c18634` の 14 件、すべて push 済み
- セッション 25〜33 の確定事項は [docs/archive/todo/TODO_NEXT_SESSION-2026-05-27-snapshot.md](docs/archive/todo/TODO_NEXT_SESSION-2026-05-27-snapshot.md) に退避
- セッション 22〜24 以前：[docs/archive/todo/](docs/archive/todo/) 配下の 2026-05-24 ／ 2026-05-25 snapshot

## 5. 関連参照

- 計画書：`docs/plan/reconstruction-plan-2026-05-21.md`（§5.23.13 軽量手続き許容はセッション 34 新設）
- 運営ガイド：`docs/operations/SESSION_WORKFLOW_GUIDE.md`
- 雛形：`templates/`（todo、specs、review 配下）
- 持ち越し所見：`.reviewcompass/pending-cross-feature-findings.md`（A-017 のみ未消化）
- 抽出進捗：`docs/extraction-mapping.md`
- 7 モデル比較実験ノート：`docs/experiments/n-model-comparison.md`（§2 共通フレームワーク、§6.9 §5.12 改訂示唆、§6.13 統計データ）
- 規律ファイル本体：`docs/disciplines/`（一覧は同ディレクトリ README.md）
- 過去 TODO snapshot：`docs/archive/todo/` 配下 3 件

セッション終了時の自動記録：`python3 tools/session-log-converter.py --latest ~/.claude/projects/-Users-Daily-Development-ReviewCompass docs/sessions/session-<NN>-<YYYY-MM-DD>.md`
