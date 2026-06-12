# proxy_model 判断依頼：wm implementation triad-review round-1 の三段階トリアージ

あなたは ReviewCompass の proxy_model（人間判断の代行役）である。workflow-management implementation
（実行時生成物 3 パスの runtime 区画切替の TDD 実装）への round-1 所見 8 件（6 クラスタ）について判断せよ。
不可逆操作の判断は範囲外。

## 操縦 LLM による事実確認

- 【K1】effective prompt の実運用読み取り経路は tools/api_providers/run_role.py の
  _resolve_effective_prompt_sha256（--effective-prompt-sha256 未指定時にファイルから sha を計算）である。
  ここに新→旧フォールバックは未接続（指摘どおり）。
- 【K3】ReviewCompass 自身では旧 3 パスはすべて gitignore 対象の未追跡ファイルとして現存する。
  `git ls-files --others`（--exclude-standard なし）はこれらを列挙するため、検出器が既存の凍結成果物を
  added_after_freeze と誤検知する（指摘どおり）。先行 ce では旧記録が git 追跡済みだったため
  「ignored を含めて検出」が正解だったが、wm は旧成果物自体が ignored であり前提が異なる。
- 【K5】claude-002 の「削除が検出されない」は誤り：`git diff --name-only <freeze>` は削除も列挙するため
  frozen_file_changed として検出される（テストの unlink ケースで検証済み）。claude-003 の指摘どおり
  「変更と削除が同一ラベル」という意味論の曖昧さは実在する。
- 【K6】claude-001 の「旧の未消費レコードが誤った再承認を許す」リスクは、読み取り解決が新→旧の順であるため
  構造上発生しない：消費後は新配置に consumed:true の記録が必ず存在し、旧の未消費記録を恒久に遮蔽する。

## クラスタと候補案

### K1：effective prompt フォールバックが実運用読み取り経路に未接続（gpt-5.5-adversarial-001、ERROR）
- A：共有モジュール tools/check_workflow_action/runtime_paths.py に定数とフォールバック解決を集約し、
  run_role の _resolve_effective_prompt_sha256 へ接続。check-workflow-action・guarded-git-commit も同モジュールを
  参照して定数の二重定義を解消（操縦 LLM の推薦案）
- B：現状維持（プロンプトの読み手は主に人間・呼び出し元）

### K2：凍結違反検出器がゲート実行経路に未統合（gpt-5.5-adversarial-002、ERROR）
- A：commit／next ゲートへ自動統合（freeze コミットの自動解決が必要、fail-closed 設計の追加検討も必要）
- B：運用文書 docs/operations/WORKFLOW_PRECHECK_DETAILS.md へ手動実行手順（freeze コミット解決例と Python 実行例）を
  記載し、ゲート統合は見送る（先行 ce の C7-B 判断〔CLI 統合はフェーズ方針により見送り・手動手順を文書化〕と同型。
  操縦 LLM の推薦案）
- C：現状維持
- 補足：tasks T-004 の確定要件は「15 観点の機械検証（テスト）」でありゲート統合は要求していない。

### K3：--exclude-standard なしで ignored 既存成果物を誤検知（gemini-3.1-pro-preview-judgment-001、ERROR）
- A：--exclude-standard を付与し ignored を検出対象から外す。未追跡 ignored の旧成果物の凍結は書き込み経路テスト
  （観点 1・2）で担保し、ce との規則差（ce は旧記録が追跡済みのため ignored 込み検出が正しい）を docstring に明記
  （操縦 LLM の推薦案）
- B：現状維持
### K4：approvals の凍結対象がディレクトリ全体（gpt-5.5-adversarial-003、WARN）
- A：パターンを契約どおり commit-approval.json 単体に限定（操縦 LLM の推薦案）／ B：現状維持

### K5：削除の違反種別が変更と同一ラベル（claude-sonnet-4-6-primary-002〔INFO〕・primary-003〔WARN〕、同根）
- A：deleted_after_freeze の専用種別を導入し、削除テストの期待値を専用種別へ更新（claude-002 の「検出されない」は
  事実誤認と注記して棄却。操縦 LLM の推薦案）／ B：現状維持（frozen_file_changed が削除も包含）

