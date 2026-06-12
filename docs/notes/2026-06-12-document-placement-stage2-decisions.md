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
| 5 | セッション記録 | 証跡の一種だが人間向け対話要約。義務の引き金は PLC-DEC-007 |
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

### PLC-DEC-007（論点 5）：セッション記録は引き金で義務化＋転写からの抽出ツールを整備

- 引き金：利用者決定・reopen・アドホック開発・規律変更があったセッションは記録必須（案 b）
- 支援：操縦 LLM の転写からセッション記録の下書き（日付・利用者指示と決定・コミット一覧・触れたファイル）を生成する抽出ツールを整備する。実測で Claude は `~/.claude/projects/<本プロジェクト>/*.jsonl` 46 件、Codex は `~/.codex/sessions/<年/月/日>/rollout-*.jsonl` 39 件（全プロジェクト混在のため絞り込み要）が機械可読で存在
- 留意：転写の内部形式は公式契約ではない（版で変わりうる）。機微情報の選別が必要で無加工転記はしない。転写はローカル限定のため、共有可能な正本は repo 側の記録
- ツール実装は段階 5 の実装課題として扱う

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
