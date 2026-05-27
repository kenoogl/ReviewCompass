# 次セッション継続用メモ

最終更新：2026-05-27（セッション 31 末、7 モデル比較実験の **第 1 段階（must-fix 9 件）完了**。Gemini プロバイダー追加（TDD 5-A）、マルチターン対応 send_messages 追加（TDD 5-B）、実験用スクリプト _experiment_n_model.py 作成（TDD 5-C）、累積テスト 100 件 pass。実験ノート [docs/experiments/n-model-comparison.md](docs/experiments/n-model-comparison.md) で §2.6 12 評価観点を事前定義、§5.1 予備実験／§5.3.1 第 1 段階の結果を記録。**重要な発見**：判定モデル間で意見分岐するケースで proxy 役にアサイン権限を与える運用（論文査読システム類似）が有効、§5.12 改訂の論点として §6.9 に追跡記録。次セッションは **第 2 段階（should-fix 7 件、topic-11〜17）** から再開）
作業ディレクトリ：`/Users/Daily/Development/ReviewCompass/`（本リポジトリ）
リポジトリ：`git@github.com:kenoogl/ReviewCompass.git`（main ブランチ）

---

<!-- TEMPLATE_HEADER_START：本ヘッダは templates/todo/TODO_NEXT_SESSION.template.md から派生。本セクションは削除・短縮しないこと。 -->

## 0. ReviewCompass 利用にあたる重要規律（削除禁止）

本セクションは ReviewCompass（dual-reviewer 方式の仕様駆動レビューシステム）を使うすべてのプロジェクトに共通する重要規律。**削除・短縮しないこと**。LLM が本 TODO を読む際、毎セッション開始時に本セクションを確認し、本セクションに書かれた手順を毎作業前に守る。

### 0.1 提案前必須確認

「次の作業」「次のステップ」を利用者に提案する前に、次を機械的に確認し、応答内で明示宣言する：

1. **`workflow_state` を必ず読む**：対象機能の `.reviewcompass/specs/<機能>/spec.json` の `workflow_state` を実際に Read で読む。要約や記憶を根拠にしない。本 TODO §3 や §4 に書かれた「次の作業候補」は要約に過ぎず、正本は spec.json の `workflow_state`
2. **規律と照合する**：運営ガイド `docs/operations/SESSION_WORKFLOW_GUIDE.md` §2.3 段の進め方の規律と照合し、次に進める段か（前段の approval まで完了しているか）を確認する。とくに「approval を得てから次フェーズに進む」（運営ガイド §2.3 第 6 項）の前提を毎回照合する
3. **TODO や要約文書を信頼せず、正本と照合する**：TODO・設計メモ・要約文の記述を信頼の根拠にしない。提案前に必ず spec.json／計画書／運営ガイド／git ログの正本と照合する

### 0.2 利用者明示承認が必要な不可逆操作

次の操作は利用者の **明示承認** なしに実行しない：

- spec.json の `workflow_state.<フェーズ>.approval` を true に変更
- spec.json のフェーズ移行
- git commit／git push
- 計画書の方針変更
- フェーズ移行に伴う一括処理
- 大規模な再設計（複数機能にまたがる責務分担変更等）

承認の判定基準：「承認します」「OK」「採用」「進めて」「はい」等の明示的肯定発言、または AskUserQuestion 等での明示選択のみ。議論継続・停止・方法論指示・沈黙・命名指摘は承認とみなさない。

### 0.3 起草者と判定者の分離（計画書 §5.4 規律）

drafting 段は actor=human または llm（草案作成のみ）、triad-review 段は actor=llm（主役・敵対役・判定役の 3 役、サブエージェント方式 §5.23.12 で実施）。**同一の actor が起草と判定を兼ねない**。

レビュー記録の front-matter には `author.identity` と `reviewer.identity` を異名で必須記載し、機械検査の対象とする。

### 0.4 AskUserQuestion を多用しない（2026-05-25 セッション 24 規律統廃合に伴い memory から移動）

確認は普通の文章で簡潔に。AskUserQuestion ツールは **4 つ以上の選択肢や視覚比較が必要な局面に限定** し、2〜3 個の選択や Yes／No には使わない。

利用者発言の出典：「(イ)の導入で他の規律を代用し、減らせる可能性はあるか」（2026-05-24 セッション 22）の指摘で制定、2026-05-25 セッション 24 で memory から TODO §0.4 に移動（規律統廃合の一環、利用者明示承認「AskUserQuestion を多用しないについては、TODOの冒頭に移すと規律が減る」）。

