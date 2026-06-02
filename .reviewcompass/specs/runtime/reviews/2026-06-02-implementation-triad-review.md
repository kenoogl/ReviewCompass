---
spec: runtime
phase: implementation
stage: triad-review
mode: api_mediated
date: 2026-06-02
author:
  identity: claude_code_main_session
  model: claude-opus-4-8
  role: drafter
reviewer:
  identity: api_mediated_triad
  role: triad_review
  separation_from_author: true
roles:
  primary_reviewer:
    provider: anthropic-api
    model: claude-opus-4-8
  adversarial_reviewer:
    provider: openai-api
    model: gpt-5.5
    timeout_seconds: 300
  judgment_reviewer:
    provider: gemini-api
    model: gemini-3.1-pro-preview
review_perspectives:
  - タスク文書との整合
  - 要件への追跡
  - テスト網羅性と信頼性
  - 配置・命名規約の遵守
  - 機能横断波及の早期検出
---

# runtime implementation 段 triad-review 記録

api_mediated（独立3社 API）方式での初の実装 triad-review。foundation（2026-06-01）は
subagent_mediated だったが、TODO §3.1 と利用者選択により本機能から独立3社 API 方式を採用。
主役 Claude Opus 4.8（Anthropic）／敵対役 GPT-5.5（OpenAI、timeout 300 秒）／判定役
Gemini 3.1 Pro（Google）。起草者（メインセッション Opus 4.8）は3役のいずれにもならず、
3役すべて独立プロバイダーの API。レビュー観点は実装レビュー5観点（セッション45 暫定確定、
[docs/notes/2026-06-01-implementation-phase-approach.md](../../../../docs/notes/2026-06-01-implementation-phase-approach.md)）。

実行基盤：プロンプト生成 `tools/experiments/_gen_runtime_impl_triad_temp.py`、役実行
`tools/experiments/_experiment_n_model.py`（既存）経由。生ログは
`tools/experiments/_runtime_triad_work/`。利用者明示承認の出典：「独立3社API（推奨）」
（実施方式、AskUserQuestion 2026-06-02）。

## 0. レビュー対象と網羅性に関する記録

**初回レビューの偽陽性と再実行**：初回は起草者のプロンプト生成が対象から
`docs/operations/RUNTIME.md`（T-001 成果物）を取りこぼし、敵対役・判定役が「RUNTIME.md が
存在しない」と must-fix（A-001 初回）を誤検出した。起草者がファイル実在を確認し（偽陽性と
判定）、プロンプト生成スクリプトに RUNTIME.md を加えて全3役を再実行した。本記録は再実行後の
完全な対象での結果。利用者明示承認の出典：「RUNTIME.mdは当然再レビュー」（2026-06-02）。

**レビュー対象（再実行）**：runtime 実装（`runtime/runtime_core/` 配下）＋テスト
（`tests/runtime/`）＋上流文書（requirements.md／design.md／tasks.md）＋運用文書
（docs/operations/RUNTIME.md）。

## 1. 主役レビュー（primary_reviewer、Claude Opus 4.8）

10 件の所見（観点別）：

| ID | 観点 | severity | 概要 |
|---|---|---|---|
| P-001 | 3 | ERROR | 正常系 close_run の closed_at 永続が単体テストで未検証（順序の偽陽性余地と主張） |
| P-002 | 3 | WARN | close_run が Step D の run_close_ready 信号を消費せず step_outcome のみで判定 |
| P-003 | 1 | WARN | writer.py が step_records に step_name を投影していないと主張 |
| P-004 | 2 | WARN | foundation_ref.vocabulary の docstring が参照範囲外の confidence_label を例示 |
| P-005 | 3 | WARN | 段実行器に step_outcome=failed を出力する経路がなく failed テストもない |
| P-006 | 3 | WARN | failure_observation_writer がパイプラインから失敗時に呼ばれる結線がない |
| P-007 | 4 | INFO | RUNTIME.md §7 の配置記述が実装の正本パスと不一致（旧計画書由来パス残存） |
| P-008 | 5 | INFO | runtime テストが foundation 検証ツールを直接 import する横断結合 |
| P-009 | 2 | INFO | 6 語彙再定義検査が YAML トップレベルキーのみで値の固定列挙を見逃す |
| P-010 | 1 | INFO | _fail_closed が evidence_class を invalid に確定しない |

## 2. 敵対役レビュー（adversarial_reviewer、GPT-5.5）

主役所見の検証：

- **同意**：P-002・P-004・P-005・P-006・P-007・P-008・P-009・P-010
- **反証あり**：
  - P-001：freeze() 後に manifest を再読込して追加保存するため closed_at は保持される。T-011 統合テストが凍結マーカーを検査しており ERROR は過大。
  - P-003：writer.py は step_records.append 内で step_name を明示投影している。主役所見は実装事実と反する（指摘自体が誤り）。

独立発見（主役見落とし、6 件）：

