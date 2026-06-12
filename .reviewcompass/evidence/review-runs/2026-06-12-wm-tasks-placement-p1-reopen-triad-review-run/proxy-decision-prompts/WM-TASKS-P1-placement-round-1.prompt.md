# proxy_model 判断依頼：wm tasks triad-review round-1 の三段階トリアージ

あなたは ReviewCompass の proxy_model（人間判断の代行役）である。workflow-management tasks の修正
（4 箇所、reopen D-0 第3過程）への round-1 所見 11 件について判断せよ。不可逆操作の判断は範囲外。

## 操縦 LLM の整理

11 件はすべて同根クラスタ **X1＝design の凍結期共通契約（承認済み）の tasks 翻訳欠落** の側面である：

- (a) 3 パス全部（検査ログ・effective prompt・commit 承認記録）の新配置書き込みとテスト要求（gpt-001 ERROR・gemini-002 ERROR・claude-002 WARN）
- (b) 旧配置への新規書き込み禁止（凍結契約）の責務・テスト要求（gpt-002 ERROR・gemini-001 ERROR・claude-003 INFO）
- (c) 読み取り互換の探索順「新→旧」の明記（gpt-003 ERROR・gemini-001 ERROR・gpt-004 WARN）
- (d) 境界条件（凍結の効力発生＝P1 実装反映コミットと同時、互換終了＝P3 専用 reopen・暗黙終了なし）の翻訳（gemini-003 WARN・claude-004 INFO）
- (e) commit 承認記録の旧パス明示（claude-001 WARN）

先行事例：同じ配置規約 P1 の ce reopen では、tasks round-1 の同型指摘（design 新機構のタスク翻訳欠落 C7）が
must-fix となり、タスク責務・テスト要件への追記で解消した（確定形式あり）。

## 候補案

- A：T-004 の責務とテスト要件へ、ce の確定形式に倣い一括追記する（操縦 LLM の推薦案）：
  - 責務へ：実行時生成物 3 パスの書き込みは常に新配置とし、旧配置（docs/logs/workflow-precheck.log・
    .reviewcompass/effective-prompts/・.reviewcompass/approvals/commit-approval.json）への新規書き込みを行わない
    （凍結契約。効力発生は P1 実装反映コミット＝書き込み先切替と同時。互換の終了は P3 の専用 reopen における設計改訂として
    扱い、暗黙の終了はない。正本は design §実行時生成物の凍結期（P3 まで）の扱い）。読み取りは新配置優先・旧配置フォールバック
    （新→旧の順、3 パスとも P3 まで）
  - テスト要件 5 へ：凍結期挙動テスト＝3 パスそれぞれについて (1) 新配置への書き込み (2) 旧配置への新規書き込みが
    発生しないこと (3) 旧パスにしか記録がない場合の新→旧フォールバック読み取り（計 9 観点）
  - 補足の判断材料：旧配置への「違反検出機構」（git 履歴判定など）は ce 側の機械検査（MV）が評価記録系で担う設計で、
    wm design の共通契約は自ツールの書き込み挙動の規定に留まる。よって wm tasks では「旧配置への新規書き込みが
    発生しないこと」の動作検証までを要求し、検出機構の新設は要求しない（design を超える追加を避ける）
- B：テスト要件 5 の拡張のみ（責務は現状維持）
- C：現状維持

## 元レビュー raw（全文）

### raw/gpt-5.5.round-1.txt（敵対役、ERROR3/WARN1）

