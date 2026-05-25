# 次セッション継続用メモ

最終更新：2026-05-25（セッション 26 末、workflow-management／design 段の drafting＋triad-review 完了、依存マップ順 5/7。規律ファイル軽量移送（memory → docs/disciplines/、17 件→16 件）と memory 側のシンボリックリンク化を実施。次は self-improvement／design.drafting から再開）
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

## 1. 起動手順（セッション 27 開始時）

ReviewCompass の運営ガイドラインの必読フローに従う：

1. ターミナルで `cd /Users/Daily/Development/ReviewCompass`
2. 本 `TODO_NEXT_SESSION.md` を読む（§0 重要規律を必ず確認）
3. **規律本体 active 必読を Read で読む**（最新の件数と一覧は `docs/disciplines/README.md` の「active 必読」表で確認。auto memory は索引のみ load し本体は load されないため毎セッション必要）
4. `docs/operations/SESSION_WORKFLOW_GUIDE.md` を読む（必読フロー・ワークフロー段の役割・サブエージェント方式の運用条件）
5. 計画書 `docs/plan/reconstruction-plan-2026-05-21.md` §5.4〜§5.8 を読む（ワークフロー手続き、reopen、session 跨ぎ、多層防御）
6. 計画書 §5.24 を読む（spec.json の正本スキーマ、2026-05-24 セッション 22 で新設）
7. 計画書 §5.12 を読む（人間代役機構、approval 段の actor=proxy_model 連動）
8. 計画書 §5.23 と §5.23.12 を読む（dogfooding と subagent_mediated 方式）
9. `.reviewcompass/pending-cross-feature-findings.md` を読む（持ち越し所見、現在 A-011 が 1 件未消化）
10. `docs/extraction-mapping.md` を読む（進行記録）
11. `git log --oneline -10`／`git status` で到達点確認

過去の経緯（セッション 19〜22 の詳細履歴、規律違反履歴、撤回履歴、過去の確定事項一覧等）は `docs/archive/todo/TODO_NEXT_SESSION-2026-05-24-snapshot.md` を参照。

### 1.5 シンボリックリンク検証結果（2026-05-25 セッション 27、fallback 案イ採用）

検証失敗：auto memory の起動時 load は MEMORY.md 索引（1 文要約）までで、シンボリックリンク経由でも規律本体はたどられない。**対処**：active 必読は §1 起動手順で毎セッション Read（参照層は必要時参照のまま）、シンボリックリンクは単一正本（repo）維持の補助として残置。最新の件数・分類は `docs/disciplines/README.md` 参照。詳細は本セッション 27 のコミットメッセージ参照。

## 2. ワークフロー上の現在位置（2026-05-26 セッション 27 末時点）

実態は **spec.json の workflow_state から確認**（§0.1 規律）：

- **intent 層**：drafting／review／approval すべて true（intent 文書 4 件は 2026-05-24 に素材リポからコピー配置済み、`intent/` 配下）
- **feature-partitioning 層**：candidate-proposal／approval すべて true（`stages/feature-partitioning/2026-05-24-proposal.md` 配置済み）
- **requirements 段**：全 7 機能で drafting／triad-review／review-wave／alignment／approval すべて true（2026-05-24 セッション 23 末で完了）
- **design 段**：
  - foundation（1/7）：drafting／triad-review が true、review-wave／alignment／approval は false（セッション 25）
  - runtime（2/7）：同上（セッション 25）
  - evaluation（3/7）：同上（セッション 25）
  - analysis（4/7）：同上（セッション 25 末、コミット `7b57072`）
  - workflow-management（5/7）：drafting／triad-review が true、review-wave／alignment／approval は false（セッション 26、コミット `881761d`／`ffd8adc`）
  - self-improvement（6/7）：drafting／triad-review が true、review-wave／alignment／approval は false（セッション 27、コミット `dd8eba9`／`2177118`）
  - conformance-evaluation（7/7）：drafting／triad-review が true、review-wave／alignment／approval は false（**本セッション 27 末**、本セッション末コミット）
- **tasks／implementation 段**：すべて false

機能横断波及所見：A-001〜A-010 の 10 件は対処済み、**A-011〜A-016 の 6 件が未消化**（A-011：analysis／evaluation 接合面 `roles/role_diff_report.json`、A-012：self-improvement と workflow-management の時系列契約、A-013：信頼度ラベル foundation 追加要請、A-014：evaluation 突き合わせ詳細、A-015：analysis 機械可読出力スキーマ、A-016：target_commit と materialization_commit_hash 整合）。すべて design レビュー波段で消化予定。詳細は `.reviewcompass/pending-cross-feature-findings.md` を参照。

