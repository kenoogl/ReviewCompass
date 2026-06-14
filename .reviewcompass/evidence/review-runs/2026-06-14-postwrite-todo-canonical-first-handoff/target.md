# 書き込み後検証対象：TODO_NEXT_SESSION.md 更新（正本優先・案2 完了反映と検討項目の引き継ぎ）

検証者へ渡すのは合意内容（決定）と書き込み結果のみ。

## 合意内容（決定・事実）

- 案2（正本優先の生成ツール2本：`tools/make-commit-approval.py`・`tools/make-post-write-manifest.py`）を実装・公開した。コミット `83abd1e6`、push 済み。生成物は正本の検証関数に通して fail-closed する。専用テストは各 4／3 件、tools 全テスト pass（unittest discover で 209 件）。
- 残る検討を引き継ぎとして TODO §4 に項 7 として追記する。内訳：(C) 「正本優先」を正式な規律にする手続きは、新規規律が `self-improvement` 由来の `new_discipline` 提案を `workflow-management` が drafting→review→approval で実体化するもので、かつ「新規規律を1つ足すなら既存規律を1つ以上統廃合する」運用ルールに従う（workflow-management requirements.md の 34 行目・124 行目）＝重い。(D) 規律変更手続きには小変更用の規模比例の軽い道が無い（書き込み後検証は小規模1体／大規模3体と規模で軽重を変える）。(拡大) 手組みしている他の成果物も正本から生成するツール化を順次検討。
- §3 先頭行の push 到達点を `83abd1e6` に更新する。§3 に案2 の項を追加する。

## 書き込み結果（TODO_NEXT_SESSION.md 差分の要旨）

- §3 先頭行の push 到達点「`a287684a` まで push 済み」→「`83abd1e6`〔正本優先・案2〕まで push 済み」。
- §3 に「正本優先（事例より正本）の生成ツール（案2）追加・公開済み」の項を追加（2ツール名・正本＝検証関数・テスト件数・コミット `83abd1e6`・dogfooding を記載）。
- §4 に項 7「『正本優先』の規律化と規律変更手続きの比例性」を追加（C／D／拡大の3点を引き継ぎとして記載）。
