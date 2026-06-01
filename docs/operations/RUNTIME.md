# RUNTIME：実行時機能の運用文書

最終更新：2026-06-02（runtime 実装 T-001：§9 実行ディレクトリ配置と運用ルールを追記）／2026-05-22（フェーズ 1 抽出、requirements 部分のみの骨子）

本文書は ReviewCompass の `runtime`（実行時機能）の運用上の役割と契約を解説する。形式仕様は [.reviewcompass/specs/runtime/requirements.md](../../.reviewcompass/specs/runtime/requirements.md) を参照する。本文書は読み手向けの解説、仕様文書は機械検査と仕様駆動手続きの正本という関係。

## 1. 役割

`runtime` は `foundation` が定義する共通契約（4 段論理契約、5 共有スキーマ、3 役抽象名、検証器メタデータ）の上で、実際のレビュー実行を担う機能である。`foundation` は契約のみで実行を持たないが、`runtime` は契約に従って実際にレビューを動かす。

具体的には：

- **レビュー実行制御**：Step A（主役検出）→ B（敵対レビュー）→ C（判定）→ D（統合）の 4 段を実行
- **処理方式の対応**：`primary`／`adversarial`／`judgment` の 3 処理方式を支える（計画書 §5.15.6 で命名統一）
- **プロンプト解決**：リポジトリ内配置からプロンプトを版付きで読み込む
- **構造化証拠の出力**：`foundation` の 5 スキーマに準拠した実行記録を出力
- **人間決定の組み込み**：承認・却下・保留の決定単位を提示し、人間署名を必須化
- **検証器連携**：実行終了時に機械検査を呼び出し、有効・無効を分離
- **再生（replay）対応**：過去実行を機械的に再現可能な記録形式を保持
- **フェーズ対応**：意図／要件／設計／タスクの各フェーズで強調点を切り替える
- **可搬な証拠束の輸出**：他環境への取り込みに必要な来歴情報を含む輸出を支える

## 2. 設計の根本姿勢

- **`foundation` 契約の遵守**：4 段、3 役、5 スキーマ、メタデータ語彙を `foundation` から取り込み、再定義しない
- **状態機械の不変性**：処理方式やフェーズプロファイルが変わっても、概念上の状態機械は同一
- **証拠の構造化と分離**：生の証拠と派生要約を分離し、下流の `evaluation`／`self-improvement` が機械的に消費可能にする
- **人間決定の明示**：署名・却下・保留を黙示にせず、決定単位として明示する
- **検証器による有効性の機械分離**：実行終了時に検査を呼び、無効実行を下流に渡さない

## 3. 10 の要件領域（要約）

| 要件 | 領域 | 何を定めるか |
|---|---|---|
| Requirement 1 | レビュー実行制御 | Step A／B／C／D の実行、段遷移の明示、実行終了境界 |
| Requirement 2 | 処理方式対応の実行 | `primary`／`adversarial`／`judgment` の 3 方式、各方式の段集合 |
| Requirement 3 | プロンプト解決と版追跡 | リポジトリ内解決、版同一性、役別・段別の区別 |
| Requirement 4 | 構造化された証拠の出力 | スキーマ準拠、`counter_status` 出力、レビューモード由来情報 |
| Requirement 5 | 人間決定の組み込み | 決定単位、署名必須、黙示自動採用の禁止 |
| Requirement 6 | 検証器連携と実行終了 | 検証器呼び出し、無効化マーカー、署名 → 検証 → 終了の順序強制 |
| Requirement 7 | 再生対応の実行時記録 | 再現条件の保持、段境界、プロンプト・処理方式同一性 |
| Requirement 8 | フェーズ対応プロファイル | `intent`／`requirements`／`design`／`tasks` の強調切り替え |
| Requirement 9 | 可搬な証拠束輸出 | 来歴項目、レビューモード保持、束輸出と取り込み判断の分離 |
| Requirement 10 | パターン定義依存の除外 | パターン定義ファイル参照の責務外明示 |

各要件の受入基準の詳細は [.reviewcompass/specs/runtime/requirements.md](../../.reviewcompass/specs/runtime/requirements.md) を参照。

## 4. 処理方式の命名（Requirement 2 受入 2）

ReviewCompass では処理方式の命名を `foundation` の 3 役名と統一する（計画書 §5.15.6）：

- `primary`：主役検出のみ（旧命名：`single`）
- `adversarial`：主役 ＋ 敵対役（旧命名：`dual`）
- `judgment`：主役 ＋ 敵対役 ＋ 判定役（旧命名：`dual+judgment`）

3 処理方式の使い分けにより、3 方式比較データ（`findings_by_method`、計画書 §5.9.6）を取得し、レビューの収束過程を可視化する。

## 5. レビューモードの記録（Requirement 4 受入 6）

実行時が出力する証拠には、`foundation` 正本のレビューモード語彙を付与する：

- `manual_dogfooding`：手動 dogfooding レビュー記録（人間が 3 役を模倣）
- `runtime_mediated`：実行時経由（本機能による大規模言語モデル呼び出し）
- `subagent_mediated`：サブエージェント経由（Claude Code 内部のサブエージェント機構、計画書 §5.23.12）

実行時は `runtime_mediated` を自動的に付与する。他のモードは別の経路が付与する。

## 6. 人間決定と検証器の順序（Requirement 6 受入 9）

