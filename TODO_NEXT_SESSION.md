# 次セッション継続用メモ

最終更新：2026-05-27（セッション 34 末、本セッションでの達成：アドホック変更整合性確保レビューを実施。agent 経由で計画書未反映または部分反映の 47 項目を時系列調査、重要 8 件（要確認 1〜8）を計画書 ／ 仕様文書側に反映完了、コミット 8 件（`24e9fb8` ／ `cfc43e8` ／ `429ddb8` ／ `2b2a484` ／ `5388d89` ／ `3935259` ／ `2509db7` ／ `c352ca3`）全 push 済み。主要成果：(1) §5.23.13 軽量手続き許容節を新設（6 サブ節、本 dogfooding をトライアル位置付け、§5.4 ／ §5.6 への相互参照付き）。(2) §5.9.7.1 ／ §7 段階的スケジュールへ API 経路先取り実装の明示。(3) §5.12.10 末尾に §5.12.11 アサイン権限の進行順序を相互参照。(4) §5.21.8 末尾に規律ファイル軽量移送の手続き 5 ステップを追記。(5) §5.9.6 末尾に N モデル比較実験への発展を相互参照。残り 23 件（影響度低）は §5.12 改訂時（全機能 tasks 段完了後）に統合対処する判断、3 重リマインダ（§5.23.13.3 末尾 ／ §5.12.10 末尾 ／ TODO §3）で予約済み。次セッション 35 は analysis 機能の tasks 段着手（依存マップ順 4/7）、または利用者提起の「同根問題のワークフロー修正議論」から再開）
作業ディレクトリ：`/Users/Daily/Development/ReviewCompass/`（本リポジトリ）
リポジトリ：`git@github.com:kenoogl/ReviewCompass.git`（main ブランチ）

---

<!-- TEMPLATE_HEADER_START：本ヘッダは templates/todo/TODO_NEXT_SESSION.template.md から派生。本セクションは削除・短縮しないこと。 -->

## 0. ReviewCompass 利用にあたる重要規律（削除禁止）

本セクションは ReviewCompass（dual-reviewer 方式の仕様駆動レビューシステム）を使うすべてのプロジェクトに共通する重要規律。**削除・短縮しないこと**。LLM が本 TODO を読む際、毎セッション開始時に本セクションを確認し、本セクションに書かれた手順を毎作業前に守る。

### 0.1 提案前必須確認

「次の作業」「次のステップ」を利用者に提案する前に、次を機械的に確認し、応答内で明示宣言する：

1. **`workflow_state` を必ず読む**：対象機能の `.reviewcompass/specs/<機能>/spec.json` の `workflow_state` を実際に Read で読む。要約や記憶を根拠にしない。本 TODO §3 や §4 に書かれた「次の作業候補」は要約に過ぎず、正本は spec.json の `workflow_state`
2. **規律と照合する**：運営ガイド `docs/operations/SESSION_WORKFLOW_GUIDE.md` §2.3 段の進め方の規律と照合し、次に進める段か（前段の approval まで完了しているか）を確認する。とくに「approval を得てから次フェーズに進む」（運営ガイド §2.3 第 6 項）の前提を毎回照合する
3. **TODO や要約文書を信頼せず、正本と照合する**：TODO・設計メモ・要約文の記述を信頼の根拠にしない。提案前に必ず spec.json／計画書／運営ガイド／git ログの正本と照合する

### 0.2 利用者明示承認が必要な不可逆操作

次の操作は利用者の **明示承認** なしに実行しない：

- spec.json の `workflow_state.<フェーズ>.approval` を true に変更
- spec.json のフェーズ移行
- git commit／git push
- 計画書の方針変更
- フェーズ移行に伴う一括処理
- 大規模な再設計（複数機能にまたがる責務分担変更等）

承認の判定基準：「承認します」「OK」「採用」「進めて」「はい」等の明示的肯定発言、または AskUserQuestion 等での明示選択のみ。議論継続・停止・方法論指示・沈黙・命名指摘は承認とみなさない。

### 0.3 起草者と判定者の分離（計画書 §5.4 規律）

drafting 段は actor=human または llm（草案作成のみ）、triad-review 段は actor=llm（主役・敵対役・判定役の 3 役、サブエージェント方式 §5.23.12 で実施）。**同一の actor が起草と判定を兼ねない**。

