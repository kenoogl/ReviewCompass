# 次セッション継続用メモ

最終更新：2026-06-02（セッション50）。**次の作業：evaluation 機能の implementation drafting（草案作成）**。セッション50 では yaml-audit 規律（補助層 E）を新設・push 済み（コミット b0c98ee・06269c6）。実装進捗（spec.json）はセッション49末から変化なし。経緯は §3.2／session 記録参照。

作業ディレクトリ：`/Users/Daily/Development/ReviewCompass/`、リポジトリ：`git@github.com:kenoogl/ReviewCompass.git`（main ブランチ）

> **運用メモ（セッション48 利用者指摘）**：ツール呼び出しを送る直前に、タグが名前空間付きの定型になっているか自己点検する（Write／Edit や長文の直後で接頭辞が抜け「malformed」になる崩れが頻発するため）。
> **報告メモ（同）**：自律実行区間（承認不要の実装・TDD 等）は報告を最小化——precheck は「（precheck: OK）」の 1 行、進捗はタスク一覧に任せ逐一の緑確認を繰り返さない、ファイル列挙の重複を避ける。コミット／push／spec.json／判断の節目は従来どおり詳述（規律由来の達成基準宣言・事前検査は維持）。

---

<!-- TEMPLATE_HEADER_START：本ヘッダは templates/todo/TODO_NEXT_SESSION.template.md から派生。 -->

## 0. ReviewCompass 利用にあたる重要規律

毎セッション開始時に確認し、毎作業前に守る。

### 0.1 提案前必須確認

「次の作業」「次のステップ」を提案する前に、次を機械的に確認し応答内で明示宣言：

1. **`workflow_state` を必ず読む**：対象機能の `.reviewcompass/specs/<機能>/spec.json` を Read。要約や記憶を根拠にしない（本 TODO §3 は要約、正本は spec.json）
2. **規律と照合**：運営ガイド §2.3「approval を得てから次フェーズに進む」を毎回確認
3. **正本と照合**：TODO・設計メモを信頼の根拠にせず、spec.json／計画書／運営ガイド／git log と照合

### 0.2 利用者明示承認が必要な不可逆操作

次は利用者の **明示承認** なしに実行しない：

- spec.json の `workflow_state` を true に変更／フェーズ移行
- git commit／git push
- 計画書の方針変更／大規模な再設計
- 規律ファイルの追加・変更（docs/disciplines/ 配下、軽量移送手続き経由）

承認の判定基準：「承認」「OK」「採用」「進めて」「はい」「案 ア」等の明示的肯定発言、または AskUserQuestion 等での明示選択のみ。議論継続・停止・方法論指示・沈黙は承認とみなさない。

### 0.3 起草者と判定者の分離（計画書 §5.4）

drafting 段は actor=human または llm（草案作成のみ）、triad-review 段は actor=llm（主役・敵対役・判定役の 3 役）。**同一の actor が起草と判定を兼ねない**。レビュー記録 front-matter に `author.identity` と `reviewer.identity` を異名必須記載、機械検査対象。

<!-- TEMPLATE_HEADER_END -->

---

## 最重要案件（毎セッション必読）

**ワークフロー手続きのナビゲーション問題** — LLM が手続きを正しく把握しないまま提案する失敗が繰り返されている。根本解は workflow-management の実装（手続きを機械的ナビゲータに集約、規律を N→1 のメタ規律に畳む）。当面は利用者がガイド（2026-05-29 セッション 39 決定）。本体：[docs/notes/2026-05-29-workflow-navigation-bootstrap-issue.md](docs/notes/2026-05-29-workflow-navigation-bootstrap-issue.md)

---

## 1. 起動手順（セッション起動と同時に強制実行。利用者の指示を待たず、「ご指示を」と伺わない）

