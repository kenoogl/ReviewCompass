# proxy_model 承認判断依頼：workflow-management requirements フェーズ approval（reopen R-0、Requirement 11）

あなたは人の判断を代行する proxy_model である。操縦 LLM（Claude）とは別系統として、requirements フェーズを承認してよいかを判断する。

## 文脈

- reopen R-0（decision-source-lint）で workflow-management requirements に Requirement 11（重要決定の出典検査＝束ね検出・逐語照合・内容性、構造化した重要決定の記録形式）を新設・改訂した。
- 既存規律 discipline_approval_operation／discipline_plain_explanation_each_step の機械強制であり、分類は R-0（intent・feature-partitioning は不変、既存「静的検査」Requirement 1・「不可逆操作の直前ゲート」Requirement 4 の範囲）。

## これまでのゲート結果

- triad-review：3 ラウンドで収束。round-1 所見13→must-fix7/should-fix4 反映。round-2 must-fix1（保留が fail-closed 抜け道との指摘）→受入3 を「保留＝確定済みとして扱わない・後続根拠にしない・タイムアウト昇格なし」に書換。round-3 で gpt-5.5・gemini 0 件、claude INFO3（design 細目、leave-as-is）＝収束（未解決 must-fix 0）。
- review-wave：no_impact（他 6 機能へ波及なし、持ち越し 0 件）。
- alignment：existing_sufficient（既存 Requirement 1〜10 と整合、既存要件の改訂不要、未処理整合所見なし）。

## 承認時の不可逆操作

承認すると spec.json の requirements alignment・approval を true へ復帰する（recheck の design／tasks／implementation は残し、下流で再実施を続ける）。

## 判断（厳守の返答形式）

次の YAML だけを返すこと（markdown フェンス無し）。

approval:
  approved: true | false
  rationale: <承認/非承認の理由を一言>
  residual_risks: <あれば残存リスクや下流(design)へ送る留意点を一言。無ければ「なし」>
