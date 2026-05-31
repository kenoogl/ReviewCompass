# 規律ファイル（disciplines）

最終更新：2026-05-31（セッション 41：`discipline_post_write_verification.md` を新設、active 必読昇格。本規律自身の起草に対し独立 3 系統で 5 回の検証ループを経て発効、OpenAI／Google で ALL_CLEAR 達成）／2026-05-26（セッション 27：旧 dominant-dominated-options ／ choice-presentation を統合し `discipline_options_presentation.md` を新設、active 必読昇格＋事前検査宣言義務を新設、旧 2 件は `archive/2026-05-26-consolidation/` へ退避。利用者明示承認「OK」「承認」）

過去履歴：
- セッション 27（2026-05-26）前半：シンボリックリンク検証失敗・fallback 案イ採用、毎セッション開始時に TODO §1 起動手順で active 必読を Read で読む運用に切り替え（auto memory 機構の起動時 load 対象は MEMORY.md の索引までで、シンボリックリンク経由でも規律本体は load されないことが判明）
- セッション 26（2026-05-25）：active 必読 12 件 ＋ 参照層 5 件＝合計 17 件を memory から軽量移送 → `no-unilateral-action` 撤去で 16 件 → memory 側 `feedback_*.md` をシンボリックリンクに変更

## 配置と所有

本ディレクトリ `docs/disciplines/` は ReviewCompass プロジェクト固有の運用規律ファイルを保管する。**所有者は `workflow-management` 機能**（A-007 案 2、2026-05-23 利用者承認）で、改廃は本機能の所定手続き（drafting → review → approval）経由で実施する。

各ファイルは `discipline_<name>.md` の命名規約に従う。`<name>` は規律内容を表す英語ハイフン区切り（例：`discipline_must_fix_discussion_obligation.md`）。

## 内部リンク記法

各規律ファイル本文に `[[link-name]]` 形式の内部参照（例：`[[approval-operation]]`、`[[workflow-precheck-invocation]]`）が登場する。これは memory 機構の慣習を引き継いだ記法で、本ディレクトリ内では次の規則で解決する：

- **`[[name]]`** → `docs/disciplines/discipline_<name>.md`（同ディレクトリ内のファイル）
- 例：`[[approval-operation]]` → `discipline_approval_operation.md`
- 例：`[[workflow-precheck-invocation]]` → `discipline_workflow_precheck_invocation.md`

本記法は Markdown viewer によっては自動でクリック可能リンクとして解決されないが、内部参照の意図を明示する目的で維持する。Markdown リンク形式への一括変換は別途検討（フェーズ 2 以降の宿題）。

## 規律ファイル一覧

最新の件数は本一覧の各表（active 必読／参照層／archive）で確認すること。件数は本見出しには固定しない（増減の都度に編集箇所が分散するのを避けるため）。

### active 必読（セッション開始時に TODO §1 起動手順で Read 対象）

