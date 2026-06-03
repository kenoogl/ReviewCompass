# 次セッション継続用メモ

最終更新：2026-06-03（Codex adapter migration 完了、TODO テンプレート Codex 専用化）。**次の作業：evaluation 機能の implementation drafting（草案作成）**。セッション52 では TODO §0.1・§1・§3 をナビゲータ起点方式に改訂（畳み込みA層完了）、Gemini 検証インフラ整備、coverage matrix（verifications[] フィールド）の TDD 実装と文書化、書き込み後検証6ラウンド ALL_CLEAR を実施した。続く Codex adapter migration では Codex 用入口文書・hook・maintenance_in_progress・Claude 前提の棚卸しを整備し、maintenance を完了して通常ワークフローへ復帰した。実装進捗（spec.json）はセッション49末から変化なし。経緯は §3.2／session 記録参照。

作業ディレクトリ：`/Users/Daily/Development/ReviewCompass/`、リポジトリ：`git@github.com:kenoogl/ReviewCompass.git`（main ブランチ）

> **運用メモ（セッション48 利用者指摘）**：ツール呼び出しを送る直前に、タグが名前空間付きの定型になっているか自己点検する（Write／Edit や長文の直後で接頭辞が抜け「malformed」になる崩れが頻発するため）。
> **報告メモ（同）**：自律実行区間（承認不要の実装・TDD 等）は報告を最小化——precheck は「（precheck: OK）」の 1 行、進捗はタスク一覧に任せ逐一の緑確認を繰り返さない、ファイル列挙の重複を避ける。コミット／push／spec.json／判断の節目は従来どおり詳述（規律由来の達成基準宣言・事前検査は維持）。

---

<!-- TEMPLATE_HEADER_START：本ヘッダは templates/todo/TODO_NEXT_SESSION.template.md から派生。 -->

## 0. ReviewCompass 利用にあたる重要規律

毎セッション開始時に確認し、毎作業前に守る。

### 0.1 提案前必須確認（ナビゲータ問い合わせを起点とする）

「次の作業」「次のステップ」「段取り」「所見の振り分け」を提案する前に、
まず次のコマンドを venv Python で実行し（実行形は本 TODO 末尾の「プロジェクト固有の補足」参照）、その `next_action` を応答に引用する：

    tools/check-workflow-action.py next --json

1. `next_action.kind` を現在の作業順序・優先順位の正本として扱う。
   共通の読み方は `docs/operations/WORKFLOW_NAVIGATION.md` に従う。
   実行環境固有の制約は、Codex では `docs/operations/WORKFLOW_NAVIGATION_FOR_CODEX.md`、
   Claude Code では `docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md` に従う。
   記憶・要約・本 TODO §3 だけを段取りの根拠にしない。
2. `post_write_verification`、`reopen_in_progress`、`resume_in_progress` が返った場合は、
   通常ワークフローよりそれらを優先する。
3. spec.json 変更・commit・push などの不可逆操作の直前は、
   対応する precheck サブコマンドを呼ぶ。
4. `unknown` または判定不能の場合は、推測せず利用者へ報告する。

### 0.2 利用者明示承認が必要な不可逆操作

次は利用者の **明示承認** なしに実行しない：

- spec.json の `workflow_state` を true に変更／フェーズ移行
- git commit／git push
- 計画書の方針変更／大規模な再設計
- 規律ファイルの追加・変更（docs/disciplines/ 配下、軽量移送手続き経由）

承認の判定基準：「承認」「OK」「採用」「進めて」「はい」「案 ア」等の明示的肯定発言、または AskUserQuestion 等での明示選択のみ。議論継続・停止・方法論指示・沈黙は承認とみなさない。

commit は利用者の職掌範囲として扱う。Codex/LLM は利用者から明示的に「コミット」と指示された場合だけ実行し、直前に `tools/check-workflow-action.py commit --rationale "<理由>"` を通す。機械ガードとして `.reviewcompass/approvals/commit-approval.json` のユーザ承認レコードを必須にし、実行は原則 `tools/guarded-git-commit.py -m "<message>" --rationale "<理由>"` 経由とする。承認レコードなし・消費済み・承認対象外 staged ファイルありの場合は `DEVIATION` として停止する。

### 0.3 起草者と判定者の分離（計画書 §5.4）

