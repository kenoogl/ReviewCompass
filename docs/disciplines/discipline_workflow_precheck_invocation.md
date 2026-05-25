---
name: workflow-precheck-invocation
description: 不可逆操作（spec.json 変更／git commit／git push）の直前に tools/check-workflow-action.py を呼び、判定結果を応答内で明示する（補助層 C 段階 1、2026-05-25 セッション 24 規律）
metadata: 
  type: feedback
---

ReviewCompass の不可逆操作の直前に、必ず tools/check-workflow-action.py を呼び、
出力の verdict と reasons を応答に書く。

**対象操作と呼び出し：**

- spec.json の workflow_state を変更する直前：
  `python3 tools/check-workflow-action.py spec-set <feature> <phase> <stage> <true/false> [--rationale "..."]`
- git commit の直前：
  `python3 tools/check-workflow-action.py commit --rationale "<理由>"`
- git push の直前：
  `python3 tools/check-workflow-action.py push --rationale "<理由>"`

**判定結果の扱い：**

- exit 0（OK）：続行
- exit 1（WARN）：警告を応答に明示し、利用者の判断を仰ぐ（自律続行しない）
- exit 2（DEVIATION）：処理を止めて利用者に報告、原因を是正してから再試行

**段階 1 と段階 3 の責務分担（2026-05-25 セッション 24 段階 3 導入後）：**

段階 3 フック（`.claude/hooks/pre-bash-precheck.sh`）が Bash の git commit／push を
PreToolUse で自動検査するようになったが、段階 1（LLM 自身の意図呼び出し）は依然
として必要：

- **依然として LLM が必ず呼ぶ**：spec.json 修正（Edit／Write）の直前。段階 3 は
  範囲案 2 のうち Bash 系のみ実装のため、Edit／Write の spec.json 検知は未対応
- **LLM が呼ぶことが望ましい**：git commit／git push の直前。段階 3 が自動発動する
  が、LLM が事前に呼べば応答内で verdict／reasons を共有でき、人間判断との連携
  が滑らか
- **「呼び忘れ」の救済**：段階 3 フックが exit 2 で遮断するため、LLM の見落とし時も
  Bash 系はブロックが効く。ただし応答テキストのみの判断（フックが効かない領域）
  は段階 1 規律が恒久的に担う

**Why:** 計画書 §5.8 補助層 C 共存モデルの段階 1。LLM（私）が段階 2 のスクリプトを
呼ばないと機械検査の効果が消える。仕様 docs/operations/WORKFLOW_PRECHECK.md §11 で
規定された段階 1 規律の文書化。利用者明示承認の出典：「ア」（起草案そのままで論点
a＝memory／b＝即時／c＝すべて で承認、2026-05-25 セッション 24）。

**How to apply:**

- 「直前」とは、対応する Edit／Write／Bash 呼び出しの直前
- `--rationale` には利用者の承認発言や操作理由を渡し、ログ docs/logs/workflow-precheck.log に残す
- [[approval-operation]]／[[no-unilateral-action]] の機械検査による補強。
  これらの規律が言う「承認なしで進めない」「勝手に走らない」を構造的に強化する
- スクリプト未実装時（過去のセッション）には適用できなかった。2026-05-25 セッション 24
  以降の不可逆操作で恒常的に運用する
