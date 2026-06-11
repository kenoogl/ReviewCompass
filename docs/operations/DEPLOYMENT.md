# DEPLOYMENT：クリーン配布方針

最終更新：2026-06-10（初期デプロイを自己テスト用の全機能検証セットとして定義）

本文書は ReviewCompass を外部アプリへ配置する前に、開発リポジトリ内の成果物をどのように整理し、配布対象をどう扱うかを定める運用方針である。現時点では、配布対象を開発リポジトリから削って作るのではなく、配布対象を明示して切り出す方式を採用する。

## 1. 基本方針

ReviewCompass の開発リポジトリには、実行に必要なファイル、仕様正本、研究証跡、レビュー記録、実験結果、作業メモが混在している。この状態のまま外部アプリへ配置すると、不要な履歴や開発専用ファイルが対象アプリへ混入する。

そのため、デプロイ前整理の目的は、開発リポジトリを即座に削減することではなく、次の 2 つを分けることである。

- **開発リポジトリ**：研究証跡、レビュー履歴、実験結果、作業メモを保持する。
- **配布物**：外部アプリで ReviewCompass を実行するために必要な最小ファイルだけを含む。

## 2. 初期デプロイ配布物 v0 の定義

初期デプロイ配布物 v0 は、第3者配布用の最小セットではなく、利用者本人がテスターとして実アプリに適用し、ReviewCompass の全機能を確認するための検証用セットとする。開発リポジトリ内にあるファイルを暗黙に含めず、配布 manifest で明示した allowlist のみを配布対象にする。

初期デプロイ配布物 v0 に含めるものは次の通り。

### 2.1 プロジェクト定義

| 配布パス | 理由 |
| --- | --- |
| `pyproject.toml` | Python 依存関係と最小プロジェクト情報を示すため。 |

### 2.2 runtime コア

| 配布パス | 理由 |
| --- | --- |
| `runtime/config/config.yaml.template` | 対象アプリ側 `.reviewcompass/config.yaml` の雛形。 |
| `runtime/config/terminology.yaml.template` | 対象アプリ側の用語設定雛形。 |
| `runtime/config/reviewcompass.yaml` | ReviewCompass 本体側の既定設定。 |
| `runtime/foundation/layer1_framework.yaml` | ReviewCompass 共通の評価軸定義。 |
| `runtime/foundation/metadata_contract.yaml` | 実行記録の共通メタデータ契約。 |
| `runtime/prompts/primary_detection/primary_reviewer.prompt.md` | 主役レビューの既定プロンプト。 |
| `runtime/prompts/adversarial_review/adversarial_reviewer.prompt.md` | 敵対役レビューの既定プロンプト。 |
| `runtime/prompts/judgment/judgment_reviewer.prompt.md` | 判定役レビューの既定プロンプト。 |
| `runtime/runtime_core/**/*.py` | review-run の実行、記録、検証、プロンプト解決に使う本体コード。 |
| `runtime/runtime_core/**/*.yaml` | runtime_core が参照する語彙、配置、スキーマ定義。 |
| `runtime/schemas/*.schema.json` | runtime の出力・観測記録の JSON Schema。 |
| `runtime/validators/contracts/*.schema.json` | validator 結果などの検証契約。 |

### 2.3 review-run API 実行部

| 配布パス | 理由 |
| --- | --- |
| `tools/api_providers/__init__.py` | Python package として読み込むため。 |
| `tools/api_providers/config_loader.py` | API 設定の読み込みに必要。 |
| `tools/api_providers/providers.py` | 各 provider 呼び出しに必要。 |
| `tools/api_providers/response_formatter.py` | レビュー応答の整形に必要。 |
| `tools/api_providers/review_triage.py` | review-run の所見整理に必要。 |
| `tools/api_providers/run_review.py` | review-run の CLI 入口。 |
| `tools/api_providers/run_role.py` | 役単位の CLI 入口。 |
| `tools/api_providers/prompt_templates/*.md` | provider 別の API 呼び出しプロンプト。 |
| `config/api-settings.yaml` | 利用者本人の初期デプロイ検証で、既存の API / CLI 経路設定をそのまま確認するため。 |

