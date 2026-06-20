# 自動実行テスト報告

対象: workflow-management implementation Req15 review-run 後の修正適用と証跡確認

## 生じた問題

1. effective prompt の監査が、必須構造、source artifact、precondition、postcondition、prompt length の要求を十分に fail-closed で検査していなかった。
2. prompt length のテストが、境界値そのものではなく別の欠落で失敗しており、検査意図が曖昧だった。
3. machine-task leakage の診断が最初の 1 件で止まり、複数違反を把握しにくかった。
4. effective prompt の sha256 表記と builder schema validation が揃っていなかった。

## 対応したこと

1. prompt audit に必須構造、壊れた source artifact、未知 action kind、manifest mismatch、未検証 precondition、不可能 postcondition、prompt length の fail-closed 検査を追加した。
2. prompt length の境界値検査を、実際に境界不正で失敗する形へ整理した。
3. machine-task leakage の複数診断と direct follow-up fixture の意図を明確化した。
4. run_role / run_review の effective prompt sha 表記と builder schema validation を整備した。

## 残った課題

1. prompt audit の運用ケースが増える場合は、個別 effective prompt ごとの fixture を追加する余地がある。
2. API レビュープロンプト全体の品質監査は、Req15 だけでなく他フェーズの利用場面でも継続して確認する。
