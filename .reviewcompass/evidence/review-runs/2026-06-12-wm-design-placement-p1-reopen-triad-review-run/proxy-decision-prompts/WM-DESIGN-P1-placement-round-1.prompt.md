# proxy_model 判断依頼：wm design triad-review round-1 の三段階トリアージ

あなたは ReviewCompass の proxy_model（人間判断の代行役）である。workflow-management の design 正本修正
（パス契約 5 箇所の runtime 区画移行、reopen D-0 第3過程）への round-1 所見 7 件（3 同根クラスタ）について、
候補案から採用案を選び、最終ラベル（must-fix／should-fix／leave-as-is）を決定せよ。不可逆操作の判断は範囲外。

## 操縦 LLM による事実確認

- 【W1 関連】design 本文の 3 箇所の由来注記のうち、「旧パス読み取り互換は P3 まで維持」が明記されているのは
  precheck ログと commit 承認記録の 2 箇所のみで、effective prompt の注記には欠落している（差分で確認済み）。
  「既存分は旧置き場で凍結」「効力発生時点」「暗黙の終了はない」は 3 箇所とも design 本文に未明記
  （レビュー対象文書の説明にのみ存在）。同じ配置規約 P1 の ce reopen では、design 本文に凍結・互換・効力発生・
  暗黙終了なしを明記する形式が確定済み（先行事例）。
- 【W2 関連・事実確認済み】決定台帳（docs/notes/2026-06-12-document-placement-stage2-decisions.md）の定義：
  PLC-DEC-004＝3 区画分割（runtime＝effective-prompts・approvals・ログ等）、PLC-DEC-005＝「実行時ログ」の
  runtime 集約専用。effective prompt・commit 承認記録は「ログ」ではないため DEC-005 は適用されず、
  **現行注記の決定番号引用は正しい**。「不一致」に見えたのは、操縦 LLM がレビュー対象文書 §1 の趣旨説明で
  3 パスを一括して「PLC-DEC-004〜005・009〜011」と書いた不正確さに起因する。

## 同根クラスタと候補案

### W1：凍結・読み取り互換の契約が design 本文で不揃い／欠落
- 対象所見：gpt-5.5-adversarial-001（ERROR）・gpt-5.5-adversarial-002（ERROR）・gemini-3.1-pro-preview-judgment-001（ERROR）・
  claude-sonnet-4-6-primary-001（WARN）・claude-sonnet-4-6-primary-003（INFO）の 5 件（同根）
- 候補案：
  - A：design に凍結期の共通契約を 1 箇所新設し（「既存分は旧置き場で凍結。効力発生は P1 実装反映コミット〔書き込み先切替〕と
    同時。凍結後の旧置き場への追加・変更はしない。旧パス読み取り互換は 3 パスとも P3 まで維持し、互換の終了は P3 の専用
    reopen における本設計の改訂として扱う〔暗黙の終了はない〕」）、3 箇所の注記から参照する。effective prompt の注記には
    互換維持の文言を補う（操縦 LLM の推薦案。ce reopen の確定形式と整合し、文言の重複を避ける）
  - B：3 箇所の注記それぞれに完全な凍結・互換文言を複製する
  - C：現状維持（凍結・互換はレビュー対象文書と運用に委ねる）
- 利点と弱点：A は正本 1 箇所で契約が読め、P3 終了判断の参照先が一意。B は冗長で改訂時に 3 箇所の同期が必要。
  C は ERROR 3 件の指摘（実装・運用が旧証跡を変更し得る、互換期間の揺れ）が未解決のまま残る。

### W2：PLC-DEC-005 参照の不一致（gpt-5.5-adversarial-003、WARN）
- 候補案：
  - A：leave-as-is（事実確認のとおり現行注記の決定番号は正しい。DEC-005 は実行時ログ専用で effective prompt・承認記録には
    非適用。トリアージ記録に事実確認を残す。操縦 LLM の推薦案）
  - B：3 箇所の注記の決定番号をすべて「004〜005」へ揃える（誤った適用拡大）
- 利点と弱点：B は決定台帳と矛盾する引用になり追跡性をかえって損なう。

### W3：フローチャートのラベルに由来注記がない（claude-sonnet-4-6-primary-002、INFO）
- 候補案：
  - A：leave-as-is（図は情報密度の低い形式で、由来注記は本文注記が正本。所見自身も許容範囲と認めている。操縦 LLM の推薦案）
  - B：図ラベルにも注記を追加
- 利点と弱点：B は図の可読性を下げる。

## 元レビュー raw（全文）

### raw/claude-sonnet-4-6.round-1.txt（主役）

