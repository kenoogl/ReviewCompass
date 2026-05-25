# TODO_NEXT_SESSION スナップショット（2026-05-25 セッション 25 末時点で退避）

本ファイルは `TODO_NEXT_SESSION.md` の §4「直近の確定事項」が肥大化したため、セッション 22〜24 の長文エントリを退避した記録である。

退避日：2026-05-25（セッション 25 末、利用者明示承認「(ア)＋(イ)」に基づく縮約）
退避元：`TODO_NEXT_SESSION.md` §4「直近の確定事項」
退避対象：2026-05-22〜2026-05-25 セッション 24 末まで（セッション 25 の確定事項は本体に残す）

旧スナップショット：[TODO_NEXT_SESSION-2026-05-24-snapshot.md](TODO_NEXT_SESSION-2026-05-24-snapshot.md)（2026-05-21 までの内容）

---

## 退避エントリ一覧（新しい順）

### セッション 24（2026-05-25 セッション 24 末）

- **memory リンク是正と段階 3 フック実運用観察（セッション 24 末）**：規律 4「workflow precheck を必ず呼ぶ」に段階 1／段階 3 の責務分担を追記、規律 5「承認の運用」に「機械検査は承認の代替ではない」を追記。派生対処として旧リンク 8 か所（旧 reactive 規律言及、統廃合前の規律名）を新規律名に修正。段階 3 フックの実運用観察で、本セッション内のフックが期待外に自動発動していたことを発見（ログ `docs/logs/workflow-precheck.log` に 8 件の `[stage-3 hook auto-invocation]` エントリ、すべて verdict=OK）。`docs/notes/2026-05-25-memory-link-fixes-and-stage-3-observation.md` 新設で詳細記録（利用者明示承認「ア」（推奨セット a=(あ)／b=(あ)／c=(い)／d=(あ)）、2026-05-25 セッション 24）
- **セッション 24 メンテナンス（振り返りメモと README 群、セッション 24 末）**：(a) docs/notes/2026-05-25-session-24-retrospective.md 新設（規律違反履歴・全 16 コミットの時系列・学んだこと）、(b) memory archive ディレクトリの README（リポジトリ外）、(c) .claude/hooks/README.md 新設、(d) TODO §3 整理（B 主要作業強調、A 完了マーク、A／C／D 完了反映）、(e) docs/notes/README.md 新設（インデックス・命名規則・主題グルーピング）。コミット `f3b6918`（利用者明示承認「イ」「a-e を順次」「ア」、2026-05-25 セッション 24）
- **段階 3 フック導入と補助層 C 完成（セッション 24、前倒し実施）**：補助層 C 共存モデルの段階 3（Claude Code フック機構）を前倒しで導入完了。[.claude/hooks/pre-bash-precheck.sh](.claude/hooks/pre-bash-precheck.sh)（bash + jq、73 行）が Bash の git commit／push を PreToolUse hook で検出し、段階 2 スクリプトを `--rationale "[stage-3 hook auto-invocation] ..."` 付きで自動発動、exit 2（DEVIATION）のときに `permissionDecision = "deny"` を返す。.claude/settings.json に PreToolUse 登録、tests.hooks.* と discover の許可ルールも追加。TDD 第 1 ラウンド（テスト 7 件先行、コミット `2520bef`）と第 2 ラウンド（実装、全 32 テスト通過、コミット `9456085`）の 2 段階。フック手動実行で 4 シナリオ確認、本セッション内のフック自動発動は Claude Code の設定再読み込みタイミングに依存。これにより補助層 C 共存モデルの 3 段階すべて完成（利用者明示承認「イは前倒しだが、取り組む」「ア」推奨セット採用「ア」コミット承認 ×2、2026-05-25 セッション 24）
- **計画書整合確認（§5.12.8／§5.13.8／§5.16、セッション 24）**：補助層 C 新設に伴い、§5.12.8 と §5.13.8 の「新しい補助層」「補助層」抽象表記を補助層 A・B・C 体系に明示化、§5.16 第 2 サイクルの「補助層の基本実装」を「補助層 A・B の基本実装」に明示化。実質方針変更でなく表記統一。コミット `c57b837`。段階 2 スクリプトの commit 検査で要注意変更（docs/plan/ 配下）警告を初観察、再承認で続行（利用者明示承認「ア」修正案 A・B・C 一括「ア」WARN 後の続行、2026-05-25 セッション 24）
- **規律統廃合効果測定（48.7% 削減を実測、セッション 24）**：[docs/notes/2026-05-25-discipline-consolidation-effect-measurement.md](docs/notes/2026-05-25-discipline-consolidation-effect-measurement.md) 新設。旧 20 件と新 11 件の active 必読層を静的測定し、ファイル数 45.0% 減、行数 41.6% 減、バイト数 48.7% 減、推定トークン数 48.7% 減を確認。目的 β（削減効果の数値化）に対応。コミット `e99d4e7`（利用者明示承認「キについて」議論着手「推奨案で。このメモを記録しておく」「ア」コミット承認、2026-05-25 セッション 24）
- **規律統廃合（active 必読 20 件 → 11 件、セッション 24）**：5 統合（承認の運用／事実と解釈の分離／事前検査チェックリスト／workflow_state 真実源 ＋ session 引継ぎ／勝手に走らない（approach／session 含む））、1 撤去（reactive 書き直し）、1 TODO 移動（AskUserQuestion を多用しない → TODO §0.4）。memory 直下の旧 14 ファイルは `archive/2026-05-25-consolidation/` に退避。TODO §0.4 を雛形にも反映。テスト 25 件すべて引き続き通過。コミット `c719651`／push `12aa862..c719651`（利用者明示承認「アでよいが、AskUserQuestion を多用しないについては、TODOの冒頭に移すと規律が減る」「ア」2026-05-25 セッション 24）
- **段階 1 規律化と初運用成功（補助層 C、セッション 24）**：memory `feedback_workflow_precheck_invocation.md` 新設（active 必読層に追加）、不可逆操作（spec.json 変更／git commit／git push）の直前に `tools/check-workflow-action.py` を呼び verdict と reasons を応答に明示する規律を確立。初運用で push 直前検査を実施、OK 判定後に push 成功（`a6c8f0c..12aa862`）。CLAUDE.md または規律ファイルへの追加は memory 配置で実現、論点 a＝memory／b＝即時／c＝すべての commit／push に適用 を承認（利用者明示承認「ア」起草案そのままで承認、2026-05-25 セッション 24）
- **段階 2 小規模運用実測完了（補助層 C、セッション 24）**：spec-set／commit／push の 3 サブコマンドで 14 シナリオ実行、すべて想定どおりの判定（OK／WARN／DEVIATION）。発見した 2 件の小さな問題（真偽値の大文字表記、ログファイルの .gitignore 未追加）を是正、コミット `662bffb`。仕様 [docs/operations/WORKFLOW_PRECHECK.md](../../docs/operations/WORKFLOW_PRECHECK.md) §13 に実測結果を併記（コミット `12aa862`、§13.1〜§13.6 で範囲・シナリオ表・仕様準拠確認・是正・観察事項・結論を記録）。push 済（`8b33e74..2f1b59a` ＋ `2f1b59a..a6c8f0c` ＋ `a6c8f0c..12aa862`）（利用者明示承認「範囲案 2」「論点 A は実装テスト段階でも効果測定やデバッグで必要になるのではないか？」「論点 B は渡す」「論点 C は別文書」「ア」「イ」「ウ」「ア」2026-05-25 セッション 24）
- **段階 2 スクリプト仕様確定と実装（補助層 C、セッション 24）**：仕様 [docs/operations/WORKFLOW_PRECHECK.md](../../docs/operations/WORKFLOW_PRECHECK.md) を 15 節構成で新設（コミット `2f1b59a`）。範囲案 2（spec.json／commit／push）、論点 A（ログ MVP 必須）／B（`--rationale` 採用、spec-set 任意・commit／push 必須）／C（別文書）を確定。TDD 第 1 ラウンド（テスト 14 件＋fixture 4 ケース、コミット `6b1b058`／強化 `1bf3cc2`）、第 2 ラウンド（spec-set 実装、コミット `dbc4cd2`）、第 3 ラウンド（commit／push テスト 11 件、コミット `e76746a`）、第 4 ラウンド（commit／push 実装、コミット `a6c8f0c`、25 テスト全件通過）を完遂。`.claude/settings.json` を新設してテスト実行の許可ルール 1 件追加（コミット `662bffb`）（利用者明示承認「(ア)」「次に進む」「範囲案 2」「ア」複数、2026-05-25 セッション 24）
- **共存モデル採用（補助層 C、セッション 24）**：ワークフロー事前検査機構の 3 段階を段階的導入計画でなく最終形態として共存する役割分担として位置付ける。段階 1（LLM 規律、恒久層）／段階 2（外部スクリプト）／段階 3（Claude Code フック）。段階 1 は段階 3 が効かない領域（応答テキストのみの判断）を恒久的に担う。計画書 §5.8 補助層 C として記録、議論メモに反映、TODO §3 D を採用済み方針に書き換え。残作業は段階 2 仕様策定 → 実装 → 段階 1 規律化 → 実測 → 規律統廃合 → 段階 3 フック導入の順（各ステップは利用者明示承認必須）（利用者明示承認「共存モデルの採用」「A から順に進める」2026-05-25 セッション 24）