### K6：旧配置に未消費レコードが残る非対称（claude-sonnet-4-6-primary-001、INFO）
- A：leave-as-is（新→旧の解決順により新配置の消費済み記録が旧を恒久遮蔽し、再承認リスクは構造上ない。
  理由を triage に記録。操縦 LLM の推薦案）／ B：運用注意の文書追記

### K7：resolve_effective_prompt_read_path の入力前提が未明記（claude-sonnet-4-6-primary-004、INFO）
- A：docstring に入力前提（新配置形式の相対パス）を明記（操縦 LLM の推薦案）／ B：leave-as-is

## 元レビュー raw（全文）

### raw/gpt-5.5.round-1.txt（敵対役）

findings:
  - severity: ERROR
    target_location: "tools/check-workflow-action.py / effective prompt read fallback"
    description: "effective prompt の旧配置フォールバック用関数が追加されているが、実際の読み取り経路に接続されていない"
    rationale: "P1 凍結期契約では effective prompt も読み取り時に新配置→旧配置の順でフォールバックし、新旧競合時は新配置を採用する必要がある。しかし差分上は resolve_effective_prompt_read_path() の追加と単体テストのみで、production のファイル読み取り箇所をこの解決関数へ切り替えた変更が確認できない。このままだと旧配置にのみ存在する effective prompt を実運用で読めず、P3 までの互換契約を満たさない可能性がある。"
  - severity: ERROR
    target_location: "tools/check_workflow_action/placement_freeze.py / check-workflow-action integration"
    description: "旧配置凍結違反検出器が通常の workflow precheck 実行経路に統合されていない"
    rationale: "凍結済み旧成果物の不変性は design/tasks 上の実装契約であり、旧配置への追加・変更・削除を検出できる必要がある。新規モジュール check_runtime_placement_freeze() と直接呼び出しテストは追加されているが、tools/check-workflow-action.py などの実行時検査経路から呼ばれる変更が示されていないため、実際の workflow-management 実行では凍結違反を見逃す可能性がある。"
  - severity: WARN
    target_location: "tools/check_workflow_action/placement_freeze.py: LEGACY_RUNTIME_PATTERNS"
    description: "commit 承認記録の旧配置パターンが .reviewcompass/approvals/ 配下全体を対象にしている"
    rationale: "上流契約で凍結対象として明示されている旧 commit 承認記録は .reviewcompass/approvals/commit-approval.json であり、ディレクトリ配下全体ではない。現実に同ディレクトリへ別用途のファイルが存在する構成では、契約対象外のファイル追加・変更まで凍結違反として扱う過検出になり得るため、対象を commit-approval.json に限定する方が配置契約と整合する。"

### raw/gemini-3.1-pro-preview.round-1.txt（判定役）

findings:
  - severity: ERROR
    target_location: "tools/check_workflow_action/placement_freeze.py"
    description: "untracked ファイルの取得に `--exclude-standard` が指定されておらず、.gitignore 対象の既存ファイルが違反として誤検知される"
    rationale: "`git ls-files --others` はデフォルトで `.gitignore` の指定を無視して全ての未追跡ファイルを出力します。仕様（冒頭注記）では「未追跡の旧成果物の凍結はテストで担保」としていますが、現在の実装では無視対象である既存の旧成果物（ローカルに残っている旧ログなど）が `untracked` に含まれてしまい、`added_after_freeze` として誤検知され凍結違反で異常終了する原因となります。"

### raw/claude-sonnet-4-6.round-1.txt（主役）

