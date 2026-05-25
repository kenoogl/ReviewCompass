# 次セッション継続用メモ

最終更新：2026-05-25（セッション 25 末、analysis／design 段の drafting＋triad-review 完了、依存マップ順 4/7。次は workflow-management／design.drafting から再開）
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

<!-- TEMPLATE_HEADER_END -->

---

## 1. 起動手順（セッション 26 開始時）

ReviewCompass の運営ガイドラインの必読フローに従う：

1. ターミナルで `cd /Users/Daily/Development/ReviewCompass`
2. 本 `TODO_NEXT_SESSION.md` を読む（§0 重要規律を必ず確認）
3. `docs/operations/SESSION_WORKFLOW_GUIDE.md` を読む（必読フロー・ワークフロー段の役割・サブエージェント方式の運用条件）
4. 計画書 `docs/plan/reconstruction-plan-2026-05-21.md` §5.4〜§5.8 を読む（ワークフロー手続き、reopen、session 跨ぎ、多層防御）
5. 計画書 §5.24 を読む（spec.json の正本スキーマ、2026-05-24 セッション 22 で新設）
6. 計画書 §5.12 を読む（人間代役機構、approval 段の actor=proxy_model 連動）
7. 計画書 §5.23 と §5.23.12 を読む（dogfooding と subagent_mediated 方式）
8. `.reviewcompass/pending-cross-feature-findings.md` を読む（持ち越し所見、現在 0 件未消化）
9. `docs/extraction-mapping.md` を読む（進行記録）
10. `git log --oneline -10`／`git status` で到達点確認

過去の経緯（セッション 19〜22 の詳細履歴、規律違反履歴、撤回履歴、過去の確定事項一覧等）は `docs/archive/todo/TODO_NEXT_SESSION-2026-05-24-snapshot.md` を参照。

## 2. ワークフロー上の現在位置（2026-05-25 セッション 25 末時点）

実態は **spec.json の workflow_state から確認**（§0.1 規律）：

- **intent 層**：drafting／review／approval すべて true（intent 文書 4 件は 2026-05-24 に素材リポからコピー配置済み、`intent/` 配下）
- **feature-partitioning 層**：candidate-proposal／approval すべて true（`stages/feature-partitioning/2026-05-24-proposal.md` 配置済み）
- **requirements 段**：全 7 機能で drafting／triad-review／review-wave／alignment／approval すべて true（2026-05-24 セッション 23 末で完了）
- **design 段**：
  - foundation（1/7）：drafting／triad-review が true、review-wave／alignment／approval は false（セッション 25）
  - runtime（2/7）：同上（セッション 25）
  - evaluation（3/7）：同上（セッション 25）
  - analysis（4/7）：drafting／triad-review が true、review-wave／alignment／approval は false（**本セッション 25 末**、コミット `7b57072`）
  - workflow-management（5/7）：すべて false（未着手）
  - self-improvement（6/7）：すべて false（未着手）
  - conformance-evaluation（7/7）：すべて false（未着手）
- **tasks／implementation 段**：すべて false

機能横断波及所見：A-001〜A-010 の 10 件は対処済み、**A-011 が未消化**（本セッション 25 末に analysis／design.triad-review で追記、`role_diff.json` 出典問題と `counter_status` 集計欠落の波及対処、design レビュー波段で消化予定）。詳細は `.reviewcompass/pending-cross-feature-findings.md` を参照。

## 3. 次の作業候補（優先順位順）

**現在の主要作業：B. 設計フェーズ継続（依存マップ順 5/7 workflow-management／design.drafting 着手、その後 6/7 self-improvement、7/7 conformance-evaluation。全 7 機能の design 段完了後に review-wave／alignment／approval へ）**


### B. 設計フェーズ継続（workflow-management／design.drafting 着手、その後 self-improvement／conformance-evaluation）

セッション 25 末時点で foundation／runtime／evaluation／analysis の 4 機能で design.drafting＋triad-review が完了。残り 3 機能：

1. **workflow-management（5/7）／design.drafting → triad-review**：次セッション開始時の主要作業
2. **self-improvement（6/7）／design.drafting → triad-review**：5/7 完了後
3. **conformance-evaluation（7/7）／design.drafting → triad-review**：6/7 完了後
4. **全 7 機能の design 段 review-wave**：3 機能の drafting＋triad-review 完了後に開始（A-011 を含む波及所見の集約消化）
5. **design.alignment**（LLM 自動判定）→ **design.approval**（利用者明示承認）

各機能の手順（運営ガイド §2.3）：drafting → triad-review → review-wave → alignment → approval

依存マップ順（計画書 §3.1 phase_order）：

1. ✅ foundation（drafting＋triad-review 完了、セッション 25）
2. ✅ runtime（drafting＋triad-review 完了、セッション 25）
3. ✅ evaluation（drafting＋triad-review 完了、セッション 25）
4. ✅ analysis（drafting＋triad-review 完了、セッション 25 末、コミット `7b57072`）
5. **workflow-management（次セッションの着手対象）**
6. self-improvement
7. conformance-evaluation

着手時の段階 2 スクリプト連動：design drafting に着手する際は `tools/check-workflow-action.py spec-set <feature> design drafting true --rationale "..."` を呼び、依存検査を通過してから Edit／Write を行う（規律 [[feedback_workflow_precheck_invocation]]）。

素材文書：`/Users/Daily/Development/Rwiki-v2-code-mod/dual-reviewer-rebuild/.kiro/specs/dual-reviewer-implementation-governance/design.md`（workflow-management の素材、機能名改称 implementation-governance → workflow-management）。

triad-review 段の 3 役配置（実験(エ)継続予定、本セッション 25 末で utilizationの一貫性を確認）：主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7（計画書 §5.9.1 改訂後既定整合）。配置変更が必要な場合はセッション 26 開始時に再確認。

---





## 4. 直近の確定事項（2026-05-24 セッション 22〜23、2026-05-25 セッション 24〜25）

利用者明示承認のあった項目を新しい順に記録：

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