レビュー記録の front-matter には `author.identity` と `reviewer.identity` を異名で必須記載し、機械検査の対象とする。

### 0.4 AskUserQuestion を多用しない（2026-05-25 セッション 24 規律統廃合に伴い memory から移動）

確認は普通の文章で簡潔に。AskUserQuestion ツールは **4 つ以上の選択肢や視覚比較が必要な局面に限定** し、2〜3 個の選択や Yes／No には使わない。

利用者発言の出典：「(イ)の導入で他の規律を代用し、減らせる可能性はあるか」（2026-05-24 セッション 22）の指摘で制定、2026-05-25 セッション 24 で memory から TODO §0.4 に移動（規律統廃合の一環、利用者明示承認「AskUserQuestion を多用しないについては、TODOの冒頭に移すと規律が減る」）。

### 0.5 TODO 更新時は常にデータ削減を考える

本 TODO に追記・更新する際は、**常にデータ削減を検討する**。具体的には：

- 既存節への新規追記は最小限の行数で行う（パス列挙や詳細手順は別文書（README／git log／archive snapshot）に外部参照させる）
- 完了済み履歴は archive snapshot または git log への参照に置き換え、本 TODO には残さない
- 詳細説明は本 TODO 外（コミットメッセージ／design.md／README）に書き、本 TODO は要点のみ
- 更新後は総行数を測定し、肥大化していれば既存節の縮小余地も同時に検討する

経緯：2026-05-25 セッション 27 で利用者指摘「TODO が肥大化しているので、対応」「TODO 更新時は常にデータ削減を考える」により制定、利用者明示承認「案 A」。

<!-- TEMPLATE_HEADER_END -->

---

## 1. 起動手順（セッション 34 開始時）

ReviewCompass の運営ガイドラインの必読フローに従う：

1. ターミナルで `cd /Users/Daily/Development/ReviewCompass`
2. 本 `TODO_NEXT_SESSION.md` を読む（§0 重要規律を必ず確認）
3. **規律本体 active 必読を Read で読む**（最新の件数と一覧は `docs/disciplines/README.md` の「active 必読」表で確認。auto memory は索引のみ load し本体は load されないため毎セッション必要）
4. `docs/operations/SESSION_WORKFLOW_GUIDE.md` を読む（必読フロー・ワークフロー段の役割・サブエージェント方式の運用条件）
5. 計画書 `docs/plan/reconstruction-plan-2026-05-21.md` §5.4〜§5.8 を読む（ワークフロー手続き、reopen、session 跨ぎ、多層防御）
6. 計画書 §5.24 を読む（spec.json の正本スキーマ、2026-05-24 セッション 22 で新設）
7. 計画書 §5.12 を読む（人間代役機構、approval 段の actor=proxy_model 連動）
8. 計画書 §5.23 と §5.23.12 を読む（dogfooding と subagent_mediated 方式）
9. `.reviewcompass/pending-cross-feature-findings.md` を読む（持ち越し所見、現在 0 件未消化、全 16 件対処済み）
10. `docs/extraction-mapping.md` を読む（進行記録）
11. `git log --oneline -10`／`git status` で到達点確認

過去の経緯（セッション 19〜22 の詳細履歴、規律違反履歴、撤回履歴、過去の確定事項一覧等）は `docs/archive/todo/TODO_NEXT_SESSION-2026-05-24-snapshot.md` を参照。

### 1.5 シンボリックリンク検証結果（2026-05-25 セッション 27、fallback 案イ採用）

検証失敗：auto memory の起動時 load は MEMORY.md 索引（1 文要約）までで、シンボリックリンク経由でも規律本体はたどられない。**対処**：active 必読は §1 起動手順で毎セッション Read（参照層は必要時参照のまま）、シンボリックリンクは単一正本（repo）維持の補助として残置。最新の件数・分類は `docs/disciplines/README.md` 参照。詳細は本セッション 27 のコミットメッセージ参照。

## 2. ワークフロー上の現在位置（2026-05-27 セッション 33 末時点）

実態は **spec.json の workflow_state から確認**（§0.1 規律）：

