# Requirements reopen triad-review triage summary

## 実行概要

- review-run: `2026-06-09-requirements-reopen-triad-review-run`
- variant: `implementation_review_independent_3way`
- phase: `requirements_reopen_triad_review`
- criteria: `requirements_reopen_no_change_decision`
- target: `target.md`

| role | provider | model | result |
| --- | --- | --- | --- |
| primary | anthropic-api | claude-sonnet-4-6 | 8 findings |
| adversarial | openai-api | gpt-5.4 | no findings |
| judgment | gemini-api | gemini-3.1-pro-preview | 3 findings |

## 利用者提示ゲート

requirements triad-review は完了したが、所見が残っているため、proxy_model 判断、requirements.md 修正、spec.json 更新、フェーズ移行にはまだ進まない。

この停止点で利用者に確認すべきことは、次の三段階トリアージである。

## 三段階トリアージ案

### 1. must-fix 候補

現在の target は、各 requirements.md の該当 Requirement 本文を引用せず、「既に受け皿確認がある」ことを根拠にしている。このため、primary は direct impact 4 feature について独立検証が困難と判定した。

対象:

- `foundation`: Requirement 5 の固定パターン依存除外が、新 intent の否定命題を受入基準レベルで十分に表しているか未提示。
- `runtime`: Requirement 10 の除外契約、Requirement 3／4 への影響が本文引用なしでは判定不能。
- `evaluation`: Requirement 9 のレビューモード区別が、LLM 判断ベースの発見と固定写像の区別を吸収できるか未検証。
- `conformance-evaluation`: Requirement 1／3／9 が、LLM 判断ベース実装の逆方向推定への影響を閉じられるか未評価。

推奨扱い:

- `must-fix`: requirements.md を直ちに修正する前に、target または補足記録へ該当 Requirement 本文と差分評価を追加する。
- その追加証拠により本当に不足が見えた場合に限り、requirements.md 修正へ進む。

### 2. should-fix 候補

drafting 再実施完了の根拠が弱い。

所見:

- 「受け皿確認が書かれている」ことをもって drafting 再実施完了とみなすプロセス根拠が target に不足している。
- 2026-06-08 に requirements.md へ受け皿確認を追記済みなら、今回の「追加修正不要」は「今回追加修正不要」であり、「過去にも修正不要」ではない。この時点の整理が必要。
- 人間承認待ちにすべき未確定点の候補が target に事前整理されていない。

推奨扱い:

- `should-fix`: 進行中記録または review summary に、「今回の drafting 再実施では追加修正不要。ただし 2026-06-08 の既存追記を前提にした判断」と明記する。

### 3. leave-as-is 候補

adversarial は所見なしだった。また judgment も requirements.md の即時修正を断定していない。

推奨扱い:

- indirect check 3 feature については、target の説明補強は望ましいが、現時点で requirements.md 本体の不足を示す決定的所見はない。
- direct impact 4 feature も、まずは requirements 本文引用に基づく差分評価を追加し、その後に修正要否を判定する。

## 次アクション候補

1. 利用者がこの三段階トリアージ方針を承認する。
2. 承認後、requirements.md 本体を直ちに直すのではなく、該当 Requirement 本文と差分評価を review-run summary に補足する。
3. 補足後、must-fix が「証拠不足」から「requirements 本文不足」に変わるかを判定する。
4. requirements 本文不足がなければ、requirements triad-review 完了として次段へ進む。
