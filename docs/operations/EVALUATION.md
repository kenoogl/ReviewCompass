# EVALUATION：評価機能の運用文書

最終更新：2026-06-03（requirements 部分の骨子に加え、分析成果物配置・取り込み・許容判定の初期契約を追加。残りの design 解説は後続セッションで追加）

本文書は ReviewCompass の `evaluation`（評価機能）の運用上の役割と契約を解説する。形式仕様は [.reviewcompass/specs/evaluation/requirements.md](../../.reviewcompass/specs/evaluation/requirements.md) を参照する。本文書は読み手向けの解説、仕様文書は機械検査と仕様駆動手続きの正本という関係。

本版では、requirements の要約、分析成果物配置、取り込み配置、許容判定、manifest の初期契約を
確定済みとして扱う。本文中で「後続論点」「後続判断事項」と明記したものは未確定であり、
§10 の一覧を追跡先とする。

## 1. 役割

`evaluation` は `runtime` が出力したレビュー実行証拠を受け取り、有効・無効に切り分け、比較可能なメトリクスと派生成果物に変換する機能である。`runtime` を動かす責務は持たず、出てきた結果を扱う側にある。

具体的には：

- **有効・無効の機械分離**：メタデータと無効化マーカーに基づき、実行を `valid`／`invalid`／`exploratory`／`analysis_blocked` に分類
- **処理方式の比較契約**：`primary`／`adversarial`／`judgment` の 3 処理方式を横断比較
- **メトリクス抽出**：構造化された証拠から再現可能な計算でメトリクスを得る
- **除外と注意点の報告**：何が除外され、その理由を明示。データ品質の問題を隠さない
- **派生成果物の生成**：`self-improvement` と `analysis` が再利用可能な機械可読出力
- **評価準備メタデータの検査**：必須メタデータが欠けた証拠を分離し、標準集計を速やかに遮断
- **フェーズ対応の評価**：`intent`／`requirements`／`design`／`tasks` 別のスライスとメトリクス
- **レビューモードの区別**：手動 dogfooding ／サブエージェント経由／実行時経由／独立 API 経由を別集団として扱う
- **外部証拠束の取り込みと許容判定**：他環境のレビュー実行を中央側で取り込む

## 2. 設計の根本姿勢

- **`foundation` 契約と `runtime` 出力の遵守**：本機能は `foundation`／`runtime` の入力証拠契約を上書きせず、既存契約に従って評価を実施
- **黙示的な集計禁止**：無効実行と有効実行、レビューモードの異なる証拠を黙示的に 1 つの集計に潰さない
- **再現可能性**：派生メトリクスから生の証拠への導出経路を保持。後から再計算可能
- **速やかな失敗**：必須メタデータ欠落、規約版／プロンプト版の混在等は標準集計を遮断。処理できる証拠まで黙示的に巻き添えにするのではなく、遮断理由を記録する
- **データ品質の透明性**：除外や注意点を明示し、後続の `analysis` や論文化が品質問題を隠せないようにする

## 3. 10 の要件領域（要約）

| 要件 | 領域 | 何を定めるか |
|---|---|---|
| Requirement 1 | 有効・無効実行の分離 | 4 分類（valid／invalid／exploratory／analysis_blocked）と、レビューモードとの直交独立性 |
| Requirement 2 | 処理方式の比較契約 | 3 処理方式（primary／adversarial／judgment）の比較、規約版・プロンプト版同一性。ここでいう処理方式は実行条件の比較軸であり、§8 の役別出力領域とは別概念 |
| Requirement 3 | メトリクス抽出 | 構造化証拠からの計算、導出経路の保持、3 階層（実行／所見／処理方式） |
| Requirement 4 | 除外と注意点の報告 | 除外件数と理由、データ品質と実行時品質の区別 |
| Requirement 5 | 派生成果物の生成 | 構造化出力、実行識別子への連結、無効化された実行に基づく成果物の陳腐化対応 |
| Requirement 6 | 評価準備メタデータの完全性 | 必須メタデータ検査、欠落時の標準集計拒否、診断情報出力 |
| Requirement 7 | フェーズ対応の評価 | 4 フェーズ（intent／requirements／design／tasks）のスライス対応 |
| Requirement 8 | フェーズ特異な有効性メトリクス | 共有の中核 ＋ フェーズ特異な重ね合わせ |
| Requirement 9 | レビューモードの区別 | `foundation` 正本が定める各経路（manual_dogfooding／subagent_mediated／runtime_mediated／api_mediated 等）の独立集団扱い |
| Requirement 10 | 外部証拠束の取り込みと許容判定 | 中央側取り込み契約、来歴情報検証、許容状態の管理 |

