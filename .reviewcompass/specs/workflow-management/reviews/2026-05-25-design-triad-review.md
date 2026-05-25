---
type: design_triad_review
target: .reviewcompass/specs/workflow-management/design.md
target_commit: <未コミット、本セッションで起草された design.md＋must-fix 反映版＋G8 軽量移送反映版>
target_baseline_commit: 881761d
date: 2026-05-25
mode: subagent_mediated
session: session-26
primary:
  provider: claude_code_subagent
  model: claude-sonnet-4-6
  model_full_id: claude-sonnet-4-6
  attempts: 1
  duration_minutes: <未計測>
  prompt_artifact_path: <未整備、メインセッションのメッセージで暫定指示>
  prompt_artifact_hash: <未整備>
adversarial:
  provider: claude_code_subagent
  model: claude-opus-4-7
  model_full_id: claude-opus-4-7
  attempts: 1
  duration_minutes: <未計測>
  prompt_artifact_path: <未整備、メインセッションのメッセージで暫定指示>
  prompt_artifact_hash: <未整備>
judgment:
  provider: claude_code_subagent
  model: claude-opus-4-7
  model_full_id: claude-opus-4-7
  attempts: 1
  duration_minutes: <未計測>
  prompt_artifact_path: <未整備、メインセッションのメッセージで暫定指示>
  prompt_artifact_hash: <未整備>
findings_by_method:
  primary:
    by_severity: { CRITICAL: 0, ERROR: 3, WARN: 12, INFO: 4 }
    count: 19
  adversarial:
    by_severity: { CRITICAL: 0, ERROR: 4, WARN: 6, INFO: 2 }
    count: 12
    counter_distribution: { counter_evidence_raised: 0, no_counter_evidence_after_challenge: 17, not_assessed: 2 }
  judgment:
    by_judgment: { must-fix: 10, should-fix: 17, leave-as-is: 4 }
    by_waterfall: { 機能内対処: 22, 波及: 0, 遡及: 1, 延期: 4, leave-as-is: 3 }
    count: 31
author:
  identity: claude_code_main_session
  model: claude-opus-4-7
  role: drafter
reviewer:
  identity: claude_code_subagent_judgment
  model: claude-opus-4-7
  role: final_judgment
  separation_from_author: true
subagent_mediated_caveats:
  - メインセッション（起草者、Opus 4.7）は 3 役のいずれにも入っていない（規律 §0.3 起草者と判定者の分離を満たす）
  - 3 役配置は実験(エ)配置（主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7）、利用者明示承認「A」2026-05-25 セッション 26。改訂された §5.9.1（コミット 0e85087）「主役と敵対役は必ず異なる、判定役は同モデル許容、能力配分優先」に整合
  - プロンプト雛形が未整備のため、各役のプロンプトはメインセッションのメッセージで暫定指示（計画書 §5.23.12.3）
  - サブエージェントの計画書引用や事実主張はメインセッションで事後検証する運用（計画書 §5.23.12.7）
  - 主役の所見要約集計（CRITICAL 0／ERROR 3／WARN 8／INFO 4＝15）は本文の所見数（19）と不整合。本文に列挙された 19 件すべてを判定対象とした（敵対役と判定役で確認）
---

# レビュー記録：workflow-management 設計 triad-review

本記録は ReviewCompass の workflow-management 機能の設計文書（design.md、起草時 806 行→must-fix 反映後 884 行）に対する 3 役レビューの結果。3 役配置は実験(エ)配置（主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7）。foundation／runtime／evaluation／analysis の同期セッション内 triad-review と同じ流れで実施、依存マップ順 5/7。

---

## 1. 主役レビュー（primary、Sonnet 4.6）

主役は計画書 §5.9.2 の設計レビュー 10 観点（要件全件の網羅／アーキテクチャ整合性／データモデル・スキーマ詳細／API 接合面の具体化／アルゴリズム＋性能達成手段／失敗モード処理＋観測性／セキュリティ・プライバシーの具体化／依存選定／テスト戦略／移行戦略）を網羅実施。19 件の所見（ERROR 3／WARN 12／INFO 4）を提示。

主役所見の主要発見：

