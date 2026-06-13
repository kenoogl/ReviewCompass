# 書き込み後検証対象（PLC-DEC-007 訂正・追補＋完了判定の繰り越し注記＋TODO 候補 4〜6、3 ファイル束。round-4）


---

## 対象ファイル: docs/notes/2026-06-12-document-placement-stage2-decisions.md

---
date: 2026-06-12
record_type: document-placement-stage2-decisions
status: decided
placement_note: 本記録自体の置き場は暫定（配置規約の決定後に正式な置き場へ従う）。
related:
  - 2026-06-12-document-placement-inventory.md
  - 2026-06-12-document-placement-plan.md
---

# 文書配置規約 段階 2：分類軸と配置原則の利用者決定

配置規約策定計画（`2026-06-12-document-placement-plan.md`）の段階 2 の成果物。実測棚卸し（`2026-06-12-document-placement-inventory.md`）を根拠に、2026-06-12 の議論で利用者が決定した。決定 ID は PLC-DEC-001〜008。

## 決定台帳

### PLC-DEC-001：文書種別の分類軸（7 種）を採用

| # | 種別 | 性質 |
| --- | --- | --- |
| 1 | 正本仕様 | 承認・reopen でのみ変更。機械ガードの対象（intent、requirements／design／tasks／spec.json、feature-dependency） |
| 2 | 証跡記録 | 日付付き・事後不変（reviews、conformance、review-run 一式、manifest、reopen／保守記録） |
| 3 | 規律・運用 | 正本の一種だが、ナビゲータ等が機械的に名指し参照する |
| 4 | 実行時生成物 | 再生成可能または実行時状態。原則 git 無視（effective-prompts、検査ログ、approvals、build） |
| 5 | セッション記録 | 証跡の一種だが人間向け対話要約。一次ソース（会話転写）と機械抽出の扱いは PLC-DEC-007（2026-06-13 訂正） |
| 6 | 学習資産 | 横断的・育てる文書（carry-forward register、提案、スキーマ） |
| 7 | 配布物定義 | 対象アプリへ渡すもの（templates、deploy-manifest、hooks） |

### PLC-DEC-002：配置原則（5 つ）を採用

1. 二重基準の明示：規約は「開発リポジトリ」と「対象アプリ」のどちらの話かを常に区別する。対象アプリ側で生成されるものは `.reviewcompass/` 配下に閉じる
2. 正本と証跡の分離：正本の置き場に証跡を混ぜない
3. 人が読む文書と機械の生データの分離
4. 実行時生成物は 1 区画に集約し、原則 git 無視
5. 過去記録は原則動かさない（動かす場合は参照修復とセット。最終判断は段階 4）

### PLC-DEC-003（論点 1）：specs は正本のみ（案 a）

`.reviewcompass/specs/<feature>/` は正本（requirements／design／tasks／spec.json・implementation-drafting 等）のみとする。証跡（reviews・conformance、実測で specs の 93%）は証跡区画（例：`.reviewcompass/evidence/<feature>/`）へ分離する。物理移動の要否・範囲は段階 4 で決める。

### PLC-DEC-004（論点 2）：`.reviewcompass/` は specs／evidence／runtime の 3 区画

- `specs/`：正本のみ（PLC-DEC-003）
- `evidence/`：証跡（reviews・conformance・review-run・manifest 等）。書き込み後検証の manifest と検証素材の混在、post-write run の置き場二重（`docs/notes/review-runs/`・`.reviewcompass/post-write-review-runs/`）もここへ統合して解消する
- `runtime/`：実行時生成物（effective-prompts・approvals・ログ等）。原則 git 無視

### PLC-DEC-005（論点 3）：実行時ログは runtime に集約。prompt.log は証跡

実行時ログは runtime 区画 1 箇所に集約し原則 git 無視とする。ただし以下は性質が「ログ」ではない：

- ルート `logs/estimation/<run_id>/prompt.log`：conformance 推定の独立性（自律探索禁止・上流遮断がプロンプトに含まれた事実）を裏付ける**証跡記録**（書き手は `tools/conformance_evaluation/machine_verification.py`）。evidence 区画へ（新規分から適用）
- `docs/logs/autonomous-parallel/` の計画・台帳：手続きの**証跡記録**。evidence 区画へ