各要件の受入基準の詳細は [.reviewcompass/specs/evaluation/requirements.md](../../.reviewcompass/specs/evaluation/requirements.md) を参照。

## 4. 直交独立な 2 軸の分類（Requirement 1 受入 6、Requirement 9）

評価では実行を 2 つの独立軸で分類する：

- **実行有効性軸（4 値）**：`valid`／`invalid`／`exploratory`／`analysis_blocked`（4 値すべてが `runtime/foundation/metadata_contract.yaml` の `evidence_class` 正本値であり、evaluation requirements はこれを参照する。`analysis_blocked` は evaluation 側の拡張値ではない）
- **レビューモード軸**：`foundation` の `review_mode` 正本値（現時点では `manual_dogfooding`／`runtime_mediated`／`subagent_mediated`／`api_mediated`）

両軸は直交独立。たとえば「内容上有効な手動 dogfooding 実行」は実行有効性軸では `valid`、レビューモード軸では `manual_dogfooding`。両軸で別々に分類される。
外部取り込み証拠については、これとは別に §6 の `admission_status` が加わる。これは取り込み可否を
表す補助軸であり、内部の `runtime` 直産証拠には付かない。
`evidence_class` と `review_mode` は実行単位の属性、`admission_status` は外部取り込み束の
`bundle_id`／`run_id` 単位で `imports/admission_register.json` に保持する属性である。
`analysis_run_manifest.yaml` はこれらの正本保持先ではなく、分析に使った入力識別子を参照する。

## 5. 標準比較集団規則（Requirement 9 受入 6）

レビューモードは独立集団として扱う：

- **`runtime_mediated`**：標準比較セットの中核
- **`manual_dogfooding`**：別集団。標準セットから除外、明示的に別スライスとして含める場合のみ加える
- **`subagent_mediated`**：別集団。同様に独立した別スライスとして扱う（計画書 §5.23.12.6 のフェーズ 4 段階移行と整合）
- **`api_mediated`**：別集団。独立 API 経由の triad-review 証拠として、標準 `runtime_mediated` 比較セットには黙示的に混ぜない

ReviewCompass では先行プロジェクトと異なり、手動 dogfooding は「Phase 1 限定」ではなく恒久運用（§5.23 由来）。
現時点の標準比較セットは `runtime_mediated` のみを中核とする。将来 `subagent_mediated` を
標準集団へ昇格させる場合は、本節と §6 の標準比較条件を同時に改訂する。

## 6. 取り込み許容の 3 状態（Requirement 10）

外部からの可搬な証拠束を取り込む際、取り込み許容状態（`admission_status`）を
実行有効性軸とは別に 3 つへ分類する：

- **`rejected`**：来歴情報不足、チェックサム不一致、必須入力欠落などで母集団に含めない
- **`admitted_exploratory`**：取り込みは許容するが標準集計から除外し、探索分析に限る
- **`admitted_standard`**：取り込み証拠として標準比較候補にできる

`admission_status` は §4 の実行有効性軸（`foundation` の `evidence_class` 値：
`valid`／`invalid`／`exploratory`／`analysis_blocked`）とは別フィールドである。
`evidence_class` の値は `runtime/foundation/metadata_contract.yaml` の正本語彙を参照する。
外部取り込み証拠では、まず `admission_status` で取り込み可否を判定し、`rejected` は
標準比較にも探索分析にも入れない。取り込みを許容した証拠だけを、次に `evidence_class` で
実行有効性分類する。

標準比較セットへ入れられる条件は次の通り。すべて満たす必要がある。§5 でレビューモードごとの
集団分離を定め、本節で実行有効性、版整合、外部取り込み時の許容状態を加える。

