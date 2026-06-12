---
feature: all_features
phase: implementation
stage: alignment
date: 2026-06-12
context: reopen R-0（docs/reviews/reopen-classification-2026-06-12-parse-error-failclosed.md）第3過程
---

# implementation alignment（整合チェック）実施記録（parse-error-failclosed）

## 確認項目と結果

1. **triad-review 所見の解消**：8 件すべて確定済み、未処理 0 件。must-fix（UnicodeDecodeError 未捕捉＝
   非 UTF-8 ファイルでクラッシュ）は、失敗テスト（test_undecodable_file_is_deviation）を先に追加して
   失敗を確認後、捕捉対象へ追加して修正、テスト通過。should-fix 2 件（非 UTF-8 テスト追加・テスト名改名）も
   反映済み。
2. **仕様との整合**：実装の挙動（探索で選ばれた 1 ファイルの unreadable／empty／not_mapping を
   未定義と区別して kind unknown・reasons 列挙・DEVIATION・exit 2 で遮断、不在・未定義は案内 OK 維持）は、
   承認済み requirements 受入 8・9・design §7・tasks T-004 と一致。理由文の最低要素（対象パス・
   内容確認促し・空は記録促し）はテストで機械検証される。
3. **テスト**：遮断 4 ケース（パース不能・空・非連想配列・非 UTF-8）＋案内維持 2 ケース＋既存全群、
   tools 161 件・全テスト群 877 件通過。仕様と実装の一時不一致は本実装で解消した。

## 判断結果

implementation alignment は pass。implementation フェーズの approval（人間承認、本 reopen の最終承認）へ進む。