### セッション 23（2026-05-24 セッション 23）

- **ワークフロー事前検査機構と規律統廃合の検討事項を記録**：利用者ご提案による逸脱防止案（処理開始時の事前検査、計画書 §5.8 補助層 C として位置付け）と、段階 2 導入による規律統廃合の可能性（active 規律 18 件 → 10〜12 件）を [docs/notes/2026-05-25-workflow-pre-check-and-discipline-consolidation.md](../../docs/notes/2026-05-25-workflow-pre-check-and-discipline-consolidation.md) に整理、TODO §3 セクション D として次セッション以降の検討項目に登録（利用者明示承認「(イ)として、次セッションで議論する」2026-05-25 セッション 23）
- **conformance-evaluation 論点 A・B 対処（軽量 reopen、design 段着手の前提条件確立）**：計画書 §5.10 改訂（§5.10.1／5.10.2／5.10.3／5.10.6／5.10.7 改訂、§5.10.9／5.10.10 新設）と conformance-evaluation/requirements.md 改訂（Boundary Context、Requirement 1〜5、Change Intent）。案 Y（2 軸 6 criteria、本筋／傍流の区別、モード別既存文書扱いルール、推定段階の triad-review 適用）を採用。A-010 として pending-cross-feature-findings.md に記録（利用者明示承認「(ア)、一気にやってしまう」「(イ) 案 Y」「(ア)」2026-05-24 セッション 23）
- conformance-evaluation requirements approval 取得（2026-05-24 セッション 23、利用者発言「ア」、依存マップ順 7/7 機能目、最終）。**全 7 機能の requirements approval 取得が完了**
- conformance-evaluation 論点 A・B（機能分離タイミング・既存文書バイアス）を別文書 [docs/notes/2026-05-24-conformance-evaluation-論点-a-b.md](../../docs/notes/2026-05-24-conformance-evaluation-論点-a-b.md) に記録、TODO §3 セクション C として design 着手前必須事項に登録（利用者発言「(ア) 案 1 で進めよう。既にここで議論したことが、ひな形になるので、メモを記録して、approval 後に対応」）
- self-improvement requirements approval 取得（2026-05-24 セッション 23、利用者発言「ア」、依存マップ順 6/7 機能目）
- self-improvement requirements.md 行 173〜175 で機能横断所見セクションを未来形（持ち越し）から過去形（対処された所見）に書き換え、本機能関連の A-007／A-008 を明示し A-001／A-003／A-004／A-005 を参考扱いに整理（修正案 B）
- workflow-management requirements approval 取得（2026-05-24 セッション 23、利用者発言「ア」、依存マップ順 5/7 機能目）
- workflow-management requirements.md 行 160〜162 で機能横断所見セクションを未来形（持ち越し）から過去形（対処された所見）に書き換え、本機能関連の A-005／A-007 を明示し A-001／A-003／A-004 を参考扱いに整理（修正案 B）
- analysis requirements approval 取得（2026-05-24 セッション 23、利用者発言「ア」、依存マップ順 4/7 機能目）
- analysis requirements.md 行 152〜154 で機能横断所見セクションを未来形（持ち越し）から過去形（対処された所見、A-001／A-003 とも 2026-05-23 対処済み）に書き換え
- evaluation requirements approval 取得（2026-05-24 セッション 23、利用者発言「ア」、依存マップ順 3/7 機能目）
- A-009 第 2 波の対処：evaluation 3 箇所（行 7／23／176）＋conformance-evaluation 1 箇所（行 32）で「論文」→「報告書」統一、evaluation 行 176 を未来形（持ち越し）から過去形（対処された所見）に書き換え。pending-cross-feature-findings.md の A-009 エントリを 2 段階対処（第 1 波／第 2 波）として詳細化、保持対象 3 箇所（analysis 行 5、self-improvement 行 24・164）を利用者明示判断「案 β 保持」として確定
- runtime requirements approval 取得（2026-05-24 セッション 23、利用者発言「承認」、依存マップ順 2/7 機能目）
- 文言と事実の食い違いの是正：runtime requirements.md 行 179・181 で A-001 を未来形（持ち越し）から過去形（2026-05-23 対処済み）に書き換え。要件本文の 4 値参照は既に正しい状態のため文言の事実整合のみ
- foundation requirements approval 取得（2026-05-24 セッション 23、利用者発言「確認した。承認」、依存マップ順 1/7 機能目）
- 旧 paper-interface 由来の用語不整合 A-009 の対処：foundation 1 箇所＋analysis 6 箇所で「論文」→「報告書」統一、行 5 の歴史的経緯記述（`paper-interface`（論文向け）の旧名）は保持。利用者発言「(ア) 、論文ではなく報告書とする」（2026-05-24 セッション 23）