- `evidence_class=valid`
- `review_mode=runtime_mediated`（将来の昇格時は §5 と本条件を同時に改訂）
- 規約版、runtime 版、プロンプト版が比較セット内で揃っている。初期契約では、各 coverage が 1 要素集合であることを指す
- 外部取り込み証拠の場合は `admission_status=admitted_standard`

`docs/notes/review-runs/<run_id>/` 由来の API レビュー証拠で、`parse_status=parse_failed`
または `decision_status=human_required` を含むもの、または raw/triage 台帳が存在しないものは、変換規則が確定するまで
暫定的に `admission_status=rejected` とし、`admission_status=admitted_standard` にしない。
これは現行の安全側既定であり、探索分析での再利用可否を確定する判断ではない。
探索分析に限って再利用する場合は、後続の判定表で `admitted_exploratory` へ明示的に
再分類する条件、人間の opt-in、caveat 記録を定めてから行う。
この再分類手続きが確定するまでの空白期間は、探索分析での再利用も行わない。
notes 側台帳の不備確認と、変換後 bundle の `admission_status` 判定は別段階の処理である。

内部の `runtime` 直産証拠には `admission_status` を要求しない。外部取り込み証拠だけが
`imports/admission_register.json` 上の `admission_status` を持ち、内部証拠は取り込み許容判定の対象外として扱う。
`manual_dogfooding` や `api_mediated` 等の別レビューモードは、標準比較セットではなく
別スライス集計として扱う。
現時点で確定しているのは、標準比較セットに入れる条件と、安全側の既定動作である。
現時点で標準比較セットへ入ると定義済みの外部取り込み証拠は、
`admission_status=admitted_standard`、`evidence_class=valid`、`review_mode=runtime_mediated`、
版整合あり、の組み合わせだけである。
`admission_status=admitted_exploratory` と `evidence_class=exploratory` の組み合わせなど、
全組み合わせの詳細は §10 の判定表追加時に確定する。未定義の組み合わせは標準比較セットへ
入れない。`admission_status=admitted_exploratory` の外部証拠は、`evidence_class=valid` であっても
標準比較セットへ入れない。`evidence_class=invalid` または `analysis_blocked` の証拠は探索分析にも黙示的に入れない。
`exploratory` を含む標準外証拠は、探索分析へ明示 opt-in した場合だけ含める。探索分析へ含める場合も
`caveats/caveat_register.json` に未定義扱いを記録し、正確な包含条件は後続の判定表に従う。
明示 opt-in の操作契約、記録主体、`caveats/caveat_register.json` への記録タイミングは
§10 の後続論点として確定する。
派生成果物にはどの許容状態の証拠を含むかを必ず明示する。

## 7. 他機能との関係

- **`foundation`**：本機能はスキーマとメタデータ契約に依存（依存：hard）。`review_mode` 語彙、`evidence_class` 語彙、`validator_status` 語彙は `runtime/foundation/metadata_contract.yaml` の正本を参照。`validator_status` は評価準備メタデータ検査と診断出力で、検証器由来の状態を解釈するために使う
- **`runtime`**：本機能は `runtime` の構造化実行証拠と可搬証拠束を受け取る（一方向の依存）
- **`self-improvement`**：本機能は再利用可能な分析入力を `self-improvement` に渡す
- **`analysis`**：本機能は読み物向け原データを `analysis` に渡す。`analysis` の特定の表現責務（運用ダッシュボード／週次／監査／論文）は本機能では持たない
- **`workflow-management`**：所定手続きの実行結果の評価要求を受ける
- **`conformance-evaluation`**：本機能の評価結果と検証器メタデータは `conformance-evaluation` の入力にもなる

## 8. 分析成果物配置

`evaluation` の実体生成物は `experiments/analysis/` 配下に置く。`runtime` が
生成する生実行証拠 `experiments/runs/<run_id>/` は編集せず、分析成果物と
生実行証拠を分離する。取り込み済み可搬証拠束は
`experiments/analysis/imports/bundles/<bundle_id>/run/<run_id>/` に保管し、
中央側で再分析できるようにする。
`imports/` は `experiments/analysis/` の管理下に置くが、生成・削除ポリシーは通常の派生出力と別扱いにする。

