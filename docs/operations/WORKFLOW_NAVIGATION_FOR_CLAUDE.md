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

### `reopen_in_progress`

`stages/in-progress/` に reopen 手続きの進行中ファイルがある。

この場合、新しい作業を始めてはいけない。post-write-verification や通常ワークフローにも進んではいけない。`next_action.file` に示された reopen 進行中ファイルを正本として扱い、`required_action` に従う。

reopen は遡及手戻りの処理である。通常の feature / phase / stage 作業より優先する。`next_action.kind` が `reopen_in_progress` の間は、`spec.json.workflow_state` から見える通常の次タスクへ進んではいけない。

必ず確認するフィールド：

- `file`：進行中状態ファイル
- `next_step`：reopen 4 過程の現在位置
- `completed_steps`：完了済み過程
- `pending_gates`：再実施すべき alignment / approval
- `current_blocker`：人間承認待ちなどの停止理由
- `required_action`：Claude が次に取るべき行動

`required_action` の読み方：

- `classify_and_rollback_flags`：第1過程。種別判定、根拠記録、進行中ファイル発行、spec.json フラグ差し戻しを扱う。
- `repair_canonical_documents`：第2過程。上流フェーズの正本文書を修正する。
- `rerun_alignment_approval_chain`：第3過程。`pending_gates` に従って alignment / approval の連鎖再実施を行う。
- `wait_for_human_approval`：人間承認待ち。`current_blocker` を報告し、承認なしに進めない。
- `finalize_reopen`：第4過程。最終確認、recheck クリア、in-progress の完了処理を行う。
- `reopen_completed`：reopen 手続きは完了済み。状態ファイルの扱いを確認する。
- `inspect_reopen_state`：判定不能。進行中ファイルを読み、利用者に状況を報告する。

`required_action` が `wait_for_human_approval` の場合、Claude は approval を完了扱いにしてはいけない。`current_blocker` をそのまま利用者へ報告し、承認または指示を待つ。

`required_action` が `rerun_alignment_approval_chain` の場合、`pending_gates` の順序を崩してはいけない。actor=human の approval に到達したら停止する。

`required_action` が `inspect_reopen_state` の場合、推測で処理を進めてはいけない。進行中ファイルの内容、判定不能の理由、必要な利用者判断を報告する。

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

### `post_write_human_decision_required`

post-write-verification manifest に、未解決の本質的指摘が記録されている。

この場合、通常ワークフローへ戻ってはいけない。`next_action.target_files` と `next_action.manifest` を確認し、未解決の本質的指摘について利用者判断を待つ。

