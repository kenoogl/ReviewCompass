# DEPLOYMENT：クリーン配布方針

最終更新：2026-06-09（開発証跡と配布対象が混在した現状から、クリーンな配布物を生成する方針を記録）

本文書は ReviewCompass を外部アプリへ配置する前に、開発リポジトリ内の成果物をどのように整理し、配布対象をどう扱うかを定める運用方針である。現時点では、配布対象を開発リポジトリから削って作るのではなく、配布対象を明示して切り出す方式を採用する。

## 1. 基本方針

ReviewCompass の開発リポジトリには、実行に必要なファイル、仕様正本、研究証跡、レビュー記録、実験結果、作業メモが混在している。この状態のまま外部アプリへ配置すると、不要な履歴や開発専用ファイルが対象アプリへ混入する。

そのため、デプロイ前整理の目的は、開発リポジトリを即座に削減することではなく、次の 2 つを分けることである。

- **開発リポジトリ**：研究証跡、レビュー履歴、実験結果、作業メモを保持する。
- **配布物**：外部アプリで ReviewCompass を実行するために必要な最小ファイルだけを含む。

## 2. 配布対象の定義

配布対象は、将来 `deploy-manifest.yaml` のような機械可読 manifest で明示する。manifest には、配布物へ含めるパスを allowlist として列挙する。

現時点で配布対象は未確定である。以下は確定リストではなく、精査を始めるための分類である。`runtime/`、`schemas/`、`templates/`、`config/`、`docs/operations/` のようなディレクトリ全体を、そのまま配布対象にしてはならない。

### 2.1 最小コア候補

最小コア候補は、外部アプリ root を読んで、対象アプリ側 `.reviewcompass/` を扱うために直接必要となる可能性が高いものに限定する。

- workflow navigation の実行入口。
- 対象アプリ側 `.reviewcompass/specs/` を読むための最小コード。
- 対象アプリ側 `.reviewcompass/config.yaml` を読むための最小設定雛形。
- 実行時に必須となる最小 schema。

### 2.2 要審査候補

次は配布対象に含める可能性はあるが、ファイル単位で必要性を確認してから allowlist に入れる。

- `tools/api_providers/` のうち、第3者配布時に実行される入口と依存モジュール。
- `tools/conformance_evaluation/` のうち、外部アプリで必要なサブコマンドに直結するもの。
- `runtime/` のうち、プロンプト解決、設定解決、schema 参照に必要なもの。
- `.reviewcompass/specs/` 配下のうち、動作仕様として実行時に参照される YAML。
- `docs/operations/` のうち、配布後の利用者が読む最小運用文書。

### 2.3 原則除外

次は、明示的な例外判断がない限り配布対象に含めない。

- ディレクトリ全体としての `docs/operations/`
- ディレクトリ全体としての `runtime/`
- ディレクトリ全体としての `schemas/`
- ディレクトリ全体としての `templates/`
- ディレクトリ全体としての `config/`

配布対象は allowlist で決める。開発リポジトリに存在するファイルを、暗黙に配布対象とはみなさない。allowlist に入れる各ファイルには、配布時に必要な理由を記録する。

## 3. 非配布対象の分類

次のファイル群は、原則として配布物へ含めない。

- `docs/notes/`
- `docs/archive/`
- `docs/plan/`
- 現行の `docs/operations/WORKFLOW_PRECHECK.md`
- 現行の `docs/operations/SESSION_WORKFLOW_GUIDE.md`
- `tools/experiments/`
- `logs/`
- `.reviewcompass/post-write-verification/`
- 過去の review-run の raw / parsed / triage 記録
- 論文用、dogfooding 用、開発検証用の証跡

これらは不要物として直ちに削除するのではなく、研究証跡または開発履歴として開発リポジトリに保持する。削除、別リポジトリ分離、アーカイブ移動は、配布 manifest と配布物生成が安定した後に判断する。

## 4. 配布物生成

外部アプリ pilot や本格デプロイでは、開発リポジトリをそのまま使わない。manifest で許可されたファイルだけを、一時的な配布ディレクトリにコピーして使う。

想定する流れは次の通り。

1. `deploy-manifest.yaml` を読む。
2. 許可されたファイルだけを `build/deploy/ReviewCompass/` などへコピーする。
3. 配布物ディレクトリ内で smoke test を実行する。
4. 配布物に非配布対象が混入していないことを機械検査する。
5. 外部アプリ pilot は、この配布物を使って実施する。