findings:
  - severity: ERROR
    target_location: ".reviewcompass/specs/workflow-management/tasks.md T-004 テスト要件 5"
    description: "テスト要件が runtime/logs のログ追記に偏っており、effective prompt と commit 承認記録の新配置書き込みを機械検証する要求がない"
    rationale: "design 確定契約は `.reviewcompass/runtime/logs/`、`.reviewcompass/runtime/effective-prompts/`、`.reviewcompass/runtime/approvals/commit-approval.json` の 3 パスすべてを P1 で新配置へ書き込む契約としている。現行のテスト要件 5 はログだけを明示しているため、implementation で effective prompt や commit 承認記録が旧パスへ書かれ続けても tasks 上の受入で検出できない。"
  - severity: ERROR
    target_location: ".reviewcompass/specs/workflow-management/tasks.md T-004 責務およびテスト要件 5"
    description: "旧配置への新規書き込み禁止と既存旧配置の凍結保全を検証するタスク／テスト要件が不足している"
    rationale: "design の凍結期共通契約は、P1 実装反映コミット以後は常時新配置へ書き、既存旧配置は凍結し、旧配置への新規書き込みを許さないことを含む。tasks では『既存配置は凍結保全』『旧パス読み取り互換』への言及はあるが、旧パスに新規作成・追記・更新しないこと、旧ファイルの内容・mtime 等を保全すること、違反時の扱いを機械検証する要求が明示されていない。"
  - severity: ERROR
    target_location: ".reviewcompass/specs/workflow-management/tasks.md T-004 責務"
    description: "旧パス読み取り互換の探索順が design 契約の『新→旧』として明記されていない"
    rationale: "凍結期の読み取り互換は 3 パスとも P3 まで維持するだけでなく、新配置を優先し、存在しない場合に旧配置へフォールバックする『新→旧』順が契約である。tasks では『旧パス読み取り互換は P3 まで維持』との記載に留まり、旧パスが新パスを上書き・優先してしまう実装を排除できない。"
  - severity: WARN
    target_location: ".reviewcompass/specs/workflow-management/tasks.md T-004 テスト要件 5"
    description: "旧パスにしか記録がない場合の読み取り互換テストがログに限定され、3 パス共通の境界条件として定義されていない"
    rationale: "レビュー観点では『旧パスにしか記録がない場合の読み取り』が例外系・境界条件として求められている。現行のテスト要件はログの旧パス読み取り互換のみを示しており、effective prompt と commit 承認記録について同じフォールバック挙動を保証できない。"

### raw/gemini-3.1-pro-preview.round-1.txt（判定役、ERROR2/WARN1）

findings:
  - severity: ERROR
    target_location: "tasks.md 変更差分 (責務およびテスト要件の段落)"
    description: "レビュー観点2および4で求められている「旧配置への新規書き込み禁止（凍結違反の扱い）」と「新→旧の順での読み取り（旧パスにしか記録がない場合の読み取り）」がタスク責務・テスト要件へ翻訳されていない。"
    rationale: "design上の新機構である凍結期共通契約の核心となる振る舞い（書き込みの遮断と読み取りのフォールバック）の明記が欠落しており、TDDにおいてこれらの機械検証が実装されない原因となるため。"
  - severity: ERROR
    target_location: "tasks.md 変更差分 (テスト要件 5)"
    description: "旧パスの読み取り互換を確認するテスト要求が workflow-precheck.log に対してのみ記述されており、effective-prompts と commit-approval.json に対するテスト要件が欠落している。"
    rationale: "実行時生成物3パスすべてにおいて読み取り互換を維持することが確定契約（レビュー観点1）であるため、テスト要件においても3パス全量に対する互換性検証を明示的に要求する必要があるため。"
  - severity: WARN
    target_location: "tasks.md 変更差分 (責務の段落)"
    description: "レビュー観点5で挙げられた例外系・境界条件（凍結の効力発生時点はP1実装反映コミット時であること、互換終了条件はP3専用reopenにおける設計改訂であり暗黙の終了はないこと）が記載されていない。"
    rationale: "ライフサイクルや状態遷移の境界に関する契約がtasksに引き継がれていないと、実装時に効力発生タイミングを誤認したり、将来のフェーズ（P3到達時など）で互換コードを暗黙的に早期削除してしまうリスクがあるため。"

### raw/claude-sonnet-4-6.round-1.txt（主役、WARN2/INFO2）