- **intent 層／feature-partitioning 層**：すべて true
- **requirements 段**：全 7 機能で全段 true
- **design 段**：全 7 機能で全段 true（セッション 28 末）
- **tasks 段**：
  - **foundation**：drafting=true、triad-review=true（セッション 32）、以降 false
  - **runtime**：drafting=true、triad-review=true（セッション 33 で機能内対処完了、コミット 4372b0a）、以降 false
  - **evaluation**：drafting=true、triad-review=true（セッション 33 で機能内対処完了、本セッションコミット）、以降 false
  - 残 4 機能（analysis／workflow-management／self-improvement／conformance-evaluation）：tasks 段全 false
- **implementation 段**：全段 false
- **7 モデル比較実験**：foundation 16 件＋ runtime 16 件＋ evaluation 19 件＝ **合計 51 件完了**、実験ノート §5.3.1〜§5.3.4／§6.13 に集計

機能横断波及所見：A-001〜A-016 の 16 件対処済み、A-017（foundation F-011 由来）が機能横断段で対処予定（runtime F-012／A-007 は A-017 と同型扱いで重複登録なし）。詳細は `.reviewcompass/pending-cross-feature-findings.md`。

規律ファイル：本体は repo の `docs/disciplines/discipline_*.md` に配置、最新の件数・分類は `docs/disciplines/README.md`。

## 3. 次の作業候補（優先順位順）

**現在の主要作業：analysis の tasks 段着手 → 残 3 機能の tasks 段完了 → 機能横断段（tasks review-wave）→ §5.12 改訂検討 ＋ 同根問題のワークフロー修正議論**

セッション 33 末で foundation／runtime／evaluation の 3 機能 tasks 段の機能内対処まで完了。セッション 34 でアドホック変更整合性確保レビュー（重要 8 件、コミット 8 件）を完了。次セッション 35 は依存マップ順 4/7 の analysis 機能から再開：

1. **同根問題のワークフロー修正議論**（最優先で先に検討）：
   - 本セッション 33 で利用者提起：「全フィーチャーの triad-review を行い、それを 7 つのモデルで評価させたところで、同根の問題をまとめて考えるという必要性がでてきた」
   - 観察された同根の実例：F-008（人間レビュー承認、3 機能で同じ）、F-003（識別子連結保持、runtime A-002 と evaluation F-003）、F-006（陳腐化伝播の前提タスク不足、runtime A-004 と evaluation F-006）等
   - 候補方向：(α) triad-review 判定役に同根所見検出を必須化、(β) 7 モデル評価プロンプトに過去同根判定を注入、(γ) 全機能 triad-review 完了後に 7 モデル一括、(δ) 機能横断段に同根問題集約を明示
   - 利用者の構造的解決の苦悩：「ワークフロー遵守させるためのコストが大きい。なんとかならないものかね」「(A)＋(C) は過去にも実行しましたが、効果はありませんでした」 → (A)＋(C)（規律ファイル新設 ＋ memory 蓄積）は効果なしと判明、(B) フック機構が本質的解決だがコスト高、別の構造的解決を模索中

2. **analysis の tasks 段着手**（依存マップ順 4/7）：
   - foundation／runtime／evaluation の方針（一気通貫粒度、責務領域単位、要件追跡表、テスト戦略継承、完成判定基準、変更意図、DVT 等）を踏襲
   - tasks.drafting → サブエージェント方式で triad-review → 7 モデル比較実験 → 利用者判定（対話形式、完全一致は一括判定）→ 機能内対処
   - **同根問題への配慮**：先に上記 1 のワークフロー修正方針を確定してから着手するか、暫定対応として「triad-review 判定役に foundation／runtime／evaluation の過去判定を grep して同根識別」を加えるかを利用者と相談

3. **残 3 機能の tasks 段**（依存マップ順 5/7 〜 7/7）：workflow-management → self-improvement → conformance-evaluation。各機能で：tasks.drafting → triad-review → 7 モデル比較実験 → 機能内対処 → コミット → 次機能

