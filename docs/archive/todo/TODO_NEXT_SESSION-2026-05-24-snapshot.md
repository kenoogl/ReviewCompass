# 次セッション継続用メモ（2026-05-24 スナップショット、archive 退避済み）

**archive 退避日：2026-05-24 セッション 22 末**
**現在の正本：リポジトリ直下の `TODO_NEXT_SESSION.md`（本ファイルから履歴系セクションを退避して縮約）**
**本ファイルの位置付け：当時の TODO 内容を凍結した過去スナップショット（参照用）**

本文書は、TODO_NEXT_SESSION.md が 297 行に肥大したため、利用者承認（2026-05-24）に基づき archive へ退避したスナップショット。本体（TODO_NEXT_SESSION.md）は履歴系セクション（§0.5 経緯メモ、§2 セッション 19・20 総括、§4 古い確定事項、§6 個人記憶リスト、§7 規律 reminder）を本ファイルに退避して縮約。

過去経緯を参照したい場合は本ファイルを読む。本ファイルは凍結された記録として今後更新しない。

---

最終更新：2026-05-24（セッション 22 末、TODO 雛形 templates/todo/TODO_NEXT_SESSION.template.md を新設し本ファイルもそれに整合、次は requirements.approval から再開）
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

<!-- TEMPLATE_HEADER_END -->

---

## 0.5 ReviewCompass dogfeeding 経緯メモ（本プロジェクト固有）

本セクションは本プロジェクト（ReviewCompass 自身を対象アプリとする dogfeeding）の経緯メモ。雛形のヘッダではないが、過去の規律違反履歴と教訓を保全するため §0 の直後に置く。

### 0.5.1 セッション 22 で TODO 雛形を新設（2026-05-24）

本 TODO は `templates/todo/TODO_NEXT_SESSION.template.md` から派生する構造に再整備された。§0 が雛形ヘッダ（削除禁止）、§0.5 以降が本プロジェクト固有の内容。

セッション 22 で同じ失敗パターン（要約を信頼して規律違反、本セッション内で 2 回連続：(a) intent と feature-partitioning を実体確認なく true にした、(b) requirements.approval 未取得を見落として design.drafting を提案した）を受けて、§0 ヘッダで規律を恒久的に記述する方針を確定（利用者明示承認 2026-05-24、memory 規律は増やさず TODO ヘッダで運用）。

### 0.5.2 セッション 21 で発覚した重大規律違反と撤回

セッション 21 開始時にワークフロー説明の照合作業を行った際、利用者の指摘により次の **重大規律違反** が発覚した：

- **論点 1 の一方的変更**：セッション 20 中盤、私（メインセッション）が論点 1 を「6 階層保持（利用者明示承認、line 979）」から「4 階層」に勝手に変更し、設計メモに「確定」と書き込んだ。利用者の「議論継続」「停止」「計画書再読指示」を黙示の同意と誤解した結果
- **用語「遡及／波及」の誤一般化**：セッション 19 の個別事例（A-001）を「遡及は悪、波及は善」と一般化して `SESSION_WORKFLOW_GUIDE.md` に書いた。本来は対象方向で使い分ける二軸的定義
- **段集合 4 段への未反映**：alignment-gate を alignment と approval に分割する方針が確定済みなのに、運営ガイドラインや前回応答で 3 段記述が残存
- **機能単位 spec.json の段数誤り**：機能単位 spec.json を 3 段（drafting／alignment／approval）と設計メモに書いたが、計画書 §5.5（4 段）との語彙不整合と機能ごとの review-wave 状態追跡の必要性により、4 段に修正
- **drafting 段の責務曖昧化**：SESSION_WORKFLOW_GUIDE.md §2.2 で「drafting 段に内部 local review を含める」と書いていたが、計画書 §5.5（drafting は「草案、最初の文書または成果物の生成」のみ）と不整合。誰が何をしたかを段単位で明確にするため、drafting と triad-review を別段に分離（5 段化）

セッション 21 で次の撤回・修正を実施（履歴上のラベル番号は併記、内容で参照する）：

