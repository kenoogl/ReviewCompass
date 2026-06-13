# 書き込み後検証対象（段階 5 完了判定と TODO 更新、3 ファイル束。round-1 所見＝status: completed 適用後。TODO の <root> は将来実行用の汎用例示として維持）


---

## 対象ファイル: TODO_NEXT_SESSION.md

# 次セッション継続用メモ

最終更新：2026-06-13。正本は `tools/check-workflow-action.py next --json` と各 feature の `spec.json`。この TODO は入口メモであり、作業順序の正本ではない。

ReviewCompass は、複数 LLM のレビュー結果を raw で保存し、三段階トリアージと人間／proxy_model の判断を経て、仕様・実装・規律を改善するための自己適用型レビュー基盤である（詳細は `intent/` と各 feature の仕様を正本とする）。

作業ディレクトリ：`/Users/Daily/Development/ReviewCompass/`
リポジトリ：`git@github.com:kenoogl/ReviewCompass.git`（main ブランチ）

## 1. 起動時に必ず行うこと

1. `.venv/bin/python3 tools/check-workflow-action.py next --json` を実行し、`next_action` を作業順序の正本として扱う。
2. `git status --short` と `git log --oneline -5` で到達点を確認する。
3. `next_action.required_disciplines` に出た規律だけを、操作直前に読む。
4. `post_write_verification`、`reopen_in_progress`、`resume_in_progress`、`unknown` が返った場合は通常作業へ進まない。

## 2. 不可逆操作の規律（要点）

- commit・push・spec.json（workflow_state）・規律ファイルの変更は、利用者の明示承認が必要。commit は利用者から「コミット」と明示された場合だけ、`tools/guarded-git-commit.py` 経由で実行する。
- commit 承認レコードの置き場は `.reviewcompass/runtime/approvals/commit-approval.json`（2026-06-13 の P1 実装で旧 `.reviewcompass/approvals/` から切替済み。委任欄 `explicit_instruction` は単発「コミット」等の機械判定に合う文字列で記録し、発言全文は rationale に残す）。
- API review-run は実行前に variant と役ごとの provider／model を提示し、結果は raw・モデル別要約・三段階トリアージをまとめて提示してから次へ進む。操縦 LLM 別の既定 variant と独立性原則の正本は `docs/operations/SESSION_WORKFLOW_GUIDE.md` §3.3 (a-3)。新規 review-run の置き場は `.reviewcompass/evidence/review-runs/<run-id>/`。
- Claude Code は子プロセスの `GEMINI_API_KEY`／`ANTHROPIC_API_KEY` を空に上書きする。API 実行は `zsh -c 'source ~/.zshrc && ...'` 経由（正本は `docs/experiments/n-model-comparison.md` §3.1）。
- 詳細の正本は `docs/operations/WORKFLOW_NAVIGATION.md` §2 と `docs/operations/SESSION_WORKFLOW_GUIDE.md`。

## 3. 現在位置（2026-06-13 時点）

- `next --json`：**`completed`**（進行中手続きなし・全 workflow_state 完了）。未コミット 0・未公開 0（`cb022e92` まで push 済み）。
- **文書配置規約は段階 5 まで完了**（計画 `docs/notes/2026-06-12-document-placement-plan.md` の状態欄が正。P1 完了判定は `docs/notes/2026-06-12-document-placement-stage4-migration.md`）。
  - 配置規約 P1 の reopen 2 本（ce＝R-0・wm＝D-0）は第 4 過程まで完了し `stages/completed/` にある。
  - 新配置の運用が開始済み：証跡は `.reviewcompass/evidence/`（review-runs・features/<feature>/conformance・estimation）、実行時生成物は `.reviewcompass/runtime/`（検査ログ・effective prompt・commit 承認レコード、gitignore 1 行）。旧置き場 6 箇所は凍結（各所の README が案内、読み取り互換は P3 まで）。
  - 凍結違反の機械検出：ce＝`tools/conformance_evaluation/machine_verification.py`（check_record_freeze 等）、wm＝`tools/check_workflow_action/placement_freeze.py`（手動実行手順は `docs/operations/WORKFLOW_PRECHECK_DETAILS.md` §8.1）。
