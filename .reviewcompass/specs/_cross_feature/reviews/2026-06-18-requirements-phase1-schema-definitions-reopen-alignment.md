---
date: 2026-06-18
gate: stages/requirements.yaml#alignment
feature: workflow-management
reopen: R-0
reopen_topic: phase1-schema-definitions
decision: existing_sufficient
---

# requirements alignment（整合確認）：Phase 1 最小スキーマ定義

reopen R-0 の第3過程、workflow-management requirements フェーズの alignment 段。Requirement 2 受入 10・11（`required_action` 19語彙スキーマ・`next --json` 応答スキーマの定義）と既存要件（Req 1〜12 受入 1〜9）、分類記録、triad-review 対処、review-wave 判定、下流 recheck 状態の整合を確認する。

## AC10・AC11 と既存要件の整合

| 既存要件 | 関係 | 整合判定 |
| --- | --- | --- |
| Req 1（段集合の静的列挙） | AC10/AC11 はスキーマファイルの定義であり、段集合 YAML の変更を要しない。 | 整合。改訂不要。 |
| Req 2 受入 1〜9（検査スクリプト） | AC10 の `required_action.schema.json` は受入 9「唯一 action selector」の語彙正本となる。AC11 の `next_action_response.schema.json` は受入 9 の振る舞い契約をスキーマで表現する。どちらも既存受入の補完であり矛盾しない。 | 整合。受入 1〜9 の改訂不要。 |
| Req 3（起草者と判定者の分離） | スキーマファイル定義は起草者・判定者の分離規則に関係しない。 | 整合。改訂不要。 |
| Req 4（不可逆操作の直前ゲート） | スキーマファイル定義は直前ゲートの操作対象に直接影響しない。 | 整合。改訂不要。 |
| Req 5（reopen 手続きの機械強制） | `required_action` の語彙正本（AC10）は reopen の trigger_map や pending gate 処理で参照するが、スキーマファイルを正本とする方針は受入 6 の「blocker/stop_point/pending gate の優先順位解決」と矛盾しない。 | 整合。改訂不要。 |
| Req 6（session 跨ぎ状態管理） | スキーマファイル定義は session 跨ぎ管理の機構を変えない。 | 整合。改訂不要。 |
| Req 7（多層防御の位置付け） | スキーマファイルは第1層の検査補助であり、多層防御の位置付けを変えない。 | 整合。改訂不要。 |
| Req 8（機能依存マップ） | スキーマファイル定義は機能依存マップに影響しない。 | 整合。改訂不要。 |
| Req 9（後追い intent 追加） | 本 reopen 自体は R-0（requirements レベル）であり、intent レベルではない。 | 整合。改訂不要。 |
| Req 10（review-wave 要約コマンド） | スキーマファイル定義は review-wave 要約コマンドの責務と無関係。 | 整合。改訂不要。 |
| Req 11（重要決定の出典検査） | スキーマファイル定義は決定記録形式に影響しない。 | 整合。改訂不要。 |
| Req 12（operation registry / preflight） | AC10/AC11 は `next --json` 出力の正本を明確化するもので、Req 12 受入 14「`next --json` を複製せず参照」と整合する。スキーマファイルによる語彙正本化は preflight 結果の `required_action` 参照を安定させる。 | 整合。改訂不要。 |

## 分類記録との整合

- `docs/reviews/reopen-classification-2026-06-18-wm-phase1-schema-definitions.md` は R-0（requirements レベル差し戻し）、feature は workflow-management、下流影響は design/tasks/implementation と判定している。
- AC10/AC11 は requirements.md への受入基準追記のみで完結する。スキーマファイルの**実体作成**は下流フェーズ（design で設計、tasks でタスク化、implementation で TDD 実装）が担う。
- 分類記録と整合する。

## triad-review 対処との整合

- クラスタ A（`action_parameters` の対象を `run_maintenance` のみに明記）：AC11(2) の「`action_parameters`（オブジェクト）は `run_maintenance` のみを対象とする必須の条件付きフィールドとして定義する」に反映済み。
- クラスタ B（偽陽性：AC10/AC11 の相互参照未明記）：requirements.md の当該箇所には「（受入10のスキーマを参照）」と明示されており leave-as-is。実際に修正は不要であったことを確認。
- クラスタ C（`repair_reasons` 非空配列を明記）：AC11(2) の「`repair_reasons`（配列）は `repair_workflow_state` 時に必須となる条件付きフィールド（非空配列・最低1要素）」に反映済み。
- クラスタ D（後方互換フィールドの一致制約を追記）：AC11(5) の末尾「これらの後方互換フィールドが存在する場合は対応する正本フィールドと一致させること（`next --json` の実装側の不変条件として要求する。JSON Schema での表現は design で確定する）」に反映済み。
- クラスタ E（D-003 §4.2 確定済み制約のみという注記を追記）：AC11(6) の末尾「上記①〜⑥の制約は D-003 §4.2 で確定している制約の全てであり、これ以外の `required_action` 種別には確定した追加フィールド制約はない（universal 必須フィールドのみが適用される）」に反映済み。
- クラスタ F（`kind` の説明を明示）：AC11(2) の「`kind`（文字列・`required_action` の分類子、値域は design で確定）」に反映済み。
- 全クラスタの対処が requirements.md に正確に反映されており、整合する。

## review-wave 判定との整合

- review-wave では `existing_sufficient`（他6機能への正本修正不要）と判定した（`stages/in-progress/reopen-procedure-2026-06-18.yaml` の `downstream_impact_decisions`）。
- AC10/AC11 は workflow-management 固有の内部スキーマファイル定義（`required_action` 語彙・`next --json` 応答スキーマ）であり、他機能の共有語彙・評価契約・分析契約等を変えない。
- review-wave 判定と整合する。

## 下流 recheck 状態との整合

- `.reviewcompass/specs/workflow-management/spec.json` は `recheck.upstream_change_pending=true`、`impacted_downstream_phases: [design, tasks, implementation]` を保持している。
- **design**：`required_action` 19語彙（D-003 §4.2）と `next --json` 応答スキーマ構造（§軽量版検査スクリプトモデル、§next --json unique action selector）は design.md に設計済み。スキーマファイルのパス（`.reviewcompass/schema/`）への明示参照はファイル一覧に未追記だが、設計の実体と矛盾しない。design の recheck では `.reviewcompass/schema/` 配下の2ファイルをファイル一覧に追加し、スキーマ生成タスクを接続することが必要。
- **tasks**：`required_action.schema.json` と `next_action_response.schema.json` の作成タスクが未追加。tasks の recheck では T-004 相当のスキーマ作成タスクを追加し、TDD 先行（失敗テスト `tests/tools/test_phase1_schema_definitions.py` 作成済み）として実装タスクを配置することが必要。
- **implementation**：スキーマファイルの TDD 実装（17テスト通過）が未着手。implementation の recheck では対応実装を追記することが必要。
- `recheck` の追跡が正確であり、requirements 段の alignment 時点で追加修正は不要。設計・タスク・実装への波及は recheck を通じて順に対処する。

## 判定

- **decision：existing_sufficient**。
- AC10・AC11 は既存要件（Req 1〜12 受入 1〜9）と整合し、requirements 段内の追加改訂を要しない。
- triad-review の対処（クラスタ A〜F）が requirements.md に正確に反映され、review-wave の判定（other features への影響なし）と整合する。
- design/tasks/implementation での追加対応（スキーマファイル一覧への追加・タスク化・TDD 実装）は `recheck.impacted_downstream_phases` で追跡中であり、requirements 段の alignment では不要。
