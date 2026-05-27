# 次セッション継続用メモ

最終更新：2026-05-27（セッション 34 末。アドホック変更整合性確保レビュー完了：重要 8 件を計画書 ／ 仕様文書側に反映、コミット 9 件全 push 済み。残り 23 件は §5.12 改訂時統合と判断、3 重リマインダで予約。TODO スリム化完了。次セッション 35 は analysis tasks 段着手または同根問題議論から再開。詳細は git log）
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

## 1. 起動手順（セッション 35 開始時）

1. `cd /Users/Daily/Development/ReviewCompass`
2. 本 `TODO_NEXT_SESSION.md` を読む（§0 規律確認）
3. **規律本体 active 必読を Read**（一覧は `docs/disciplines/README.md`、auto memory は索引のみ load のため毎セッション必要）
4. `docs/operations/SESSION_WORKFLOW_GUIDE.md`
5. 計画書 `docs/plan/reconstruction-plan-2026-05-21.md` §5.4〜§5.8 ／ §5.12 ／ §5.23 ／ §5.23.12 ／ §5.23.13（軽量手続き許容、セッション 34 新設）／ §5.24（spec.json 正本スキーマ）
6. `.reviewcompass/pending-cross-feature-findings.md`（A-017 1 件未消化）
7. `docs/extraction-mapping.md`
8. `git log --oneline -10`／`git status` で到達点確認

## 2. ワークフロー上の現在位置（セッション 34 末）

実態は **spec.json の workflow_state から確認**（§0.1）：

- intent 層／feature-partitioning 層／requirements 段／design 段：全 7 機能で全段 true
- **tasks 段**：foundation／runtime／evaluation は drafting＋triad-review=true（機能内対処完了）、残 4 機能（analysis／workflow-management／self-improvement／conformance-evaluation）は全 false
- implementation 段：全段 false

## 3. 次の作業候補

セッション 33 末で foundation／runtime／evaluation の tasks 段機能内対処完了、セッション 34 でアドホック変更整合性確保レビュー完了。次セッション 35 は依存マップ順 4/7 の analysis 機能から再開：

1. **同根問題のワークフロー修正議論**（最優先）：セッション 33 で利用者提起「全フィーチャーの triad-review を 7 モデル評価したところで、同根の問題をまとめて考える必要性」。観察された同根の実例と利用者の構造的解決の苦悩（「(A)＋(C) は過去にも効果なし」「ワークフロー遵守のコスト大」）は git log のセッション 33 コミット参照
2. **analysis の tasks 段着手**（依存マップ順 4/7）：foundation／runtime／evaluation の方針（一気通貫粒度、責務領域単位、要件追跡表、テスト戦略継承、DVT 等）を踏襲、tasks.drafting → triad-review → 7 モデル比較実験 → 利用者判定 → 機能内対処。同根問題への配慮として上記 1 の方針確定を先行するか、暫定で過去判定 grep を加えるかを利用者と相談
3. **残 3 機能の tasks 段**（5/7〜7/7）：workflow-management → self-improvement → conformance-evaluation
4. **全機能 tasks 段完了後**：機能横断段（tasks review-wave、A-017 一括対処）／DVT 解除（evaluation DVT-001）／design 軽量再オープン（F-001、F-015 関連）／§5.12 改訂（§5.12.11 アサイン権限新設、case B 路線）

**§5.12 改訂時の必須参照**：§5.12.11 起草時に計画書 §5.23.13.3 末尾「セッション 34 整合性確保レビューの結果」の **残り 23 件** もあわせて統合的に取り込む（多重リマインダ：§5.23.13.3 末尾／§5.12.10 末尾／本 TODO §3）。利用者明示承認「案 W」（セッション 34）

---

## 4. 直近の確定事項

- **セッション 34（2026-05-27）の総括**：アドホック変更整合性確保レビュー実施、agent 経由で 47 項目時系列調査、重要 8 件を計画書／仕様文書側に反映完了（コミット範囲 `24e9fb8`〜`f398260` の 9 件、git log 参照）。残り 23 件は §5.12 改訂時統合と判断、3 重リマインダで予約。TODO スリム化完了（198 行 → 約 80 行、§0.4／§0.5／§1.5 を実効性低として削除）
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
