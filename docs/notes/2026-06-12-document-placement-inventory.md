---
date: 2026-06-12
record_type: document-placement-inventory
status: ready
placement_note: 本記録自体の置き場は暫定（利用者指示 2026-06-12「暫定的にdocs/notes/に配置」）。配置規約の決定後に正式な置き場へ従う。
---

# 文書配置の現状棚卸し（2026-06-12 実測）

## 目的と方法

ReviewCompass の開発過程で生成された文書の配置を体系化する議論（配置規約の策定）の段階 1 として、現状配置を実測した。すべて `git ls-files` による追跡情報とディスク実在の確認に基づく（実測時点：commit `b5f91a9d`、作業ツリー clean）。

背景：これまで「どこに何を書くか」を予め決めずに、必要になるたびに文書を配置してきたため整合性が取れていない。今後のデプロイ後は対象アプリ側での生成文書になるため、配置規約が必要（利用者提起 2026-06-12）。

追跡ファイル総数：3,624 件（`git ls-files` 実測、引用符付きパスを含む）。ルート直下のファイルは 6 件（`AGENTS.md`・`CLAUDE.md`・`TODO_NEXT_SESSION.md`・`deploy-manifest.yaml`・`pyproject.toml`・`.gitignore`）。

2026-06-12 の再精査（利用者指示「棚卸しに漏れがないかをチェック」）で、初版の数値訂正と漏れ 7 件を反映済み。

## 1. 製品コード（ルート直下に feature 名のパッケージとして同居）

| 場所 | 追跡件数 | 中身 |
| --- | --- | --- |
| `tools/` | 1,274 | 検査ツール・API 経路・conformance 評価などの本体。うち 1,205 件は `experiments/`（実験スクリプトと結果データ） |
| `analysis/` | 56 | feature 実装（Python・スキーマ） |
| `runtime/` | 55 | feature 実装（実行コード・プロンプト・設定雛形）。一部は配布対象 |
| `evaluation/` | 47 | feature 実装（metrics 抽出ほか） |
| `tests/` | 111 | テスト＋fixture。fixture 内に `.reviewcompass` 構造の複製が 4 件埋め込まれている。なおテストは `tools/api_providers/tests/`・`tools/experiments/tests/`（計 13 件）にもあり二重置き場（pyproject の testpaths が両方を指す） |
| `schemas/` | 2 | レビュー基準スキーマ |
| `config/` | 1 | API 設定（配布対象） |

## 2. `.reviewcompass/`（追跡 685 件＋無視 2 区画）

| 場所 | 件数 | 中身 |
| --- | --- | --- |
| `specs/` | 538 | feature 7 つ＋`_cross_feature`。正本（requirements/design/tasks/spec.json・implementation-drafting 等）は約 40 件のみ。残り約 500 件（93%）は証跡：`reviews/` 計 437 件（feature 別 4〜55、`_cross_feature` 291）、`conformance/` 計 19 件 |
| `post-write-verification/` | 140 | manifest 124 件と検証素材（raw/parsed）16 件が混在 |
| `post-write-review-runs/` | 7 | 書き込み後検証の review-run 1 件分。同種の run は `docs/notes/review-runs/` にもあり置き場が二重 |
| `approvals/` | 無視 | commit 承認記録（実行時状態） |
| `effective-prompts/` | 無視 | next 判定時の生成物（実測時 8 件） |

feature 別の specs 内訳（追跡件数）：`_cross_feature` 296、`workflow-management` 64、`conformance-evaluation` 54、`analysis` 52、`self-improvement` 45、`evaluation`・`foundation`・`runtime` 各 9。

## 3. `docs/`（1,302 件）