- F-003（ERROR）：verdict 語彙が design.md（OK／WARN／BLOCK）と正本 WORKFLOW_PRECHECK.md（OK／WARN／DEVIATION）で不一致
- F-006（ERROR）：review-wave 段の `{phase}` テンプレート変数の展開ルール未定義
- F-009（ERROR）：commit／push サブコマンドの `--rationale` 必須引数が design.md の表で「引数なし」と誤記
- F-001／F-002／F-004／F-005／F-007／F-008／F-010〜F-014／F-017（WARN）：各観点の精緻化対象
- F-015／F-016／F-018／F-019（INFO）：軽微な改善余地

主役所見の詳細はサブエージェント出力（本セッション内のメッセージ履歴）を参照。

---

## 2. 敵対役レビュー（adversarial、Opus 4.7）

### 2.1 主役所見への反論・同意（19 件）

敵対役は主役 19 件のすべてに対し 3 値判定（counter_evidence_raised／no_counter_evidence_after_challenge／not_assessed）を付与：

- `counter_evidence_raised`：0 件
- `no_counter_evidence_after_challenge`：17 件
- `not_assessed`：2 件（F-005／F-007、判定材料が不足するため判定役に委ねる）

主役 19 件いずれにも反証は得られず、severity 維持。

### 2.2 独立発見（12 件、A-001〜A-012）

敵対役は強制的差異化（forced-divergence、計画書 §5.15.5）の精神で独立発見 12 件（ERROR 4／WARN 6／INFO 2）を提示。主な独立発見：

- A-001（ERROR、横断）：`feature-dependency.yaml` の `phase_order` に self-improvement が含まれるが、計画書 §5.5 行 376〜383 の `phase_order` には self-improvement が欠落、整合矛盾
- A-002（ERROR、横断）：trigger_map の `actor` フィールドが「llm」固定だが、計画書 §5.6 では段ごと多様、Req 5 受入 3〜4 の機械強制が成立しない疑い
- A-003（ERROR、横断）：完成判定条件 1 で 9 ファイル配置を要求するが、現リポジトリには 2 件しか存在せず、設計が現状到達点を可視化していない
- A-004（ERROR、横断）：`depends_on` の連想配列構造のパース仕様と判定述語が完全欠落
- A-005／A-006／A-007／A-008／A-009／A-010（WARN）：規律ファイル本体の所有関係／削減した素材機構の代替先未明示／規律ファイル実体配置の不一致／in-progress 複数並存時の判定不在／フェーズ移行ゲートの機能数／front-matter の hash 機構と削減方針の矛盾
- A-011／A-012（INFO）：要件追跡表の冗長記載／本機能自身の自己言及性

敵対役所見の詳細はサブエージェント出力（本セッション内のメッセージ履歴）を参照。

---

## 3. 判定役レビュー（judgment、Opus 4.7）

### 3.1 各所見への判定（31 件）

判定役は主役 19 件＋敵対役独立発見 12 件＝計 31 件のすべてについて、judgment（must-fix／should-fix／leave-as-is）と waterfall_class（機能内対処／波及／遡及／延期／leave-as-is）を判定。

### 3.2 severity 再評定

敵対役の判定を受けた severity の再評定では、severity 値の数値変更はなし。F-010 のみ「judgment を must-fix に上げる」処置（severity は WARN 維持で must-fix に紐付け）。

### 3.3 judgment の分布

| judgment | 件数 | 内訳 |
|---|---|---|
| **must-fix** | **10 件** | F-003、F-006、F-009、F-010、F-016、A-001、A-002、A-004、A-007、A-009 |
| **should-fix** | **17 件** | F-001、F-002、F-004、F-005、F-007、F-008、F-011、F-012、F-013、F-014、F-015、F-017、F-019、A-003、A-006、A-008、A-010 |
| **leave-as-is** | **4 件** | F-018、A-005、A-011、A-012 |
| **合計** | **31 件** | |

### 3.4 waterfall_class の分布

| waterfall_class | 件数 | 内訳 |
|---|---|---|
| **機能内対処** | **22 件** | F-001、F-002、F-003、F-004、F-005、F-006、F-007、F-008、F-009、F-010、F-011、F-012、F-013、F-016、F-017、F-019、A-001、A-002、A-004、A-006、A-008、A-009、A-010（A-012 は leave-as-is に算入） |
| **波及** | **0 件** | — |
| **遡及** | **1 件** | A-007（規律ファイル所有先パスと実体配置の不一致、要件側 Boundary Context 隣接期待の修正または規律ファイル実体の移送方針確定を要する） |
| **延期** | **4 件** | F-014、F-015、F-018、A-003 |
| **leave-as-is** | **3 件** | A-005（敵対役の誤読、要件側に既に明示済み）、A-011（複数参照は適切）、A-012（適用対象は §下流仕様への影響で明示済み） |
| **合計** | **30 件** | （A-012 を leave-as-is に算入したため 31 件のうち 1 件二重カウント回避） |

