# Agentic Flow 論文から ReviewCompass へ取り込む実装計画

作成日：2026-06-11

## 1. 位置づけ

本文書は、Agentic Flow 論文のうち ReviewCompass に有用な設計原則を、仕様駆動開発の手順で取り込むための計画メモである。正本の要件・設計・タスクを直接置き換えるものではない。正本を変更する場合は reopen 手続きに乗せる。

取り込む対象は Agentic Flow ライブラリそのものではなく、次の設計原則である。

1. 宣言と実行の分離。
2. 実行点の明示。
3. フェーズ境界による一時作業、証跡、正本更新の分離。
4. 副作用のある操作を実行前に列挙し、機械検査できる形にすること。

## 2. ReviewCompass での採用方針

ReviewCompass では、Agentic Flow の `ExecutionSpec` に相当する概念を、まず review-run と workflow action に限定して導入する。いきなり全機能を共通抽象に置き換えない。

採用する概念：

| Agentic Flow の考え方 | ReviewCompass での対応 |
| --- | --- |
| `agent(prompt)` は即実行せず仕様を返す | review-run 実行前に `ReviewExecutionSpec` 相当の計画を生成する |
| `await` だけが実行点 | API 呼び出し、manifest 生成、workflow state 更新、commit、push を副作用実行点として明示する |
| `phase()` で境界を作る | `scratch`、`evidence`、`canonical_update`、`approval_gate` の作業境界を区別する |
| `.stream()` などの修飾子は仕様を変えるだけ | 実行オプションは実行前 spec に記録し、実行時に確定済み入力として扱う |

採用しないもの：

- Agentic Flow ライブラリへの依存。
- Python の `await` 構文そのものを ReviewCompass 全体のワークフロー DSL にすること。
- 既存の workflow-management 判定モデルを置き換えること。

## 3. 機能境界

### 3.1 runtime

`runtime` は、review-run の宣言と実行の分離を担当する。

追加候補：

- review-run 実行前に、対象ファイル、phase、criteria、variant、provider、model、prompt、出力先、想定書き込みファイルを列挙する実行仕様を生成する。
- 実行仕様は API 呼び出し前に保存または表示できる。
- 実行後の `rounds.yaml`、`target-manifest.yaml`、`model-result-summary.yaml` は、実行仕様と対応付けられる。
- 実行仕様と実際の出力が食い違う場合は、無効実行または要確認として扱う。

### 3.2 workflow-management

`workflow-management` は、副作用のある操作の事前検査と不可逆ゲートを担当する。

追加候補：

- `next`、`commit`、`push`、`reopen-start` などの判定点で、実行前に読むファイル、書くファイル、更新する状態を列挙する。
- commit / push / spec.json 更新 / manifest 生成を `state_mutation` として明示する。
- 実行前 spec に含まれないファイルが更新された場合、commit precheck で検出する。
- `post_write_verification`、`yaml_audit`、`reopen` などの side track を phase 境界として扱い、本線 workflow と混同しない。

### 3.3 foundation

`foundation` は、共通語彙や schema が必要になった場合だけ変更する。

追加候補：

- `effect_kind` 語彙：`read`、`write`、`state_mutation`、`external_call`、`irreversible_action`。
- `phase_boundary` 語彙：`scratch`、`evidence`、`canonical_update`、`approval_gate`。

ただし、最初から foundation を変更すると波及が大きい。初期実装では `runtime` と `workflow-management` の局所 schema として始め、共通化が必要になった時点で foundation reopen を検討する。

## 4. 仕様駆動開発の進め方

### Step 0：計画メモ作成

- [x] Agentic Flow 論文の要点を ReviewCompass 観点で整理する。
- [x] 採用する原則と採用しない範囲を分ける。
- [x] 変更候補の feature 境界を仮決めする。

### Step 1：reopen 分類

- [ ] 本件を正本変更に進めるか利用者判断を得る。
- [ ] `runtime`、`workflow-management`、必要なら `foundation` の feature impact を判定する。
- [ ] `docs/reviews/reopen-classification-<日付>.md` を作成する。
- [ ] `stages/in-progress/reopen-procedure-<日付>.yaml` を作成する。
- [ ] 該当 feature の `spec.json` を reopen 状態にする。