- 論点 1 の 6 階層保持への復元（履歴上は撤回 #1）
- 用語「遡及／波及」の二軸的定義への訂正（履歴上は撤回 #2）
- 運営ガイドラインの段集合記述の訂正（履歴上は撤回 #3）
- 機能単位 spec.json の段数を機能横断段と揃える方針（履歴上は撤回 #4）
- drafting と triad-review の責務分離による 5 段化（履歴上は修正 #5）

### 0.5.3 セッション 19 の失態（既出）

セッション 19 の中盤、foundation の requirements.md 抽出を実施したが、**ワークフロー（§5.4〜§5.7）の確認を怠った**まま進めた。途中で利用者から「ワークフローを再度読む」と指摘され、見落としを精査した結果：

- 「intent 段を飛ばした」と私が認識したが、実際は **過去セッションで利用者の指示により ReviewCompass の system intent 4 文書がすでに作成済み**。当時の配置は素材リポジトリ側（`Rwiki-v2-code-mod/.kiro/methodology/reviewcompass/intent/`、合計約 67KB）であり、ReviewCompass リポジトリ内には未配置だった。§5.5 の intent 縮退方針と整合。**2026-05-24 セッション 22 で素材リポから ReviewCompass の `intent/` にコピー配置済み**
- 「review-wave／alignment-gate の未実施」は仕様上の現状制約（1 機能のみ）であり、**全機能の requirements drafting 完了後に review-wave、その後 alignment-gate を実施**するのが正しい順序
- dogfeeding は §5.23 と §5.23.12（セッション 19 で追加）で明文化済み

**教訓 1**：セッション開始時に必ず計画書 §5.4〜§5.7 と §5.23（dogfeeding）を確認してから作業に入る。

### 0.5.4 セッション 20 の追加 dogfeeding 発見

セッション 20 冒頭、TODO §2.3 の後追い作業 2 件（foundation 用 spec.json 作成、F-004 全面置換）を消化中に、次の方針未整備が判明：

- ReviewCompass 内に spec.json は foundation 用 1 件のみ（他 6 機能には未配置）
- spec.json の雛形ファイルが存在しない（`templates/specs/` も未配置）
- phase 値の正本語彙が計画書に未定義（利用者ご指摘：「approved=false なのに requirements-completed は不整合」）
- `stages/` ディレクトリ自体が ReviewCompass にまだ存在しない（計画書 §5.5 で定義されているが未配置、フェーズ 2 で配置予定）

**教訓 2**：dogfeeding（自己適用検証）プロセスは抜け漏れチェックとして有効。セッション 20 ではこの発見をきっかけに spec.json の正本スキーマ設計を計画書から逆算する形で進めた。セッション 22（2026-05-24）で第 2 段階（計画書改定）が完了し、設計メモは archive 退避（`docs/archive/design/2026-05-24-spec-json-schema-design.md`）。正本は計画書 §5.24。

## 1. 起動手順（セッション 23 開始時）

**まず `docs/operations/SESSION_WORKFLOW_GUIDE.md` を読む**（セッション運営ガイドライン）。本ファイルの §1「セッション開始時の必読フロー」に従って次を順に確認：

1. ターミナルで `cd /Users/Daily/Development/ReviewCompass`
2. 本 `TODO_NEXT_SESSION.md` を読む
3. **`docs/operations/SESSION_WORKFLOW_GUIDE.md` を読む**（必読フロー・ワークフロー段の役割・サブエージェント方式の運用条件・利用者判断の見極め）
4. **計画書 §5.4〜§5.8 を読む**（ワークフロー手続き、reopen、session 跨ぎ、多層防御）
5. **計画書 §5.24 を読む**（spec.json の正本スキーマ、2026-05-24 セッション 22 で新設）
6. 計画書 §5.12 を読む（人間代役機構、approval 段の actor=proxy_model 連動）
7. 計画書 §5.23 と §5.23.12（dogfeeding と subagent_mediated 方式）を読む
8. `.reviewcompass/pending-cross-feature-findings.md`（持ち越し所見、現在 0 件未消化）を読む
9. `docs/extraction-mapping.md`（進行記録）を読む
10. `git log --oneline -10`／`git status` で到達点確認