`config/api-settings.yaml` は初期デプロイ検証では含める。ただし、同ファイルには API key、token、password などの秘密値を置かず、秘密値は実行環境の環境変数など配布物外で扱う。第3者配布では、経緯コメントや検証用 variant を除いた API 設定テンプレートを別途作成し、そのテンプレートへ差し替える。

### 2.4 conformance-evaluation

| 配布パス | 理由 |
| --- | --- |
| `tools/conformance-evaluation-check.py` | conformance-evaluation の CLI 入口。 |
| `tools/conformance-evaluation-cross-feature.py` | 機能横断 conformance-evaluation の CLI 入口。 |
| `tools/conformance_evaluation/*.py` | conformance-evaluation の本体コード。 |
| `tools/conformance_evaluation/schemas/*.schema.json` | evaluation record と intent diff の検証に必要。 |
| `schemas/review-criteria/conformance_evaluation.yaml` | conformance-evaluation の評価基準。 |

### 2.5 workflow-management

| 配布パス | 理由 |
| --- | --- |
| `tools/check-workflow-action.py` | workflow state と不可逆操作前検査の CLI 入口。 |
| `tools/document_link_lint.py` | 正本文書・規律文書の参照検査に必要。 |
| `tools/deployment_independence_lint.py` | 配置非依存性の検査に必要。 |
| `tools/guarded-git-commit.py` | commit 操作を workflow-management の検査に通すため。 |
| `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml` | 判定点ごとの必読プロンプト対応を機械判定するため。 |
| `docs/operations/WORKFLOW_NAVIGATION.md` | workflow navigation の正本手順。 |
| `docs/operations/WORKFLOW_PRECHECK.md` | 事前検査の運用手順。 |
| `docs/operations/WORKFLOW_PRECHECK_DETAILS.md` | 事前検査の詳細仕様。 |
| `docs/operations/REOPEN_PROCEDURE.md` | reopen 手続きの正本手順。 |
| `docs/operations/SESSION_WORKFLOW_GUIDE.md` | 作業完了時レポート契約と review-run 処理手順。 |
| `docs/disciplines/discipline_*.md` | workflow-management が判定時に読む規律文書。 |
| `.reviewcompass/specs/workflow-management/post-write-verification-spec.yaml` | 書き込み後検証の動作仕様。 |
| `.reviewcompass/specs/workflow-management/yaml-audit-spec.yaml` | YAML 監査の動作仕様。 |

`tools/check-workflow-action.py` には ReviewCompass 開発リポジトリ自身の feature order や carry-forward register 依存が残っている。そのため初期デプロイでは、汎用配布物としてではなく、利用者本人による実アプリ検証で依存箇所を発見する対象として含める。

### 2.6 self-improvement

| 配布パス | 理由 |
| --- | --- |
| `tools/self-improvement-check.py` | self-improvement の機械検査 CLI 入口。 |
| `tools/self_improvement/*.py` | 改善提案、carry-forward、承認済み更新の検査に必要。 |
| `tools/self_improvement/schemas/*.schema.json` | self-improvement 記録の検証に必要。 |
| `learning/workflow/schemas/*.schema.json` | self-improvement が読む workflow 改善用の正本 schema。 |
| `learning/workflow/proposals/README.md` | 改善提案の配置先を初期デプロイで確認するため。 |
| `learning/workflow/approved-updates/README.md` | 承認済み改善の配置先を初期デプロイで確認するため。 |
| `learning/workflow/rejected-updates/README.md` | 却下済み改善の配置先を初期デプロイで確認するため。 |
| `learning/workflow/rollback/README.md` | ロールバック記録の配置先を初期デプロイで確認するため。 |
| `learning/workflow/metrics/README.md` | 効果測定記録の配置先を初期デプロイで確認するため。 |
| `learning/workflow/carry-forward-register/README.md` | 持ち越し台帳の配置先を初期デプロイで確認するため。 |
| `learning/workflow/carry-forward-register/reviewcompass-import.yaml` | 現行の持ち越し台帳処理を検証するため。 |