findings:
  - severity: INFO
    target_location: "tools/guarded-git-commit.py: consume_commit_approval()"
    description: "旧配置にのみ承認レコードが存在する場合、read_path は旧配置を指すが write_path は常に新配置 (DEFAULT_COMMIT_APPROVAL_PATH) へ固定される。この非対称動作は設計契約（書き込みは常に新配置）に完全準拠しているが、旧配置から読んだレコードの consumed 状態が新配置へ書き出された後も、旧配置の未消費レコードが残り続ける。運用上の二重起動ガード等への影響は P3 完了後に旧配置を削除するまで潜在する。"
    rationale: "契約上は許容された挙動であり違反ではないが、凍結期中に同一セッションで旧レコードを再読取りする経路が残る場合、consumed フラグの不一致が誤った再承認を許可するリスクがある。tasks T-004 の完了条件観点 3（フォールバック読み取り）と観点 1（書き込み常時新配置）の組み合わせ挙動として、運用注意事項として明示しておく価値がある。"

  - severity: INFO
    target_location: "tools/check_workflow_action/placement_freeze.py: _matching() / check_runtime_placement_freeze()"
    description: "deleted（freeze_commit 時点で存在したが現在 git 追跡から消えたファイル）の検出が violations に含まれない。現実装は added（frozen に無くて現在ある）と modified（frozen にあり diff あり）を検出するが、frozen に存在し tracked にも untracked にも無いファイル（削除ケース）は無視される。"
    rationale: "design 契約『凍結済み旧成果物の不変性』には削除も違反に含まれる（追加・変更・削除）と tasks 観点 5 に明記されている。テスト test_changes_deletions_and_additions_are_violations では LEGACY_LOG を unlink しているが、violations 検出のアサートは workflow-precheck.log について frozen_file_changed のみ確認しており deleted ケースの検出アサートは存在しない。実装とテストの双方でこの観点がカバーされていない可能性がある。"

  - severity: WARN
    target_location: "tests/tools/test_runtime_placement_freeze.py: test_changes_deletions_and_additions_are_violations()"
    description: "LEGACY_LOG を unlink() した後の violations アサートが frozen_file_changed を期待しているが、ファイルが削除された場合 git diff --name-only <freeze_commit> は当該ファイルを出力するため changed に含まれ、changed & frozen により frozen_file_changed として検出される。一方、ls-files も ls-files --others も削除済みファイルを返さないため tracked にも untracked にも含まれず added にはならない。この動作は偶発的に正しいが、『削除 = frozen_file_changed』という解釈は変更と削除を区別しない曖昧な命名であり、削除専用の違反種別（deleted_after_freeze 等）が存在しない点は将来の保守で混乱を招く可能性がある。"
    rationale: "tasks T-004 観点 5 は追加・変更・削除を明示的に列挙している。実装が削除を変更と同一ラベル（frozen_file_changed）で報告する場合、違反種別の意味論が設計仕様と乖離し、違反レポートを受け取るツールや人間が削除違反を正確に識別できない。"

  - severity: INFO
    target_location: "tools/check-workflow-action.py: resolve_effective_prompt_read_path()"
    description: "引数 relative_path が新配置形式（DEFAULT_EFFECTIVE_PROMPT_DIR + '/' で始まる）でない場合（例：絶対パス、旧配置パスを直接渡す等）、フォールバック分岐をスキップして relative_path をそのまま返す。呼び出し側が旧配置パスを渡した場合は新配置へのマッピングが行われない。"
    rationale: "現在の呼び出し元が新配置パスのみを渡すことが実装上保証されていれば実害はないが、関数シグネチャと docstring には前提条件の制約が明示されていない。将来の変更で旧配置パスが渡された場合のサイレントな誤動作を防ぐため、入力前提条件の明示またはアサーションの追加が望ましい。"

## 回答形式（厳守）

次の YAML だけを返す。8 所見すべてに 1 エントリずつ。finding_id は完全 ID
（接頭辞 2026-06-12-wm-implementation-placement-p1-reopen-triad-review-run-）。
値に YAML として不正な書き出し（引用符・バッククォート始まり等）を使わないこと。

```yaml
decisions:
  - finding_id: <完全な finding_id>
    cluster_id: <K1-K7>
    selected_option: <A|B|C>
    final_label: <must-fix|should-fix|leave-as-is>
    rationale: <採用理由 1-3 文>
    rejected_options:
      <記号>: <棄却理由>
```