4. **全機能 tasks 段完了後の作業**：
   - **機能横断段（tasks review-wave）**：A-017（foundation F-011 由来）と類似の波及項目（runtime F-012、A-007 含む）を全機能の tasks.md に対して一括対処
   - **DVT 解除**：evaluation DVT-001（T-009 の analysis 仕様起草後の下流接合面再評価）は analysis tasks 段完了時に解除トリガー発火
   - **design 軽量再オープン**：F-001（runtime T-002 ingestion_register 8 項目正本化）、F-015 関連（evaluation T-009 命名統一）等で発生する可能性
   - **計画書 §5.12 改訂検討と機能実装**（案 B 路線＝§5.12.11 新節新設、ReviewCompass 自身の implementation 段で dogfooding テスト、進行順序確定：2026-05-27 セッション 32）
   - **§5.12 改訂時の必須参照（2026-05-27 セッション 34 追記）**：§5.12.11 起草時には、計画書 §5.23.13.3 末尾「セッション 34 整合性確保レビューの結果」に記載の **残り 23 件**（影響度低の未反映 ／ 部分反映項目、影響範囲は git log のセッション 34 コミット 8 件 `24e9fb8`〜`(本コミット)` 以前で追跡可能）もあわせて統合的に取り込む。多重リマインダ（計画書 §5.23.13.3 末尾、計画書 §5.12.10 末尾の「§5.12.11 起草時の必須参照」段落、本 TODO §3）の一部、§5.12.11 起草作業中の参照漏れを防ぐ目的。利用者明示承認「案 W（」（2026-05-27 セッション 34）

7 モデル比較実験の構造（参考、本セッション 32 で確立した運用方式）：
- 比較対象 8 者：Opus 4.7（既出推奨）／Sonnet 4.6 CLI／Sonnet 4.6 API／GPT-5.5／GPT-5.4／Gemini-3.5-flash／Gemini-3.1-pro-preview／人本人
- 各機能で must-fix ＋ should-fix を対象（leave-as-is は除外）、合計 16 件程度
- 完全一致は要約一括判定、不一致は 1 件ずつ平易説明＋利用者判定の対話形式（判定支援資料は事前作成しない）

統計データ初期集計（実験ノート §6.13、2026-05-27 セッション 32）：
- 合計 32 件（foundation 16 ＋ runtime 16）で案 1 採用率 71.9%、別案 15.6%、案 2 12.5%
- モデル安定性序列：GPT-5.4（87.5%）> GPT-5.5 ≒ Gemini-flash（84.4%）> Opus 4.7 ≒ Sonnet CLI ≒ Gemini-pro（75〜76.7%）> Sonnet API（71.9%）
- 残 5 機能完了時点で合計約 112 件のデータ蓄積見込み、計画書 §5.12.11 新節の確定根拠とする

計画書 §5.5 phase_order の補正課題（セッション 26 で認識）：行 376〜383 の phase_order 構造例には self-improvement が記載漏れで 6 機能のみ列挙されているが、§3.1／§5.16 に基づき本設計では 7 機能を採用済み。計画書側の補正は別途追跡。

---

## 4. 直近の確定事項

利用者明示承認のあった項目を新しい順に記録（詳細は pending-cross-feature-findings.md ／ docs/disciplines/README.md ／ git log で追える）：

- **セッション 34（2026-05-27）の総括**：アドホック変更整合性確保レビューを実施。agent 経由で計画書未反映または部分反映 47 項目を時系列調査し、重要 8 件（要確認 1〜8）を計画書 ／ 仕様文書側に反映完了、コミット 8 件全 push 済み。主要反映：(1) `24e9fb8` 計画書 §5.23.13 軽量手続き許容節を新設（6 サブ節構成、本 dogfooding をトライアル位置付け、§5.4 ／ §5.6 への相互参照付き）。(2) `cfc43e8` API 経路先取り実装のフェーズ位置を §7 と §5.9.7.1 に明示。(3) `429ddb8` A-017 組み込み判断を pending-cross-feature-findings.md に追記。(4) `2b2a484` DVT 機構の正規化判断を evaluation/tasks.md 末尾に追記。(5) `5388d89` §5.12.11 アサイン権限の進行順序を §5.12.10 末尾に相互参照。(6) `3935259` 規律ファイル軽量移送の手続き 5 ステップを §5.21.8 末尾に追記。(7) `2509db7` N モデル比較実験への発展を §5.9.6 末尾に相互参照（要確認 7 を要確認 6 でカバー済みと統合）。(8) `c352ca3` 残り 23 件処理方針＋ 3 重化リマインダ（§5.23.13.3 末尾 ／ §5.12.10 末尾 ／ TODO §3 の §5.12 改訂検討項目）。残り 23 件（影響度低の未反映 ／ 部分反映）は §5.12 改訂時（全機能 tasks 段完了後）に統合的に対処する判断、3 重リマインダで予約済み。利用者明示承認の出典：「本dogfoodingがトライアル的意味合いを認識し、軽量 reopen ／ 軽量手続きを許容する。ただし、計画書、意図・仕様・設計･タスクに反映されていることを確認すること。最終的に、プロダクトと文書が整合性を保つことを目標に修正を行う」「ｂ。以降推奨案で自律的に進める」「案 c ／案 b ／案 a ／案 d ／案 b2 ／案 W」（要確認別の処理方針、2026-05-27 セッション 34）。次セッション 35 開始時の任意作業：§4 のセッション 32 ／ 33 の詳細記述を archive snapshot に退避（§0.5 データ削減規律）の要否を検討