---

## 4. 統合（integration）

### 4.1 must-fix 10 件の対処方針と利用者承認の出典

運営ガイド §3.3 (a-1) 規律（must-fix 議論義務）に従い、must-fix 10 件を 7 グループに分けて 1 件ずつ深掘り議論。各グループで「経緯」「複数候補案」「各案の利点と弱点」「後段で発生し得る問題の深掘り」「推奨案と根拠」を平易な日本語で提示し、利用者明示承認を得てから反映。

| グループ | 所見 | 対処方針 | 利用者承認発言 |
|---|---|---|---|
| G1 | F-003 | verdict 語彙 BLOCK → DEVIATION 統一（案 ア、完全削除） | 「案 ア」（2026-05-25 セッション 26） |
| G2 | F-006 | テンプレート変数の展開規則明示（案 ア＋方針候補 α：`{phase}` は `process_id` から、`{日付}` は辞書順最大） | 「提案どおり」（2026-05-25 セッション 26） |
| G3 | F-009＋F-010 | commit／push の `--rationale` 必須化、参照節番号 §7.3 → §7.2 訂正（案 ア、両所見完全対処） | 「案 ア」（2026-05-25 セッション 26） |
| G4 | F-016 | 「fook」→「フック」タイポ修正（案 ア、表記統一） | 「案 ア」（2026-05-25 セッション 26） |
| G5 | A-001＋A-009 | `phase_order` 7 機能採用の根拠注記、「全 N 機能」を `feature-dependency.yaml#phase_order` 参照に変更（案 ア＋追跡先は本設計の注記と TODO で代用） | 「案 ア、追跡先も提案どおり」（2026-05-25 セッション 26） |
| G6 | A-002 | trigger_map の `actor` 値域を動的解決に修正（案 ア、`actor_resolution: per_target_stage` 追加） | 「案 ア」（2026-05-25 セッション 26） |
| G7 | A-004 | `depends_on` 連想配列構造のパース仕様と判定述語追加（案 ア、`hard`／`review` 意味確定） | 「案 ア」（2026-05-25 セッション 26） |
| G8 | A-007 | 規律ファイル本体を memory から `docs/disciplines/` へ軽量手続きで移管（active 必読 12＋参照層 5＝17 件） | 「推奨セット（案 b＋案 X＋案 P＋案 1）」「推奨案（参照層 5 件追加移送）」（2026-05-25 セッション 26） |

G8 は当初「a 種（auto memory）／b 種（運営ガイド）／c 種（disciplines）の 3 種区別」案 ア' を提示したが、利用者指摘「形式だけ見て判断していないか？内容を精査」を受けて精査した結果、memory ファイルの多くが ReviewCompass プロジェクト固有の規律本体を含んでいることが判明（参照だけではなかった）。判定を撤回し、利用者提案の「軽量手続きによる移送」で全 17 件を repo に集約する方針を再策定して合意。

### 4.2 反映箇所一覧（design.md、機能内対処 9 件＋遡及 1 件）

| グループ | 反映箇所 |
|---|---|
| G1 | §全体構造 Mermaid 図／§軽量版検査スクリプトモデル §2／§変更意図、4 か所 |
| G2 | §段集合の静的列挙モデル §2 末尾に「テンプレート変数の展開規則」新節 |
| G3 | §軽量版検査スクリプトモデル §2 のサブコマンド表と出力形式説明 |
| G4 | §多層防御の位置付けモデル §3、1 か所 |
| G5 | §機能依存マップモデル §2 直下に注記、§不可逆操作の直前ゲートモデル §1 表のフェーズ移行行を参照化 |
| G6 | §reopen 機械強制モデル §2 の trigger_map YAML 例の `actor` 行とその後の説明文 |
| G7 | §軽量版検査スクリプトモデル §3 の述語集合表に `depends_on_resolves_correctly` 追加、§機能依存マップモデル §6 新節 |
| G8 | §責務境界の明確化の表（規律ファイル本体／auto memory 索引／提案権の 3 行）、§変更意図、requirements.md §Boundary Context 隣接期待 |