### 2.7 analysis / evaluation

| 配布パス | 理由 |
| --- | --- |
| `analysis/` | ReviewCompass の分析機能を実アプリ上で確認するため。 |
| `evaluation/` | ReviewCompass の評価機能を実アプリ上で確認するため。 |

### 2.8 対象アプリ側生成テンプレート

| 配布パス | 理由 |
| --- | --- |
| `templates/specs/spec.json.template` | 対象アプリ側 `.reviewcompass/specs/<feature>/spec.json` の雛形。 |
| `templates/specs/feature-dependency.yaml.template` | 対象アプリ側 `.reviewcompass/feature-dependency.yaml`（feature 一覧・開発順・依存）の雛形。 |
| `templates/review/manual_dogfooding_review_template.md` | 初期デプロイで手動 review-run を記録するため。 |
| `templates/todo/TODO_NEXT_SESSION.template.md` | 初期デプロイ中のセッション引き継ぎを確認するため。 |
| `templates/entry/AGENT_ENTRY.template.md` | 対象アプリ側 `.reviewcompass/AGENT_ENTRY.md`（複数 LLM 共通のセッション入口規律）の雛形。 |
| `templates/hooks/pre-bash-precheck.sh.template` | 対象アプリ側 commit／push 事前検査 hook の雛形（初期設定時に絶対パスへ置換）。 |
| `templates/hooks/claude-settings.json.template` | 対象アプリ側 `.claude/settings.json` への hook 登録の雛形。 |
| `templates/hooks/codex-hooks.json.template` | 対象アプリ側 `.codex/hooks.json` の雛形。 |

## 3. 初期デプロイ配布物 v0 に含めないもの

次のファイル群は、初期デプロイ配布物 v0 に含めない。

- `AGENTS.md`
- `.codex/`
- `.claude/`
- `docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md`・`WORKFLOW_NAVIGATION_FOR_CODEX.md`（開発リポジトリ専用の手引き。対象アプリ側の入口は `templates/entry/` から実体化する AGENT_ENTRY が担うため、意図的に配布しない）
- `.reviewcompass/post-write-verification/`
- `.reviewcompass/effective-prompts/`
- `.reviewcompass/approvals/`
- `.reviewcompass/specs/*/reviews/`
- `.reviewcompass/specs/*/conformance/`
- `.reviewcompass/specs/_cross_feature/`
- `docs/notes/`
- `docs/archive/`
- `docs/plan/`
- `docs/sessions/`
- `docs/reviews/`
- `docs/experiments/`
- `docs/logs/`
- `docs/discipline-compliance-reports/`
- `tools/experiments/`
- `tools/**/tests/`
- `tests/`
- `learning/workflow/carry-forward-register/sources/`
- `learning/workflow/deployment-readiness/`
- `learning/workflow/replication-pilots/`
- `logs/`
- `SES26/`

`.reviewcompass/specs/` は、初期デプロイ配布物には workflow-management の動作仕様 YAML だけを含める。ReviewCompass 自身の要件、設計、タスク、レビュー記録、conformance 証跡は、対象アプリ側へ持ち込まない。

`learning/workflow/` は、初期デプロイ配布物には self-improvement の実行に必要な配置先 README、schema、現行 carry-forward register だけを含める。deployment-readiness、replication-pilots、carry-forward register の source 文書は開発証跡として除外する。