取り込み済み可搬証拠束は分析入力に近い性質を持つが、現行 design.md の配置契約に従い、
初期実装では `experiments/analysis/imports/` 配下に保持する。分析成果物のクリーンアップ時に
取り込み済み束を誤って削除しないよう、`imports/` は通常の派生出力とは異なる保管領域として扱う。
この配置を analysis 外へ移すかどうかは、配置契約の再設計を伴うため後続判断事項とする。
初期実装では保護属性を文章で定めるに留め、`layout_spec.yaml` への `cleanup_policy: preserve`
のような機械可読属性は後続の配置詳細化事項とする。

本節では、分析成果物パスと仕様ファイルパスの 2 種類を使い分ける。分析成果物パスは、
特記がない限り `experiments/analysis/` からの相対表記である。仕様ファイルパスは
リポジトリルートからの相対表記として明示する。
`experiments/analysis/` 配下のトップレベル必須サブディレクトリは次の 8 件。この一覧は
`evaluation/analysis_layout/layout_spec.yaml` の `required_directories[].path` と一致する。
配下のファイルやサブ構造は、同ファイルの `artifact_families` と突き合わせる。
2026-06-03 時点では、`tests/evaluation/test_t001_layout.py` がこの対応を検査している。

- `imports`：取り込み履歴、許容判定履歴、取り込み済み可搬証拠束。必須領域だが、通常の派生出力ではなく保護対象の保管領域
- `manifests`：分析実行の構成、入力集合、状態を記録するメタデータ領域。`analysis_run_manifest.yaml`、`staleness_register.json`
- `classifications`：実行分類、除外報告、不十分メタデータ診断
- `metrics`：実行レベル、所見レベル、処理方式レベルのメトリクス
- `comparisons`：処理方式比較、フェーズ対応比較
- `caveats`：注意点登録
- `modes`：レビューモード別所見差分
- `roles`：主役、敵対役、判定役別所見差分

`treatment` は `primary`／`adversarial`／`judgment` の処理方式を表す軸であり、
`roles` は主役／敵対役／判定役という 3 役別の所見差分を表す出力領域である。
値名は対応しうるが、前者は「実行条件の比較軸」、後者は「役別の所見差分出力」として
別概念として扱う。処理方式別の比較結果は主に `comparisons/`、処理方式別メトリクスは
`metrics/`、役別の所見差分は `roles/` に置く。

`imports` 配下では、取り込み済み可搬証拠束を
`imports/bundles/<bundle_id>/run/<run_id>/` の形で保持する。`bundle_manifest.yaml`
や `checksums/` も同じ `imports/bundles/<bundle_id>/` 配下に置き、runtime 側の
`exports/<bundle_id>/` と中央側保管先の構造を対称にする。
取り込み履歴は `imports/ingestion_register.json`、許容判定履歴は
`imports/admission_register.json` に記録し、`bundle_id`／`run_id`／`admission_status` を
通じて束本体と判定結果を対応付ける。`admission_register.json` は外部取り込み証拠だけを
対象とし、内部の `runtime` 直産証拠は登録しない。`rejected` の束はここに履歴を残すが、
`analysis_run_manifest.yaml` の `input_run_set` には含めない。`admitted_exploratory` は
探索分析の入力集合には含めうるが、標準比較セットの入力集合には含めない。

`evaluation/analysis_layout/layout_spec.yaml` は実体生成物ではなく、配置ルール定義である。
要件契約の正本は `.reviewcompass/specs/evaluation/requirements.md`、分析成果物配置ルールの
機械可読正本は `evaluation/analysis_layout/layout_spec.yaml` として、契約種別ごとに
正本を分ける。配置仕様を `.reviewcompass/specs/evaluation/` 配下へ移すかどうかは、
仕様ディレクトリと実装側配置ルールの責務分離に関わるため §10 の後続判断事項とする。
配置仕様の機械可読正本はリポジトリルート相対で
`evaluation/analysis_layout/layout_spec.yaml` に置く。本ファイルから参照する場合の
相対パスは [../../evaluation/analysis_layout/layout_spec.yaml](../../evaluation/analysis_layout/layout_spec.yaml)。
同ファイルは初期実装で新設済みである。
後続実装はこの仕様に従い、各成果物を担当ディレクトリへ出力する。

