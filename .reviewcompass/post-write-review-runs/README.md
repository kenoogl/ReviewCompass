# 凍結案内（この置き場への新規追加は行わない）

- **凍結日**：2026-06-13（配置規約 P1 実装反映と同時。決定は PLC-DEC-009、2026-06-12）
- **対象**：書き込み後検証（post-write-verification）の review-run 証跡
- **新しい置き場**：`.reviewcompass/evidence/review-runs/<run-id>/`
- **凍結理由**：文書配置規約（`docs/notes/2026-06-12-document-placement-stage2-decisions.md`・
  `docs/notes/2026-06-12-document-placement-stage4-migration.md`）により、証跡は evidence 区画・
  実行時生成物は runtime 区画へ集約した。既存分はリンク切れを避けるため移動せず、この置き場で凍結保全する
  （PLC-DEC-009「既存証跡は動かさない」）。
- **読み取り互換**：旧パスの読み取りは最終形移行（P3、PLC-DEC-011）まで維持される。互換の終了は P3 の
  専用 reopen で明示的に扱う（暗黙の終了はない）。
- **検査**：この置き場への新規追加・変更は凍結違反として機械検出の対象になる（本 README 自身は凍結案内として対象外）。
