# 規律ファイルの旧配置（disciplines）

最終更新：2026-06-19（`discipline_normal_output_minimization.md` を新設、active 必読昇格。CLI / tool の正常系 human output を最小化し、異常系と `--json` の情報量を維持する共通規律。利用者指示「全 CLI / 全ツールへ広げるなら、別途『正常系出力最小化』の共通規律と各ツールの棚卸し。これを対応」に基づく）／2026-06-18（イレギュラー組み込み：`discipline_llm_as_judge_prompting.md` を新設、active 必読昇格。3者レビュー・proxy_model 利用時のプロンプト作成ガイドライン。通常の drafting→review→approval 手続きを省略し利用者明示承認「強制的に組み込みたい」「はい」で即時発効）／2026-06-02（セッション 50：`discipline_yaml_audit.md` を新設、active 必読昇格。設定・動作仕様 yaml 専用の監査規律（補助層 E）。独立 3 系統で 2 回の検証ループを経て発効、利用者明示承認「承認」）／2026-05-31（セッション 41：`discipline_post_write_verification.md` を新設、active 必読昇格。本規律自身の起草に対し独立 3 系統で 5 回の検証ループを経て発効、OpenAI／Google で ALL_CLEAR 達成）／2026-05-26（セッション 27：旧 dominant-dominated-options ／ choice-presentation を統合し `discipline_options_presentation.md` を新設、active 必読昇格＋事前検査宣言義務を新設、旧 2 件は `archive/2026-05-26-consolidation/` へ退避。利用者明示承認「OK」「承認」）

過去履歴：
- セッション 27（2026-05-26）前半：シンボリックリンク検証失敗・fallback 案イ採用により、当時は毎セッション開始時に TODO §1 起動手順で active 必読を Read で読む運用に切り替えた。現在は `.reviewcompass/guidance/WORKFLOW_NAVIGATION.md` に従い、`tools/check-workflow-action.py next --json` の `next_action.required_disciplines` が示す場面別の規律だけを作業直前に読む。
- セッション 26（2026-05-25）：active 必読 12 件 ＋ 参照層 5 件＝合計 17 件を memory から軽量移送 → `no-unilateral-action` 撤去で 16 件 → memory 側 `feedback_*.md` をシンボリックリンクに変更

## 配置と所有

active 規律ファイルの正本は `.reviewcompass/guidance/discipline_*.md` へ移動済みである。

本ディレクトリ `docs/disciplines/` は旧配置の説明と archive を保管する。**所有者は `workflow-management` 機能**（A-007 案 2、2026-05-23 利用者承認）で、active 規律の改廃は `.reviewcompass/guidance/discipline_*.md` を対象として本機能の所定手続き（drafting → review → approval）経由で実施する。

active 規律ファイルは `.reviewcompass/guidance/discipline_<name>.md` の命名規約に従う。`<name>` は規律内容を表す英語ハイフン区切り（例：`discipline_must_fix_discussion_obligation.md`）。

## 内部リンク記法

各規律ファイル本文に `[[link-name]]` 形式の内部参照（例：`[[approval-operation]]`、`[[workflow-precheck-invocation]]`）が登場する。これは memory 機構の慣習を引き継いだ記法で、本ディレクトリ内では次の規則で解決する：

- **`[[name]]`** → `.reviewcompass/guidance/discipline_<name>.md`
- 例：`[[approval-operation]]` → `discipline_approval_operation.md`
- 例：`[[workflow-precheck-invocation]]` → `discipline_workflow_precheck_invocation.md`

本記法は Markdown viewer によっては自動でクリック可能リンクとして解決されないが、内部参照の意図を明示する目的で維持する。Markdown リンク形式への一括変換は別途検討（フェーズ 2 以降の宿題）。

## 規律ファイル一覧

最新の件数は本一覧の各表（active 必読／参照層／archive）で確認すること。件数は本見出しには固定しない（増減の都度に編集箇所が分散するのを避けるため）。

### active 規律（`next --json` の required_disciplines に従い作業直前に読む）

