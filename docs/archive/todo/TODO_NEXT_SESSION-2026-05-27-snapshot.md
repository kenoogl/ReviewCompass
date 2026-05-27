# TODO_NEXT_SESSION スナップショット（2026-05-27 セッション 34 末）

本スナップショットは、2026-05-25 セッション 26 から 2026-05-27 セッション 33 末までの **TODO §4 直近の確定事項** を退避保管したもの。本セッション 34（2026-05-27）の TODO スリム化（案 C 採用、利用者明示承認「C」）の際に作成。

正本：[TODO_NEXT_SESSION.md](../../../TODO_NEXT_SESSION.md) の §4 直近の確定事項（本スナップショット作成時点の状態）。本スナップショット作成後、TODO §4 にはセッション 34 の総括と短い既存項目のみ残し、本スナップショットへの参照を §4 末尾と §5 関連参照に追加する。

退避の根拠：

- 規律 §0.5「TODO 更新時は常にデータ削減を考える」（2026-05-26 セッション 27 制定）
- 利用者明示承認「TODO が肥大。スリム化」「C」（2026-05-27 セッション 34）
- 過去 2 件のスナップショット（[TODO_NEXT_SESSION-2026-05-24-snapshot.md](TODO_NEXT_SESSION-2026-05-24-snapshot.md) ／ [TODO_NEXT_SESSION-2026-05-25-snapshot.md](TODO_NEXT_SESSION-2026-05-25-snapshot.md)）と同じパターンの退避

---

## 退避内容

### セッション 33 後半（2026-05-27）の追加総括

evaluation tasks 段全体（起草・triad-review・7 モデル比較実験・利用者判定・機能内対処）完了。(1) tasks.md 11 タスク起草（T-001〜T-011、約 230 行）。(2) サブエージェント方式 triad-review レビュー実施（主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7、所見 23 件：主役 16 件 ／ 敵対役独立発見 7 件、判定役判定 must-fix 8 ／ should-fix 11 ／ leave-as-is 4）。(3) 7 モデル比較実験：API 経路 5 モデル × 19 件 = 95 件、Gemini-flash 深掘り 3 件の turn-2、Sonnet 4.6 CLI Agent 並列 19 件、合計 117 件の判定経路。一致度：完全一致 13 件 ／ 分岐 6 件。(4) 利用者本人判定 19 件（topic-34〜52）：案 1 採用 14 件 ／ 別案採用 4 件（F-003 ／ F-012 改良版 A ／ A-006 ／ A-007 別案 A）／ 案 2 採用 0 件。(5) tasks.md 機能内対処 18 箇所 ＋ 遅延確認事項テーブル（DVT）セクション新設、レビュー記録新設、spec.json evaluation/tasks.triad-review=true。(6) 利用者重要発言：「同根の問題をまとめて考える必要性」「(A)＋(C) は過去にも実行しましたが、効果はありませんでした」「ワークフロー遵守させるためのコストが大きい。なんとかならないものかね」 → 構造的解決はフック機構（補助層 C 段階 3、計画書 §5.8）の前倒し検討が必要、本セッションでは結論先送り、次セッションで議論。(7) 表層的失敗の振り返り：実験ノート §3.1 を読まずに `zsh -c` で実験起動失敗、モデル名のドット表記／ハイフン表記の確認漏れ、(A)＋(C) を過去効果なしと知らず再提案、等。利用者明示承認の出典：「(イ)」「はい」「採用：別案」「採用：案 1」「採用：改良版 A」「採用：別案 A」「OK」「q」「採用：案 1」「採用：別案」（topic 個別判定）

### セッション 33 前半（2026-05-27）の総括

