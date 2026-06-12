---
date: 2026-06-12
record_type: document-placement-target-design
status: ready
placement_note: 本記録自体の置き場は暫定（配置規約の決定後に正式な置き場へ従う）。
related:
  - 2026-06-12-document-placement-inventory.md
  - 2026-06-12-document-placement-plan.md
  - 2026-06-12-document-placement-stage2-decisions.md
---

# 文書配置規約 段階 3：目標配置の設計

配置規約策定計画の段階 3 の成果物。入力は段階 2 の利用者決定（PLC-DEC-001〜008）と段階 1 の実測棚卸し。本記録は設計であり、実装・移動は行わない。移行範囲の最終判断は段階 4、実装は段階 5。

## 1. 目標配置表

「当面形」は実アプリ pilot 前に到達する配置（PLC-DEC-008 の案 a 期）、「最終形」は pilot 後の専用 reopen で到達する配置（同・案 b。開発リポジトリも対象アプリと同型にする）。

### 1.1 対象アプリ（＝最終形の骨格。原則 1：生成物は `.reviewcompass/` に閉じる）

| 種別 | 置き場 |
| --- | --- |
| 1 正本仕様 | `.reviewcompass/specs/<feature>/`（requirements・design・tasks・spec.json・implementation-drafting）、`.reviewcompass/feature-dependency.yaml` |
| 2 証跡記録 | `.reviewcompass/evidence/`（内部構造は §2） |
| 3 規律・運用 | `.reviewcompass/AGENT_ENTRY.md`＋配布された規律（最終形では開発リポジトリの operations／disciplines と同型） |
| 4 実行時生成物 | `.reviewcompass/runtime/`（原則 git 無視。内部構造は §2） |
| 5 セッション記録 | `.reviewcompass/evidence/sessions/` |
| 6 学習資産 | `.reviewcompass/learning/`（carry-forward register 等。required_inputs の抽象入力経由で参照） |
| 7 配布物定義 | （対象アプリ側には持たない。配布元の deploy-manifest が正本） |

### 1.2 開発リポジトリ（ReviewCompass 自身）

| 種別 | 当面形 | 最終形 |
| --- | --- | --- |
| 1 正本仕様 | `.reviewcompass/specs/<feature>/`（正本のみ・PLC-DEC-003）、`intent/`、`stages/` の正本 3 件（intent.yaml・feature-dependency.yaml・feature-partitioning） | 対象アプリと同型（`intent/`・`stages/` 正本の扱いは P3 の reopen で確定） |
| 2 証跡記録 | `.reviewcompass/evidence/`（新規分から。既存分は段階 4 判断） | 同左 |
| 3 規律・運用 | `docs/operations/`・`docs/disciplines/`（現状維持・PLC-DEC-008） | `.reviewcompass/` 配下へ移行 |
| 4 実行時生成物 | `.reviewcompass/runtime/`（git 無視） | 同左 |
| 5 セッション記録 | `docs/sessions/`（人が読む開発文書として） | 対象アプリと同型へ寄せるか P3 で判断 |
| 6 学習資産 | `learning/`（現状維持） | `.reviewcompass/learning/` へ |
| 7 配布物定義 | `templates/`・`deploy-manifest.yaml`・hooks（現状維持） | 同左（配布元固有） |
| 開発文書 | `docs/`＝人が読む開発リポジトリ専用文書（notes・plan・experiments・archive・sessions。PLC-DEC-006） | 同左 |
| 手続き記録 | `stages/in-progress/`・`stages/completed/`（当面動かさない） | `.reviewcompass/evidence/procedures/` へ |
| 製品コード | `tools/`・`analysis/`・`runtime/`・`evaluation/`・`tests/`（本規約の対象外。`tools/experiments/` の実験データ 1,205 件の整理は将来課題として記録のみ） | 同左 |

## 2. evidence／runtime 区画の内部構造（PLC-DEC-004・005）

