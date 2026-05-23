# spec.json の正本スキーマ設計メモ

最終更新：2026-05-23（セッション 21、論点 1 の 6 階層復元・用語訂正・段集合の 5 段化を反映）
種別：設計メモ（計画書改定の入力として作成）
位置付け：本文書は **第 1 段階の成果物** であり、第 2 段階（計画書改定）、第 3 段階（雛形配置 ＋ 7 機能配置）の入力となる

## 0. 撤回・修正履歴（2026-05-23、セッション 21）

セッション 20 末でコミットした本設計メモには、利用者明示承認を経ない記述が含まれていた。セッション 21 でこれを発見し、次の撤回・修正を適用した（履歴上のラベル番号は併記、内容で参照する）：

- **論点 1 の 6 階層保持への復元（履歴上は撤回 #1）**：論点 1 を「4 階層」と記載していた箇所を、利用者明示承認である「6 階層保持」（セッション 20 ログ line 979、AskUserQuestion での明示選択 2026-05-22）に戻す。論点 1 と論点 6（証跡を artifacts へ）の整合性問題は未解決として保留
- **機能単位 spec.json の段数を機能横断段と揃える方針（履歴上は撤回 #4）**：機能単位 spec.json の段数を 3 段と記載していた箇所を 4 段（drafting／review-wave／alignment／approval、当時は過去分詞 aligned／approved で表記）に変更（利用者明示承認 2026-05-23）。review-wave 段の機能単位側の状態を追跡する必要性により
- **drafting と local-review の責務分離による 5 段化（履歴上は修正 #5）**：drafting 段に内部 local review（局所レビュー）を含めるか別段に分離するかの曖昧さに対し、5 段化（drafting／local-review／review-wave／alignment／approval）を採用（責務分離を優先、利用者明示承認 2026-05-23）。drafting 段は草案作成のみ、local-review 段は 3 役レビュー（主役・敵対役・判定役）と機能内対処の実施段として分離。誰が何をしたかを段単位で明確に記録する
- 用語「遡及／波及」の二軸的定義への訂正（履歴上は撤回 #2）と運営ガイドラインの段集合記述訂正（履歴上は撤回 #3）は本設計メモ外（`SESSION_WORKFLOW_GUIDE.md` ／ `pending-cross-feature-findings.md`）で対応
- **current_phase をフィールドから計算値に変更する再確定**（2026-05-23 セッション 21 利用者明示承認、再オープン手順を踏んで実施）：旧確定（セッション 20 line 2110〜2165、`current_phase` を書く ＋ 運用規律で同期）から、`current_phase` を書かず `workflow_state` から計算で求める方針に変更。理由は「ワークフロー実行全般が持つ同根問題」（LLM が記録動作を確実に実行できない）に対し、嘘の近道（古い current_phase を信じる失敗モード）を構造的に消すため。補助規律 1 件（workflow_state を唯一の真実源として扱う、読む側／書く側を一体規律化）を memory に追加して併用する
- **段ラベルを名詞統一**（2026-05-23 セッション 21 利用者明示承認）：旧表記「aligned」「approved」（過去分詞）を「alignment」「approval」（名詞、活動名）に統一。全段名が活動名で揃い、揺らぎが消える。計画書 §5.5 の既存の名詞型表記（drafting／review／approval／candidate-proposal／local-review／review-wave）と整合

本撤回の根本原因は、セッション 20 で論点 1 を再オープンする際に、利用者の「議論継続指示」「計画書再読指示」「命名指摘」を **黙示の同意** と誤解し、明示承認なしで設計メモに「4 階層 確定」と書き込んだこと。セッション 21 で再発防止策（確定事項表に承認出典必須、黙示承認の不採用、再オープン手順の明文化、集計局面の自己検査チェックリスト、セッション開始時の引継ぎ規律）を memory に追加する。

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

## 2. 計画書の二重構造（ワークフロー管理とレビュープロセス管理）

計画書 §5.4〜§5.9 を再読した結果、ワークフロー管理は **二重構造** で設計されていることを確認した。

### 2.1 ワークフロー管理（§5.4〜§5.8）

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

### 2.2 レビュープロセス管理（§5.9）

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

