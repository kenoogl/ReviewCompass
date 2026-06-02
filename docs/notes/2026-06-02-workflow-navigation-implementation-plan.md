# ReviewCompass ワークフローナビゲーション実装計画

記録日：2026-06-02

## 1. 現在の対応方針

ReviewCompass の dogfooding 中に、LLM がワークフロー手順を読み違えて品質を下げる危険を抑えるため、まず ReviewCompass 自身の固定ワークフローを機械的にナビゲートする。

初期実装では汎用ワークフローエンジンを作らない。現在の `spec.json.workflow_state`、既定のフェーズ順、既定の段順、既定の機能順を読み、次に許可される作業を返す。

## 2. ReviewCompass 用の最小実装

### 2.1 対象

- `tools/check-workflow-action.py next`
- 入力：`.reviewcompass/specs/<feature>/spec.json`
- 入力：`stages/in-progress/`
- 出力：次に行うべき作業、対象 feature、phase、stage、理由

### 2.2 判定順

1. `stages/in-progress/` に進行中ファイルがあれば、その手続きを優先再開する。
2. post-write-verification 対象の未コミット変更があれば、通常ワークフローより優先して検証タスクを返す。
3. post-write-verification pending 中に禁止変更があれば、通常検証ではなく逸脱として返す。
4. `workflow_state` を全 feature から読む。
5. フェーズ順に未完了箇所を探す。
6. `drafting` と `triad-review` は機能単位で、機能順に次対象を返す。
7. `review-wave`、`alignment`、`approval` は機能横断段として、全機能の前提が満たされた時点で返す。
8. すべて完了していれば `completed` を返す。

### 2.2.1 post-write-verification pending 中の禁止変更

post-write-verification pending は、書き込み済み文書の検証に作業を限定する状態である。この状態で検証 runner や一時ツールを新規作成すると、LLM が「検証を実施する」という指示を拡張解釈して外部 API 実行まで進む危険がある。

初期実装では、post-write-verification 対象ファイルが未コミット変更に含まれる状態で、`tools/*.py` の未追跡ファイルがあれば `post_write_policy_violation` として `DEVIATION` を返す。

これは完全な許可操作ポリシーではなく、今回観測された逸脱を最小範囲で機械的に止める第一段である。

### 2.2.2 reopen 進行中ファイルの詳細解決

`stages/in-progress/` に `process_id: reopen-procedure` の YAML がある場合、単なる再開指示ではなく、reopen 手続きの具体的な次作業を返す。

初期実装で読むフィールド：

- `process_id`
- `next_step`
- `completed_steps`
- `pending_gates`
- `current_blocker`
- `feature`

`required_action` の初期対応：

- `current_blocker` がある：`wait_for_human_approval`
- `next_step` が第1過程：`classify_and_rollback_flags`
- `next_step` が第2過程：`repair_canonical_documents`
- `next_step` が第3過程：`rerun_alignment_approval_chain`
- `next_step` が第4過程：`finalize_reopen`
- `next_step` が完了：`reopen_completed`
- 判定不能：`inspect_reopen_state`

これにより、review-wave などで遡及手戻りが発生し、reopen が `stages/in-progress/` に記録された後は、通常ワークフローや post-write-verification へ進まず、reopen の次作業を優先できる。

### 2.3 初期実装の境界

- 所見内容の意味分類は行わない。
- reopen は、既に存在する in-progress ファイルの詳細解決と、記録済み classification からの `reopen-start` による trigger_map 解決・in-progress 生成までを扱う。所見から classification を自動判定すること、spec.json のフラグ差し戻しを自動実行することは扱わない。
- post-write-verification は、対象ファイルの未コミット変更検出、manifest による完了認定、人間判断待ちの検出までを扱う。検証内容の妥当性そのものは扱わない。
- post-write-verification pending 中の許可操作を完全には管理しない。初期実装では、新規 `tools/*.py` runner 作成だけを逸脱として扱う。
- 任意の workflow graph は扱わない。
- ReviewCompass の現行フェーズ、段、機能順を前提にする。

## 3. その後の拡張計画

### 3.1 決定表の追加

`classify` サブコマンドを追加し、所見分類後の処理段を機械決定する。

- `in_feature` -> 当該 feature の triad-review 内で処理
- `cross_feature` -> pending に記録し review-wave へ
- `upstream_reopen` -> reopen 手続きへ
- `leave_as_is` -> 記録のみ
- `deferred` -> 将来段の確認項目へ

### 3.2 post-write-verification 完了認定の manifest 化

検証結果の完了認定を、LLM の自己申告ではなく manifest で表す。

- 対象ファイル一覧
- 検証者一覧
- 各検証結果ファイル
- 統合結果
- 未解決の本質的指摘の有無
- 人間判断待ちの有無

`next` は manifest を読み、未完了なら検証継続、収束済みなら通常ワークフローへ戻す。

初期実装では `.reviewcompass/post-write-verification/*.yaml` を読む。対象ファイル群を覆う manifest があり、`status: completed`、`required_verifiers` が `completed_verifiers` で満たされ、`unresolved_substantive_findings: 0` なら通常ワークフローへ戻る。未解決の本質的指摘が 1 件以上ある場合は `post_write_human_decision_required` を返す。

### 3.3 post-write-verification 許可操作ポリシーの拡張

pending 中に許される操作と禁止される操作を、ファイル種別・操作種別ごとの表として定義する。

初期候補：

- 許可：対象ファイルの読み取り
- 許可：既存の検証手段の実行
- 許可：検証結果ファイルまたは manifest の作成
- 許可：検証不能の報告
- 禁止：新規 runner / 一時ツールの作成
- 禁止：未承認の外部 API 呼び出し
- 禁止：target_files 以外の正本文書変更

### 3.4 reopen-start による trigger_map 解決

`reopen-start` サブコマンドで、手戻り種別から `pending_gates` を解決し、`stages/in-progress/reopen-procedure-<日付>.yaml` を生成する。

初期実装の入力：

- `--classification`：手戻り種別（例：`D-1`）
- `--feature`：対象 feature
- `--basis`：種別判定根拠ファイル
- `--date`：進行中ファイル名の日付
- `--trigger`：reopen 起動理由

初期実装の出力：

- `process_id: reopen-procedure`
- `classification`
- `feature`
- `classification_basis`
- `next_step: 第1過程：判定とフラグ差し戻し`
- `pending_gates`
- `current_blocker: null`

この実装は in-progress 生成までを担う。spec.json のフラグ差し戻しはまだ自動実行しない。

### 3.5 定義の外出し

現在コード内にあるフェーズ順、段順、機能順を、段集合 YAML または workflow 定義ファイルから読む形へ移す。

### 3.6 任意構造への拡張

intent から feature 分割した結果を workflow 定義として保存し、固定の ReviewCompass 構造ではなく任意の phase / stage / feature graph を解決できるようにする。

### 3.7 フック連携

`next` の結果を commit / push / spec-set の事前検査と連動させ、現在許可されていない作業を検出した場合に fail-closed で止める。