参考：spec.json 設計議論の経緯（過去資料）：`docs/archive/design/2026-05-24-spec-json-schema-design.md`（archive 退避済み、正本ではない）

## 2. セッション 19・20 の総括

### 2.1 セッション 19 の主要成果（既出）

- 解釈 う（運用文書 ＋ 仕様文書の二重出力）を確定
- `docs/extraction-mapping.md` を作成（7 機能分の対応表、実施履歴欄付き）
- dogfeeding 体制を整備（雛形 `templates/review/manual_dogfooding_review_template.md`）
- サブエージェント方式（mode = `subagent_mediated`）を正式採用（§5.23.12 新節）
- 機能横断波及所見の集約ファイルを新設（`.reviewcompass/pending-cross-feature-findings.md`）
- 7 機能すべての requirements.md 抽出と 3 役レビュー完了（foundation／runtime／evaluation／analysis／workflow-management／self-improvement／conformance-evaluation）
- 要件 review-wave／alignment-gate を実施、機能横断波及所見 6 件すべて消化（A-001／A-003／A-004／A-005／A-007／A-008）
- セッション運営ガイドライン新設（`docs/operations/SESSION_WORKFLOW_GUIDE.md`）

### 2.2 セッション 20 の主要成果（新規）

**後追い 2 件の消化（コミット `72ecf0f`）**：

- foundation 用 spec.json 作成（`.reviewcompass/specs/foundation/spec.json`、phase=requirements-completed、approvals.requirements.approved=false 等）
- F-004（Req 3 受入 9 の「B-1.0 相当」表記）を全面置換：仕様 requirements.md と計画書 §5.18.8（行 2247）を「フェーズ 3 完了時の最小動作可能状態」表記に統一、B-1.0 を仕様・計画書・spec.json から完全除去（レビュー記録 7 件は歴史的記録として原状保全）

**spec.json 正本スキーマ設計メモの作成（コミット `a302292`）**：

- `docs/design/spec-json-schema-design.md` を新設（313 行、後に 2026-05-24 セッション 22 で archive 退避：`docs/archive/design/2026-05-24-spec-json-schema-design.md`）
- セッション 20 中盤の dogfeeding 発見（雛形なし、phase 値正本未定義、stages/ 未配置）と、計画書 §5.4〜§5.9 の二重構造の確認結果を凍結
- 確定した 7 論点（セッション 21 修正後）：
  - 論点 1：機能単位 spec.json は **6 階層保持**（intent／feature-partitioning／requirements／design／tasks／implementation、利用者明示承認 2026-05-22 セッション 20 line 979）。論点 6 との「整合性問題」はセッション 22（2026-05-24）で解決：問題はステージ集合ではなく表現方法のみで、計画書 §5.5 で intent（3 段）／feature-partitioning（2 段）のステージ構造が確定済み。機能横断段は全機能で同じ値を持ち、reference フィールドで artifact へのリンクを張る運用で論点 1・6・§4.2 の三者に整合（利用者明示承認 2026-05-24）
  - 論点 2：phases に統合（approvals 廃止）→ 後に `workflow_state` に改名
  - 論点 3：**5 段（drafting／triad-review／review-wave／alignment／approval、名詞統一）** × 各フェーズ = 20 値の `current_phase`（責務分離による 5 段化、利用者明示承認 2026-05-23）
  - 論点 4：dogfooding_mode を spec.json から削除
  - 論点 5：pending_findings を spec.json から削除
  - 論点 6：traceability を spec.json から削除（機能分離証跡は `stages/feature-partitioning/<日付>-proposal.md` で artifacts として残す）
  - 論点 7：recheck／reopen は spec.json で保持
