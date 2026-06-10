---
name: must-fix-discussion-obligation
description: triad-review 段で must-fix と判定された所見の対処は利用者と必ず議論する。独自判断で仕様文書を修正することを禁ずる。各推奨案には後段影響の深掘りを義務付ける。
metadata: 
  type: feedback
---

triad-review 段で判定役が must-fix と判定した所見の対処は、起草者（LLM）が独自判断で仕様文書（design.md／requirements.md／tasks.md／implementation.md）を修正することを禁ずる。利用者と必ず議論し、各所見の対処方針を 1 件ずつ平易な日本語で説明して合意を得てから反映する。

**Why**：2026-05-25 セッション 25 で、foundation／design の must-fix 7 件の対処内容を私が独自判断で起草し design.md に反映、コミット・push まで進めた事案が発生。利用者の問いかけ「foundationのmust_fixについては、議論しなくて良いのか」で気づき進行を中断。その後の議論で「(イ)で後段に問題発生はないか」「一連の提案は、表層的で深掘りされていない。先ほどの指摘がなければ、下流でreopen案件になっていた」と指摘を受け、本規律として確立した。

**How to apply**：

- 正本手順：運営ガイド [docs/operations/SESSION_WORKFLOW_GUIDE.md](../operations/SESSION_WORKFLOW_GUIDE.md) §3.3 (a-1) must-fix 所見の対処手順 を参照する。本 memory は参照リンクのみで、規律本体は運営ガイドが正本
- triad-review 完了後、must-fix 所見を 1 件ずつ取り上げ、利用者と議論しながら平易な日本語で対処方針を提案する
- 各推奨案には必ず後段影響の深掘り（下流仕様・対象アプリ配置・機械検証・実装運用・将来拡張）を含める
- 「現状維持を推奨」する場合も、現状維持の弱点を検証してから示す
- 一括処理（複数論点を一気に決着）を避け、各論点を個別に深掘りする
- 候補案は必ず複数提示、代替案との比較を欠かない
- API 経由の review-run で `ERROR`／`CRITICAL` または最終判断 `must-fix` の重要件を扱う場合は、raw 参照、モデル別要約、三段階トリアージ、利用者承認を提示・記録してから `review_triage.py decide` / `write-manifest` を実行する。機械ゲートの正本手順は `docs/operations/WORKFLOW_NAVIGATION.md` の `post_write_verification` 分岐に従う

関連：[[plain-japanese]]（平易な日本語）、[[concise-complete-report]]（簡潔・もれなく報告）
