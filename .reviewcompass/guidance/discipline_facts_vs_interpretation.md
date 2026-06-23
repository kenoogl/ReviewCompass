---
name: facts-vs-interpretation
description: 達成基準を事前宣言、編集後は機械的（grep／Read）照合、事実と解釈を別個に示し出典に辿れる形に（旧 3 規律統合：check-logs-and-git／separate-facts-from-interpretation／completion-verification-protocol、2026-05-25 セッション 24 統廃合）
metadata: 
  type: feedback
---

事実は記憶でなく出典（ファイル行・コミット・ログ）で確認し、解釈と明示的に分けて示す。

**達成基準と検証のプロトコル：**

- 指示を受けたら冒頭で達成基準を箇条書きで宣言
- 編集後は grep／Read で機械的に照合し、出典を残す
- 報告の中心は「やったこと」でなく「達成基準と現状の照合結果」
- 完了承認後は基準を満たすまで作業継続

**事実と解釈の区別：**

- 完了・適合・GO を断定せず、検証可能な証拠と「満たした／満たさない」で示す
- 主張・報告は必ず出典（ファイル行・コミット）に辿れる形にする

**Why:** 旧 3 規律（check-logs-and-git／completion-verification-protocol／separate-facts-from-interpretation）を統合（2026-05-25 セッション 24）。事実根拠と機械的確認と解釈の分離は密接に関連する一連の規律で、一体運用が自然。過去の失態：記憶に頼って事実と異なる断定をした、達成基準を宣言せず「やったこと」を報告して齟齬が露見、解釈と事実を混在させて利用者に誤伝した。

**How to apply:**

- 指示を受けたら冒頭で「達成基準の宣言」節を出力
- 編集後に grep／Read の出力を引用して「達成基準 N が満たされている」を機械的に証明
- 報告は「やったこと」ではなく「達成基準 N → 検証結果」の形式
- 機械化の一部は段階 2 スクリプト（[[workflow-precheck-invocation]]）が代行するが、宣言と報告の構造は LLM の責務
- 詳細・過去事例：`memory/archive/2026-05-25-consolidation/` 配下の旧 3 ファイルを参照
