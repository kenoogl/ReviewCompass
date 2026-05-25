---
name: workflow-state-truth-source
description: 状態判定は workflow_state を読み、過去確定事項は出典付きのみ信頼、出典なし項目はログ grep または利用者確認で再検証（旧 2 規律統合：workflow-state-single-truth-source／session-handoff-verification、2026-05-25 セッション 24 統廃合）
metadata: 
  type: feedback
---

ReviewCompass の workflow_state（spec.json）を唯一の真実源として扱い、過去確定事項は出典付きのみ信頼する。

**読む側の規律：**

- 状態判定時は必ず workflow_state を実際に Read で読む
- 要約や TODO の記述を根拠にしない（正本と照合）

**書く側の規律：**

- 要約値（current_phase 相当）を spec.json に書かない
- 応答で単独断定しない
- 状態表現には workflow_state の根拠を必ず併記

**セッション開始時の引継ぎ：**

- TODO・設計メモの過去確定事項は出典付きのみ信頼
- 出典なし項目はログ grep または利用者確認で再検証
- 規律違反の伝播を断ち切る（前セッションの過誤を今セッションで踏襲しない）

**Why:** 旧 2 規律（workflow-state-single-truth-source／session-handoff-verification、ともにセッション 21 規律）を統合（2026-05-25 セッション 24）。workflow_state を真実源として扱う規律と、セッション跨ぎでの引継ぎ規律は同じ「正本を信頼、要約を疑う」原理に基づく。前者は計画書 §5.24 の正本スキーマと連動、後者は出典なし過去確定事項の伝播防止が目的。

**How to apply:**

- セッション冒頭の状態確認：spec.json の workflow_state を Read。要約資料に頼らない
- 「○○段が approved である」と書く前：その状態の出典（ファイル行）を併記
- 過去 TODO に書かれた確定事項を踏襲する前：出典の有無を確認、なければログ grep か利用者確認
- 段階 2 スクリプトの spec-set 判定が真実源参照を自動化するが、書く側の規律（要約値禁止、根拠併記）は依然として LLM の責務
- 詳細・過去事例：`memory/archive/2026-05-25-consolidation/` 配下の旧 2 ファイルを参照
