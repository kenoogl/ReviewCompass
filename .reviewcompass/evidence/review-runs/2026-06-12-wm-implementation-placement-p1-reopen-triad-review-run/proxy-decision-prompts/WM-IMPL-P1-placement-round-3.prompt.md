# proxy_model 判断依頼：wm implementation triad-review round-3 の三段階トリアージと収束判定

あなたは ReviewCompass の proxy_model（人間判断の代行役）である。round-3 では判定役（gemini）所見ゼロ、
敵対役（gpt-5.5）ERROR1、主役（claude）INFO3。4 所見の最終ラベルと round-4 の要否を判断せよ。不可逆操作は範囲外。

## 事実確認

- 【N1】resolver は旧配置形式の入力（例：P1 前の記録が保持する `.reviewcompass/effective-prompts/...`）をそのまま返す。
  凍結期に同名 prompt が新配置にも存在する場合、契約（新旧競合時は新を正）に反して旧の sha を採用し得る（指摘どおり）。
  修正は小規模：旧形式入力を新形式へ正規化してから新→旧の順で存在確認する。
- 【N3】check-workflow-action.py は placement_freeze を import しておらず、フック複製に含めない現状で実害なし。
- 【N4】M5 対応（git 失敗の平易な再送出）は実装済み。運用手順書への出力例 1 行は任意の改善。

## クラスタと候補案

### N1：旧形式パス入力で新配置優先が働かない（gpt-5.5-adversarial-001〔ERROR〕・claude-sonnet-4-6-primary-001〔INFO、同根＝入力域の境界とテスト欠落〕）
- A：resolver を双方向対応にする（旧形式入力を新形式へ正規化し新→旧で存在確認。新形式・旧形式・絶対パスの境界テストを追加。
  docstring 追従。操縦 LLM の推薦案）
- B：leave-as-is（呼び出し元が新形式のみを渡す前提を維持）

### N3：フック複製と配布一覧の対称性（claude-sonnet-4-6-primary-002、INFO）
- A：leave-as-is（フックの複製は実際の import 依存だけを最小コピーする方針。配布一覧はパッケージ全体で将来依存にも安全。
  操縦 LLM の推薦案）／ B：placement_freeze もフック複製へ追加

### N4：手動手順への例外時出力例の追記（claude-sonnet-4-6-primary-003、INFO）
- A：leave-as-is（M5 の平易メッセージで足りる。操縦 LLM の推薦案）／ B：手順書に 1 行追記

### 収束判定：round-4 の要否
- R4-A：N1 適用後に round-4 を実行して収束確認する（操縦 LLM の推薦案：N1 は挙動変更を伴う must-fix 候補のため、
  適用後の確認 round を 1 回置くのが安全）
- R4-B：round-4 を省略して収束とみなす

## 元レビュー raw（全文）

### raw/gpt-5.5.round-3.txt（敵対役）

findings:
  - severity: ERROR
    target_location: "tools/check_workflow_action/runtime_paths.py:resolve_effective_prompt_read_path"
    description: "effective prompt の resolver が、新配置形式の相対パスに対してのみ新→旧フォールバックを適用しており、旧配置形式のパスを渡された場合は新配置を確認せず旧配置を返す。"
    rationale: "P1 の確定契約は、3 パスの読み取りを新→旧順とし、新旧競合時は新配置を採用することを求めている。P1 前の記録や互換読み取り経路が `.reviewcompass/effective-prompts/...` 形式の旧パスを保持している場合、runtime 側に同名 prompt が存在しても旧 prompt の sha を計算・採用し得るため、run_role の実運用読み取りで契約違反になる。旧配置形式も対応する新配置へ正規化してから新優先で存在確認する必要がある。"

### raw/claude-sonnet-4-6.round-3.txt（主役）

findings:
  - severity: INFO
    target_location: "tools/check_workflow_action/runtime_paths.py: resolve_effective_prompt_read_path"
    description: "resolve_effective_prompt_read_path は入力が新配置形式（DEFAULT_EFFECTIVE_PROMPT_DIR + '/' 始まり）でない場合にそのまま返すと docstring に明記されているが、旧配置形式のパスや絶対パスが渡された場合の挙動についてテストが存在しない。"
    rationale: "境界条件カバレッジとして軽微な欠落。契約上の主要パスは全てカバーされており障害リスクは低いが、将来の利用者が誤った前提でこの関数を呼び出すリスクを低減するためにテストの追加が望ましい。"

  - severity: INFO
    target_location: "tests/hooks/test_pre_bash_precheck.py: _setup_git_repo_with_script"
    description: "フックテストの一時リポジトリへコピーされるのは runtime_paths.py のみで、placement_freeze.py は含まれていない。現時点でフックテストが placement_freeze を直接 import しないなら問題ないが、将来的に check-workflow-action.py が placement_freeze を参照する場合に ModuleNotFoundError が発生する可能性がある。"
    rationale: "現時点では check-workflow-action.py は placement_freeze を import していないため実害はない。ただし deploy-manifest.yaml で tools/check_workflow_action/** を追加済みであることと対称性が保たれておらず、保守上の注意点として記録する。"

  - severity: INFO
    target_location: "tools/check_workflow_action/placement_freeze.py: _matching"
    description: "_matching は git コマンドの戻り値が returncode != 0 の場合に ValueError を送出するが、check_runtime_placement_freeze の呼び出し元へ伝播する例外を catch している箇所がない。WORKFLOW_PRECHECK_DETAILS.md §8.1 の手動実行手順でも例外が素通りになる。M5 対応（git 失敗を平易なメッセージで再送出）は placement_freeze.py 内に実装済みで規約どおりだが、上位での catch に関する記述がドキュメント手順に無い。"
    rationale: "運用手順書に例外伝播の注意（例：freeze_commit 指定誤りの場合の出力例）を一行追加すると利用者体験が向上する。機能的な誤りではないため INFO とする。"

### raw/gemini-3.1-pro-preview.round-3.txt（判定役）

findings: []

## 回答形式（厳守）

次の YAML だけを返す。4 所見＋round_4。finding_id は完全 ID
（接頭辞 2026-06-12-wm-implementation-placement-p1-reopen-triad-review-run-）。
値に YAML として不正な書き出しを使わない。

```yaml
decisions:
  - finding_id: <完全な finding_id>
    cluster_id: <N1|N3|N4>
    selected_option: <A|B>
    final_label: <must-fix|should-fix|leave-as-is>
    rationale: <採用理由 1-3 文>
    rejected_options:
      <記号>: <棄却理由>
round_4:
  selected_option: <R4-A|R4-B>
  rationale: <理由 1-2 文>
```
