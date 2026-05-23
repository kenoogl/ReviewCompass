# spec.json の正本スキーマ設計メモ

最終更新：2026-05-23（セッション 20 中盤、議論結果の凍結）
種別：設計メモ（計画書改定の入力として作成）
位置付け：本文書は **第 1 段階の成果物** であり、第 2 段階（計画書改定）、第 3 段階（雛形配置 ＋ 7 機能配置）の入力となる

## 1. 経緯と目的

### 1.1 経緯

セッション 20 の冒頭、TODO_NEXT_SESSION.md §2.3 の後追い作業 2 件（foundation 用 spec.json 作成、F-004 全面置換）を消化中に、次の方針未整備が判明した：

- ReviewCompass 内に spec.json は foundation 用 1 件のみ（他 6 機能には未配置）
- spec.json の雛形ファイルが存在しない（`templates/specs/` も未配置）
- phase 値の正本語彙が計画書に未定義（利用者ご指摘：「approved=false なのに requirements-completed は不整合」）
- `stages/` ディレクトリ自体が ReviewCompass にまだ存在しない（計画書 §5.5 で定義されているが未配置、フェーズ 2 で配置予定）

dogfeeding（自己適用検証）プロセスの抜け漏れチェックとして、spec.json の正本仕様を計画書から逆算する形で設計し直すことになった。

### 1.2 目的

本文書は次を確定する：

- spec.json の役割（計画書の二重構造に基づく単一責任の定義）
- 機能単位 spec.json のフィールド構造と値リスト
- 命名整理（曖昧な名前の解消）
- 計画書改定の影響範囲
- 次セッション以降の作業計画

## 2. 計画書の二重構造の確認

計画書 §5.4〜§5.9 を再読した結果、ワークフロー管理は **二重構造** で設計されていることを確認した。

### 2.1 構造 A：ワークフロー自体の管理（§5.4〜§5.8）

「**今どのフェーズの、どの段にいるか**」を管理する仕組み。

- §5.4：軽量化方針（思想は継承、実装は 1／10）
- §5.5：所定手続きの階層構造（intent／feature-partitioning／requirements／design／tasks／implementation の 6 フェーズ × 各フェーズの段集合）
- §5.6：reopen 手続きの機械強制（手戻り種別・連鎖再実施・trigger_map）
- §5.7：session 跨ぎ時の状態管理（in-progress ファイル）
- §5.8：多層防御の必要性と段階的導入

管理する情報：

- どの段が完了したか
- 利用者承認の状況
- reopen の履歴
- 上流変更による下流再検査要否（recheck）
- 不可逆操作（commit／push／フェーズ移行）の可否

### 2.2 構造 B：各フェーズでのレビュープロセスの管理（§5.9）

「**ある段でレビューを実施するときに、どんな所見を、誰が、どう記録するか**」を管理する仕組み。

- §5.9.1：基本構造（3 役 ＋ モデル多様化 ＋ ファイル遮断）
- §5.9.2：観点と重大度の統一
- §5.9.3：所見メタデータの必須化と機械検査
- §5.9.4：形骸化規律の取り下げ
- §5.9.5：workflow 層 self-improvement
- §5.9.6：3 方式比較データの取得
- §5.9.7：API 経路と障害対応
- §5.9.8：コスト最適化
- §5.9.9：段階的導入

管理する情報：

- 所見メタデータ（severity／judgment／depth／evidence_type／verifying_commands）
- 3 役メタデータ（provider／model／model_full_id／prompt_artifact_hash）
- 観点別の所見
- mode（manual_dogfooding／subagent_mediated／runtime_mediated）
- 3 方式比較データ（findings_by_method）
- 持ち越し所見

### 2.3 管理場所の責任分担

