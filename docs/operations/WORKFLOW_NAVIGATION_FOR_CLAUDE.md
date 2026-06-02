# Claude 作業用：ReviewCompass ワークフローナビゲータの使い方

この文書は、Claude が ReviewCompass の開発作業を始める前に読むための手順書である。

目的は、Claude が記憶や推測で「次にやること」を決めないようにし、`tools/check-workflow-action.py next` の結果に従って作業することである。

## 1. 最初に必ず実行するコマンド

作業を始める前、または次に何をするかを提案する前に、必ず次を実行する。

```bash
python3 tools/check-workflow-action.py next --json
```

このコマンドの結果を、現在の正本として扱う。

## 2. 判定結果の読み方

出力 JSON の `next_action.kind` を見る。

### `resume_in_progress`

`stages/in-progress/` に進行中手続きがある。

この場合、新しい作業を始めてはいけない。`next_action.file` に示された進行中ファイルを読み、その手続きを続ける。

### `post_write_verification`

post-write-verification 対象の未コミット変更がある。

この場合、通常ワークフローへ進んではいけない。`next_action.target_files` に示されたファイルについて、書き込み後検証を実施する。

ただし、Claude はこの結果を根拠に、独自の検証スクリプトを新規作成してはいけない。外部 API を呼ぶ検証も、利用者の明示承認または既に許可された既存コマンドがない限り実行してはいけない。

実行手段が未確定、または承認フィルター・権限・API 設定により検証を実行できない場合は、検証を完了扱いにせず、次を利用者へ報告して停止する。

- 検証対象ファイル
- 必要な検証者数
- 実行しようとした既存手段
- 実行できない理由
- 人間判断または承認が必要であること

対象ファイルの例：

- `docs/plan/`
- `docs/disciplines/`
- `docs/operations/`
- `docs/notes/`
- `docs/experiments/`
- `docs/reviews/` の `reopen-classification-*.md` または `*-audit-*.md`
- `TODO_NEXT_SESSION.md`

`.reviewcompass/specs/` 配下の仕様文書は、post-write-verification ではなく通常の 5 段ワークフローで検証される。

### `post_write_policy_violation`

post-write-verification pending 中に、禁止された変更がある。

この場合、検証を完了扱いにしてはいけない。通常ワークフローへ進んでもいけない。

`next_action.forbidden_files` を確認し、どのファイルが禁止変更として検出されたかを利用者に報告する。

初期実装では、post-write-verification 対象ファイルが未コミット変更に含まれる状態で、`tools/*.py` の未追跡ファイルがあると逸脱になる。これは、独自検証 runner や一時ツールを作って外部 API 呼び出しへ進む逸脱を止めるためである。

### `stage`

通常ワークフロー上の次タスクが決まっている。

この場合、次のフィールドに従う。

- `feature`
- `phase`
- `stage`

例：

```json
{
  "kind": "stage",
  "feature": "evaluation",
  "phase": "implementation",
  "stage": "drafting"
}
```

この例では、`evaluation` 機能の `implementation.drafting` に着手する。

### `cross_feature_stage`

機能横断段に進む。

`feature` は `all_features` になる。`phase` と `stage` を確認し、全機能を対象にした review-wave、alignment、approval などを実施する。

### `completed`

全 workflow_state が完了している。

通常の次タスクはない。利用者へ完了状態を報告する。

### `unknown`

必要な `spec.json` が不足しているなど、状態判定できない。

この場合、推測で進めてはいけない。`reasons` と `current_state` を確認し、利用者に状況を報告する。

## 3. Claude が守るべき作業規則

1. `next` を実行せずに次作業を提案しない。
2. `next_action.kind` が `resume_in_progress` のとき、新規作業を始めない。
3. `next_action.kind` が `post_write_verification` のとき、検証を実施するまで通常ワークフローへ進まない。
4. `next_action.kind` が `stage` または `cross_feature_stage` のとき、その feature、phase、stage だけを扱う。
5. `spec.json.workflow_state` の変更、commit、push は不可逆操作として扱い、別途 `check-workflow-action.py` の該当サブコマンドで事前検査する。
6. commit と push は、利用者の運用方針に従い、人間が行う。Claude は勝手に実行しない。
7. post-write-verification のために、新しい runner、検証スクリプト、一時ツールを作成しない。既存の検証手段がない場合は、作成せずに利用者へ確認する。
8. 外部 API 呼び出し、ネットワーク通信、API キー利用を伴う検証は、利用者の明示承認なしに実行しない。
9. `next_action.kind` が `post_write_policy_violation` のとき、禁止変更の内容を報告して停止する。禁止ファイルを勝手に削除・修正してはいけない。

## 4. 典型的な作業開始手順

```bash
python3 tools/check-workflow-action.py next --json
```

その後、結果に応じて進める。

`post_write_verification` が返った場合：

```text
1. target_files を確認する
2. 対象ファイルの変更内容を確認する
3. 既存の検証手段と実行権限があるか確認する
4. 実行権限があれば、書き込み後検証を実施する
5. 実行権限がなければ、検証未完了として利用者へ報告する
6. 未解決の本質的指摘があれば利用者へ確認する
7. 検証が終わるまで通常ワークフローへ戻らない
```

`stage` が返った場合：

```text
1. feature / phase / stage を確認する
2. 該当 feature の spec.json と関連仕様を読む
3. TDD が必要な実装作業では、先にテストを書く
4. その stage の完了条件だけを満たす
5. stage 完了後、必要な検査を行って利用者へ報告する
```

## 5. 現在の制限

このナビゲータは、現時点では ReviewCompass 固有のワークフローを対象とする。

任意の workflow graph、reopen の trigger_map 解決、post-write-verification の完了認定 manifest はまだ未実装である。

そのため、`next` は「次に何を優先すべきか」を返すが、検証内容の妥当性や人間承認の有無を完全には判定しない。
