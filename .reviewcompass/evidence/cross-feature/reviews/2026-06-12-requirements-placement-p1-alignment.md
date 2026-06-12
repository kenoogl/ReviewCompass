---
feature: all_features
phase: requirements
stage: alignment
date: 2026-06-12
status: completed
record_type: reopen-alignment
related_reopen: stages/in-progress/reopen-procedure-2026-06-12-placement-p1-ce.yaml
---

# reopen R-0（placement-p1）requirements alignment 実施記録

## 確認項目と結果

triad-review（round-1：ERROR 1・WARN 2・INFO 2、round-2：WARN 3・INFO 4、いずれも判断確定済み）
適用後の conformance-evaluation requirements 本文について、次の整合を確認した。

1. **受入間の整合**：Requirement 6 受入 2 を配置ルート契約の正本とし、Requirement 2 受入 7・
   Requirement 3 受入 8・Requirement 12 受入 4・Boundary Context の 4 箇所が明示的に委譲する構造。
   各成果物の名前形式の定義箇所（評価記録＝受入 2、草案＝Requirement 12 受入 4、handoff＝
   Requirement 12 と tasks の成果物定義）を受入 2 に列挙し、解釈の分岐を解消（round-1 F1・round-2 W2/W3 対処）
2. **分離契約の維持**：`conformance/`／`reviews/` の分離（Requirement 8 受入 4・MV-3）は
   `evidence/features/<feature>/` 配下でも維持と明記
3. **配置規約との整合**：PLC-DEC-003〜005・009〜011（決定台帳 2026-06-12-document-placement-stage2-decisions.md・
   移行計画 stage4-migration.md）と矛盾なし。凍結（既存記録は移動しない）・読み取り互換（P3 まで、
   終了は P3 の専用 reopen における仕様改訂、暗黙終了なし）を明文化
4. **fail-closed との整合**：検証対象判定は変更せず（設計記録 §4）、実装は仕様確定後の TDD（正順）。
   現実装が旧パスへ書く間も両置き場は追跡され証跡は失われない

## 判断

- existing_sufficient（追加修正不要）。requirements approval（人の承認）へ進む
