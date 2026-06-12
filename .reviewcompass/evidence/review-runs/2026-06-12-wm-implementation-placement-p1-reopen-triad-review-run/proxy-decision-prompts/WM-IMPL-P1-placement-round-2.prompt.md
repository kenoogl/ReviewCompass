# proxy_model 判断依頼：wm implementation triad-review round-2 の三段階トリアージ

あなたは ReviewCompass の proxy_model（人間判断の代行役）である。round-2（round-1 の 7 採用適用後の収束確認）では
判定役（gemini）所見ゼロ、敵対役（gpt-5.5）ERROR1/WARN2、主役（claude）INFO3。6 所見を判断せよ。不可逆操作は範囲外。

## 操縦 LLM による事実確認

- 【M1・反証済み】run_role.py はモジュール冒頭で自身の位置からプロジェクトルートを sys.path へ挿入する
  （`_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent`）。リポジトリ外の cwd（/tmp 配下）から
  スクリプト位置指定で読み込み、旧配置のみにプロンプトを置いて `_resolve_effective_prompt_sha256` を実行した結果、
  ModuleNotFoundError は発生せず旧配置の sha を正しく返した（returncode 0）。指摘のシナリオは実機で再現しない。
- 【M2】検査ログにはツール側の読み取り経路が存在しない（追記専用）。契約は「3 パスとも読み取り新→旧」。
- 【M3】guarded-git-commit の消費はフォールバックを手書きしており、共有 resolver（resolve_commit_approval_path）と
  論理が重複している（指摘どおり）。

## クラスタと候補案

### M1：run_role の import がスクリプト実行で壊れるとの指摘（gpt-5.5-adversarial-001、ERROR）
- A：leave-as-is（上記の実証により再現しない。検証手順を triage に記録。操縦 LLM の推薦案）
- B：防御的に try-except とパス直解決の二重化を追加
- 利点と弱点：B は実害のない複雑化（重複ロジック追加は K1 の集約方針と逆行）。

### M2：検査ログの読み取り resolver とテストが無い（gpt-5.5-adversarial-002、WARN）
- A：runtime_paths に `resolve_precheck_log_read_path(cwd)`（新→旧）を追加しテストを付ける（読み手＝人間・外部ツールに
  契約どおりの解決を提供。操縦 LLM の推薦案）
- B：leave-as-is（ツール自身は追記のみ）

### M3：guarded の消費が共有 resolver を使っていない（gpt-5.5-adversarial-003、WARN）
- A：consume_commit_approval の読み取り解決を resolve_commit_approval_path へ置換（操縦 LLM の推薦案）
- B：leave-as-is

### M4：resolver の引数型契約（str/Path）が不明確（claude-sonnet-4-6-primary-001、INFO）
- A：docstring に「str または Path を受け、内部で str 化する」を明記（操縦 LLM の推薦案）／ B：leave-as-is

### M5：freeze_commit 不正時に git の生エラーが出る（claude-sonnet-4-6-primary-002、INFO）
- A：CalledProcessError を捕捉して平易なメッセージで再送出（操縦 LLM の推薦案）／ B：leave-as-is（手動手順の入力ミス時の体験のみの問題）

### M6：テストの os.chdir が並列実行で干渉し得る（claude-sonnet-4-6-primary-003、INFO）
- A：leave-as-is（現行構成では影響なし、所見も将来リスクの記録と明言。操縦 LLM の推薦案）／ B：今すぐ書き換え

## 元レビュー raw（全文）

### raw/gpt-5.5.round-2.txt（敵対役）