runtime tasks の機能内対処完了。(1) レビュー記録 §3.2 集計訂正 8 箇所（判定表からの再集計：must-fix 5 → 6、should-fix 11 → 10、leave-as-is 6 で計 22 件）。(2) tasks.md 14 箇所編集：議論論点 1（F-003 ／ A-001 連動、T-008 関連 3 箇所）、議論論点 2（F-005 ／ A-006 連動、T-005 ／ T-007 責務分離 4 箇所）、議論論点 3（A-002、Req 6 受入 6 責務整理 3 箇所）、議論論点 4（A-004、T-010 前提タスクに T-002 追加）、議論論点 5（F-010、T-011 完了条件に runtime 所有 3 語彙の正本確定機械検証）、should-fix 7 件（F-002 ／ F-006 ／ F-008 別案 ／ F-009 ／ F-013 ／ A-003 ／ A-005）。(3) 案 2 採用 2 件（F-012 ／ A-007）は tasks.md 変更なし、機能横断段に委ねる。leave-as-is 6 件は判定のみ記録。(4) レビュー記録 §4.1 見出し訂正、§4.2 利用者判定履歴新設（16 件を topic-NN-human.yaml への出典付き表で記録）、§4.3 反映箇所新設（14 件の編集箇所を行番号付き表で記録）、§4.4 処理結果に更新。(5) spec.json の runtime/tasks.triad-review を true に更新（事前検査 OK）。コミット 4372b0a を push 済。(6) 利用者フィードバック：「やたらと承認をもとめてくるなあ」 → 大きな枠の承認（例：(イ)）後は判定反映を止めず自律進行、不可逆操作（spec.json ／ commit ／ push ／ フェーズ移行）のみ承認を取る運用に切り替える。利用者明示承認の出典：「(イ)」（実験段階の判定を合意済みとみなす運用、本セッション開始時）／「はい」x 5 件（議論論点 1〜5 反映）／「承認」（should-fix 7 件一括）／「承認」（spec.json 更新）／「a」（commit WARN 承知）／「a のあと、b」（push → TODO 更新）

### セッション 32（2026-05-27）の総括

(1) 第 2 段階完了（should-fix 7 件、topic-11〜17）、利用者判定 案 1: 3／別案: 4／案 2: 0、別案集約・再議論パターンの実例化（§6.9.7）。(2) foundation tasks の機能内対処完了（must-fix 10＋should-fix 6＋A-017 機能横断波及追加、spec.json foundation/tasks.triad-review=true）、コミット c044ff6＋6b34a22。(3) runtime tasks の起草（11 タスク T-001〜T-011、author: claude-opus-4-7）→ triad-review レビュー実施（subagent_mediated、22 件 must-fix 6／should-fix 10／leave-as-is 6）→ コミット dff3525。(4) runtime 7 モデル比較実験完了（16 件、API 80＋CLI 16＋人本人 16、所要 API 21 分／実時間並列で約 8 分）→ 利用者判定 案 1: 13／案 2: 2／別案: 1、コミット e7d5bac（138 ファイル、+3802 行）。(5) 実験ノート §5.3.3／§5.3.4／§6.13 を新設、foundation＋runtime 合計 32 件の統計データ初期集計、モデル安定性序列を確定（GPT-5.4 最高 87.5%、Sonnet API 最低 71.9%）。(6) 重要な利用者発言：「完了条件というのは機械が判断するものか？」（機械判定が完了条件の必須条件ではないという認識、topic-26 議論の転換点）、「統一性重視」（topic-28／33、foundation 既存判定との一貫性優先）、「判定支援資料はほぼ意味をなさない、逐次平易説明で判定」（対話形式に切り替え、本セッション以降の標準運用）。(7) 進行順序確定：§5.12 改訂は全機能 tasks 段完了後、案 B 路線（§5.12.11 新節新設）、ReviewCompass implementation 段で dogfooding テスト。(8) 規律違反 1 件の自己振り返り：.gitignore コミット時に workflow-precheck commit を呼び忘れ（前段の DEVIATION 解決で意識から抜けた）

### セッション 31（2026-05-27）の総括