Claude は、本質的指摘を独断で逐語的指摘として扱ってはいけない。判断に迷う場合も利用者へ上げる。

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
3. `next_action.kind` が `reopen_in_progress` のとき、reopen 手続きを通常ワークフローより優先する。
4. `next_action.kind` が `post_write_verification` のとき、検証を実施するまで通常ワークフローへ進まない。
5. `next_action.kind` が `stage` または `cross_feature_stage` のとき、その feature、phase、stage だけを扱う。
6. `spec.json.workflow_state` の変更、commit、push は不可逆操作として扱い、別途 `check-workflow-action.py` の該当サブコマンドで事前検査する。
7. commit と push は、利用者の運用方針に従い、人間が行う。Claude は勝手に実行しない。
8. post-write-verification のために、新しい runner、検証スクリプト、一時ツールを作成しない。既存の検証手段がない場合は、作成せずに利用者へ確認する。
9. 外部 API 呼び出し、ネットワーク通信、API キー利用を伴う検証は、利用者の明示承認なしに実行しない。
10. `next_action.kind` が `post_write_policy_violation` のとき、禁止変更の内容を報告して停止する。禁止ファイルを勝手に削除・修正してはいけない。
11. `next_action.kind` が `post_write_human_decision_required` のとき、未解決の本質的指摘について利用者判断を待つ。

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
5. 検証結果を manifest に記録する
6. 実行権限がなければ、検証未完了として利用者へ報告する
7. 未解決の本質的指摘があれば利用者へ確認する
8. 検証が終わるまで通常ワークフローへ戻らない
```

post-write-verification manifest は `.reviewcompass/post-write-verification/*.yaml` に置く。`next` は manifest を読み、完了済みなら通常ワークフローへ戻る。

manifest は検証完了の自己申告ではなく、`next` が読む状態ファイルである。対象ファイル、必要検証者、完了検証者、未解決の本質的指摘数を正しく記録する。

同じ対象ファイルを覆う manifest が複数ある場合、`next` はファイル名の辞書順で新しいものを優先する。命名は `post-write-YYYY-MM-DD-NNN.yaml` の形にする。

最小フィールド：

```yaml
status: completed
target_files:
  - docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md
required_verifiers:
  - google
completed_verifiers:
  - google
unresolved_substantive_findings: 0
```

未解決の本質的指摘がある場合：

```yaml
status: pending_human
target_files:
  - docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md
required_verifiers:
  - google
completed_verifiers:
  - google
unresolved_substantive_findings: 1
```

この場合、`next` は `post_write_human_decision_required` を返す。Claude は通常ワークフローへ戻らず、利用者判断を待つ。

`stage` が返った場合：

```text
1. feature / phase / stage を確認する
2. 該当 feature の spec.json と関連仕様を読む
3. TDD が必要な実装作業では、先にテストを書く
4. その stage の完了条件だけを満たす
5. stage 完了後、必要な検査を行って利用者へ報告する
```

`reopen_in_progress` が返った場合：

```text
1. file に示された stages/in-progress/*.yaml を読む
2. next_step / completed_steps / pending_gates / current_blocker を確認する
3. required_action に従って次作業を決める
4. wait_for_human_approval なら承認待ちとして利用者へ報告する
5. rerun_alignment_approval_chain なら pending_gates の順序で進める
6. inspect_reopen_state なら推測で進めず、判定不能として報告する
```

## 5. reopen-start の使い方

所見が遡及手戻りであることと手戻り種別が決まっている場合、`reopen-start` で `stages/in-progress/` ファイルを生成できる。

Claude は、所見の意味分類や手戻り種別を独断で確定してはいけない。利用者判断または記録済みの分類根拠がある場合だけ実行する。

例：

```bash
python3 tools/check-workflow-action.py reopen-start \
  --classification D-1 \
  --feature runtime \
  --basis docs/reviews/reopen-classification-2026-06-02.md \
  --date 2026-06-02 \
  --trigger "design で requirements の不整合を検出" \
  --json
```

`reopen-start` は trigger_map から `pending_gates` を解決し、次のような進行中ファイルを生成する。

```yaml
process_id: reopen-procedure
feature: runtime
classification: D-1
classification_basis: docs/reviews/reopen-classification-2026-06-02.md
completed_steps: []
next_step: 第1過程：判定とフラグ差し戻し
step_number: 1
pending_gates:
  - stages/requirements.yaml#alignment
  - stages/requirements.yaml#approval
  - stages/design.yaml#alignment
  - stages/design.yaml#approval
current_blocker: null
```

`reopen-start` は in-progress 生成までを行う。spec.json のフラグ差し戻しは自動実行しない。

`step_number` は `next_step` の日本語表記ゆれを避けるための補助フィールドである。手動で in-progress ファイルを作る場合も、可能なら `step_number` を併記する。

## 6. 現在の制限

このナビゲータは、現時点では ReviewCompass 固有のワークフローを対象とする。

任意の workflow graph にはまだ対応していない。

post-write-verification については、manifest による完了認定に対応している。ただし、検証者の中身の妥当性そのものは機械判定しない。

reopen については、記録済みの手戻り種別から `reopen-start` で trigger_map を解決し、in-progress ファイルを生成できる。ただし、所見から手戻り種別を自動分類すること、spec.json のフラグ差し戻しを自動実行することは未実装である。

そのため、`next` は「次に何を優先すべきか」を返すが、検証内容の妥当性や人間承認の有無を完全には判定しない。