- 全テスト：ディレクトリ単位で計 921 件 pass（同名テストファイルの衝突があるため `tests/` 一括ではなくディレクトリごとに pytest を実行する）。

## 4. 次作業（候補。正本は next --json と利用者指示）

`next` が `completed` のため、次は保留事項からの利用者選択になる：

1. **実アプリ pilot**：前提だった P1 完了（PLC-DEC-010）を充足。配布前 smoke も合格済み（`tools/build-deploy-package.py --clean --verify --smoke-external-app-root <root>`）。
2. **review-wave 要約コマンドの実装**：reopen で対応（利用者決定 2026-06-12）。
3. **レビュー証跡の機能側ポインタ要件の一般化**：配置規約の実装完了により再開可能（置き場の前提が確定済み）。
4. **P3（最終形）の専用 reopen 計画**：pilot 後に別途起こす（PLC-DEC-008・011）。配置規約の「1 本の正本文書化」（段階 5 の未実施分）もここで再評価。
5. 検討材料：WP-001（外れ所見の原因分類軸）、`docs/notes/2026-06-11-agentic-flow-adoption-plan.md`。

## 5. 参照

- workflow navigation：`docs/operations/WORKFLOW_NAVIGATION.md`
- session guide：`docs/operations/SESSION_WORKFLOW_GUIDE.md`
- 配置規約一式：`docs/notes/2026-06-12-document-placement-{inventory,plan,stage2-decisions,target-design,stage4-migration}.md`
- reopen 分類記録：`docs/reviews/reopen-classification-2026-06-12-placement-p1-path-contracts.md`
- carry-forward register：`learning/workflow/carry-forward-register/reviewcompass-import.yaml`

過去の完了事項の履歴は git log と `docs/notes/`・`stages/completed/` の各記録を正本とする（本 TODO には残さない）。


---

## 対象ファイル: docs/notes/2026-06-12-document-placement-plan.md

---
date: 2026-06-12
record_type: document-placement-plan
status: completed
placement_note: 本記録自体の置き場は暫定（利用者方針 2026-06-12。配置規約の決定後に正式な置き場へ従う）。
related:
  - 2026-06-12-document-placement-inventory.md
  - 2026-06-12-document-placement-stage2-decisions.md
  - 2026-06-12-document-placement-target-design.md
  - 2026-06-12-document-placement-stage4-migration.md
---

# 文書配置規約の策定計画（5 段階）

## 目的

ReviewCompass の開発過程で生成される文書は、どこに何を書くかを予め決めずに必要の都度配置してきたため整合性が取れていない。デプロイ後は対象アプリ側での生成文書になるため、「どこに何を配置するか」の規約を定める（利用者提起 2026-06-12）。

## 利用者提起の論点（6 件）

1. `.reviewcompass/specs/` 配下は feature の要件・設計などの正本および spec.json のみとすべきではないか（現状は reviews 等の証跡が 93% を占める）
2. `.reviewcompass/` 配下のその他のディレクトリの役割と、生成文書の置き場としての適否
3. `logs/` ディレクトリの使い方（実測では 3 箇所に分裂）
4. `docs/` の使い方（実測では人が読む文書が機械の生データに埋没）
5. LLM セッションのログ（対話は記録されないため事後確認用に記録する、が本来の目的）が守られていない。規律化すべきか（実測：repo 内 6 件に対し repo 外転写 46 件）
6. `docs/operations/`・`docs/disciplines/` はルート配置か `.reviewcompass/` 配下が適切か

## 追加の検討点（2026-06-12 合意）

7. ツールが読む・書くパス契約の棚卸しと影響分析（40 種超の固定参照）
8. 開発リポジトリと対象アプリの二重基準の明記（探索順の先例あり。配布の正本は deploy-manifest）
9. 過去記録と参照の保全方針（移すか、新規のみ新配置か。文書リンク lint・effective prompt の SHA 固定との整合）
10. git 管理区分（コミットする／無視する）との結合
11. 命名・日付・索引（README・supersedes）の規約
12. 検証義務との結合（書き込み後検証の範囲はパス定義そのもの。fail-closed を壊さない移行順序）

## 5 段階の進め方