- **セッション 33 後半（2026-05-27）の追加総括**：evaluation tasks 段全体（起草・triad-review・7 モデル比較実験・利用者判定・機能内対処）完了。(1) tasks.md 11 タスク起草（T-001〜T-011、約 230 行）。(2) サブエージェント方式 triad-review レビュー実施（主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7、所見 23 件：主役 16 件 ／ 敵対役独立発見 7 件、判定役判定 must-fix 8 ／ should-fix 11 ／ leave-as-is 4）。(3) 7 モデル比較実験：API 経路 5 モデル × 19 件 = 95 件、Gemini-flash 深掘り 3 件の turn-2、Sonnet 4.6 CLI Agent 並列 19 件、合計 117 件の判定経路。一致度：完全一致 13 件 ／ 分岐 6 件。(4) 利用者本人判定 19 件（topic-34〜52）：案 1 採用 14 件 ／ 別案採用 4 件（F-003 ／ F-012 改良版 A ／ A-006 ／ A-007 別案 A）／ 案 2 採用 0 件。(5) tasks.md 機能内対処 18 箇所 ＋ 遅延確認事項テーブル（DVT）セクション新設、レビュー記録新設、spec.json evaluation/tasks.triad-review=true。(6) 利用者重要発言：「同根の問題をまとめて考える必要性」「(A)＋(C) は過去にも実行しましたが、効果はありませんでした」「ワークフロー遵守させるためのコストが大きい。なんとかならないものかね」 → 構造的解決はフック機構（補助層 C 段階 3、計画書 §5.8）の前倒し検討が必要、本セッションでは結論先送り、次セッションで議論。(7) 表層的失敗の振り返り：実験ノート §3.1 を読まずに `zsh -c` で実験起動失敗、モデル名のドット表記／ハイフン表記の確認漏れ、(A)＋(C) を過去効果なしと知らず再提案、等。利用者明示承認の出典：「(イ)」「はい」「採用：別案」「採用：案 1」「採用：改良版 A」「採用：別案 A」「OK」「q」「採用：案 1」「採用：別案」（topic 個別判定）

