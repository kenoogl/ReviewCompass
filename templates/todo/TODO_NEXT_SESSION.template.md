# <プロジェクト名> - 次セッション継続用メモ

最終更新：<YYYY-MM-DD>（<セッション要約>）
作業ディレクトリ：<リポジトリの絶対パス>
リポジトリ：<git リモート URL>

---

<!-- TEMPLATE_HEADER_START：本ヘッダは templates/todo/TODO_NEXT_SESSION.template.md から派生。本セクションは削除・短縮しないこと。 -->

## 0. ReviewCompass 利用にあたる重要規律（削除禁止）

本セクションは ReviewCompass（dual-reviewer 方式の仕様駆動レビューシステム）を使うすべてのプロジェクトに共通する重要規律。**削除・短縮しないこと**。LLM が本 TODO を読む際、毎セッション開始時に本セクションを確認し、本セクションに書かれた手順を毎作業前に守る。

### 0.1 提案前必須確認（ナビゲータ問い合わせを起点とする）

「次の作業」「次のステップ」「段取り」「所見の振り分け」を提案する前に、
まず次のコマンドを venv Python で実行し（実行形は本 TODO 末尾の「プロジェクト固有の補足」参照）、その `next_action` を応答に引用する：

    tools/check-workflow-action.py next --json

1. `next_action.kind` を現在の作業順序・優先順位の正本として扱う。
   読み方は `docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md` に従う。
   記憶・要約・本 TODO §3 だけを段取りの根拠にしない。
2. `post_write_verification`、`reopen_in_progress`、`resume_in_progress` が返った場合は、
   通常ワークフローよりそれらを優先する。
3. spec.json 変更・commit・push などの不可逆操作の直前は、
   対応する precheck サブコマンドを呼ぶ。
4. `unknown` または判定不能の場合は、推測せず利用者へ報告する。

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

**この手順はセッション起動と同時に強制実行する。利用者の指示を待たず、「ご指示をいただけますか」と伺わない。**

1. navigator を実行し、`next_action` を確認する。
   実行形は本 TODO 末尾の「プロジェクト固有の補足」を参照する。
2. 本 `TODO_NEXT_SESSION.md` の §2（現在位置）と §3（次の作業候補）を確認
3. `git log --oneline -5` / `git status` で到達点確認
4. 作業開始前に対象機能の `.reviewcompass/specs/<機能>/spec.json` を Read

規律は MEMORY.md 索引がセッション開始時に自動ロード済み。全件の本文読み込みは不要。操作の直前に下表の該当行を Read する。

| 操作 | 直前に読む規律ファイル（`docs/disciplines/` 配下） |
|------|------------------------------------------------|
| コミット・プッシュ前 | `discipline_workflow_precheck_invocation.md`・`discipline_approval_operation.md` |
| 規律を変更する前 | `discipline_reopen_procedure_for_settled_topics.md` |
| triad-review 所見の対処前 | `discipline_must_fix_discussion_obligation.md` |
| md 文書を書いた後 | `discipline_post_write_verification.md` |
| yaml ファイルを書いた後 | `discipline_yaml_audit.md` |
| 複数ファイルの横断操作前 | `discipline_pre_action_precheck.md` |

計画書・運営ガイドは当該操作に関わる節だけ、必要なときに Read する。

## 2. 過去経緯と総括

（過去セッションの主要成果、規律違反履歴、教訓等を必要に応じて記載）

## 3. 次の作業候補

この節は候補であり、現在の作業順序の正本ではない。
作業開始前に §0.1 / §1 の navigator を実行し、`next_action` に従う。

`next_action.kind == "stage"` の場合のみ、`feature`・`phase`・`stage` を確認して以下の作業に着手する。

`post_write_verification`、`reopen_in_progress`、`resume_in_progress`、`unknown` が返った場合は、この節の作業へ進まない。

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

### プロジェクト固有の補足

（プロジェクト特有の実行環境・ツールの注意事項をここに記載。例：仮想環境（venv）の使い方、認証情報の場所、外部サービスへの接続手順など。起動手順 §1 には含めず、参照用として本節に置く。）

---

## 利用上の注意（雛形利用者向け）

- 本雛形をプロジェクトに配置するときは、ファイル名を `TODO_NEXT_SESSION.md` とし、リポジトリ直下に置く
- `<プロジェクト名>` や `<日付>` 等のプレースホルダを実値に置き換える
- §0 ReviewCompass 利用にあたる重要規律はテンプレートヘッダで囲まれている（`<!-- TEMPLATE_HEADER_START -->` と `<!-- TEMPLATE_HEADER_END -->` の間）。本ヘッダは **削除・短縮しない**
- §1〜§5 はプロジェクト固有・セッション固有の内容として自由に書き換え可能