規律ファイルの現状：本体は repo の `docs/disciplines/discipline_*.md` に配置、memory 側 `feedback_*.md` はシンボリックリンクで repo 本体を指す。最新の件数・分類は `docs/disciplines/README.md` の規律ファイル一覧表を参照。本セッション 27 で options-presentation 統合規律と effekt 測定ログ（options-precheck-log.md）を新設。

## 3. 次の作業候補（優先順位順）

**現在の主要作業：B. 設計フェーズ継続（design.review-wave で機能横断波及所見の集約消化、その後 alignment／approval）**


### B. 設計フェーズ継続（review-wave、その後 alignment／approval）

セッション 27 末時点で全 7 機能の design.drafting＋triad-review が完了：foundation／runtime／evaluation／analysis／workflow-management／self-improvement／conformance-evaluation。次の作業：

1. **全 7 機能の design 段 review-wave**：機能横断波及所見 A-011〜A-016 の 6 件を集約消化
   - A-011：analysis／evaluation 接合面の `roles/role_diff_report.json` 新設
   - A-012：self-improvement と workflow-management の時系列契約・完了通知形式
   - A-013：信頼度ラベル 3 値を foundation 語彙体系に追加要請
   - A-014：evaluation との接合面の突き合わせ詳細
   - A-015：analysis との接合面の機械可読出力スキーマ
   - A-016：target_commit と self-improvement の materialization_commit_hash の整合ルール
2. **design.alignment**（LLM 自動判定）→ **design.approval**（利用者明示承認）
3. **章番号体系の整合確認**：他機能（foundation／runtime／evaluation／analysis／workflow-management）の design.md でも本セッション 27 と同様の章番号体系の不整合が存在する可能性があり、design.alignment 段で確認が必要（利用者明示承認「他機能でも生じていたはずなので後ほど対処」2026-05-26 セッション 27）

各機能の手順（運営ガイド §2.3）：drafting → triad-review → review-wave → alignment → approval

依存マップ順（計画書 §3.1 phase_order）：1〜5 完了（foundation／runtime／evaluation／analysis／workflow-management、drafting＋triad-review、セッション 25〜26）、**6 self-improvement（次着手）**、7 conformance-evaluation。完了 5 件の詳細コミットは git log 参照。

着手時の段階 2 スクリプト連動：design drafting に着手する際は `tools/check-workflow-action.py spec-set <feature> design drafting true --rationale "..."` を呼び、依存検査を通過してから Edit／Write を行う（規律 [[workflow-precheck-invocation]]）。

素材文書：`/Users/Daily/Development/Rwiki-v2-code-mod/dual-reviewer-rebuild/.kiro/specs/dual-reviewer-self-improvement/design.md`（self-improvement の素材）。

triad-review 段の 3 役配置（実験(エ)継続予定、本セッション 26 末で workflow-management triad-review に適用済み）：主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7（計画書 §5.9.1 改訂後既定整合）。配置変更が必要な場合はセッション 27 開始時に再確認。

計画書 §5.5 phase_order の補正課題（セッション 26 で A-001 として認識）：計画書 §5.5 行 376〜383 の phase_order 構造例には self-improvement が記載漏れで 6 機能のみ列挙されているが、§3.1／§5.16／A-007 案 2 に基づき本機能（workflow-management）の design では 7 機能（self-improvement 含む）を採用済み。計画書側の補正は本機能の責務範囲外で別途追跡が必要。

---





## 4. 直近の確定事項（2026-05-24 セッション 22〜23、2026-05-25 セッション 24〜26、2026-05-26 セッション 27）

利用者明示承認のあった項目を新しい順に記録：

- **conformance-evaluation／design 段完了（セッション 27 末、2026-05-26、依存マップ順 7/7、drafting＋triad-review、本セッション末コミット）**：triad-review 完了。design.md は 930 → 約 1150 行（20 章維持）。所見 28 件（主役 15＋敵対役独立 13）、must-fix 12 件を 10 グループに分けて深掘り議論し機能内対処 8 件＋遡及 1 件（A-001、12→6 criteria 軽量 reopen）＋波及 5 件（A-003／F-006／A-008／A-011／F-015）を反映。主要な対処：新規 Decision 9〜12（finding_id 発番／推定順序／信頼度 foundation 追加／規律対象範囲）、機械検査 MV-7（foundation 受入番号照合）追加、章番号体系の整合確認は alignment 段で持ち越し。利用者明示承認多数（「はい」×3／「候補 1」×7／「候補 2」×2／「候補 3」×1、2026-05-26 セッション 27）。**全 7 機能の design.drafting＋triad-review 完了**