### セッション 22（2026-05-24 セッション 22）

- TODO 縮約：履歴系を `docs/archive/todo/TODO_NEXT_SESSION-2026-05-24-snapshot.md` に退避、本体約 100 行に削減
- TODO 雛形 `templates/todo/TODO_NEXT_SESSION.template.md` 新設、本 TODO も雛形構造に整合
- intent 4 文書を素材リポから `intent/` にコピー、`stages/intent.yaml` と `stages/feature-partitioning/2026-05-24-proposal.md` 新設、7 機能の spec.json reference を実在パスに更新
- 設計メモ `docs/design/spec-json-schema-design.md` を archive 退避（`docs/archive/design/2026-05-24-spec-json-schema-design.md`）
- spec.json 雛形配置と 7 機能配置（第 3 段階完了）
- 計画書改定の第 2 段階完了（§5.5／§5.6／§5.7／§5.12／§5.20 改定 ＋ §5.24 新設）
- 段名 local-review → triad-review に改名（active 全ファイル一括置換、63 箇所）
- 論点 1（6 階層保持）と論点 6（機能分離証跡を artifacts へ）の整合解決
- active 必読層棚卸し（候補 1：pre-action-checklist を multi-file-dependency-precheck に統合）
- 規律違反の認知と是正：(a) intent と feature-partitioning を実体確認なく true にした失態、(b) requirements.approval 未取得を見落として design.drafting を提案した失態