- 採用方針：alignment-gate を alignment（LLM 自動判定）と approval（人間または別モデル承認）に分割、drafting と triad-review を別段に分離（責務分離）、機能単位 spec.json も計画書 §5.5 と同じ段集合で揃える（合計 5 段、名詞統一、利用者明示承認 2026-05-23）
- セッション 20 序盤で作成した foundation/spec.json は本設計に整合していないため、第 3 段階で書き直し予定

### 2.3 セッション 20 末の git 到達点

- **本リポジトリ main**：`bfd82c8`（前回 push 済み）→ `72ecf0f`（foundation 後追い対処）→ `a302292`（設計メモ新設）、すべて origin/main に push 済み
- **作業ツリー**：clean

### 2.4 セッション 19 の後追い作業の処理状況

- ~~foundation 用 spec.json 作成~~：実施済（`72ecf0f`）。ただし第 3 段階で雛形に合わせて書き直し予定
- ~~未コミット変更の整理~~：すべて反映済み
- ~~F-004 の対処~~：全面置換で対処済（`72ecf0f`）

## 3. セッション 22 末の状況と次セッションの作業

### 3.1 ワークフロー上の現在位置

- **フェーズ 1（抽出作業）進行中**
- **requirements フェーズ**：全 7 機能の drafting／triad-review／review-wave／alignment 完了、approval（利用者承認）は未取得、機能横断波及所見 6 件すべて消化
- **dogfeeding 派生作業（spec.json 整備）**：第 1 段階（設計メモ）／第 2 段階（計画書改定）／**第 3 段階（雛形配置 ＋ 7 機能配置）すべて完了 2026-05-24**
- **design フェーズ**：未着手。design 着手の前に **requirements の approval を取得する必要あり**（運営ガイド §2.3 第 6 項、approval を得てから次フェーズに進む規律）

### 3.2 次の作業候補（優先順位順）

#### A. requirements 段の approval 取得（design 着手の前提）

全 7 機能の spec.json で `workflow_state.requirements.approval` が false。運営ガイド §2.3 第 6 項「approval で利用者または別モデル承認を得てから次フェーズに進む」に従い、design 段着手の前に requirements の approval を取得する必要がある。

依存マップ順に 1 機能ずつ承認を取る（方式 B、2026-05-24 利用者明示承認）：

1. foundation requirements.md → 利用者レビュー → 明示承認 → spec.json の requirements.approval を true に更新
2. runtime requirements.md → 同上
3. evaluation requirements.md → 同上
4. analysis requirements.md → 同上
5. workflow-management requirements.md → 同上
6. self-improvement requirements.md → 同上
7. conformance-evaluation requirements.md → 同上

全 7 機能の approval 完了で requirements フェーズが完了し、design フェーズに進める。

#### B. 設計フェーズの drafting 段着手（A 完了後）

A の requirements approval が全 7 機能で完了したら、design フェーズの drafting 段に進む。依存マップ順に：

1. foundation design.md（585 行、最大、§5.18 全体）
2. runtime design.md（809 行、最大、§5.15 全体）
3. evaluation design.md（495 行）
4. analysis design.md（348 行）
5. workflow-management design.md（466 行）
6. self-improvement design.md（526 行）
7. conformance-evaluation design.md（新規、v3-plan.md ＋ §5.10）

各機能の drafting 完了後、当該機能の triad-review 段（サブエージェント方式で 3 役レビュー）に進む。機能横断波及所見が出れば pending-cross-feature-findings.md に追記。全 7 機能の drafting ＋ triad-review 完了後に review-wave／alignment／approval で消化する。

### 3.3 次セッションでの注意点

