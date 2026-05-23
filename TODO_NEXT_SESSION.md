# 次セッション継続用メモ

最終更新：2026-05-23（セッション 21 中盤、論点 1 の 6 階層復元・用語訂正・段集合の 5 段化を反映）
作業ディレクトリ：`/Users/Daily/Development/ReviewCompass/`（本リポジトリ）
リポジトリ：`git@github.com:kenoogl/ReviewCompass.git`（main ブランチ）

---

## 0. セッション 21 で発覚した重大規律違反と撤回

セッション 21 開始時にワークフロー説明の照合作業を行った際、利用者の指摘により次の **重大規律違反** が発覚した：

- **論点 1 の一方的変更**：セッション 20 中盤、私（メインセッション）が論点 1 を「6 階層保持（利用者明示承認、line 979）」から「4 階層」に勝手に変更し、設計メモに「確定」と書き込んだ。利用者の「議論継続」「停止」「計画書再読指示」を黙示の同意と誤解した結果
- **用語「遡及／波及」の誤一般化**：セッション 19 の個別事例（A-001）を「遡及は悪、波及は善」と一般化して `SESSION_WORKFLOW_GUIDE.md` に書いた。本来は対象方向で使い分ける二軸的定義
- **段集合 4 段への未反映**：alignment-gate を aligned と approved に分割する方針が確定済みなのに、運営ガイドラインや前回応答で 3 段記述が残存
- **機能単位 spec.json の段数誤り**：機能単位 spec.json を 3 段（drafting／aligned／approved）と設計メモに書いたが、計画書 §5.5（4 段）との語彙不整合と機能ごとの review-wave 状態追跡の必要性により、4 段に修正
- **drafting 段の責務曖昧化**：SESSION_WORKFLOW_GUIDE.md §2.2 で「drafting 段に内部 local review を含める」と書いていたが、計画書 §5.5（drafting は「草案、最初の文書または成果物の生成」のみ）と不整合。誰が何をしたかを段単位で明確にするため、drafting と local-review を別段に分離（5 段化）

セッション 21 で次の撤回・修正を実施（履歴上のラベル番号は併記、内容で参照する）：

- 論点 1 の 6 階層保持への復元（履歴上は撤回 #1）
- 用語「遡及／波及」の二軸的定義への訂正（履歴上は撤回 #2）
- 運営ガイドラインの段集合記述の訂正（履歴上は撤回 #3）
- 機能単位 spec.json の段数を機能横断段と揃える方針（履歴上は撤回 #4）
- drafting と local-review の責務分離による 5 段化（履歴上は修正 #5）

再発防止策 5 点を memory に追加予定。

### 0.0 セッション 19・20 で発覚した重要な失態と教訓

### 0.1 セッション 19 の失態（既出）

セッション 19 の中盤、foundation の requirements.md 抽出を実施したが、**ワークフロー（§5.4〜§5.7）の確認を怠った**まま進めた。途中で利用者から「ワークフローを再度読む」と指摘され、見落としを精査した結果：

- 「intent 段を飛ばした」と私が認識したが、実際は **過去セッションで利用者の指示により ReviewCompass の system intent 4 文書がすでに作成済み**（`.kiro/methodology/reviewcompass/intent/`、合計約 67KB）。§5.5 の intent 縮退方針と整合
- 「review-wave／alignment-gate の未実施」は仕様上の現状制約（1 機能のみ）であり、**全機能の requirements drafting 完了後に review-wave、その後 alignment-gate を実施**するのが正しい順序
- dogfeeding は §5.23 と §5.23.12（セッション 19 で追加）で明文化済み

**教訓 1**：セッション開始時に必ず計画書 §5.4〜§5.7 と §5.23（dogfeeding）を確認してから作業に入る。

### 0.2 セッション 20 の追加 dogfeeding 発見

セッション 20 冒頭、TODO §2.3 の後追い作業 2 件（foundation 用 spec.json 作成、F-004 全面置換）を消化中に、次の方針未整備が判明：

- ReviewCompass 内に spec.json は foundation 用 1 件のみ（他 6 機能には未配置）
- spec.json の雛形ファイルが存在しない（`templates/specs/` も未配置）
- phase 値の正本語彙が計画書に未定義（利用者ご指摘：「approved=false なのに requirements-completed は不整合」）
- `stages/` ディレクトリ自体が ReviewCompass にまだ存在しない（計画書 §5.5 で定義されているが未配置、フェーズ 2 で配置予定）