- **セッション 33 前半（2026-05-27）の総括**：runtime tasks の機能内対処完了。(1) レビュー記録 §3.2 集計訂正 8 箇所（判定表からの再集計：must-fix 5 → 6、should-fix 11 → 10、leave-as-is 6 で計 22 件）。(2) tasks.md 14 箇所編集：議論論点 1（F-003 ／ A-001 連動、T-008 関連 3 箇所）、議論論点 2（F-005 ／ A-006 連動、T-005 ／ T-007 責務分離 4 箇所）、議論論点 3（A-002、Req 6 受入 6 責務整理 3 箇所）、議論論点 4（A-004、T-010 前提タスクに T-002 追加）、議論論点 5（F-010、T-011 完了条件に runtime 所有 3 語彙の正本確定機械検証）、should-fix 7 件（F-002 ／ F-006 ／ F-008 別案 ／ F-009 ／ F-013 ／ A-003 ／ A-005）。(3) 案 2 採用 2 件（F-012 ／ A-007）は tasks.md 変更なし、機能横断段に委ねる。leave-as-is 6 件は判定のみ記録。(4) レビュー記録 §4.1 見出し訂正、§4.2 利用者判定履歴新設（16 件を topic-NN-human.yaml への出典付き表で記録）、§4.3 反映箇所新設（14 件の編集箇所を行番号付き表で記録）、§4.4 処理結果に更新。(5) spec.json の runtime/tasks.triad-review を true に更新（事前検査 OK）。コミット 4372b0a を push 済。(6) 利用者フィードバック：「やたらと承認をもとめてくるなあ」 → 大きな枠の承認（例：(イ)）後は判定反映を止めず自律進行、不可逆操作（spec.json ／ commit ／ push ／ フェーズ移行）のみ承認を取る運用に切り替える。利用者明示承認の出典：「(イ)」（実験段階の判定を合意済みとみなす運用、本セッション開始時）／「はい」x 5 件（議論論点 1〜5 反映）／「承認」（should-fix 7 件一括）／「承認」（spec.json 更新）／「a」（commit WARN 承知）／「a のあと、b」（push → TODO 更新）

- **セッション 32（2026-05-27）の総括**：(1) 第 2 段階完了（should-fix 7 件、topic-11〜17）、利用者判定 案 1: 3／別案: 4／案 2: 0、別案集約・再議論パターンの実例化（§6.9.7）。(2) foundation tasks の機能内対処完了（must-fix 10＋should-fix 6＋A-017 機能横断波及追加、spec.json foundation/tasks.triad-review=true）、コミット c044ff6＋6b34a22。(3) runtime tasks の起草（11 タスク T-001〜T-011、author: claude-opus-4-7）→ triad-review レビュー実施（subagent_mediated、22 件 must-fix 6／should-fix 10／leave-as-is 6）→ コミット dff3525。(4) runtime 7 モデル比較実験完了（16 件、API 80＋CLI 16＋人本人 16、所要 API 21 分／実時間並列で約 8 分）→ 利用者判定 案 1: 13／案 2: 2／別案: 1、コミット e7d5bac（138 ファイル、+3802 行）。(5) 実験ノート §5.3.3／§5.3.4／§6.13 を新設、foundation＋runtime 合計 32 件の統計データ初期集計、モデル安定性序列を確定（GPT-5.4 最高 87.5%、Sonnet API 最低 71.9%）。(6) 重要な利用者発言：「完了条件というのは機械が判断するものか？」（機械判定が完了条件の必須条件ではないという認識、topic-26 議論の転換点）、「統一性重視」（topic-28／33、foundation 既存判定との一貫性優先）、「判定支援資料はほぼ意味をなさない、逐次平易説明で判定」（対話形式に切り替え、本セッション以降の標準運用）。(7) 進行順序確定：§5.12 改訂は全機能 tasks 段完了後、案 B 路線（§5.12.11 新節新設）、ReviewCompass implementation 段で dogfooding テスト。(8) 規律違反 1 件の自己振り返り：.gitignore コミット時に workflow-precheck commit を呼び忘れ（前段の DEVIATION 解決で意識から抜けた）

- **セッション 31（2026-05-27）の総括**：(1) 7 モデル比較実験（人間代役機構 §5.12 検証）の基盤整備＋第 1 段階完了。コミット cfb5db9（実験ノート初版）／5084746＋1e21138（TDD 5-A：GeminiProvider）／197940b＋60f9de4（TDD 5-B：マルチターン send_messages）／e34c4f5＋ad93688（TDD 5-C：_experiment_n_model.py）／a858432（予備実験完了、8 者全員「採用：案 1」）／f01597a（§2.6 12 評価観点の事前定義）／0e57bdb（第 1 段階完了、83 ファイル 2646 行追加）。(2) Gemini API 追加（gemini-3.5-flash／gemini-3.1-pro-preview、GEMINI_API_KEY は zsh 経由）、累積テスト 100 件 pass。(3) 5 者→ **7 モデル**比較実験に拡大（利用者明示承認「対象モデルを拡大し、google gemini API を追加する」セッション 31）。(4) 第 1 段階（must-fix 9 件 × 8 者）完了：完全一致 4 件／準一致 3 件／分岐 2 件、Sonnet 4.6 の CLI／API 経路差を観察、Gemini 系で質問発火 3 件（マルチターン 2 ターン目に進入）。(5) **重要発見**：分岐論点では proxy 役にアサイン権限（論文査読システム類似）を与える運用が有効、§5.12 改訂の論点として §6.9 に記録（利用者明示承認「d」セッション 31）。(6) settings.local.json に zsh -c 等の許可ルール追加（案 3：deny ルールで安全策）。(7) 判定支援資料 tools/experiments/judgment-aid-for-human.md 作成。(8) F-006（topic-05）と A-005（topic-10）は人本人が「平易な説明が必要」と要求、観点 3（質問能力）の人本人発火例