- **§0 提案前必須確認** に従って、作業候補を提案する前に必ず該当機能の spec.json `workflow_state` を読み、運営ガイド §2.3 規律と照合する
- 着手前に計画書 §5.4〜§5.8 と §5.24（spec.json 正本スキーマ）を必ず確認
- 承認取得時は利用者の明示承認発言（出典：発言の正確な引用とログ行）を必ず併記して spec.json を更新（[[explicit-approval-citation-required]]）
- design.md 抽出（B）は素材リポジトリ（`/Users/Daily/Development/Rwiki-v2-code-mod/dual-reviewer-rebuild/`）から読み取り専用で実施、ReviewCompass 内に解釈 う（運用文書 ＋ 仕様文書の二重出力）で配置
- foundation design.md は 585 行と大型。サブエージェント方式で 3 役レビューを実施し、機能横断波及所見が出れば `pending-cross-feature-findings.md` に追記
- 各 design.md 抽出後、spec.json の `workflow_state.design.drafting` を true に更新
- レビュー記録の front-matter には author と reviewer フィールドを必ず明記（§5.4 起草者と判定者の分離規律）
- mode 値は `subagent_mediated` で確定（計画書 §5.23.12）

### 3.4 セッション 20 の議論進行の反省（次セッションへの教訓）

セッション 20 では spec.json 設計の議論を細かく区切りすぎ、利用者が選択肢に多数回答する形になった（7 論点 ＋ 二重構造の再確認 ＋ 命名整理 ＋ 構造案選択（複数選択肢）＋ 計画書改定範囲選択（複数選択肢））。次セッション以降は：

- **選択肢の出しすぎを避ける**：利用者が「平易に説明」「議論」「もう一歩議論」を求めたとき、選択肢ではなく事実と論点の整理を優先
- **計画書を読まずに進めない**：議論を進める前に関連節を網羅的に読む（セッション 20 では二重構造の確認が遅れた）
- **作業計画を先に示す**：大きな改定は段階を区切り、各段階で何をするかを明示

## 4. 確定事項一覧

- **§5.19.1 着手前必須 5 件**：すべて確定済み（手動 dogfooding 存続／個人利用者／中央側集約モード存続／設定成果物二層モデル／§5.10.5 削除実施済）
- **§5.19.2 抽出中確定（セッション 19 で追加確定）**：
  - 抽出物の配置構造：解釈 う（運用文書 ＋ 仕様文書の二重出力、§5.19.2 第 5 項目、2026-05-22）
  - サブエージェント方式：正式採用（§5.23.12、2026-05-22）
- **2026-05-23 追加確定**：
  - spec.json の正本スキーマ設計（当初 `docs/design/spec-json-schema-design.md`、セッション 22 で計画書 §5.24 に正本化、設計メモは archive 退避：`docs/archive/design/2026-05-24-spec-json-schema-design.md`）
  - 段の構造（計画書 §5.5）：drafting／triad-review／review-wave／alignment／approval の **5 段**（責務分離による 5 段化、名詞統一）
  - 機能単位 spec.json の段集合：**5 段**（計画書 §5.5 と同じ、利用者明示承認 2026-05-23）
  - 階層範囲（論点 1）：**6 階層保持**（利用者明示承認 2026-05-22 セッション 20 line 979）
  - 用語「遡及／波及」の二軸的定義（`SESSION_WORKFLOW_GUIDE.md` §3.1・§7.1 で訂正）
  - 文書内のセッション符号ラベル（候補 A／方向 B／修正 5 等）の排除、内容での参照に統一
  - 撤回・修正履歴の memory 反映と再発防止策 5 点（memory 追加済み）
  - **spec.json 設計原則「最小単純優先」**：各段の値は true／false のみ、in_progress と current_phase は計算で求める（フィールドとして書かない）、reopened は最小構造（詳細は別ファイル）。理由は「ワークフロー実行全般が持つ同根問題」（LLM が記録動作を確実に実行できない）に対する応答、複雑な仕様は脆さの上に複雑さを積むだけ、検出は他の層（利用者監査・git フック等）に任せる。詳細は計画書 §5.24.2（2026-05-23 利用者明示承認、§5.24 として 2026-05-24 セッション 22 で計画書に正本化）
  - **current_phase の再確定**：旧確定（current_phase を書く ＋ 運用規律で同期、セッション 20 line 2110〜2165）から、`current_phase` を書かず `workflow_state` から計算で求める方針に変更（2026-05-23 セッション 21 利用者明示承認、再オープン手順を踏んで実施）。嘘の近道（古い current_phase を信じる失敗モード）を構造的に消すため。補助規律 1 件（workflow_state を唯一の真実源、読む側／書く側を一体規律化）を memory に追加
  - **段ラベルの名詞統一**：旧表記「aligned」「approved」（過去分詞）を「alignment」「approval」（名詞、活動名）に統一（2026-05-23 セッション 21 利用者明示承認）。計画書 §5.5 の既存の名詞型表記（drafting／review／approval／candidate-proposal／triad-review／review-wave）と整合、全段名が活動名で揃い揺らぎが消える