findings:
  - severity: WARN
    target_location: "design.md § effective-prompts パス変更箇所（行 +323付近）"
    description: "effective-prompts の旧パス読み取り互換（P3 まで維持）の明記が欠落している。commit-approval（行 +1064）とworkflow-precheck.log（行 +61）には『旧パス読み取り互換は P3 まで維持』が明記されているが、effective-prompts の変更注記には『実行時生成物の runtime 区画集約』のみで互換維持期間の記述がない。"
    rationale: "3 パスの扱いは統一された契約（ce reopen で確定した形式）に従うべきであり、effective-prompts だけ互換維持の終了条件が明示されないと、P3 到達時の廃止判断・移行処理で扱いが揺れるリスクがある。レビュー観点 2（由来注記・凍結・読み取り互換の一貫性）への抵触。"

  - severity: INFO
    target_location: "design.md §フローチャート（Pass → Log ノード、行 +85付近）"
    description: "フローチャートの Log ノードは新パスへ更新済みだが、WARN/DEVIATION 経路の Block → Log も同一ノードを参照するため変更は最小限で正しい。ただし Log ノードのラベルに由来注記が含まれておらず、差分の他 2 箇所と記述粒度が異なる。"
    rationale: "フローチャートはテキスト注記より情報密度が低い形式であり、由来注記がない点は許容範囲だが、一貫性を好む立場からは補足余地がある。重大な欠陥ではないため INFO。"

  - severity: INFO
    target_location: "design.md §凍結・旧パス読み取り互換の終了条件（レビュー観点 5）"
    description: "読み取り互換の終了条件として『P3 まで維持（暗黙の終了はない）』と target.md §1 に記述されているが、design.md 本文には『P3 まで維持』のみで『暗黙の終了はない（明示終了が必要）』という積極的な意図が書かれていない。"
    rationale: "将来の P3 完了時に明示終了処理を省略するミスを防ぐ観点では、design に終了条件の明示方法（誰が・何をもって終了とするか）を一文添えることが望ましい。現状は欠如というより省略であり INFO 扱い。"

### raw/gpt-5.5.round-1.txt（敵対役）

findings:
  - severity: ERROR
    target_location: ".reviewcompass/specs/workflow-management/design.md: paragraph beginning `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml`"
    description: "effective prompt の runtime 移動について、旧 `.reviewcompass/effective-prompts/` の読み取り互換を P3 まで維持する契約が design 本文に明記されていない"
    rationale: "レビュー対象の前提では 3 パスすべてで旧パス読み取り互換を P3 まで維持するとしているが、effective prompt の変更箇所だけ互換期間が欠落している。implementation 段で既存の `rounds.yaml` や証跡が参照する旧 `effective_prompt_path` を読めなくする実装になり得るため、P1 の runtime path contract として不完全。"
  - severity: ERROR
    target_location: ".reviewcompass/specs/workflow-management/design.md: runtime path changes for workflow-precheck.log, effective-prompts, commit-approval.json"
    description: "旧置き場の既存生成物を凍結する契約が design 差分内に明記されていない"
    rationale: "レビュー対象の説明では「既存分は旧置き場で凍結」としているが、design の変更行には凍結の効力発生時点や、旧パス上の既存ファイルを移動・上書き・追記しないことが記録されていない。正本 design にない場合、implementation や運用で旧ログ・旧承認記録・旧 effective prompt を変更対象にしてしまい、過去証跡の不変性を損なう。"
  - severity: WARN
    target_location: ".reviewcompass/specs/workflow-management/design.md: effective prompt and commit approval provenance annotations"
    description: "配置規約の由来注記が path 種別間で不一致で、effective prompt と commit approval では PLC-DEC-005 が参照されていない"
    rationale: "レビュー対象の趣旨は PLC-DEC-004〜005・009〜011 の反映だが、workflow-precheck.log だけ PLC-DEC-004〜005・009〜011 を参照し、effective prompt と commit approval は PLC-DEC-004・009〜011 に留まっている。PLC-DEC-005 が非適用である理由がない限り、後続レビューや実装でどの決定に基づく runtime 配置変更か追跡しにくくなる。"

### raw/gemini-3.1-pro-preview.round-1.txt（判定役）

findings:
  - severity: ERROR
    target_location: "design.md 差分 (Lines 64, 323, 1064)"
    description: "由来注記にて「既存分の凍結」の記述が全箇所で欠落しており、effective-promptsの箇所では「P3までの読み取り互換」の記述も欠落している"
    rationale: "レビュー観点2「由来注記・凍結・読み取り互換（P3 まで）の明記が一貫しているか」および観点5「例外系・境界条件（凍結の効力発生時点、読み取り互換の終了条件）」を満たしていない。ce reopen事例で確定した「既存分は旧置き場で凍結」「旧パス読み取り互換は P3 まで維持（暗黙の終了はない）」という重要な制約が、対象ドキュメントの各注記に一貫して反映されておらず、実装時の要件漏れや運用時の混乱を招くリスクがある。"

## 回答形式（厳守）

次の YAML だけを返す。7 所見すべてに 1 エントリずつ。finding_id は完全 ID
（接頭辞 2026-06-12-wm-design-placement-p1-reopen-triad-review-run-）。
値に YAML として不正な書き出し（引用符・バッククォート始まり等）を使わないこと。

```yaml
decisions:
  - finding_id: <完全な finding_id>
    cluster_id: <W1-W3>
    selected_option: <A|B|C>
    final_label: <must-fix|should-fix|leave-as-is>
    rationale: <採用理由 1-3 文>
    rejected_options:
      <記号>: <棄却理由>
```
