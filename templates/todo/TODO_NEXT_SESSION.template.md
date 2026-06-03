# ReviewCompass - Codex 次セッション継続用メモ

最終更新：<YYYY-MM-DD>（<セッション要約>）
作業ディレクトリ：`/Users/Daily/Development/ReviewCompass/`
リポジトリ：`git@github.com:kenoogl/ReviewCompass.git`

---

<!-- TEMPLATE_HEADER_START：本ヘッダは templates/todo/TODO_NEXT_SESSION.template.md から派生。本セクションは削除・短縮しないこと。 -->

## 0. ReviewCompass 利用にあたる重要規律（削除禁止）

本セクションは ReviewCompass を Codex で運用するための入口規律。**削除・短縮しないこと**。Codex が本 TODO を読む際、毎セッション開始時に本セクションを確認し、本セクションに書かれた手順を毎作業前に守る。

### 0.1 提案前必須確認（ナビゲータ問い合わせを起点とする）

「次の作業」「次のステップ」「段取り」「所見の振り分け」を提案する前に、
まず次のコマンドを venv Python で実行し（実行形は本 TODO 末尾の「プロジェクト固有の補足」参照）、その `next_action` を応答に引用する：

    tools/check-workflow-action.py next --json

1. `next_action.kind` を現在の作業順序・優先順位の正本として扱う。
   共通の読み方は `docs/operations/WORKFLOW_NAVIGATION.md` に従う。
   Codex 固有の制約は `docs/operations/WORKFLOW_NAVIGATION_FOR_CODEX.md` に従う。
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
- maintenance_in_progress の開始・完了
- 計画書の方針変更
- フェーズ移行に伴う一括処理
- 大規模な再設計（複数機能にまたがる責務分担変更等）

承認の判定基準：「承認します」「OK」「採用」「進めて」「はい」等の明示的肯定発言、または AskUserQuestion 等での明示選択のみ。議論継続・停止・方法論指示・沈黙・命名指摘は承認とみなさない。

### 0.3 起草者と判定者の分離（計画書 §5.4）

drafting 段は actor=human または llm（草案作成のみ）、triad-review 段は actor=llm（主役・敵対役・判定役の 3 役、API 経由の独立系統で実施）。**同一の actor が起草と判定を兼ねない**。

レビュー記録の front-matter には `author.identity` と `reviewer.identity` を異名で必須記載し、機械検査の対象とする。

<!-- TEMPLATE_HEADER_END -->

---

## 1. 起動手順（Codex セッション開始時）

**この手順はセッション起動と同時に強制実行する。利用者の指示を待たず、「ご指示をいただけますか」と伺わない。**

1. navigator を実行し、`next_action` を確認する。
   実行形は本 TODO 末尾の「プロジェクト固有の補足」を参照する。
2. 本 `TODO_NEXT_SESSION.md` の §2（現在位置）と §3（次の作業候補）を確認
3. `git log --oneline -5` / `git status` で到達点確認
4. 作業開始前に対象機能の `.reviewcompass/specs/<機能>/spec.json` を Read

Codex では repo 外 memory の自動ロードを前提にしない。規律本文は repo 内 `docs/disciplines/` を正本とし、操作の直前に下表の該当行を Read する。

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

（過去セッションの主要成果、maintenance、規律違反履歴、教訓等を必要に応じて記載）

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

- §0 提案前必須確認に従って、作業候補を提案する前に必ず navigator を実行し、`next_action` を正本として扱う
- Codex では `AGENTS.md` と `docs/operations/WORKFLOW_NAVIGATION_FOR_CODEX.md` を入口規律として扱う
- repo 外 memory を前提にしない。必要な規律・記録は repo 内文書を読む
- 承認取得時は利用者の明示承認発言（発言の正確な引用とログ行）を必ず併記して spec.json を更新
- レビュー記録の front-matter には author と reviewer フィールドを必ず明記（§5.4 起草者と判定者の分離規律）
- mode 値は現行の計画書・仕様に従う（例：`api_mediated`）
- docs/ 配下や `TODO_NEXT_SESSION.md` を書いた後は navigator を再実行し、post-write-verification の状態を確認する
- commit／push は利用者の明示指示がある場合のみ実行する

## 4. 確定事項一覧

（日付ごとに利用者明示承認のあった確定事項を出典付き＝発言の正確な引用とログ行を併記して列挙）

## 5. 関連参照とスクリプト

- Codex 入口規律：`AGENTS.md`
- 共通ナビゲーション：`docs/operations/WORKFLOW_NAVIGATION.md`
- Codex 用ナビゲーション：`docs/operations/WORKFLOW_NAVIGATION_FOR_CODEX.md`
- Codex hook：`.codex/hooks/README.md`
- ナビゲータ：`tools/check-workflow-action.py`
- 計画書：`docs/plan/reconstruction-plan-2026-05-21.md`
- 運営ガイド：`docs/operations/SESSION_WORKFLOW_GUIDE.md`
- 規律本体：`docs/disciplines/`
- spec.json 正本：`.reviewcompass/specs/<feature>/spec.json`

### プロジェクト固有の補足

**Python 実行（venv 経由）**：スクリプト実行は **必ず venv の Python を直接指定**（`python3` 直叩きや `zsh -c '... python3'` は PyYAML なしで失敗。`subprocess.run([sys.executable])` が venv パッケージを参照するため起動 Python が venv である必要）：

```
zsh -c 'source ~/.zshrc && /Users/Daily/Development/ReviewCompass/.venv/bin/python3 <script.py>'
```