- **セッション 30（2026-05-26）の総括**：API 経路先取り実装サイクル 4 完成（4-A／4-B／4-C、累積 60 件 pass）、foundation／tasks.drafting＋triad-review レビュー実施（must-fix 10 件・should-fix 7 件・leave-as-is 4 件）、5 者比較実験の方針確定。詳細は git log（コミット ce02bc1／22721b4／3f95012／f1813f0／133c45b／3325b3d／9f1f472／576513b）参照

- **API 経路先取り実装の計画変更（軽量手続き、セッション 28、2026-05-26）**：本来フェーズ 4 第 2 サイクルで実装予定の API 経路を、tasks 段着手前に先取りで最小実装。3 者評価比較（Claude／API 経由他モデル：Anthropic ＋ OpenAI／人間）をパイロット → 段階的拡張で実施。計画書 §5.9.7.1 新設、§5.11 フェーズ 3 ／ フェーズ 4 第 2 サイクル改訂。設計済み 7 機能への遡及不要（実装方針の前倒しのみ）。利用者明示承認「API 実装を先取りで実装」「論点 2 ＝案 B」「論点 3 ＝案 b」「論点 4 ＝提示案どおり」「論点 5 ＝案 Z」「承認」（セッション 28）。設計案 P：オーケストレーター方式（Claude Code 内で私が呼び出しと結果統合）、役単位で path: cli / api を選択、API 経路は Python スクリプト `tools/api_providers/run_role.py`（1 役を 1 回実行、私が Bash で起動）、結果統合は私が手動（フェーズ 4 以降に自動化検討）。プロバイダー抽象層でモデル名は文字列指定、候補は Anthropic（claude-sonnet-4-6／claude-opus-4-7）と OpenAI（gpt-5.5／gpt-5.4／gpt-5.3-codex 等、セッション 29 で利用者更新）。論点 γ の進め方は (2)「yaml 構造設計を先行、モデル名はプレースホルダー、実装後に利用者が yaml で書き換え」を採用。利用者明示承認「提案どおりでよい」「提案で OK．実装後に yaml で書き換え」（セッション 28）「(2)。openai の場合、gpt-5.5, gpt-5.4, gpt-5.3-codex が候補」（セッション 29）

- **API 経路先取り実装：論点 α〜δ 確定と TDD サイクル 1〜3 完了（セッション 29、2026-05-26）**：論点 α（yaml 保存場所＝ `config/api-settings.yaml`、5961d1b）／論点 β（`run_role.py` 入出力契約、長オプション 6 種、標準出力 YAML、ac6eb63）／論点 γ（OpenAI 候補名 gpt-5.5／gpt-5.4／gpt-5.3-codex、進め方 (2) プレースホルダー方式、755fd6d）／論点 δ（yaml 命名規約 `connection`／`default`／`variants`、本体作成、19b1eeb）を確定。ディレクトリ命名整合修正（`tools/api-providers/` → `tools/api_providers/`、計画書 §4 行 209 規則準拠、8ddc674）。Python 環境整備（`pyproject.toml` 新規、`.venv` 隔離、`.gitignore` 更新、c2815db）。TDD サイクル 1（config_loader.py、c2815db／c57c5ae）／サイクル 2（providers.py プロバイダー抽象層、1ea0380／b1cb58c）／サイクル 3（providers.py の send_request、httpx／respx 依存、5eb051b／7778b80）累積 30 件全通過、回帰なし。利用者明示承認多数（コミットメッセージに記載、再オープン手続き 1 件含む：experiments 方式 → connection／default／variants）。次工程：サイクル 4（リトライ機構、yaml 出力整形、`run_role.py` エントリポイント）