### 0.5 TODO 更新時は常にデータ削減を考える

本 TODO に追記・更新する際は、**常にデータ削減を検討する**。具体的には：

- 既存節への新規追記は最小限の行数で行う（パス列挙や詳細手順は別文書（README／git log／archive snapshot）に外部参照させる）
- 完了済み履歴は archive snapshot または git log への参照に置き換え、本 TODO には残さない
- 詳細説明は本 TODO 外（コミットメッセージ／design.md／README）に書き、本 TODO は要点のみ
- 更新後は総行数を測定し、肥大化していれば既存節の縮小余地も同時に検討する

経緯：2026-05-25 セッション 27 で利用者指摘「TODO が肥大化しているので、対応」「TODO 更新時は常にデータ削減を考える」により制定、利用者明示承認「案 A」。

<!-- TEMPLATE_HEADER_END -->

---

## 1. 起動手順（セッション 32 開始時）

ReviewCompass の運営ガイドラインの必読フローに従う：

1. ターミナルで `cd /Users/Daily/Development/ReviewCompass`
2. 本 `TODO_NEXT_SESSION.md` を読む（§0 重要規律を必ず確認）
3. **規律本体 active 必読を Read で読む**（最新の件数と一覧は `docs/disciplines/README.md` の「active 必読」表で確認。auto memory は索引のみ load し本体は load されないため毎セッション必要）
4. `docs/operations/SESSION_WORKFLOW_GUIDE.md` を読む（必読フロー・ワークフロー段の役割・サブエージェント方式の運用条件）
5. 計画書 `docs/plan/reconstruction-plan-2026-05-21.md` §5.4〜§5.8 を読む（ワークフロー手続き、reopen、session 跨ぎ、多層防御）
6. 計画書 §5.24 を読む（spec.json の正本スキーマ、2026-05-24 セッション 22 で新設）
7. 計画書 §5.12 を読む（人間代役機構、approval 段の actor=proxy_model 連動）
8. 計画書 §5.23 と §5.23.12 を読む（dogfooding と subagent_mediated 方式）
9. `.reviewcompass/pending-cross-feature-findings.md` を読む（持ち越し所見、現在 0 件未消化、全 16 件対処済み）
10. `docs/extraction-mapping.md` を読む（進行記録）
11. `git log --oneline -10`／`git status` で到達点確認

過去の経緯（セッション 19〜22 の詳細履歴、規律違反履歴、撤回履歴、過去の確定事項一覧等）は `docs/archive/todo/TODO_NEXT_SESSION-2026-05-24-snapshot.md` を参照。

### 1.5 シンボリックリンク検証結果（2026-05-25 セッション 27、fallback 案イ採用）

検証失敗：auto memory の起動時 load は MEMORY.md 索引（1 文要約）までで、シンボリックリンク経由でも規律本体はたどられない。**対処**：active 必読は §1 起動手順で毎セッション Read（参照層は必要時参照のまま）、シンボリックリンクは単一正本（repo）維持の補助として残置。最新の件数・分類は `docs/disciplines/README.md` 参照。詳細は本セッション 27 のコミットメッセージ参照。

## 2. ワークフロー上の現在位置（2026-05-27 セッション 31 末時点）

実態は **spec.json の workflow_state から確認**（§0.1 規律）：

- **intent 層／feature-partitioning 層**：すべて true
- **requirements 段**：全 7 機能で全段 true
- **design 段**：全 7 機能で全段 true（セッション 28 末）
- **tasks 段**：foundation で drafting=true（コミット 9f1f472）、triad-review レビュー記録あり（コミット 576513b、must-fix 10 件・should-fix 7 件・leave-as-is 4 件の判定）、**機能内対処は本実験完了後に実施**（実験結果と人本人判定を踏まえる）。残 6 機能は全段 false
- **implementation 段**：全段 false
- **API 経路先取り実装（§5.9.7.1）**：TDD サイクル 4 完成＋セッション 31 で 5-A（Gemini）／5-B（マルチターン）／5-C（実験スクリプト）追加、累積 100 件 pass
- **7 モデル比較実験（人間代役機構 §5.12 検証、`docs/experiments/n-model-comparison.md`）**：予備実験 1 件＋第 1 段階 9 件（must-fix）完了、**第 2 段階 7 件（should-fix）が次セッション以降**

機能横断波及所見：A-001〜A-016 の **16 件すべて対処済み**。詳細は `.reviewcompass/pending-cross-feature-findings.md`。