---

## 退避規律

- 本ファイルへの退避は、TODO 本体が肥大化した際に古いセッションの確定事項を移すための運用パターン
- 退避タイミング：利用者の明示承認に基づく（「TODOが肥大している」の指摘を受けて）
- 退避対象：3 セッション以上前の長文エントリ（要約は本体に残す）
- 復帰：退避エントリを参照する必要が生じた場合、本ファイルから検索可能

---

## 追加退避（2026-05-25 セッション 25 末でのさらなる縮約、利用者明示承認「(ウ)」）

利用者ご指摘「TODOは短くなっていない」を受け、§3 の完了済み項目と §4 のセッション 25 内エントリ（analysis／design 完了以外）を追加退避。詳細は各参照先（レビュー記録／議論メモ／コミットメッセージ）に既に格納されているため、本セクションは標題と参照先のみを保持する。

### §3 完了済み項目（5 セクション）

| セクション | 結論 | 参照先 |
|---|---|---|
| E. 計画書 §5.9.1 再検討（セッション 25 内決着） | §5.9.1 改訂不要、規律違反対策なし、次回再発時報告運用 | [docs/notes/2026-05-25-triad-review-model-allocation-experiment.md](../../docs/notes/2026-05-25-triad-review-model-allocation-experiment.md)、foundation／reviews／2026-05-25-design-triad-review.md |
| A. requirements approval 取得（2026-05-24 セッション 23 末） | 全 7 機能で取得完了 | コミット履歴（2026-05-24）／各機能 spec.json |
| C. conformance-evaluation 論点 A・B 対処（2026-05-24 セッション 23 末） | 案 Y 採用、計画書 §5.10 改訂、A-010 として記録 | [docs/notes/2026-05-24-conformance-evaluation-論点-a-b.md](../../docs/notes/2026-05-24-conformance-evaluation-論点-a-b.md) |
| D. ワークフロー事前検査機構（補助層 C、セッション 24 で全項目完了） | 3 段階共存モデル完成 | [docs/notes/2026-05-25-workflow-pre-check-and-discipline-consolidation.md](../../docs/notes/2026-05-25-workflow-pre-check-and-discipline-consolidation.md)、計画書 §5.8、[docs/operations/WORKFLOW_PRECHECK.md](../../docs/operations/WORKFLOW_PRECHECK.md) |
| B. 設計フェーズ着手前提（A／C／D 完了で前提条件達成） | 本セッション 25 で 4 機能着手・完了済み | 本セッションのコミット履歴 |