- **conformance-evaluation／design.drafting 完了（セッション 27 末、2026-05-26、依存マップ順 7/7、本セッション末コミット）**：design.md 起草 930 行、全 20 章、Req 1〜8 全対応。計画書 §5.10（artifact-to-spec conformance evaluation、2026-05-24 セッション 23 改訂後）を実装可能な形に落とし込み、本筋（照合チェックモード）と傍流（文書生成モード、人協働）を明示的に分離、6 criteria（requirements 3 ＋ design 3）の検査構造を確定。主要な設計決定 8 件（本筋／傍流分離／二段階方式／feature-partitioning 例外／2 軸 6 criteria／3 役レビュー両段階適用／連想配列構造／モード切替明示／conformance ディレクトリ分離）。機能横断所見 A-005／A-008／A-009／A-010 はすべて要件段で対処済み。triad-review は次セッション 28 以降で実施予定。**全 7 機能の design.drafting 完了**。利用者明示承認「次へ」「はい」「はい」（2026-05-26 セッション 27）

- **self-improvement／design 段完了（セッション 27、2026-05-26、依存マップ順 6/7、コミット `dd8eba9`＋本セッション末コミット）**：design.drafting 起草 643 行＋ triad-review 完了で 942 行（17 章 → 20 章拡張）。3 役配置は実験(エ)。所見 32 件（主役 19＋敵対役独立 13）、must-fix 13 件を 8 グループに分けて深掘り議論し機能内対処 10 件＋遡及 1 件（A-001、requirements.md 軽量 reopen）＋波及 2 件（A-003／F-008、pending-cross-feature-findings.md に A-012 として追記）を反映。主要な対処：新章 §7 signal_extraction／§17 機械検査の具体手段（MV-1〜MV-4）／§18 テスト戦略を新設、§8.4 YAML スキーマに source_discipline_paths 等を追加、§9.3 パイロット運用閾値を 90% に確定、§13.5 workflow-management との時系列契約を詳細記述、§14 要件追跡表を受入基準単位に詳細化。利用者明示承認多数（「案 1」「OK」「承認」「案 2」「候補 1」×8／「候補 1、90%」「案 A」、2026-05-26 セッション 27）

- **複数案提示規律の統廃合＋事前検査宣言義務新設（セッション 27、2026-05-26）**：旧 dominant-dominated-options ／ choice-presentation（ともに参照層）を統合し `docs/disciplines/discipline_options_presentation.md` を新設（active 必読に昇格）。新規節として事前検査宣言義務（応答内で内部判定の (a) 候補総数 ／ (b) 3 規律適用結果 ／ (c) dominated 除外 ／ (d) 残合理案を明示宣言）を追加。効果測定ログ `docs/discipline-compliance-reports/options-precheck-log.md` を初版作成。旧 2 件は `docs/disciplines/archive/2026-05-26-consolidation/` へ退避。経緯：本セッション 27 で利用者から「規律が効いていない」と構造的欠陥を指摘され、active 必読昇格＋事前宣言義務の併設で対処。利用者明示承認「読み取りは正しい。軽量手続きでよい。効果を測る必要がある」「OK」（短縮版承認）「承認」（実装承認）

- **memory 側をシンボリックリンクに変更（セッション 26 末、コミット `9b9e827`）**：memory 配下の `feedback_*.md` 16 件を repo の `docs/disciplines/discipline_*.md` を指すシンボリックリンクに変更。auto memory 機構の起動時 load を維持しつつ、単一の正本（repo）と git 追跡の両立を実現。次セッション 27 開始時に検証予定（§1.5 検証手順）。検証失敗時の fallback：TODO §1 起動手順に「`docs/disciplines/` 16 件すべてを Read」を追加する案イに切り替え。利用者明示承認「試してみる」→「コミット」（2026-05-25 セッション 26）

- **規律 no-unilateral-action を撤去（セッション 26、コミット `b529c8e`、active 必読 12→11 件）**：規律作成自体の利用者明示承認が不在（旧 no-unilateral-approach-change／no-unilateral-session-ending はいずれも利用者の失態指摘から LLM が自律的に規律化）、規律が形骸化（直前応答で session 終結を提案しながら同規律を盾とする違反を実演）、不可逆操作の承認は [[approval-operation]] で重複カバー済み、を理由に完全削除。関連 3 規律ファイルから [[no-unilateral-action]] 参照を削除、MEMORY.md／README.md／design.md を更新。利用者指摘「無駄な規律」、利用者明示承認「案 ア」（2026-05-25 セッション 26）

- **規律ファイル軽量移送（セッション 26、コミット `b830785`、active 必読 12＋参照層 5＝17 件を memory → docs/disciplines/）**：計画書 §5.21（規律ファイルの ReviewCompass 方針への取り入れ手順）を前倒し実施。A-007（規律ファイル所有先パスと実体配置の不一致）の対処として、workflow-management 機能の所定手続きが効く配置に変更。フラット配置で命名規約 discipline_*.md に統一、front-matter 統一形式に正規化、内部リンク [[link-name]] の解決規則を README.md に明記。軽量手続き（明示承認＋文書化＋ archive 退避）で実施、本機能の所定手続きが整備されるまでの暫定運用。利用者明示承認「推奨セット（案 b＋案 X＋案 P＋案 1）」「案 ア（直ちに対応）」「推奨案（参照層 5 件追加移送）」（2026-05-25 セッション 26）