| ファイル | 概要 |
|---|---|
| [discipline_must_fix_discussion_obligation.md](../../.reviewcompass/guidance/discipline_must_fix_discussion_obligation.md) | triad-review の must-fix 所見は利用者と必ず議論、独自判断で仕様修正禁止 |
| [discipline_intent_conformance_is_the_acceptance_gate.md](../../.reviewcompass/guidance/discipline_intent_conformance_is_the_acceptance_gate.md) | 受け入れ基準は「実装が意図どおり機能＝承認仕様に適合」か（フルスクラッチは手法でゲートでない） |
| [discipline_standing_directives_are_hard_constraints.md](../../.reviewcompass/guidance/discipline_standing_directives_are_hard_constraints.md) | フルスクラッチ等の恒常指示は既定でなく硬い制約、approach 変更は自律確定せずエスカレーション |
| [discipline_workflow_precheck_invocation.md](../../.reviewcompass/guidance/discipline_workflow_precheck_invocation.md) | 不可逆操作の直前に tools/check-workflow-action.py を呼び verdict／reasons を応答に明示 |
| [discipline_approval_operation.md](../../.reviewcompass/guidance/discipline_approval_operation.md) | 不可逆操作は利用者明示承認必須、明示的肯定発言のみ承認、確定記述には承認出典を併記 |
| [discipline_facts_vs_interpretation.md](../../.reviewcompass/guidance/discipline_facts_vs_interpretation.md) | 達成基準を事前宣言、編集後は機械的照合、事実と解釈を別個に示し出典に辿れる形に |
| [discipline_pre_action_precheck.md](../../.reviewcompass/guidance/discipline_pre_action_precheck.md) | 集約・横断操作の前に 5 項目チェックリスト＋grep＋3 分類を応答内で明示。波及調査は全対象×全表記（機械可読の識別子と人間可読の和訳の両方）で網羅 grep してから着手（2026-06-02 セッション 47 追加） |
| [discipline_workflow_state_truth_source.md](../../.reviewcompass/guidance/discipline_workflow_state_truth_source.md) | 状態判定は workflow_state を読み、過去確定事項は出典付きのみ信頼 |
| [discipline_concise_complete_report.md](../../.reviewcompass/guidance/discipline_concise_complete_report.md) | 作業後は応答末尾で実施内容を箇条書きで全件列挙、ファイルパス・変更内容を必ず含める |
| [discipline_reopen_procedure_for_settled_topics.md](../../.reviewcompass/guidance/discipline_reopen_procedure_for_settled_topics.md) | 確定済み論点を変更する場合は 5 ステップ（宣言・理由・新案・明示承認・履歴記録） |
| [discipline_plain_japanese.md](../../.reviewcompass/guidance/discipline_plain_japanese.md) | 英語技術用語を多用しない、完全な日本語の文で書く、応答送信前に自己検査 |
| [discipline_options_presentation.md](../../.reviewcompass/guidance/discipline_options_presentation.md) | 複数案提示時、dominated 案は提示しない、提示前に検査結果を応答内で明示宣言、3 選択肢以内で大局→細部の階層性を守る（旧 dominant-dominated-options ／ choice-presentation を統合＋事前検査宣言義務を新設） |
| [discipline_avoid_compound_bash.md](../../.reviewcompass/guidance/discipline_avoid_compound_bash.md) | 読み取り目的の複合 Bash コマンド（`;`／`&&`／`|`）を避ける、Read／Glob／Grep ツールで代替するか単一コマンドに留める、許可プロンプト多発の防止（2026-05-28 セッション 36 軽量移送で確立、利用者明示承認「案 イを処理」） |
| [discipline_post_write_verification.md](../../.reviewcompass/guidance/discipline_post_write_verification.md) | ワークフロー段の外側にある正本文書への書き込み後、起草者と異なる検証経路による独立検証を必須化。検出は逐語的指摘（弾く）と本質的指摘（人へ上げる）に分類して処理し、収束基準は動作仕様ファイル post-write-verification-spec.yaml と現行 API variant 設定に従う。2026-05-31 セッション 41 新設・2026-06-01 セッション 43 収束基準改訂 |
| [discipline_yaml_audit.md](../../.reviewcompass/guidance/discipline_yaml_audit.md) | 設定・動作仕様 yaml（config/, runtime/config/, stages/, .reviewcompass/specs/ 配下）への書き込み後に監査を必須化する規律（補助層 E）。md 用書き込み後検証（補助層 D）とは別立て。11 観点（A 系統：機械検査 6 必須＋2 推奨、B 系統：独立検証 3 必須）で点検。新規対象の組み入れ時に全件を初回検証。2026-06-02 セッション 50 新設 |
| [discipline_llm_as_judge_prompting.md](../../.reviewcompass/guidance/discipline_llm_as_judge_prompting.md) | 3者レビュー・proxy_model 利用時のプロンプト作成ガイドライン。材料揃え（メインLLMが問題を直接検討）→ 問い設計（情報・問い・範囲の3要素）→ 選択肢なし分析の手順で品質を高める。2026-06-18 セッション 新設 |
| [discipline_normal_output_minimization.md](../../.reviewcompass/guidance/discipline_normal_output_minimization.md) | CLI / tool の正常系 human output を最小化し、異常系と `--json` の情報量を維持する。共通棚卸し YAML を更新しながら全 tool へ段階適用する。2026-06-19 新設 |

### 参照層（3 件、必要時に grep／Read で参照、起動時 load なし）

| ファイル | 概要 |
|---|---|
| [discipline_no_redundant_workflow_questions.md](../../.reviewcompass/guidance/discipline_no_redundant_workflow_questions.md) | 正本ワークフローが順序・方式を既定する局面で機能ごとに止めて尋ねない |
| [discipline_plain_explanation_each_step.md](../../.reviewcompass/guidance/discipline_plain_explanation_each_step.md) | 1 件ずつ承認の各ステップで承認前に平易な日本語説明を先に添える |
| [discipline_implementation_autonomy.md](../../.reviewcompass/guidance/discipline_implementation_autonomy.md) | 実装フェーズはタスクごとに止めず自律進行、コミット／プッシュ／spec.json／フェーズ移行のみ明示承認 |

### archive（統廃合元・撤廃済みの本体保全、起動時 load なし）

| ディレクトリ | 内容 |
|---|---|
| [archive/2026-05-26-consolidation/](archive/2026-05-26-consolidation/) | セッション 27（2026-05-26）の統廃合元 2 件（旧 dominant-dominated-options ／ choice-presentation）。統合先は active 必読の `discipline_options_presentation.md` |

## 関連参照

- **対応する memory 側索引**：`~/.claude/projects/-Users-Daily-Development-ReviewCompass/memory/feedback_*.md`（短い参照索引、本体は本ディレクトリを Read で参照）
- **memory archive**（統廃合元 14 件）：`~/.claude/projects/-Users-Daily-Development-ReviewCompass/memory/archive/2026-05-25-consolidation/`
- **本機能の設計**：`.reviewcompass/specs/workflow-management/design.md` §責務境界の明確化
- **計画書 §5.21**：規律ファイルの ReviewCompass 方針への取り入れ手順
- **移送経緯**：本セッション 26（2026-05-25）の軽量手続きにより、active 必読 12 件＋参照層 5 件を memory から移管。2026-06-23 の guidance relocation により、active 本体は `.reviewcompass/guidance/` へ移動