findings:
  - severity: WARN
    target_location: "T-004 責務（diff +行）commit 承認記録の旧パス読み取り互換"
    description: "commit 承認記録（`.reviewcompass/runtime/approvals/commit-approval.json`）の旧パス読み取り互換について「旧パス読み取り互換は P3 まで維持」と記述されているが、旧パスが何であるかが明示されていない。effective prompt（旧 `.reviewcompass/effective-prompts/`）と workflow-precheck.log（旧 `docs/logs/`）は旧パスが括弧内に明記されているのに対し、commit 承認記録のみ旧パスの記述が欠落している。"
    rationale: "design 確定契約（凍結期共通契約）は「旧パス読み取り互換は 3 パスとも P3 まで維持」と規定している。テスト要件や実装者が旧パスを特定できない場合、互換実装が不完全になるリスクがある。3 パス一貫した旧パス明記がレビュー観点 §2 の変更漏れ検査にも関わる。"

  - severity: WARN
    target_location: "T-004 テスト要件 5（diff +行）"
    description: "テスト要件 5 は「旧パスの読み取り互換を確認するテストを含む」と記載されているが、commit 承認記録（`.reviewcompass/runtime/approvals/commit-approval.json`）の旧パス読み取り互換テストが明示されていない。ログパスの読み取り互換テストのみ言及されており、3 パスの互換テストが揃っていない。"
    rationale: "design 契約では 3 パス全て（検査ログ・effective prompt・commit 承認記録）の読み取り互換が P3 まで必須とされている。テスト要件 5 が commit 承認記録の旧パス互換テストをカバーしていない場合、TDD による互換実装の検証が不完全となる。ce reopen での C7 先行事例（レビュー観点 §2）と同種の翻訳漏れに相当する可能性がある。"

  - severity: INFO
    target_location: "T-004 テスト要件 5（diff +行）"
    description: "「旧パスの読み取り互換を確認するテスト」が新配置への書き込み後に旧パスには新規書き込みを行わない（書き込み禁止）ことの機械検証を含むかどうかが不明瞭である。凍結違反（旧パスへの新規書き込み）を検出するテストの要否が記述されていない。"
    rationale: "design 凍結期共通契約は「書き込み常時新配置」と「既存分は旧置き場で凍結」を両立する契約であり、旧パスへの新規書き込みは凍結違反となる。テスト要件がこの禁止側の検証を要求しているか明確でないと、implementation 段で凍결違反の検出が漏れる可能性がある。"

  - severity: INFO
    target_location: "T-004 責務（diff +行）凍結効力発生時点"
    description: "凍結の効力発生時点（「P1 実装反映コミット＝書き込み先切替と同時」）が tasks 責務・テスト要件のどこにも明示されていない。design 確定契約では効力発生タイミングが境界条件として規定されているが、tasks への翻訳が省略されている。"
    rationale: "レビュー観点 §5（例外系・境界条件）として「凍結の効力発生時点」が明示的に挙げられている。implementation 者がこの境界条件を把握しないと、コミット前後の動作切り替えロジックを誤実装するリスクがある。テスト要件として境界コミット時点の挙動を機械検証可能な形で要求することが望ましい。"

## 回答形式（厳守）

次の YAML だけを返す。11 所見すべてに 1 エントリずつ。finding_id は完全 ID
（接頭辞 2026-06-12-wm-tasks-placement-p1-reopen-triad-review-run-、
モデル別連番は raw の記載順に claude-sonnet-4-6-primary-001〜004・gpt-5.5-adversarial-001〜004・
gemini-3.1-pro-preview-judgment-001〜003）。値に YAML として不正な書き出しを使わない。

```yaml
decisions:
  - finding_id: <完全な finding_id>
    cluster_id: X1
    selected_option: <A|B|C>
    final_label: <must-fix|should-fix|leave-as-is>
    rationale: <採用理由 1-3 文>
    rejected_options:
      <記号>: <棄却理由>
```