実行終了の順序は機械的に強制される：

1. **人間署名**（sign-off）：運用者が承認・却下・保留を決定単位ごとに実施
2. **検証器呼び出し**：必須メタデータの存在と必須節の充足を機械検査
3. **実行終了**：上記 2 つが完了した場合のみ run が closed として扱われる

この順序を逆転させた実行は無効とする。検証器結果が人間決定より先行することは禁止される。

## 7. 配置先（ディレクトリ構造）

実行時の出力先と参照先（計画書 §4 と §5.15.3）：

- `<対象アプリ>/.reviewcompass/specs/<feature>/reviews/<日付>-<種別>.md`：レビュー記録
- `<対象アプリ>/.reviewcompass/specs/<feature>/spec.json`：実行状態（承認・拒否・保留）
- リポジトリ内 `templates/prompts/<段の用途>/<役>.prompt.md`：プロンプト雛形
- リポジトリ内 `schemas/foundation/`／`schemas/domain/`／`schemas/validators/`：契約の参照先

## 8. 他機能との関係

- **`foundation`**：本機能はスキーマ、メタデータ契約、プロンプト配置規則を取り込む（依存：hard）
- **`evaluation`**：本機能の出力する実行記録から有効・無効判定を行う（本機能は evaluation の要求する証拠形式を満たす）
- **`self-improvement`**：本機能の実行証拠から提案を生成する（本機能は再生可能な記録形式を保持）
- **`analysis`**：本機能の証拠は `evaluation` を経由してから `analysis` に渡る（直接従属しない）
- **`workflow-management`**：本機能の状態機械契約に基づき、各フェーズの所定手続きを駆動する
- **`conformance-evaluation`**：本機能の出力する実行記録から、上流文書との適合性を評価する

## 9. 実行ディレクトリ配置と運用ルール（design 段反映、tasks T-001）

実行時は 1 回のレビュー実行（review session）ごとに 1 ディレクトリ（`experiments/runs/<run_id>/`）を生成する。配置の機械可読正本は [runtime/runtime_core/run_layout/layout_spec.yaml](../../runtime/runtime_core/run_layout/layout_spec.yaml)、構造の解説は同ディレクトリの [README.md](../../runtime/runtime_core/run_layout/README.md) にある。本節は配置の運用ルールを記述する。

### 9.1 ディレクトリ構造（design.md §実行成果物配置）

```text
experiments/runs/<run_id>/
├── run_manifest.yaml          # 実行メタデータの運用者可読な正本
├── review_case.json           # 機械可読な正本（唯一の横断正本）
├── steps/                     # 段単位再演の最小単位（生段証拠）
├── decisions/                 # 人間決定連携を生証拠から切り離して保存
├── failures/failure_observations/  # 失敗観察を独立成果物として保管
├── validation/                # 検証器結果と無効化標識を別配置
└── derived/                   # runtime 便宜成果物（evaluation の正本ではない）
```

必須ディレクトリは 6 件（上記 5 サブディレクトリ ＋ ルート）。物理ディレクトリの実体作成は実行時に session controller（tasks T-002）が `run_id` ごとに行う。

### 9.2 配置の運用ルール（3 原則）

実行ディレクトリの運用は次の 3 原則に従う（design.md §配置の運用ルール）。

1. **生証拠の不変（生証拠不変）**：段ごとの生証拠（`steps/*.json`）は実行終了後に書き換えない。要約を後から更新しても生証拠は変更しない。実行終了時に `run_manifest.yaml` へ `closed_at`（凍結マーカー）を記録し、これ以降の生段証拠変更を禁止する。

2. **生証拠と派生証拠の分離（派生分離）**：証拠は 3 層に書き分ける。生段証拠（`steps/*.json`）、人間・決定統合証拠（`decisions/*.json`）、便宜要約（`derived/*.json`）を分離して保存する。後追で追加されるデータ（失敗観察・検証結果・無効化標識）は `failures/`／`validation/` に独立保管し、`review_case.json` からは参照のみとする。

3. **`review_case.json` 唯一の横断正本**：`review_case.json` を唯一の横断正本とする（スキーマは foundation 所有、下流機能はこれを正本として読む）。runtime は `steps/*.json` や `decisions/*.json` から `review_case.json` への投影規約を所有・定義し、`review_case.json` が常に foundation の `review_case` スキーマに準拠することを保証する。

なお、可搬証拠束輸出（tasks T-010）は生実行ディレクトリを置き換えず、別成果物として扱う。

## 10. 後続セッションでの追加予定

本文書は requirements 骨子に design 段の実行ディレクトリ配置（§9）を追記した段階。残りの design／実装の詳細は後続で追記する：

- 4 状態軸の独立性に関する設計（§5.15.4）
- 4 つの設計の工夫（§5.15.5）
- 拡張する 5 点（§5.15.7）

## 11. 関連文書

- 形式仕様：[.reviewcompass/specs/runtime/requirements.md](../../.reviewcompass/specs/runtime/requirements.md)
- 計画書 §5.15：[runtime 仕様の整理](../plan/reconstruction-plan-2026-05-21.md)
- 計画書 §4：[ReviewCompass リポジトリの初期構造案](../plan/reconstruction-plan-2026-05-21.md)
- 計画書 §5.20.2 runtime 行：[抽出対応表](../extraction-mapping.md)
- 隣接機能：[foundation](FOUNDATION.md)