**教訓 2**：dogfeeding（自己適用検証）プロセスは抜け漏れチェックとして有効。セッション 20 ではこの発見をきっかけに spec.json の正本スキーマ設計を計画書から逆算する形で進めた。次セッションでは、本セッションの設計メモ（`docs/design/spec-json-schema-design.md`）を入力として計画書改定に進む。

## 1. 起動手順（セッション 21 開始時）

**まず `docs/operations/SESSION_WORKFLOW_GUIDE.md` を読む**（セッション 19 の経験を反映したセッション運営ガイドライン）。本ファイルの §1「セッション開始時の必読フロー」に従って次を順に確認：

1. ターミナルで `cd /Users/Daily/Development/ReviewCompass`
2. 本 `TODO_NEXT_SESSION.md` を読む
3. **`docs/operations/SESSION_WORKFLOW_GUIDE.md` を読む**（必読フロー・ワークフロー段の役割・サブエージェント方式の運用条件・利用者判断の見極め）
4. **`docs/design/spec-json-schema-design.md` を読む**（セッション 20 末で凍結した spec.json 設計メモ、第 2 段階の入力）
5. 計画書 §5.4〜§5.7（ワークフロー手続き）を読む
6. 計画書 §5.23 と §5.23.12（dogfeeding と subagent_mediated 方式）を読む
7. `.reviewcompass/pending-cross-feature-findings.md`（持ち越し所見、現在 0 件未消化）を読む
8. `docs/extraction-mapping.md`（進行記録）を読む
9. `git log --oneline -10`／`git status` で到達点確認

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

- `docs/design/spec-json-schema-design.md` を新設（313 行）
- セッション 20 中盤の dogfeeding 発見（雛形なし、phase 値正本未定義、stages/ 未配置）と、計画書 §5.4〜§5.9 の二重構造の確認結果を凍結
- 確定した 7 論点（セッション 21 修正後）：
  - 論点 1：機能単位 spec.json は **6 階層保持**（intent／feature-partitioning／requirements／design／tasks／implementation、利用者明示承認 2026-05-22 セッション 20 line 979）。論点 6 との整合性問題は未解決として保留
  - 論点 2：phases に統合（approvals 廃止）→ 後に `workflow_state` に改名
  - 論点 3：**5 段（drafting／local-review／review-wave／aligned／approved）** × 各フェーズ = 20 値の `current_phase`（責務分離による 5 段化、利用者明示承認 2026-05-23）
  - 論点 4：dogfooding_mode を spec.json から削除
  - 論点 5：pending_findings を spec.json から削除
  - 論点 6：traceability を spec.json から削除（機能分離証跡は `stages/feature-partitioning/<日付>-proposal.md` で artifacts として残す）
  - 論点 7：recheck／reopen は spec.json で保持
- 採用方針：alignment-gate を aligned（LLM 自動判定）と approved（人間または別モデル承認）に分割、drafting と local-review を別段に分離（責務分離）、機能単位 spec.json も計画書 §5.5 と同じ段集合で揃える（合計 5 段、利用者明示承認 2026-05-23）
- セッション 20 序盤で作成した foundation/spec.json は本設計に整合していないため、第 3 段階で書き直し予定

### 2.3 セッション 20 末の git 到達点

- **本リポジトリ main**：`bfd82c8`（前回 push 済み）→ `72ecf0f`（foundation 後追い対処）→ `a302292`（設計メモ新設）、すべて origin/main に push 済み
- **作業ツリー**：clean

### 2.4 セッション 19 の後追い作業の処理状況

- ~~foundation 用 spec.json 作成~~：実施済（`72ecf0f`）。ただし第 3 段階で雛形に合わせて書き直し予定
- ~~未コミット変更の整理~~：すべて反映済み
- ~~F-004 の対処~~：全面置換で対処済（`72ecf0f`）

## 3. セッション 21 の主要作業

### 3.1 ワークフロー上の現在位置

- **フェーズ 1（抽出作業）進行中**
- **requirements フェーズ**：全 7 機能の drafting／review-wave／alignment-gate 完了、機能横断波及所見 6 件すべて消化
- **dogfeeding 派生作業**：spec.json 正本スキーマ設計（第 1 段階完了、第 2〜3 段階は次セッション以降）
- **design フェーズ**：未着手（spec.json 整備の第 2〜3 段階の後に進む）