### PLC-DEC-006（論点 4）：docs は人が読む開発リポジトリ専用文書に限定

`docs/` は議論メモ・計画・実験・保管庫・セッション記録など「人が読む、開発リポジトリ固有の文書」に限定する。review-run の生データ（実測 1,152 件、docs/notes の 95%）は evidence 区画へ。

### PLC-DEC-007（論点 5）：セッション会話の転写を一次ソースとし、機械抽出でセッション記録を生成する（2026-06-13 訂正）

- **全セッションの会話転写を一次ソースと位置づける（選別しない）**。実測で Claude は `~/.claude/projects/<本プロジェクト>/*.jsonl` 46 件、Codex は `~/.codex/sessions/<年/月/日>/rollout-*.jsonl` 39 件（全プロジェクト混在のため絞り込み要）が機械可読で存在
- repo 側のセッション記録（共有可能な形）は、転写からの機械抽出ツールで生成する（日付・利用者指示と決定・コミット一覧・触れたファイル）。抽出ツールは実装課題（2026-06-13 時点で未実装）
- どのセッションを記録化するかの**選別規則は不要**：全セッションが一次ソースとして抽出可能であるため、選別の問題自体が消える（2026-06-13 利用者確認「これは不要になるのではないか」）。残る課題は抽出ツール側の 2 点＝機微情報の選別（無加工転記をしない）と、転写がローカル限定であること（共有可能な正本は repo 側の記録）
- 留意：転写の内部形式は公式契約ではない（版で変わりうる）
- **追補（2026-06-13、利用者決定「案 A」）**：整形・機微除去済みの**発言全文転写**（役割・時刻・利用者発言とアシスタント本文。ツール実行は要約参照に縮約）を repo の evidence 区画へ取り込む。抽出ツールの出力は 2 層（整形済み転写＋人が読むセッション記録）とする。根拠＝ローカル転写には永続保証がなく、裁定の遡及検証（台帳 ↔ 発言の突き合わせ。本決定の訂正がその実例）には repo 内の転写が必要。生 jsonl の無加工取り込みはしない（機微・容量・形式不安定）。過去分のバックフィルは**現存転写のみのベストエフォート**（実測 2026-06-13：Claude 47 件・約 142MB、Codex 39 件〔全プロジェクト混在〕。既に消去された過去セッション分は復元不能）。repo は公開リポジトリであり、取り込みは会話内容の公開を意味することを利用者了解のうえ決定
- **訂正記録（2026-06-13、利用者指摘・転写照合に基づく）**：本決定の旧文「セッション記録は引き金（利用者決定・reopen・アドホック開発・規律変更）で義務化（案 b）」は、操縦 LLM が再構成した決定案一覧への包括「OK」（2026-06-12）のみを根拠とした誤記録であり削除した。利用者の一次発言は「論点 5＝会話記録が手がかりになることもあり。claude/codex のログからとれないか？」（2026-06-12、転写 `837fa265-*.jsonl` で照合）であり、案 b の選択ではなく、転写の一次ソース化と機械抽出の調査指示だった。訂正文言は 2026-06-13 の利用者決定「案 1」による

### PLC-DEC-008（論点 6）：operations／disciplines は当面ルート docs/。最終形は `.reviewcompass/` 配下

- 当面：ルート `docs/operations/`・`docs/disciplines/` のまま（案 a）。理由はパス契約 40 種超の移行コストと実アプリ pilot 前の大移動リスク
- 最終形：ReviewCompass は自己適用が建前であり、自分自身も対象アプリと同じ配置で運用するのが正当（案 b）。規約に最終形として明記する
- 移行：実アプリ pilot 後に専用の reopen として計画する（段階的移行・二重参照期間を含む）

## 根拠とした実証事例（棚卸し記録より）

1. 運用必須の知見（API キー干渉の回避策）が実験ノートにのみあり、検証実行の失敗を直接生んだ（気づき 8）
2. 実態を主張する記録の誤り 11 件が書き込み後検証 2 回を所見ゼロで通過（検証役に実態アクセスがなく事実検証が構造的に不可能、気づき 9）
3. review-run の置き場 3 箇所・ログ 3 箇所・テスト 2 箇所への分裂、specs の証跡 93%、セッション記録 6/60+（気づき 1〜4）