(1) 7 モデル比較実験（人間代役機構 §5.12 検証）の基盤整備＋第 1 段階完了。コミット cfb5db9（実験ノート初版）／5084746＋1e21138（TDD 5-A：GeminiProvider）／197940b＋60f9de4（TDD 5-B：マルチターン send_messages）／e34c4f5＋ad93688（TDD 5-C：_experiment_n_model.py）／a858432（予備実験完了、8 者全員「採用：案 1」）／f01597a（§2.6 12 評価観点の事前定義）／0e57bdb（第 1 段階完了、83 ファイル 2646 行追加）。(2) Gemini API 追加（gemini-3.5-flash／gemini-3.1-pro-preview、GEMINI_API_KEY は zsh 経由）、累積テスト 100 件 pass。(3) 5 者→ **7 モデル**比較実験に拡大（利用者明示承認「対象モデルを拡大し、google gemini API を追加する」セッション 31）。(4) 第 1 段階（must-fix 9 件 × 8 者）完了：完全一致 4 件／準一致 3 件／分岐 2 件、Sonnet 4.6 の CLI／API 経路差を観察、Gemini 系で質問発火 3 件（マルチターン 2 ターン目に進入）。(5) **重要発見**：分岐論点では proxy 役にアサイン権限（論文査読システム類似）を与える運用が有効、§5.12 改訂の論点として §6.9 に記録（利用者明示承認「d」セッション 31）。(6) settings.local.json に zsh -c 等の許可ルール追加（案 3：deny ルールで安全策）。(7) 判定支援資料 tools/experiments/judgment-aid-for-human.md 作成。(8) F-006（topic-05）と A-005（topic-10）は人本人が「平易な説明が必要」と要求、観点 3（質問能力）の人本人発火例

### セッション 30（2026-05-26）の総括

API 経路先取り実装サイクル 4 完成（4-A／4-B／4-C、累積 60 件 pass）、foundation／tasks.drafting＋triad-review レビュー実施（must-fix 10 件・should-fix 7 件・leave-as-is 4 件）、5 者比較実験の方針確定。詳細は git log（コミット ce02bc1／22721b4／3f95012／f1813f0／133c45b／3325b3d／9f1f472／576513b）参照

### API 経路先取り実装の計画変更（軽量手続き、セッション 28、2026-05-26）

本来フェーズ 4 第 2 サイクルで実装予定の API 経路を、tasks 段着手前に先取りで最小実装。3 者評価比較（Claude／API 経由他モデル：Anthropic ＋ OpenAI／人間）をパイロット → 段階的拡張で実施。計画書 §5.9.7.1 新設、§5.11 フェーズ 3 ／ フェーズ 4 第 2 サイクル改訂。設計済み 7 機能への遡及不要（実装方針の前倒しのみ）。利用者明示承認「API 実装を先取りで実装」「論点 2 ＝案 B」「論点 3 ＝案 b」「論点 4 ＝提示案どおり」「論点 5 ＝案 Z」「承認」（セッション 28）。設計案 P：オーケストレーター方式（Claude Code 内で私が呼び出しと結果統合）、役単位で path: cli / api を選択、API 経路は Python スクリプト `tools/api_providers/run_role.py`（1 役を 1 回実行、私が Bash で起動）、結果統合は私が手動（フェーズ 4 以降に自動化検討）。プロバイダー抽象層でモデル名は文字列指定、候補は Anthropic（claude-sonnet-4-6／claude-opus-4-7）と OpenAI（gpt-5.5／gpt-5.4／gpt-5.3-codex 等、セッション 29 で利用者更新）。論点 γ の進め方は (2)「yaml 構造設計を先行、モデル名はプレースホルダー、実装後に利用者が yaml で書き換え」を採用。利用者明示承認「提案どおりでよい」「提案で OK．実装後に yaml で書き換え」（セッション 28）「(2)。openai の場合、gpt-5.5, gpt-5.4, gpt-5.3-codex が候補」（セッション 29）

### API 経路先取り実装：論点 α〜δ 確定と TDD サイクル 1〜3 完了（セッション 29、2026-05-26）

