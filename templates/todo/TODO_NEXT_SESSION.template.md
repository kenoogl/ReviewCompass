# <プロジェクト名> - 次セッション継続用メモ

最終更新：<YYYY-MM-DD>（<セッション要約>）
作業ディレクトリ：<リポジトリの絶対パス>
リポジトリ：<git リモート URL>

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

## 1. 起動手順（セッション X 開始時）

ReviewCompass の運営ガイドラインの必読フローに従う：

1. ターミナルで `cd <作業ディレクトリ>`
2. 本 `TODO_NEXT_SESSION.md` を読む（§0 重要規律を必ず確認）
3. `docs/operations/SESSION_WORKFLOW_GUIDE.md` を読む（必読フロー・ワークフロー段の役割・サブエージェント方式の運用条件・利用者判断の見極め）
4. 計画書 §5.4〜§5.8 を読む（ワークフロー手続き、reopen、session 跨ぎ、多層防御）
5. 計画書 §5.24 を読む（spec.json の正本スキーマ）
6. 計画書 §5.12 を読む（人間代役機構）
7. 計画書 §5.23 と §5.23.12 を読む（dogfooding と subagent_mediated 方式）
8. `.reviewcompass/pending-cross-feature-findings.md` を読む（持ち越し所見）
9. `docs/extraction-mapping.md` を読む（進行記録、存在する場合）
10. `git log --oneline -10`／`git status` で到達点確認

## 2. 過去経緯と総括

（過去セッションの主要成果、規律違反履歴、教訓等を必要に応じて記載）

## 3. 次の作業

### 3.1 ワークフロー上の現在位置

（ベースとなる現状。spec.json の workflow_state から計算）

### 3.2 次の作業候補（優先順位順）

（依存マップ順、運営ガイド §2.3 段の進め方の規律に従う。各候補の前段が approval まで完了していることを確認）

### 3.3 次セッションでの注意点

- §0 提案前必須確認に従って、作業候補を提案する前に必ず該当機能の spec.json `workflow_state` を読み、運営ガイド §2.3 規律と照合する
- 承認取得時は利用者の明示承認発言（発言の正確な引用とログ行）を必ず併記して spec.json を更新
- レビュー記録の front-matter には author と reviewer フィールドを必ず明記（§5.4 起草者と判定者の分離規律）
- mode 値は計画書 §5.23.12 に従う（`subagent_mediated` 等）

## 4. 確定事項一覧

（日付ごとに利用者明示承認のあった確定事項を出典付き＝発言の正確な引用とログ行を併記して列挙）

## 5. 関連参照とスクリプト

- 計画書：`docs/plan/<計画書ファイル名>`
- 運営ガイド：`docs/operations/SESSION_WORKFLOW_GUIDE.md`
- spec.json 正本スキーマ：計画書 §5.24
- 機能依存マップ：`stages/feature-dependency.yaml`（フェーズ 2 以降に配置）
- 自動記録スクリプト：`tools/session-log-converter.py`（存在する場合）

---

## 利用上の注意（雛形利用者向け）

- 本雛形をプロジェクトに配置するときは、ファイル名を `TODO_NEXT_SESSION.md` とし、リポジトリ直下に置く
- `<プロジェクト名>` や `<日付>` 等のプレースホルダを実値に置き換える
- §0 ReviewCompass 利用にあたる重要規律はテンプレートヘッダで囲まれている（`<!-- TEMPLATE_HEADER_START -->` と `<!-- TEMPLATE_HEADER_END -->` の間）。本ヘッダは **削除・短縮しない**
- §1〜§5 はプロジェクト固有・セッション固有の内容として自由に書き換え可能
