# 次セッション継続用メモ

最終更新：2026-05-24（セッション 22 末、TODO 雛形新設＋本体縮約、過去履歴は archive snapshot に退避、次は requirements.approval から再開）
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

<!-- TEMPLATE_HEADER_END -->

---

## 1. 起動手順（セッション 23 開始時）

ReviewCompass の運営ガイドラインの必読フローに従う：

1. ターミナルで `cd /Users/Daily/Development/ReviewCompass`
2. 本 `TODO_NEXT_SESSION.md` を読む（§0 重要規律を必ず確認）
3. `docs/operations/SESSION_WORKFLOW_GUIDE.md` を読む（必読フロー・ワークフロー段の役割・サブエージェント方式の運用条件）
4. 計画書 `docs/plan/reconstruction-plan-2026-05-21.md` §5.4〜§5.8 を読む（ワークフロー手続き、reopen、session 跨ぎ、多層防御）
5. 計画書 §5.24 を読む（spec.json の正本スキーマ、2026-05-24 セッション 22 で新設）
6. 計画書 §5.12 を読む（人間代役機構、approval 段の actor=proxy_model 連動）
7. 計画書 §5.23 と §5.23.12 を読む（dogfooding と subagent_mediated 方式）
8. `.reviewcompass/pending-cross-feature-findings.md` を読む（持ち越し所見、現在 0 件未消化）
9. `docs/extraction-mapping.md` を読む（進行記録）
10. `git log --oneline -10`／`git status` で到達点確認

過去の経緯（セッション 19〜22 の詳細履歴、規律違反履歴、撤回履歴、過去の確定事項一覧等）は `docs/archive/todo/TODO_NEXT_SESSION-2026-05-24-snapshot.md` を参照。

## 2. ワークフロー上の現在位置（2026-05-24 セッション 22 末時点）

実態は **spec.json の workflow_state から確認**（§0.1 規律）：

- **intent 層**：drafting／review／approval すべて true（intent 文書 4 件は 2026-05-24 に素材リポからコピー配置済み、`intent/` 配下）
- **feature-partitioning 層**：candidate-proposal／approval すべて true（`stages/feature-partitioning/2026-05-24-proposal.md` 配置済み）
- **requirements 段**：drafting／triad-review／review-wave／alignment すべて true、**approval が false（利用者承認未取得）**
- **design 段以降**：すべて false

機能横断波及所見：6 件すべて対処済み（`.reviewcompass/pending-cross-feature-findings.md`）。

## 3. 次の作業候補（優先順位順）

### A. requirements 段の approval 取得（design 着手の前提）

全 7 機能の spec.json で `workflow_state.requirements.approval` が false。運営ガイド §2.3 第 6 項「approval で利用者または別モデル承認を得てから次フェーズに進む」に従い、design 段着手の前に requirements の approval を取得する必要がある。

依存マップ順に 1 機能ずつ承認を取る（方式 B、2026-05-24 利用者明示承認）：

1. foundation → 2. runtime → 3. evaluation → 4. analysis → 5. workflow-management → 6. self-improvement → 7. conformance-evaluation

各機能の手順：

- 利用者が `.reviewcompass/specs/<機能>/requirements.md` をレビュー
- 明示承認（規律 §0.2）
- spec.json の `workflow_state.requirements.approval` を true に更新、承認発言の出典（発言の正確な引用・日付）を併記

### B. 設計フェーズの drafting 段着手（A 完了後）

A の requirements approval が全 7 機能で完了したら、design フェーズの drafting 段に進む。依存マップ順に foundation design.md（585 行、§5.18）から開始。各機能 drafting 後に triad-review、機能横断所見があれば pending-cross-feature-findings.md に追記。

design.md の素材：`/Users/Daily/Development/Rwiki-v2-code-mod/dual-reviewer-rebuild/.kiro/specs/<機能名>/design.md`（読み取り専用）

## 4. 直近の確定事項（2026-05-24 セッション 22〜23）

利用者明示承認のあった項目を新しい順に記録：

- runtime requirements approval 取得（2026-05-24 セッション 23、利用者発言「承認」、依存マップ順 2/7 機能目）
- 文言と事実の食い違いの是正：runtime requirements.md 行 179・181 で A-001 を未来形（持ち越し）から過去形（2026-05-23 対処済み）に書き換え。要件本文の 4 値参照は既に正しい状態のため文言の事実整合のみ
- foundation requirements approval 取得（2026-05-24 セッション 23、利用者発言「確認した。承認」、依存マップ順 1/7 機能目）
- 旧 paper-interface 由来の用語不整合 A-009 の対処：foundation 1 箇所＋analysis 6 箇所で「論文」→「報告書」統一、行 5 の歴史的経緯記述（`paper-interface`（論文向け）の旧名）は保持。利用者発言「(ア) 、論文ではなく報告書とする」（2026-05-24 セッション 23）
- TODO 縮約：履歴系を `docs/archive/todo/TODO_NEXT_SESSION-2026-05-24-snapshot.md` に退避、本体約 100 行に削減
- TODO 雛形 `templates/todo/TODO_NEXT_SESSION.template.md` 新設、本 TODO も雛形構造に整合
- intent 4 文書を素材リポから `intent/` にコピー、`stages/intent.yaml` と `stages/feature-partitioning/2026-05-24-proposal.md` 新設、7 機能の spec.json reference を実在パスに更新
- 設計メモ `docs/design/spec-json-schema-design.md` を archive 退避（`docs/archive/design/2026-05-24-spec-json-schema-design.md`）
- spec.json 雛形配置と 7 機能配置（第 3 段階完了）
- 計画書改定の第 2 段階完了（§5.5／§5.6／§5.7／§5.12／§5.20 改定 ＋ §5.24 新設）
- 段名 local-review → triad-review に改名（active 全ファイル一括置換、63 箇所）
- 論点 1（6 階層保持）と論点 6（機能分離証跡を artifacts へ）の整合解決
- active 必読層棚卸し（候補 1：pre-action-checklist を multi-file-dependency-precheck に統合）
- 規律違反の認知と是正：(a) intent と feature-partitioning を実体確認なく true にした失態、(b) requirements.approval 未取得を見落として design.drafting を提案した失態

過去の確定事項（2026-05-21 までの §5.19.1 着手前必須 5 件、2026-05-22 抽出中確定、2026-05-23 セッション 21 確定 8 件等）は archive snapshot を参照。

## 5. 関連参照とスクリプト

- 計画書：`docs/plan/reconstruction-plan-2026-05-21.md`
- 運営ガイド：`docs/operations/SESSION_WORKFLOW_GUIDE.md`
- spec.json 正本スキーマ：計画書 §5.24
- TODO 雛形：`templates/todo/TODO_NEXT_SESSION.template.md`
- spec.json 雛形：`templates/specs/spec.json.template`
- レビュー記録雛形：`templates/review/manual_dogfooding_review_template.md`
- 機能依存マップ：`stages/feature-dependency.yaml`（フェーズ 2 以降に配置予定）
- 持ち越し所見：`.reviewcompass/pending-cross-feature-findings.md`（0 件未消化）
- 抽出進捗：`docs/extraction-mapping.md`
- 過去スナップショット：`docs/archive/todo/TODO_NEXT_SESSION-2026-05-24-snapshot.md`

自動記録スクリプト（セッション終了時）：

```
cd /Users/Daily/Development/ReviewCompass
python3 tools/session-log-converter.py --latest \
    ~/.claude/projects/-Users-Daily-Development-ReviewCompass \
    docs/sessions/session-22-2026-05-24.md
```