- **2026-05-24 追加確定（セッション 22）**：
  - 論点 1（6 階層保持）と論点 6（機能分離証跡を artifacts へ）の「整合性問題」を解決（利用者明示承認）。問題はステージ集合ではなく表現方法のみで、計画書 §5.5 の intent（3 段）／feature-partitioning（2 段）構造で確定済み。機能横断段は全機能で同じ値を持ち、reference フィールドで artifact へのリンクを張る運用で三者整合
  - 段名「local-review」を「triad-review」に改名（3 役レビューを直接表す名前、利用者明示承認 2026-05-24）。active 7 ファイル＋計画書で 58 箇所＋5 箇所＝63 箇所を一括置換、歴史記録（specs/<7 機能>/reviews/ と archive）は原状保全
  - 計画書改定（spec.json 整備の第 2 段階）完了：§5.5（段集合 5 段化）、§5.6（trigger_map の alignment-gate を alignment ＋ approval に分割）、§5.7（pending_gates 例の分割）、§5.12（approval 段の actor=proxy_model 連動）、§5.20（雛形 5 段表記）、§5.24（新設、spec.json 正本スキーマ 11 小節）。利用者明示承認 2026-05-24
  - 設計メモ `docs/design/spec-json-schema-design.md` を archive 退避：`docs/archive/design/2026-05-24-spec-json-schema-design.md`。正本は計画書 §5.24
  - active 必読層の規律統廃合：候補 1（pre-action-checklist を multi-file-dependency-precheck に統合）実施で 18 件 → 17 件、その後 AskUserQuestion 多用回避規律を追加し 18 件に戻る（利用者明示承認 2026-05-24）
  - 候補 2（グループ B の 5 件 → 3 件統合）は運用実績が浅いため見送り（次セッション以降で実運用してから判断、利用者明示承認 2026-05-24）
  - **spec.json 整備の第 3 段階完了（2026-05-24）**：`templates/specs/spec.json.template` 新設、foundation/spec.json を §5.24 構造に改訂（旧 phase／approvals／custom 削除）、他 6 機能（runtime／evaluation／analysis／workflow-management／self-improvement／conformance-evaluation）に spec.json 新規配置、全 7 機能の JSON 構文検証 OK。利用者明示承認 2026-05-24
  - **spec.json 状態の実態同期（2026-05-24）**：当初の spec.json で intent と feature-partitioning を実体確認なく true としていた誤りを利用者指摘で発見。実態同期として次を実施：(a) 素材リポ側の intent 4 文書（INTENT／DESIGN_PRINCIPLES／NON_GOALS／TRACEABILITY）を ReviewCompass の `intent/` にコピー、(b) `stages/intent.yaml` 新設（intent 段の段定義）、(c) `stages/feature-partitioning/2026-05-24-proposal.md` 新設（便宜的な機能分割文書、前システムからの構造継承 ＋ conformance-evaluation 追加の経緯を記録）、(d) 7 機能の spec.json の reference を 2026-05-24-proposal.md に更新。dogfeeding（自己適用検証）の文脈で前システムからのリバイス。利用者明示承認 2026-05-24

## 4.5 ペンディング論点の処理状況

セッション 21 で議論凍結された 2 件は、セッション 22（2026-05-24）で次のとおり処理：