findings:
  - severity: ERROR
    target_location: "tools/api_providers/run_role.py::_resolve_effective_prompt_sha256"
    description: "The effective-prompt fallback import uses `from tools.check_workflow_action.runtime_paths ...`, but the added test masks direct-script import behavior by injecting the repository root into `sys.path`."
    rationale: "If `run_role.py` is invoked as a script path such as `python tools/api_providers/run_role.py`, the repository root is not guaranteed to be importable as the top-level `tools` package. In that mode, path-based SHA resolution can raise `ModuleNotFoundError` before applying the required new→old fallback, breaking the P1 runtime-path read-compatibility contract on an operational API-provider path."
  - severity: WARN
    target_location: "tools/check_workflow_action/runtime_paths.py; tests/tools/test_runtime_placement_freeze.py::PrecheckLogPlacementTests"
    description: "The shared runtime path module does not provide a new→old read resolver for `workflow-precheck.log`, and the log tests only verify write placement/preservation rather than log read fallback."
    rationale: "The upstream contract describes all three runtime artifacts as reading new→old with new winning on conflict. Commit approvals and effective prompts have explicit read resolution, but the precheck log path has no equivalent implementation or test coverage. Any consumer that needs to read historical legacy logs after P1 would miss `docs/logs/workflow-precheck.log`."
  - severity: WARN
    target_location: "tools/guarded-git-commit.py::consume_commit_approval"
    description: "Commit-approval read fallback is still hand-coded in `guarded-git-commit.py` instead of using the shared `resolve_commit_approval_path` resolver."
    rationale: "Round-2 K1 states that constants and read resolution are centralized in `runtime_paths.py`. Duplicating the new→old fallback logic creates drift risk, especially for the P3 compatibility-removal transition or future path changes."

### raw/claude-sonnet-4-6.round-2.txt（主役）

findings:
  - severity: INFO
    target_location: "tools/check_workflow_action/runtime_paths.py: resolve_effective_prompt_read_path"
    description: "relative_path の型が str と Path の両方を受け入れるが、型注釈・docstring には str を想定するとのみ記載されており、Path オブジェクトが渡された場合の str() 変換は実装内で行われているが明示されていない。"
    rationale: "run_role.py では Path(path_value) で渡す可能性があり、startswith の引数が Path オブジェクトだと意図どおり動作しない。実際は str(relative_path) で変換しているため動作上の問題はないが、呼び出し側の型契約が不明確なため将来の誤用リスクがある。"

  - severity: INFO
    target_location: "tools/check_workflow_action/placement_freeze.py: _matching 関数"
    description: "subprocess.run に check=True を指定しているため、freeze_commit が無効なコミットハッシュの場合（初回実行・浅いクローン等）に CalledProcessError が捕捉されず呼び出し元で未処理の例外となる。"
    rationale: "WORKFLOW_PRECHECK_DETAILS.md §8.1 の手動実行手順では freeze_commit を利用者が直接指定するため、入力ミス時のエラーメッセージが git の生エラーのまま表示される。ユーザビリティ上の懸念であり、凍結違反の検出精度には影響しない。"

  - severity: INFO
    target_location: "tests/tools/test_runtime_placement_freeze.py: RunRoleEffectivePromptFallbackTests.test_sha_resolution_falls_back_to_legacy_prompt"
    description: "os.chdir で作業ディレクトリを変更しており、テスト失敗時に finally が実行される前に例外が発生した場合でも os.chdir(previous) は finally で保護されているため問題ないが、並列テスト実行（pytest-xdist 等）では同一プロセス内の他テストに影響する可能性がある。"
    rationale: "現行のテスト実行構成（912 件の通常実行）では影響なし。並列実行を将来導入する際の潜在的な干渉リスクとして記録する。"

### raw/gemini-3.1-pro-preview.round-2.txt（判定役）

findings: []

## 回答形式（厳守）

次の YAML だけを返す。6 所見すべてに 1 エントリずつ。finding_id は完全 ID
（接頭辞 2026-06-12-wm-implementation-placement-p1-reopen-triad-review-run-）。
値に YAML として不正な書き出しを使わない。

```yaml
decisions:
  - finding_id: <完全な finding_id>
    cluster_id: <M1-M6>
    selected_option: <A|B>
    final_label: <must-fix|should-fix|leave-as-is>
    rationale: <採用理由 1-3 文>
    rejected_options:
      <記号>: <棄却理由>
```