design.md の行数変化：起草時 806 行 → 反映後 884 行（+78 行）。

### 4.3 規律ファイル軽量移送の実施（G8 対処）

G8 の対処として、`docs/disciplines/` への規律ファイル移送を本セッションで実施（独立コミット `b830785`）：

- **新規配置 18 件**：規律 17 件（active 必読 12＋参照層 5）＋ README.md
- **memory 側の置換**：17 件すべて短い参照索引（14 行）に置換、本体は repo を Read で参照する設計
- **整理作業**：front-matter 統一形式に正規化、`node_type: memory`／`originSessionId` を全 17 件から削除、旧名リンク 4 か所を新名に修正、`plain_japanese` と参照層 5 件の旧形式を整理
- **MEMORY.md 更新**：移管通知を 17 件全体に拡張、参照層 5 件の本体パスを併記
- **archive 14 件**：memory 側に残存（過去履歴の保全、移送対象外）

移送は軽量手続き（過去 3 回の memory 整理と同じパターン：明示承認＋文書化＋ archive 退避）で実施。本来は workflow-management の所定手続きが整備された後に通すべきだが、design 段で構造的に必要な前倒し対処として利用者明示承認を経て実施。

### 4.4 should-fix 17 件と延期 4 件の処理状況

- **should-fix 17 件**：本セッションでは反映せず、継続課題として記録のみ。判定役は「少なくとも 5 件（F-001／F-004／F-011／A-006／A-010）は設計の自己完結性に関わるため反映が望ましい」と推奨。次セッション以降または design レビュー波段で個別判断
- **延期 4 件**：design.md §先送り論点に既に記載済み（F-014／F-015／F-018／A-003）。フェーズ 2 以降または該当時期に判断

### 4.5 波及所見の処理

- **波及（同フェーズ・他機能への影響）**：0 件（判定役は波及該当所見なしと判定）
- **遡及（A-007）**：本セッション内で「軽量手続き経由の移送」として吸収（再オープン手続きを正式起動せず、過去 A-010 と同型の軽量対処）

### 4.6 関連参照

- design.md：`.reviewcompass/specs/workflow-management/design.md`（884 行、本セッション 26 で起草＋ must-fix 反映）
- requirements.md：`.reviewcompass/specs/workflow-management/requirements.md`（A-007 対処として §Boundary Context 隣接期待の `docs/disciplines/discipline_*.md` 記述を移管反映に更新）
- 規律ファイル移送先：`docs/disciplines/`（17 件＋ README.md、コミット `b830785`）
- 持ち越し所見：`.reviewcompass/pending-cross-feature-findings.md`（A-011 が未消化、design レビュー波段で消化予定、本機能の責務範囲外）
- 計画書 §5.5（`phase_order` 構造例）：A-001 の注記で「self-improvement が記載漏れ」と明示、計画書側の補正は別途追跡（本機能の責務範囲外）
- 補助層 C 段階 2 仕様：`docs/operations/WORKFLOW_PRECHECK.md`（verdict 語彙 OK／WARN／DEVIATION、サブコマンド `spec-set`／`commit`／`push` の引数、出力形式 §7.2／§7.3 の正本参照）

### 4.7 利用者議論で判明した重要事項（後段への引き継ぎ）

- **過去 3 回の memory 整理が形式的所定手続きを通らずに実施されていた**（セッション 22／セッション 24／セッション 24 末）。各回とも利用者明示承認＋文書化＋ archive 退避で軽量手続きとして機能していた。本セッション 26 の移送も同じ軽量手続きとして位置付け、本機能の所定手続きが整備されるまでの暫定運用とする
- **`memory/feedback_*.md` の多くが Claude Code 製品機能ではなく ReviewCompass プロジェクト固有の規律本体を含んでいた**。形式（配置場所と front-matter）だけで「製品機能のインデックス」と早急に判定した当初の主役レビューと敵対役レビューに認識ずれがあった。利用者指摘「形式だけ見て判断していないか？内容を精査」を契機に精査し、判定を撤回。今後のレビューでは内容精査を形式判断より優先する
- **本機能の所定手続きの段集合（規律変更を `drafting → review → approval` の 3 段で扱うか triad-review を含むか）**：先送り論点 6 として明示、self-improvement の design 段着手前までに確定する必要