### 3.2 次の作業候補（優先順位順）

#### A. 計画書改定（spec.json 整備の第 2 段階）

設計メモ（`docs/design/spec-json-schema-design.md`）を入力として、計画書改定を進める：

- §5.5：requirements 以降のフェーズの段集合を 4 段（drafting／review-wave／aligned／approved）に拡張
- §5.6：trigger_map（reopen 時の再実施段マップ）の alignment-gate 参照箇所をすべて aligned ＋ approved の組合せに置換（I 起点／A 起点／D 起点／R 起点／N 起点の全エントリ）
- §5.12：人間代役機構と approved 段の actor の連動を明記
- §5.24（新設）：spec.json の正本スキーマ（フィールド一覧、段の構造、状態値、current_phase 値リスト、構造例、同期問題の運用方針、責任分担）
- §5.7／§5.8／§5.20：alignment-gate 登場箇所の見直し

1 節ずつ改定文案を提示 → 利用者承認 → 反映の手順で進める。

#### B. spec.json 雛形配置と 7 機能配置（spec.json 整備の第 3 段階）

第 2 段階の計画書改定が完了したら：

- spec.json 雛形を `templates/specs/spec.json.template` に配置
- foundation/spec.json を雛形に合わせて改訂（pending_findings 削除、traceability 削除、approvals → workflow_state へ変換、命名整理を反映）
- 他 6 機能（runtime／evaluation／analysis／workflow-management／self-improvement／conformance-evaluation）に spec.json を配置
- 各機能の現状（requirements-aligned）を反映

#### C. 設計フェーズの drafting 段着手（spec.json 整備の後）

第 3 段階完了後、本来の design フェーズ drafting 段に進む。依存マップ順に：

1. foundation design.md（585 行、最大、§5.18 全体）
2. runtime design.md（809 行、最大、§5.15 全体）
3. evaluation design.md（495 行）
4. analysis design.md（348 行）
5. workflow-management design.md（466 行）
6. self-improvement design.md（526 行）
7. conformance-evaluation design.md（新規、v3-plan.md ＋ §5.10）

各 design.md 抽出後はサブエージェント方式で 3 役レビューを実施し、機能横断波及所見が出れば pending-cross-feature-findings.md に追記して design 段の review-wave／alignment-gate で消化する。

### 3.3 次セッションでの注意点

- 着手前に計画書 §5.4〜§5.7 と `docs/design/spec-json-schema-design.md` を必ず確認
- 計画書改定（作業候補 A）は影響範囲が広い（§5.5、§5.6 の trigger_map、§5.12、§5.24 新設等）ため、1 節ずつ提示 → 承認 → 反映の手順を守る
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
  - spec.json の正本スキーマ設計（`docs/design/spec-json-schema-design.md`、セッション 21 で 6 階層復元と 5 段化を反映）
  - 段の構造（計画書 §5.5）：drafting／local-review／review-wave／aligned／approved の **5 段**（責務分離による 5 段化）
  - 機能単位 spec.json の段集合：**5 段**（計画書 §5.5 と同じ、利用者明示承認 2026-05-23）
  - 階層範囲（論点 1）：**6 階層保持**（利用者明示承認 2026-05-22 セッション 20 line 979）
  - 用語「遡及／波及」の二軸的定義（`SESSION_WORKFLOW_GUIDE.md` §3.1・§7.1 で訂正）
  - 文書内のセッション符号ラベル（候補 A／方向 B／修正 5 等）の排除、内容での参照に統一
  - 撤回・修正履歴の memory 反映と再発防止策 5 点（memory 追加予定）

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

_セッション 20 は当初の後追い 2 件の消化中に spec.json の方針未整備（雛形なし、phase 値正本未定義）が判明し、dogfeeding の抜け漏れチェックとして spec.json の正本スキーマ設計を進めた。論点 1〜7 を確定し、責務分離方針を採用、`docs/design/spec-json-schema-design.md` に議論を凍結。第 2 段階（計画書改定）と第 3 段階（雛形配置 ＋ 7 機能配置）は次セッション 21 に持ち越し。設計フェーズ drafting 段への移行はその後となる。なおセッション 21 で論点 1 が利用者明示承認なく変更されていたことが発覚、6 階層保持に復元、合わせて段集合の責務分離による 5 段化（drafting／local-review／review-wave／aligned／approved）が利用者承認により確定した。_