1. `cd /Users/Daily/Development/ReviewCompass`
2. 本 `TODO_NEXT_SESSION.md` を読む（§0 規律確認）
3. **規律本体 active 必読を個別に Read**（auto memory は索引のみ load のため毎セッション必要。README を読むだけでは不十分、各ファイルを Read）。対象一覧は `docs/disciplines/README.md` の active 必読表（現在 14 件）
4. `docs/operations/SESSION_WORKFLOW_GUIDE.md` と `docs/operations/REOPEN_PROCEDURE.md`（再オープン 4 過程）
5. 計画書 `docs/plan/reconstruction-plan-2026-05-21.md` の §5.4〜§5.9.6・§5.12・§5.23〜§5.24（行番号は変動、参考値）
6. 実験ノート `docs/experiments/n-model-comparison.md` §3.4（マルチターンプロトコル）
7. `git log --oneline -10`／`git status` で到達点確認

### 1.1 Python 実行（venv 経由、毎セッション要確認）

スクリプト実行は **必ず venv の Python を直接指定**（`python3` 直叩きや `zsh -c '... python3'` は PyYAML なしで失敗。`subprocess.run([sys.executable])` が venv パッケージを参照するため起動 Python が venv である必要）：

```
zsh -c 'source ~/.zshrc && /Users/Daily/Development/ReviewCompass/.venv/bin/python3 <script.py>'
```

## 2. ワークフロー上の現在位置（セッション 50 末、正本は spec.json）

- intent／feature-partitioning：全 7 機能 全段 true
- requirements／design／tasks（全 7 機能）：全段 true（reopened は履歴 true。最新は §3.2／reopen-classification 記録）
- implementation：foundation・runtime（2/7 機能）＝drafting・triad-review true（review-wave 以降 false）／他 5 機能（evaluation／analysis／workflow-management／self-improvement／conformance-evaluation）＝全段 false
- recheck：runtime クリア。**foundation のみ upstream_change_pending=true・impacted=["implementation"]**（api_mediated 変更を将来の review-wave→alignment→approval で織り込む、implementation 未到達のため残置）

## 3. 次の作業（セッション 50 起点）

**次の作業：evaluation 機能の implementation drafting（草案作成）**。runtime の triad-review は完了（spec.json で implementation.triad-review=true）。残り機能順序（§3.1）で次は evaluation。review-wave 以降は全機能の triad-review 完了後に機能横断で実施（運営ガイド §2.3、現在 2/7 機能完了）。

**将来（段階2実装時）の必須作業：yaml-audit ⑦⑧ 必須化**（2026-06-02 セッション50 規律確定）：yaml-audit 補助層 E（`docs/disciplines/discipline_yaml_audit.md`）の観点⑦・⑧（下流コード波及／検証テスト存在）は現在「推奨」。段階2で専用の機械検査スクリプトが整備された時点で自動的に「必須」へ昇格する。段階2移行時に `yaml-audit-spec.yaml` の `promotion.trigger` 条件成立を確認し、⑦⑧を required に変更すること。忘れの自動検出（スクリプトありで推奨のまま＝警告）と多重リマインダ（本行・規律 md 段階づけ節・yaml promotion 節）が機能する。

**次セッション持ち越し（規律改訂、2026-06-02 セッション49 利用者決定「案A」）**：post-write-verification（書き込み後独立検証）の対象範囲を拡大する。`config/` の設定ファイルと、`.reviewcompass/specs/` 配下の動作仕様 yaml（ワークフロー5段の成果物でないもの、例：post-write-verification-spec.yaml）を対象に追加。あわせて (1) 5段で検証される仕様文書と直接編集される動作仕様 yaml の区別ルールの明文化、(2) 今回直接編集した2ファイル（post-write-verification-spec.yaml ／ config/api-settings.yaml、コミット 340413d）への遡及検証の要否、を扱う。改訂対象は規律 docs/disciplines/discipline_post_write_verification.md と post-write-verification-spec.yaml の scope_of_application（利用者明示承認＋所定手続き）。

### 3.1 実装フェーズで確立した手順（runtime 以降も踏襲）