## 段階 3 への引き継ぎ

- 7 種別 ×（開発リポジトリ／対象アプリ）の目標配置表を作る
- パス契約 40 種超・機械ガード・deploy-manifest への影響分析を付ける
- evidence／runtime 区画の内部構造（feature 別か日付別か、命名）を設計する
- 書き込み後検証の対象定義（現状 `docs/` プレフィックス）を新配置でどう定義し直すかを設計する（fail-closed を壊さない移行順序を含む）


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

繰り越し注記（2026-06-13 追記）：段階 5 の当初課題のうち本作業分解（#1〜9）に含めなかった未実施分は 2 件——(1) 配置規約の 1 本の正本文書化（計画文書の状態欄に記載どおり P3 計画時に再評価）、(2) **セッション記録の機械抽出ツール**（PLC-DEC-007 が段階 5 の実装課題としたが #1〜9 に含まれず未実施。引き継ぎ先＝PLC-DEC-007 の 2026-06-13 訂正・追補と TODO 次作業候補。本注記は完了判定時の記載漏れの補正）。


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

- `next --json`：**`completed`**（進行中手続きなし・全 workflow_state 完了）。未コミット 0・未公開 0（段階 5 完了判定を含む `682935f5` まで push 済み、2026-06-13）。
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
4. **P3（最終形）の専用 reopen 計画**：pilot 後に別途起こす（PLC-DEC-008・011）。主な項目＝disciplines／operations の `.reviewcompass/` 同型化（PLC-DEC-008 最終形）、旧パス読み取り互換の明示終了（PLC-DEC-011）、配置規約の「1 本の正本文書化」（段階 5 の未実施分）の再評価。
5. **セッション記録の機械抽出ツールの実装**：全セッションの会話転写（Claude `~/.claude/projects/<本プロジェクト>/*.jsonl`・Codex `~/.codex/sessions/...`）を一次ソースとして、出力 2 層を生成する（PLC-DEC-007 の 2026-06-13 訂正＋追補が正本）。(1) **整形・機微除去済みの発言全文転写**を evidence 区画へ取り込み（利用者決定「案 A」。裁定の遡及検証用。生 jsonl は無加工取り込みしない）、(2) 人が読むセッション記録（日付・利用者指示と決定・コミット一覧・触れたファイル）。選別規則は不要（全セッションが対象）。過去分のバックフィルは現存転写のみのベストエフォート（実測 2026-06-13：Claude 47 件・Codex 39 件混在。消去済み分は復元不能）。残る設計課題＝機微情報の除去規則・対象アプリ絞り込み（Codex）。
6. **裁定負荷対策（利用者決定の埋没防止）の規律改訂の検討**（利用者決定 2026-06-13「(b) で対応」）。動機事例＝PLC-DEC-007 の誤記録（6 論点の一括確認表＋包括「OK」により、利用者発言と食い違う決定文言が裁定されないまま台帳化された。訂正記録は同決定の 2026-06-13 訂正欄）。検討候補：(1) 決定台帳の各項目に利用者発言の引用（出典）を必須化し、包括承認のみの項目は確定として扱わない、(2) LLM が利用者発言を決定文言へ再構成した場合は原文との差分を並べて個別確認（a-1 の同型を利用者決定へ拡張）、(3) 台帳の決定 ID ごとの出典欄を lint で機械検査、(4) 抽出ツール（候補 5）による台帳 ↔ 転写の突き合わせ検証。
7. 検討材料：WP-001（外れ所見の原因分類軸）、`docs/notes/2026-06-11-agentic-flow-adoption-plan.md`。

## 5. 参照

- workflow navigation：`docs/operations/WORKFLOW_NAVIGATION.md`
- session guide：`docs/operations/SESSION_WORKFLOW_GUIDE.md`
- 配置規約一式：`docs/notes/2026-06-12-document-placement-{inventory,plan,stage2-decisions,target-design,stage4-migration}.md`
- reopen 分類記録：`docs/reviews/reopen-classification-2026-06-12-placement-p1-path-contracts.md`
- carry-forward register：`learning/workflow/carry-forward-register/reviewcompass-import.yaml`

過去の完了事項の履歴は git log と `docs/notes/`・`stages/completed/` の各記録を正本とする（本 TODO には残さない）。