これらは不要物として直ちに削除するのではなく、研究証跡または開発履歴として開発リポジトリに保持する。削除、別リポジトリ分離、アーカイブ移動は、配布 manifest と配布物生成が安定した後に判断する。

## 4. 第3者配布で再検討するもの

初期デプロイ配布物 v0 は利用者本人の検証用であり、第3者配布用の最終形ではない。第3者配布時には、次の配布単位を再検討する。

| 配布単位 | 候補 | 条件 |
| --- | --- | --- |
| workflow-management 汎用実行部 | `check-workflow-action.py` 相当、`WORKFLOW_DISCIPLINE_MAP.yaml` 相当、規律文書 | 初期デプロイで発見した ReviewCompass 開発リポジトリ固有依存を外す。 |
| LLM 別 adapter 一式 | 入口正本テンプレート（`templates/entry/`）、hook テンプレート（`templates/hooks/`）、操縦 LLM 別の API 既定 variant（`config/api-settings.yaml` の `*_codex_operator` 系等） | 初期デプロイ版は Claude Code と Codex CLI に対応済み（設計記録 `docs/notes/2026-06-10-deployment-multi-llm-entry-design.md`）。第3者配布では、操縦 LLM の追加（例：Gemini 操縦時の variant）、LLM 別注意のファイル分離、開発リポジトリ用手引き（`WORKFLOW_NAVIGATION_FOR_CLAUDE.md`／`FOR_CODEX.md`）の扱いを再検討する。 |
| 開発者向け検査 | `tools/document_link_lint.py`、`tools/deployment_independence_lint.py` | 配布物生成側の CI または開発者向け pack として追加する。 |
| 第3者配布用 API 設定テンプレート | `config/api-settings.yaml` から経緯コメントや検証用 variant を除いたテンプレート | 初期デプロイ検証では現行 `config/api-settings.yaml` を使い、第3者配布時に差し替える。 |
| 第3者向け最小コア | runtime、review-run、conformance-evaluation の最小セット | 全機能検証後、不要機能を除いて再定義する。 |

## 5. 配布物生成

外部アプリ pilot や本格デプロイでは、開発リポジトリをそのまま使わない。manifest で許可されたファイルだけを、一時的な配布ディレクトリにコピーして使う。

想定する流れは次の通り。

1. `deploy-manifest.yaml` を読む。
2. `tools/build-deploy-package.py --clean --verify` で、許可されたファイルだけを `build/deploy/ReviewCompass/` などへコピーする。
3. `--verify` で、allowlist 外ファイル、exclude 対象ファイル、欠落ファイルがないことを機械検査する。
4. `--smoke-external-app-root <外部アプリroot>` で、配布物だけを使って外部アプリ root の `.reviewcompass/specs/<feature>/reviews/` へ review-run 成果物を書けることを確認する。
5. 実アプリ pilot は、この生成済み配布物を使って実施する。

配布物生成時に、開発リポジトリ側の workflow state や仕様状態を変更してはならない。

## 6. 外部アプリ側の扱い

外部アプリの git リポジトリには、アプリ側状態だけを置く。

外部アプリ側に生成または更新される候補は次の通り。

- `<対象アプリ>/.reviewcompass/config.yaml`
- `<対象アプリ>/.reviewcompass/AGENT_ENTRY.md`（複数 LLM 共通の入口規律。テンプレートから実体化）
- `<対象アプリ>/.reviewcompass/feature-dependency.yaml`（feature 一覧・開発順・依存）
- `<対象アプリ>/.reviewcompass/specs/<feature>/requirements.md`
- `<対象アプリ>/.reviewcompass/specs/<feature>/design.md`
- `<対象アプリ>/.reviewcompass/specs/<feature>/tasks.md`
- `<対象アプリ>/.reviewcompass/specs/<feature>/spec.json`
- `<対象アプリ>/.reviewcompass/specs/<feature>/reviews/`
- `<対象アプリ>/CLAUDE.md`・`AGENTS.md`（入口への参照 1 行の追記）
- `<対象アプリ>/.claude/settings.json`・`.claude/hooks/`（commit／push 事前検査 hook）
- `<対象アプリ>/.codex/hooks.json`・`.codex/hooks/`（同上）