| 段階 | 作業内容 | 成果物 | 手続き経路 | 状態 |
| --- | --- | --- | --- | --- |
| 1. 現状棚卸し | 全ディレクトリの実測（内容・書き手・参照元・ライフサイクル・検証義務・配布対象・git 区分）。repo 外の文書地点も含む | 現状配置マップ | 読み取りのみ＋記録の書き込み後検証 | **完了**（`2026-06-12-document-placement-inventory.md`、コミット `1782f9f2`。再精査で漏れ・誤り 11 件を訂正済み） |
| 2. 分類軸と配置原則の合意 | 文書種別（正本仕様／証跡記録／規律・運用／実行時生成物／セッション記録／学習資産／配布物）と「種別→置き場→ライフサイクル→検証→配布」の原則を議論し決定。論点 1〜6・8・10 とセッションログ規律化（論点 5）の要否・引き金をここで判断 | 利用者決定の台帳（MLE-DEC 方式）＋議論記録 | 議論＋記録の書き込み後検証 | **完了**（`2026-06-12-document-placement-stage2-decisions.md`、PLC-DEC-001〜008） |
| 3. 目標配置の設計 | 合意原則に基づく目標配置表＋影響分析（論点 7・12。パス契約・機械ガード・配布 manifest への波及一覧） | 設計記録 | 起草＋書き込み後検証 | **完了**（`2026-06-12-document-placement-target-design.md`） |
| 4. 移行方針の決定 | 全面移動／新規のみ新配置（過去は不動）／折衷の選択（論点 9）。変更の経路割り付け（仕様の意味変更→reopen、ツール→保守記録＋TDD、運用文書→書き込み後検証） | 移行計画＋利用者決定 | 議論＋記録 | **完了**（`2026-06-12-document-placement-stage4-migration.md`、PLC-DEC-009〜012） |
| 5. 実装と規律化 | 配置規約を 1 本の正本文書化。ツール・仕様・配布 manifest の追従。安価な機械検査（新規文書の置き場違反検知等）の追加 | 配置規約の正本＋実装＋検査 | reopen／保守記録＋TDD／書き込み後検証 | **完了**（2026-06-13。作業分解＝段階 4 記録の P1 移行計画 #1〜9 を全消化。完了判定は `2026-06-12-document-placement-stage4-migration.md` の「P1 完了判定」を参照。置き場違反の機械検査は凍結違反検出器（ce：`tools/conformance_evaluation/machine_verification.py`、wm：`tools/check_workflow_action/placement_freeze.py`）として実現。配置規約の「1 本の正本文書化」は段階 4 の作業分解に含めなかったため未実施＝P3（最終形）の専用 reopen 計画時に再評価する） |

## 議論に持ち込む実証事例（棚卸しで確定）

- 運用必須の知見（API キー干渉の回避策）が実験ノートにのみあり、検証実行の失敗を直接生んだ（棚卸し記録 気づき 8）
- 実態を主張する記録の誤り 11 件が書き込み後検証 2 回を所見ゼロで通過した。検証役に実態アクセスがなく事実検証が構造的に不可能（同 気づき 9）。検証役への実態アクセス付与または実測コマンドの再実行照合が改善候補
- 複数セッションにまたがる議論計画を機械追跡する手続き種別がない（2026-06-12 議論。進行中ファイルは範囲確定済みの修繕向けで、開かれた議論に使うと完了まで他作業を過剰遮断する）。本計画の継続は当面 TODO 入口メモと本計画記録で担保する

## 関連する保留・決定（2026-06-12）

- review-wave 要約コマンドの実装：次セッション以降に reopen で対応（利用者決定）
- レビュー証跡の機能側ポインタ要件の一般化：本配置議論の決定後に再開（置き場の前提が論点 1 に依存）
- 判断 2（実行時生成物：`.gitignore` 手順簡素化・`.reviewcompass/effective-prompts/` 運用）：本議論の論点 2・3・10 に合流

## 再開方法（次セッション向け）

1. `next --json` が `completed` であることを確認する
2. 本計画の「5 段階の進め方」の表の状態欄を唯一の正として「次の作業」を確認し、必要な関連記録（related と各段階の成果物）を読み込んでから作業を始める
3. 段階ごとの成果物は完成時に本計画の状態欄を更新する（更新は書き込み後検証を伴う）


---

## 対象ファイル: docs/notes/2026-06-12-document-placement-stage4-migration.md

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