drafting 段は actor=human または llm（草案作成のみ）、triad-review 段は actor=llm（主役・敵対役・判定役の 3 役）。**同一の actor が起草と判定を兼ねない**。レビュー記録 front-matter に `author.identity` と `reviewer.identity` を異名必須記載、機械検査対象。

<!-- TEMPLATE_HEADER_END -->

---

## 最重要案件（毎セッション必読）

**ワークフロー手続きのナビゲーション問題** — LLM が手続きを正しく把握しないまま提案する失敗が繰り返されている。根本解は workflow-management の実装（手続きを機械的ナビゲータに集約、規律を N→1 のメタ規律に畳む）。当面は利用者がガイド（2026-05-29 セッション 39 決定）。本体：[docs/notes/2026-05-29-workflow-navigation-bootstrap-issue.md](docs/notes/2026-05-29-workflow-navigation-bootstrap-issue.md)

---

## 1. 起動手順（セッション起動と同時に強制実行。利用者の指示を待たず、「ご指示を」と伺わない）

1. navigator を実行し、`next_action` を確認する。
   実行形は本 TODO 末尾の「プロジェクト固有の補足」を参照する。
2. 本 `TODO_NEXT_SESSION.md` の §2（現在位置）と §3（次の作業候補）を確認
3. `git log --oneline -5` / `git status` で到達点確認
4. 作業開始前に対象機能の `.reviewcompass/specs/<機能>/spec.json` を Read

Codex では Claude memory の自動ロードを前提にしない。規律本文は repo 内 `docs/disciplines/` を正本とし、操作の直前に下表の該当行を Read する。Claude Code で作業する場合のみ、Claude 用 memory 索引は補助参照として扱う。

| 操作 | 直前に読む規律ファイル（`docs/disciplines/` 配下） |
|------|------------------------------------------------|
| コミット・プッシュ前 | `discipline_workflow_precheck_invocation.md`・`discipline_approval_operation.md` |
| 規律を変更する前 | `discipline_reopen_procedure_for_settled_topics.md` |
| triad-review 所見の対処前 | `discipline_must_fix_discussion_obligation.md` |
| md 文書を書いた後 | `discipline_post_write_verification.md` |
| yaml ファイルを書いた後 | `discipline_yaml_audit.md` |
| 複数ファイルの横断操作前 | `discipline_pre_action_precheck.md` |

計画書・運営ガイドは当該操作に関わる節だけ、必要なときに Read する。

## 2. ワークフロー上の現在位置（2026-06-03 Codex adapter migration 完了時点、正本は spec.json）

- intent／feature-partitioning：全 7 機能 全段 true
- requirements／design／tasks（全 7 機能）：全段 true（reopened は履歴 true。最新は §3.2／reopen-classification 記録）
- implementation：foundation・runtime（2/7 機能）＝drafting・triad-review true（review-wave 以降 false）／他 5 機能（evaluation／analysis／workflow-management／self-improvement／conformance-evaluation）＝全段 false
- recheck：runtime クリア。**foundation のみ upstream_change_pending=true・impacted=["implementation"]**（api_mediated 変更を将来の review-wave→alignment→approval で織り込む、implementation 未到達のため残置）

## 3. 次の作業候補（セッション 53 起点）

この節は候補であり、現在の作業順序の正本ではない。
作業開始前に §0.1 / §1 の navigator を実行し、`next_action` に従う。

`next_action.kind == "stage"` かつ `feature == "evaluation"`、`phase == "implementation"`、`stage == "drafting"` の場合のみ、以下の作業に着手する。

`post_write_verification`、`reopen_in_progress`、`resume_in_progress`、`unknown` が返った場合は、この節の作業へ進まない。

**次の作業：evaluation 機能の implementation drafting（草案作成）**。runtime の triad-review は完了（spec.json で implementation.triad-review=true）。Codex adapter migration の maintenance は完了済みで、`next` は通常ワークフローの `evaluation / implementation / drafting` を返す。残り機能順序（§3.1）で次は evaluation。review-wave 以降は全機能の triad-review 完了後に機能横断で実施（運営ガイド §2.3、現在 2/7 機能完了）。