これらは対象アプリの仕様、状態、レビュー記録であり、対象アプリ側 git リポジトリの変更として扱う。ReviewCompass 側の開発証跡、実験ログ、過去 review-run 記録は対象アプリ側へ持ち込まない。

## 7. 第3者への配布

第3者へ ReviewCompass を配布するときは、対象アプリごとに GitHub 上で ReviewCompass リポジトリを fork させる方式を標準にしない。標準は、ReviewCompass 開発リポジトリから生成したクリーン配布物を渡す方式とする。

配布形式は、初期段階では zip / tarball / GitHub Release asset のいずれかを想定する。将来、運用が安定した段階で PyPI package や専用 installer に移行してよい。

第3者側の導入手順は次の形を基本とする。

1. ReviewCompass の配布物を取得する。
2. 配布物を展開する、または package として install する。
3. 対象アプリの git リポジトリで ReviewCompass を実行する。
4. 対象アプリ側に `.reviewcompass/config.yaml` と `.reviewcompass/specs/` を生成または更新する。
5. 対象アプリ側の判断で `.reviewcompass/` 配下の変更を commit / push する。

ReviewCompass 本体を改変したい場合は、第3者の対象アプリ repo 内で個別 fork を増やすのではなく、ReviewCompass 開発リポジトリに対する issue / pull request / patch 提案として扱う。

## 8. 2 つの git リポジトリの責務

デプロイ時は、ReviewCompass 側リポジトリと対象アプリ側リポジトリを分けて扱う。

| リポジトリ | 主な責務 | 変更されるもの |
| --- | --- | --- |
| ReviewCompass 側 | ツール本体、既定設定、スキーマ、テンプレート、プロンプト、配布物生成 | 配布 manifest、ツール実装、正本資産 |
| 対象アプリ側 | アプリ固有の仕様、状態、レビュー記録、上書き設定 | `.reviewcompass/config.yaml`、`.reviewcompass/specs/` |

対象アプリで ReviewCompass を実行しても、ReviewCompass 側リポジトリの workflow state を暗黙に変更しない。対象アプリ側に生成された `.reviewcompass/` 配下の変更を commit / push するかは、対象アプリ側の運用判断として扱う。

## 9. 機械チェック

配布物には、次の機械チェックを設ける。

- allowlist 外のファイルが配布物に含まれていないこと。
- `docs/notes/`、`tools/experiments/`、`.reviewcompass/post-write-verification/` などの非配布対象が混入していないこと。
- 絶対パス、固定ユーザパス、開発リポジトリ固有パスが配布対象に混入していないこと。
- 配布物だけで最小 smoke test が通ること。
- 外部アプリ root の `.reviewcompass/specs/` を読み書きできること。

`tools/deployment_independence_lint.py` は、絶対パスや配置非依存性の検査に使う。`tools/build-deploy-package.py --verify` は、配布 manifest と組み合わせて、配布物そのものの混入検査を行う。

## 10. 当面の次作業

1. 実アプリ pilot で使う外部アプリ root を決める。
2. `config/api-settings.yaml` に秘密値が含まれていないことを確認する。
3. `tools/build-deploy-package.py --clean --verify --smoke-external-app-root <外部アプリroot>` を実アプリ用の一時 root で実行する。
4. 実アプリ pilot では、開発リポジトリではなく生成済み配布物を使う。
5. pilot で見つかった ReviewCompass 開発リポジトリ固有依存を、第3者配布前の修正候補として記録する。

この順序により、開発リポジトリの研究証跡を失わずに、外部アプリへ渡す ReviewCompass を小さく、説明可能で、検査可能な状態にする。
