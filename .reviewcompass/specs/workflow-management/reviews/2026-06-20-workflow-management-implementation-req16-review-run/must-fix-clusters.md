# Must-fix clusters: 2026-06-20-workflow-management-implementation-req16-review-run

Req16 の API レビュー結果を、同根の問題ごとにまとめた判断材料です。

## R16-A: proxy decision checks do not apply human-required predicates before accepting proxy output

対象所見: 2026-06-20-workflow-management-implementation-req16-review-run-gpt-5.4-primary-001, 2026-06-20-workflow-management-implementation-req16-review-run-claude-sonnet-4-6-adversarial-001, 2026-06-20-workflow-management-implementation-req16-review-run-claude-sonnet-4-6-adversarial-002, 2026-06-20-workflow-management-implementation-req16-review-run-claude-sonnet-4-6-adversarial-004

平易な説明: proxy decision の CLI が、人間判断に戻すべき条件を十分に確認しないまま OK を返せる状態でした。証拠不足や矛盾がある場合でも proxy 出力を適用できる余地があります。

候補案:
- A: `check_decision` で human-required 判定と evidence completeness を必ず評価する（proxy 境界を入口で守れる）
- B: schema validation のみで不足を検出する（軽いが、運用上の判断条件を表しきれない）

推薦案: A
理由: proxy モードではユーザが介入しない前提なので、適用入口で human-required 条件を fail-closed にする必要があります。

## R16-B: proxy decision schema does not require enough evidence, coverage, and mapping structure

対象所見: 2026-06-20-workflow-management-implementation-req16-review-run-gpt-5.4-primary-003, 2026-06-20-workflow-management-implementation-req16-review-run-gpt-5.4-primary-007, 2026-06-20-workflow-management-implementation-req16-review-run-claude-sonnet-4-6-adversarial-007

平易な説明: proxy decision の schema が、根拠、coverage、finding-to-operation mapping、approval gate 参照などを必須にしていませんでした。後から判断根拠を追うための構造が不足していました。

候補案:
- A: schema に evidence, coverage, mapping, approval/review-wave references を必須化する（機械監査しやすい）
- B: 自由記述欄に残すだけにする（柔軟だが、欠落を機械的に止められない）

推薦案: A
理由: proxy 判断は証跡を構造化しないと、適用後の検査で根拠不足を検出できません。

## R16-C: approval scope semantics need a narrower rule than simple set equality

対象所見: 2026-06-20-workflow-management-implementation-req16-review-run-gpt-5.4-primary-002, 2026-06-20-workflow-management-implementation-req16-review-run-claude-sonnet-4-6-adversarial-003

平易な説明: triage 決定の承認と修正適用の承認は別物ですが、単純な finding set equality だけでは境界が曖昧になります。ユーザ承認により、より狭い実装ルールとして扱いました。

候補案:
- A: review_triage_decide と apply_fixes の scope 境界を明示し、apply 側でより厳しく検査する（承認流用を防ぎやすい）
- B: set equality のみ維持する（単純だが、承認意味の違いを表しにくい）

推薦案: A
理由: 以前の議論どおり、proxy 前提では承認境界の混同を避ける必要があります。

## R16-D: implementation phase checks do not enforce required snapshot evidence or commit boundary details

対象所見: 2026-06-20-workflow-management-implementation-req16-review-run-gpt-5.4-primary-004, 2026-06-20-workflow-management-implementation-req16-review-run-gpt-5.4-primary-005, 2026-06-20-workflow-management-implementation-req16-review-run-gemini-3.1-pro-preview-judgment-001

平易な説明: implementation phase plan が、snapshot evidence や commit boundary の意味を十分に検査していませんでした。段階が整って見えても、完了根拠が弱いまま進む可能性がありました。

候補案:
- A: phase schema と checker に snapshot evidence、ordered Phase 0-6、commit boundary を必須化する（段階完了の根拠が強くなる）
- B: 既存の phase order check だけに留める（軽いが、証跡の鮮度と境界は保証できない）

推薦案: A
理由: implementation フェーズを機械的に運用するには、段階そのものだけでなく根拠の有無も検査する必要があります。

## R16-E: review-wave consumer impact states are under-modeled

対象所見: 2026-06-20-workflow-management-implementation-req16-review-run-gpt-5.4-primary-008, 2026-06-20-workflow-management-implementation-req16-review-run-claude-sonnet-4-6-adversarial-005, 2026-06-20-workflow-management-implementation-req16-review-run-claude-sonnet-4-6-adversarial-006

平易な説明: review-wave の下流影響は、未解決だけでなく、影響なし、carry-forward、証跡付き解決などの状態を区別する必要がありました。

候補案:
- A: consumer impact の状態を明示的に分けて判定する（後続判断の誤判定を減らせる）
- B: unresolved の有無だけを見る（単純だが、状態の意味を取り違えやすい）

推薦案: A
理由: review-wave は後続作業への接続が重要なので、影響状態を粗く扱うと再判断の品質が落ちます。

## R16-F: operation-list and positive-path CLI coverage are weak

対象所見: 2026-06-20-workflow-management-implementation-req16-review-run-gpt-5.4-primary-006, 2026-06-20-workflow-management-implementation-req16-review-run-claude-sonnet-4-6-adversarial-008, 2026-06-20-workflow-management-implementation-req16-review-run-claude-sonnet-4-6-adversarial-009

平易な説明: operation-list の出力が pending conflict などの意味ある状態を十分に示しておらず、CLI の正常系確認も弱い状態でした。

候補案:
- A: operation-list に pending conflict status を出し、CLI 正常系テストを補う（運用時に判断しやすくなる）
- B: 現状の最小表示に留める（表示は軽いが、確認時の情報が不足する）

推薦案: A
理由: 実運用では、判断前に read-only な一覧で十分な状態が見えることが重要です。

## R16-G: active reopen scope structure validation is a minor robustness issue

対象所見: 2026-06-20-workflow-management-implementation-req16-review-run-claude-sonnet-4-6-adversarial-010

平易な説明: malformed reopen scope への追加防御の指摘です。今回の中心要件は満たしており、直接の修正対象からは外しました。

候補案:
- A: 今回は leave-as-is とし、観測された入力経路になったら扱う（範囲を保てる）
- B: 追加 validation を先に入れる（堅くなるが今回の主目的から外れる）

推薦案: A
理由: Req16 の中心は proxy decision と実装フェーズの境界であり、この指摘は周辺的な堅牢化です。