| ファイル | 概要 |
|---|---|
| [discipline_must_fix_discussion_obligation.md](discipline_must_fix_discussion_obligation.md) | triad-review の must-fix 所見は利用者と必ず議論、独自判断で仕様修正禁止 |
| [discipline_intent_conformance_is_the_acceptance_gate.md](discipline_intent_conformance_is_the_acceptance_gate.md) | 受け入れ基準は「実装が意図どおり機能＝承認仕様に適合」か（フルスクラッチは手法でゲートでない） |
| [discipline_standing_directives_are_hard_constraints.md](discipline_standing_directives_are_hard_constraints.md) | フルスクラッチ等の恒常指示は既定でなく硬い制約、approach 変更は自律確定せずエスカレーション |
| [discipline_workflow_precheck_invocation.md](discipline_workflow_precheck_invocation.md) | 不可逆操作の直前に tools/check-workflow-action.py を呼び verdict／reasons を応答に明示 |
| [discipline_approval_operation.md](discipline_approval_operation.md) | 不可逆操作は利用者明示承認必須、明示的肯定発言のみ承認、確定記述には承認出典を併記 |
| [discipline_facts_vs_interpretation.md](discipline_facts_vs_interpretation.md) | 達成基準を事前宣言、編集後は機械的照合、事実と解釈を別個に示し出典に辿れる形に |
| [discipline_pre_action_precheck.md](discipline_pre_action_precheck.md) | 集約・横断操作の前に 5 項目チェックリスト＋grep＋3 分類を応答内で明示 |
| [discipline_workflow_state_truth_source.md](discipline_workflow_state_truth_source.md) | 状態判定は workflow_state を読み、過去確定事項は出典付きのみ信頼 |
| [discipline_concise_complete_report.md](discipline_concise_complete_report.md) | 作業後は応答末尾で実施内容を箇条書きで全件列挙、ファイルパス・変更内容を必ず含める |
| [discipline_reopen_procedure_for_settled_topics.md](discipline_reopen_procedure_for_settled_topics.md) | 確定済み論点を変更する場合は 5 ステップ（宣言・理由・新案・明示承認・履歴記録） |
| [discipline_plain_japanese.md](discipline_plain_japanese.md) | 英語技術用語を多用しない、完全な日本語の文で書く、応答送信前に自己検査 |
| [discipline_options_presentation.md](discipline_options_presentation.md) | 複数案提示時、dominated 案は提示しない、提示前に検査結果を応答内で明示宣言、3 選択肢以内で大局→細部の階層性を守る（旧 dominant-dominated-options ／ choice-presentation を統合＋事前検査宣言義務を新設） |
| [discipline_avoid_compound_bash.md](discipline_avoid_compound_bash.md) | 読み取り目的の複合 Bash コマンド（`;`／`&&`／`|`）を避ける、Read／Glob／Grep ツールで代替するか単一コマンドに留める、許可プロンプト多発の防止（2026-05-28 セッション 36 軽量移送で確立、利用者明示承認「案 イを処理」） |
| [discipline_post_write_verification.md](discipline_post_write_verification.md) | ワークフロー段の外側にある正本文書への書き込み後、起草者と異なるサブエージェント（既定 3 体、Anthropic ／ OpenAI ／ Google の独立系統）による独立検証を必須化。1 件でも検出があれば一律阻止。small=1 体でも起草者系統と異なる独立系統必須（既定 Google `gemini-3.5-flash`）。本セッションの 5 回検証で実証（独立 3 系統で OpenAI／Google が ALL_CLEAR、利用者明示承認「OK」、2026-05-31 セッション 41 新設） |

### 参照層（3 件、必要時に grep／Read で参照、起動時 load なし）

| ファイル | 概要 |
|---|---|
| [discipline_no_redundant_workflow_questions.md](discipline_no_redundant_workflow_questions.md) | 正本ワークフローが順序・方式を既定する局面で機能ごとに止めて尋ねない |
| [discipline_plain_explanation_each_step.md](discipline_plain_explanation_each_step.md) | 1 件ずつ承認の各ステップで承認前に平易な日本語説明を先に添える |
| [discipline_implementation_autonomy.md](discipline_implementation_autonomy.md) | 実装フェーズはタスクごとに止めず自律進行、コミット／プッシュ／spec.json／フェーズ移行のみ明示承認 |

### archive（統廃合元・撤廃済みの本体保全、起動時 load なし）

| ディレクトリ | 内容 |
|---|---|
| [archive/2026-05-26-consolidation/](archive/2026-05-26-consolidation/) | セッション 27（2026-05-26）の統廃合元 2 件（旧 dominant-dominated-options ／ choice-presentation）。統合先は active 必読の `discipline_options_presentation.md` |

## 関連参照

- **対応する memory 側索引**：`~/.claude/projects/-Users-Daily-Development-ReviewCompass/memory/feedback_*.md`（短い参照索引、本体は本ディレクトリを Read で参照）
- **memory archive**（統廃合元 14 件）：`~/.claude/projects/-Users-Daily-Development-ReviewCompass/memory/archive/2026-05-25-consolidation/`
- **本機能の設計**：`.reviewcompass/specs/workflow-management/design.md` §責務境界の明確化
- **計画書 §5.21**：規律ファイルの ReviewCompass 方針への取り入れ手順
- **移送経緯**：本セッション 26（2026-05-25）の軽量手続きにより、active 必読 12 件＋参照層 5 件を memory から移管。memory 側は短い参照索引に置換、本体は git 追跡対象として本ディレクトリで管理