| ID | 観点 | severity | 概要 |
|---|---|---|---|
| A-001 | 1 | ERROR | start_session が実行ルートのみ作成し、必須5サブディレクトリ（steps/decisions/failures/validation/derived）を作らない（T-001／T-002 明示要求） |
| A-002 | 3 | ERROR | 検証器が4値外を返すと close_run が例外送出のみで fail-closed せず、closed_at 持ちの in_progress 中間状態が残る |
| A-003 | 3 | ERROR | validator_status=failed/blocked のとき無効化標識・トリアージ記録（invalid_run_triage_note.json）が生成されない（要件6受入7・8） |
| A-004 | 3 | WARN | Step D の run_close_ready が省略段の skipped_by_treatment マーカー存在を要求せず、欠落でも True になりうる（要件2受入5） |
| A-005 | 2 | WARN | RUNTIME.md §5 が review_mode を3値列挙のままで foundation 正本に追加された api_mediated を欠く（contract consumer 原則と矛盾する縮約） |
| A-006 | 1 | WARN | close_run が run_manifest.yaml のみ更新し横断正本 review_case.json の終了メタデータを反映しない（design §実行終了境界 手順3） |

## 3. 判定役（judgment_reviewer、Gemini 3.1 Pro）

主役・敵対役の全16所見を判定。**すべて waveband=in_feature（機能内対処）。波及・遡及・延期はゼロ**。

| 判定 | 件数 | 所見 |
|---|---|---|
| must-fix | 9 | P-002／P-005／P-006／P-010／A-001／A-002／A-003／A-005／A-006 |
| should-fix | 5 | P-004／P-007／P-008／P-009／A-004 |
| leave-as-is | 2 | P-001（敵対役反証：closed_at は保持）／P-003（敵対役反証：step_name は投影済み） |

leave-as-is 2件はいずれも主役の誤指摘を敵対役・判定役が事実で覆したもの。起草者と判定者の
分離が機能した実例。

**起草者の事後検証**（運営ガイド §4.3）：must-fix 9件を design.md／tasks.md／requirements.md と
照合し、いずれも明示要求または設計整合性に基づく真の所見と確認（再実行では偽陽性なし）。

## 4. 統合（対処方針・利用者承認・反映箇所）

must-fix 9件は規律（運営ガイド §3.3 a-1）に従い利用者と4論点で議論。利用者明示判断：
論点A「案ア」／論点B・C・D「まとめて案ア」／should-fix「案ア」（いずれも 2026-06-02）。

| 所見 | 判定 | 対処 | 反映箇所 |
|---|---|---|---|
| A-001 | must-fix | start_session で必須5サブディレクトリを作成 | session_controller.py |
| A-006 | must-fix | close_run で EvidenceWriter.project_to_review_case を呼び終了メタデータを横断正本に反映 | bridge.py、writer.py |
| P-002 | must-fix | close_run の前提に run_close_ready 確認を追加 | bridge.py |
| P-010 | must-fix | _fail_closed で evidence_class=invalid を確定 | bridge.py |
| A-002 | must-fix | 検証器4値外で fail-closed（中間状態を残さない） | bridge.py |
| A-003 | must-fix | evidence_class=invalid 時にトリアージ記録を生成 | bridge.py |
| P-005 | must-fix | 各段の実行失敗で step_outcome=failed マーカーを残す | step_executors/__init__.py、step_a/b/c |
| P-006 | must-fix | 失敗時に failure_observation を独立成果物として書き出す | step_executors/__init__.py、step_a/b/c |
| A-005 | must-fix | RUNTIME.md §5 に api_mediated を追加し正本参照を明記 | docs/operations/RUNTIME.md（独立検証 ALL_CLEAR） |
| A-004 | should-fix | Step D の _readiness が省略段マーカーの存在も確認 | step_d_integration.py |
| P-004 | should-fix | docstring の参照範囲を明確化（confidence_label は参照範囲外） | foundation_ref.py |
| P-007 | should-fix | RUNTIME.md §7 の配置記述を実装パスに更新 | docs/operations/RUNTIME.md（独立検証 ALL_CLEAR） |
| P-008 | should-fix | 要件追跡テストの foundation ツール直接 import を自前実装に置換 | test_t011_traceability.py |
| P-009 | should-fix | 語彙再定義検査を値集合レベルまで強化 | test_t011_foundation_contract.py |
| P-001 | leave-as-is | 対処なし（敵対役反証：closed_at は保持される。判定根拠を本記録に保全） | — |
| P-003 | leave-as-is | 対処なし（敵対役反証：step_name は投影済み、主役所見は実装事実と反する） | — |

**検証結果**：TDD（テスト先行→実装）。新規テスト11件を先行追加し赤を確認、対処後に全テスト
緑 143 件（回帰なし）。RUNTIME.md（docs/operations 配下）の修正は規律 post-write-verification に
従い Google（gemini-3.5-flash、起草者の Anthropic 系統と独立）で独立検証し ALL_CLEAR。

**コミット**：テスト先行 `99c0471`、実装 `43846f8`。本記録と spec.json 更新は別コミット。

**機能横断波及**：判定役の全所見が in_feature のため、`pending-cross-feature-findings.md` への
追記なし（runtime 機能内で完結）。
