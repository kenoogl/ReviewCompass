---
name: pre-action-precheck
description: 集約・横断操作（≥3 file 操作、確定事項表作成等）の前に 5 項目チェックリスト＋grep＋3 分類を応答内で明示（旧 2 規律統合：aggregation-self-check／multi-file-dependency-precheck、2026-05-25 セッション 24 統廃合）
metadata: 
  type: feedback
---

集約・横断操作の前に、応答内で事前検査チェックリストを明示し、grep で対象を全件列挙する。

**集約局面（確定事項表・採用方針一覧等）の事前検査 5 項目：**

1. 各項目に承認発言の出典は併記されているか（[[approval-operation]] 連動）
2. 確定済み論点と未確定論点が区別されているか
3. workflow_state（spec.json）の状態と整合しているか（[[workflow-state-truth-source]] 連動）
4. 過去確定との矛盾はないか
5. 利用者の最新発言と整合しているか

**多 file 操作（≥3 file）の事前検査：**

- grep 実行で対象を行番号付き全件提示
- 3 分類で categorize（編集／追記／削除、または機能内対処／波及／遡及）
- scope 独立検証（提案範囲が利用者意図と一致するか）

**Why:** 旧 2 規律（aggregation-self-check／multi-file-dependency-precheck v2.1）を統合（2026-05-25 セッション 24）。事前検査は集約局面と多 file 操作の両方で必要、規律として一体で扱う方が自然。過去の経緯：aggregation-self-check はセッション 21 の表作成前自己検査として制定、multi-file-dependency-precheck v2.1 はセッション 22 で旧 pre-action-checklist を統合した経緯がある。

**How to apply:**

- 確定事項表・採用方針一覧を書く前：5 項目チェックリストを応答内で明示宣言、書く前の事前検査として実行
- 3 file 以上の操作前：grep ＋ 全件提示 ＋ 3 分類 ＋ scope 独立検証を実施
- 段階 2 スクリプトの機械検査では捕捉できない（応答内の宣言で守る）
- 詳細・過去事例：`memory/archive/2026-05-25-consolidation/` 配下の旧 2 ファイルを参照