- TDD（テスト先行で赤 → 実装で緑）。コミットは依存グループ単位＋テスト/実装の 2 段（CLAUDE.md 優先）
- 実装レビュー観点 5 点（タスク文書整合・要件追跡・テスト網羅性・配置命名規約・機能横断波及）。本体 [docs/notes/2026-06-01-implementation-phase-approach.md](docs/notes/2026-06-01-implementation-phase-approach.md)
- **triad-review は独立 API 経由 3 役**（主役 `claude-opus-4-8`／敵対役 `gpt-5.5`／判定役 `gemini-3.1-pro-preview`、mode 値 `api_mediated`）。GPT-5.5 は `timeout_seconds=300` 指定。呼び出しは `tools/api_providers/providers.py`（get_provider／send_request）経由、鍵は OpenAI／Anthropic／Gemini 設定済み
- 所見の調停（must-fix 含む）は LLM、上位判断（規律変更・大方針転換・遡及）は本人留保
- 書き込み後検証：docs/ 配下等の正本文書更新後に独立系統で検証（規律 post-write-verification、`tools/api_providers/` 経由）
- 各段完了で spec.json を true 化（不可逆操作・本人承認）
- 残り機能順序：runtime → evaluation → analysis → workflow-management → self-improvement → conformance-evaluation（workflow-management は §5.12 改訂論点を実装する側のため後ろが安全）

### 3.2 過去セッションの完了経緯

- **セッション49**：runtime implementation triad-review を api_mediated（独立3社 API：主役 Opus 4.8／敵対役 GPT-5.5／判定役 Gemini 3.1 Pro）で実施・完了。所見 16 件（判定 must-fix9／should-fix5／leave-as-is2、全 in_feature）を TDD で対処、tests/runtime 全テスト緑 143。初回の対象漏れ（RUNTIME.md）による偽陽性を再レビューで解消。RUNTIME.md 更新は post-write-verification（Google）で ALL_CLEAR。spec.json implementation.triad-review=true。コミット 3 件（`99c0471`／`43846f8`／`81cfc90`）push 済み。記録 [reviews/2026-06-02-implementation-triad-review.md](.reviewcompass/specs/runtime/reviews/2026-06-02-implementation-triad-review.md)
- **セッション48**：runtime implementation drafting（T-001〜T-011）を TDD 完了、テスト緑 351 件。foundation 6 語彙は `foundation_ref.py` 経由で参照のみ、runtime 所有 3 語彙確定。T-011 着手時に tasks 要件追跡の作業単位不整合（要件1・2・4・5・6・10）を発見し再オープン（4 過程、独立 1 体検証＋3 系統諮問）で解消。コミット 11 件（`02daa0a`〜`3810985`、push 済み）。記録 [session-48](docs/sessions/session-48-2026-06-02.md)
- セッション 47 以前（40 含む）の経緯は各 [session 記録](docs/sessions/)・git log・[docs/archive/todo/](docs/archive/todo/) のスナップショット参照

### 3.3 残作業の補完項目（任意・低優先）

- analysis 完全一致 15 件の人本人判定の遡及保存（`topic-{54〜75}-human.yaml` のうちセッション36未保存 15 件、詳細は git log）／実験ノート §5・§6 への追記（両軸2表構成・起草者バイアス検出の観察）

## 4. 関連参照

- 計画書 `docs/plan/reconstruction-plan-2026-05-21.md`／運営ガイド `docs/operations/SESSION_WORKFLOW_GUIDE.md`・`REOPEN_PROCEDURE.md`
- 雛形 `templates/`／持ち越し所見 `.reviewcompass/pending-cross-feature-findings.md`（未消化 0 件）
- 実験ノート `docs/experiments/n-model-comparison.md`／規律本体 `docs/disciplines/`（一覧は README.md）／セッション記録 `docs/sessions/`／過去 TODO snapshot `docs/archive/todo/`