配布物生成時に、開発リポジトリ側の workflow state や仕様状態を変更してはならない。

## 5. 外部アプリ側の扱い

外部アプリの git リポジトリには、アプリ側状態だけを置く。

外部アプリ側に生成または更新される候補は次の通り。

- `<対象アプリ>/.reviewcompass/config.yaml`
- `<対象アプリ>/.reviewcompass/specs/<feature>/requirements.md`
- `<対象アプリ>/.reviewcompass/specs/<feature>/design.md`
- `<対象アプリ>/.reviewcompass/specs/<feature>/tasks.md`
- `<対象アプリ>/.reviewcompass/specs/<feature>/spec.json`
- `<対象アプリ>/.reviewcompass/specs/<feature>/reviews/`

これらは対象アプリの仕様、状態、レビュー記録であり、対象アプリ側 git リポジトリの変更として扱う。ReviewCompass 側の開発証跡、実験ログ、過去 review-run 記録は対象アプリ側へ持ち込まない。

## 6. 第3者への配布

第3者へ ReviewCompass を配布するときは、対象アプリごとに GitHub 上で ReviewCompass リポジトリを fork させる方式を標準にしない。標準は、ReviewCompass 開発リポジトリから生成したクリーン配布物を渡す方式とする。

配布形式は、初期段階では zip / tarball / GitHub Release asset のいずれかを想定する。将来、運用が安定した段階で PyPI package や専用 installer に移行してよい。

第3者側の導入手順は次の形を基本とする。

1. ReviewCompass の配布物を取得する。
2. 配布物を展開する、または package として install する。
3. 対象アプリの git リポジトリで ReviewCompass を実行する。
4. 対象アプリ側に `.reviewcompass/config.yaml` と `.reviewcompass/specs/` を生成または更新する。
5. 対象アプリ側の判断で `.reviewcompass/` 配下の変更を commit / push する。

ReviewCompass 本体を改変したい場合は、第3者の対象アプリ repo 内で個別 fork を増やすのではなく、ReviewCompass 開発リポジトリに対する issue / pull request / patch 提案として扱う。

## 7. 2 つの git リポジトリの責務

デプロイ時は、ReviewCompass 側リポジトリと対象アプリ側リポジトリを分けて扱う。

| リポジトリ | 主な責務 | 変更されるもの |
| --- | --- | --- |
| ReviewCompass 側 | ツール本体、既定設定、スキーマ、テンプレート、プロンプト、配布物生成 | 配布 manifest、ツール実装、正本資産 |
| 対象アプリ側 | アプリ固有の仕様、状態、レビュー記録、上書き設定 | `.reviewcompass/config.yaml`、`.reviewcompass/specs/` |

対象アプリで ReviewCompass を実行しても、ReviewCompass 側リポジトリの workflow state を暗黙に変更しない。対象アプリ側に生成された `.reviewcompass/` 配下の変更を commit / push するかは、対象アプリ側の運用判断として扱う。

## 8. 機械チェック

配布物には、次の機械チェックを設ける。

- allowlist 外のファイルが配布物に含まれていないこと。
- `docs/notes/`、`tools/experiments/`、`.reviewcompass/post-write-verification/` などの非配布対象が混入していないこと。
- 絶対パス、固定ユーザパス、開発リポジトリ固有パスが配布対象に混入していないこと。
- 配布物だけで最小 smoke test が通ること。
- 外部アプリ root の `.reviewcompass/specs/` を読み書きできること。

既存の `tools/deployment_independence_lint.py` は、絶対パスや配置非依存性の検査に使える。今後は、配布 manifest と組み合わせて、配布物そのものの混入検査にも拡張する。

## 9. 当面の次作業

1. `deploy-manifest.yaml` の形式を決める。
2. 最小コア候補と要審査候補をファイル単位で棚卸しする。
3. 各ファイルについて、配布時に必要な理由を manifest に記録する。
4. manifest に基づく配布物生成スクリプトを作る。
5. 非配布対象の混入を検出するテストを追加する。
6. 配布物だけで外部アプリ root に対する smoke test を実行する。
7. 実アプリ pilot では、開発リポジトリではなく生成済み配布物を使う。

この順序により、開発リポジトリの研究証跡を失わずに、外部アプリへ渡す ReviewCompass を小さく、説明可能で、検査可能な状態にする。