| 種別 | 管理対象 | 管理場所 |
|---|---|---|
| ワークフロー管理 | ワークフロー自体（段の状態、reopen、recheck） | spec.json（機能単位）／ stages/\*.yaml（機能横断、フェーズ 2 で配置） |
| レビュープロセス管理 | レビュープロセス（所見、3 役、mode、観点） | レビュー記録（reviews/*.md）の front-matter と本文 |

## 3. spec.json の役割定義

**spec.json は機能単位のワークフロー管理を担う**。それ以外（レビュープロセス管理、機能横断段）は別の場所に書く。

この単一責任の定義に従い、次は spec.json に **含めない**：

- レビュー所見の管理（pending_findings 等） → レビュー記録の責務
- レビュー経路（dogfooding_mode 等） → レビュー記録の責務
- 機能分離証跡（traceability、intent_requirements_matrix 等） → 機能横断 yaml と `stages/feature-partitioning/<日付>-proposal.md` の責務
- 機能横断段の **機能横断側** の状態（波全体の進行、対象機能集合の到達状況） → `stages/<フェーズ>.yaml` の責務（機能単位 spec.json は **当該機能の個別状態** だけを保持、機能単位と機能横断の責任分担）

## 4. 機能単位 spec.json の設計

### 4.0 設計原則：最小単純優先（2026-05-23 利用者明示承認）

spec.json に書く情報は **最小** にし、構造は **単純** にする。これは次の認識を踏まえた選択：

- ワークフロー記録（spec.json の各フィールド更新、別ファイル作成、trigger_map 参照等）は LLM の判断と実行に依存する
- LLM が文脈圧力下で規律違反を起こす失敗モードが実証されている（セッション 20 で論点 1 が利用者明示承認なく一方的に変更された事例）
- 計画書 §5.8 は「100% の規律遵守は原理的に不可能、多層防御で実効遵守率を上げる」と明文化
- 第 1 層（仕様検査）の段階で複雑な構造を持たせても、書き忘れの余地が増えるだけで、根本的な脆さは解消されない

これは **ワークフロー実行全般が持つ同根問題**（LLM が記録動作を確実に実行できない）に対する設計上の応答である。仕様設計でできるのは **失敗の検出を容易にすること** までで、**実行の信頼性自体は別の層**（利用者監査・git フック・定期事後監査等）に依存する。

最小単純優先の具体的な適用：

1. **各段の値は true／false のみ**：多値型（completed／pending／failed 等）は採用しない
2. **in_progress フィールドは持たない**：「フェーズが進行中か」は各段の値から計算で求める（書く情報の重複を避ける）
3. **current_phase フィールドは持たない**：「今どこか」の要約値も `workflow_state` から計算で求める。要約値を別フィールドとして書くと、LLM が要約値だけ見て進行する **嘘の近道** が生まれ、古い要約値を信じて誤った進行をする失敗モードに弱くなる。フィールド自体を持たないことで、状態を知りたい主体は **`workflow_state` を読むしか選択肢がない**（嘘の近道を構造的に消す）
4. **reopened は最小構造**：詳細（日付、種別、根拠）は別ファイル `docs/reviews/reopen-classification-<日付>.md` に書き、spec.json には起きたかの真偽値のみ
5. **詳細記述は別ファイル**：spec.json は要約、詳細は別ファイル（既存方針 §5.6 と整合）

検出と人手は他の層に任せる：

- 第 1 層（仕様検査）：spec.json の整合性検査（例：current_phase と workflow_state の不整合検出）
- 第 3 層（利用者監査、フェーズ 1 では手動）：全件確認、規律違反の発見
- 仕様設計の複雑化で書き忘れを防ごうとしないことが、本原則の本質

### 4.1 フィールド一覧

| フィールド | 由来 | 内容 |
|---|---|---|
| `feature_name` | §3.1 feature-dependency.yaml の features キーと一致 | 機能識別 |
| `language` | 素材継承（既定 `ja`） | 仕様文書の言語 |
| `created_at`／`updated_at` | 素材継承 | 履歴管理 |
| `workflow_state` | 計画書改定で定義（詳細状態） | 4 フェーズ × 5 段の段別状態（責務分離による 5 段化、2026-05-23）。各段は true／false |
| `reopened` | §5.6 | reopen 履歴と手戻り種別 |
| `recheck` | §5.6 | 上流変更による下流再検査要否 |

`current_phase` フィールドは持たない（§4.0 設計原則）。「今どこか」の要約は `workflow_state` から計算で求める（§4.4 計算式参照）。

### 4.2 段の構造（責務分離による 5 段化、2026-05-23 利用者明示承認）

機能単位 spec.json では requirements 以降の各フェーズに **5 段** を持つ：

| 段 | actor | 内容 |
|---|---|---|
| drafting | llm（または human） | 機能単位の草案作成のみ。レビューは含まない |
| local-review | llm | 機能内の 3 役レビュー（主役・敵対役・判定役）と機能内対処の実施。サブエージェント方式の場合は mode=`subagent_mediated` |
| review-wave | llm | 機能横断レビュー波における当該機能の所見対応状況（機能単位の側面） |
| alignment | llm | LLM 自動判定による整合確認の活動 |
| approval | human または proxy_model | 人間または別モデル（§5.12 人間代役機構）による承認の活動 |

drafting 段と local-review 段は分離する（責務分離を優先、誰が何をしたかを段単位で明確に記録するため）。drafting は草案作成のみ、local-review は 3 役レビューと機能内対処の実施。

review-wave 段は機能横断段だが、各機能には「自機能の所見が当該波で解消されたか」「未消化の所見があるか」という **機能単位の状態** が存在するため、機能単位 spec.json でも保持する。機能横断側の状態（波全体の進行、対象機能集合の到達状況）は `stages/<フェーズ>.yaml` で管理し、両者で **同じ波の異なる側面** を保持する。

intent と feature-partitioning は機能横断段のみで構成され、機能単位の進捗が概念として存在しない。論点 1（6 階層保持、利用者明示承認 2026-05-22）でどのように機能単位 spec.json に含まれるかは、論点 6（機能分離証跡を artifacts に分離）との **整合性問題として未解決**、6 階層復元後の議論事項として保留する。

### 4.3 各段の状態値（最小単純優先で true／false に統一、2026-05-23 利用者明示承認）

各段の値は **true（通過済み）** または **false（未通過）** のみ。

| 段 | 取り得る値 |
|---|---|
| drafting | `true` ／ `false` |
| local-review | `true` ／ `false` |
| review-wave | `true` ／ `false` |
| alignment | `true` ／ `false` |
| approval | `true` ／ `false` |

多値型（`not_started` ／ `in_progress` ／ `completed` 等）は採用しない（§4.0 設計原則）。失う情報は他の手段で表現する：

- **未着手 vs 進行中**：`stages/in-progress/` ディレクトリの存在で判別（計画書 §5.7、フェーズ 2 で配置予定）
- **失敗・却下**：`reopened` フィールドが履歴を残す（§4.6 参照）
- **所見の未消化**：`pending-cross-feature-findings.md` が機能横断で管理（spec.json では扱わない）

「現在このフェーズに取り組んでいるか」は **計算で求める**：当該フェーズの各段に 1 つでも false があれば「進行中」、全段が true なら「完了」、全段が false なら「未着手」。in_progress フィールドは持たない（書く情報の重複と矛盾の余地を避ける）。

### 4.4 current_phase の計算式（フィールドとしては保持しない）

`current_phase` は spec.json には書かない（§4.0 設計原則）。「今どこか」を知りたいときは `workflow_state` から計算で求める。

#### 計算の規則

1. `workflow_state` の各フェーズを依存順に走査（要件 → 設計 → タスク → 実装、intent と feature-partitioning は機能横断段で機能ごとには持たない／6 階層拡張は保留中）
2. 各フェーズの段（drafting／local-review／review-wave／alignment／approval）を順に走査
3. **最初に `false` が現れた段** を見つける
4. その段の名前が「現在地」を表す要約値となる
   - 例：`workflow_state.requirements.approval: false`（alignment まで true、approval だけ false）→ `current_phase = requirements-approval-pending` または `requirements-alignment-passed` のような形で「次に取り組むべき段」を示す
5. 全段が `true` のフェーズしかない場合 → 「completed」（全フェーズ完了）

#### 想定される要約値の語彙

20 種類の段識別子（5 段 × 4 フェーズ）＋ 未着手特別値。intent 段／feature-partitioning 段の current_phase 値はラベル統一の議論と 6 階層拡張の議論が保留中のため保留。

#### 計算は誰が行うか

- フェーズ 1〜2：人間（または LLM）が `workflow_state` を読んで頭の中で計算
- フェーズ 3 以降：`reviewcompass status` コマンドが計算で出力（計画書 §5.11.7）

#### 嘘の近道を作らない設計意図

`current_phase` をフィールドとして書くと、LLM が要約値だけ見て進行する **嘘の近道** が生まれる。古い要約値を信じて誤った進行をする失敗モード（同根問題）に弱くなる。フィールド自体を持たないことで、状態を知りたい主体は `workflow_state` を読むしか選択肢がなくなり、嘘の近道が構造的に消える。

ただし「`workflow_state` を読まずに憶測する」失敗モードは別途残るため、補助規律 [[workflow-state-single-truth-source]]（読む側：状態判定時は `workflow_state` を必ず読む、書く側：要約値を勝手に作らない、状態表現には根拠を併記）を memory で併用する。

### 4.5 構造案

```yaml
feature_name: foundation
language: ja
created_at: 2026-05-23T00:00:00+09:00
updated_at: 2026-05-23T00:00:00+09:00
# current_phase は持たない。今どこかは workflow_state から計算で求める（§4.4）
workflow_state:                        # 各段は true（通過済み）／ false（未通過）
  # intent／feature-partitioning は論点 1（6 階層保持）と論点 6（証跡を artifacts へ）
  # の整合性問題が未解決のため、本構造例では保留
  requirements:
    drafting: true
    local-review: true
    review-wave: true
    alignment: true
    approval: false
  design:
    drafting: false
    local-review: false
    review-wave: false
    alignment: false
    approval: false
  tasks:
    drafting: false
    local-review: false
    review-wave: false
    alignment: false
    approval: false
  implementation:
    drafting: false
    local-review: false
    review-wave: false
    alignment: false
    approval: false
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
- 詳細状態のフィールド名を `workflow_state`（ワークフロー状態）と命名
- `workflow_state` は計画書 §5.4 のワークフロー管理という概念に直結
- 要約値は **フィールドとして書かない**（§4.0 設計原則、嘘の近道を作らない）。「今どこか」を表現したいときは `workflow_state` から計算で求める（§4.4）

### 4.7 同期問題が起きない設計（2026-05-23 再確定）

要約値（旧 `current_phase`）を **書かないことで、不整合の余地そのものを消す**：

- spec.json に書く真実源は `workflow_state` の 1 ヶ所のみ（複数フィールドの同期問題が発生しない）
- 「今どこか」の要約は計算で求める（§4.4 計算式）
- フェーズ 1〜2：人間や LLM が `workflow_state` を読んで頭の中で計算
- フェーズ 3 以降：`reviewcompass status` コマンドが計算で出力（計画書 §5.11.7）
- 補助規律 [[workflow-state-single-truth-source]]：読む側（状態判定時は `workflow_state` を必ず読む）と書く側（要約値を勝手に作らない、状態表現には根拠を併記）を一体で規律化

旧設計（要約値を別フィールドとして書く ＋ 運用規律で同期）の同期問題は、再確定により **構造的に消滅**。

## 5. 確定した論点（議論経緯）

セッション 20 の議論で確定した 7 論点：

| 論点 | 確定内容 | 根拠 |
|---|---|---|
| 論点 1：含めるフェーズ範囲 | **6 階層保持**（intent／feature-partitioning／requirements／design／tasks／implementation）。論点 6 との整合性問題は未解決として保留 | 利用者明示承認 2026-05-22（セッション 20 line 979 で AskUserQuestion 明示選択） |
| 論点 2：phases 構造 と approvals の関係 | **phases に統合（approvals 廃止）**。後に `workflow_state` に改名 | クリーンスレート方針と命名一致 |
| 論点 3：phase 値の粒度 | **5 段の組合せ**（drafting／local-review／review-wave／alignment／approval、全段名を名詞統一）、各段は **true／false の 2 値**（最小単純優先、§4.0）。要約値 `current_phase` は **フィールドとして書かず、`workflow_state` から計算で求める**（再確定 2026-05-23、過去判断「current_phase を書く」から変更、§4.0 と §4.4 参照） | 責務分離、最小単純優先、嘘の近道を作らない、ラベル統一、利用者明示承認 2026-05-23 |
| 論点 4：dogfooding_mode | **spec.json から削除**（レビュー記録の front-matter のみで管理） | レビュープロセス管理の責務 |
| 論点 5：pending_findings | **spec.json から削除**（レビュー記録のみで管理） | レビュープロセス管理の責務 |
| 論点 6：traceability | **spec.json から削除**。機能分離証跡は `stages/feature-partitioning/<日付>-proposal.md` として artifacts で残す | 機能横断の責務 |
| 論点 7：recheck／reopen | **spec.json に保持** | §5.6 と直接対応するワークフロー管理の中核 |

## 6. 計画書改定の影響範囲（段を 5 段に拡張する大幅変更）

利用者の選択は **段集合の大幅変更**（alignment-gate を alignment と approval の 2 段に分割し、さらに drafting と local-review も分離する責務分離による 5 段化、ラベルは名詞統一）。理由は「将来の別モデル承認（§5.12 人間代役機構）との連動を視野に入れたとき、alignment と approval を別段として明示するほうが拡張しやすい」「誰が何をしたかを段単位で明確に記録する」ため。

### 6.1 §5.5 の改定

requirements 以降のフェーズの段集合を変更：

- **改定前**：drafting / review-wave / alignment-gate（3 段）
- **改定後**：drafting / local-review / review-wave / alignment / approval（5 段、全段名は名詞統一）

drafting と local-review の責務分離：

- drafting：actor=llm（または human）、草案作成のみ
- local-review：actor=llm、機能内 3 役レビュー（主役・敵対役・判定役）と機能内対処の実施

alignment-gate の actor=llm／human 混在を解体（alignment と approval の 2 段に分割）：

- alignment：actor=llm（自動判定）
- approval：actor=human または proxy_model（人間または別モデルの承認）

機能単位 spec.json は requirements 以降の各フェーズで **同じ 5 段（drafting／local-review／review-wave／alignment／approval）** を保持する。機能横断段（review-wave／alignment／approval）の **機能横断側の状態** は機能横断 yaml で管理し、**機能単位側の状態** は機能単位 spec.json で管理する責任分担を §5.5 に明記。

### 6.2 §5.6 の trigger_map 改定

reopen 時の再実施段マップで alignment-gate を参照していた箇所をすべて alignment と approval の組合せに置換。

例：

```
# 改定前
I-2:
  - stages/design.yaml#alignment-gate
  - stages/tasks.yaml#alignment-gate
  - stages/implementation.yaml#alignment-gate

# 改定後
I-2:
  - stages/design.yaml#alignment
  - stages/design.yaml#approval
  - stages/tasks.yaml#alignment
  - stages/tasks.yaml#approval
  - stages/implementation.yaml#alignment
  - stages/implementation.yaml#approval
```

trigger_map の全エントリ（I 起点／A 起点／D 起点／R 起点／N 起点）に同様の置換が必要。

### 6.3 §5.12 との連動を明記

approval 段の actor として `proxy_model` を含むことを §5.5 と §5.12 の両方で明記。§5.12 の代行可能／本人必須の線引きルールに「approval 段の代行可否」を含める。

### 6.4 §5.24 新節の追加

spec.json の正本スキーマを §5.24「spec.json の正本スキーマ」として新設：

- §5.24.1：spec.json の役割と単一責任（ワークフロー管理の機能単位部分）
- §5.24.2：フィールド一覧と意味
- §5.24.3：段の構造と状態値の正本
- §5.24.4：current_phase の値リスト
- §5.24.5：構造例
- §5.24.6：同期問題の運用方針
- §5.24.7：他の管理場所との責任分担（レビュー記録、stages/*.yaml）
- §5.24.8：機能横断段と機能単位 spec.json の対応関係（review-wave／alignment／approval の機能横断側／機能単位側の責任分担を明示）
- §5.24.9：drafting 段と local-review 段の責務分離（起草者と判定者の分離規律 §5.4 との連動を明記）

### 6.5 その他の改定

- §5.7、§5.8 など alignment-gate が登場する箇所を見直し、alignment と approval の 2 段に分けて記述
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
- 各機能の現状（requirements の alignment 段まで通過、approval は未取得など）を反映
- 全機能配置後にコミット

## 8. 現状の foundation/spec.json との差分

セッション 20 序盤で作成した foundation/spec.json は本設計に整合していない。第 3 段階で次の修正が必要：

- `phase`：`requirements-completed`（造語）→ alignment 段まで通過の状態を示す正本値（current_phase はフィールドとして書かず計算で求める方針に再確定したため、過去の foundation/spec.json の `phase` フィールド自体を削除する）
- `approvals` フィールド全体 → `workflow_state` に置換、各段の状態値を正本（drafting／local-review／review-wave／alignment／approval、名詞統一）に変更（5 段化）
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