規律ファイル：本体は repo の `docs/disciplines/discipline_*.md` に配置、最新の件数・分類は `docs/disciplines/README.md`。

## 3. 次の作業候補（優先順位順）

**現在の主要作業：7 モデル比較実験 第 2 段階（should-fix 7 件）→ 機能内対処 → 計画書 §5.12 改訂 → 次機能（runtime）の tasks.drafting**

セッション 31 末で第 1 段階（must-fix 9 件 × 8 者 = 72 判定）完了。次セッションは第 2 段階から再開：

1. **第 2 段階の準備**（最優先）：
   - レビュー記録 §3.1 の should-fix 7 件（F-005／F-007／F-011／A-003／A-004／A-006／A-007）について、元の主役・反論役の所見から「事実／候補案／深掘り」を新規整形（must-fix と違い §4.1 に整形済みデータがない）
   - プロンプトファイル 7 件作成（tools/experiments/prompts/topic-11〜17.txt）
   - F-011 は波及（pending-cross-feature-findings.md 対象）で対処方針が固定的、含めるが解説に注記

2. **第 2 段階の実行**：
   - 5 経路 × 7 件 = 35 回の API 呼び出し（zsh -c 経由、settings.local.json で許可済み）
   - Sonnet 4.6 CLI 7 件（Agent ツール経由）
   - 利用者本人の判定 7 件（判定支援資料 tools/experiments/judgment-aid-for-human.md を 7 件分追記して提示）
   - 質問発火時のマルチターン対話継続（案 b' 事実応答型代役）

3. **第 2 段階の集計と分析**：
   - 実験ノート §5.3.2 に結果追記
   - §6.1〜§6.12 の 12 観点で総合分析（特に観点 6 重大度別の傾向：must-fix vs should-fix の差）
   - §6.9 のアサイン権限の運用パターンを should-fix で再検証

4. **機能内対処の実施**（本実験完了後）：
   - 利用者本人の判定が確定した方針で tasks.md を修正（must-fix 10 件＋必要な should-fix）
   - spec.json の foundation/tasks.triad-review を true に更新
   - 規律 [[workflow-precheck-invocation]] で `tools/check-workflow-action.py spec-set foundation tasks triad-review true` 経由

5. **計画書 §5.12 改訂手続き**（本実験完了後、利用者明示承認 §0.2 必須、軽量手続き）：
   - §5.12.4 の権限範囲に「アサイン可能カテゴリ」を追加（3 分類化）
   - §5.12.5 記録上の区別の拡張（actor_chain フィールド）
   - §5.12.7 エスカレーション条件の見直し
   - §5.12.11 新節としてアサイン権限の具体設計を起草

6. **機能横断波及（F-011）**：pending-cross-feature-findings.md に A-017 として追記（tasks 段 review-wave で全機能の tasks.md に対して一括対処）

7. **次機能（runtime）の tasks.drafting**：依存マップ順 2/7、foundation の一気通貫粒度方針を踏襲

7 モデル比較実験の構造（参考）：
- 比較対象：Opus 4.7（既出推奨）／Sonnet 4.6 CLI／Sonnet 4.6 API／GPT-5.5／GPT-5.4／Gemini-3.5-flash／Gemini-3.1-pro-preview／人本人 の **8 者**
- 12 評価観点を事前定義（§2.6）：判断収束性／信頼度妥当性／質問能力／経路差／モデル間差／重大度別／出力形式／case_scores 表現力／§5.12 示唆／rationale 質的分析／assumed_context 差異／comment_to_human 質
- 案 b'（事実応答型代役）でマルチターン対話、推奨案は人本人のみ閲覧（判定者には非開示）

計画書 §5.5 phase_order の補正課題（セッション 26 で認識）：行 376〜383 の phase_order 構造例には self-improvement が記載漏れで 6 機能のみ列挙されているが、§3.1／§5.16 に基づき本設計では 7 機能を採用済み。計画書側の補正は別途追跡。

---

## 4. 直近の確定事項

利用者明示承認のあった項目を新しい順に記録（詳細は pending-cross-feature-findings.md ／ docs/disciplines/README.md ／ git log で追える）：