### §4 セッション 25 内エントリ（9 件、analysis／design 完了以外、新しい順）

| エントリ | 主要成果 | 参照先 |
|---|---|---|
| foundation／design 段の drafting と triad-review 実施 | design.md 628→659 行、must-fix 7 件機能内対処 | コミット `9d00d7f`、foundation／reviews／2026-05-25-design-triad-review.md |
| 計画書 §5.9.1 再検討議題追加（セッション 25） | 暫定推奨「敵対役と判定役を Opus 級に」を次セッションで協議 | [docs/notes/2026-05-25-triad-review-model-allocation-experiment.md](../../docs/notes/2026-05-25-triad-review-model-allocation-experiment.md) |
| evaluation／design 段完了（依存マップ順 3/7） | design.md 686→749 行、must-fix 9 件機能内対処、counter_status 中核メトリクス化 | コミット `ef9dcf6`、evaluation／reviews／2026-05-25-design-triad-review.md |
| runtime／design 段完了（依存マップ順 2/7） | design.md 704→725 行、must-fix 3 件機能内対処、step_outcome 3 値正本確定 | コミット `7ee63e0`＋`6ebf9e8`、runtime／reviews／2026-05-25-design-triad-review.md |
| 計画書 §5.9.1 包括改訂（コミット 0e85087） | 旧規律「同モデル使用禁止」撤回、「モデル能力配分規律」に改訂 | コミット `0e85087` |
| foundation／design must-fix の手順違反記録 | 「(ア-1)」議論義務化規律へ展開 | コミット `bdca440`、foundation／reviews／2026-05-25-design-triad-review.md §4.1.1 |
| must-fix 議論セット 1〜3 の決着と原則確立 | 設計原則 2 つ確立：(1) review_case の不変性、(2) foundation は契約のみ固定 | foundation／reviews／2026-05-25-design-triad-review.md §4.1.1 |
| must-fix 対処の議論義務化規律の制定 | 運営ガイド §3.3 (a-1) 新設、memory 規律新設 | [docs/operations/SESSION_WORKFLOW_GUIDE.md](../../docs/operations/SESSION_WORKFLOW_GUIDE.md) §3.3 (a-1)、memory／feedback_must_fix_discussion_obligation.md |
| §5.9.1 再検討の決着（§5.9.1 改訂不要） | §5.9.1 既定（主役 Opus 4.7 ／ 敵対役 Sonnet 4.6 ／ 判定役 Opus 4.7）を維持 | コミット `f17a14e`（TODO 更新）、TODO §3 E（本退避前） |