| 場所 | 件数 | 中身 |
| --- | --- | --- |
| `notes/` | 1,197 | うち 1,138 件（95%）は `review-runs/`（API レビュー生データ、124 run 分）。人が読む議論メモ・計画・checklist は直下 40 件（README 含む）、`post-write-verification-review/` 18 件、`archive/` 1 件（規律ドラフト保管） |
| `disciplines/` | 23 | 規律の正本 |
| `operations/` | 19 | 運用手引きの正本（NAVIGATION・SESSION_WORKFLOW_GUIDE・DISCIPLINE_MAP 等） |
| `experiments/` | 19 | 実験記録 4 件＋**`review-runs/` 2 run 分 14 件**（review-run の 3 つ目の置き場）。`n-model-comparison.md` §3.1 には API キー干渉の回避策など運用必須の知見も含まれる |
| `reviews/` | 17 | reopen 分類記録の**現行の置き場**（reopen-classification 15・intent-review 1・監査 1。2026-06-12 の 2 件を含み現役。`reopen-start` ツールと書き込み後検証の対象判定が名指しで参照） |
| `logs/` | 10＋無視 1 | 自律並列の計画・台帳（追跡）と `workflow-precheck.log`（無視） |
| `archive/` | 9 | 旧計画・旧 TODO・過去セッション記録の保管庫 |
| `sessions/` | 6 | セッション記録。35・45〜49 の 6 件のみ（セッション総数は 60 超） |
| その他 | 4 | `plan/` 1、`discipline-compliance-reports/` 2、`extraction-mapping.md` 1 |

## 4. その他のディレクトリ

- `stages/`（28）：手続き記録 25（`completed/` に reopen 系 14・maintenance 系 11、`in-progress/` は実測時 0）＋正本 3（`intent.yaml`・`feature-dependency.yaml`・`feature-partitioning/2026-05-24-proposal.md`）。**段集合 YAML は `intent.yaml` の 1 つだけ**で、requirements／design／tasks／implementation の段集合 YAML は存在しない（仕様 T-003 は 8 ファイルを要求。MLE-GAP-003 の既存 gap として記録済み）
- `learning/`（35）：実質は `workflow/` 29 件で **9 区画**（schemas 12・carry-forward-register 3・proposals 3・approved-updates 2・rejected-updates 2・rollback 2・metrics 2・replication-pilots 2・deployment-readiness 1）。`backtests/`・`findings/`・`templates/` は README と .gitkeep のみ
- `intent/`（4）：INTENT・DESIGN_PRINCIPLES・NON_GOALS・TRACEABILITY
- `templates/`（8）：配布対象の雛形（entry・hooks・specs・review・todo）
- `logs/`（ルート、2 件、追跡）：conformance 推定の `prompt.log`（書き手は `tools/conformance_evaluation/machine_verification.py`）
- `.claude/`・`.codex/`（各 3）：hook 配備先
- 無視区画：`build/`（配布物出力）・`.venv/`・`SES26/`（論文素材）・`reviewcompass.egg-info/`・`tools/experiments/logs/`

### repo 外の文書地点（再精査で追加）

- **Claude memory**：`~/.claude/projects/<本プロジェクト>/memory/`（`MEMORY.md`＋`archive/`）。2026-06-10 の縮退で規律の正本は repo 側へ移行済みだが、文書地点としては存続
- **セッション転写**：`~/.claude/projects/<本プロジェクト>/*.jsonl` に **46 セッション分**が Claude Code により自動保存されている（repo 外・共有不可・操縦 LLM 固有）。repo 内の `docs/sessions/` に人が読める形で反映されたのは 6 件のみ
- **利用者グローバル設定**：`~/.claude/CLAUDE.md`（全プロジェクト共通指示）

## 5. 機械が握るパス契約（配置変更の影響範囲）

ツール群がコード内で固定参照するパスは 40 種超。主要なもの：

- 書き込み後検証の対象判定：`TODO_NEXT_SESSION.md`、`docs/` 全域（`docs/archive/` と検査ログ `docs/logs/workflow-precheck.log` は除外、`docs/reviews/` は reopen-classification／audit 名のみ対象）
- feature 一覧の解決：`.reviewcompass/feature-dependency.yaml` → `stages/feature-dependency.yaml` → `feature-dependency.yaml` の探索順
- 手続き記録：`stages/in-progress/`・`stages/completed/` の `reopen-procedure-`／`maintenance-` 接頭辞
- 規律の正本参照：`docs/operations/`（WORKFLOW_NAVIGATION・WORKFLOW_DISCIPLINE_MAP・REOPEN_PROCEDURE）、`docs/disciplines/` の個別 3 ファイル（workflow_state_truth_source・approval_operation・post_write_verification）
- 証跡：`.reviewcompass/specs/`、`.reviewcompass/approvals/commit-approval.json`、`docs/notes/review-runs/`
- 学習資産：`learning/workflow/` 配下 5 パス（register・schemas・proposals・replication-pilots・deployment-readiness）
- intent：`intent/` の 4 ファイルを名指し
- 配布：`deploy-manifest.yaml` の許可一覧（`runtime/` の一部・`config/`・`templates/`・`tools/` 等）＋検査 4 種（許可一覧限定・開発証跡排除・配置非依存 lint・外部 root smoke）。「対象アプリへ行くもの」の事実上の正本