```
.reviewcompass/
  specs/<feature>/                     # 正本のみ
  evidence/
    features/<feature>/reviews/        # 旧 specs/<feature>/reviews/（証跡・ポインタ記録）
    features/<feature>/conformance/    # 旧 specs/<feature>/conformance/
    cross-feature/reviews/             # 旧 specs/_cross_feature/reviews/
    review-runs/<run-id>/              # 旧 docs/notes/review-runs/・docs/experiments/review-runs/・
                                       #   .reviewcompass/post-write-review-runs/ を統合（置き場 3 箇所の解消）
    post-write/                        # 最終形：manifest と素材。当面は現行
                                       #   .reviewcompass/post-write-verification/ を evidence 区画の一部とみなす
    estimation/<run-id>/               # 旧ルート logs/estimation/（prompt.log は証跡・PLC-DEC-005）
    ledgers/autonomous-parallel/       # 旧 docs/logs/autonomous-parallel/（手続きの証跡）
    procedures/                        # 最終形のみ：旧 stages/in-progress・completed
    sessions/                          # 対象アプリのセッション記録（PLC-DEC-007）
  runtime/                             # 原則 git 無視（.gitignore は .reviewcompass/runtime/ の 1 行）
    effective-prompts/                 # 旧 .reviewcompass/effective-prompts/
    approvals/                         # 旧 .reviewcompass/approvals/（commit-approval.json）
    logs/                              # 旧 docs/logs/workflow-precheck.log ほか実行時ログ
  feature-dependency.yaml              # 対象アプリの標準配置。開発リポジトリの当面形は
                                       #   stages/feature-dependency.yaml のまま（探索順で両対応）
```

命名規約：日付付き記録は `YYYY-MM-DD-<slug>.md`、run-id は `<日付>-<内容>-<段>`。各区画直下に README（索引と置き場の根拠）を置く。`supersedes:` 前付けで改訂版から旧版を指す。非 ASCII ファイル名は新規作成では使わない。

## 3. パス契約への影響分析（論点 7）

棚卸しで確認した固定参照 40 種超を、変更要否で分類する。

### 3.1 当面形（P1）で変更が必要な契約

| 契約 | 現行 | 変更内容 |
| --- | --- | --- |
| review-run の標準置き場（運用文書の慣行） | `docs/notes/review-runs/<run-id>` | `WORKFLOW_NAVIGATION.md` §post_write_verification の例示と `SESSION_WORKFLOW_GUIDE.md` の記載を `.reviewcompass/evidence/review-runs/` へ。ツールは `--review-run-dir` 引数渡しのため**コード変更不要** |
| conformance 記録の出力先 | `evaluation_record.py`・`post_hoc_intent_diff.py` が `.reviewcompass/specs/conformance-evaluation/conformance/` へ書く | `.reviewcompass/evidence/features/conformance-evaluation/conformance/` へ（ツール変更＋conformance-evaluation 仕様の記録パス契約の reopen） |
| 推定独立性ログ | `machine_verification.py` がルート `logs/estimation/` へ書く | `.reviewcompass/evidence/estimation/` へ（ツール変更） |
| 対象アプリの gitignore 手順 | `INITIAL_SETUP_LLM_GUIDE.md` §8 が複数パスを列挙 | `.reviewcompass/runtime/` の 1 行に簡素化（判断 2 の解。effective-prompts・approvals・実行時ログを runtime へ集約することが前提） |
| effective prompt・approvals の置き場 | `.reviewcompass/effective-prompts/`・`.reviewcompass/approvals/`（ツール固定参照） | `.reviewcompass/runtime/` 配下へ（ツール変更＋.gitignore 追従。workflow-management 仕様の reopen） |
| 検査ログ | `DEFAULT_LOG_PATH=docs/logs/workflow-precheck.log`（無視済み・検証除外済み） | `.reviewcompass/runtime/logs/` へ（ツール変更。除外規則も追従） |

### 3.2 変更が不要な契約（当面形）

