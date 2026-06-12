---
feature: all_features
phase: requirements
stage: alignment
date: 2026-06-12
context: reopen R-0（docs/reviews/reopen-classification-2026-06-12-parse-error-failclosed.md）第3過程
---

# requirements alignment（整合チェック）実施記録（parse-error-failclosed）

## 確認項目と結果

1. **triad-review 所見の解消**：6 件すべて確定済み、未処理 0 件。must-fix なし。
   should-fix 4 件（型違反の位置づけと判定順・unknown の出どころ・遮断対象の限定・空ファイルの扱い）は
   受入 9 へ反映済み（利用者承諾のうえ r2 は省略、本 alignment で整合確認）。
2. **要件内の整合**：受入 8（不在・未定義 → 案内）と受入 9（パース不能・空・型違反 → 遮断）の境界が
   明確になり、受入 9 の判定順（受入 7 の整合検査より先）と出力規定（kind unknown・reasons・
   DEVIATION・exit 2）は受入 7 と同型で整合。受入 6（探索で選ばれた 1 ファイル）への参照も明示。
3. **設計判断との整合**：受入 9 は fail-closed 原則（design 判断 3）の適用を広げる方向であり矛盾なし。
4. **実装との関係**：実装は旧挙動のまま（意図的）。仕様確定後に implementation 段で TDD 実装する旨は
   reopen 進行記録・tasks T-004 テスト要件に明示済み。
5. **feature 間の整合**：他 6 機能への波及なし（review-wave 記録）。

## 残存事項

- design §7・tasks T-004 への境界精密化（空ファイル・判定順・1 ファイル限定）の追従は、
  各フェーズの drafting 補正として実施し、それぞれの triad-review で検証する。

## 判断結果

requirements alignment は pass。requirements フェーズの approval（人間承認）へ進む。