- **セッション 31（2026-05-27）の総括**：(1) 7 モデル比較実験（人間代役機構 §5.12 検証）の基盤整備＋第 1 段階完了。コミット cfb5db9（実験ノート初版）／5084746＋1e21138（TDD 5-A：GeminiProvider）／197940b＋60f9de4（TDD 5-B：マルチターン send_messages）／e34c4f5＋ad93688（TDD 5-C：_experiment_n_model.py）／a858432（予備実験完了、8 者全員「採用：案 1」）／f01597a（§2.6 12 評価観点の事前定義）／0e57bdb（第 1 段階完了、83 ファイル 2646 行追加）。(2) Gemini API 追加（gemini-3.5-flash／gemini-3.1-pro-preview、GEMINI_API_KEY は zsh 経由）、累積テスト 100 件 pass。(3) 5 者→ **7 モデル**比較実験に拡大（利用者明示承認「対象モデルを拡大し、google gemini API を追加する」セッション 31）。(4) 第 1 段階（must-fix 9 件 × 8 者）完了：完全一致 4 件／準一致 3 件／分岐 2 件、Sonnet 4.6 の CLI／API 経路差を観察、Gemini 系で質問発火 3 件（マルチターン 2 ターン目に進入）。(5) **重要発見**：分岐論点では proxy 役にアサイン権限（論文査読システム類似）を与える運用が有効、§5.12 改訂の論点として §6.9 に記録（利用者明示承認「d」セッション 31）。(6) settings.local.json に zsh -c 等の許可ルール追加（案 3：deny ルールで安全策）。(7) 判定支援資料 tools/experiments/judgment-aid-for-human.md 作成。(8) F-006（topic-05）と A-005（topic-10）は人本人が「平易な説明が必要」と要求、観点 3（質問能力）の人本人発火例

- **セッション 30（2026-05-26）の総括**：API 経路先取り実装サイクル 4 完成（4-A／4-B／4-C、累積 60 件 pass）、foundation／tasks.drafting＋triad-review レビュー実施（must-fix 10 件・should-fix 7 件・leave-as-is 4 件）、5 者比較実験の方針確定。詳細は git log（コミット ce02bc1／22721b4／3f95012／f1813f0／133c45b／3325b3d／9f1f472／576513b）参照

- **API 経路先取り実装の計画変更（軽量手続き、セッション 28、2026-05-26）**：本来フェーズ 4 第 2 サイクルで実装予定の API 経路を、tasks 段着手前に先取りで最小実装。3 者評価比較（Claude／API 経由他モデル：Anthropic ＋ OpenAI／人間）をパイロット → 段階的拡張で実施。計画書 §5.9.7.1 新設、§5.11 フェーズ 3 ／ フェーズ 4 第 2 サイクル改訂。設計済み 7 機能への遡及不要（実装方針の前倒しのみ）。利用者明示承認「API 実装を先取りで実装」「論点 2 ＝案 B」「論点 3 ＝案 b」「論点 4 ＝提示案どおり」「論点 5 ＝案 Z」「承認」（セッション 28）。設計案 P：オーケストレーター方式（Claude Code 内で私が呼び出しと結果統合）、役単位で path: cli / api を選択、API 経路は Python スクリプト `tools/api_providers/run_role.py`（1 役を 1 回実行、私が Bash で起動）、結果統合は私が手動（フェーズ 4 以降に自動化検討）。プロバイダー抽象層でモデル名は文字列指定、候補は Anthropic（claude-sonnet-4-6／claude-opus-4-7）と OpenAI（gpt-5.5／gpt-5.4／gpt-5.3-codex 等、セッション 29 で利用者更新）。論点 γ の進め方は (2)「yaml 構造設計を先行、モデル名はプレースホルダー、実装後に利用者が yaml で書き換え」を採用。利用者明示承認「提案どおりでよい」「提案で OK．実装後に yaml で書き換え」（セッション 28）「(2)。openai の場合、gpt-5.5, gpt-5.4, gpt-5.3-codex が候補」（セッション 29）

- **API 経路先取り実装：論点 α〜δ 確定と TDD サイクル 1〜3 完了（セッション 29、2026-05-26）**：論点 α（yaml 保存場所＝ `config/api-settings.yaml`、5961d1b）／論点 β（`run_role.py` 入出力契約、長オプション 6 種、標準出力 YAML、ac6eb63）／論点 γ（OpenAI 候補名 gpt-5.5／gpt-5.4／gpt-5.3-codex、進め方 (2) プレースホルダー方式、755fd6d）／論点 δ（yaml 命名規約 `connection`／`default`／`variants`、本体作成、19b1eeb）を確定。ディレクトリ命名整合修正（`tools/api-providers/` → `tools/api_providers/`、計画書 §4 行 209 規則準拠、8ddc674）。Python 環境整備（`pyproject.toml` 新規、`.venv` 隔離、`.gitignore` 更新、c2815db）。TDD サイクル 1（config_loader.py、c2815db／c57c5ae）／サイクル 2（providers.py プロバイダー抽象層、1ea0380／b1cb58c）／サイクル 3（providers.py の send_request、httpx／respx 依存、5eb051b／7778b80）累積 30 件全通過、回帰なし。利用者明示承認多数（コミットメッセージに記載、再オープン手続き 1 件含む：experiments 方式 → connection／default／variants）。次工程：サイクル 4（リトライ機構、yaml 出力整形、`run_role.py` エントリポイント）

