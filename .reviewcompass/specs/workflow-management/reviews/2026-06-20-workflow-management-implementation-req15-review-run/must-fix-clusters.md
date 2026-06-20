# Must-fix clusters: 2026-06-20-workflow-management-implementation-req15-review-run

Req15 の API レビュー結果を、同根の問題ごとにまとめた判断材料です。

## R15-A: prompt audit does not implement the required fail-closed checks

対象所見: 2026-06-20-workflow-management-implementation-req15-review-run-claude-sonnet-4-6-adversarial-001, 2026-06-20-workflow-management-implementation-req15-review-run-claude-sonnet-4-6-adversarial-002, 2026-06-20-workflow-management-implementation-req15-review-run-claude-sonnet-4-6-adversarial-003, 2026-06-20-workflow-management-implementation-req15-review-run-gemini-3.1-pro-preview-judgment-001

平易な説明: effective prompt の監査が、必須構造、壊れた source artifact、未知の action kind、未検証 precondition、不可能 postcondition などを十分に拒否できていませんでした。これでは、以前問題になった弱い API レビュープロンプトを機械的に止めきれません。

候補案:
- A: prompt audit に必須構造と source/precondition/postcondition の fail-closed 検査を追加する（Req15 の目的に直接効く）
- B: 文書規律だけで運用する（軽いが、同じ見落としを機械的に止められない）

推薦案: A
理由: API に渡すプロンプトの品質を機械的に守る入口なので、実行前監査で落とすのが最も確実です。

## R15-B: prompt length boundary semantics are not actually verified

対象所見: 2026-06-20-workflow-management-implementation-req15-review-run-claude-sonnet-4-6-adversarial-004

平易な説明: prompt length のテストが、境界値の不正ではなく別の欠落で失敗していました。テスト名と実際の失敗理由がずれるため、長さ制約の確認ができたように見えてしまいます。

候補案:
- A: 境界値の不正そのものを検査する fixture と監査ロジックに直す（テスト意図と実装が一致する）
- B: 現状の schema 必須項目検査だけに任せる（長さ境界の意味は保証されない）

推薦案: A
理由: prompt の構成品質を扱う Req15 では、境界条件の検査が本当に効いていることが重要です。

## R15-C: machine-task leakage diagnostics are incomplete

対象所見: 2026-06-20-workflow-management-implementation-req15-review-run-claude-sonnet-4-6-adversarial-005, 2026-06-20-workflow-management-implementation-req15-review-run-claude-sonnet-4-6-adversarial-006, 2026-06-20-workflow-management-implementation-req15-review-run-claude-sonnet-4-6-adversarial-007

平易な説明: machine-task leakage の検出はできていますが、複数の違反がある場合に最初の 1 件だけで止まり、診断の全体像が見えにくくなっていました。また、テスト fixture の意図が term list に依存していて読み取りにくい状態でした。

候補案:
- A: 複数違反を収集し、テスト fixture の狙いを明確化する（診断品質が上がる）
- B: 最初の違反だけを返す現状を維持する（実装は軽いが、レビュー後の原因分析が弱い）

推薦案: A
理由: 重大な遮断条件そのものではないものの、再発調査とレビュー結果の説明品質に効きます。

## R15-D: digest format and manifest validation are inconsistent

対象所見: 2026-06-20-workflow-management-implementation-req15-review-run-claude-sonnet-4-6-adversarial-008, 2026-06-20-workflow-management-implementation-req15-review-run-claude-sonnet-4-6-adversarial-009

平易な説明: manifest 側は `sha256:<hex>` 形式、rounds 側は bare hex 形式で記録されており、後続監査で混乱する余地がありました。また、effective prompt builder が生成物を schema に照らして確認していませんでした。

候補案:
- A: rounds 側も prefixed sha を記録し、builder 出力を schema 検証する（追跡形式が揃う）
- B: 形式差を文書化するだけにする（互換性は保てるが、機械監査の負担が残る）

推薦案: A
理由: effective prompt の真正性を後から追えるようにするには、digest 形式と schema 検証を揃えるのが自然です。