| 構造 | 管理対象 | 管理場所 |
|---|---|---|
| 構造 A | ワークフロー自体（段の状態、reopen、recheck） | spec.json（機能単位）／ stages/\*.yaml（機能横断、フェーズ 2 で配置） |
| 構造 B | レビュープロセス（所見、3 役、mode、観点） | レビュー記録（reviews/*.md）の front-matter と本文 |

## 3. spec.json の役割定義

**spec.json は機能単位の構造 A（ワークフロー管理）を担う**。それ以外（構造 B、機能横断段）は別の場所に書く。

この単一責任の定義に従い、次は spec.json に **含めない**：

- レビュー所見の管理（pending_findings 等） → レビュー記録の責務
- レビュー経路（dogfooding_mode 等） → レビュー記録の責務
- 機能分離証跡（traceability、intent_requirements_matrix 等） → 機能横断 yaml と `stages/feature-partitioning/<日付>-proposal.md` の責務
- フェーズ横断の review-wave／alignment-gate の機能横断段の状態 → `stages/<フェーズ>.yaml` の責務

## 4. 機能単位 spec.json の設計

### 4.1 フィールド一覧

| フィールド | 由来 | 内容 |
|---|---|---|
| `feature_name` | §3.1 feature-dependency.yaml の features キーと一致 | 機能識別 |
| `language` | 素材継承（既定 `ja`） | 仕様文書の言語 |
| `created_at`／`updated_at` | 素材継承 | 履歴管理 |
| `current_phase` | 計画書改定で定義（要約値） | 現在の到達点を一瞥用に示す |
| `workflow_state` | 計画書改定で定義（詳細状態） | 4 フェーズ × 3 段の段別状態 |
| `reopened` | §5.6 | reopen 履歴と手戻り種別 |
| `recheck` | §5.6 | 上流変更による下流再検査要否 |

### 4.2 段の構造（案 Z ＋ 方向 B 採用）

機能単位 spec.json では各フェーズに **3 段** を持つ：

| 段 | actor | 内容 |
|---|---|---|
| drafting | llm（または human） | 機能単位の草案作成 |
| aligned | llm | LLM 自動判定による整合確認の通過記録（機能横断 yaml の判定結果を反映） |
| approved | human または proxy_model | 人間または別モデル（§5.12 人間代役機構）による承認 |

review-wave 段は機能単位 spec.json には **含めない**（機能横断 yaml に任せる）。理由は review-wave が「全機能の drafting がすべて完了してから始まる横断段」で、機能単位で個別に通過状態を持つ意味が薄いため。

### 4.3 各段の状態値

| 段 | 取り得る値 |
|---|---|
| drafting | `not_started` ／ `in_progress` ／ `completed` |
| aligned | `not_yet` ／ `passed` ／ `failed` |
| approved | `pending` ／ `approved` ／ `rejected` |

### 4.4 current_phase の値リスト

`current_phase` は要約値として、現在のフェーズと段の組合せを 1 つの文字列で示す：

- `requirements-drafting`（要件段の drafting 中）
- `requirements-aligned`（要件段の aligned 通過、approved 未）
- `requirements-approved`（要件段の approved 完了）
- `design-drafting` ／ `design-aligned` ／ `design-approved`
- `tasks-drafting` ／ `tasks-aligned` ／ `tasks-approved`
- `implementation-drafting` ／ `implementation-aligned` ／ `implementation-approved`

12 値 ＋ 未着手の特別値（例：`not_started`）。`current_phase` は `workflow_state` の詳細から計算可能な要約値で、人間が spec.json を一瞥した時の可読性のために保持する。

### 4.5 構造案

```yaml
feature_name: foundation
language: ja
created_at: 2026-05-23T00:00:00+09:00
updated_at: 2026-05-23T00:00:00+09:00
current_phase: requirements-aligned    # 一瞥用の要約値
workflow_state:                        # 機械検査用の詳細
  requirements:
    drafting: completed
    aligned: passed
    approved: pending
  design:
    drafting: not_started
    aligned: not_yet
    approved: pending
  tasks:
    drafting: not_started
    aligned: not_yet
    approved: pending
  implementation:
    drafting: not_started
    aligned: not_yet
    approved: pending
reopened:
  requirements: false
  design: false
  tasks: false
  implementation: false
recheck:
  upstream_change_pending: false
  impacted_downstream_phases: []
```

### 4.6 命名整理の根拠

- `phase` と `phases` を英語の単複だけで区別するのは日本語の文脈で不明瞭
- `current_phase`（現在のフェーズ）と `workflow_state`（ワークフロー状態）に改名
- `workflow_state` は計画書 §5.4 のワークフロー管理という概念に直結
- 修飾語「current_」で要約値であることを示す

### 4.7 同期問題の運用方針

`current_phase`（要約）と `workflow_state`（詳細）は同じ事実を別の粒度で表すため、不整合の余地が残る：

- **フェーズ 1（現在）**：手動編集。利用者または LLM が `workflow_state` を更新したとき、`current_phase` も合わせて更新する規律
- **フェーズ 3（スタブ）以降**：`reviewcompass status` コマンドが `workflow_state` から `current_phase` を計算し、不整合があれば警告（fail-closed）
- **機械検査**：`workflow_state` を正本、`current_phase` を要約として扱い、両者の整合を計算で検査

## 5. 確定した論点（議論経緯）

セッション 20 の議論で確定した 7 論点：

| 論点 | 確定内容 | 根拠 |
|---|---|---|
| 論点 1：含めるフェーズ範囲 | **4 階層**（requirements／design／tasks／implementation）。intent と feature-partitioning は機能横断なので機能単位 spec.json には含めない | 単一責任原則と機能横断の責任分担 |
| 論点 2：phases 構造 と approvals の関係 | **phases に統合（approvals 廃止）**。後に `workflow_state` に改名 | クリーンスレート方針と命名一致 |
| 論点 3：phase 値の粒度 | **3 段（drafting／aligned／approved）の組合せ**、計 12 値。要約値として `current_phase` に保持 | 一瞥可能性と詳細との整合 |
| 論点 4：dogfooding_mode | **spec.json から削除**（レビュー記録の front-matter のみで管理） | 構造 B（レビュープロセス管理）の責務 |
| 論点 5：pending_findings | **spec.json から削除**（レビュー記録のみで管理） | 構造 B の責務 |
| 論点 6：traceability | **spec.json から削除**。機能分離証跡は `stages/feature-partitioning/<日付>-proposal.md` として artifacts で残す | 機能横断の責務 |
| 論点 7：recheck／reopen | **spec.json に保持** | §5.6 と直接対応する構造 A の中核 |

## 6. 計画書改定の影響範囲（方向 B：大幅変更）

利用者の選択は **方向 B（大幅変更：段を分割）**。理由は「将来の別モデル承認（§5.12 人間代役機構）との連動を視野に入れたとき、aligned と approved を別段として明示するほうが拡張しやすい」ため。

### 6.1 §5.5 の改定

requirements 以降のフェーズの段集合を変更：

- **改定前**：drafting / review-wave / alignment-gate（3 段）
- **改定後**：drafting / review-wave / aligned / approved（4 段、alignment-gate を 2 段に分割）

alignment-gate の actor=llm／human 混在を解体：

- aligned：actor=llm（自動判定）
- approved：actor=human または proxy_model（人間または別モデルの承認）

機能単位 spec.json では review-wave を除く 3 段（drafting / aligned / approved）を保持する旨を §5.5 に明記。

### 6.2 §5.6 の trigger_map 改定

reopen 時の再実施段マップで alignment-gate を参照していた箇所をすべて aligned と approved の組合せに置換。

例：

```
# 改定前
I-2:
  - stages/design.yaml#alignment-gate
  - stages/tasks.yaml#alignment-gate
  - stages/implementation.yaml#alignment-gate

# 改定後
I-2:
  - stages/design.yaml#aligned
  - stages/design.yaml#approved
  - stages/tasks.yaml#aligned
  - stages/tasks.yaml#approved
  - stages/implementation.yaml#aligned
  - stages/implementation.yaml#approved
```

trigger_map の全エントリ（I 起点／A 起点／D 起点／R 起点／N 起点）に同様の置換が必要。

### 6.3 §5.12 との連動を明記

approved 段の actor として `proxy_model` を含むことを §5.5 と §5.12 の両方で明記。§5.12 の代行可能／本人必須の線引きルールに「approved 段の代行可否」を含める。

### 6.4 §5.24 新節の追加

spec.json の正本スキーマを §5.24「spec.json の正本スキーマ」として新設：

- §5.24.1：spec.json の役割と単一責任（構造 A の機能単位管理）
- §5.24.2：フィールド一覧と意味
- §5.24.3：段の構造と状態値の正本
- §5.24.4：current_phase の値リスト
- §5.24.5：構造例
- §5.24.6：同期問題の運用方針
- §5.24.7：他の管理場所との責任分担（レビュー記録、stages/*.yaml）

### 6.5 その他の改定

- §5.7、§5.8 など alignment-gate が登場する箇所を見直し、aligned と approved の 2 段に分けて記述
- §5.20（抽出対応表の雛形）に spec.json 配置の項目を追加

## 7. 作業計画

### 7.1 第 1 段階（本セッションで完了）

- 本設計メモ（`docs/design/spec-json-schema-design.md`）を作成
- 利用者承認後にコミット（commit のみ、push は利用者明示承認必須）

### 7.2 第 2 段階（次セッション以降）

- 計画書 §5.5、§5.6、§5.12、§5.24（新設）、§5.7、§5.8、§5.20 の改定
- 1 節ずつ改定文案を提示 → 利用者承認 → 反映の手順
- 全節改定後にコミット

### 7.3 第 3 段階（第 2 段階完了後）

- spec.json 雛形を `templates/specs/spec.json.template` に配置
- 現在の foundation/spec.json を雛形に合わせて改訂（pending_findings 削除、traceability 削除、approvals → workflow_state へ変換、命名整理を反映）
- 他 6 機能（runtime／evaluation／analysis／workflow-management／self-improvement／conformance-evaluation）に spec.json を配置
- 各機能の現状（requirements-aligned 等）を反映
- 全機能配置後にコミット

## 8. 現状の foundation/spec.json との差分

セッション 20 序盤で作成した foundation/spec.json は本設計に整合していない。第 3 段階で次の修正が必要：

- `phase`：`requirements-completed`（造語）→ `requirements-aligned`（正本値）に修正、フィールド名を `current_phase` に改名
- `approvals` フィールド全体 → `workflow_state` に置換、各段の状態値を正本（drafting／aligned／approved）に変更
- `custom.alignment` → `workflow_state` の各段の status と統合
- `custom.reopened` → 直接 `reopened` フィールドに昇格
- `custom.recheck` → 直接 `recheck` フィールドに昇格
- `custom.traceability` → 削除（機能分離証跡は stages/feature-partitioning/ で管理）
- `custom.pending_findings` → 削除（F-004 はレビュー記録に既記録）

## 9. 関連参照

- 計画書：`docs/plan/reconstruction-plan-2026-05-21.md` §5.4〜§5.9、§5.12、§5.23、§5.23.12
- 現状の foundation/spec.json：`.reviewcompass/specs/foundation/spec.json`
- 素材リポジトリの spec.json：`/Users/Daily/Development/Rwiki-v2-code-mod/dual-reviewer-rebuild/.kiro/specs/dual-reviewer-foundation/spec.json`
- セッション運営ガイドライン：`docs/operations/SESSION_WORKFLOW_GUIDE.md`
- TODO：`TODO_NEXT_SESSION.md`

## 10. 改訂規律

- 本設計メモは第 2 段階の計画書改定が完了した時点で **役目を終える**（計画書 §5.24 が正本になるため、本メモは過去の議論経緯の記録として `docs/archive/design/` に退避する候補）
- 第 2 段階の作業中に設計の見直しが必要になった場合、本メモを更新したうえで計画書改定に反映する
- 本メモは設計の **議論経緯の凍結** であり、計画書とは別の責務を持つ（議論の出典としての記録）