**セッション51 完了事項（2026-06-02）**：ワークフローナビゲータ（`check-workflow-action.py next`・`reopen-start`）を Codex が実装、Claude がレビュー・修正確認・コミットを実施。主な機能：(1) `next` サブコマンドで現在の workflow_state から次作業を機械的に返す、(2) `reopen-start` で trigger_map から in-progress ファイルを生成、(3) post-write-verification manifest による完了認定、(4) `cross_feature_stage` 時の `recheck_items`・`pending_cross_feature_findings` 補助情報。Claude 向け手引き `docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md` も整備済み。

**将来（段階2実装時）の必須作業：yaml-audit ⑦⑧ 必須化**（2026-06-02 セッション50 規律確定）：yaml-audit 補助層 E（`docs/disciplines/discipline_yaml_audit.md`）の観点⑦・⑧（下流コード波及／検証テスト存在）は現在「推奨」。段階2で専用の機械検査スクリプトが整備された時点で自動的に「必須」へ昇格する。段階2移行時に `yaml-audit-spec.yaml` の `promotion.trigger` 条件成立を確認し、⑦⑧を required に変更すること。忘れの自動検出（スクリプトありで推奨のまま＝警告）と多重リマインダ（本行・規律 md 段階づけ節・yaml promotion 節）が機能する。

**次セッション持ち越し（規律改訂、2026-06-02 セッション49 利用者決定「案A」）**：post-write-verification（書き込み後独立検証）の対象範囲を拡大する。`config/` の設定ファイルと、`.reviewcompass/specs/` 配下の動作仕様 yaml（ワークフロー5段の成果物でないもの、例：post-write-verification-spec.yaml）を対象に追加。あわせて (1) 5段で検証される仕様文書と直接編集される動作仕様 yaml の区別ルールの明文化、(2) 今回直接編集した2ファイル（post-write-verification-spec.yaml ／ config/api-settings.yaml、コミット 340413d）への遡及検証の要否、を扱う。改訂対象は規律 docs/disciplines/discipline_post_write_verification.md と post-write-verification-spec.yaml の scope_of_application（利用者明示承認＋所定手続き）。

### 3.1 実装フェーズで確立した手順（runtime 以降も踏襲）

- TDD（テスト先行で赤 → 実装で緑）。Codex では `AGENTS.md` を入口規律とし、コミットは利用者の明示指示がある場合のみ実行する。
- 実装レビュー観点 5 点（タスク文書整合・要件追跡・テスト網羅性・配置命名規約・機能横断波及）。本体 [docs/notes/2026-06-01-implementation-phase-approach.md](docs/notes/2026-06-01-implementation-phase-approach.md)
- **triad-review は独立 API 経由 3 役**（主役 `claude-opus-4-8`／敵対役 `gpt-5.5`／判定役 `gemini-3.1-pro-preview`、mode 値 `api_mediated`）。GPT-5.5 は `timeout_seconds=300` 指定。呼び出しは `tools/api_providers/providers.py`（get_provider／send_request）経由、鍵は OpenAI／Anthropic／Gemini 設定済み
- 所見の調停（must-fix 含む）は LLM、上位判断（規律変更・大方針転換・遡及）は本人留保
- 書き込み後検証：docs/ 配下等の正本文書更新後に独立系統で検証（規律 post-write-verification、`tools/api_providers/` 経由）
- 各段完了で spec.json を true 化（不可逆操作・本人承認）
- 残り機能順序：runtime → evaluation → analysis → workflow-management → self-improvement → conformance-evaluation（workflow-management は §5.12 改訂論点を実装する側のため後ろが安全）

### 3.2 過去セッションの完了経緯