## 6. 議論の種になる実測上の気づき

1. 同種の文書が複数置き場に分裂している：review-run（API レビュー一式）の置き場が 3 箇所（`docs/notes/review-runs/` 124 run・`docs/experiments/review-runs/` 2 run・`.reviewcompass/post-write-review-runs/` 1 run）＋検証素材が `.reviewcompass/post-write-verification/` に混在。レビュー関連記録はほかに `.reviewcompass/specs/<feature>/reviews/`（証跡・ポインタ）と `docs/reviews/`（reopen 分類、現役）。ログは 3 箇所（ルート `logs/`・`docs/logs/`・`tools/experiments/logs/`〔無視〕）。テストも 2 箇所（`tests/`・`tools/*/tests/`）
2. 人が読む文書が機械の生データに埋没している：`docs/notes/` は 95% が生データで、議論メモ 39 件が 1,138 件の中にある
3. `.reviewcompass/specs/` の 93% が証跡で、正本置き場としての純度が低い（利用者指摘 1 の定量確認）
4. セッション記録は 6/60+ 件しか残っていない（利用者指摘 5 の定量確認）。一方で操縦 LLM 側の転写は repo 外に 46 セッション分が自動保存されており、「対話の生記録は存在するが、repo の共有可能な記録には反映されない」構造になっている
5. ツール配下に実験データ 1,205 件がある（`tools/experiments/`）
6. 非 ASCII ファイル名が 2 件ある（`docs/archive/past-sessions/ReviewCompass再設計.md`、`docs/notes/2026-05-24-conformance-evaluation-論点-a-b.md`）
7. `.reviewcompass/post-write-verification/` 内で manifest と検証素材が混在している
8. 運用に必須の知見が実験ノートにしか書かれていない実例：Claude Code が子プロセスの `GEMINI_API_KEY` 等を空文字列で上書きする干渉と回避策（`zsh -c 'source ~/.zshrc && ...'` 経由で起動、セッション 31 で動作確認済み）は `docs/experiments/n-model-comparison.md` §3.1 にのみ記録されており、書き込み後検証の手順正本（WORKFLOW_NAVIGATION・SESSION_WORKFLOW_GUIDE）から辿れない。本記録の検証実行時（2026-06-12）に操縦 LLM がこれを見落とし、検証が一度失敗した。配置と参照経路の不全が運用エラーを直接生んだ証左である
9. 書き込み後検証は事実主張を検証できない（検証機構の限界の実例）：本記録の初版には漏れ・誤り 11 件（事実誤認 2 件を含む）があったが、書き込み後検証（Gemini 1 体）を 2 回通過し所見ゼロだった。誤りは利用者指示の再精査で初めて発見された。検証役は文書テキストだけを受け取り、リポジトリの実態（正解データ）にアクセスできないため、文書としての整いは検査できても、実態との一致（事実検証）は構造的に検査できない。実態を主張する記録（棚卸し・サマリ等）の品質保証には、検証役へ実態アクセスを与えるか、機械的な実測の再現（コマンドの再実行照合）を組み込む別経路が必要である

## 7. 次段階

合意済みの進め方（2026-06-12）の段階 2 として、文書の分類軸（正本仕様／証跡記録／規律・運用／実行時生成物／セッション記録／学習資産／配布物）と「種別→置き場→ライフサイクル→検証→配布」の配置原則を議論する。利用者提起の論点 1〜6 と追加論点（パス契約の影響、開発リポジトリと対象アプリの二重基準、過去記録の保全方針、git 管理区分、命名・索引、検証義務との結合）をここで判断する。