- **design 段完全終了（セッション 28、2026-05-26、コミット 8cbb5b9／7cb8d6d／6b95a10）**：全 7 機能で drafting／triad-review／review-wave／alignment／approval すべて true。design.review-wave 全 16 件対処済み、章番号体系は機能内整合 OK／機能横断統一は案 C で許容、接合面整合 A-011〜A-016 全 6 件 OK、軽量一括承認（案 b）で approval 完了。利用者明示承認「案 X」「案 C」「案 b」「はい」x 多数（2026-05-26 セッション 28）。**次フェーズは tasks 段**

- **design.review-wave 全 16 件対処完了（セッション 28、2026-05-26、コミット e24d86e／c15ef5b／a2a65c0／04ab855／79ec3d9／92ff60a）**：3 グループ段階消化（① A-013：foundation 信頼度ラベル／② A-011／A-014／A-015：evaluation／analysis 接合面／③ A-012／A-016：self-improvement／workflow-management／conformance-evaluation 相互参照）。軽量再オープン手続き 2 件（A-013／A-011）を含む。詳細は pending-cross-feature-findings.md とコミットメッセージ参照

- **design 段 drafting＋triad-review 全 7 機能完了（セッション 25〜27、2026-05-25〜2026-05-26）**：foundation／runtime／evaluation／analysis／workflow-management／self-improvement／conformance-evaluation。詳細は各機能の spec.json workflow_state と git log（コミット 49aa7d8／7b57072／881761d／ffd8adc／dd8eba9／2177118／dda65ec／207a33e）参照

- **規律ファイル管理体制の整備（セッション 26〜27、2026-05-25〜2026-05-26）**：memory → docs/disciplines/ への軽量移送（16 件、シンボリックリンク化）、no-unilateral-action 撤去、複数案提示規律統合（discipline_options_presentation.md 新設・active 必読昇格）。詳細は docs/disciplines/README.md と git log（コミット b830785／b529c8e／9b9e827）参照

セッション 22〜24 の確定事項は archive snapshot に退避：[docs/archive/todo/TODO_NEXT_SESSION-2026-05-25-snapshot.md](docs/archive/todo/TODO_NEXT_SESSION-2026-05-25-snapshot.md)。
2026-05-21 までのさらに古い確定事項は別の snapshot：[docs/archive/todo/TODO_NEXT_SESSION-2026-05-24-snapshot.md](docs/archive/todo/TODO_NEXT_SESSION-2026-05-24-snapshot.md)。

## 5. 関連参照とスクリプト

- 計画書：`docs/plan/reconstruction-plan-2026-05-21.md`
- 運営ガイド：`docs/operations/SESSION_WORKFLOW_GUIDE.md`
- spec.json 正本スキーマ：計画書 §5.24
- TODO 雛形：`templates/todo/TODO_NEXT_SESSION.template.md`
- spec.json 雛形：`templates/specs/spec.json.template`
- レビュー記録雛形：`templates/review/manual_dogfooding_review_template.md`
- 持ち越し所見：`.reviewcompass/pending-cross-feature-findings.md`（0 件未消化、全 16 件対処済み）
- 抽出進捗：`docs/extraction-mapping.md`
- **規律ファイル本体**：`docs/disciplines/`（active 必読 12 件＋参照層 3 件＋ README.md）
- 規律ファイルディレクトリの解説：`docs/disciplines/README.md`
- 過去スナップショット 2 件：
  - `docs/archive/todo/TODO_NEXT_SESSION-2026-05-24-snapshot.md`（2026-05-21 までの確定事項）
  - `docs/archive/todo/TODO_NEXT_SESSION-2026-05-25-snapshot.md`（2026-05-22〜2026-05-25 セッション 24 末＋セッション 25 内の確定事項）

自動記録スクリプト（セッション終了時）：

```
cd /Users/Daily/Development/ReviewCompass
python3 tools/session-log-converter.py --latest \
    ~/.claude/projects/-Users-Daily-Development-ReviewCompass \
    docs/sessions/session-22-2026-05-24.md
```
