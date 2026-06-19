# .reviewcompass/ 区画索引

ReviewCompass の状態・証跡・生成物の置き場。区画構成の正本根拠は配置規約の決定台帳
（`docs/notes/2026-06-12-document-placement-stage2-decisions.md` PLC-DEC-004、
設計 `docs/notes/2026-06-12-document-placement-target-design.md`）。

| 区画 | 役割 | git 管理 |
| --- | --- | --- |
| `specs/<feature>/` | 正本仕様のみ（requirements・design・tasks・spec.json）。証跡を置かない（PLC-DEC-003。既存の reviews／conformance は凍結保全、新規は evidence へ）。implementation drafting は文書成果物ではなく、tasks.md に従ったテストと実装コード生成として扱う | 追跡 |
| `evidence/` | 証跡記録（レビュー・conformance・review-run・検証 manifest・推定ログ等）。内部構造は `evidence/README.md` | 追跡 |
| `runtime/` | 実行時生成物（effective-prompts・approvals・実行ログ）。再生成可能または実行時状態のため git 無視。ツールが書き込み時に作成する | 無視 |
| `post-write-verification/` | 書き込み後検証 manifest（当面の置き場。最終形で evidence へ統合、PLC-DEC-011・P3） | 追跡 |
| `feature-dependency.yaml` | 対象アプリでの機能依存の標準配置（開発リポジトリは `stages/` 配置、探索順で両対応） | 追跡 |

P1 移行（新規分のみ新配置）の計画は `docs/notes/2026-06-12-document-placement-stage4-migration.md` を正本とする。