- **workflow-management／design 段完了（セッション 26 末、依存マップ順 5/7、コミット `881761d`＋`ffd8adc`）**：design.drafting＋triad-review 完了。design.md 806→884 行（+78 行）。3 役配置は実験(エ)。所見 31 件（主役 19＋敵対役独立発見 12）、must-fix 10 件を 7 グループに分けて深掘り議論し機能内対処 9 件を design.md に反映、遡及 1 件（A-007）は規律ファイル軽量移送として独立コミットで対処。レビュー記録 [.reviewcompass/specs/workflow-management/reviews/2026-05-25-design-triad-review.md](.reviewcompass/specs/workflow-management/reviews/2026-05-25-design-triad-review.md) 新設（212 行）。利用者明示承認（G1〜G8 各案＋「はい」最終仕上げ、2026-05-25 セッション 26）

- **analysis／design 段完了（セッション 25 末、依存マップ順 4/7、コミット `49aa7d8`＋`7b57072`）**：design.drafting＋triad-review 完了。design.md 659→776 行（+117 行）。3 役配置は実験(エ)。所見 27 件、must-fix 14 件を 3 セット 11 グループに分けて深掘り議論し機能内対処 9 件を design.md に反映。波及 1 件は A-011 として `pending-cross-feature-findings.md` に記録（design レビュー波段で `evaluation` 設計改訂と合わせて消化予定）。レビュー記録 [.reviewcompass/specs/analysis/reviews/2026-05-25-design-triad-review.md](.reviewcompass/specs/analysis/reviews/2026-05-25-design-triad-review.md) 新設（利用者明示承認多数、2026-05-25 セッション 25 末）

セッション 22〜24（2026-05-24〜2026-05-25 セッション 24 末）の確定事項は archive snapshot に退避：[docs/archive/todo/TODO_NEXT_SESSION-2026-05-25-snapshot.md](docs/archive/todo/TODO_NEXT_SESSION-2026-05-25-snapshot.md)（補助層 C 共存モデル完成、規律統廃合 20→11 件、全 7 機能 requirements approval 取得、conformance-evaluation 論点 A・B 対処、TODO 雛形新設、spec.json 7 機能配置、段名 local-review→triad-review 改名等、合計約 30 件）。

2026-05-21 までのさらに古い確定事項は別の snapshot を参照：[docs/archive/todo/TODO_NEXT_SESSION-2026-05-24-snapshot.md](docs/archive/todo/TODO_NEXT_SESSION-2026-05-24-snapshot.md)。

## 5. 関連参照とスクリプト

- 計画書：`docs/plan/reconstruction-plan-2026-05-21.md`
- 運営ガイド：`docs/operations/SESSION_WORKFLOW_GUIDE.md`
- spec.json 正本スキーマ：計画書 §5.24
- TODO 雛形：`templates/todo/TODO_NEXT_SESSION.template.md`
- spec.json 雛形：`templates/specs/spec.json.template`
- レビュー記録雛形：`templates/review/manual_dogfooding_review_template.md`
- 機能依存マップ：`stages/feature-dependency.yaml`（フェーズ 2 以降に配置予定）
- 持ち越し所見：`.reviewcompass/pending-cross-feature-findings.md`（A-011 が未消化、design レビュー波段で消化予定）
- 抽出進捗：`docs/extraction-mapping.md`
- **規律ファイル本体**（セッション 26 末で新設）：`docs/disciplines/`（active 必読 11 件＋参照層 5 件＝16 件＋README.md）。memory 側 `feedback_*.md` はシンボリックリンクで repo 本体を指す
- 規律ファイルディレクトリの解説：`docs/disciplines/README.md`（内部リンク `[[link-name]]` の解決規則と全 16 件のインデックス表）
- 過去スナップショット 2 件：
  - `docs/archive/todo/TODO_NEXT_SESSION-2026-05-24-snapshot.md`（2026-05-21 までの確定事項）
  - `docs/archive/todo/TODO_NEXT_SESSION-2026-05-25-snapshot.md`（2026-05-22〜2026-05-25 セッション 24 末の確定事項＋セッション 25 内の §3 完了項目と §4 補助エントリ）

自動記録スクリプト（セッション終了時）：

```
cd /Users/Daily/Development/ReviewCompass
python3 tools/session-log-converter.py --latest \
    ~/.claude/projects/-Users-Daily-Development-ReviewCompass \
    docs/sessions/session-22-2026-05-24.md
```
