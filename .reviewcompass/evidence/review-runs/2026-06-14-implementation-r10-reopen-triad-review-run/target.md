# レビュー対象：reopen R-0（review-wave-summary-command）workflow-management implementation（TDD）

## 0. variant 選定理由
- variant：implementation_review_independent_3way（claude-sonnet-4-6／gpt-5.5／gemini-3.1-pro-preview）。Claude Code 操縦時の API 既定。利用者「コミット点まで自律で進める」。

## 1. 位置付け
reopen R-0 の第3過程 implementation フェーズ triad-review。requirements・design・tasks は approval 済み。T-012（review-wave-summary サブコマンド）を TDD で実装。

## 2. 実装内容（tools/check-workflow-action.py に追加）

### 2.1 サブコマンド `review-wave-summary`（design §1〜§5 準拠）
- `build_review_wave_summary(cwd)`：(summary_dict, exit_code) を返す。読み取りに徹し spec.json・triage・phase を書き換えない。
- 必須記録＝全 feature の spec.json と feature-dependency.yaml。欠落・解析不能で status:insufficient＋exit 2。
- features[]：coverage（completed/total/all_approved）、phases（phase 名→{stage: bool}）、recheck。
- `aggregate_triage_for_summary(cwd)`：triage.yaml 群を走査（evidence/review-runs/ 優先・旧 _cross_feature/reviews/ 互換、run_id＝ディレクトリ名で重複排除）。unresolved/human_required は item 単位、draft は run 単位。任意記録の非在は 0 件で ok、存在して解析不能なら insufficient。
- dependencies：feature_order と未充足依存（depends_on は list/dict 両対応、上流が all_approved でないものを unmet）。
- carry_forward：count_unresolved_carry_forward_items（status≠resolved）。
- JSON 安定スキーマ（schema_version/generated_at/status/features/triage/dependencies/carry_forward/errors）。Markdown は情報同等（render_review_wave_summary_markdown）。終了コード 0=ok／2=insufficient。
- 既存関数（load_all_feature_specs・load_feature_dependency・count_unresolved_carry_forward_items）を再利用。

### 2.2 CLI 登録
- サブパーサ `review-wave-summary`（--json は共通、--out <path>、--save）。dispatch を main に追加。
- 保存（--out/--save）は自身の要約出力のみ。spec.json・triage・phase は不変。

### 2.3 テスト（TDD、先に失敗テスト → 実装で緑）
- `tests/tools/test_review_wave_summary.py` 10 件：JSON スキーマ・status ok、必須記録欠落（feature-dependency／spec.json）で insufficient＋exit 2、任意 triage の非在は ok・0 件、存在して解析不能で insufficient、triage 集計軸（unresolved/human_required=item 単位・draft=run 単位）、run_id 重複排除（evidence 優先）、読み取り専用（実行後 spec.json 不変）、Markdown 既定出力、--out 保存＋読み取り専用。
- 結果：赤（invalid choice）→ 実装 → 緑（10/10 pass）。tests/tools/ 全体 297 件 pass（回帰なし）。実リポジトリ dogfooding で workflow-management が pending(implementation) と表示、status ok。

## 3. レビュー観点（criteria: implementation_r10_review_wave_summary_command）
1. 実装が design §1〜§5 の契約（読み取り元・算出定義・JSON 安定スキーマ・fail-closed の必須/任意記録の扱い・終了コード 0/2・読み取り専用・保存）を満たすか。
2. fail-closed の漏れ（例外時の挙動、部分集計を ok にしない）がないか。
3. テストが design の各契約を網羅し TDD（赤→緑）であるか。回帰がないか。
4. 既存関数の再利用が正しく、副作用（状態書き換え）がないか。
5. tasks T-012 の完了条件・テスト要件を満たすか。