- feature 一覧の探索順（`.reviewcompass/` → `stages/` → 直下）：そのまま
- 書き込み後検証の対象判定（`docs/` 配下＋TODO）：**変更不要**。新 evidence 区画は `.reviewcompass/` 配下のため現行判定で自動的に対象外となり、生データが docs から出ることで対象が自然に縮小する（fail-closed を保ったまま）
- manifest の置き場（書き手 `review_triage.py:1140`・読み手 check-workflow-action の `.reviewcompass/post-write-verification/`）：当面そのまま（evidence 区画の一部とみなす。物理改名は P3）
- `stages/in-progress/`・`completed/` の手続き接頭辞、規律・運用文書の名指し参照（9 件超）、`intent/` 4 ファイル、`learning/workflow/` 5 パス、TODO、deploy-manifest の include：当面そのまま

### 3.3 最終形（P3）で変更する契約

規律・運用文書の名指し参照群、`stages/` 手続き接頭辞、manifest 置き場の改名、`learning/` 移行、（判断により）`docs/sessions/`。いずれも pilot 後の専用 reopen で一括計画する（PLC-DEC-008）。

## 4. 書き込み後検証の対象定義の再定義（論点 12）

現行実装（`docs/` 配下＋TODO、archive・検査ログ除外）を**種別語彙で言い直し、意味は変えない**：

> 書き込み後検証の対象は「人が読む正本・記録のうち、他のレビューゲート（triad-review／reopen／conformance）で検証されないもの」＝規律・運用文書、人が読む開発文書（docs）、入口メモ（TODO）。証跡記録（evidence）は検証の**出力**であり対象外。実行時生成物（runtime）は対象外。正本仕様（specs）は reopen 系ゲートが担うため対象外。

この再定義により、評価生データが evidence へ移った後の対象縮小が「定義どおりの挙動」になる。**当面形（P1）では**対象判定の実装変更は不要（fail-closed 維持）。最終形（P3）で規律・運用文書が `.reviewcompass/` 配下へ移る際は、対象判定の実装変更（プレフィックス・名指し参照の張り替え）が必要であり、§3.3 の専用 reopen に含める。

## 5. 移行順序の設計（fail-closed を壊さない 3 フェーズ）

| フェーズ | 時期 | 内容 | 経路 |
| --- | --- | --- | --- |
| P1：新規分の新配置 | 実アプリ pilot 前 | evidence／runtime 区画を新設し、**新規に生成される**証跡・生成物から新配置へ書く。ツールの書き込み先変更（§3.1）は旧パスの読み取り互換（二重読み）を残す。ガイド・ナビゲーション文書の記載追従。gitignore 簡素化 | ツール＝保守記録＋TDD。仕様の記録パス契約＝reopen。文書＝書き込み後検証 |
| P2：既存証跡の扱い | 段階 4 で判断 | 原則 5 のデフォルトは「動かさない」（旧置き場は凍結し、README で新置き場を案内）。動かす場合はリンク修復＋文書リンク lint 通過をセットにする | 段階 4 の利用者決定 |
| P3：最終形への移行 | pilot 後 | 規律・運用・stages 手続き・manifest 置き場・learning の `.reviewcompass/` 移行。検証対象定義の名指し参照の張り替え。二重読みの廃止 | 専用 reopen として一括計画 |

順序の根拠：P1 は「書き込み先の変更＋読み取り互換」だけなので、どの時点でも機械ガードが破綻しない。検証対象判定は変更しないため、移行中に検証漏れが生じる経路がない。pilot で生成される証跡を最初から新配置に乗せられる。

## 6. 段階 4 への引き継ぎ（未決事項）

1. **既存証跡の物理移動の範囲**：推薦は「動かさない」（新規のみ新配置）。docs/notes/review-runs の既存 124 run・specs 内の証跡約 500 件は凍結し README で案内。全移動する場合のコスト（リンク修復・effective prompt の SHA 再生成・履歴追跡性）は本記録 §3 が前提
2. **P1 の実施時期**：推薦は pilot 前（pilot の生成物が最初から新配置に乗る）
3. **二重読みの廃止時期**：推薦は P3 と同時
4. **`docs/experiments/` の既存 review-run 2 件と `tools/experiments/` 実験データ 1,205 件の扱い**：本設計では対象外として凍結を推薦（研究データの整理は別課題）