`staleness_register.json` は、無効化または再分類により派生成果物が古くなったことを記録する
台帳である。初期契約では、影響を受けた論理成果物 ID、原因となった実行 ID、検出時刻、
選択した処理方針を `manifests/staleness_register.json` に追記する。

## 9. analysis_run_manifest.yaml

初期実装では、各 analysis run は最新の分析実行を表す
`manifests/analysis_run_manifest.yaml` を必ず生成する。
この manifest は、どの入力実行集合をどの評価ロジックで分析したかを記録する。
複数 analysis run の履歴を run 別ディレクトリで保持するかどうかは、後続の版管理拡張事項とする。
単一 manifest は最新状態のみを表し、過去の manifest 履歴を保持するものではない。
再実行時は同じ `manifests/analysis_run_manifest.yaml` を更新する。
`output_artifact_ids` は物理ファイルパスではなく論理成果物 ID を列挙する。
初期実装では、生成した主要成果物を安定した文字列 ID のリストとして記録する。
生成物が診断だけの場合は診断成果物の ID を記録し、出力がない遮断状態では空リストを許容する。
命名規約が確定するまでの暫定 ID は、`evaluation/analysis_layout/layout_spec.yaml` の
`artifact_families` に列挙された成果物名を基準にする。
論理成果物 ID の命名規約、各ディレクトリとの対応、再実行時の継続性は §10 の後続論点として確定する。
`input_run_set` は入力に使った実行識別子のリストである。内部証拠は `run_id`、外部取り込み証拠は
初期表記では `bundle_id/run_id` で識別する。これは暫定表記であり、安全な区切り文字または
URN 形式は §10 の後続論点として確定する。暫定表記を YAML に書く場合は文字列としてクォートする。
`rejected` は含めず、`admitted_exploratory` は
明示 opt-in された探索分析の入力集合に限って含めうる。
必須項目は次の 13 件。この一覧は `evaluation/analysis_layout/layout_spec.yaml` の
`analysis_run_manifest.required_fields` と一致する。
2026-06-03 時点では、`tests/evaluation/test_t001_layout.py` がこの required fields の一致を検査している。

- `analysis_logic_version`
- `input_run_set`
- `generated_at`
- `metric_set_version`
- `phase_metric_profile_version`
- `comparison_contract_version`
- `protocol_version_coverage`
- `runtime_version_coverage`
- `prompt_set_version_coverage`
- `analysis_run_id`
- `analysis_started_at`
- `analysis_completed_at`
- `output_artifact_ids`

`protocol_version_coverage`、`runtime_version_coverage`、
`prompt_set_version_coverage` は、入力実行集合に含まれる版の集合を列挙する版被覆記録である。
ここでいう規約版はレビュー手続きやメタデータ契約の版、runtime 版は実行器側の版、
プロンプト版はレビューに使ったプロンプトセットの版を指す。
`analysis_run_id` は分析実行を識別する ID、`analysis_started_at` と `analysis_completed_at` は
その分析実行の開始時刻と完了時刻である。
標準比較セット内で規約版、runtime 版、プロンプト版が混在していないかを後続の比較器が
検査できるよう、manifest に明示する。
初期実装では manifest を生成したうえで比較器が標準集計を遮断する。manifest 自体は、
遮断理由を後続で追跡するための被覆記録として残す。
`analysis_run_manifest.yaml` は分析実行の入力、版被覆、出力 ID を記録し、
`staleness_register.json` は後から古くなった成果物を記録する。
処理方式別または役別のプロンプト版被覆へ分解するかどうかは、§10 の後続論点とする。

## 10. 後続セッションでの追加予定

本文書は requirements 部分の骨子と、分析成果物配置、取り込み配置、許容判定の初期契約を含む。
次のセッション以降で次を追加する：