- **design 段完全終了（セッション 28、2026-05-26、コミット 8cbb5b9／7cb8d6d／6b95a10）**：全 7 機能で drafting／triad-review／review-wave／alignment／approval すべて true。design.review-wave 全 16 件対処済み、章番号体系は機能内整合 OK／機能横断統一は案 C で許容、接合面整合 A-011〜A-016 全 6 件 OK、軽量一括承認（案 b）で approval 完了。利用者明示承認「案 X」「案 C」「案 b」「はい」x 多数（2026-05-26 セッション 28）。**次フェーズは tasks 段**

- **design.review-wave 全 16 件対処完了（セッション 28、2026-05-26、コミット e24d86e／c15ef5b／a2a65c0／04ab855／79ec3d9／92ff60a）**：3 グループ段階消化（① A-013：foundation 信頼度ラベル／② A-011／A-014／A-015：evaluation／analysis 接合面／③ A-012／A-016：self-improvement／workflow-management／conformance-evaluation 相互参照）。軽量再オープン手続き 2 件（A-013／A-011）を含む。詳細は pending-cross-feature-findings.md とコミットメッセージ参照

- **design 段 drafting＋triad-review 全 7 機能完了（セッション 25〜27、2026-05-25〜2026-05-26）**：foundation／runtime／evaluation／analysis／workflow-management／self-improvement／conformance-evaluation。詳細は各機能の spec.json workflow_state と git log（コミット 49aa7d8／7b57072／881761d／ffd8adc／dd8eba9／2177118／dda65ec／207a33e）参照

- **規律ファイル管理体制の整備（セッション 26〜27、2026-05-25〜2026-05-26）**：memory → docs/disciplines/ への軽量移送（16 件、シンボリックリンク化）、no-unilateral-action 撤去、複数案提示規律統合（discipline_options_presentation.md 新設・active 必読昇格）。詳細は docs/disciplines/README.md と git log（コミット b830785／b529c8e／9b9e827）参照

セッション 22〜24 の確定事項は archive snapshot に退避：[docs/archive/todo/TODO_NEXT_SESSION-2026-05-25-snapshot.md](docs/archive/todo/TODO_NEXT_SESSION-2026-05-25-snapshot.md)。
2026-05-21 までのさらに古い確定事項は別の snapshot：[docs/archive/todo/TODO_NEXT_SESSION-2026-05-24-snapshot.md](docs/archive/todo/TODO_NEXT_SESSION-2026-05-24-snapshot.md)。

## 5. 関連参照とスクリプト

- 計画書：`docs/plan/reconstruction-plan-2026-05-21.md`
- 運営ガイド：`docs/operations/SESSION_WORKFLOW_GUIDE.md`
- spec.json 正本スキーマ：計画書 §5.24
- TODO 雛形：`templates/todo/TODO_NEXT_SESSION.template.md`
- spec.json 雛形：`templates/specs/spec.json.template`
- レビュー記録雛形：`templates/review/manual_dogfooding_review_template.md`
- 持ち越し所見：`.reviewcompass/pending-cross-feature-findings.md`（0 件未消化、全 16 件対処済み）
- 抽出進捗：`docs/extraction-mapping.md`
- **規律ファイル本体**：`docs/disciplines/`（active 必読 12 件＋参照層 3 件＋ README.md）
- 規律ファイルディレクトリの解説：`docs/disciplines/README.md`
- 過去スナップショット 2 件：
  - `docs/archive/todo/TODO_NEXT_SESSION-2026-05-24-snapshot.md`（2026-05-21 までの確定事項）
  - `docs/archive/todo/TODO_NEXT_SESSION-2026-05-25-snapshot.md`（2026-05-22〜2026-05-25 セッション 24 末＋セッション 25 内の確定事項）

自動記録スクリプト（セッション終了時）：

```
cd /Users/Daily/Development/ReviewCompass
python3 tools/session-log-converter.py --latest \
    ~/.claude/projects/-Users-Daily-Development-ReviewCompass \
    docs/sessions/session-22-2026-05-24.md
```
