---
name: no-unilateral-action
description: approach 変更・session 継続終結・不可逆操作・大きな自律実行の前は確認、恒常指示に触れる判断はエスカレーション（旧 2 規律統合：no-unilateral-approach-change／no-unilateral-session-ending、2026-05-25 セッション 24 統廃合）
metadata: 
  type: feedback
---

approach 選択、session 継続／終結、不可逆操作、大きな自律実行の前は止めて確認する。

**確認が必要な局面：**

- approach 変更（フルスクラッチ／既存修正、設計方針の変更等）
- session の継続／終結誘導：「本セッションはここで完了」「次セッションで」「(イ) を推奨」（次セッション送りの提案）等は LLM から提案しない
- 不可逆操作（commit／push／spec.json／phase 移行）
- 大きな自律実行（複数 file 編集、計画書改訂等）

**「合理的判断で進めてよい」が指示されていても：**

- 恒常指示（フルスクラッチ規律等）に触れる判断は例外＝必ずエスカレーション

**Why:** 旧 2 規律（no-unilateral-approach-change／no-unilateral-session-ending）を統合（2026-05-25 セッション 24）。両方とも「LLM が利用者判断を待たずに走る」失態への対処で、原理（勝手に走らない）は共通。前者は approach 変更を技術判断で自律確定した過去の失態、後者はセッション 24 で push 直後に「次セッションで」と勝手に提案した失態の指摘から派生。両者を統合することで「勝手に走らない」原理として一括把握できる。

**How to apply:**

- approach 変更の判断点：止めて確認、「合理的判断で進めてよい」でも恒常指示に触れるなら例外
- session 進行：「次の選択肢」を示すとき「本セッションを区切る」「次セッションで」等を含めない（終結は利用者判断）
- 不可逆操作：[[approval-operation]] に従い明示承認を取る
- 段階 2 スクリプト（[[workflow-precheck-invocation]]）が不可逆操作の検査を一部代行するが、approach 変更や session 進行の判断は LLM の責務
- 詳細・過去事例：`memory/archive/2026-05-25-consolidation/` 配下の旧 2 ファイルを参照