想定分類：

| feature | 想定判断 | 理由 |
| --- | --- | --- |
| runtime | `reopen_existing_feature` | review-run 実行前仕様と実行点明示は runtime の実行制御に属する |
| workflow-management | `reopen_existing_feature` | 副作用事前検査と不可逆ゲートは workflow-management の責務 |
| foundation | `indirect_check_only` から開始 | 共通語彙化が必要になった場合のみ direct impact |
| evaluation | `indirect_check_only` | 実行仕様と実行結果の差分評価を将来消費する可能性はあるが、初期実装の所有者ではない |
| analysis | `indirect_check_only` | 論文用分析では有用だが、初期実装の所有者ではない |
| self-improvement | `indirect_check_only` | 改善提案の証跡として利用できるが、初期実装の所有者ではない |
| conformance-evaluation | `indirect_check_only` | 実行仕様と正本の整合確認に利用できるが、初期実装の所有者ではない |

### Step 2：requirements 更新

runtime requirements への追加候補：

- review-run 実行前仕様を生成できること。
- 実行仕様は、入力、外部呼び出し、出力先、想定生成物を含むこと。
- 実行仕様なしの API 実行を通常経路にしないこと。
- 実行仕様と実行結果を対応付けること。

workflow-management requirements への追加候補：

- 副作用のある workflow action は、実行前に読み取り・書き込み・状態更新・不可逆操作を列挙すること。
- commit precheck は、実行前 spec または承認レコードの範囲外にある staged 変更を遮断すること。
- side track と本線 workflow を phase 境界として区別すること。

### Step 3：design 更新

runtime design への追加候補：

- `ReviewExecutionSpec` または同等の YAML schema。
- spec 生成、spec 確認、実行、結果保存、close validation の順序。
- `rounds.yaml` と spec の対応関係。

workflow-management design への追加候補：

- `ActionEffectSpec` または同等の効果列挙 schema。
- `next` / `commit` / `push` / `reopen-start` の効果列挙。
- commit approval record と staged sha256 の関係を、効果列挙の一部として整理。

### Step 4：tasks 更新

タスクは TDD 前提で分ける。

1. runtime の実行前 spec schema テストを追加する。
2. review-run が spec を生成するテストを追加する。
3. review-run の出力が spec と対応するテストを追加する。
4. workflow action の effect spec schema テストを追加する。
5. commit precheck が effect spec 外変更を遮断するテストを追加する。
6. side track phase 境界の記録テストを追加する。
7. deploy package に必要な schema / docs が含まれることを確認する。

### Step 5：実装

実装は、テストを先に作成して失敗を確認してから進める。

初期実装の最小単位：

1. `runtime` 側に review-run 実行前 spec の schema と writer を追加する。
2. `run_review.py` が spec を保存し、その spec を `rounds.yaml` から参照する。
3. `workflow-management` 側に action effect spec の schema または出力関数を追加する。
4. `check-workflow-action.py next --json` が主要判定点で効果情報を返す。

## 5. 完了条件

初期実装の完了条件：

- review-run の前に、実行仕様が機械可読に生成される。
- 実行仕様に、読むもの、外部呼び出し、書くもの、更新する状態が含まれる。
- review-run 記録から、どの実行仕様で実行したか追跡できる。
- workflow action の主要な副作用が `next --json` または commit precheck の出力で確認できる。
- 既存の workflow-management、runtime、post-write verification、deploy package の検査が通る。

## 6. 注意点

- 本件は便利な抽象化の追加ではなく、副作用管理と証跡再現性の強化として扱う。
- 既存の requirements / design / tasks を大きく書き換えない。必要な追加に留める。
- 共通語彙化は急がない。局所実装で重複や不整合が見えた時点で foundation へ昇格する。
- 実行仕様を作っただけで安全になるわけではない。commit precheck や post-write verification と接続して初めて意味がある。
