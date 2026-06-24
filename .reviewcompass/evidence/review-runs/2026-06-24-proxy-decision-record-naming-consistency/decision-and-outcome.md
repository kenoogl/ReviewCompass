# 三者レビューの結論と最終決定：proxy_model 判断レコードの命名・意味づけ

run_id: 2026-06-24-proxy-decision-record-naming-consistency
変種: implementation_review_independent_3way（Claude Sonnet 4.6 / GPT-5.5 / Gemini 3.1 Pro）

## 1. 三者レビューの所見（要約）

- Gemini（判定役・CRITICAL 1件）：AIの判断を approval として扱うのは人間承認との混同リスク。
  設計書(B)の decision パラダイム（decided_by・承認ではない）を正本とし、実装(A)・規律(C)を直すべき。
- Claude（主分析・CRITICAL 1 / ERROR 2 / WARN 2）：承認/判断の二重定義は安全上の矛盾でゲートの
  抜け穴になりうる。資料が方向を推奨しておらず actionable でない、テスト失敗が CI を通過しているか
  未確認、改名の git 経緯未確認、等のメタ指摘。
- GPT（反証役）：0件（反証なし）。

## 2. レビュー後に判明した決定的文脈（レビュアー未提供）

利用者の指摘により、proxy 承認の設計動機と安全機構を検証した。

- requirements.md:79：proxy_model は所見トリアージを代行できるが、コミット・プッシュ・spec.json
  更新・フェーズ移行は代行しない。proxy 承認は「軽いゲートを人手なしで通す＝自律実行」のために
  存在する。
- design.md / コード：安全境界は `decision_scope`（human_only / proxy_allowed / advisory_only）で
  機械的に強制。`tools/check_workflow_action/proxy_triage_decisions.py:137` が
  `decision_scope == "human_only"` の承認ゲートで proxy 適用をブロックする（実装済み）。

つまり「proxy が approval を名乗ると人間承認と混同する」という安全懸念は、名前ではなく
decision_scope が既に防いでいる。三者レビューはこの動機と decision_scope を材料に含めていな
かったため、結論を過大評価した（これは review prompt を作った担当 LLM の材料不足が原因）。

## 3. 最終決定（方向）

- **正本＝実装コード**（`proxy-approval.yaml` / `approved_by` + decision_scope）。
- 三者レビューの「decision に寄せてコードを直せ」は**不採用**（自律動機と decision_scope を欠いた
  過大評価のため）。ただし副次指摘「design.md の言い回しが誤解を生む」は**採用**。
- design.md の「proxy decision bundle は承認 record ではない」は誤誘導なので、
  「`proxy_allowed` 範囲（所見トリアージ）は承認、`human_only`（コミット等）は不可」と正確化する。
- 命名は `proxy-approval.yaml` に統一する。

## 4. 整合作業（follow-up へ）

design.md・tasks.md は workflow-management の正本仕様であり、これらの変更は reopen 分類を要する
正式な仕様整合になる。本決定の実装（命名統一・design.md 文言修正・test line-91・規律整合）は
`.reviewcompass/backlog/plans/plan-2026-06-24-proxy-decision-record-naming-reconciliation.yaml`
に scoped follow-up として記録する。

## 5. メタ教訓

review prompt の材料に「設計動機」と「既存の安全機構（decision_scope）」を欠いたため、外部
モデルが過大評価した。behavior-path / safety claim を問う場合は、変更対象だけでなく動機・既存
ガード・実行経路を材料に含める（llm-as-judge 指針の main preanalysis 強化点）。
