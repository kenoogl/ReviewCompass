---
date: 2026-06-12
record_type: document-placement-stage4-migration
status: decided
placement_note: 本記録自体の置き場は暫定（配置規約の決定後に正式な置き場へ従う）。
related:
  - 2026-06-12-document-placement-plan.md
  - 2026-06-12-document-placement-stage2-decisions.md
  - 2026-06-12-document-placement-target-design.md
---

# 文書配置規約 段階 4：移行方針の利用者決定と移行計画

配置規約策定計画の段階 4 の成果物。段階 3 の設計記録 §6（未決 4 点）に対し、2026-06-12 に利用者が推薦案をすべて採用した（利用者発言「推薦」）。決定 ID は PLC-DEC-009〜012。

## 決定台帳

### PLC-DEC-009：既存証跡は動かさない（新規のみ新配置）

- 配置原則 5（過去記録は原則動かさない）の既定どおり。既存の証跡・生データは現在の置き場で凍結保全し、新規生成分から新配置（evidence／runtime）へ書く
- 凍結対象（実測値は棚卸し記録のとおり）：`docs/notes/review-runs/`（124 run）、`.reviewcompass/specs/<feature>/` 内の reviews・conformance（約 500 件）、`docs/experiments/review-runs/`（2 run）、`.reviewcompass/post-write-review-runs/`（1 run）、ルート `logs/estimation/`、`docs/logs/autonomous-parallel/`
- 各旧置き場に凍結案内の README（凍結日・新置き場・凍結理由）を置く。README 追加は P1 の作業に含める
- 不動のため、文書リンクと effective prompt の SHA 固定への影響はない

### PLC-DEC-010：P1（新規分の新配置）は実アプリ pilot 前に実施

pilot で生成される証跡・生成物を最初から新配置に乗せるため、P1 を pilot 開始の前提作業とする。

### PLC-DEC-011：二重読み（旧パスの読み取り互換）の廃止は P3 と同時

P1 で入れる旧パス読み取り互換は、最終形移行の専用 reopen（P3）で名指し参照の張り替えと一括して廃止する。

### PLC-DEC-012：実験データは凍結（整理は別課題）

`docs/experiments/` の既存 review-run 2 件と `tools/experiments/` の実験データ 1,205 件は本配置規約の適用外として凍結する。研究データの整理は将来の別課題として扱う。

## P1 移行計画（段階 5 の作業分解）

| # | 作業 | 経路 | 完了条件への寄与 |
| --- | --- | --- | --- |
| 1 | `.reviewcompass/evidence/`・`.reviewcompass/runtime/` 区画の新設と区画 README | 書き込み後検証 | 区画と索引の存在 |
| 2 | ツール改修 a：effective-prompts・approvals・検査ログの書き込み先を `runtime/` へ（旧パス二重読み付き） | 保守記録＋TDD | 生成物が runtime に集約 |
| 3 | ツール改修 b：conformance 記録の出力先を `evidence/features/conformance-evaluation/conformance/` へ（二重読み付き） | 保守記録＋TDD（仕様の記録パス契約は #4 の reopen と整合させる） | 新規記録が evidence へ |
| 4 | 仕様 reopen：workflow-management（effective prompt・approvals・検査ログのパス契約、T-004）と conformance-evaluation（記録パス契約） | reopen 手続き | 仕様と実装の一致 |
| 5 | ツール改修 c：推定独立性ログ（`machine_verification.py`）を `evidence/estimation/` へ | 保守記録＋TDD | ルート logs/ の新規書き込み停止 |
| 6 | `.gitignore` 更新（`.reviewcompass/runtime/` の 1 行へ集約）と `INITIAL_SETUP_LLM_GUIDE.md` §8 の簡素化（判断 2 の解） | 文書は書き込み後検証 | 対象アプリ初期設定の簡素化 |
| 7 | 運用文書の追従：`WORKFLOW_NAVIGATION.md` の review-run 例示・`SESSION_WORKFLOW_GUIDE.md` の置き場記載を `evidence/review-runs/` へ | 書き込み後検証 | 新規 run の標準置き場の正本化 |
| 8 | 旧置き場 6 箇所への凍結案内 README | 書き込み後検証（docs 配下のみ） | 凍結の明示 |
| 9 | 配布物の再生成と配布前 smoke（deploy-manifest への影響確認を含む） | ツール実行 | 配布整合 |

実施順序は表の番号順を基本とする（2・3・5 のツール改修は仕様 reopen（4）と同一サイクルで先行テスト可。fail-closed の根拠は設計記録 §5：書き込み先の変更＋読み取り互換のみで、検証対象判定は変更しない）。

## P1 完了条件

1. 新規の review-run・manifest・conformance 記録・推定ログが新配置に生成される（実 run で確認）
2. 対象アプリの `.gitignore` 手順が 1 行になり、`INITIAL_SETUP_LLM_GUIDE.md` §8 が追従している
3. 全テスト群が通過し、`next --json` が正常（completed または正規の次 action）
4. 配布前 smoke が合格する
5. 旧置き場 6 箇所に凍結案内 README がある

## 段階 5 への引き継ぎ

- 上表 #1〜9 を段階 5 の作業一覧とする。着手指示があり次第、#2〜5 は保守記録（side track）と TDD、#4 は reopen 手続きで進める
- P3（最終形）の専用 reopen 計画は pilot 後に別途起こす（PLC-DEC-008・011）

## P1 完了判定（2026-06-13）

P1 移行計画 #1〜9 を全消化し、P1 完了条件 5 項目の充足を確認した。

| 完了条件 | 判定 | 証跡 |
| --- | --- | --- |
| 1. 新規生成物が新配置に生成される（実 run で確認） | 充足 | review-run は `.reviewcompass/evidence/review-runs/`（reopen の triad-review・書き込み後検証の計 7 run）。検査ログ・effective prompt・commit 承認レコードは `.reviewcompass/runtime/`（実機 `next`・guarded commit で確認）。推定ログ・conformance 記録の切替は TDD（凍結期挙動テスト）で機械検証（コミット `dc5708fa`・`106a0c37`） |
| 2. 対象アプリの gitignore 手順が 1 行・ガイド §8 追従 | 充足 | `INITIAL_SETUP_LLM_GUIDE.md` §8 手順 5（コミット `cb022e92`） |
| 3. 全テスト群通過・`next --json` 正常 | 充足 | ディレクトリ別 計 921 件 pass、`next` は completed |
| 4. 配布前 smoke 合格 | 充足 | `build-deploy-package.py --clean --verify --smoke-external-app-root` 合格（269 ファイル、evidence／runtime 除外・`tools/check_workflow_action/` 同梱を確認） |
| 5. 旧置き場 6 箇所に凍結案内 README | 充足 | `docs/notes/review-runs/`・`.reviewcompass/post-write-review-runs/`・`.reviewcompass/specs/{conformance-evaluation,workflow-management}/conformance/`・`logs/estimation/`・`docs/logs/`（コミット `cb022e92`） |

経路の記録：#4（仕様 reopen）は ce＝R-0（`stages/completed/reopen-procedure-2026-06-12-placement-p1-ce.yaml`）・wm＝D-0（同 `-wm.yaml`）として完了。#2・3・5 のツール改修は各 reopen の implementation 段（TDD）で実施。#1 は区画新設済み（`.reviewcompass/evidence/README.md`）。本判定の反映により段階 5＝完了（計画文書の状態欄を更新）。