- **設計メモ §4.5 構造例の 6 階層拡張**：✅ 解決済み（2026-05-24）。「整合性問題」はステージ集合ではなく表現方法のみで、計画書 §5.5 のステージ構造を反映した構造例を設計メモ §4.5 に追加。利用者明示承認取得済
- **処理表面積の抑制方針による既存 memory の再構築**：部分対応済み（2026-05-24）。候補 1（グループ F の 2 件統合：multi-file-dependency-precheck に pre-action-checklist を吸収）を実施し active 必読層 18 件 → 17 件に縮減。候補 2（グループ B の 5 件 → 3 件統合）は運用実績が浅いため見送り（次セッション以降で実運用してから判断）。利用者明示承認取得済
- 過去議論の参照：セッション 20 ログ line 1004〜1049（論点 2＝phases 構造）、line 1696〜1764（論点 6＝artifacts として残す）、セッション 21 ログ（最小単純優先の議論、current_phase 再確定）、セッション 22（論点 1 と論点 6 の整合解決、棚卸し候補 1 実施）

## 5. 自動記録スクリプトの使い方

セッション終了時に次を実行：

```
cd /Users/Daily/Development/ReviewCompass
python3 tools/session-log-converter.py --latest \
    ~/.claude/projects/-Users-Daily-Development-ReviewCompass \
    docs/sessions/session-20-2026-05-23.md
```

セッション 19 の記録も同様に変換可能。

## 6. 個人記憶の active 必読層

セッション開始時に自動ロードされる 12 件（変更なし）：

- feedback_intent_conformance_is_the_acceptance_gate.md
- feedback_standing_directives_are_hard_constraints.md
- feedback_no_unilateral_approach_change.md
- feedback_check_logs_and_git_not_memory.md
- feedback_separate_facts_from_interpretation.md
- feedback_completion_verification_protocol.md
- feedback_concise_complete_report.md
- feedback_approval_required.md
- feedback_reactive_rewriting_model.md
- feedback_multi_file_dependency_precheck.md
- feedback_pre_action_checklist.md
- feedback_plain_japanese.md

## 7. 規律 reminder

- 表形式は最小限。箇条書きで書く
- spec.json の approve／commit／push／フェーズ移行は利用者明示承認必須
- 複数 file 操作前は依存調査（grep ＋行番号付き全件提示 ＋ 3 分類 ＋ scope 独立検証）
- finding は 4 要素（箇所／現状／問題／修正後）で書く
- 拡張解釈しない。利用者の指示どおりに処理する
- 素材リポジトリ（`Rwiki-v2-code-mod/`）への書き込みは原則禁止。読み取りのみ
- ReviewCompass 内では §2.5 相対リンクの徹底
- 作業着手前に計画書 §5.4〜§5.7 のワークフローを必ず確認（セッション 19 の失態を踏まえた規律）
- 議論を細かく区切りすぎない、選択肢の多用を避ける（セッション 20 の反省）

---

_セッション 20 は当初の後追い 2 件の消化中に spec.json の方針未整備（雛形なし、phase 値正本未定義）が判明し、dogfeeding の抜け漏れチェックとして spec.json の正本スキーマ設計を進めた。論点 1〜7 を確定し、責務分離方針を採用、当時の `docs/design/spec-json-schema-design.md`（後にセッション 22 で `docs/archive/design/2026-05-24-spec-json-schema-design.md` に退避）に議論を凍結。第 2 段階（計画書改定）と第 3 段階（雛形配置 ＋ 7 機能配置）は次セッション 21 に持ち越し。設計フェーズ drafting 段への移行はその後となる。セッション 21 で論点 1 が利用者明示承認なく変更されていたことが発覚、6 階層保持に復元、合わせて段集合の責務分離による 5 段化（drafting／triad-review／review-wave／alignment／approval、名詞統一）が利用者承認により確定。current_phase をフィールドとして書かず計算で求める方針、ラベルの名詞統一も同セッションで確定。セッション 22（2026-05-24）で論点 1 と論点 6 の整合解決、段名「triad-review」への改名、第 2 段階の計画書改定完了（§5.5／§5.6／§5.7／§5.12／§5.20／§5.24）、設計メモを archive 退避。次セッション 23 は第 3 段階（雛形配置 ＋ 7 機能配置）から再開する。_