論点 α（yaml 保存場所＝ `config/api-settings.yaml`、5961d1b）／論点 β（`run_role.py` 入出力契約、長オプション 6 種、標準出力 YAML、ac6eb63）／論点 γ（OpenAI 候補名 gpt-5.5／gpt-5.4／gpt-5.3-codex、進め方 (2) プレースホルダー方式、755fd6d）／論点 δ（yaml 命名規約 `connection`／`default`／`variants`、本体作成、19b1eeb）を確定。ディレクトリ命名整合修正（`tools/api-providers/` → `tools/api_providers/`、計画書 §4 行 209 規則準拠、8ddc674）。Python 環境整備（`pyproject.toml` 新規、`.venv` 隔離、`.gitignore` 更新、c2815db）。TDD サイクル 1（config_loader.py、c2815db／c57c5ae）／サイクル 2（providers.py プロバイダー抽象層、1ea0380／b1cb58c）／サイクル 3（providers.py の send_request、httpx／respx 依存、5eb051b／7778b80）累積 30 件全通過、回帰なし。利用者明示承認多数（コミットメッセージに記載、再オープン手続き 1 件含む：experiments 方式 → connection／default／variants）。次工程：サイクル 4（リトライ機構、yaml 出力整形、`run_role.py` エントリポイント）

### design 段完全終了（セッション 28、2026-05-26、コミット 8cbb5b9／7cb8d6d／6b95a10）

全 7 機能で drafting／triad-review／review-wave／alignment／approval すべて true。design.review-wave 全 16 件対処済み、章番号体系は機能内整合 OK／機能横断統一は案 C で許容、接合面整合 A-011〜A-016 全 6 件 OK、軽量一括承認（案 b）で approval 完了。利用者明示承認「案 X」「案 C」「案 b」「はい」x 多数（2026-05-26 セッション 28）。**次フェーズは tasks 段**

### design.review-wave 全 16 件対処完了（セッション 28、2026-05-26、コミット e24d86e／c15ef5b／a2a65c0／04ab855／79ec3d9／92ff60a）

3 グループ段階消化（① A-013：foundation 信頼度ラベル／② A-011／A-014／A-015：evaluation／analysis 接合面／③ A-012／A-016：self-improvement／workflow-management／conformance-evaluation 相互参照）。軽量再オープン手続き 2 件（A-013／A-011）を含む。詳細は pending-cross-feature-findings.md とコミットメッセージ参照

### design 段 drafting＋triad-review 全 7 機能完了（セッション 25〜27、2026-05-25〜2026-05-26）

foundation／runtime／evaluation／analysis／workflow-management／self-improvement／conformance-evaluation。詳細は各機能の spec.json workflow_state と git log（コミット 49aa7d8／7b57072／881761d／ffd8adc／dd8eba9／2177118／dda65ec／207a33e）参照

### 規律ファイル管理体制の整備（セッション 26〜27、2026-05-25〜2026-05-26）

memory → docs/disciplines/ への軽量移送（16 件、シンボリックリンク化）、no-unilateral-action 撤去、複数案提示規律統合（discipline_options_presentation.md 新設・active 必読昇格）。詳細は docs/disciplines/README.md と git log（コミット b830785／b529c8e／9b9e827）参照

---

## 関連参照

- 正本（縮約後）：[TODO_NEXT_SESSION.md](../../../TODO_NEXT_SESSION.md) §4
- 同種スナップショット 2 件：
  - [TODO_NEXT_SESSION-2026-05-24-snapshot.md](TODO_NEXT_SESSION-2026-05-24-snapshot.md)（2026-05-21 までの確定事項）
  - [TODO_NEXT_SESSION-2026-05-25-snapshot.md](TODO_NEXT_SESSION-2026-05-25-snapshot.md)（2026-05-22〜2026-05-25 セッション 24 末＋セッション 25 内の確定事項）
- 退避作業のコミット：本セッション 34 で作成（git log で参照可能）
- 利用者明示承認：「C」（TODO スリム化案 C 採用、2026-05-27 セッション 34）