- **優先度: must-fix**：`admission_status` と `evidence_class` の組み合わせ判定表
- **優先度: must-fix**：論理成果物 ID の命名規約と、`experiments/analysis/` 配下ディレクトリとの対応
- **優先度: must-fix**：`input_run_set` の外部証拠識別子で使う安全な区切り文字または URN 形式
- **優先度: must-fix**：探索分析への明示 opt-in 操作契約と caveat 記録タイミング
- **優先度: must-fix**：`docs/notes/review-runs/<run_id>/` の raw/triage 台帳を `experiments/analysis/imports/` 配下の可搬証拠束へ変換する規則
- **優先度: must-fix**：`parse_status=parse_failed` や `decision_status=human_required` を含む review run 証拠の `admission_status` / `evidence_class` へのマッピング
- **優先度: must-fix**：review run 証拠の判断主体をモデル ID と版で記録し、provider 名を実行経路メタデータに留める正規化規則
- **優先度: must-fix**：review run raw 応答を可搬証拠束へ変換する際のサニタイズ、保護属性、共有範囲
- **優先度: must-fix**：`decision_actor_type` や `formatted_by_actor_type` など、review run 証拠内の actor 類型語彙を foundation 正本へ追加するか、evaluation 局所語彙として扱うかの判断
- **優先度: must-fix**：`parse_status`、`decision_status`、`follow_up_action`、`invocation_path`、`formatted_by` など、review run 台帳の局所状態語彙を foundation 正本へ追加するか、evaluation 局所語彙として扱うかの判断
- **優先度: must-fix**：`severity_normalized` と `final_label` を所見レベルメトリクスの集計軸へどう取り込むかのマッピング
- **優先度: must-fix**：独立レビュー群のオーケストレーター集約と、モデル間対話を伴う議論モードを評価上どう区別するか。
  推薦案は、`aggregation_mode=independent_orchestrated` と `aggregation_mode=discussion` を分けて記録し、
  人間が比較可能と判断するまで同じ標準母集団へ混ぜないこと
- **優先度: must-fix**：`api_mediated` 証拠を標準比較集団へ昇格させるかどうか、昇格する場合の条件。
  現版では標準比較集団へ入れず、昇格には §5、§6、比較契約、manifest 被覆項目の同時改訂を必要とする
- **優先度: must-fix**：`metric_set_version`、`phase_metric_profile_version`、`comparison_contract_version` の運用単位
- **優先度: should-fix**：design.md 抽出に基づく設計の説明（計画書 §5.17 全体）
- **優先度: should-fix**：5 段パイプライン構造の継承（§5.17.2）
- **優先度: should-fix**：4 状態区分の詳細な分類・遷移ロジック（§5.17.3）
- **優先度: should-fix**：3 階層・2 層の指標構造（§5.17.4）
- **優先度: should-fix**：処理方式別／役別のプロンプト版被覆記録の要否
- **優先度: should-fix**：複数 analysis run の履歴保存方式
- **優先度: should-fix**：`staleness_register.json` の詳細な生成・更新契約
- **優先度: should-fix**：比較適格性ノートのスキーマ所有者（§5.17.11）
- **優先度: should-fix**：探索的区分のフィールド整合（§5.17.12）
- **拡張**：取り込み済み可搬証拠束を `experiments/analysis/imports/` 外へ移すかどうか
- **拡張**：`imports/` の機械可読な保護属性（例：cleanup policy）
- **拡張**：配置仕様 `layout_spec.yaml` を `.reviewcompass/specs/evaluation/` 配下へ移すかどうか

## 11. 関連文書

- 形式仕様：[.reviewcompass/specs/evaluation/requirements.md](../../.reviewcompass/specs/evaluation/requirements.md)
- 計画書 §5.17：[evaluation 機能の継承方針](../plan/reconstruction-plan-2026-05-21.md)
- 計画書 §5.20.2 evaluation 行：[抽出対応表](../extraction-mapping.md)
- 機能横断波及所見：[.reviewcompass/pending-cross-feature-findings.md](../../.reviewcompass/pending-cross-feature-findings.md)
- 隣接機能：[foundation](FOUNDATION.md)、[runtime](RUNTIME.md)
