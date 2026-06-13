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