- **Codex adapter migration（2026-06-03）**：ReviewCompass を Codex で安定稼働させるため、共通ナビゲーション文書 `docs/operations/WORKFLOW_NAVIGATION.md` と Codex 用文書 `docs/operations/WORKFLOW_NAVIGATION_FOR_CODEX.md` を整備。`AGENTS.md` を入口規律として追加し、`.codex/hooks/` を repo 管理へ移行。通常ワークフロー外の整備を表す `maintenance_in_progress` を navigator に追加し、maintenance 完了後に `stages/completed/maintenance-2026-06-03-codex-adapter-migration.yaml` へ移動。Claude memory 前提の扱いは `docs/notes/2026-06-03-claude-memory-correction-decision.md` に記録し、Codex では repo 外 memory を前提にしない方針を確定。完了コミットは `890b689`。
- **セッション52**：ナビゲータ導入による規律の畳み込みを議論・着手。A層（§0.1・§1・§3 書き換え・navigator 起点方式・no-redundant の趣旨吸収）を先行実施、B層と no-redundant 規律本体の参照化は workflow-management 正式手続きで実施（急がない）。Gemini 検証インフラ整備、response_formatter コードブロック対応バグを TDD で修正（全12件緑）。post-write-verification の coverage matrix（verifications[] フィールド）を TDD 実装（check-workflow-action.py `coverage_matrix_satisfied` 関数、全47件緑）。実装計画・運用ガイドに coverage matrix 仕様を文書化（8条件・YAML例）。書き込み後検証6ラウンド ALL_CLEAR（Gemini・GPT-5.5・GPT-5.4 独立多重チェック）。コミット10件（`7755ad9`〜`9503e17`）push 済み。
- **セッション51**：ワークフローナビゲータ（Codex 実装）のレビュー・修正確認・コミット。`check-workflow-action.py next`・`reopen-start`・post-write-verification manifest 完了認定・recheck 補助情報を整備。Claude 向け手引き完成。コミット 6 件（`a02a714`〜`1c3bcdb`）push 済み（セッション52 時点）。
- **セッション49**：runtime implementation triad-review を api_mediated（独立3社 API：主役 Opus 4.8／敵対役 GPT-5.5／判定役 Gemini 3.1 Pro）で実施・完了。所見 16 件（判定 must-fix9／should-fix5／leave-as-is2、全 in_feature）を TDD で対処、tests/runtime 全テスト緑 143。初回の対象漏れ（RUNTIME.md）による偽陽性を再レビューで解消。RUNTIME.md 更新は post-write-verification（Google）で ALL_CLEAR。spec.json implementation.triad-review=true。コミット 3 件（`99c0471`／`43846f8`／`81cfc90`）push 済み。記録 [reviews/2026-06-02-implementation-triad-review.md](.reviewcompass/specs/runtime/reviews/2026-06-02-implementation-triad-review.md)
- **セッション48**：runtime implementation drafting（T-001〜T-011）を TDD 完了、テスト緑 351 件。foundation 6 語彙は `foundation_ref.py` 経由で参照のみ、runtime 所有 3 語彙確定。T-011 着手時に tasks 要件追跡の作業単位不整合（要件1・2・4・5・6・10）を発見し再オープン（4 過程、独立 1 体検証＋3 系統諮問）で解消。コミット 11 件（`02daa0a`〜`3810985`、push 済み）。記録 [session-48](docs/sessions/session-48-2026-06-02.md)
- セッション 47 以前（40 含む）の経緯は各 [session 記録](docs/sessions/)・git log・[docs/archive/todo/](docs/archive/todo/) のスナップショット参照

### 3.3 残作業の補完項目（任意・低優先）

- analysis 完全一致 15 件の人本人判定の遡及保存（`topic-{54〜75}-human.yaml` のうちセッション36未保存 15 件、詳細は git log）／実験ノート §5・§6 への追記（両軸2表構成・起草者バイアス検出の観察）

## 4. 関連参照

- 計画書 `docs/plan/reconstruction-plan-2026-05-21.md`／運営ガイド `docs/operations/SESSION_WORKFLOW_GUIDE.md`・`REOPEN_PROCEDURE.md`
- 雛形 `templates/`／持ち越し所見 `.reviewcompass/pending-cross-feature-findings.md`（未消化 0 件）
- 実験ノート `docs/experiments/n-model-comparison.md`／規律本体 `docs/disciplines/`（一覧は README.md）／セッション記録 `docs/sessions/`／過去 TODO snapshot `docs/archive/todo/`

### プロジェクト固有の補足

**Python 実行（venv 経由）**：スクリプト実行は **必ず venv の Python を直接指定**（`python3` 直叩きや `zsh -c '... python3'` は PyYAML なしで失敗。`subprocess.run([sys.executable])` が venv パッケージを参照するため起動 Python が venv である必要）：

```
zsh -c 'source ~/.zshrc && /Users/Daily/Development/ReviewCompass/.venv/bin/python3 <script.py>'
```
