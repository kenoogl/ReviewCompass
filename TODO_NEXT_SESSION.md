# 次セッション継続用メモ

最終更新：2026-05-26（セッション 28 末、design 段完全終了。全 7 機能で drafting／triad-review／review-wave／alignment／approval すべて true。design.review-wave で機能横断波及所見 16 件すべて対処、軽量再オープン手続き 2 件（A-013／A-011）を含む。次フェーズは tasks 段（drafting → triad-review → review-wave → alignment → approval）から再開）
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

## 1. 起動手順（セッション 29 開始時）

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

## 2. ワークフロー上の現在位置（2026-05-26 セッション 28 末時点）

実態は **spec.json の workflow_state から確認**（§0.1 規律）：

- **intent 層**：drafting／review／approval すべて true
- **feature-partitioning 層**：candidate-proposal／approval すべて true
- **requirements 段**：全 7 機能で drafting／triad-review／review-wave／alignment／approval すべて true
- **design 段**：全 7 機能で drafting／triad-review／review-wave／alignment／approval すべて true（セッション 28 末で完全終了）
- **tasks／implementation 段**：すべて false

機能横断波及所見：A-001〜A-016 の **16 件すべて対処済み**（design.review-wave 完了、セッション 28 末）。詳細は `.reviewcompass/pending-cross-feature-findings.md` を参照。

規律ファイルの現状：本体は repo の `docs/disciplines/discipline_*.md` に配置、memory 側 `feedback_*.md` はシンボリックリンクで repo 本体を指す。最新の件数・分類は `docs/disciplines/README.md` の規律ファイル一覧表を参照。

## 3. 次の作業候補（優先順位順）

**現在の主要作業：tasks 段着手（drafting → triad-review → review-wave → alignment → approval）**

セッション 28 末で全 7 機能の design 段が完全終了。次フェーズは tasks 段：

1. **tasks 段 drafting**：依存マップ順（foundation → runtime → evaluation → analysis → workflow-management → self-improvement → conformance-evaluation）で順次起草
2. **tasks 段 triad-review／review-wave／alignment／approval**：drafting 完了後、運営ガイド §2.3 の段順に従って進める

着手時の段階 2 スクリプト連動：`tools/check-workflow-action.py spec-set <feature> tasks drafting true` を呼んで依存検査を通過してから Edit／Write を行う（規律 [[workflow-precheck-invocation]]）。

3 役配置（実験(エ)継続予定）：主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7（tasks 段着手時に再確認）。

計画書 §5.5 phase_order の補正課題（セッション 26 で A-001 として認識）：計画書 §5.5 行 376〜383 の phase_order 構造例には self-improvement が記載漏れで 6 機能のみ列挙されているが、§3.1／§5.16／A-007 案 2 に基づき本設計では 7 機能を採用済み。計画書側の補正は別途追跡。

---

## 4. 直近の確定事項

利用者明示承認のあった項目を新しい順に記録（詳細は pending-cross-feature-findings.md ／ docs/disciplines/README.md ／ git log で追える）：

- **API 経路先取り実装の計画変更（軽量手続き、セッション 28、2026-05-26）**：本来フェーズ 4 第 2 サイクルで実装予定の API 経路を、tasks 段着手前に先取りで最小実装。3 者評価比較（Claude／API 経由他モデル：Anthropic ＋ OpenAI／人間）をパイロット → 段階的拡張で実施。計画書 §5.9.7.1 新設、§5.11 フェーズ 3 ／ フェーズ 4 第 2 サイクル改訂。設計済み 7 機能への遡及不要（実装方針の前倒しのみ）。利用者明示承認「API 実装を先取りで実装」「論点 2 ＝案 B」「論点 3 ＝案 b」「論点 4 ＝提示案どおり」「論点 5 ＝案 Z」「承認」（セッション 28）。設計案 P：オーケストレーター方式（Claude Code 内で私が呼び出しと結果統合）、役単位で path: cli / api を選択、API 経路は Python スクリプト `tools/api-providers/run_role.py`（1 役を 1 回実行、私が Bash で起動）、結果統合は私が手動（フェーズ 4 以降に自動化検討）。プロバイダー抽象層でモデル名は文字列指定、候補は Anthropic（claude-sonnet-4-6／claude-opus-4-7）と OpenAI（gpt-5.5／gpt-5.4／gpt-5.5-pro／o4-pro 等、利用者確認待ち）。利用者明示承認「提案どおりでよい」「提案で OK．実装後に yaml で書き換え」（セッション 28）

- **API 設定ファイルの再オープン（セッション 29、2026-05-26）**：旧確定「複数 experiments 方式（3 パターン：baseline_claude／claude_vs_openai_adversarial／all_openai）」を撤回し、新確定として **`config/api-settings.yaml` を新設**（`reviewcompass.yaml` から参照、恒久の API 設定ファイル）。default 1 設定を本体とし、パイロット段階のみ `variants` 節で複数バリエーションを併設、起動時に `--variant <名前>` で切替。デプロイ時は variants 節を削るだけで運用設定に移行できる。再オープン理由：利用者指摘「yaml ファイルは API の設定を保存するところ。今回は実験だが、デプロイしたときには実験か？」（experiments の恒久名称が運用後に意味と合わない）。維持部分：オーケストレーター方式、役単位の経路選択、Python スクリプト、プロバイダー抽象層（モデル名は文字列指定）、モデル能力配分規律。利用者明示承認「(I) 再オープン可、別ファイル」「いずれも OK」（セッション 29）。計画書 §5.9.7.1 末尾に正本記述を追記

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
