# docs/notes/ インデックス

セッション内議論・設計検討・振り返り・効果測定など、本リポジトリの正本文書（計画書／operations／仕様）の補助となるメモを置く。

## 命名規則

- `YYYY-MM-DD-<topic-slug>.md`（日付＋短い主題）
- 主題は英小文字とハイフン、または日本語（短い場合）
- 各メモの冒頭に「最終更新」「経緯」「対象範囲」を明示

## 一覧（日付の新しい順）

### 2026-05-25

| ファイル | 主題 | 関連コミット |
|---|---|---|
| [2026-05-25-session-24-retrospective.md](2026-05-25-session-24-retrospective.md) | セッション 24 振り返り：補助層 C 共存モデル完成、規律統廃合 20→11、規律違反 1 件記録 | 本セッション末尾 |
| [2026-05-25-discipline-consolidation-effect-measurement.md](2026-05-25-discipline-consolidation-effect-measurement.md) | 規律統廃合の効果測定：48.7% 削減（ファイル／行数／バイト数／推定トークン） | `e99d4e7` |
| [2026-05-25-workflow-pre-check-and-discipline-consolidation.md](2026-05-25-workflow-pre-check-and-discipline-consolidation.md) | 補助層 C 共存モデルの議論経緯（セッション 23 末で起案、セッション 24 で採用） | `8b33e74`／`04a2eef` |

### 2026-05-24

| ファイル | 主題 | 関連コミット |
|---|---|---|
| [2026-05-24-conformance-evaluation-論点-a-b.md](2026-05-24-conformance-evaluation-論点-a-b.md) | conformance-evaluation の論点 A（機能分離タイミング）・論点 B（既存文書バイアス）の議論と案 Y 採用 | `8edefbf`／`8165f01` |

## 主題ごとのグルーピング

### 補助層 C 共存モデル（セッション 24 主要トピック）

- 議論経緯：`2026-05-25-workflow-pre-check-and-discipline-consolidation.md`
- 効果測定：`2026-05-25-discipline-consolidation-effect-measurement.md`
- 振り返り：`2026-05-25-session-24-retrospective.md`
- 仕様正本（別ディレクトリ）：[../operations/WORKFLOW_PRECHECK.md](../operations/WORKFLOW_PRECHECK.md)

### conformance-evaluation（セッション 23 末）

- 論点 A・B 議論：`2026-05-24-conformance-evaluation-論点-a-b.md`

## メモと正本文書の関係

- **メモ（本ディレクトリ）**：議論経緯・検討メモ・振り返り・効果測定など、後から参照しうる作業記録
- **operations 文書（`../operations/`）**：運用ガイドラインの正本（SESSION_WORKFLOW_GUIDE.md 等）
- **計画書（`../plan/`）**：戦略・方針の正本
- **仕様文書（`.reviewcompass/specs/<機能>/`）**：機能別の正本

メモは正本ではないため、運用上の判断材料・議論経緯の保全用途。確定方針はメモから正本文書へ反映される。

## archive

過去の TODO スナップショット等：[../archive/todo/](../archive/todo/)

## 関連参照

- TODO_NEXT_SESSION.md §3／§4：本セッションの作業候補と確定事項
- 運営ガイド：[../operations/SESSION_WORKFLOW_GUIDE.md](../operations/SESSION_WORKFLOW_GUIDE.md)
- 計画書：[../plan/reconstruction-plan-2026-05-21.md](../plan/reconstruction-plan-2026-05-21.md)
