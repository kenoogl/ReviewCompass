# workflow-management implementation triad-review target bundle

run_id: 2026-06-04-workflow-management-implementation-review-run

## Review instruction

Review whether the workflow-management implementation, tests, and operating discipline satisfy the upstream requirements/design/tasks and the autonomous/parallel execution workflow. Focus on traceability, missing machine guards, raw response preservation, three-level triage, important-finding approval/proxy gates, commit/push boundaries, and auditability.

Use the output contract in the outer prompt. Findings should be actionable and grounded in the quoted target files.

## FILE: .reviewcompass/specs/workflow-management/requirements.md

```text
# Requirements Document：workflow-management

## Introduction

`workflow-management` は ReviewCompass における所定手続きの定義と機械強制を担う機能である。先行プロジェクトでは `implementation-governance` と呼ばれ、節ハッシュ・独立再導出パーサ・通過マーカーの後続確認・supersedes リンク等を含む大規模機構として組み上がっていたが、ReviewCompass では計画書 §5.4「軽量化方針」に従い、**思想は継承、実装は 1／10** を目標として再設計する。

計画書 §5.15.6 により機能名を `implementation-governance` → `workflow-management` に改称、§5.4〜§5.8 で軽量化方針・段階層構造・reopen 機械強制・session 跨ぎ状態管理・多層防御の位置付けを確定済み。本仕様はこれらの確定事項を要件として整理する。

## Boundary Context

- **In scope（範囲内）**
  - 所定手続き（intent／feature-partitioning／requirements／design／tasks／implementation／reopen／cross-spec-alignment）の段集合定義
  - 段集合の YAML 静的列挙（リポジトリ内 `stages/<process_id>.yaml`）
  - 軽量版検査スクリプト（証跡ファイル存在 ＋ 必須節充足の判定）
  - 不可逆操作の直前ゲート（spec.json 承認／コミット／プッシュ／フェーズ移行）
  - reopen 手続きの機械強制（手戻り種別の二次元表記、`trigger_map` による連鎖再実施）
  - session 跨ぎ状態管理（`stages/in-progress/`）
  - 多層防御の第 1 層位置付け（フェーズ 4 以降の第 2〜5 層の宿題化）
  - 起草者と判定者の分離（レビュー記録の front-matter `author`／`reviewer` 異名必須）

- **Out of scope（範囲外）**
  - 各機能の業務ロジック修正
  - `runtime`／`evaluation`／`self-improvement`／`analysis`／`conformance-evaluation` の具体的挙動変更
  - PR 運用や外部 CI の詳細
  - 人間レビュアー割り当て方針
  - 節ハッシュ・supersedes リンク・grandfathering 機構（§5.4 で削除確定）
  - 独立再導出パーサ（§5.4 で削除確定）
  - 通過マーカーの後続確認（§5.4 で削除確定、二次防御は多層防御の宿題）

- **隣接仕様の期待**
  - `foundation`／`runtime`／`evaluation`／`analysis`／`self-improvement`／`conformance-evaluation` は本仕様の完了規則に従う
  - `foundation` が所有する語彙正本を再定義せず参照する。本機能が実際に参照するのは、レビュー記録の冒頭メタデータ検査（Requirement 3）で用いる `review_mode`（レビューモード語彙、`foundation` Requirement 6 受入 6 所有）であり、所見系（`counter_status`／`severity`／`final_label`／`confidence_label`）・状態軸系（`run_status`／`validator_status`／`human_signoff_status`／`evidence_class`）は本機能の責務外で参照しない（`foundation` design.md が `severity` 等の再定義禁止対象から本機能を明示的に除外していることと整合。A-003 対処 2026-05-28）
  - `evaluation` から本仕様の所定手続き実行結果に対する評価要求を受ける
  - `self-improvement` からの規律変更提案（5 種類：new_discipline／update／status_change／archive／consolidation、`self-improvement` Requirement 3 由来）を所定手続き（drafting → review → approval）の入力として受け取り、承認後に規律ファイル（`docs/disciplines/discipline_*.md`、active 必読 12 件は 2026-05-25 セッション 26 で memory から軽量手続きで移管済み）の実体変更を本機能が実施する。本機能は規律変更を不可逆操作（Requirement 4 受入 1）の対象として扱い、`self-improvement` が直接ファイル書き換えを行うことはない（案 2、2026-05-23 利用者承認、A-007 由来）。memory 側の `feedback_*.md` 索引（Claude Code auto memory 機構の領域）は本機能の管理対象外で、本体は repo の `docs/disciplines/` を参照する設計

## Requirements

### Requirement 1：所定手続きの段集合の静的列挙

**目的（Objective）**：保守担当者と実装者が、所定手続きの段集合を機械可読な形で参照でき、各段の完了条件を再現可能に検査できるようにする。

#### 受入基準（Acceptance Criteria）

1. 本機能はリポジトリ内 `stages/` ディレクトリに、所定手続きごとの段集合を YAML として静的に列挙する。Markdown 節からの動的解析を行わない。
2. 本機能は計画書 §5.5 で確定した 9 ファイル体制（`intent.yaml`／`feature-partitioning.yaml`／`feature-dependency.yaml`／`requirements.yaml`／`design.yaml`／`tasks.yaml`／`implementation.yaml`／`reopen-procedure.yaml`／`cross-spec-alignment.yaml`）を支える。
3. 各 YAML 段は最低限、段名、`actor`（`human` または `llm`）、期待する証跡ファイルのパスパターン、必須節名のリスト、完了判定方式を含む。
4. 機能横断段の場合、`feature_order` フィールドで `feature-dependency.yaml#phase_order` を参照する。
5. 段集合の変更は YAML ファイル 1 箇所の修正で完結し、Markdown 文書側との整合は人手で取る前提とする（§5.4 受け入れリスク）。
6. **機能横断段（review-wave）の作業内容（2026-05-27 セッション 34 追記、2026-05-28 セッション 35 で 2 回方式に訂正、軽量手続き）**：本機能が管理する所定手続きの中で、機能横断段（review-wave）の作業内容は計画書 §5.5（機能横断段の作業内容）／ §5.9.6（N モデル比較実験の実施タイミング）と整合する。具体的には、機能横断段は「機能横断波及所見の集約・対処」に加え、「**7 モデル比較実験の 2 回目（同根問題評価）と同根問題集約**」（(ニ) (Q2)、2026-05-27 セッション 34 確定 ／ 2 回方式への訂正、2026-05-28 セッション 35 確定）を作業内容として含む。7 モデル比較実験は **2 回方式** で実施し、1 回目は機能ごとの triad-review 段で機能内 must-fix／should-fix を評価して機能内対処を完了させ、2 回目（本機能横断段）は機能横断波及所見と同根所見を評価する。本受入基準は計画書 §5.23.13 軽量手続き許容の範囲内で追加。利用者明示承認の出典：「計画書や仕様・設計にも反映」「提案通り」（2026-05-27 セッション 34）／「機能内対処は triad-review 段で実施しないと、他のフィーチャーの処理に影響する可能性がある。一方、同根問題は機能横断段で処理するべきである。つまり、2 回に分けて 7 モデルの must-fix+should-fix の対応が必要」「案 イ」「案 ア」（2 回方式への訂正、2026-05-28 セッション 35）。

### Requirement 2：軽量版検査スクリプトの提供

**目的**：保守担当者が、所定手続きの段完了を機械検査できるようにする。検査は主張ではなく証拠に基づき、結論不能なら遮断する。

#### 受入基準

1. 本機能はリポジトリ内検査スクリプト（Python 実装）を提供する。
2. 本検査スクリプトは段ごとの完了判定を次のみで実施する：YAML に列挙された証跡ファイルがすべて存在し、必須節名がすべて含まれること。
3. 本検査スクリプトは中身の妥当性（記述内容の品質）を判定しない。第 1 層の限界（§5.8）として明示する。
4. 本検査スクリプトは結論不能（証跡ファイルが解析不能、YAML が壊れている等）の場合、合格判定を出さず fail を返す。
5. 本検査スクリプトは `stages/in-progress/` に何かファイルがあれば「未完了の手続きあり」の警告を出す（§5.7）。

### Requirement 3：起草者と判定者の分離

**目的**：保守担当者が、自己承認による所定手続きの空洞化を防ぐ。レビュー記録の冒頭メタデータで起草者と判定者の異名を必須化する。

#### 受入基準

1. 本機能はレビュー記録の front-matter に `author`（起草者）と `reviewer`（最終判定者）のフィールドを必須化する。
2. 本機能は `author.identity` と `reviewer.identity` の同一を許容しない（§5.4 の自己承認禁止）。
3. 本機能はサブエージェント方式（`mode: subagent_mediated`、計画書 §5.23.12）でメインセッションが主役を担う場合、判定役を必ず別エンティティ（別モデル、別 session）で実施することを要求する。
4. 本機能は機械検査時に front-matter の必須フィールド存在と異名条件を判定する（別モデル・別 session の機械判定は第 1 層検査対象外。利用者監査の第 3 層に委ねる、Requirement 7 受入 2 由来）。
5. 本機能は review-run 後の proxy_model 判断代行を、メインセッション LLM のトリアージ下書き、proxy_model の採用案・判断理由・最終ラベル決定、機械ガードによる proxy decision 充足確認、メインセッション LLM の TDD 実装、利用者による不可逆操作承認、の分担として扱う。proxy_model は重要件の判断を代行できるが、コミット・プッシュ・spec.json 更新・フェーズ移行は代行しない。

### Requirement 4：不可逆操作の直前ゲート

**目的**：保守担当者が、所定手続きの空洞化を構造的に防ぐ。機械ゲートを不可逆操作の直前に集中する。

#### 受入基準

1. 本機能は次の不可逆操作の直前を機械ゲートの対象とする：`spec.json` の `approve` 書き込み、コミット、プッシュ、フェーズ移行。
2. 本機能はゲート発火条件として、Requirement 2 の検査スクリプトが pass を返すこと、および `stages/in-progress/` に未完了手続きがないことを要求する。直前ゲートは毎回独立して走行する（session 開始時の検査結果（Requirement 6 受入 3）をキャッシュせず、session 開始後の状態変化を直前で再検出する）。
3. 本機能は検査が結論不能な場合、ゲートを通さない（fail-closed の既定）。
4. 本機能は機械ゲートを最小集合に絞り、不可逆操作以外には機械検査を強制しない（§5.4 の「最小集合」方針）。

### Requirement 5：reopen 手続きの機械強制

**目的**：保守担当者が、reopen 手続き（やり直し）の連鎖再実施を機械的に決定できるようにする。手戻り種別から再実施対象を自動決定する。

#### 受入基準

1. 本機能は手戻り種別を「起点フェーズ記号 N／R／D／A／I ＋ 深さ」の二次元表記で表す（計画書 §5.6）。N＝intent、R＝requirements、D＝design、A＝tasks、I＝implementation。深さの範囲は起点ごとに非対称：N 起点は深さ 0 のみ（intent より上流が存在しないため）、R 起点は 0〜1、D 起点は 0〜2、A 起点は 0〜3、I 起点は 0〜4。
2. 本機能は `stages/reopen-procedure.yaml` の第 7 段に `trigger_map` を持たせ、種別から再実施対象を機械的に決定する。
3. 本機能は actor=human の段（intent.yaml#approval、feature-partitioning.yaml#approval 等）に進行が到達した時点で作業を停止し、in-progress ファイルに「人間承認待ち」を記録して待機する。
4. 本機能は人間承認なしに次の段への進行を許さない（fail-closed）。
5. 本機能は種別判定の根拠を `docs/reviews/reopen-classification-<日付>.md` として保存し、第 7 段はその判定ファイルを読み込んで連鎖再実施対象を決定する。

### Requirement 6：session 跨ぎ状態管理

**目的**：複数段にまたがる手続きの途中で session が切れる場合、進行中状態を明示し、次セッションが優先処理できるようにする。

#### 受入基準

1. 本機能は現在進行中の手続きを `stages/in-progress/<process_id>-<日付>.yaml` で表す。
2. 進行中ファイルは最低限、`process_id`、`started_at`、`trigger`、`completed_steps`、`next_step`、`pending_gates` を含む。
3. 本機能は session 開始時の標準フローとして次を要求する：TODO_NEXT_SESSION.md と git log で全体到達点把握、`stages/*.yaml` 全件検査、`stages/in-progress/` の有無確認、進行中手続きの優先完了、次作業の決定。
4. 本機能は手続き完了時、進行中ファイルを `stages/completed/` に移動するか削除する。
5. 本機能は `stages/in-progress/` に何かある状態での不可逆操作実行を遮断する（fail-closed、Requirement 4 と整合）。
6. 本機能は原則として毎 session、特に重要な判断・承認・レビュー結果・修正経緯が発生した session について、`docs/sessions/session-<N>-<YYYY-MM-DD>.md` にセッション記録を残す運用を要求する。`<N>` は既存の最大セッション番号 + 1 とし、メインセッション LLM が草案作成責任を持つ。`TODO_NEXT_SESSION.md` は入口メモ、`docs/sessions/` は経緯記録の保存先として役割を分離する。

### Requirement 7：多層防御の位置付け

**目的**：保守担当者が、本機能（軽量版 YAML 検査機構）が多層防御の第 1 層であることを理解し、過剰な期待をしないようにする。100% の規律遵守は原理的に不可能であり、複数層を重ねて実効遵守率を引き上げる方針。

#### 受入基準

1. 本機能は自身を多層防御の第 1 層として位置付け、第 1 層が解決しない失敗モード（中身の空疎、検査スクリプトの呼び出し依存、in-progress ファイルの自己申告性、文脈圧力下での規律低下、§5.8 由来）を明文化する。
2. 本機能は第 2〜5 層（git フックによる外部強制、フェーズ境目の利用者監査、定期事後監査、処理表面積の抑制方針）をフェーズ 4 以降の宿題として参照する。
3. 本機能は第 5 層（処理表面積の抑制方針）の運用ルール「新規規律を追加するときは既存規律 1 つ以上を統廃合する」を本機能の運用ルールに反映する（フェーズ 4 までは利用者の意識に依拠、機械強制は第 5 層導入時に検討）。
4. 本機能は第 1 層の限界を運用文書に明示し、利用者の期待値を整える。

### Requirement 8：機能依存マップの一元化

**目的**：保守担当者が、機能間の処理順と依存関係を 1 箇所で管理できるようにする。各フェーズの YAML がこのマップを参照することで、機能の追加・削除や依存関係の変更が 1 箇所のみの修正で完結する。

#### 受入基準

1. 本機能は `stages/feature-dependency.yaml` を機能間処理順と依存関係の一元保管先とする。
2. 本ファイルは最低限、`features`（機能ごとの `depends_on` 列挙）と `phase_order`（機能間処理順）を含む。`depends_on` の値は単純なリスト構造（例：`[foundation, runtime]`）、または依存種別（`hard`／`review`）を持つ連想配列構造（例：`foundation: hard, runtime: review`）の両方を許容する。後者は `conformance-evaluation` のように依存性の強度を区別する機能で使う（計画書 §5.5 行 368〜373 由来）。
3. 各フェーズの YAML（`requirements.yaml`／`design.yaml`／`tasks.yaml`／`implementation.yaml`）の草案段とレビュー波段は `feature_order: <feature-dependency.yaml#phase_order>` の参照を持つ。
4. 機能の追加・削除や依存関係の変更は本ファイル 1 箇所の修正で完結する（計画書 §5.5 選択肢 X：独立 YAML 参照方式）。
5. 機能間依存マップの所有者は本機能であり、`runtime`／`evaluation` 等の他機能は再定義せず参照のみとする。

## Change Intent

本仕様は先行プロジェクトの `implementation-governance` 仕様（156 行、9 要件）を、ReviewCompass の方針（計画書 §5.4〜§5.8）に基づき**思想は継承、実装は 1／10**で再設計した。素材の Req 9（実行台帳と強制機構）の大規模機構（節ハッシュ・独立再導出パーサ・通過マーカーの後続確認・supersedes リンク等）は §5.4 で削除確定。

ReviewCompass 固有の追加：

- 機能名 `implementation-governance` → `workflow-management` に改称（計画書 §5.15.6）
- 段集合の YAML 静的列挙への置き換え（Requirement 1、§5.4 由来）
- 軽量版検査スクリプト（証跡 ＋ 必須節のみ判定）（Requirement 2、§5.4 由来）
- 起草者と判定者の分離をレビュー記録の front-matter で担保（Requirement 3、§5.4 由来）
- 不可逆操作の直前ゲートを最小集合に絞る（Requirement 4、§5.4 由来）
- reopen 手続きの機械強制を `trigger_map` で（Requirement 5、§5.6 由来）
- session 跨ぎ状態管理を `stages/in-progress/` で（Requirement 6、§5.7 由来）
- 多層防御の第 1 層位置付けを明示（Requirement 7、§5.8 由来）
- 機能依存マップの一元化（Requirement 8、§5.5 由来）
- サブエージェント方式（`mode: subagent_mediated`）への対応を Requirement 3 受入 3 で明示（計画書 §5.23.12 由来）

削減・除去：

- 旧 Req 1（implementation conformance review の必須化）：ReviewCompass の所定手続き全体に統合（要件 5 の reopen を含む）
- 旧 Req 2（レビュー成果物と所見契約）：内容は §5.9（レビュー方法、所有者は本機能と evaluation の境界に位置）に整理
- 旧 Req 3（適合性メトリクス台帳）：§5.9.5 効果測定 3 指標に統合
- 旧 Req 4（signal と handback 連携）：Requirement 5 reopen の中に統合
- 旧 Req 5（governance artifact 検証）：Requirement 2 検査スクリプトに統合
- 旧 Req 6（workflow gate 状態と機能横断整合）：Requirement 4 ＋ Requirement 8 ＋ §5.5 の `cross-spec-alignment.yaml` に分散
- 旧 Req 7（intent review と phase-review メトリクス）：§5.5 の intent 層 ＋ §5.9.5 効果測定 3 指標に統合
- 旧 Req 8（reference-free case bootstrap）：ReviewCompass の対象アプリ配置（§5.23.7）に統合、本機能から外す
- 旧 Req 9（実行台帳と強制機構）：本仕様 Requirement 1〜4 の軽量版に置き換え。大規模機構は §5.4 で削除確定

機能横断レビューで対処された所見：

- 本機能に関連する所見：A-005（feature-dependency 依存記述の連想配列構造、Requirement 8 受入 2 で対処済み、2026-05-23）、A-007（self-improvement との権限分散調停、Boundary Context 隣接期待で対処済み、案 2 採用、2026-05-23 利用者承認）
- 参考：他機能の所見（A-001／A-003／A-004 とも 2026-05-23 対処済み）の対処履歴は [learning/workflow/carry-forward-register/reviewcompass-import.yaml](../../learning/workflow/carry-forward-register/reviewcompass-import.yaml) を参照

```

## FILE: .reviewcompass/specs/workflow-management/design.md

```text
# Design Document：workflow-management

最終更新：2026-05-25（セッション 26：design.drafting 起草、要件 8 件に対応）

## 概要（Overview）

`workflow-management` は ReviewCompass における所定手続きの定義と機械強制を担う機能の **設計層** である。

要件文書（requirements.md）は 8 件の Requirement で、段集合の静的列挙、軽量版検査スクリプト、起草者と判定者の分離、不可逆操作の直前ゲート、reopen 機械強制、session 跨ぎ状態管理、多層防御の第 1 層位置付け、機能依存マップの一元化を求めている。本設計は計画書 §5.4〜§5.8（軽量化方針、所定手続きの階層構造、reopen 機械強制、session 跨ぎ状態管理、多層防御）を実装可能な形に落とし込み、先行プロジェクト `dual-reviewer-implementation-governance` の素材設計（466 行、節ハッシュ・独立再導出パーサ・supersedes リンク・通過マーカーの後続確認等を含む大規模機構）から **思想は継承、実装は 1／10** を目標として再設計する。

本設計の所有物は **手続きの段集合定義・検査スクリプト・直前ゲート・reopen 機械強制・session 跨ぎ状態管理** の 5 つのモデルである。レビューロジック（3 役・観点・所見分類）は `foundation` と `evaluation` が所有し、本機能は所定手続きの「どの段がいつ完了するか」「どの不可逆操作の前にどの検査を走らせるか」のみを担う。

## 目標（Goals）

- 所定手続きの段集合を機械可読な YAML（構造化テキスト形式）として静的に列挙し、Markdown 節からの動的解析を行わない
- 検査スクリプトの完了判定を「証跡ファイル存在＋必須節充足」のみに絞り、中身の妥当性判定を含めない（第 1 層の限界として明示）
- 起草者と判定者の分離をレビュー記録の冒頭メタデータ（front-matter、文書頭の構造化メタ情報）で機械検査可能にする
- 不可逆操作（spec.json 承認書き込み、コミット、プッシュ、フェーズ移行）の直前のみに機械ゲートを置き、それ以外には機械検査を強制しない（最小集合方針）
- 結論不能（証跡ファイルが解析不能、YAML が壊れている等）の場合に合格判定を出さず、必ず遮断する（fail-closed、検査結果が出せないときは止める方針）
- reopen 手続きの連鎖再実施を手戻り種別から機械的に決定し、`actor=human` の段（intent.yaml#approval 等）に到達した時点で必ず作業を停止する
- 機能間の処理順と依存関係を 1 ファイル（`stages/feature-dependency.yaml`）に一元化し、追加・削除を 1 箇所修正で完結させる

## 範囲外（Non-Goals）

- 各機能の業務ロジック修正（`runtime`／`evaluation`／`self-improvement`／`analysis`／`conformance-evaluation` の挙動変更は本機能の責務外）
- レビュー所見の妥当性判定（中身の質的評価は本機能の検査範囲外、利用者監査の第 3 層に委ねる）
- 節ハッシュ・supersedes リンク・grandfathering・format-migration・独立再導出パーサ（§5.4 で削除確定、素材から継承しない）
- 通過マーカーの後続確認（§5.4 で削除確定、二次防御は多層防御の第 2 層以降の宿題）
- 外部 CI・GitHub Actions・PR 運用ルール
- 人間レビュアーの組織割り当て方針
- 規律ファイル自体の起案・改廃方針（`self-improvement` の責務、本機能は所定手続きの入力として規律変更提案を受け取るのみ）
- 機械ゲートを git フックとして外部強制する仕組み（第 2 層、フェーズ 4 以降の宿題）

## 設計の前提（Design Drivers）

- 100% の規律遵守は原理的に不可能であり、複数層を重ねて実効遵守率を引き上げる方針（計画書 §5.8）
- LLM は文脈圧力下で規律ファイルの優先度を下げる失敗モードを起こす（§5.8 第 1 層の限界、補助層 C で事前検査を別途設計）
- 検査を呼ばない・結果を読まない・独断で進める経路は第 1 層の上にあるため、第 1 層単独では解決しない（多層防御の前提）
- 起草と判定を同一の actor が兼ねると自己承認の空洞化が起きる（§5.4 規律）
- 機能の追加・削除を 1 箇所修正で完結させないと、整合漏れが累積する（§5.5 選択肢 X の根拠）
- session 跨ぎの最大の盲点は「複数段にまたがる手続きの途中状態」であり、状態ベース検査だけでは捉えられない（§5.7 由来）

## 全体構造（Architecture）

本機能は repo 内に **段集合 YAML 9 ファイル ＋ 検査スクリプト 1 本 ＋ 進行中状態ファイル群** を持つ。実体は次の 3 層構造を取る。

``\`
リポジトリ内配置（実体）
├── stages/                              # 段集合 YAML の保管先（Req 1）
│   ├── intent.yaml                      # intent 層（drafting／review／approval の 3 段）
│   ├── feature-partitioning.yaml        # 機能分離（candidate-proposal／approval の 2 段）
│   ├── feature-dependency.yaml          # 機能依存マップ（Req 8、所有者は本機能）
│   ├── requirements.yaml                # 要件フェーズ（5 段、feature-dependency 参照）
│   ├── design.yaml                      # 設計フェーズ（5 段、同上）
│   ├── tasks.yaml                       # タスクフェーズ（5 段、同上）
│   ├── implementation.yaml              # 実装フェーズ（5 段、同上）
│   ├── reopen-procedure.yaml            # reopen 手続き（4 過程構成、trigger_map 含む）
│   ├── cross-spec-alignment.yaml        # 機能横断整合（段集合は別途確定）
│   ├── in-progress.schema.json          # 進行中状態ファイルのスキーマ（T-008、命名を in-progress/ に統一、F-018 対処 2026-05-28）
│   ├── in-progress/                     # 進行中状態ファイル（Req 6、session 跨ぎ用）
│   └── completed/                       # 完了済み手続きの記録
├── tools/check-workflow-action.py       # 検査スクリプト本体（Req 2、補助層 C 段階 2）
├── docs/logs/workflow-precheck.log      # 検査結果のログ書き出し先（Req 2 受入 5 補強）
├── docs/reviews/reopen-classification-<日付>.md  # reopen 種別判定の根拠（Req 5 受入 5）
├── docs/operations/WORKFLOW_MANAGEMENT.md        # アプリ側規約（T-001 で配置、F-019 対処 2026-05-28）
└── docs/operations/WORKFLOW_PRECHECK.md          # 補助層 C 段階 2 正本仕様（T-004／T-005／T-008／T-009 が節を追記、F-019 対処 2026-05-28）
``\`

実行時のデータの流れ：

``\`mermaid
graph TD
    Trigger["利用者または LLM が<br>不可逆操作を要求"] --> Precheck["補助層 C 段階 1<br>事前検査呼び出し"]
    Precheck --> Script["tools/check-workflow-action.py<br>（Req 2）"]
    Script --> Stages["stages/*.yaml<br>段集合と完了判定（Req 1）"]
    Script --> InProgress["stages/in-progress/<br>進行中状態（Req 6）"]
    Script --> SpecJson["spec.json<br>機能単位 workflow_state"]
    Script --> Pending["learning/workflow/carry-forward-register/reviewcompass-import.yaml<br>未消化所見"]
    Script --> Verdict{"verdict 判定"}
    Verdict -->|OK| Pass["不可逆操作の実行を許可"]
    Verdict -->|WARN| Warn["警告して継続"]
    Verdict -->|DEVIATION| Block["fail-closed で遮断<br>（Req 4 受入 3）"]
    Pass --> Log["docs/logs/workflow-precheck.log<br>に検査結果を追記"]
    Block --> Log
``\`

検査スクリプトは段集合 YAML、進行中状態ファイル、spec.json、未消化所見の 4 つを入力として読み、verdict（判定結果）を返す。verdict には OK／WARN／DEVIATION の 3 値を使う（actor=human の段で承認待ちのときは DEVIATION で止め、警告のみで継続できる軽微な未整合は WARN とする）。語彙の正本は補助層 C 段階 2 仕様 `docs/operations/WORKFLOW_PRECHECK.md` §7.1〜§7.2 と検査スクリプト本体 `tools/check-workflow-action.py` の実装で、本設計は実装に合わせる方向で語彙を確定する（F-003 対処、2026-05-25 セッション 26 利用者明示承認）。

### 責務境界の明確化（Boundary Clarification）

本機能が所有するのは **手続きの完了規則と検査スクリプト** であり、各機能の業務 artifact の所有権は持たない。

| 所有関係 | 所有者 | 本機能との関係 |
|---|---|---|
| 段集合 YAML（`stages/*.yaml`） | **workflow-management** | 本機能が単独所有・改廃 |
| 検査スクリプト（`tools/check-workflow-action.py`） | **workflow-management** | 本機能が単独所有・改廃 |
| 機能依存マップ（`stages/feature-dependency.yaml`） | **workflow-management**（Req 8 受入 5） | 他機能は再定義せず参照のみ |
| reopen 種別判定の根拠ファイル | **workflow-management**（Req 5 受入 5） | 他機能は参照のみ |
| 各機能の spec.json（`.reviewcompass/specs/<機能>/spec.json`） | 各機能 | 本機能は読むのみ、書き込みは検査通過後に各機能の起草者が行う |
| レビュー記録（`.reviewcompass/specs/<機能>/reviews/*.md`） | 各機能 | 本機能は front-matter の構造のみ検査（Req 3 受入 4） |
| レビュー所見の妥当性 | `evaluation`／利用者監査の第 3 層 | 本機能の検査範囲外（Req 2 受入 3、Req 7 受入 1） |
| 語彙正本（本機能が参照するのは `review_mode` のみ。所見系・状態軸系は責務外で不参照） | `foundation` | 本機能は再定義せず参照のみ（要件 Boundary Context 隣接期待。A-003 対処 2026-05-28） |
| 規律ファイル本体（`docs/disciplines/discipline_*.md`、12 件配置済み） | **workflow-management**（実体書き換え、A-007 案 2） | `self-improvement` から変更提案を受け取り、所定手続き経由で実体変更。本機能の検査スクリプトと段階 3 フックの対象に含まれる |
| 規律ファイルの提案権 | `self-improvement` | 本機能は提案を所定手続きの入力として受け取る |
| 規律ファイルの memory 側索引（`~/.claude/projects/.../memory/feedback_*.md`、12 件） | Claude Code auto memory 機構（製品機能） | 本機能の管理対象外。短い参照索引のみ保持し、本体は `docs/disciplines/` を Read で参照する設計（A-007 対処、2026-05-25 セッション 26 移管） |

**規律ファイルの所有先確定の経緯（A-007 対処、2026-05-25 セッション 26 利用者明示承認）**：本機能の所定手続きが規律変更を扱うには、規律ファイル本体がリポジトリ内（git 追跡対象）に存在する必要がある。素材設計時点では本体が memory（リポジトリ外、Claude Code auto memory 機構の領域）に置かれていたため、本機能の機械検査が効かない構造的問題があった。本セッション 26 で **軽量手続き** により次を実施し本問題を解消：

- active 必読 11 件（feedback_must_fix_discussion_obligation／intent_conformance_is_the_acceptance_gate／standing_directives_are_hard_constraints／workflow_precheck_invocation／approval_operation／facts_vs_interpretation／pre_action_precheck／workflow_state_truth_source／concise_complete_report／reopen_procedure_for_settled_topics／plain_japanese）と参照層 5 件（feedback_dominant_dominated_options／feedback_choice_presentation／feedback_no_redundant_workflow_questions／feedback_plain_explanation_each_step／feedback_implementation_autonomy）の合計 **16 件** の本体を `docs/disciplines/discipline_*.md` にフラット配置で移管（コミット b830785 で active 必読 12 件＋参照層 5 件＝17 件として移管後、セッション 26 で利用者明示承認に基づき `no-unilateral-action` 規律 1 件を撤去、合計 16 件に減）。さらに memory 側の `feedback_*.md` 16 件はシンボリックリンクで repo 本体を指す構成に変更（2026-05-25 セッション 26、利用者明示承認「試してみる」）。当初は auto memory 機構がセッション起動時にリンクをたどって規律本体を完全に auto load する想定だったが、**2026-05-25 セッション 27 の検証で否定された**：auto memory の起動時 load 対象は `MEMORY.md` の索引（1 文要約）までで、シンボリックリンク経由でも本体はたどられない。**fallback 案イを採用**（利用者明示承認「推奨案」、2026-05-25 セッション 27）：シンボリックリンク 16 件は単一正本（repo）維持の補助機構として残置、TODO §1 起動手順に「規律本体 11 件を Read で読む」ステップを追加、active 必読 11 件は毎セッション開始時に Read で明示的に読み込む運用に切り替え。
- memory 側は短い参照索引（移管先パスと改廃ルールへのリンクのみ）に置換、`MEMORY.md` 索引ファイルにも移管反映
- archive 14 件（`memory/archive/2026-05-25-consolidation/`）のみ memory 側に残存（過去履歴の保全）
- 移管後の整理として、front-matter の memory 機構固有メタ（`node_type: memory`／`originSessionId`）を全 17 件から削除、`plain_japanese` ／参照層 5 件の旧形式を統一形式に正規化、旧名リンク（`[[feedback-implementation-autonomy]]` 等）を新名に修正、`docs/disciplines/README.md` を新設して内部リンク `[[link-name]]` の解決規則と全 17 件のインデックスを明記
- 計画書 §5.21（規律ファイルの ReviewCompass 方針への取り入れ手順）を前倒し実施した位置付け

`self-improvement` との権限分散（A-007 案 2、2026-05-23 利用者承認）：規律ファイルの **提案権** は `self-improvement` が持ち、**実体変更権** は本機能が所定手続き（drafting → review → approval）経由で実施する。本機能は規律変更を Req 4 受入 1 の不可逆操作の対象として扱い、`self-improvement` が直接ファイル書き換えを行うことはない。

## 段集合の静的列挙モデル（Stage Set Static Enumeration Model）— Req 1

### 1. 9 ファイル体制（計画書 §5.5）

段集合は次の 9 ファイルに静的列挙する。Markdown 節からの動的解析は行わない（Req 1 受入 1）。

| ファイル | 段集合 | actor 構成 |
|---|---|---|
| `stages/intent.yaml` | drafting／review／approval の 3 段 | human／llm／human |
| `stages/feature-partitioning.yaml` | candidate-proposal／approval の 2 段 | llm／human |
| `stages/feature-dependency.yaml` | 段集合なし（機能依存マップ本体、Req 8） | — |
| `stages/requirements.yaml` | drafting／triad-review／review-wave／alignment／approval の 5 段 | llm／llm／llm／llm／human または proxy_model |
| `stages/design.yaml` | 同上 | 同上 |
| `stages/tasks.yaml` | 同上 | 同上 |
| `stages/implementation.yaml` | 同上 | 同上 |
| `stages/reopen-procedure.yaml` | 4 過程構成（§reopen 機械強制モデル §5）、第3過程で trigger_map 参照 | llm／human 混合 |
| `stages/cross-spec-alignment.yaml` | 段集合は別途確定（フェーズ 2 以降） | — |

各 YAML 段は最低限、段名／`actor`／期待する証跡ファイルのパスパターン／必須節名のリスト／完了判定方式を含む（Req 1 受入 3）。

### 2. 段定義の構造例

`stages/requirements.yaml` の段定義例：

``\`yaml
process_id: requirements
description: 要件フェーズの所定手続き（drafting → triad-review → review-wave → alignment → approval の 5 段）
feature_order: feature-dependency.yaml#phase_order   # Req 8 受入 3、Req 1 受入 4

stages:
  - name: drafting
    actor: llm                                      # 起草、主に LLM
    artifact_paths:
      - .reviewcompass/specs/{feature}/requirements.md
    required_sections:
      - Introduction
      - Boundary Context
      - Requirements
      - Change Intent
    completion_predicate: artifact_exists_and_sections_present
    description: 起草者と判定者の分離規律により、起草段は判定段と別 actor で実施する

  - name: triad-review
    actor: llm
    artifact_paths:
      - .reviewcompass/specs/{feature}/reviews/*-requirements-triad-review.md
    required_sections:
      - 主役レビュー
      - 敵対役レビュー
      - 判定役レビュー
      - 統合
    completion_predicate: artifact_exists_and_sections_present_and_author_reviewer_distinct
    front_matter_required:
      - author.identity
      - reviewer.identity
      - reviewer.separation_from_author
    description: 3 役レビュー、起草者と判定者の異名を front-matter で必須化

  - name: review-wave
    actor: llm
    feature_order_required: true                    # 全機能の drafting＋triad-review 完了後に開始
    artifact_paths:
      - docs/reviews/{phase}-review-wave-{日付}.md
    completion_predicate: all_features_drafting_and_triad_review_completed
    description: 機能横断の波及所見の集約消化

  - name: alignment
    actor: llm                                      # LLM 自動判定
    completion_predicate: cross_spec_alignment_passed
    description: フェーズ終端の機能横断整合確認（LLM 自動判定）

  - name: approval
    actor: human                                    # 人間が承認（proxy_model 代行は §5.12 で条件付き許容）
    actor_allowed:
      - human
      - proxy_model
    proxy_allowed_condition: reviewcompass.yaml#human_proxy.proxy_allowed
    completion_predicate: explicit_human_approval_recorded
    description: 不可逆操作（フェーズ移行）の直前ゲート、本人または proxy_model による明示承認
``\`

### review-run 後の proxy_model 判断代行モデル

review-run 後の重要件判断は、approval 段の proxy_model 許容とは別に、triad-review 段内の修正方針決定にも適用できる。対象は API 経由 review-run の `must-fix`、`should-fix`、`ERROR`、`CRITICAL`、または同根所見クラスタである。

責務分担：

- メインセッション LLM：raw response を読み、モデル別要約、同根所見集約、三段階トリアージ下書き、候補案、推薦案、proxy_model への判断材料を作る
- proxy_model：重要件ごと、または同根所見クラスタごとに、採用案、判断理由、棄却案理由、最終ラベルを決定する
- 機械ガード：proxy decision の存在、raw response の存在、候補案の存在、採用案と最終ラベルの整合、未判断件数 0 を確認する
- メインセッション LLM：機械ガード通過後、採用された修正だけを TDD で実装する
- 利用者：コミット、プッシュ、spec.json 更新、フェーズ移行、規律変更、大方針変更を承認する

証跡構造：

``\`text
.reviewcompass/specs/<feature>/reviews/<review-run-id>/
  raw/
  parsed/
  triage.yaml
  model-result-summary.yaml
  review_summary.md
  proxy-decisions/
    <finding-id>.prompt.md
    <finding-id>.raw.txt
    <finding-id>.decision.yaml
  approval-proxy-<日付>.yaml
``\`

`proxy-decisions/<finding-id>.decision.yaml` は最低限、`finding_id`、`approved_by: proxy_model`、`proxy_model_id`、`selected_option`、`final_label`、`rationale`、`rejected_options`、`raw_response_path` を持つ。`approval-proxy-<日付>.yaml` は対象 review-run、承認対象 finding、参照した decision、summary/triage 提示済みフラグを束ねる。

proxy decision の監査性を保つため、decision は `decision_prompt_path`、`source_raw_paths`、`candidate_options` も持つ。`decision_prompt_path` は proxy_model に渡した prompt 証跡、`source_raw_paths` は元 review raw、`candidate_options` は proxy_model に提示された候補案セットである。機械ガードは、これらの参照先が存在し、`candidate_options` が空でないことを確認する。現行の軽量ガードは、`proxy_model_id` の文字列一致、decision file の `finding_id` 一致、`final_label` 一致、prompt/raw/候補案証跡の存在を検査する。API 署名や暗号学的な生成元証明は将来課題とする。

parallelizable_units：

- proxy_model 判断依頼：同根所見クラスタ単位で並列化可能。同根とは、複数モデルの所見が同じ対象ファイル、同じ出力契約、同じ機械ガード、同じ証跡、または同じ原因に触れているものをいう
- 実装：互いに同じファイルを更新しない実装単位、または入出力契約が独立したタスク単位で並列化可能
- 直列必須：共通スキーマ、共通ビルダー、同一ファイル、同一 manifest、同一 traceability 出力、生成物、共有 helper、推移的契約を触る修正
- 統合時：メインセッション LLM が triage、proxy decision、テスト結果、ファイル差分を再照合する

実装サブ担当 LLM は、原則として別スレッドかつ分離 worktree で扱う。同じ repo での並列実装は原則禁止し、読み取り調査または差分を残さない確認に限定する。メインセッション LLM は、対象 finding、proxy decision、許可ファイル、期待テスト、禁止事項、停止条件を渡し、統合時に差分とテスト結果を検査する。未承認の便乗リファクタ、隣接挙動変更、対象外 cleanup は実施せず、新規判断問題として停止する。

subimplementation_outputs：

- implementation_diff：本線へ取り込み可能なソース、テスト、スキーマ、fixture、必要最小限の docs 差分
- verification_summary：サブ担当が実行したテスト、赤確認、緑確認、未実行理由
- decision_basis：実装不能、停止、新規判断問題、採否判断に影響する失敗ログ
- work_noise：一時メモ、途中ログ、失敗パッチ案、ローカル調査メモ。原則として本線 repo に取り込まない

本線へ戻す標準単位は、パッチ、テスト結果サマリ、未解決事項の 3 点である。メインセッション LLM は `work_noise` を直接取り込まず、必要な場合のみ session record または docs/notes に要約する。判断に影響した失敗試行、失敗パッチ、途中ログは `decision_basis` へ昇格し、メインセッション LLM が要約または該当箇所を保存する。

### テンプレート変数の展開規則（F-006 対処、2026-05-25 セッション 26 利用者明示承認）

段集合 YAML の `artifact_paths` フィールドに登場する 3 種のテンプレート変数（プレースホルダ）の展開元と解決規則を次のとおり確定する：

- **`{feature}`**：機能横断段（`feature_order` を持つ段）では `feature-dependency.yaml#phase_order` から機能名を順に展開する。機能単位段（`feature_order` を持たない段）では当該機能名で固定する
- **`{phase}`**：当該 YAML の `process_id` フィールドから取得する（例：`requirements.yaml` の `process_id: requirements` なら `{phase}` は `requirements` に展開）。`process_id` と YAML ファイル名は段集合 YAML 配置時に同期させる前提とし、両者がずれた場合は `process_id` を正本として優先する
- **`{日付}`**：ファイル名のワイルドカード（`*`）として許容する。検査スクリプトは `glob` で `artifact_paths` パターンに一致する全ファイルを取得し、ファイル名に含まれる日付部分（`YYYY-MM-DD` 形式と仮定）の **辞書順最大** を最新と判定する

ワイルドカード解決時の優先順位を「辞書順最大」（mtime 基準ではなく）にする理由：ファイル名の日付は人手で命名されるため意図が明示される一方、ファイルの更新時刻（mtime）は `git clone` ／ `git checkout` で書き換わるため再現性に劣る。`YYYY-MM-DD` 以外の日付形式が混入した場合、検査スクリプトは結論不能（fail-closed）として DEVIATION を返す。

複数ファイルが存在しても重複定義の禁止ではなく、reopen による複数回生成（同じ段の証跡が日付違いで複数並存）を自然に扱うための設計。

### 3. 機能横断段と機能単位段の区別

- **機能横断段**：`feature_order` を持つ段（review-wave、alignment、approval の 3 段）。`feature_order: feature-dependency.yaml#phase_order` で機能依存マップを参照し、対象機能集合を一元化する（Req 1 受入 4、Req 8 受入 3）
- **機能単位段**：`feature_order` を持たない段（drafting、triad-review の 2 段）。各機能の `spec.json` の `workflow_state.<フェーズ>.<段>` で個別に管理する

機能横断段の機能横断側状態は `stages/<フェーズ>.yaml` の進行記録または別途配置する集約ファイルで保持し、機能単位の状態は各機能の `spec.json` で保持する（計画書 §5.24.8 由来）。

**機能横断段 review-wave の作業内容（2026-05-27 セッション 34 追記、2026-05-28 セッション 35 で 2 回方式に訂正、軽量手続き、Req 1 受入 6 と整合）**：

7 モデル比較実験は **2 回方式** で実施する（2026-05-28 セッション 35 確定、初版の「機能横断段で一括実施、機能ごとに実施しない」記述を訂正）：

- **1 回目（機能ごとの triad-review 段）**：当該機能の機能内 must-fix／should-fix を 7 モデル評価し、機能内対処を triad-review 段で完了させる。前機能の機能内対処未完了に次機能の triad-review が依存しない構造を保つ
- **2 回目（本機能横断段 review-wave）**：全機能の triad-review 完了後、機能横断波及所見と同根所見を 7 モデル評価

機能横断段 review-wave は、機能横断波及所見の集約・対処に加え、次の作業を含む（計画書 §5.5 ／ §5.9.6 と整合）：

- 全機能の triad-review が完了した時点で本段を開始する
- 機能横断波及所見と同根所見を対象に 7 モデル評価（2 回目）を実施
- 7 モデル評価データを全機能横並びで分析し、**同根所見**（異なる機能で同じ性格の所見が独立に発見された組）を grep ／ 集約で識別
- 同根所見ごとに一貫した対処方針を立案、全該当機能の仕様文書（requirements.md ／ design.md ／ tasks.md）に同じ対処を反映
- 個別機能の triad-review で「機能横断段に持ち越し」と判定された所見も本段で一括対処

本作業内容は、セッション 33 利用者発言「あるフィーチャーだけをみてもダメで、全フィーチャーの triad-review を行い、それを 7 つのモデルで評価させたところで、同根の問題をまとめて考える」を受けた構造的対処、およびセッション 35 利用者指摘「機能内対処は triad-review 段で実施しないと、他のフィーチャーの処理に影響する可能性がある」を受けた 2 回方式への訂正。利用者明示承認の出典：「(ニ)」「提案通り」「計画書や仕様・設計にも反映」（2026-05-27 セッション 34）／「2 回に分けて 7 モデルの must-fix+should-fix の対応が必要」「案 イ」「案 ア」（2 回方式への訂正、2026-05-28 セッション 35）。本記述は計画書 §5.23.13 軽量手続き許容の範囲内で追加。

### 4. 段集合の変更運用

段集合の変更は YAML ファイル 1 箇所の修正で完結する（Req 1 受入 5）。Markdown 文書（運営ガイド、計画書）側との整合は人手で取る前提とし、自動同期は行わない（§5.4 受け入れリスク）。段集合の変更そのものを不可逆操作の対象とするかは本フェーズで決めず、第 5 層（処理表面積の抑制）導入時に検討する（先送り論点参照）。

## 軽量版検査スクリプトモデル（Lightweight Check Script Model）— Req 2

### 1. 検査の対象と原則

検査スクリプト `tools/check-workflow-action.py` は Python 実装で（Req 2 受入 1）、次の 4 入力のみを読む：

- 段集合 YAML（`stages/*.yaml`）
- 進行中状態ファイル（`stages/in-progress/*.yaml`）
- 機能単位 spec.json（`.reviewcompass/specs/<機能>/spec.json`）
- 未消化所見（`learning/workflow/carry-forward-register/reviewcompass-import.yaml`）

判定原則：

- **段ごとの完了判定**：YAML に列挙された証跡ファイルがすべて存在し、必須節名がすべて含まれること、それ以外は判定対象としない（Req 2 受入 2）
- **中身の妥当性判定は行わない**：所見の質、表現の適切性、論理的整合性は判定範囲外（Req 2 受入 3、第 1 層の限界として明示）
- **fail-closed の既定**：結論不能（YAML が壊れている、証跡ファイルが解析不能、必須フィールド欠落）の場合は合格判定を出さず、必ず fail を返す（Req 2 受入 4）
- **進行中手続きの警告**：`stages/in-progress/` に何かファイルがあれば「未完了の手続きあり」の警告を出す（Req 2 受入 5）

### 2. サブコマンド構成（補助層 C 段階 2 由来、`docs/operations/WORKFLOW_PRECHECK.md` 参照）

| サブコマンド | 入力（必須引数） | 用途 |
|---|---|---|
| `spec-set <feature> <phase> <stage> <new_value>` | 機能名・フェーズ・段・新しい真偽値、`--rationale "<理由>"`（任意、ログ記録用） | `spec.json` の `workflow_state` 変更前の依存検査 |
| `commit` | `--rationale "<理由>"`（**必須**） | `git commit` 直前の検査（spec.json 整合、規律遵守、未消化所見の有無） |
| `push` | `--rationale "<理由>"`（**必須**） | `git push` 直前の検査（コミット履歴整合、リモート状態） |

引数仕様の正本は `docs/operations/WORKFLOW_PRECHECK.md` §5.1〜§5.3 と検査スクリプト本体 `tools/check-workflow-action.py` の argparse 定義。`commit` と `push` の `--rationale` 必須化の理由：両者は不可逆操作で、利用者承認発言の出典をログに残す必要があるため（F-009 対処、2026-05-25 セッション 26 利用者明示承認）。

各サブコマンドの戻り値（exit code）：

- `0`：OK（不可逆操作を許可）
- `1`：WARN（警告を出すが継続可、利用者判断で進める）
- `2`：DEVIATION（fail-closed で遮断、不可逆操作を許可しない）

出力形式は人間可読の既定形式と、`--json` 指定時の JSON 形式の 2 種類。人間可読既定は補助層 C 段階 2 仕様 `docs/operations/WORKFLOW_PRECHECK.md` §7.2、JSON 出力は同 §7.3 を正本参照する。人間可読既定の書式は `[VERDICT] OK ／ WARN ／ DEVIATION（exit N）` のように **大括弧付きラベル形式** で、`[VERDICT]`／`[ACTION]`／`[REASON]`／`[CURRENT STATE]` の 4 ブロックを順に出力する（F-010 対処、2026-05-25 セッション 26 利用者明示承認）。判定結果はログ（`docs/logs/workflow-precheck.log`、上書き可能）に追記する（同 §8.2）。

### 3. 完了判定の述語集合（completion_predicate 値域）

段集合 YAML の `completion_predicate` フィールドが取る値の集合：

| 述語名 | 判定内容 |
|---|---|
| `artifact_exists` | 期待する証跡ファイルが存在する |
| `artifact_exists_and_sections_present` | ファイル存在＋必須節名がすべて含まれる |
| `artifact_exists_and_sections_present_and_author_reviewer_distinct` | 上記＋front-matter の `author.identity` と `reviewer.identity` が異名 |
| `all_features_drafting_and_triad_review_completed` | `feature_order` の全機能で drafting＋triad-review が true |
| `cross_spec_alignment_passed` | 機能横断整合の判定が pass、未消化所見が 0 件 |
| `explicit_human_approval_recorded` | 利用者または proxy_model の明示承認が記録されている |
| `depends_on_resolves_correctly` | `feature-dependency.yaml` の各機能の `depends_on` が単純リスト構造または連想配列構造として解析可能、連想配列構造の場合は値が `hard` または `review` のいずれかであること（A-004 対処、2026-05-25 セッション 26 利用者明示承認） |

述語集合の追加・削除は本機能の責務。新しい述語を導入する場合は、本節と検査スクリプト実装の両方を同時に更新する。

### 4. 第 1 層の限界の明示

検査スクリプトが解決しない失敗モード（計画書 §5.8 由来、Req 7 受入 1）：

- 中身の空疎（必須節は存在するが内容が「特に問題なし」のみ）
- 検査スクリプト自体が呼ばれない経路
- `stages/in-progress/` ファイルの自己申告性（嘘・古い・欠落の余地）
- 文脈圧力下での規律ファイル優先度低下

これらは多層防御の他層（補助層 A／B／C、第 2〜5 層）で補完する。本機能は第 1 層の限界を運用文書（`docs/operations/WORKFLOW_PRECHECK.md`）に明示し、利用者の期待値を整える（Req 7 受入 4）。

## 起草者と判定者の分離モデル（Author-Reviewer Separation Model）— Req 3

### 1. front-matter の必須フィールド（計画書 §5.4 由来）

レビュー記録（`.reviewcompass/specs/<機能>/reviews/<日付>-<種別>.md`）の冒頭メタデータに次を必須化する：

``\`yaml
---
type: <レビュー種別>                     # 例：design_triad_review
target: <対象文書のパス>
target_commit: <commit hash>
target_content_hash: <sha256>
date: 2026-05-25
mode: subagent_mediated                  # レビューモード。値は foundation 正本を参照（再定義しない）
author:
  identity: claude_code_main_session     # 起草者の識別子
  model: claude-opus-4-7
  role: drafter
reviewer:
  identity: claude_code_subagent         # 最終判定者の識別子（必ず異名）
  model: claude-opus-4-7
  role: final_judgment
  separation_from_author: true           # 明示的に異名であることを宣言
---
``\`

機械検査は次の 3 点を判定する（Req 3 受入 4）：

1. `author.identity` と `reviewer.identity` フィールドの存在
2. `author.identity` ≠ `reviewer.identity`（文字列比較で同一を許容しない、Req 3 受入 2）
3. `reviewer.separation_from_author` が `true`

別モデル・別 session の機械判定は第 1 層検査対象外。これは利用者監査の第 3 層に委ねる（Req 3 受入 4 由来）。理由：CLI／API 経路の実行環境を機械判定で確実に区別する手段がフェーズ 1 では整わないため。

### 2. サブエージェント方式（subagent_mediated）の特例（Req 3 受入 3）

メインセッション LLM が主役（primary_reviewer）を兼ねる場合、判定役（judgment_reviewer）は **必ず別エンティティ**（別モデルかつ別 session）で実施する。これは計画書 §5.23.12 サブエージェント方式の限界（§5.23.12.7）を踏まえた特例である。

サブエージェント方式採用時の front-matter 例：

``\`yaml
author:
  identity: claude_code_main_session     # メインセッションが主役と起草を兼ねる
  model: claude-opus-4-7
  role: drafter_and_primary_reviewer     # 暫定許容の宣言
reviewer:
  identity: claude_code_subagent_judgment   # 判定役は別サブエージェント
  model: claude-opus-4-7                    # 同モデル許容（§5.9.1 改訂後）
  role: final_judgment
  separation_from_author: true
  subagent_invocation_method: agent_tool_with_general_purpose
``\`

`subagent_mediated` の場合、`role` フィールドに `drafter_and_primary_reviewer` 等の複合役を許容する（暫定許容の明示）。完全分離（メイン LLM が 3 役のいずれにもならない）はフェーズ 4 の runtime_mediated 経路で実装する。

### 3. 異名判定の機械検査範囲

機械検査の対象範囲（第 1 層で判定可能）：

- フィールドの存在判定
- 文字列の同一性判定
- 値域チェック（`actor` フィールドが `human`／`llm`／`proxy_model` のいずれか等）

機械検査の対象外（第 3 層 利用者監査または定期事後監査に委ねる）：

- 別モデルであることの実体確認（環境変数や API 呼び出し履歴の照合）
- 別 session であることの実体確認（session ID の独立性検証）
- レビュー記録の中身が独立性を満たすかの質的判定

## 不可逆操作の直前ゲートモデル（Pre-Operation Gate Model）— Req 4

### 1. 不可逆操作の最小集合（Req 4 受入 1）

機械ゲートの対象は次の 4 種類に絞る：

| 不可逆操作 | 検査対象 | 検査結果が fail の場合 |
|---|---|---|
| `spec.json` の `approval` 段書き込み | 当該機能の前段（alignment）が true、未消化所見が 0 件 | spec.json 書き込みを許可しない |
| `git commit` | 検査スクリプトが pass、`stages/in-progress/` が空 | commit を許可しない |
| `git push` | 直前のコミットが上記検査を通過済み、リモート状態と整合 | push を許可しない |
| フェーズ移行（次フェーズの drafting 段 true 化） | 当該フェーズの approval 段が `feature-dependency.yaml#phase_order` の全機能で true（本設計時点 7 機能、§機能依存マップモデル §2 の A-001 注記参照） | フェーズ移行を許可しない |

それ以外（spec.json の drafting／triad-review 段の書き込み、中間段の遷移など）には機械ゲートを置かない（最小集合方針、Req 4 受入 4）。これは検査スクリプトを呼ぶ頻度を下げ、検査自体の存在感を高めるため。

### 2. ゲート発火条件と独立走行（Req 4 受入 2）

ゲートは次の 2 条件で発火する：

1. Requirement 2 の検査スクリプトが pass を返す
2. `stages/in-progress/` に未完了手続きが存在しない

直前ゲートは **毎回独立して走行する**。session 開始時の検査結果（Req 6 受入 3）をキャッシュせず、session 開始後の状態変化（途中での `stages/in-progress/` ファイル追加、所見の追加等）を直前で再検出する。これは「session 開始時には pass だったが、その後の作業で状態が変わって本来 fail になるはずの遷移を見落とす」失敗モードを防ぐため。

### 3. fail-closed の既定（Req 4 受入 3）

検査が結論不能な場合：

- 検査スクリプトの実行に失敗した（exit code が 0 でも 1 でも 2 でもない、または stderr に致命的エラー）
- 段集合 YAML が壊れている（YAML パースエラー）
- 必須フィールドが欠落している
- `feature_order` が参照する `feature-dependency.yaml` が存在しない

これらの場合、ゲートを通さず必ず遮断する。判定不能を pass と解さない（fail-closed の既定）。これは「曖昧なときは止める」方針で、誤って不可逆操作を許可することによる被害を防ぐ。

### 4. ゲートと補助層 C 段階 3 の関係

本ゲートは検査スクリプト（補助層 C 段階 2）を内部で呼び出す。利用者または LLM が不可逆操作を要求した時点で、補助層 C の 3 段階が次の順に走る：

1. **段階 1**：LLM 規律として、これから何をするかを応答内で明示し、段階 2 を呼ぶ
2. **段階 2**：本ゲートの検査スクリプト（`check-workflow-action.py`）が走る
3. **段階 3**：Claude Code フック機構（フェーズ 2 以降の宿題）が段階 2 を自動で呼び、逸脱なら遮断

段階 3 が実装されるまでは段階 1 の規律で代用する。段階 1 と段階 3 は段階 2 を呼ぶ経路が異なるだけで、判定本体は段階 2 が単一の責務として持つ。

## reopen 機械強制モデル（Reopen Mechanical Enforcement Model）— Req 5

### 1. 手戻り種別の二次元表記（Req 5 受入 1、計画書 §5.6）

手戻り種別は **起点フェーズ記号 ＋ 深さ** の二次元で表す：

| 記号 | フェーズ | 深さの値域 |
|---|---|---|
| N | intent | 0 のみ（intent より上流なし） |
| R | requirements | 0〜1 |
| D | design | 0〜2 |
| A | tasks | 0〜3 |
| I | implementation | 0〜4 |

深さは「起点フェーズの何段上に戻るか」を表す。例：

- I-0 は実装段の整合ゲート再実施のみ
- I-4 は実装段で発見された問題が intent まで遡る場合の全フェーズ連鎖再実施
- D-1 は設計段で発見された問題が要件段の修正を要する場合（要件・設計の 2 フェーズ連鎖）

旧表記 A／B／C／D は I-0／I-2／I-3／I-4 に対応し、旧表記で欠落していた I-1 を含めた完全二次元表記となる。

### 2. trigger_map による連鎖再実施対象の決定（Req 5 受入 2）

`stages/reopen-procedure.yaml` に `trigger_map` を持たせ、第3過程（連鎖再実施）で参照する。種別から再実施対象を機械的に決定する：

``\`yaml
- name: 該当ゲートの再実施
  actor: llm                            # 第3過程の実行主体は LLM（trigger_map を解決して順次進行する）
  actor_resolution: per_target_stage    # 各 trigger_map エントリの参照先段の `actor` を段定義から動的解決
  trigger_map:
    D-1:
      - stages/requirements.yaml#alignment    # 参照先段の actor は当該段定義から取得（actor=llm 等）
      - stages/requirements.yaml#approval     # 同上（actor=human または proxy_model）
      - stages/design.yaml#alignment
      - stages/design.yaml#approval
    # 他種別（N-0／R-0〜1／D-0／D-2／A-0〜3／I-0〜4）の trigger_map は計画書 §5.6 行 457〜565 を正本参照
``\`

**第3過程の actor 解決規則（A-002 対処、2026-05-25 セッション 26 利用者明示承認）**：第3過程の進行ロジックは LLM が担うが、各 trigger_map エントリの参照先段（`<YAML ファイル>#<段名>` 形式）の実 actor は **当該段定義（`stages/<YAML>.yaml` の `stages` 配列のうち該当段の `actor` フィールド）から動的に解決** する。段定義の `actor` フィールドが単一正本で、trigger_map 側には actor を二重記述しない（Req 1 受入 5 の「YAML 1 箇所修正で完結」の趣旨と整合）。動的解決の挙動：

- 参照先段の actor が `llm`：第3過程の進行ロジックが当該段の完了判定を実施
- 参照先段の actor が `human`：作業を停止し、`stages/in-progress/` ファイルに「人間承認待ち」を記録して待機（Req 5 受入 3〜4）
- 参照先段の actor が `proxy_model`：`reviewcompass.yaml#human_proxy.proxy_allowed` の許可条件を満たす場合のみ proxy_model が代行（§段集合の静的列挙モデル §2 の approval 段の記述と整合）

これにより Req 5 受入 3〜4 の機械強制が段定義 `actor` フィールドという単一正本に基づき動作する。

連鎖再実施対象は「根本原因フェーズの整合ゲート」から「起点フェーズの整合ゲート」まで、上流から下流へ順に並べる。起点フェーズまで再実施することで、上流変更が下流に正しく伝播したかを機械判定できる（計画書 §5.6 連鎖再実施の対象範囲）。

### 3. actor=human 段での自動停止（Req 5 受入 3〜4）

LLM が trigger_map に沿って連鎖を進めるとき、`actor=human` の段（`intent.yaml#approval`、`feature-partitioning.yaml#approval`、`requirements.yaml#approval` 等）に到達した時点で **作業を停止し、`stages/in-progress/` ファイルに「人間承認待ち」を記録して待機する**。

人間承認なしに次の段への進行を許さない（fail-closed、Req 5 受入 4）。これは「LLM が intent を勝手に書き換えて承認なしで進む」リスクを構造的に止めるため。

待機中の `stages/in-progress/reopen-procedure-<日付>.yaml` の例：

``\`yaml
process_id: reopen-procedure
started_at: 2026-05-25T14:00:00+09:00
trigger: D-1（設計段で要件段の不整合発見）
classification_basis: docs/reviews/reopen-classification-2026-05-25.md
completed_steps: [第1過程：判定とフラグ差し戻し, 第2過程：正本修正]
next_step: 第3過程：連鎖再実施
pending_gates:
  - stages/requirements.yaml#alignment   # actor=llm、機械判定で進行
  - stages/requirements.yaml#approval    # actor=human、ここで停止
  - stages/design.yaml#alignment
  - stages/design.yaml#approval
current_blocker: stages/requirements.yaml#approval（人間承認待ち）
``\`

### 4. 種別判定の根拠保存（Req 5 受入 5）

reopen の第1過程で、種別判定の根拠を `docs/reviews/reopen-classification-<日付>.md` として保存する。第3過程はこの判定ファイルを読み込んで `trigger_map` から連鎖再実施対象を決定する。

種別判定根拠ファイルの最低限の構造：

``\`markdown
---
date: 2026-05-25
classifier: claude_code_main_session
classification: D-1
trigger_source: design/triad-review で発見した要件段の不整合
---

## 分類根拠
- 発見段：design.triad-review
- 影響範囲：要件段の Requirement X の語彙が design.md と矛盾
- 上流戻り：requirements 段への修正が必須
- 連鎖：requirements の修正後、design の再整合を要する → D-1
``\`

判定が後で誤りと分かった場合、reopen 自体をやり直す（`stages/in-progress/` ファイルを新しいものに置き換え、旧ファイルは削除せず証跡として保全）。

### 5. 再オープン手続きの 4 過程構成（A-001 対処、2026-05-28 セッション 37）

本機能が管理する再オープン手続きの全体構成を、現在の 5 段ワークフロー（drafting → triad-review → review-wave → alignment → approval）に合わせて 4 つの過程で定義する。正本は計画書 §5.6.1、運用手順は `docs/operations/REOPEN_PROCEDURE.md`。素材（先行プロジェクトの `workflow-repair-procedure.md`）の 10 ステップは旧ワークフロー前提だったため、現行構造に再構成した。各過程は「停止せず連続実行できる作業の単位」とし、人の承認点で締める。

| 過程 | 作業 | 停止点 |
|---|---|---|
| 1：判定とフラグ差し戻し | 種別判定 → trigger_map で再実施対象決定 → 根拠記録 → 進行中ファイル発行 → spec.json のフラグ差し戻し（reopened／recheck、上流・下流の対象段を false に） | フラグ差し戻しを人が承認（コミットなし） |
| 2：正本修正 | 上流フェーズの正本を修正 | コミット（第1過程＋第2過程をまとめて） |
| 3：連鎖再実施 | 依存順に上流→下流で alignment（波及チェック）→ 波及あれば triad-review、なければ approval | 各 approval、全完了後にコミット |
| 4：完了 | 整合性の最終確認 → recheck クリア → 進行中ファイルを completed へ | コミット |

spec.json の `reopened`／`recheck` の更新の詳細は §機能依存マップモデルでなく計画書 §5.24.8.1 を正本参照する。`reopened` は 6 フェーズ（intent／feature-partitioning／requirements／design／tasks／implementation）を対象とする。

**`reopen-procedure.yaml` への反映**：本 4 過程構成を `stages/reopen-procedure.yaml` の段集合として静的列挙する（tasks 段 T-003／T-007 の実装対象）。素材由来の「10 ステップ」という数え方ではなく、現行の 4 過程構成を正とする。trigger_map（§2）は本構成の第3過程（連鎖再実施）で参照される。

**暫定版**：本構成は計画書 §5.6.1 と同じく暫定版で、dogfooding の運用で見直す。

**A-001（再オープン手続きが design 未定義）の対処状況**：本節の追加により、tasks.md T-003／T-007 が参照する再オープン手続きの段集合が design.md に明示された。tasks.md 側の「10 ステップ静的列挙」という記述、および design.md 本文に残っていた「第 7 段／第 6 ステップ」等の旧表記は、本手続き（種別 A-2）を用いた再オープン処理で「4 過程構成」に統一済み（2026-05-28、第2過程）。

## session 跨ぎ状態管理モデル（Session-Spanning State Model）— Req 6

### 1. 進行中状態ファイルの構造（Req 6 受入 1〜2）

現在進行中の手続きは `stages/in-progress/<process_id>-<日付>.yaml` で表す。ファイル名は「手続き ID」と「開始日付」で一意化する。

最低限のフィールド（Req 6 受入 2）：

| フィールド | 内容 |
|---|---|
| `process_id` | 手続きの識別子（`reopen-procedure`／`requirements-review-wave` 等） |
| `started_at` | 開始時刻（ISO 8601） |
| `trigger` | 開始の契機（人間可読の短い説明） |
| `completed_steps` | 完了済みステップの番号リスト |
| `next_step` | 次に実施すべきステップの番号 |
| `pending_gates` | 残ゲートのリスト（`stages/<ファイル>#<段名>` 形式） |

任意の追加フィールド：`classification_basis`（reopen の場合、種別判定根拠ファイルへのリンク）、`current_blocker`（人間承認待ちの場合、停止位置）、`escalation_status`（通知済みか否か）など。

### 2. session 開始時の標準フロー（Req 6 受入 3）

session 開始時、次を順に行う：

1. `TODO_NEXT_SESSION.md` を読み、全体の到達点を把握
2. 直近の `docs/sessions/session-*.md` を読み、TODO に圧縮された経緯の詳細を確認
3. `git log --oneline -10` ／ `git status` で直近の到達点と未コミット変更を確認
4. 検査スクリプトを `stages/*.yaml` 全件に走らせる（フェーズ 1 段階では人手で `check-workflow-action.py` を呼ぶ）
5. `stages/in-progress/` の有無を確認
6. 進行中手続きがあれば、それを優先的に完了させる（無視して新規作業を始めない）
7. 完了済み・未着手の状態に基づき、次の作業を決定

本フローは運営ガイド `docs/operations/SESSION_WORKFLOW_GUIDE.md` §1 必読フローと一体運用する。

### 3. セッション記録の保存（Req 6 受入 6）

原則として毎 session、特に重要な判断・承認・レビュー結果・修正経緯が発生した session は、セッション終了時または重要判断後に `docs/sessions/session-<N>-<YYYY-MM-DD>.md` へ要約記録を残す。記録は会話全文の逐語ログではなく、後で判断経緯を再構成できる運用記録とする。`<N>` は `docs/sessions/` に存在する既存の最大セッション番号に 1 を加えた番号とし、同じ番号を再利用しない。1 session につき 1 ファイルとし、同一 session 内の重要判断は同じファイルへ追記する。並行 session や未コミット作業により採番が衝突した場合、メインセッション LLM は既存記録・git 状態・未コミット差分を確認し、利用者が採番を確定するまで正式な新規セッション記録を作成しない。採番確定前に記録が必要な場合は、`docs/sessions/drafts/session-<YYYY-MM-DD>-<short-topic>.md` に一時草案を置き、正式番号確定後に `docs/sessions/session-<N>-<YYYY-MM-DD>.md` へ移動する。移動後は draft ファイルを残さず、正式ファイルに草案内容が統合済みであることを確認する。

メインセッション LLM はセッション記録の草案作成責任を持つ。利用者判断の引用・承認範囲・未確定事項に曖昧さがある場合は、記録前に利用者へ確認する。コンテキスト切れや中断により当該 LLM が記録できない場合、次 session が草案を引き継ぐ。草案がない場合は、TODO、review-run、approval record、git diff から経緯を再構成して記録する。

`TODO_NEXT_SESSION.md` は次セッション開始時の入口メモであり、詳細経緯の正本ではない。詳細経緯は `docs/sessions/`、API レビューの raw/parsed/triage は各 review-run ディレクトリ、承認記録は approval record に分けて保持する。

### 4. 完了時の移動（Req 6 受入 4）

手続きが完了したら、`stages/in-progress/<process_id>-<日付>.yaml` を `stages/completed/` に移動するか削除する。移動を採用する利点は「過去の手続きの記録が残り、事後監査に使える」こと、削除を採用する利点は「ディレクトリが肥大化しない」こと。本フェーズでは移動を既定とし、定期的に古いものを `docs/archive/in-progress/` 配下に退避する運用とする。

### 5. 進行中状態と不可逆操作の関係（Req 6 受入 5）

`stages/in-progress/` に何かファイルがある状態での不可逆操作実行を遮断する（fail-closed、Req 4 と整合）。これは「進行中の手続きを放置して別の不可逆操作を始める」失敗モードを防ぐため。

例外：進行中状態ファイル自体の更新（次ステップ進行、人間承認の記録）は遮断対象外。これらは進行中の手続きを進めるための更新であり、別の不可逆操作とは区別する。

## 多層防御の位置付けモデル（Multi-Layered Defense Positioning Model）— Req 7

### 1. 第 1 層の限界の明文化（Req 7 受入 1）

本機能（軽量版 YAML 検査機構）は多層防御の **第 1 層** に位置付ける。第 1 層が解決しない失敗モードを次のように明文化する：

| 失敗モード | 発生原因 | 補完する層 |
|---|---|---|
| 中身の空疎 | 必須節は存在するが内容が「特に問題なし」のみ | 第 3 層（フェーズ境目の利用者監査）、第 4 層（定期事後監査） |
| 検査スクリプト呼び出し依存 | LLM が検査を呼ばない、結果を読まない | 第 2 層（git フック）、補助層 C 段階 3（Claude Code フック） |
| in-progress ファイルの自己申告性 | 「進行中」「次ステップ」を書くのは LLM 自身、嘘・古い・欠落の余地 | 第 3 層、第 4 層 |
| 文脈圧力下での規律低下 | 規律ファイルを増やすほど LLM が優先度を下げる | 第 5 層（処理表面積の抑制方針）、補助層 C |

これらは多層防御の他層で補完し、第 1 層単独で 100% の遵守を達成しようとしない。

### 2. 第 2〜5 層への参照（Req 7 受入 2、計画書 §5.8）

第 2〜5 層はフェーズ 4 以降の宿題として参照する：

- **第 2 層：git フックによる外部強制**：検査スクリプトを `pre-commit`／`pre-push` フックに組み込み、LLM が「呼ばない」選択を構造的に不可能にする
- **第 3 層：フェーズ境目の利用者監査**：フェーズの境目で利用者が検査結果を必ず確認する手続きを必須化
- **第 4 層：定期事後監査**：一定 session 数または期間ごとに独立 LLM で過去証跡全件を監査
- **第 5 層：処理表面積の抑制方針**：「新規規律を追加するときは既存規律 1 つ以上を統廃合する」等の縮減義務

本機能は第 2〜5 層の具体実装を持たないが、設計時に **将来導入する余地を残す** ことを明示する。例：段集合 YAML の `completion_predicate` 述語集合は第 2 層の git フックから直接呼び出せる構造とする（CLI からもフックからも同じスクリプトを呼ぶ）。

### 3. 補助層 A／B／C の位置付け（計画書 §5.8、§5.12、§5.13）

第 1 層と第 2 層の中間に補助層を 3 つ置く：

- **補助層 A：人間代役機構（§5.12）**：軽い判断を外部モデルが代行、本人関与の頻度を下げる
- **補助層 B：人間への通知機構（§5.13）**：本人判断が必要な場面で外部チャネル（メール・LINE 等）に即時通知
- **補助層 C：処理開始時のワークフロー事前検査（§5.8 補助層 C、3 段階共存モデル）**：本機能の検査スクリプトがその実体

補助層 C は本機能の検査スクリプトを段階 2 として持ち、段階 1（LLM 規律）と段階 3（Claude Code フック）から呼ばれる。本機能は段階 2 の実装を所有し、段階 1 の規律化と段階 3 のフック実装は別経路で進める。

### 4. 第 5 層運用ルールの反映（Req 7 受入 3）

第 5 層（処理表面積の抑制方針）の運用ルール「新規規律を追加するときは既存規律 1 つ以上を統廃合する」を本機能の運用ルールに反映する。フェーズ 4 までは利用者の意識に依拠（機械強制は第 5 層導入時に検討、Req 7 受入 3）。

本機能の段集合 YAML を変更する場合：

- 段の追加：既存段の統廃合または明確な根拠を運用文書に記録
- 段の改廃：影響を受ける機能（依存先・依存元）の確認と整合
- 述語の追加：既存述語との重複確認、検査スクリプトの拡張

これらは現時点では運用上の規律としてのみ存在し、機械検査の対象ではない。

### 5. 第 1 層の限界の運用文書への明示（Req 7 受入 4）

第 1 層の限界を運用文書（`docs/operations/WORKFLOW_PRECHECK.md`）に明示し、利用者の期待値を整える。「本検査スクリプトは中身の妥当性を判定しない」「結論不能なら必ず遮断する」「補助層 A／B／C と第 2〜5 層で補完する」の 3 点を最低限明示する。

## 機能依存マップモデル（Feature Dependency Map Model）— Req 8

### 1. 一元保管先（Req 8 受入 1、計画書 §5.5 選択肢 X）

機能間の処理順と依存関係を `stages/feature-dependency.yaml` に一元化する。各フェーズの YAML はこのファイルを参照し、重複させない。

### 2. ファイル構造（Req 8 受入 2）

最低限のフィールド：

``\`yaml
features:
  foundation:
    depends_on: []
  runtime:
    depends_on: [foundation]
  evaluation:
    depends_on: [foundation, runtime]
  analysis:
    depends_on: [foundation, evaluation]
  workflow-management:
    depends_on: [foundation, runtime, evaluation, analysis]
  self-improvement:
    depends_on: [foundation, workflow-management]
  conformance-evaluation:
    depends_on:
      foundation: hard                  # 連想配列構造、依存種別あり
      runtime: review
      evaluation: review
      workflow-management: review

phase_order:
  - foundation
  - runtime
  - evaluation
  - analysis
  - workflow-management
  - self-improvement
  - conformance-evaluation
``\`

**`phase_order` 7 機能採用の根拠（A-001 対処、2026-05-25 セッション 26 利用者明示承認）**：計画書 §5.5 の `phase_order` 構造例（行 376〜383）には self-improvement が記載漏れで 6 機能のみ列挙されている。本設計は次の確定事項に基づき `phase_order` に self-improvement を含めて **7 機能** を採用する：

- 計画書 §3.1（self-improvement の workflow 層改善を第 1 期に含める確定）
- 計画書 §5.16（self-improvement の全面書き直し方針）
- A-007 案 2（2026-05-23 利用者承認による本機能と self-improvement の権限分散調停、規律ファイルの提案権と実体変更権の分離）
- 全 7 機能の requirements 段 approval 完了（2026-05-24 セッション 23 末）

計画書 §5.5 の構造例の補正は計画書全体管理の責務範囲で、本機能の責務範囲外。本セッション末尾の TODO_NEXT_SESSION.md に「計画書 §5.5 phase_order の self-improvement 追記」を補正課題として記録する。

`depends_on` は次の 2 形式を許容する（Req 8 受入 2 後段）：

- **単純リスト構造**：`[foundation, runtime]` のように依存先を列挙するだけ
- **連想配列構造**：`foundation: hard, runtime: review` のように依存種別（`hard`／`review`）を併記。`conformance-evaluation` のように依存性の強度を区別する機能で使う

依存種別の語彙：

- `hard`：その機能の仕様が変わると本機能の仕様も影響を受ける（必須整合）
- `review`：その機能の出力を本機能がレビュー対象とする（参照関係）

### 3. 各フェーズ YAML からの参照（Req 8 受入 3）

各フェーズの YAML（`requirements.yaml`／`design.yaml`／`tasks.yaml`／`implementation.yaml`）の草案段とレビュー波段は `feature_order: feature-dependency.yaml#phase_order` の参照を持つ。検査スクリプトはこの参照を解決して機能名を順に展開する。

### 4. 変更の一元化（Req 8 受入 4）

機能の追加・削除や依存関係の変更は本ファイル 1 箇所の修正で完結する。各フェーズの YAML を個別に修正する必要はない。これにより、新機能追加時の整合漏れを構造的に防ぐ。

### 5. 所有者の明示（Req 8 受入 5）

機能間依存マップの所有者は本機能（`workflow-management`）であり、`runtime`／`evaluation` 等の他機能は再定義せず参照のみとする。他機能の design.md／tasks.md で「依存関係を独自に定義する」記述があれば、本機能の `feature-dependency.yaml` を正本として参照する形に統一する。

### 6. パース仕様と依存種別の機械処理上の意味（A-004 対処、2026-05-25 セッション 26 利用者明示承認）

検査スクリプトが `feature-dependency.yaml` を解析する際の規則と、依存種別（`hard` ／ `review`）の機械処理上の意味を次のとおり確定する。

**パース仕様**：

- `depends_on` の値が YAML パーサで配列（`list`）として解釈できる場合は **単純リスト構造**（例：`[foundation, runtime]`）と判定する
- `depends_on` の値が YAML パーサで辞書（`dict` ／ `mapping`）として解釈できる場合は **連想配列構造**（例：`foundation: hard, runtime: review`）と判定する
- 上記以外の型（文字列、整数、null、ネスト構造等）は結論不能とし、検査スクリプトは DEVIATION（exit 2）を返す（fail-closed、Req 2 受入 4 と整合）

**連想配列構造の値域**：

- 値は `hard` または `review` の 2 値のみ許容する
- それ以外の値（例：`weak`、`strong`、空文字、null）は結論不能とし、DEVIATION を返す
- 将来の依存種別追加（例：`weak`）は、本設計の本節と検査スクリプト実装の両方を同時に更新する

**依存種別の機械処理上の意味**：

- **`hard`（強依存）**：当該依存先の仕様が変更された場合、本機能の `spec.json` の `recheck.upstream_change_pending` を `true` に設定し、`recheck.impacted_downstream_phases` に本機能の下流フェーズ（design／tasks／implementation）を追記する。これにより本機能の下流フェーズの再検査が要求される（reopen 手続きの軽量版として動作）
- **`review`（レビュー対象）**：当該依存先は本機能のレビュー対象として参照されるのみで、依存先の変更は本機能の `recheck` を自動発火しない。レビュー記録の作成時に依存先の最新状態を読むが、依存先の変更が本機能の再検査を必須化しない

**判定述語との関係**：`depends_on_resolves_correctly` 述語は値域チェックのみを担い、依存先の変更検知と `recheck` の更新発火は別の機構（tasks 段で実装、本設計時点ではフェーズ 2 以降の宿題）が担う。本設計では「述語が値域を判定できる」「機械処理上の意味が確定している」までを設計範囲とし、変更検知ロジックの実装は先送り論点として §先送り論点に追加する。

## 主要な設計判断（Interface Decisions）

### 判断 1：段集合は静的列挙、Markdown からの動的解析はしない

理由：素材設計（節ハッシュ・独立再導出パーサ・通過マーカー）は実装コストが高く、フェーズ 1 では維持できない。YAML 静的列挙に置き換えることで実装コストを 1／10 に抑え、Markdown 側との整合は人手で取る前提とする（§5.4 受け入れリスク）。

### 判断 2：検査スクリプトは中身を判定しない

理由：中身の妥当性判定を始めると検査スクリプトの規模が爆発し、第 1 層の本来の責務（証跡＋必須節の機械判定）が薄まる。中身判定は第 3 層（利用者監査）と第 4 層（定期事後監査）に委ね、第 1 層は「形式が揃っているか」のみに絞る。

### 判断 3：fail-closed を全面採用

理由：誤って不可逆操作を許可することによる被害は、検査が pass しないことで作業が止まる不便さを大きく上回る。曖昧なときは止める方針を全段に適用する。

### 判断 4：直前ゲートは最小集合に絞る

理由：機械ゲートをすべての段遷移に置くと、検査スクリプトを呼ぶ頻度が上がり、LLM が「検査を回避する」「結果を読み飛ばす」失敗モードを誘発する。不可逆操作の直前のみに絞ることで、検査の存在感を維持し、回避のコストを上げる。

### 判断 5：reopen 連鎖は actor=human で必ず停止

理由：「LLM が intent を勝手に書き換えて承認なしで進む」リスクは構造的に止めなければならない。trigger_map の連鎖を `actor=human` の段で必ず停止させ、人間承認なしには次に進めない設計とする。

### 判断 6：機能依存マップは 1 ファイル所有

理由：各フェーズの YAML に依存関係を分散させると、新機能追加時の整合漏れが避けられない。1 ファイル所有・他機能は参照のみ、の構造で整合漏れを構造的に防ぐ。

### 判断 7：規律変更は本機能が所定手続き経由で実体変更（A-007 案 2、A-012 対処で時系列契約・完了通知形式を詳細化）

理由：規律ファイル本体の変更権を `self-improvement`（提案権）と本機能（実体変更権）に分散させ、自己承認の空洞化を防ぐ。`self-improvement` が直接ファイル書き換えを行うことを禁じ、必ず本機能の所定手続き（drafting → review → approval）を通す。

**self-improvement との時系列契約・完了通知形式（A-012 対処、2026-05-26 セッション 28 確定、self-improvement design §13.5 の合意点を受け入れ）**：

self-improvement design §13.5 で本機能との接合面の詳細が定義されており、本機能はこの合意点を受け入れる。

- **時系列契約**：
  - `approved` ＝ self-improvement の提案レビュー承認時点
  - `materialized_at` ＝ 本機能の所定手続き完了時点（self-improvement の status は `approved` のまま、本フィールドのみ追記）
- **入力経路**：self-improvement が承認済み提案 YAML を `git mv` で `learning/workflow/approved-updates/` に配置、本機能はこのディレクトリを所定手続きの input として読む
- **完了通知形式**：本機能が所定手続き完了時に `approved-updates/<日付>-<id>.yaml` に次のフィールドを追記：
  - `materialized_at`：ISO 8601 形式の完了時点
  - `materialization_commit_hash`：規律ファイルの実体変更コミットのハッシュ
- **ロールバック責務**：`approved` だが未 `materialized` の状態でロールバックが必要になった場合、self-improvement が `superseded` に遷移させ、本機能に通知する（本機能側で能動的なロールバック実行は不要、状態は self-improvement が管理）
- **整合性検査タイミング**：本機能の `materialized_at` 記録後、self-improvement の遵守検査再実行のトリガーとなる（self-improvement §11.6 と整合）

### 判断 8：補助層 C の段階 2 を本機能が所有

理由：補助層 C 段階 2 の検査スクリプト（`check-workflow-action.py`）は本機能の Req 2 検査スクリプトと実体が同一であり、別経路で同じ機能を実装すると保守コストが二重化する。段階 2 は本機能が単独所有し、段階 1（LLM 規律）と段階 3（Claude Code フック）は段階 2 を呼ぶだけの薄い層とする。

## 要件と設計の対応（Requirements Traceability）

| 要件 | 受入基準 | 対応する設計節 |
|---|---|---|
| Requirement 1：段集合の静的列挙 | 受入 1（YAML 静的列挙、動的解析しない） | §段集合の静的列挙モデル §1〜§2 |
| | 受入 2（9 ファイル体制） | §段集合の静的列挙モデル §1 |
| | 受入 3（段名／actor／証跡パス／必須節／完了判定） | §段集合の静的列挙モデル §2 |
| | 受入 4（feature_order 参照） | §段集合の静的列挙モデル §3、§機能依存マップモデル §3 |
| | 受入 5（YAML 1 箇所修正、Markdown 整合は人手） | §段集合の静的列挙モデル §4 |
| Requirement 2：検査スクリプト | 受入 1（Python 実装） | §軽量版検査スクリプトモデル §1 |
| | 受入 2（証跡＋必須節のみ判定） | §軽量版検査スクリプトモデル §1〜§3 |
| | 受入 3（中身の妥当性判定しない） | §軽量版検査スクリプトモデル §4、§主要な設計判断 判断 2 |
| | 受入 4（結論不能は fail） | §軽量版検査スクリプトモデル §1、§不可逆操作の直前ゲートモデル §3、§主要な設計判断 判断 3 |
| | 受入 5（in-progress 警告） | §軽量版検査スクリプトモデル §2、§session 跨ぎ状態管理モデル §4 |
| Requirement 3：起草者と判定者の分離 | 受入 1（author／reviewer 必須） | §起草者と判定者の分離モデル §1 |
| | 受入 2（identity 同一を許容しない） | §起草者と判定者の分離モデル §1、§3 |
| | 受入 3（subagent_mediated の判定役は別エンティティ） | §起草者と判定者の分離モデル §2 |
| | 受入 4（front-matter 検査、別モデル／別 session は第 1 層対象外） | §起草者と判定者の分離モデル §3 |
| Requirement 4：不可逆操作の直前ゲート | 受入 1（4 種類の不可逆操作） | §不可逆操作の直前ゲートモデル §1 |
| | 受入 2（pass ＋ in-progress 空、毎回独立走行） | §不可逆操作の直前ゲートモデル §2 |
| | 受入 3（fail-closed） | §不可逆操作の直前ゲートモデル §3、§主要な設計判断 判断 3 |
| | 受入 4（最小集合方針） | §不可逆操作の直前ゲートモデル §1、§主要な設計判断 判断 4 |
| Requirement 5：reopen 機械強制 | 受入 1（二次元表記） | §reopen 機械強制モデル §1 |
| | 受入 2（trigger_map） | §reopen 機械強制モデル §2 |
| | 受入 3（actor=human で停止） | §reopen 機械強制モデル §3、§主要な設計判断 判断 5 |
| | 受入 4（人間承認なしに進まない） | §reopen 機械強制モデル §3 |
| | 受入 5（種別判定根拠の保存） | §reopen 機械強制モデル §4 |
| Requirement 6：session 跨ぎ状態管理 | 受入 1（in-progress ファイル） | §session 跨ぎ状態管理モデル §1 |
| | 受入 2（必須フィールド） | §session 跨ぎ状態管理モデル §1 |
| | 受入 3（標準フロー） | §session 跨ぎ状態管理モデル §2 |
| | 受入 4（完了時の移動） | §session 跨ぎ状態管理モデル §3 |
| | 受入 5（in-progress ある状態での遮断） | §session 跨ぎ状態管理モデル §4、§不可逆操作の直前ゲートモデル §2 |
| Requirement 7：多層防御 | 受入 1（第 1 層の限界の明文化） | §多層防御の位置付けモデル §1 |
| | 受入 2（第 2〜5 層を宿題として参照） | §多層防御の位置付けモデル §2 |
| | 受入 3（第 5 層運用ルールの反映） | §多層防御の位置付けモデル §4 |
| | 受入 4（第 1 層の限界の運用文書への明示） | §多層防御の位置付けモデル §5 |
| Requirement 8：機能依存マップの一元化 | 受入 1（feature-dependency.yaml が一元保管先） | §機能依存マップモデル §1 |
| | 受入 2（features ＋ phase_order、2 形式の depends_on） | §機能依存マップモデル §2 |
| | 受入 3（feature_order 参照） | §機能依存マップモデル §3 |
| | 受入 4（1 箇所修正で完結） | §機能依存マップモデル §4、§主要な設計判断 判断 6 |
| | 受入 5（所有者は本機能、他機能は参照のみ） | §機能依存マップモデル §5、§主要な設計判断 判断 6 |

## 下流仕様への影響（Impact on Downstream Specs）

本設計は次の下流仕様に影響を与える：

- **`self-improvement`**：規律変更の提案権と実体変更権の分離（判断 7、A-007 案 2）。`self-improvement` の design.md／tasks.md で「規律ファイルを直接書き換える」記述があれば、本機能の所定手続き経由に変更する必要がある。**時系列契約・完了通知形式は self-improvement design §13.5 と本機能 判断 7 で相互参照（A-012 対処、2026-05-26 セッション 28 確定）**
- **`conformance-evaluation`**：機能依存マップの依存種別（`hard`／`review`）を仕様内で明示する必要（A-005 の conformance-evaluation 側対処、`feature-dependency.yaml` の連想配列構造を Req 7 で参照）
- **全 7 機能の design 段以降**：レビュー記録の front-matter に `author.identity` ／ `reviewer.identity` ／ `separation_from_author` を必須化（Req 3 受入 1）。既存のレビュー記録 7 件（requirements の各機能）はフェーズ 2 の検査スクリプト導入時に遡及検査の対象に含めるか、grandfathering（移行期免除）として扱うかを別途決定する

`evaluation` への影響はなし（評価ロジック本体は `evaluation` が所有、本機能は所定手続きの実行結果に対する評価要求を受けるのみ）。

## 先送り論点（Open Issues Deferred to Later Specs）

本設計で確定せず、後続フェーズで決定する論点：

1. **段集合の変更そのものを不可逆操作の対象とするか**：第 5 層（処理表面積の抑制）導入時に検討（フェーズ 4 以降）
2. **第 2 層 git フックの具体配線**：フェーズ 4 で `pre-commit` ／ `pre-push` のフック実装、本機能の検査スクリプトを再利用する形を想定
3. **第 3 層 利用者監査の具体手順**：フェーズ境目（要件→設計、設計→タスク等）での確認チェックリストを `docs/operations/PHASE_BOUNDARY_AUDIT.md` として別途整備
4. **既存レビュー記録の遡及検査**：Req 3 の front-matter 必須化を既存 7 件（requirements の各機能）に遡及適用するか、grandfathering で免除するか
5. **段階 3 の Claude Code フック実装**：補助層 C 段階 3 はフェーズ 2 以降の宿題、本機能の検査スクリプトとの結合方式を別途設計
6. **規律変更の所定手続きの段集合**：規律変更を `drafting → review → approval` の 3 段で扱うか、`triad-review` を含めるかを A-007 案 2 対応の細部として後続セッションで確定
7. **`stages/cross-spec-alignment.yaml` の段集合**：機能横断整合手続きの段集合は別途確定、本設計では枠のみ確保
8. **規律変更の所定手続きの実装と参照層 5 件の扱い**：A-007 対処で active 必読 12 件は `docs/disciplines/` に移管済み（2026-05-25 セッション 26）。本機能の所定手続きが `docs/disciplines/` 内の規律変更を扱う実装はフェーズ 2 以降。参照層 5 件（feedback_dominant_dominated_options 等）の memory → repo 移管要否は別途判断
9. **運営ガイド等の現行規律本体の改廃手続き**：`docs/operations/SESSION_WORKFLOW_GUIDE.md` 等の運営文書を本機能の所定手続きの対象に含めるかは別論点。フェーズ 2 で `docs/disciplines/` 配置構造との整合とともに整理

## テスト戦略（Test Strategy）

本機能の検証境界を設計段で次のとおり明示する。詳細ケース分解は tasks 段で行う。

- **単体テスト**：
  - 段集合 YAML のパース（壊れた YAML、必須フィールド欠落のケース）
  - 完了述語の判定（`artifact_exists`、`artifact_exists_and_sections_present` 等の各述語）
  - `author.identity` ≠ `reviewer.identity` の文字列比較
  - 手戻り種別の解析（`D-1` → `trigger_map[D-1]` の再実施対象リスト）
  - 進行中状態ファイルの読み書き（必須フィールド欠落の検出）
  - 依存マップの解析（`depends_on` の単純リスト構造と連想配列構造の両方）

- **統合テスト**：
  - 不可逆操作（spec.json 書き込み、commit、push）の直前ゲートが実際に遮断すること
  - reopen 連鎖が `actor=human` 段で停止し、`stages/in-progress/` にファイルが残ること
  - `stages/in-progress/` ある状態での不可逆操作が遮断されること
  - 機能依存マップの 1 箇所修正が各フェーズ YAML の解釈に正しく反映されること

- **異常系 fixture**：
  - YAML パースエラー（壊れた構文）
  - 証跡ファイル不在
  - 必須節欠落
  - `author.identity` ＝ `reviewer.identity` の同一
  - `feature-dependency.yaml` 不在または依存循環
  - 検査スクリプト実行失敗（Python 例外）
  - いずれも fail-closed となることを検証

- **境界条件**：
  - `depends_on: []`（依存先なし）の foundation の扱い
  - `depends_on` の連想配列構造で未知の依存種別（`hard`／`review` 以外）の扱い
  - 進行中状態ファイルが複数存在する場合（複数の `reopen-procedure-*.yaml` 並存）の扱い

- **対象外**：
  - 中身の妥当性判定（判断 2 で明示的に除外）
  - 別モデル・別 session の機械判定（Req 3 受入 4 で除外）
  - 第 2〜5 層の機能（先送り論点 1〜5）

## 完成判定基準（Completion Criteria）

本設計に基づく実装が完成したとみなす条件：

1. `stages/` 配下に 9 ファイル（`intent.yaml`／`feature-partitioning.yaml`／`feature-dependency.yaml`／`requirements.yaml`／`design.yaml`／`tasks.yaml`／`implementation.yaml`／`reopen-procedure.yaml`／`cross-spec-alignment.yaml`）がすべて配置されている
2. `tools/check-workflow-action.py` が 3 サブコマンド（`spec-set`／`commit`／`push`）を提供し、各サブコマンドが exit code 0／1／2 を正しく返す
3. 機能単位 spec.json 7 件（全 7 機能）が `workflow_state` を計画書 §5.24 の正本スキーマで持つ
4. レビュー記録の front-matter 検査が機能横断段（review-wave／alignment）の前提として組み込まれている
5. 進行中状態ファイル（`stages/in-progress/*.yaml`）の有無検査が `git commit`／`git push` の直前ゲートに統合されている
6. 手戻り種別判定の根拠ファイル（`docs/reviews/reopen-classification-*.md`）の雛形が `templates/review/reopen_classification_template.md` として配置されている
7. 運用文書（`docs/operations/WORKFLOW_PRECHECK.md`）に第 1 層の限界が明示されている

フェーズ 1 段階（本設計時点）では条件 1〜3 の最低限（9 ファイル骨格、検査スクリプトの `spec-set` サブコマンド、機能単位 spec.json）が満たされており、条件 4〜7 はフェーズ 2 以降で順次追加する。

## 変更意図（Change Intent）

本設計は先行プロジェクトの `dual-reviewer-implementation-governance/design.md`（466 行、節ハッシュ・独立再導出パーサ・supersedes リンク・通過マーカーの後続確認等を含む大規模機構）を、ReviewCompass の方針（計画書 §5.4〜§5.8）に基づき **思想は継承、実装は 1／10** で再設計した。

### 継承した思想

- 不可逆操作の直前にしか機械ゲートを置かない（fail-closed の最小集合）
- 証跡 artifact の存在＋構造適合で完了を判定する（主張ではなく証拠）
- 起草者と判定者を分ける（自己承認の禁止）
- 検査が結論不能なら遮断（fail-closed の既定）
- 完了判定述語と独立性 marker の分離（素材の小節 2 と小節 3 を §軽量版検査スクリプトモデル §3 と §起草者と判定者の分離モデル §1 に縮約継承）

### 削減・除去した機構（素材から継承しない、§5.4 確定）

- 節ハッシュ（`section_content_hash`）と陳腐化／改竄検知（素材の小節 1.3、§5.4 で削除確定）
- supersedes リンクによる旧台帳保全（素材の小節 1.1、§5.4 で削除確定）
- grandfathering と format-migration の機構（素材の小節 10、§5.4 で削除確定。本設計でも先送り論点 4 として grandfathering の判断は別途）
- 権威マップ（authority-map）と独立再導出パーサ（素材の小節 1.2、§5.4 で削除確定）
- 通過マーカーの後続確認（素材の小節 4 後段、§5.4 で削除確定、二次防御は補助層 C 段階 3 と第 2 層に分離）
- 実行台帳（workflow-execution-ledger）の機構全体（素材の §Workflow Execution Ledger and Enforcement Model、§5.4 で削除確定）
- 上位文書同期（C-1／C-2／C-3 取り込み、素材の小節 6）：人手の整合に置き換え

### ReviewCompass 固有の追加

- 補助層 C 段階 2 として `tools/check-workflow-action.py` を本機能に組み込む（§5.8 補助層 C、計画書 §5.8 採用承認 2026-05-25 セッション 24）
- サブエージェント方式（`mode: subagent_mediated`）への対応を §起草者と判定者の分離モデル §2 に明示（計画書 §5.23.12 由来）
- 規律変更の提案権と実体変更権の分離を §責務境界の明確化と §主要な設計判断 判断 7 に明示（A-007 案 2、2026-05-23 利用者承認）
- 機能依存マップの依存種別（`hard`／`review`）の連想配列構造を §機能依存マップモデル §2 に明示（A-005 対処由来、計画書 §5.5 行 368〜373）
- 検査スクリプトの 3 サブコマンド構成（`spec-set`／`commit`／`push`）と verdict 3 値（OK／WARN／DEVIATION）を §軽量版検査スクリプトモデル §2 に明示（補助層 C 段階 2 仕様 `docs/operations/WORKFLOW_PRECHECK.md` 由来）
- 人間代役機構（proxy_model）による approval 段の代行条件を §段集合の静的列挙モデル §2 に明示（計画書 §5.12.4 由来）
- 規律ファイル本体を `~/.claude/projects/.../memory/feedback_*.md`（Claude Code auto memory 機構の領域）から `docs/disciplines/discipline_*.md`（リポジトリ内 git 追跡対象）へ軽量手続きで移管、12 件（active 必読相当）を移管、memory 側は短い参照索引に置換（2026-05-25 セッション 26、計画書 §5.21 前倒し実施、利用者明示承認）

### 機能横断レビューで対処された所見の反映状況

- **A-005**（feature-dependency 依存記述の連想配列構造）：§機能依存マップモデル §2 で対処済み
- **A-007**（self-improvement との権限分散調停、案 2 採用＋規律ファイルの配置先移管）：§責務境界の明確化、§主要な設計判断 判断 7、ReviewCompass 固有の追加で対処済み。本セッション 26 で軽量手続きにより `docs/disciplines/` への移管も完了（精査により memory ファイルが規律本体であることが判明、技術機構（Claude Code）と内容（ReviewCompass 規律）の二重性を移管で解消）
- **A-011**（analysis／design の 3 役差分集約ファイル、未消化）：本機能の責務範囲外、`analysis`／`evaluation` の design レビュー波段で消化予定（本設計の対処事項に含めない）

### must-fix 所見の対処状況（本セッション 26 triad-review）

主役 19 件＋敵対役独立発見 12 件＝計 31 件の所見のうち、判定役が must-fix と判定した 10 件への対処：

- **F-003**（verdict 語彙 BLOCK → DEVIATION 統一）：機能内対処済み、§全体構造／§軽量版検査スクリプトモデル §2／§変更意図 の 4 箇所
- **F-006**（テンプレート変数の展開規則明示）：機能内対処済み、§段集合の静的列挙モデル §2 末尾に新節追加
- **F-009 ＋ F-010**（commit／push の `--rationale` 必須引数と参照節番号修正）：機能内対処済み、§軽量版検査スクリプトモデル §2 の表と出力形式説明
- **F-016**（「fook」→「フック」タイポ修正）：機能内対処済み、§多層防御の位置付けモデル §3
- **A-001 ＋ A-009**（`phase_order` 7 機能採用の根拠注記、「全 N 機能」を `feature-dependency.yaml#phase_order` 参照に変更）：機能内対処済み、§機能依存マップモデル §2 と §不可逆操作の直前ゲートモデル §1
- **A-002**（trigger_map の `actor` 値域を動的解決に修正）：機能内対処済み、§reopen 機械強制モデル §2
- **A-004**（`depends_on` の連想配列構造のパース仕様と判定述語追加）：機能内対処済み、§軽量版検査スクリプトモデル §3 の述語集合と §機能依存マップモデル §6 新節
- **A-007**（規律ファイル所有先パスと実体配置の不一致）：軽量手続き経由で `docs/disciplines/` への移管実施により解消（本節と §責務境界の明確化に反映）

### triad-review 段への引き継ぎ事項

- 主要な設計判断 8 件（特に判断 1〜4 の fail-closed と最小集合方針、判断 7 の権限分散）の合理性を 3 役レビューで検証
- 先送り論点 7 件（特に論点 4 の grandfathering、論点 6 の規律変更の段集合）の妥当性と漏れの確認
- 素材設計から削減した機構（節ハッシュ・supersedes リンク等）の削減判断が ReviewCompass のリスク受容範囲内であるかの再確認

```

## FILE: .reviewcompass/specs/workflow-management/tasks.md

```text
---
spec: workflow-management
phase: tasks
stage: drafting
author:
  identity: claude-opus-4-7
  role: drafter
created_at: 2026-05-28
language: ja
---

# Tasks Document：workflow-management

## 概要（Overview）

本文書は `workflow-management`（所定手続きの定義と機械強制を担う機能）の実装タスクを列挙する。本機能は、所定手続きの段集合定義、軽量版検査スクリプト、起草者と判定者の分離機械検査、不可逆操作の直前ゲート、reopen 機械強制、session 跨ぎ状態管理、多層防御の第 1 層位置付け、機能依存マップの一元化を担う。計画書 §5.4「軽量化方針」に従い、思想は継承、実装は 1／10 を目標として再設計する。

タスクは設計文書（design.md）の所有モデル単位でまとめ、各タスクは「起草・実装・テスト・コミット」まで一気通貫で完結できる粒度とする。タスクの依存順は design.md §全体構造（リポジトリ内配置の 3 層構造）と各モデル節（Req 1〜8 に対応）に従う。

## タスク粒度と方針（Granularity and Policy）

- **粒度**：1 タスク ＝ 1 つの所有モデル領域。design.md の節と必ずしも 1 対 1 でなく、密接に関連する節は同じタスクにまとめる
- **一気通貫**：1 タスクは「起草・実装・テスト・コミット」まで止めず連続で進められる単位
- **依存順**：前提タスクが完了してから後続タスクに進む
- **自律進行**：実装段で per-task 承認は取らず、コミット・プッシュ・spec.json 更新・フェーズ移行のみ明示承認（規律 [[implementation-autonomy]] 準拠）
- **テスト要件**：成果物は静的検証（YAML スキーマ整合、述語値域、必須節充足、front-matter 異名）と動的検証（fail-closed の遮断、reopen 連鎖の actor=human 停止）で機械的に判定可能とする
- **contract consumer 原則**：foundation が所有する語彙正本を再定義せず参照のみで使用。本機能が実際に参照するのは `review_mode`（レビューモード語彙、front-matter 検査 T-005 で使用）であり、所見系（`counter_status`／`severity`／`final_label`／`confidence_label`）・状態軸系（`run_status`／`validator_status`／`human_signoff_status`／`evidence_class`）は本機能の責務外で参照しない（A-003 対処 2026-05-28）。本機能所有の正本（`completion_predicate` 述語集合 7 値 ／ `verdict` 3 値 OK／WARN／DEVIATION ／ 手戻り種別記号 5 値 N／R／D／A／I ／ 依存種別 2 値 `hard`／`review`）は本機能で確定
- **fail-closed の徹底**：結論不能（YAML パースエラー、必須フィールド欠落、未知の値）の場合は合格判定を出さず必ず fail を返す（判断 3 全面採用）

`workflow-management` 全体で 11 タスク。

## タスク一覧（Task List）

### T-001：成果物配置の準備

- **対応設計節**：design.md §全体構造、§段集合の静的列挙モデル §1
- **対応要件**：Requirement 1 受入 1（段集合の静的列挙）、Requirement 6 受入 1（進行中状態ファイル配置）
- **責務**：リポジトリ内に `stages/` ディレクトリと配下の 9 ファイル骨格、`stages/in-progress/` と `stages/completed/` の 2 サブディレクトリ、検査スクリプト配置先 `tools/`、ログ書き出し先 `docs/logs/`、reopen 種別判定根拠ファイル配置先 `docs/reviews/`、種別判定根拠ファイル雛形配置先 `templates/review/` を新設し、各ディレクトリに配置目的を記す README を置く。`stages/in-progress/.gitkeep` と `stages/completed/.gitkeep` で空ディレクトリを Git 追跡可能にする（foundation T-001 ／ runtime T-001 ／ evaluation T-001 ／ analysis T-001 の方針継承）
- **前提タスク**：なし（起点）
- **成果物**：
  - `stages/README.md`
  - `stages/in-progress/.gitkeep`
  - `stages/in-progress/README.md`
  - `stages/completed/.gitkeep`
  - `stages/completed/README.md`
  - `docs/logs/README.md`（`workflow-precheck.log` の所在説明、初版は空ログ）
  - `docs/reviews/README.md`（`reopen-classification-<日付>.md` の所在説明）
  - `templates/review/reopen_classification_template.md`（reopen 種別判定根拠ファイルの雛形＝空の骨格を配置。内容の確定は T-007 が担い、本ファイルの成果物所有は T-001 単独、A-010 対処 案 2 2026-05-28）
  - `docs/operations/WORKFLOW_MANAGEMENT.md`（アプリ側規約節を追記、計画書 §5.4〜§5.8 由来）
  - `tools/README.md`（検査スクリプト配置先 `tools/` の説明、実体 `.py` は T-004 で配置。`tests/` との対称化、F-017 対処 2026-05-28）
  - `tests/workflow-management/.gitkeep`
- **完了条件**：
  1. `stages/` 配下のディレクトリ構造（直下 9 ファイル骨格 ＋ `in-progress/` ＋ `completed/`）と各 README が存在し、`docs/operations/WORKFLOW_MANAGEMENT.md` に配置規約が記述されている。`tools/` ディレクトリに README が存在し Git 追跡可能である（F-017 対処 2026-05-28）
  2. `templates/review/reopen_classification_template.md` が design.md §reopen 機械強制モデル §4 の最低限の構造（front-matter ＋分類根拠節）を満たす
  3. `tests/workflow-management/.gitkeep` が Git に追跡可能な状態である
- **テスト要件**：ディレクトリ存在検査、README 存在検査、`reopen_classification_template.md` 必須節検査、`.gitkeep` 存在検査

### T-002：機能依存マップ（feature-dependency.yaml）

- **対応設計節**：design.md §機能依存マップモデル §1〜§6、§主要な設計判断 判断 6
- **対応要件**：Requirement 8 受入 1〜5
- **責務**：`stages/feature-dependency.yaml` を作成、7 機能（foundation／runtime／evaluation／analysis／workflow-management／self-improvement／conformance-evaluation）の `features.<機能>.depends_on` と `phase_order` を一元保管。`depends_on` の 2 形式（単純リスト構造 ／ 連想配列構造）を許容し、`conformance-evaluation` のみ連想配列構造（`hard` ／ `review` 併記）。`phase_order` は 7 機能を依存マップ順で列挙。本機能が単独所有・他機能は再定義せず参照のみ、を運用文書に明示
- **前提タスク**：T-001
- **成果物**：
  - `stages/feature-dependency.yaml`（features ＋ phase_order）
  - `stages/feature-dependency.schema.json`（パース仕様の正本：単純リスト構造 ／ 連想配列構造の許容、値域 `hard` ／ `review` の 2 値、それ以外は結論不能）
  - `docs/operations/WORKFLOW_MANAGEMENT.md` の §機能依存マップ節（所有者明示、改廃ルール）
- **完了条件**：
  1. `feature-dependency.yaml` の `features` に 7 機能すべてが列挙、`phase_order` が 7 機能を依存マップ順で列挙
  2. `conformance-evaluation` の `depends_on` が連想配列構造で `foundation: hard ／ runtime: review ／ evaluation: review ／ workflow-management: review` を保持
  3. `feature-dependency.schema.json` が JSON Schema として meta-schema 検証を通る、`hard` ／ `review` 以外の値が結論不能になることが機械検証される
  4. 単純リスト構造と連想配列構造の両方が同一スキーマでパース可能であることが機械検証される
- **テスト要件**：スキーマ検証、7 機能列挙テスト、依存マップ順テスト、連想配列構造の値域テスト（`hard` ／ `review` ／ 不正値 `weak` ／ 空文字 ／ null の 5 ケース）、依存循環検出テスト

### T-003：段集合 YAML 8 ファイル（9 ファイル体制のうち feature-dependency.yaml を除く）

- **対応設計節**：design.md §段集合の静的列挙モデル §1〜§4、§テンプレート変数の展開規則
- **対応要件**：Requirement 1 受入 1〜5、Requirement 5 受入 1〜5（reopen-procedure.yaml の構造）
- **責務**：`stages/` 配下に 8 ファイル（`intent.yaml` ／ `feature-partitioning.yaml` ／ `requirements.yaml` ／ `design.yaml` ／ `tasks.yaml` ／ `implementation.yaml` ／ `reopen-procedure.yaml` ／ `cross-spec-alignment.yaml`）を作成。各 YAML は段集合（段名・`actor`・`artifact_paths`・`required_sections`・`completion_predicate`）を静的列挙、機能横断段は `feature_order: feature-dependency.yaml#phase_order` を参照。テンプレート変数（`{feature}` ／ `{phase}` ／ `{日付}`）の展開規則は設計書 §テンプレート変数の展開規則に従う。`reopen-procedure.yaml` に `trigger_map` を持たせ（第3過程で参照）、種別記号 N／R／D／A／I × 深さの二次元表記から再実施対象を機械的に決定。`cross-spec-alignment.yaml` は段集合本体を後続フェーズで確定する旨を YAML コメントに明記、枠のみ確保
- **前提タスク**：T-001、T-002（`feature_order` 参照先）
- **成果物**：
  - `stages/intent.yaml`（drafting／review／approval の 3 段、actor=human／llm／human）
  - `stages/feature-partitioning.yaml`（candidate-proposal／approval の 2 段、actor=llm／human）
  - `stages/requirements.yaml`（drafting／triad-review／review-wave／alignment／approval の 5 段、機能横断段 3 段は `feature_order` 参照）
  - `stages/design.yaml`（同 5 段）
  - `stages/tasks.yaml`（同 5 段）
  - `stages/implementation.yaml`（同 5 段）
  - `stages/reopen-procedure.yaml`（4 過程構成、`trigger_map` ＋ `actor_resolution: per_target_stage` を第3過程で参照）
  - `stages/cross-spec-alignment.yaml`（枠のみ、段集合は後続フェーズで確定）
  - `stages/stage_schema.json`（段集合 YAML 共通スキーマ：段名・actor・artifact_paths・required_sections・completion_predicate・feature_order・front_matter_required）
- **完了条件**：
  1. 8 ファイルすべてが配置、各 YAML が `stage_schema.json` で構造検証を通る。`stage_schema.json` は `completion_predicate` を 7 値（design §軽量版検査スクリプトモデル §3 確定）に、`actor` を 3 値（`human` ／ `llm` ／ `proxy_model`、design §段集合 §1／§3 確定）に enum で値域制限し、いずれも未知の値が DEVIATION（fail-closed）になることが機械検証される（F-015／A-004 対処 2026-05-28）
  2. 機能横断段（review-wave／alignment／approval）が `feature_order: feature-dependency.yaml#phase_order` を参照、機能単位段（drafting／triad-review）は `feature_order` を持たない
  3. `reopen-procedure.yaml` の `trigger_map` が手戻り種別 N-0 ／ R-0〜1 ／ D-0〜2 ／ A-0〜3 ／ I-0〜4 の全 15 種について再実施対象段リストを保持
  4. `trigger_map` 各エントリの参照先段（`<YAML ファイル>#<段名>` 形式）が、`actor_resolution: per_target_stage` により段定義から動的解決可能であることが機械検証される
  5. テンプレート変数 `{feature}` ／ `{phase}` ／ `{日付}` の展開元と解決規則が `stage_schema.json` の構造化フィールド（各変数の展開元を列挙する `template_vars` 等）に格納され、フィールドの存在が機械検証される（自由記述コメントの grep ではなく構造化、F-010 対処 案 2 2026-05-28）
- **テスト要件**：8 ファイルすべての構造検証、`feature_order` 参照解決テスト、`trigger_map` 全 15 種テスト、テンプレート変数展開テスト（3 種それぞれ）、`cross-spec-alignment.yaml` の枠のみ確保テスト、`completion_predicate` 値域 7 値テスト（7 値 OK ＋ 未知値 DEVIATION）、`actor` 値域 3 値テスト（human ／ llm ／ proxy_model OK ＋ 未知値 DEVIATION、F-015／A-004 対処 2026-05-28）

### T-004：軽量版検査スクリプト本体（補助層 C 段階 2）

- **対応設計節**：design.md §軽量版検査スクリプトモデル §1〜§4、§主要な設計判断 判断 2 ／ 判断 3 ／ 判断 8
- **対応要件**：Requirement 2 受入 1〜5、Requirement 4 受入 2 ／ 3（fail-closed と独立走行）
- **責務**：`tools/check-workflow-action.py` を Python で実装。3 サブコマンド（`spec-set <feature> <phase> <stage> <new_value> [--rationale "..."]` ／ `commit --rationale "..."` ／ `push --rationale "..."`）と `--json` 出力オプションを提供。verdict 3 値（OK／WARN／DEVIATION）と exit code（0 ／ 1 ／ 2）の対応。`completion_predicate` 述語集合 7 値（`artifact_exists` ／ `artifact_exists_and_sections_present` ／ `artifact_exists_and_sections_present_and_author_reviewer_distinct` ／ `all_features_drafting_and_triad_review_completed` ／ `cross_spec_alignment_passed` ／ `explicit_human_approval_recorded` ／ `depends_on_resolves_correctly`）の判定ロジックを符号化。fail-closed の既定（YAML パースエラー ／ 証跡欠落 ／ 必須フィールド欠落 ／ `feature_order` 解決失敗の全ケースで遮断）を全面採用。`docs/logs/workflow-precheck.log` への追記、出力形式は `[VERDICT]` ／ `[ACTION]` ／ `[REASON]` ／ `[CURRENT STATE]` の 4 ブロック大括弧付きラベル形式
- **前提タスク**：T-001、T-002、T-003
- **成果物**：
  - `tools/check-workflow-action.py`（argparse 定義 ＋ 3 サブコマンド ＋ `--json` ＋ ログ追記）
  - `tools/check_workflow_action/predicates.py`（`completion_predicate` 述語集合 7 値の判定ロジック）
  - `tools/check_workflow_action/yaml_loader.py`（YAML 読み込み ＋ パースエラー fail-closed）
  - `tools/check_workflow_action/output_formatter.py`（4 ブロック大括弧付きラベル形式 ／ JSON 形式）
  - `docs/operations/WORKFLOW_PRECHECK.md`（補助層 C 段階 2 正本仕様：§5 サブコマンド引数 ／ §7 出力形式 ／ §8 ログ）
- **完了条件**：
  1. 3 サブコマンドが exit code 0 ／ 1 ／ 2 を正しく返す
  2. 述語 7 値すべてが正常系で OK、異常系（証跡欠落 ／ 必須節欠落 ／ 異名不成立 等）で DEVIATION を返す
  3. YAML パースエラー時に DEVIATION（exit 2）を返す（fail-closed）
  4. `--rationale` が `commit` ／ `push` で必須引数として強制される（省略時はエラー）。`spec-set` の `--rationale`（任意）を省略した場合もログ記録が正しく行われる（F-013 対処 2026-05-28）
  5. ログ追記が `docs/logs/workflow-precheck.log` に発生、4 ブロックラベル形式と JSON 形式の両方が正しく出力される
  6. `explicit_human_approval_recorded` 述語は `actor=proxy_model` の場合 `reviewcompass.yaml#human_proxy.proxy_allowed` を参照して代行可否を機械判定する（条件を満たさなければ DEVIATION）。`depends_on_resolves_correctly` 述語は値域チェック（依存先の解決可能性）のみを担い、依存先の変更検知と recheck 更新発火は別機構（フェーズ 2 宿題、DVT-W007）であることを境界テストで明示する（A-004／A-006 対処 2026-05-28）
  7. review-run の proxy_model 判断代行ゲートは、`approval-proxy-<日付>.yaml`、`proxy-decisions/<finding-id>.decision.yaml`、decision prompt、元 review raw、raw response、候補案、採用案、判断理由、最終ラベルを検査し、欠落または triage との不一致があれば DEVIATION にする。proxy_model 代行は実装方針判断に限定し、コミット・プッシュ・spec.json 更新・フェーズ移行には使わない
- **テスト要件**：3 サブコマンド × 各 verdict 3 値 = 9 ケース、述語 7 値の正常系 ／ 異常系テスト、YAML パースエラーの fail-closed テスト、`--rationale` 必須化テスト（commit／push）＋ `spec-set` 省略時ログ記録テスト（F-013）、ログ追記テスト、4 ブロックラベル形式 ／ JSON 出力テスト、`explicit_human_approval_recorded` の proxy_model 代行可否テスト（proxy_allowed 満たす／満たさないの 2 ケース、A-004）、`depends_on_resolves_correctly` の境界テスト（値域チェックのみで変更検知しないことの確認、A-006）、proxy_model 判断代行ゲートの正常系／raw 欠落／候補案欠落／採用案欠落／判断理由欠落／triage 不一致の fail-closed テスト

### T-005：起草者と判定者の分離 機械検査

- **対応設計節**：design.md §起草者と判定者の分離モデル §1〜§3
- **対応要件**：Requirement 3 受入 1〜4
- **責務**：レビュー記録の front-matter 検査機能を `tools/check_workflow_action/front_matter_checker.py` として実装、`completion_predicate=artifact_exists_and_sections_present_and_author_reviewer_distinct` から呼び出される。判定 3 点：(1) `author.identity` ／ `reviewer.identity` フィールドの存在、(2) `author.identity` ≠ `reviewer.identity`（文字列比較）、(3) `reviewer.separation_from_author=true`。`mode: subagent_mediated` の場合の `role` フィールド複合役（`drafter_and_primary_reviewer` 等）を許容する暫定特例を符号化。別モデル ／ 別 session の機械判定は範囲外（第 3 層利用者監査に委ねる、Req 3 受入 4）であることを運用文書に明示
- **前提タスク**：T-004
- **成果物**：
  - `tools/check_workflow_action/front_matter_checker.py`（3 点判定ロジック）
  - `tools/check_workflow_action/front_matter_schema.json`（必須フィールド：type ／ target ／ target_commit ／ target_content_hash ／ date ／ mode ／ author ／ reviewer、author/reviewer の必須サブフィールド：identity ／ model ／ role、reviewer.separation_from_author=true 必須）
  - `docs/operations/WORKFLOW_PRECHECK.md` §front-matter 検査節
- **完了条件**：
  1. 3 点判定が機械検証で確実に発火する（異名のみ／同名／separation_from_author=false の 3 ケース）
  2. `subagent_mediated` の複合役（`drafter_and_primary_reviewer`）が許容される
  3. 既存レビュー記録 7 件以上（各機能の requirements ／ design ／ tasks）への本検査の遡及適用は、grandfathering（遡及検査の免除）判断（DVT-W002、利用者承認事項）が確定するまで検査対象から除外する（未確定のまま走らせて既存記録が DEVIATION を返し本機能のゲートが自己ロックするのを回避）。本完了条件としては「DVT-W002 のエントリが DVT 表に存在すること」を grep で機械検証する（実装作業と人手判断を分離、F-009／A-007 対処 2026-05-28）
- **テスト要件**：3 点判定テスト（異名 ／ 同名 ／ separation_from_author=false の 3 ケース）、`mode` の各値（foundation 正本が定める）の複合役許容テスト（複合役の許容は `subagent_mediated` 特例のみ、他の値は不許容）、必須フィールド欠落テスト、fail-closed テスト

### T-006：不可逆操作の直前ゲート機構

- **対応設計節**：design.md §不可逆操作の直前ゲートモデル §1〜§4、§主要な設計判断 判断 4
- **対応要件**：Requirement 4 受入 1〜4
- **責務**：4 種類の不可逆操作（`spec.json` の `approval` 段書き込み ／ `git commit` ／ `git push` ／ フェーズ移行）の直前ゲート判定ロジックを `tools/check_workflow_action/gate_predicates.py` として実装、T-004 のサブコマンドから呼ばれる。ゲート発火条件：(1) Requirement 2 検査スクリプトが pass を返す、(2) `stages/in-progress/` が空。毎回独立走行（session 開始時のキャッシュを使わない、状態変化を直前で再検出）。fail-closed の既定（検査結論不能で必ず遮断）。フェーズ移行検査は `feature-dependency.yaml#phase_order` の全機能で approval=true を要求。最小集合方針の徹底（中間段の遷移には機械ゲートを置かない）
- **前提タスク**：T-002、T-003、T-004
- **成果物**：
  - `tools/check_workflow_action/gate_predicates.py`（4 種類のゲート判定）
  - `tools/check_workflow_action/state_resolver.py`（spec.json ／ in-progress ／ pending 所見の状態解決、毎回独立走行）
- **完了条件**：
  1. 4 種類のゲートそれぞれが正常系で OK、異常系（前段未完了 ／ in-progress あり ／ 未消化所見あり ／ 全機能 approval 未完了）で DEVIATION を返す
  2. session 開始時のキャッシュを使わず、毎回 spec.json と `stages/in-progress/` を読み直すことが機械検証される
  3. 最小集合方針（中間段の遷移には機械ゲートが発火しない）が機械検証される
- **テスト要件**：4 種類ゲート × 正常系 ／ 異常系 = 8 ケース、独立走行テスト（同 session 内で状態変化させて再検査が異なる結果を返す）、最小集合テスト（drafting ／ triad-review の遷移ではゲート発火しない）

### T-007：reopen 機械強制

- **対応設計節**：design.md §reopen 機械強制モデル §1〜§4、§主要な設計判断 判断 5
- **対応要件**：Requirement 5 受入 1〜5
- **責務**：reopen 手続きの 4 過程構成を T-003 の `stages/reopen-procedure.yaml` で静的列挙、第3過程の `trigger_map` 解決ロジックを `tools/check_workflow_action/reopen_resolver.py` として実装。手戻り種別の二次元表記（N／R／D／A／I × 深さ）から再実施対象段リストを取得、各段の `actor` を当該段定義から動的解決（`actor_resolution: per_target_stage`）。`actor=human` 段に到達した時点で作業を停止し、`stages/in-progress/reopen-procedure-<日付>.yaml` に「人間承認待ち」を記録して待機。種別判定根拠ファイル（`docs/reviews/reopen-classification-<日付>.md`）の保存・読み込み機構を実装。fail-closed の既定（人間承認なしに次段への進行を許さない）
- **前提タスク**：T-003、T-004、T-005、T-006（T-005 を追加：reopen 解決器が triad-review 段の述語 `artifact_exists_and_sections_present_and_author_reviewer_distinct` 経由で `front_matter_checker` を呼ぶため、T-005 完了前の着手を防ぐ。F-006 対処 2026-05-28）
- **成果物**：
  - `tools/check_workflow_action/reopen_resolver.py`（`trigger_map` 解決 ＋ `actor` 動的解決 ＋ actor=human 自動停止）
  - `tools/check_workflow_action/classification_loader.py`（種別判定根拠ファイルの読み込み）
  - （`templates/review/reopen_classification_template.md` の成果物所有は T-001 単独。本タスクは内容確定のみで成果物に再列挙しない、A-010 対処 案 2 2026-05-28）
- **完了条件**：
  1. 全 15 種の手戻り種別（N-0 ／ R-0〜1 ／ D-0〜2 ／ A-0〜3 ／ I-0〜4）に対する `trigger_map` 解決が機械検証される
  2. `actor=human` 段で自動停止し、`stages/in-progress/reopen-procedure-<日付>.yaml` に `current_blocker` フィールドが書き込まれる
  3. 種別判定根拠ファイル不在の場合は結論不能（DEVIATION）で遮断
  4. 人間承認なしに次段への進行が機械的に許可されない（fail-closed）
  5. T-001 が配置した `reopen_classification_template.md` の内容（front-matter ＋ 分類根拠節）が確定している（成果物所有は T-001、本タスクは内容確定のみ、A-010 対処 案 2 2026-05-28）
- **テスト要件**：15 種類の `trigger_map` 解決テスト、`actor=human` 自動停止テスト、種別判定根拠ファイル欠落の fail-closed テスト、人間承認なし進行禁止テスト

### T-008：session 跨ぎ状態管理

- **対応設計節**：design.md §session 跨ぎ状態管理モデル §1〜§5
- **対応要件**：Requirement 6 受入 1〜6
- **責務**：進行中状態ファイル（`stages/in-progress/<process_id>-<日付>.yaml`）の発行 ／ 読み込み ／ 完了時移動（`stages/completed/` への移動）の機構を `tools/check_workflow_action/in_progress_manager.py` として実装。最低限のフィールド 6 件（`process_id` ／ `started_at` ／ `trigger` ／ `completed_steps` ／ `next_step` ／ `pending_gates`）を必須化、任意フィールド（`classification_basis` ／ `current_blocker` ／ `escalation_status`）を許容。session 開始時の標準フロー 7 ステップ（TODO 確認 ／ 直近 session 記録確認 ／ git log ／ 検査スクリプト全件 ／ in-progress 有無 ／ 進行中優先 ／ 次作業決定）と、session record 作成手順（重要な判断・承認・レビュー結果・修正経緯を `docs/sessions/session-<N>-<YYYY-MM-DD>.md` に残す）を運用文書に明示、`tools/check-workflow-action.py session-start` サブコマンドとして実装可能か別途判断（任意拡張）。fail-closed：`stages/in-progress/` に何かファイルがある状態での不可逆操作実行を遮断（T-006 と整合）。reopen 固有フィールド（`current_blocker` 等）の意味解釈は T-007 の責務とし、T-008 は進行中ファイルの一般管理（発行 ／ 読み込み ／ 移動 ／ 遮断）に徹して reopen 連動を内包しない（前提タスクに T-007 を加えず独立性を保つ、F-007 対処 案 2 2026-05-28）
- **前提タスク**：T-001、T-004、T-006
- **成果物**：
  - `tools/check_workflow_action/in_progress_manager.py`（発行 ／ 読み込み ／ 完了時移動）
  - `stages/in-progress.schema.json`（必須 6 フィールド ＋ 任意フィールド。命名をディレクトリ名 `in-progress/` に合わせハイフン統一、design 配置ツリーにも追記、F-018 対処 案 1 2026-05-28）
  - `docs/operations/WORKFLOW_PRECHECK.md` §session 跨ぎ状態管理節
  - `docs/operations/SESSION_WORKFLOW_GUIDE.md` §セッション記録の作成規律
- **完了条件**：
  1. `in-progress.schema.json` が JSON Schema として meta-schema 検証を通る、必須 6 フィールドが確定（F-018 対処 命名統一）
  2. 進行中状態ファイルの発行 ／ 読み込み ／ 完了時移動が機械検証される
  3. `stages/in-progress/` に何かある状態での不可逆操作実行が遮断される（T-006 連動）
  4. 進行中状態ファイル自体の更新（次ステップ進行 ／ 人間承認の記録）は遮断対象外であることが機械検証される
  5. `SESSION_WORKFLOW_GUIDE.md` と workflow-management 仕様が session record 作成手順を持つことが機械検証される
- **テスト要件**：スキーマ検証、必須 6 フィールド検査、発行 ／ 読み込み ／ 移動の 3 機能テスト、in-progress あり状態での不可逆操作遮断テスト、自己更新の許容テスト、複数 in-progress 並存テスト（複数 reopen-procedure-*.yaml が正常系として並ぶ場合の優先完了対象と解決順。design §テスト戦略 境界条件 L840、reopen やり直し時の証跡保全 L505 由来、A-008 対処 案 1 2026-05-28）

### T-009：多層防御の位置付けと運用文書

- **対応設計節**：design.md §多層防御の位置付けモデル §1〜§5、§主要な設計判断（全般）
- **対応要件**：Requirement 7 受入 1〜4
- **責務**：第 1 層の限界（中身の空疎 ／ 検査呼び出し依存 ／ in-progress 自己申告性 ／ 文脈圧力下での規律低下）を運用文書 `docs/operations/WORKFLOW_PRECHECK.md` に明示。第 2〜5 層（git フック ／ 利用者監査 ／ 定期事後監査 ／ 処理表面積の抑制）と補助層 A／B／C の位置付けを記述。第 5 層運用ルール「新規規律を追加するときは既存規律 1 つ以上を統廃合する」を本機能の運用ルールに反映（フェーズ 4 まで利用者の意識に依拠、機械強制は第 5 層導入時に検討）。本タスクは実装ではなく運用文書の整備が主、機械検査の対象ではない。規律変更ゲート（T-010 が実装）の説明追記も本タスクが担い、T-010 の実装内容を参照して `WORKFLOW_PRECHECK.md` に記述する（運用文書の所有を T-009 に一本化、F-004 対処 案 2 2026-05-28）
- **前提タスク**：T-004、T-005、T-006、T-007、T-008
- **成果物**：
  - `docs/operations/WORKFLOW_PRECHECK.md`（§第 1 層の限界 ／ §第 2〜5 層の宿題 ／ §補助層 A／B／C ／ §第 5 層運用ルール）
  - `docs/operations/WORKFLOW_MANAGEMENT.md` の §多層防御位置付け節
- **完了条件**：
  1. 第 1 層の限界 4 点が運用文書に明示される
  2. 第 2〜5 層と補助層 A／B／C の位置付けが運用文書に記述される
  3. 第 5 層運用ルールが本機能の運用ルールとして反映される（フェーズ 4 まで利用者の意識に依拠の旨を明示）
- **テスト要件**：運用文書の必須節検査（4 節すべての存在）。本タスクの「実装ではなく運用文書の整備が主、機械検査の対象ではない」位置づけ（責務記述）と整合させ、文書内容の grep キーワード検査は完了条件・テスト要件から外す（自己矛盾の解消、F-011 対処 案 2 2026-05-28）

### T-010：規律変更の所定手続き経由実体変更（A-007 案 2、A-012 連動）

- **対応設計節**：design.md §責務境界の明確化、§主要な設計判断 判断 7
- **対応要件**：Requirement 4 受入 1（規律変更は不可逆操作）、Boundary Context 隣接期待（self-improvement との接合面）
- **責務**：`learning/workflow/approved-updates/` ディレクトリを新設、`self-improvement` から承認済み提案 YAML が `git mv` で配置される入力経路を確立。本機能の所定手続き（drafting → review → approval）を経て規律ファイル（`docs/disciplines/discipline_*.md`）の実体変更を実施。完了時に `approved-updates/<日付>-<id>.yaml` に `materialized_at`（ISO 8601 完了時点）と `materialization_commit_hash`（規律変更コミットのハッシュ）を追記。`self-improvement` design §13.5 と本機能 判断 7 の相互参照、時系列契約（`approved` ＝ self-improvement 承認時点 ／ `materialized_at` ＝ 本機能完了時点）の符号化。ロールバック責務は `self-improvement` 側、本機能は受動的に状態通知を受ける
- **前提タスク**：T-003（段集合 YAML 群の配置）、T-004。**規律変更段集合の方針（F-008 対処 案 1 2026-05-28）**：規律変更専用の段集合は機能横断整合用 `cross-spec-alignment.yaml` への相乗り（責務混在）を避け、独立ファイル `stages/discipline-update.yaml` とする方針に一意化。ただし段集合本体（`drafting → review → approval` の 3 段か `triad-review` を含むか）は未確定のため **DVT-W003 として後続セッションに延期**し、本ファイルは T-003 の成果物には含めず DVT-W003 解除時に静的列挙する（tasks 段 2 軸整合性監査 #5 で「T-003 が枠を新設」との誤記述を訂正、2026-05-29）
- **成果物**：
  - `learning/workflow/approved-updates/.gitkeep`
  - `learning/workflow/approved-updates/README.md`（入力経路の説明、`git mv` 配置の規約）
  - （入力 YAML のスキーマは本機能で独自定義しない。self-improvement design §8.4 の正本スキーマを唯一の定義元として参照し、項目名は §8.4（`target_discipline_path` ／ `status` ／ `materialized_at` ／ `materialization_commit_hash` 等）に従う。受け手側の検証は §8.4 由来の共有フィクスチャで行う。**A-019 対処（案1、2026-05-29 セッション40）**：独自 `approved_update.schema.json` の新設と独自項目名 `approved_at` ／ `target_discipline` を廃止し、二重管理を解消）
  - `tools/check_workflow_action/discipline_update_processor.py`（規律変更の所定手続き実施 ＋ 完了通知の追記）
  - （`learning/workflow/approved-updates/` の配置は本機能 design 配置ツリー外だが、self-improvement design §13.5 に正本記述があり機能横断では整合済み。tasks.md 側は出典注記で吸収し design 遡及はしない、F-020 対処 案 1 2026-05-28）
- **完了条件**：
  1. `approved-updates/` ディレクトリが配置され、入力 YAML が self-improvement §8.4 正本スキーマに適合することを検証する（本機能は独自スキーマを定義しない、A-019 対処 案1）
  2. `self-improvement` から `git mv` で配置された YAML を本機能が読み、所定手続きを経て規律ファイル実体変更を完了
  3. 完了時に `materialized_at` ／ `materialization_commit_hash` が追記される
  4. `self-improvement` design §13.5 との時系列契約の整合が機械検証される（DVT-W003）。さらに **§13.5 の変更が機能依存マップ（feature-dependency.yaml）に記録されたとき、DVT-W003 を自動的に open（未解決）へ差し戻し、事前検査スクリプトが再評価完了を確認するまで本タスクを完了扱いにしない**（依存マップ駆動の追従強制、本機能の自己適用、F-016 対処 案 3 2026-05-28）。**【実装時の調停】** A-006 で「`depends_on_resolves_correctly` の汎用的な変更検知はフェーズ 2 の宿題（DVT-W007）」と確定したため、本条件では §13.5（self-improvement 接合面）の変更検知のみを先行実装し、機能依存マップ全般の汎用変更検知はフェーズ 2 に据え置く
- **テスト要件**：スキーマ検証、所定手続きの 3 段（drafting → review → approval）が走るテスト、完了通知の追記テスト、時系列契約の整合テスト、self-improvement の `git mv` 外部依存をモック／スタブ化した consumer 側統合テスト（`approved-updates/` への YAML 配置を擬似再現、実 git mv は呼ばない。擬似 YAML は self-improvement §8.4 正本スキーマ準拠の共有フィクスチャとする（A-019 解消＝案1 採用 2026-05-29 により §8.4 を唯一の定義元として参照）。producer/consumer 境界の契約確認は T-011 に集約、F-012 対処 別案 2026-05-28）

### T-011：テスト戦略全体の整備

- **対応設計節**：design.md §テスト戦略 §1〜§5、§完成判定基準
- **対応要件**：本機能全要件の機械的合否判定、foundation 語彙正本（本機能が参照する `review_mode`）の参照のみ使用の機械検証、要件追跡表の双方向整合、DVT 解除確認
- **責務**：design.md §テスト戦略で定義された 4 検証類（単体テスト ／ 統合テスト ／ 異常系 fixture ／ 境界条件）をすべて Python テストとして整備。pytest で一括実行可能。foundation 語彙正本（本機能が参照する `review_mode`）の参照のみ使用の機械検証、および所見系・状態軸系語彙を参照していないことの機械検証、本機能所有正本（`completion_predicate` 述語 7 値 ／ `verdict` 3 値 ／ 手戻り種別記号 5 値 ／ 依存種別 2 値）が T-002 ／ T-003 ／ T-004 ／ T-007 の成果物で正本確定されていることの機械検証。要件追跡表と各タスク本文の対応要件欄の双方向整合チェック（foundation T-010 ／ runtime T-011 ／ evaluation T-011 ／ analysis T-011 の方針継承）。**遅延確認事項テーブル（DVT）内の未解除項目がない、または延期理由が明記されている**ことを完了条件にゲート化（evaluation T-011 ／ analysis T-011 の方針継承）
- **前提タスク**：T-001 ／ T-002 ／ T-003 ／ T-004 ／ T-005 ／ T-006 ／ T-007 ／ T-008 ／ T-009 ／ T-010
- **成果物**：`tests/workflow-management/` 配下のテストファイル群（`test_feature_dependency.py` ／ `test_stages_yaml.py` ／ `test_check_workflow_action.py` ／ `test_front_matter.py` ／ `test_gate_predicates.py` ／ `test_reopen.py` ／ `test_in_progress.py` ／ `test_discipline_update.py` ／ `test_operations_docs.py` ／ `test_traceability.py` の 10 ファイル相当）
- **完了条件**：すべての pytest が pass、4 検証類を網羅、foundation 語彙正本（本機能が参照する `review_mode`）の参照のみ使用が機械検証される（所見系・状態軸系の不参照を含む）、workflow-management 所有正本（`completion_predicate` 述語 7 値 ／ `verdict` 3 値 ／ 手戻り種別記号 5 値 ／ 依存種別 2 値）が正本確定されている、要件追跡表の双方向整合が機械チェックされる、DVT 内の未解除項目がない（または延期理由が明記されている）
- **テスト要件**：すべての pytest が pass、回帰なし、要件追跡表の双方向整合チェック、DVT ゲート化、self-improvement との接合面の producer/consumer 境界の契約確認（T-010 の consumer 側統合テストと対をなす境界テスト、`git mv` 経由の `approved-updates/` 取り込みの整合確認を集約、F-012 対処 別案 2026-05-28）

## 要件追跡（Requirements Traceability）

| 要件 | 対応タスク |
|------|-----------|
| Requirement 1 受入 1：YAML 静的列挙、Markdown 動的解析しない | T-003 |
| Requirement 1 受入 2：9 ファイル体制 | T-001（配置）＋ T-002（feature-dependency）＋ T-003（8 ファイル） |
| Requirement 1 受入 3：段名／actor／証跡パス／必須節／完了判定 | T-003 |
| Requirement 1 受入 4：feature_order 参照 | T-002（参照先）＋ T-003（参照側） |
| Requirement 1 受入 5：YAML 1 箇所修正、Markdown 整合は人手 | T-003 |
| Requirement 1 受入 6：機能横断段 review-wave の作業内容（7 モデル評価 2 回方式） | T-003（`cross-spec-alignment.yaml` 枠）＋ T-009（運用文書）※ 段集合本体は DVT-W004 で延期、cross-spec-alignment.yaml 確定後に符号化（F-001 対処 2026-05-28） |
| Requirement 2 受入 1：Python 実装 | T-004 |
| Requirement 2 受入 2：証跡＋必須節のみ判定 | T-004 |
| Requirement 2 受入 3：中身の妥当性判定しない | T-004（判定範囲）＋ T-009（運用文書での明示） |
| Requirement 2 受入 4：結論不能は fail（fail-closed） | T-004（パースエラー）＋ T-006（ゲート） |
| Requirement 2 受入 5：in-progress 警告 | T-004（警告出力）＋ T-008（in-progress 管理） |
| Requirement 3 受入 1：author／reviewer 必須 | T-005 |
| Requirement 3 受入 2：identity 同一を許容しない | T-005 |
| Requirement 3 受入 3：subagent_mediated の判定役は別エンティティ | T-005（複合役許容） |
| Requirement 3 受入 4：front-matter 検査、別モデル／別 session は第 1 層対象外 | T-005（検査範囲）＋ T-009（運用文書での明示） |
| Requirement 4 受入 1：4 種類の不可逆操作 | T-006 |
| Requirement 4 受入 2：pass ＋ in-progress 空、毎回独立走行 | T-006（独立走行）＋ T-008（in-progress 連動） |
| Requirement 4 受入 3：fail-closed | T-004 ／ T-006 ／ T-007 ／ T-008（全体方針） |
| Requirement 4 受入 4：最小集合方針 | T-006 |
| Requirement 5 受入 1：手戻り種別の二次元表記 | T-003（reopen-procedure.yaml）＋ T-007（解決ロジック） |
| Requirement 5 受入 2：trigger_map | T-003（trigger_map 列挙）＋ T-007（解決） |
| Requirement 5 受入 3：actor=human で停止 | T-007 |
| Requirement 5 受入 4：人間承認なしに進まない | T-007 |
| Requirement 5 受入 5：種別判定根拠の保存 | T-001（雛形配置）＋ T-007（読み込み機構） |
| Requirement 6 受入 1：in-progress ファイル配置 | T-001（配置）＋ T-008（管理機構） |
| Requirement 6 受入 2：必須フィールド | T-008 |
| Requirement 6 受入 3：session 開始時の標準フロー | T-008（実装）＋ T-009（運用文書） |
| Requirement 6 受入 4：完了時の移動 | T-008 |
| Requirement 6 受入 5：in-progress ある状態での遮断 | T-006 ／ T-008 連動 |
| Requirement 7 受入 1：第 1 層の限界の明文化 | T-009 |
| Requirement 7 受入 2：第 2〜5 層を宿題として参照 | T-009 |
| Requirement 7 受入 3：第 5 層運用ルールの反映 | T-009 |
| Requirement 7 受入 4：第 1 層の限界の運用文書への明示 | T-009 |
| Requirement 8 受入 1：feature-dependency.yaml が一元保管先 | T-002 |
| Requirement 8 受入 2：features ＋ phase_order、2 形式の depends_on | T-002 |
| Requirement 8 受入 3：feature_order 参照 | T-003 |
| Requirement 8 受入 4：1 箇所修正で完結 | T-002（運用文書）※ T-009 は本受入に直接寄与しないため追跡先から除外（F-003 対処 2026-05-28） |
| Requirement 8 受入 5：所有者は本機能、他機能は参照のみ | T-002（運用文書） |
| Boundary Context 隣接期待（self-improvement との接合面、A-007 案 2／A-012） | T-010 |

## テスト戦略の継承（Test Strategy Inheritance）

design.md §テスト戦略の 4 検証類を T-011 にまとめて継承する。各検証類の対応タスクは次のとおり：

- 単体テスト → T-002 ／ T-003 ／ T-004 ／ T-005 ／ T-008 個別 ＋ T-011 統合
- 統合テスト → T-006 ／ T-007 ／ T-010 個別 ＋ T-011 統合
- 異常系 fixture → 各タスクで fail-closed テスト ＋ T-011 統合
- 境界条件 → T-002（依存マップ境界）／ T-003（テンプレート変数境界）／ T-008（複数 in-progress 並存）＋ T-011 統合

## 完成判定基準（Completion Criteria）

本タスク文書は次を満たすときに完了とみなす：

- T-001〜T-011 のすべてが起草・実装・テスト・コミット完了
- design.md §完成判定基準の 7 項目すべてが T-011 の統合テストで pass
- foundation が所有する語彙正本のうち本機能が参照する `review_mode` を再定義せず参照のみで使用し、所見系（`counter_status`／`severity`／`final_label`／`confidence_label`）・状態軸系（`run_status`／`validator_status`／`human_signoff_status`／`evidence_class`）を参照していないことが、機械検証で確認できる（A-003 対処 2026-05-28）
- workflow-management 所有の正本（`completion_predicate` 述語集合 7 値 ／ `verdict` 3 値 OK／WARN／DEVIATION ／ 手戻り種別記号 5 値 N／R／D／A／I ／ 依存種別 2 値 `hard`／`review`）が T-002 ／ T-003 ／ T-004 ／ T-007 の成果物で正本として確定されている
- 各タスクの成果物配置が design.md §全体構造 と一致
- 各タスクの依存順が守られている（前提タスクなしで後続タスクを開始しない）
- 遅延確認事項テーブル（DVT）内の未解除項目がない（または延期理由が明記されている）

## 変更意図（Change Intent）

本タスク文書は workflow-management 機能を「思想は継承、実装は 1／10」（計画書 §5.4 軽量化方針）の精神で実装するため、次を採用する：

- **一気通貫粒度**：1 タスク ＝ 1 つの所有モデル領域。foundation T-001〜T-010 ／ runtime T-001〜T-011 ／ evaluation T-001〜T-011 ／ analysis T-001〜T-011 の粒度方針を継承
- **所有モデル単位の分離**：design.md の所有モデル 5 種（段集合 ／ 検査スクリプト ／ 起草者判定者分離 ／ 直前ゲート ／ reopen 機械強制 ／ session 跨ぎ ／ 多層防御 ／ 機能依存マップ）に T-003〜T-010 を対応付け
- **依存順の明示**：T-001（配置）→ T-002（依存マップ）→ T-003（段集合 YAML）→ T-004（検査スクリプト本体）→ T-005〜T-008（各機械検査）→ T-009（運用文書）→ T-010（規律変更接合面）→ T-011（統合テスト）の流れを固定
- **fail-closed の全面採用**：判断 3 を全タスクで徹底、結論不能（YAML パースエラー ／ 証跡欠落 ／ 必須フィールド欠落 ／ 未知の値）は必ず DEVIATION で遮断
- **最小集合方針**：判断 4 を T-006 で徹底、中間段の遷移には機械ゲートを置かない
- **contract consumer 原則の徹底**：foundation が所有する語彙正本を再定義せず参照のみで使用（本機能が参照するのは `review_mode` のみ。所見系・状態軸系は責務外で不参照、A-003 対処 2026-05-28）、本機能所有の正本（`completion_predicate` 述語 7 値 ／ `verdict` 3 値 ／ 手戻り種別記号 5 値 ／ 依存種別 2 値）は本機能で確定
- **テスト戦略の継承**：design.md §テスト戦略の 4 検証類を T-011 で網羅
- **要件追跡表の双方向整合チェックを T-011 に組み込み**：foundation T-010 ／ runtime T-011 ／ evaluation T-011 ／ analysis T-011 の方針を踏襲
- **遅延確認事項テーブル（DVT）の活用**：未確定上流仕様（段階 3 Claude Code フック ／ 既存レビュー記録の遡及検査 grandfathering ／ 規律変更の所定手続きの段集合 ／ cross-spec-alignment.yaml の段集合）を DVT で集約管理、T-011 完了条件で未解除項目がないことをゲート化（evaluation T-011 ／ analysis T-011 の方針継承）
- **自律進行**：実装段で per-task 承認は取らず、コミット・プッシュ・spec.json 更新・フェーズ移行のみ明示承認（規律 [[implementation-autonomy]] 準拠）
- **計画書 §5.4 軽量化方針との整合**：節ハッシュ・supersedes リンク・通過マーカー後続確認・独立再導出パーサ・実行台帳の機構全体は導入せず、`required_sections` 配列と `completion_predicate` 述語集合、構造化参照、機械検証可能な fail-closed 判定のみで mandatory ／ deferred を符号化

---

## 遅延確認事項テーブル（Deferred Verification Table、DVT）

本テーブルは tasks 段で参照される未確定上流仕様または将来確定予定の事項を集約管理する。evaluation T-011 ／ analysis T-011 の DVT 同型運用。

| ID | 関連タスク | 遅延内容 | 解除トリガー | 状態 |
|---|---|---|---|---|
| DVT-W001 | T-004 ／ T-006 | 段階 3 Claude Code フックとの結合方式（design.md §先送り論点 5）。検査スクリプトを `pre-commit` ／ `pre-push` フックから呼ぶ経路、および Claude Code の PreToolUse フックから呼ぶ経路の具体配線はフェーズ 2 以降の宿題 | フェーズ 2 で段階 3 フック実装着手時に T-004 ／ T-006 完了条件と整合を再確認 | 未解除（フェーズ 2 以降まで延期） |
| DVT-W002 | T-005 | 既存レビュー記録の遡及検査（design.md §先送り論点 4）。Req 3 の front-matter 必須化を既存 7 件（requirements の各機能）に遡及適用するか、grandfathering（移行期免除）で扱うかが未確定 | フェーズ 2 で検査スクリプト導入時に grandfathering 判断を確定、または利用者明示承認で遡及適用範囲を確定 | 未解除 |
| DVT-W003 | T-010 | 規律変更の所定手続きの段集合（design.md §先送り論点 6）。規律変更を `drafting → review → approval` の 3 段で扱うか、`triad-review` を含めるかが未確定。A-007 案 2 対応の細部 | 後続セッションで規律変更の段集合を確定、`stages/discipline-update.yaml` 等として静的列挙 | 未解除 |
| DVT-W004 | T-003 | `cross-spec-alignment.yaml` の段集合（design.md §先送り論点 7）。機能横断整合手続きの段集合本体が未確定、本タスクでは枠のみ確保 | フェーズ 2 以降で機能横断整合手続きの実体設計時に段集合を確定 | 未解除（フェーズ 2 以降まで延期） |
| DVT-W005 | T-010 | 規律変更の所定手続き実装と参照層 5 件（memory 配下の現行規律本体）の memory→repo 移管要否（design.md §先送り論点 8）。参照層が repo 未移管なら本機能の機械検査が効かない構造問題 | 参照層の移管方針を利用者明示承認で確定、またはフェーズ 2 で対象範囲を確定 | 未解除（A-005 対処で登録 2026-05-28） |
| DVT-W006 | T-009 ／ T-010 | 運営ガイド等の現行規律本体の改廃手続きを本機能の規律変更手続きの対象に含めるか（design.md §先送り論点 9） | フェーズ 2 以降で対象範囲を確定 | 未解除（A-005 対処で登録 2026-05-28） |
| DVT-W007 | T-004 ／ T-010 | `depends_on_resolves_correctly` の汎用的な変更検知と recheck 更新発火（design.md §機能依存マップ §6、フェーズ 2 宿題）。**ただし F-016 案 3 により §13.5（self-improvement 接合面）の変更検知のみ T-010 で先行実装**、機能依存マップ全般の汎用変更検知は本 DVT で据え置き | フェーズ 2 で変更検知機構の実装着手時に T-004／T-010 完了条件と整合を再確認 | 未解除（A-006／F-016 調停で登録 2026-05-28、フェーズ 2 以降まで延期） |

**運用ルール**：

- 本テーブルの「未解除」項目があるとき、関連タスクは完了判定可能だが、解除トリガー発火時に再評価が必須
- T-011 完了条件は本テーブル内の未解除項目がない（または延期理由が明記されている）ことをゲート化
- 新規の遅延項目が発生した場合は本テーブルに追記、解除時に「状態」を「解除済（日付、解除根拠）」に更新

---

## 機能横断段への持ち越し事項

本機能の triad-review 段で発見された機能横断波及所見は、`learning/workflow/carry-forward-register/reviewcompass-import.yaml` に追記し、tasks の機能横断段（review-wave）で消化する。7 モデル評価 2 回目と同根問題集約は本機能では実施せず、機能横断段で一括実施する（(Q2) ／ (ニ) 採用、2 回方式に訂正、計画書 §5.5 ／ §5.9.6 反映済み）。

```

## FILE: .reviewcompass/specs/workflow-management/spec.json

```text
{
  "feature_name": "workflow-management",
  "language": "ja",
  "created_at": "2026-05-24T00:00:00+09:00",
  "updated_at": "2026-06-04T00:00:00+09:00",
  "workflow_state": {
    "intent": {
      "drafting": true,
      "review": true,
      "approval": true,
      "reference": "stages/intent.yaml"
    },
    "feature-partitioning": {
      "candidate-proposal": true,
      "approval": true,
      "reference": "stages/feature-partitioning/2026-05-24-proposal.md"
    },
    "requirements": {
      "drafting": true,
      "triad-review": true,
      "review-wave": true,
      "alignment": true,
      "approval": true
    },
    "design": {
      "drafting": true,
      "triad-review": true,
      "review-wave": true,
      "alignment": true,
      "approval": true
    },
    "tasks": {
      "drafting": true,
      "triad-review": true,
      "review-wave": true,
      "alignment": true,
      "approval": true
    },
    "implementation": {
      "drafting": true,
      "triad-review": false,
      "review-wave": false,
      "alignment": false,
      "approval": false
    }
  },
  "reopened": {
    "intent": false,
    "feature-partitioning": false,
    "requirements": true,
    "design": true,
    "tasks": true,
    "implementation": false
  },
  "recheck": {
    "upstream_change_pending": false,
    "impacted_downstream_phases": []
  }
}

```

## FILE: tools/check-workflow-action.py

```text
#!/usr/bin/env python3
"""ワークフロー事前検査スクリプト（補助層 C 段階 2）

仕様：docs/operations/WORKFLOW_PRECHECK.md
位置付け：計画書 §5.8 補助層 C 共存モデルの段階 2（外部スクリプトによる機械的判定）

呼び出し側（段階 1 LLM または段階 3 フック）から不可逆操作の直前に呼ばれ、
当該操作が現在のワークフロー状態と整合するかを機械的に判定する。判定のみを
行い、状態の書き換えやエスカレーションは行わない。

サブコマンド：
  spec-set <feature> <phase> <stage> <new-value>  spec.json の workflow_state 変更を判定
  commit   --rationale "<理由>"                    git commit を判定
  push     --rationale "<理由>"                    git push を判定

終了コード（仕様 §7.1）：
  0  問題なし、処理続行可
  1  警告あり、呼び出し側の判断で続行可
  2  逸脱検出、呼び出し側が遮断推奨
"""

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import yaml


# 既定のログファイルパス（呼び出し時の cwd 相対、仕様 §8.2）
DEFAULT_LOG_PATH = "docs/logs/workflow-precheck.log"
DEFAULT_COMMIT_APPROVAL_PATH = ".reviewcompass/approvals/commit-approval.json"

# 各フェーズの段集合（計画書 §5.5 と §5.24.4 と整合）
PHASE_STAGES = {
  "intent": ["drafting", "review", "approval"],
  "feature-partitioning": ["candidate-proposal", "approval"],
  "requirements": ["drafting", "triad-review", "review-wave", "alignment", "approval"],
  "design": ["drafting", "triad-review", "review-wave", "alignment", "approval"],
  "tasks": ["drafting", "triad-review", "review-wave", "alignment", "approval"],
  "implementation": ["drafting", "triad-review", "review-wave", "alignment", "approval"],
}

# フェーズの依存順（計画書 §5.5）
PHASE_ORDER = [
  "intent",
  "feature-partitioning",
  "requirements",
  "design",
  "tasks",
  "implementation",
]

# 機能横断段（全機能で同じ値を持つフェーズ、計画書 §5.24.4）
CROSS_FEATURE_PHASES = ("intent", "feature-partitioning")

# ReviewCompass 現行 dogfooding 用の機能順（stages/feature-partitioning/2026-05-24-proposal.md と整合）
FEATURE_ORDER = [
  "foundation",
  "runtime",
  "evaluation",
  "analysis",
  "workflow-management",
  "self-improvement",
  "conformance-evaluation",
]

POST_WRITE_VERIFICATION_DIR_PREFIXES = (
  "docs/plan/",
  "docs/disciplines/",
  "docs/operations/",
  "docs/notes/",
  "docs/experiments/",
)

AUTONOMOUS_PARALLEL_REQUIRED_INTEGRATION_GATES = (
  "requires_main_session_review",
  "requires_diff_scope_check",
  "requires_tests",
  "requires_decision_basis_review",
)

AUTONOMOUS_PARALLEL_REQUIRED_OUTPUTS_POLICY = {
  "implementation_diff": "commit_candidate",
  "verification_summary": "required",
  "decision_basis": "preserve_if_used",
  "work_noise": "exclude",
}

AUTONOMOUS_PARALLEL_REQUIRED_HISTORY_FLAGS = (
  "record_task_assignments",
  "record_decision_basis",
  "record_integration_result",
)

REOPEN_TRIGGER_MAP = {
  "I-0": [
    "stages/implementation.yaml#alignment",
    "stages/implementation.yaml#approval",
  ],
  "I-1": [
    "stages/tasks.yaml#alignment",
    "stages/tasks.yaml#approval",
    "stages/implementation.yaml#alignment",
    "stages/implementation.yaml#approval",
  ],
  "I-2": [
    "stages/design.yaml#alignment",
    "stages/design.yaml#approval",
    "stages/tasks.yaml#alignment",
    "stages/tasks.yaml#approval",
    "stages/implementation.yaml#alignment",
    "stages/implementation.yaml#approval",
  ],
  "I-3": [
    "stages/requirements.yaml#alignment",
    "stages/requirements.yaml#approval",
    "stages/design.yaml#alignment",
    "stages/design.yaml#approval",
    "stages/tasks.yaml#alignment",
    "stages/tasks.yaml#approval",
    "stages/implementation.yaml#alignment",
    "stages/implementation.yaml#approval",
  ],
  "I-4": [
    "stages/intent.yaml#review",
    "stages/intent.yaml#approval",
    "stages/feature-partitioning.yaml#candidate-proposal",
    "stages/feature-partitioning.yaml#approval",
    "stages/requirements.yaml#alignment",
    "stages/requirements.yaml#approval",
    "stages/design.yaml#alignment",
    "stages/design.yaml#approval",
    "stages/tasks.yaml#alignment",
    "stages/tasks.yaml#approval",
    "stages/implementation.yaml#alignment",
    "stages/implementation.yaml#approval",
  ],
  "A-0": [
    "stages/tasks.yaml#alignment",
    "stages/tasks.yaml#approval",
  ],
  "A-1": [
    "stages/design.yaml#alignment",
    "stages/design.yaml#approval",
    "stages/tasks.yaml#alignment",
    "stages/tasks.yaml#approval",
  ],
  "A-2": [
    "stages/requirements.yaml#alignment",
    "stages/requirements.yaml#approval",
    "stages/design.yaml#alignment",
    "stages/design.yaml#approval",
    "stages/tasks.yaml#alignment",
    "stages/tasks.yaml#approval",
  ],
  "A-3": [
    "stages/intent.yaml#review",
    "stages/intent.yaml#approval",
    "stages/feature-partitioning.yaml#candidate-proposal",
    "stages/feature-partitioning.yaml#approval",
    "stages/requirements.yaml#alignment",
    "stages/requirements.yaml#approval",
    "stages/design.yaml#alignment",
    "stages/design.yaml#approval",
    "stages/tasks.yaml#alignment",
    "stages/tasks.yaml#approval",
  ],
  "D-0": [
    "stages/design.yaml#alignment",
    "stages/design.yaml#approval",
  ],
  "D-1": [
    "stages/requirements.yaml#alignment",
    "stages/requirements.yaml#approval",
    "stages/design.yaml#alignment",
    "stages/design.yaml#approval",
  ],
  "D-2": [
    "stages/intent.yaml#review",
    "stages/intent.yaml#approval",
    "stages/feature-partitioning.yaml#candidate-proposal",
    "stages/feature-partitioning.yaml#approval",
    "stages/requirements.yaml#alignment",
    "stages/requirements.yaml#approval",
    "stages/design.yaml#alignment",
    "stages/design.yaml#approval",
  ],
  "R-0": [
    "stages/requirements.yaml#alignment",
    "stages/requirements.yaml#approval",
  ],
  "R-1": [
    "stages/intent.yaml#review",
    "stages/intent.yaml#approval",
    "stages/feature-partitioning.yaml#candidate-proposal",
    "stages/feature-partitioning.yaml#approval",
    "stages/requirements.yaml#alignment",
    "stages/requirements.yaml#approval",
  ],
  "N-0": [
    "stages/intent.yaml#review",
    "stages/intent.yaml#approval",
    "stages/feature-partitioning.yaml#candidate-proposal",
    "stages/feature-partitioning.yaml#approval",
  ],
}


def load_spec_json(cwd, feature):
  """機能の spec.json を読み込んで dict として返す

  見つからない場合は None。
  """
  spec_path = Path(cwd) / ".reviewcompass" / "specs" / feature / "spec.json"
  if not spec_path.exists():
    return None
  return json.loads(spec_path.read_text(encoding="utf-8"))


def judge_spec_set(spec_data, phase, stage, new_value):
  """spec-set の判定を行う（仕様 §6.1）

  戻り値：(verdict, exit_code, reasons)
    verdict: "OK" / "WARN" / "DEVIATION"
    exit_code: 0 / 1 / 2
    reasons: 理由文のリスト
  """
  workflow_state = spec_data.get("workflow_state", {})
  phase_state = workflow_state.get(phase, {})
  current_value = phase_state.get(stage)

  if new_value:
    # true に変える場合：依存チェック
    reasons = []

    # 同フェーズ内の前段がすべて true か
    stages = PHASE_STAGES[phase]
    stage_index = stages.index(stage)
    for prior_stage in stages[:stage_index]:
      if not phase_state.get(prior_stage, False):
        reasons.append(
          f"workflow_state.{phase}.{prior_stage} が false です"
          f"（{stage} の前提が満たされていません）"
        )

    # 上流フェーズの approval が true か（機能横断段は不要）
    if phase not in CROSS_FEATURE_PHASES:
      phase_idx = PHASE_ORDER.index(phase)
      for prior_phase in PHASE_ORDER[:phase_idx]:
        prior_phase_state = workflow_state.get(prior_phase, {})
        if not prior_phase_state.get("approval", False):
          reasons.append(
            f"workflow_state.{prior_phase}.approval が false です"
            f"（上流フェーズの approval が必要）"
          )

    if reasons:
      return "DEVIATION", 2, reasons
    return "OK", 0, []

  else:
    # false に変える場合：reopen 警告（現状 true のときのみ）
    if current_value is True:
      return "WARN", 1, [
        f"{phase}.{stage} を true から false に戻しています"
        f"（reopen 手続き 計画書 §5.6 に従っているか確認してください）"
      ]
    return "OK", 0, []


def format_current_state_text(feature, phase, phase_state):
  """現状を人間可読のテキストとして整形する（仕様 §7.2 サンプル準拠で小文字真偽値）"""
  lines = [f"{feature}.{phase}:"]
  for s in PHASE_STAGES[phase]:
    value = phase_state.get(s, False)
    value_str = "true" if value else "false"
    lines.append(f"  {s}: {value_str}")
  return "\n".join(lines)


def format_human_output(verdict, exit_code, action_str, reasons, current_state_text):
  """人間可読出力を整形する（仕様 §7.2）"""
  lines = [
    f"[VERDICT] {verdict}（exit {exit_code}）",
    f"[ACTION] {action_str}",
    "[REASON]",
  ]
  if reasons:
    for r in reasons:
      lines.append(f"  - {r}")
  else:
    lines.append("  - 問題は検出されませんでした")
  lines.append("[CURRENT STATE]")
  for line in current_state_text.splitlines():
    lines.append(f"  {line}")
  return "\n".join(lines)


def format_json_output(verdict, exit_code, action_dict, reasons, current_state_dict):
  """JSON 出力を整形する（仕様 §7.3）"""
  return json.dumps(
    {
      "verdict": verdict,
      "exit_code": exit_code,
      "action": action_dict,
      "reasons": reasons,
      "current_state": current_state_dict,
    },
    ensure_ascii=False,
    indent=2,
  )


def format_next_json_output(verdict, exit_code, next_action, reasons, current_state_dict):
  """next サブコマンドの JSON 出力を整形する"""
  return json.dumps(
    {
      "verdict": verdict,
      "exit_code": exit_code,
      "next_action": next_action,
      "reasons": reasons,
      "current_state": current_state_dict,
    },
    ensure_ascii=False,
    indent=2,
  )


def append_log(log_path, action_dict, verdict, exit_code, reasons, current_state_dict):
  """ログを JSON Lines 形式で追記する（仕様 §8.1）"""
  log_path = Path(log_path)
  log_path.parent.mkdir(parents=True, exist_ok=True)

  jst = timezone(timedelta(hours=9))
  entry = {
    "timestamp": datetime.now(jst).isoformat(),
    "action": action_dict,
    "verdict": verdict,
    "exit_code": exit_code,
    "reasons": reasons,
    "current_state": current_state_dict,
  }

  with open(log_path, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def path_specs_overlap(left, right):
  """allowed_paths の衝突を保守的に判定する"""
  left_value = str(left).rstrip("/")
  right_value = str(right).rstrip("/")
  return (
    left_value == right_value
    or left_value.startswith(right_value + "/")
    or right_value.startswith(left_value + "/")
  )


def tasks_have_dependency(left_task, right_task):
  """2 タスク間に直列化の依存宣言があるかを判定する"""
  left_id = left_task.get("task_id")
  right_id = right_task.get("task_id")
  left_depends_on = set(left_task.get("depends_on") or [])
  right_depends_on = set(right_task.get("depends_on") or [])
  return right_id in left_depends_on or left_id in right_depends_on


def validate_autonomous_parallel_plan(plan):
  """自律・並列モード実行計画を fail-closed で検査する"""
  reasons = []
  current_state = {
    "mode": None,
    "run_id": None,
    "task_count": 0,
    "parallel_task_count": 0,
    "checked_gates": list(AUTONOMOUS_PARALLEL_REQUIRED_INTEGRATION_GATES),
    "history_ledger_path": None,
  }

  if not isinstance(plan, dict):
    return reasons + ["plan は YAML mapping である必要があります"], current_state

  current_state["mode"] = plan.get("mode")
  current_state["run_id"] = plan.get("run_id")

  if plan.get("mode") != "autonomous_parallel":
    reasons.append("mode は autonomous_parallel である必要があります")
  if not plan.get("run_id"):
    reasons.append("run_id が必要です")

  authorization = plan.get("authorization")
  if not isinstance(authorization, dict):
    reasons.append("authorization が必要です")
  else:
    approved_by = authorization.get("approved_by")
    if approved_by not in ("user", "proxy_model"):
      reasons.append("authorization.approved_by は user または proxy_model が必要です")
    if not authorization.get("approval_record_path"):
      reasons.append("authorization.approval_record_path が必要です")
    if authorization.get("summary_presented_to_user") is not True:
      reasons.append("authorization.summary_presented_to_user は true が必要です")
    if authorization.get("triage_presented_to_user") is not True:
      reasons.append("authorization.triage_presented_to_user は true が必要です")

  tasks = plan.get("tasks")
  if not isinstance(tasks, list) or not tasks:
    reasons.append("tasks は 1 件以上の list が必要です")
    tasks = []
  current_state["task_count"] = len(tasks)
  current_state["parallel_task_count"] = len([
    task for task in tasks
    if isinstance(task, dict) and not task.get("depends_on")
  ])

  seen_task_ids = set()
  for index, task in enumerate(tasks):
    task_label = task.get("task_id") if isinstance(task, dict) else f"index:{index}"
    if not isinstance(task, dict):
      reasons.append(f"tasks[{index}] は mapping が必要です")
      continue

    task_id = task.get("task_id")
    if not task_id:
      reasons.append(f"tasks[{index}].task_id が必要です")
    elif task_id in seen_task_ids:
      reasons.append(f"tasks[{index}].task_id が重複しています: {task_id}")
    else:
      seen_task_ids.add(task_id)

    if not task.get("source_finding_ids"):
      reasons.append(f"{task_label}.source_finding_ids が必要です")
    if not task.get("allowed_paths"):
      reasons.append(f"{task_label}.allowed_paths が必要です")
    if not task.get("expected_tests"):
      reasons.append(f"{task_label}.expected_tests が必要です")
    stop_conditions = task.get("stop_conditions") or []
    if "important_decision_requires_approval" not in stop_conditions:
      reasons.append(
        f"{task_label}.stop_conditions に important_decision_requires_approval が必要です"
      )

    assignee = task.get("assignee")
    if not isinstance(assignee, dict):
      reasons.append(f"{task_label}.assignee が必要です")
      continue
    assignee_kind = assignee.get("kind")
    worktree_policy = assignee.get("worktree_policy")
    if assignee_kind not in ("main_session", "subthread", "subagent"):
      reasons.append(f"{task_label}.assignee.kind が無効です")
    if assignee_kind in ("subthread", "subagent") and worktree_policy != "separate_worktree":
      reasons.append(
        f"{task_label}.assignee.worktree_policy は separate_worktree が必要です"
      )

  for left_index, left_task in enumerate(tasks):
    if not isinstance(left_task, dict):
      continue
    for right_task in tasks[left_index + 1:]:
      if not isinstance(right_task, dict):
        continue
      if tasks_have_dependency(left_task, right_task):
        continue
      for left_path in left_task.get("allowed_paths") or []:
        for right_path in right_task.get("allowed_paths") or []:
          if path_specs_overlap(left_path, right_path):
            reasons.append(
              "依存関係のない並列タスクの allowed_paths が衝突しています: "
              f"{left_task.get('task_id')}:{left_path} / "
              f"{right_task.get('task_id')}:{right_path}"
            )

  integration_gate = plan.get("integration_gate")
  if not isinstance(integration_gate, dict):
    reasons.append("integration_gate が必要です")
  else:
    for key in AUTONOMOUS_PARALLEL_REQUIRED_INTEGRATION_GATES:
      if integration_gate.get(key) is not True:
        reasons.append(f"integration_gate.{key} は true が必要です")

  outputs_policy = plan.get("outputs_policy")
  if not isinstance(outputs_policy, dict):
    reasons.append("outputs_policy が必要です")
  else:
    for key, expected in AUTONOMOUS_PARALLEL_REQUIRED_OUTPUTS_POLICY.items():
      if outputs_policy.get(key) != expected:
        reasons.append(f"outputs_policy.{key} は {expected} が必要です")

  history = plan.get("history")
  if not isinstance(history, dict):
    reasons.append("history が必要です")
  else:
    ledger_path = history.get("ledger_path")
    current_state["history_ledger_path"] = ledger_path
    if not ledger_path:
      reasons.append("history.ledger_path が必要です")
    elif not str(ledger_path).startswith("docs/logs/autonomous-parallel/"):
      reasons.append(
        "history.ledger_path は docs/logs/autonomous-parallel/ 配下が必要です"
      )
    for key in AUTONOMOUS_PARALLEL_REQUIRED_HISTORY_FLAGS:
      if history.get(key) is not True:
        reasons.append(f"history.{key} は true が必要です")
    if history.get("retention") != "preserve":
      reasons.append("history.retention は preserve が必要です")

  return reasons, current_state


def write_autonomous_parallel_ledger(cwd, plan, verdict, exit_code, reasons, current_state):
  """自律・並列モード実行計画の後追い用台帳を書き出す"""
  history = plan.get("history") if isinstance(plan, dict) else None
  if not isinstance(history, dict):
    return
  ledger_path_value = history.get("ledger_path")
  if not ledger_path_value:
    return

  ledger_path = Path(ledger_path_value)
  if ledger_path.is_absolute():
    return
  ledger_path = cwd / ledger_path
  ledger_path.parent.mkdir(parents=True, exist_ok=True)

  tasks = plan.get("tasks") if isinstance(plan.get("tasks"), list) else []
  task_ids = [
    task.get("task_id")
    for task in tasks
    if isinstance(task, dict) and task.get("task_id")
  ]
  ledger = {
    "run_id": plan.get("run_id"),
    "mode": plan.get("mode"),
    "verdict": verdict,
    "exit_code": exit_code,
    "reasons": reasons,
    "task_ids": task_ids,
    "authorization": plan.get("authorization"),
    "history": history,
    "integration_gate": plan.get("integration_gate"),
    "outputs_policy": plan.get("outputs_policy"),
    "current_state": current_state,
  }
  ledger_path.write_text(
    yaml.safe_dump(ledger, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def build_autonomous_parallel_plan_template(run_id):
  """自律・並列モード実行計画の最小テンプレートを返す"""
  return {
    "mode": "autonomous_parallel",
    "run_id": run_id,
    "authorization": {
      "approved_by": "user",
      "approval_record_path": "docs/notes/approval.md",
      "summary_presented_to_user": True,
      "triage_presented_to_user": True,
    },
    "tasks": [
      {
        "task_id": "task-001",
        "source_finding_ids": ["finding-001"],
        "assignee": {
          "kind": "subthread",
          "worktree_policy": "separate_worktree",
        },
        "allowed_paths": ["path/to/target.py"],
        "forbidden_paths": [".git/"],
        "depends_on": [],
        "expected_tests": ["python3 -m pytest path/to/test.py -q"],
        "stop_conditions": ["important_decision_requires_approval"],
      }
    ],
    "integration_gate": {
      "requires_main_session_review": True,
      "requires_diff_scope_check": True,
      "requires_tests": True,
      "requires_decision_basis_review": True,
    },
    "history": {
      "ledger_path": f"docs/logs/autonomous-parallel/{run_id}.yaml",
      "record_task_assignments": True,
      "record_decision_basis": True,
      "record_integration_result": True,
      "retention": "preserve",
    },
    "outputs_policy": {
      "implementation_diff": "commit_candidate",
      "verification_summary": "required",
      "decision_basis": "preserve_if_used",
      "work_noise": "exclude",
    },
  }


def cmd_autonomous_plan_template(args):
  """自律・並列モード実行計画のテンプレートを書き出す"""
  plan = build_autonomous_parallel_plan_template(args.run_id)
  out_path = Path(args.out)
  out_path.parent.mkdir(parents=True, exist_ok=True)
  out_path.write_text(
    yaml.safe_dump(plan, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  print(str(out_path))
  return 0


def cmd_autonomous_plan_record_integration(args):
  """自律・並列モード台帳へ統合結果を追記する"""
  ledger_path = Path(args.ledger)
  try:
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
  except OSError as e:
    print(f"error: ledger を読めません: {e}", file=sys.stderr)
    return 2
  except yaml.YAMLError as e:
    print(f"error: ledger を YAML として読めません: {e}", file=sys.stderr)
    return 2

  if not isinstance(ledger, dict):
    print("error: ledger は YAML mapping である必要があります", file=sys.stderr)
    return 2
  if args.status not in ("completed", "blocked", "rejected"):
    print("error: --status は completed / blocked / rejected のいずれかです", file=sys.stderr)
    return 2
  if not args.tests:
    print("error: --tests が必要です", file=sys.stderr)
    return 2
  if not args.decision:
    print("error: --decision が必要です", file=sys.stderr)
    return 2

  ledger["integration_result"] = {
    "status": args.status,
    "tests": args.tests,
    "decision": args.decision,
  }
  ledger_path.write_text(
    yaml.safe_dump(ledger, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  print(str(ledger_path))
  return 0


def cmd_autonomous_plan(args):
  """自律・並列モード実行計画の事前検査を行う"""
  cwd = Path.cwd()
  plan_path = Path(args.plan_path)
  action_str = f"autonomous-plan {plan_path}"
  action_dict = {
    "subcommand": "autonomous-plan",
    "args": {
      "plan_path": str(plan_path),
    },
  }

  try:
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
  except OSError as e:
    reasons = [f"plan_path を読めません: {e}"]
    current_state_dict = {"plan_path": str(plan_path)}
    if args.json:
      print(format_json_output("DEVIATION", 2, action_dict, reasons, current_state_dict))
    else:
      current_state_text = json.dumps(current_state_dict, ensure_ascii=False, indent=2)
      print(format_human_output("DEVIATION", 2, action_str, reasons, current_state_text))
    return 2
  except yaml.YAMLError as e:
    reasons = [f"plan_path を YAML として読めません: {e}"]
    current_state_dict = {"plan_path": str(plan_path)}
    if args.json:
      print(format_json_output("DEVIATION", 2, action_dict, reasons, current_state_dict))
    else:
      current_state_text = json.dumps(current_state_dict, ensure_ascii=False, indent=2)
      print(format_human_output("DEVIATION", 2, action_str, reasons, current_state_text))
    return 2

  reasons, current_state_dict = validate_autonomous_parallel_plan(plan)
  current_state_dict["plan_path"] = str(plan_path)
  if reasons:
    verdict, exit_code = "DEVIATION", 2
  else:
    verdict, exit_code = "OK", 0

  write_autonomous_parallel_ledger(
    cwd,
    plan,
    verdict,
    exit_code,
    reasons,
    current_state_dict,
  )

  if args.json:
    print(format_json_output(verdict, exit_code, action_dict, reasons, current_state_dict))
  else:
    current_state_text = json.dumps(current_state_dict, ensure_ascii=False, indent=2)
    print(format_human_output(verdict, exit_code, action_str, reasons, current_state_text))

  log_path = args.log_path if args.log_path else DEFAULT_LOG_PATH
  try:
    append_log(log_path, action_dict, verdict, exit_code, reasons, current_state_dict)
  except OSError as e:
    print(f"warning: ログ書き込みに失敗しました（処理は続行）: {e}", file=sys.stderr)

  return exit_code


def cmd_spec_set(args):
  """spec-set サブコマンドのエントリポイント

  戻り値：終了コード（0／1／2）
  """
  feature = args.feature
  phase = args.phase
  stage = args.stage
  new_value_str = args.new_value
  rationale = args.rationale

  # 引数妥当性の検査（仕様 §5.1）
  if new_value_str not in ("true", "false"):
    print(
      f"error: new-value は 'true' または 'false' であるべき。受け取り: {new_value_str}",
      file=sys.stderr,
    )
    return 2
  new_value = (new_value_str == "true")

  if phase not in PHASE_STAGES:
    print(
      f"error: phase '{phase}' は無効です。有効値: {', '.join(PHASE_STAGES.keys())}",
      file=sys.stderr,
    )
    return 2

  if stage not in PHASE_STAGES[phase]:
    print(
      f"error: stage '{stage}' は phase '{phase}' で無効です。"
      f"有効値: {', '.join(PHASE_STAGES[phase])}",
      file=sys.stderr,
    )
    return 2

  # spec.json 読み込み
  cwd = Path.cwd()
  spec_data = load_spec_json(cwd, feature)
  if spec_data is None:
    spec_path = cwd / ".reviewcompass" / "specs" / feature / "spec.json"
    print(
      f"error: spec.json が見つかりません。期待パス: {spec_path}",
      file=sys.stderr,
    )
    return 2

  # 判定
  verdict, exit_code, reasons = judge_spec_set(spec_data, phase, stage, new_value)

  # 出力の組み立て
  workflow_state = spec_data.get("workflow_state", {})
  phase_state = workflow_state.get(phase, {})
  current_state_text = format_current_state_text(feature, phase, phase_state)
  current_state_dict = {feature: {phase: phase_state}}

  action_str = f"spec-set {feature} {phase} {stage} {new_value_str}"
  action_dict = {
    "subcommand": "spec-set",
    "args": {
      "feature": feature,
      "phase": phase,
      "stage": stage,
      "new_value": new_value,
      "rationale": rationale,
    },
  }

  if args.json:
    print(format_json_output(verdict, exit_code, action_dict, reasons, current_state_dict))
  else:
    print(format_human_output(verdict, exit_code, action_str, reasons, current_state_text))

  # ログ記録（仕様 §8、MVP 必須）
  log_path = args.log_path if args.log_path else DEFAULT_LOG_PATH
  try:
    append_log(log_path, action_dict, verdict, exit_code, reasons, current_state_dict)
  except OSError as e:
    # ログ書き込み失敗は処理を止めない（警告のみ）
    print(f"warning: ログ書き込みに失敗しました（処理は続行）: {e}", file=sys.stderr)

  return exit_code


def count_unresolved_findings(pending_path):
  """機能横断持ち越し所見ファイルから未消化件数を数える（仕様 §6.2）

  「### A-」で始まり「✅」を含まない行を未消化扱いとする。
  ファイルが存在しない場合は 0 を返す。
  """
  if not Path(pending_path).exists():
    return 0
  count = 0
  for line in Path(pending_path).read_text(encoding="utf-8").splitlines():
    if line.startswith("### A-") and "✅" not in line:
      count += 1
  return count


def classify_staged_file(filepath):
  """staged ファイルを 3 群に分類する（仕様 §6.2）

  戻り値："dangerous" / "caution" / "normal"
  """
  f_lower = filepath.lower()
  if filepath.startswith(".git/") or "secret" in f_lower or "credential" in f_lower:
    return "dangerous"
  if filepath.endswith("spec.json") or filepath.startswith("docs/plan/"):
    return "caution"
  return "normal"


def validate_commit_approval(cwd, staged_files):
  """commit 用ユーザ承認レコードを検査する"""
  approval_path = Path(cwd) / DEFAULT_COMMIT_APPROVAL_PATH
  approval_state = {
    "path": DEFAULT_COMMIT_APPROVAL_PATH,
    "exists": approval_path.exists(),
    "valid": False,
    "target_files": [],
    "consumed": None,
  }

  if not approval_path.exists():
    return approval_state, [
      f"ユーザ承認レコードがありません（{DEFAULT_COMMIT_APPROVAL_PATH}）"
    ]

  try:
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError) as e:
    return approval_state, [f"ユーザ承認レコードを読めません: {e}"]

  if not isinstance(approval, dict):
    return approval_state, ["ユーザ承認レコードの形式が不正です（object ではありません）"]

  target_files = approval.get("target_files")
  if target_files is None:
    target_files = []
  approval_state["target_files"] = target_files
  approval_state["consumed"] = approval.get("consumed")

  errors = []
  if approval.get("approved_action") != "commit":
    errors.append("ユーザ承認レコードの approved_action が commit ではありません")
  if approval.get("approved_by") != "user":
    errors.append("ユーザ承認レコードの approved_by が user ではありません")
  if approval.get("consumed") is True:
    errors.append("ユーザ承認レコードは消費済みです")
  if not isinstance(target_files, list) or not all(isinstance(f, str) for f in target_files):
    errors.append("ユーザ承認レコードの target_files が文字列配列ではありません")
  else:
    approved_set = set(target_files)
    if "*" not in approved_set:
      out_of_scope = [f for f in staged_files if f not in approved_set]
      if out_of_scope:
        errors.append(
          "承認対象外の staged ファイルがあります: " + ", ".join(out_of_scope)
        )

  approval_state["valid"] = not errors
  return approval_state, errors


def cmd_commit(args):
  """commit サブコマンドのエントリポイント（仕様 §6.2）"""
  cwd = Path.cwd()
  rationale = args.rationale

  # git リポジトリ内かの確認
  if not (cwd / ".git").exists():
    print("error: git リポジトリではありません", file=sys.stderr)
    return 2

  # 未消化所見の確認
  pending_path = cwd / ".reviewcompass" / "learning/workflow/carry-forward-register/reviewcompass-import.yaml"
  unresolved_count = count_unresolved_findings(pending_path)

  # staged ファイルの取得と分類
  result = subprocess.run(
    ["git", "diff", "--cached", "--name-only"],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  if result.returncode != 0:
    print(f"error: git diff 失敗: {result.stderr}", file=sys.stderr)
    return 2

  staged_files = [f for f in result.stdout.strip().splitlines() if f]
  dangerous = [f for f in staged_files if classify_staged_file(f) == "dangerous"]
  caution = [f for f in staged_files if classify_staged_file(f) == "caution"]
  normal = [f for f in staged_files if classify_staged_file(f) == "normal"]
  approval_state, approval_errors = validate_commit_approval(cwd, staged_files)
  post_write_state, post_write_errors = validate_post_write_completion_for_targets(
    cwd,
    staged_files,
  )

  # 判定（仕様 §6.2）
  reasons = []
  deviation_reasons = []
  if approval_errors:
    deviation_reasons.extend(approval_errors)
  if dangerous:
    for f in dangerous:
      deviation_reasons.append(f"危険変更: {f}（commit を遮断推奨）")
  if post_write_errors:
    deviation_reasons.extend(post_write_errors)

  if deviation_reasons:
    reasons.extend(deviation_reasons)
    verdict, exit_code = "DEVIATION", 2
  elif unresolved_count > 0 or caution:
    if unresolved_count > 0:
      reasons.append(
        f"未消化所見が {unresolved_count} 件あります"
        f"（learning/workflow/carry-forward-register/reviewcompass-import.yaml）"
      )
    for f in caution:
      reasons.append(f"要注意変更: {f}（変更根拠を確認してください）")
    verdict, exit_code = "WARN", 1
  else:
    verdict, exit_code = "OK", 0

  # 出力の組み立て
  current_state_text = (
    f"未消化所見: {unresolved_count} 件\n"
    f"staged ファイル数: {len(staged_files)} 件\n"
    f"  危険変更: {len(dangerous)} 件\n"
    f"  要注意変更: {len(caution)} 件\n"
    f"  通常変更: {len(normal)} 件\n"
    f"ユーザ承認レコード: {'有効' if approval_state['valid'] else '無効'}\n"
    f"post-write-verification 対象: {len(post_write_state['target_files'])} 件\n"
    f"post-write-verification 状態: {post_write_state['manifest_status']}"
  )
  current_state_dict = {
    "pending_unresolved_count": unresolved_count,
    "staged_files": {
      "dangerous": dangerous,
      "caution": caution,
      "normal": normal,
    },
    "commit_approval": approval_state,
    "post_write_verification": post_write_state,
  }
  action_str = f"commit (rationale='{rationale}')"
  action_dict = {
    "subcommand": "commit",
    "args": {"rationale": rationale},
  }

  if args.json:
    print(format_json_output(verdict, exit_code, action_dict, reasons, current_state_dict))
  else:
    print(format_human_output(verdict, exit_code, action_str, reasons, current_state_text))

  # ログ記録
  log_path = args.log_path if args.log_path else DEFAULT_LOG_PATH
  try:
    append_log(log_path, action_dict, verdict, exit_code, reasons, current_state_dict)
  except OSError as e:
    print(f"warning: ログ書き込みに失敗しました（処理は続行）: {e}", file=sys.stderr)

  return exit_code


def cmd_push(args):
  """push サブコマンドのエントリポイント（仕様 §6.3）"""
  cwd = Path.cwd()
  rationale = args.rationale

  # git リポジトリ内かの確認
  if not (cwd / ".git").exists():
    print("error: git リポジトリではありません", file=sys.stderr)
    return 2

  # 作業ツリーの clean 性
  status_result = subprocess.run(
    ["git", "status", "--porcelain"],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  if status_result.returncode != 0:
    print(f"error: git status 失敗: {status_result.stderr}", file=sys.stderr)
    return 2

  is_dirty = bool(status_result.stdout.strip())

  # 直近 5 コミット
  log_result = subprocess.run(
    ["git", "log", "--oneline", "-5"],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  recent_commits = log_result.stdout.strip() if log_result.returncode == 0 else "(取得失敗)"

  # ローカル先行コミット数（origin/main がない場合は情報なし）
  ahead_result = subprocess.run(
    ["git", "rev-list", "--count", "origin/main..HEAD"],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  ahead_info = (
    ahead_result.stdout.strip()
    if ahead_result.returncode == 0
    else "(リモート origin/main が未設定または取得失敗)"
  )

  # 判定（仕様 §6.3）
  reasons = []
  if is_dirty:
    reasons.append("作業ツリーに未コミット変更があります（push 前に commit が必要）")
    verdict, exit_code = "DEVIATION", 2
  else:
    verdict, exit_code = "OK", 0

  # 出力の組み立て
  current_state_text = (
    f"作業ツリー: {'dirty' if is_dirty else 'clean'}\n"
    f"origin/main からの先行コミット数: {ahead_info}\n"
    f"直近 5 コミット:\n{recent_commits}"
  )
  current_state_dict = {
    "is_dirty": is_dirty,
    "ahead_count": ahead_info,
    "recent_commits": recent_commits.splitlines() if recent_commits else [],
  }
  action_str = f"push (rationale='{rationale}')"
  action_dict = {
    "subcommand": "push",
    "args": {"rationale": rationale},
  }

  if args.json:
    print(format_json_output(verdict, exit_code, action_dict, reasons, current_state_dict))
  else:
    print(format_human_output(verdict, exit_code, action_str, reasons, current_state_text))

  # ログ記録
  log_path = args.log_path if args.log_path else DEFAULT_LOG_PATH
  try:
    append_log(log_path, action_dict, verdict, exit_code, reasons, current_state_dict)
  except OSError as e:
    print(f"warning: ログ書き込みに失敗しました（処理は続行）: {e}", file=sys.stderr)

  return exit_code


def list_commit_changed_files(cwd, commitish):
  """指定 commit の変更ファイル一覧を返す"""
  result = subprocess.run(
    ["git", "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", commitish],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  if result.returncode != 0:
    raise ValueError(result.stderr.strip() or f"commit を読めません: {commitish}")
  return sorted(set(f for f in result.stdout.splitlines() if f))


def commit_file_sha256(cwd, commitish, path):
  """指定 commit 内のファイル内容 sha256 を返す"""
  result = subprocess.run(
    ["git", "show", f"{commitish}:{path}"],
    cwd=str(cwd),
    capture_output=True,
  )
  if result.returncode != 0:
    return None
  return hashlib.sha256(result.stdout).hexdigest()


def cmd_audit_commit(args):
  """audit-commit サブコマンドのエントリポイント"""
  cwd = Path.cwd()
  commitish = args.commitish

  if not (cwd / ".git").exists():
    print("error: git リポジトリではありません", file=sys.stderr)
    return 2

  try:
    changed_files = list_commit_changed_files(cwd, commitish)
  except ValueError as e:
    print(f"error: {e}", file=sys.stderr)
    return 2

  post_write_targets = [
    path
    for path in changed_files
    if is_post_write_verification_target(path)
  ]
  commit_hashes = {
    target: commit_file_sha256(cwd, commitish, target)
    for target in post_write_targets
  }
  post_write_state, post_write_errors = validate_post_write_completion_for_targets(
    cwd,
    post_write_targets,
    commit_hashes,
  )

  if post_write_errors:
    verdict, exit_code = "DEVIATION", 2
    reasons = [
      reason.replace("staged ファイル", "commit 対象ファイル")
      for reason in post_write_errors
    ]
  else:
    verdict, exit_code = "OK", 0
    reasons = []

  current_state_text = (
    f"commit: {commitish}\n"
    f"変更ファイル数: {len(changed_files)} 件\n"
    f"post-write-verification 対象: {len(post_write_targets)} 件\n"
    f"post-write-verification 状態: {post_write_state['manifest_status']}"
  )
  current_state_dict = {
    "commit": commitish,
    "changed_files": changed_files,
    "post_write_targets": post_write_targets,
    "post_write_verification": post_write_state,
  }
  action_str = f"audit-commit {commitish}"
  action_dict = {
    "subcommand": "audit-commit",
    "args": {"commitish": commitish},
  }

  if args.json:
    print(format_json_output(verdict, exit_code, action_dict, reasons, current_state_dict))
  else:
    print(format_human_output(verdict, exit_code, action_str, reasons, current_state_text))

  log_path = args.log_path if args.log_path else DEFAULT_LOG_PATH
  try:
    append_log(log_path, action_dict, verdict, exit_code, reasons, current_state_dict)
  except OSError as e:
    print(f"warning: ログ書き込みに失敗しました（処理は続行）: {e}", file=sys.stderr)

  return exit_code


def list_in_progress_files(cwd):
  """stages/in-progress 配下の進行中ファイルを相対パス文字列で返す"""
  in_progress_dir = Path(cwd) / "stages" / "in-progress"
  if not in_progress_dir.exists():
    return []
  files = [p for p in in_progress_dir.iterdir() if p.is_file()]
  return [str(p.relative_to(cwd)) for p in sorted(files)]


def load_in_progress_file(cwd, relative_path):
  """進行中状態ファイルを YAML として読み込む"""
  path = Path(cwd) / relative_path
  try:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
  except (OSError, yaml.YAMLError):
    return {}
  return data if isinstance(data, dict) else {}


def resolve_reopen_required_action(next_step, current_blocker, step_number=None):
  """reopen の next_step/current_blocker から要求アクションを返す"""
  if current_blocker:
    return "wait_for_human_approval"
  if step_number in (1, "1"):
    return "classify_and_rollback_flags"
  if step_number in (2, "2"):
    return "repair_canonical_documents"
  if step_number in (3, "3"):
    return "rerun_alignment_approval_chain"
  if step_number in (4, "4"):
    return "finalize_reopen"
  if not next_step:
    return "inspect_reopen_state"
  # 既存の in-progress YAML は next_step の日本語表記を正本として持つ。
  # 将来生成分は step_number を併記し、文字列表記ゆれへの依存を下げる。
  if "第1過程" in next_step:
    return "classify_and_rollback_flags"
  if "第2過程" in next_step:
    return "repair_canonical_documents"
  if "第3過程" in next_step:
    return "rerun_alignment_approval_chain"
  if "第4過程" in next_step:
    return "finalize_reopen"
  if "完了" in next_step:
    return "reopen_completed"
  return "inspect_reopen_state"


def build_in_progress_next_action(cwd, relative_path):
  """進行中状態ファイルから next_action を作る"""
  data = load_in_progress_file(cwd, relative_path)
  process_id = data.get("process_id")
  if process_id == "maintenance":
    return {
      "kind": "maintenance_in_progress",
      "file": relative_path,
      "process_id": process_id,
      "title": data.get("title"),
      "required_action": data.get("required_action", "continue_maintenance"),
      "blocked_normal_workflow": data.get("blocked_normal_workflow", True),
      "allowed_scope": data.get("allowed_scope", []),
      "completion_conditions": data.get("completion_conditions", []),
      "feature": None,
      "phase": None,
      "stage": None,
      "reason": data.get(
        "reason",
        "maintenance 手続きの進行中状態ファイルがあります",
      ),
    }
  if process_id == "reopen-procedure":
    next_step = data.get("next_step")
    current_blocker = data.get("current_blocker")
    pending_gates = data.get("pending_gates", [])
    if pending_gates is None:
      pending_gates = []
    return {
      "kind": "reopen_in_progress",
      "file": relative_path,
      "process_id": process_id,
      "next_step": next_step,
      "step_number": data.get("step_number"),
      "completed_steps": data.get("completed_steps", []),
      "pending_gates": pending_gates,
      "current_blocker": current_blocker,
      "required_action": resolve_reopen_required_action(
        next_step,
        current_blocker,
        data.get("step_number"),
      ),
      "feature": data.get("feature"),
      "phase": None,
      "stage": None,
      "reason": "reopen 手続きの進行中状態ファイルがあります",
    }
  return {
    "kind": "resume_in_progress",
    "file": relative_path,
    "feature": None,
    "phase": None,
    "stage": None,
    "reason": "stages/in-progress に進行中ファイルがあるため、新規作業より優先します",
  }


def parse_git_status_path(line):
  """git status --short の 1 行から変更後パスを取り出す"""
  if len(line) < 4:
    return None
  path = line[3:]
  if " -> " in path:
    path = path.split(" -> ", 1)[1]
  return path.strip()


def list_changed_files(cwd):
  """git status --short から未コミット変更ファイルを返す"""
  if not (Path(cwd) / ".git").exists():
    return []
  result = subprocess.run(
    ["git", "status", "--short", "--untracked-files=all"],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  if result.returncode != 0:
    return []
  paths = []
  for line in result.stdout.splitlines():
    path = parse_git_status_path(line)
    if path:
      paths.append(path)
  return sorted(set(paths))


def list_untracked_files(cwd):
  """git status --short から未追跡ファイルを返す"""
  if not (Path(cwd) / ".git").exists():
    return []
  result = subprocess.run(
    ["git", "status", "--short", "--untracked-files=all"],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )
  if result.returncode != 0:
    return []
  paths = []
  for line in result.stdout.splitlines():
    if line.startswith("?? "):
      path = parse_git_status_path(line)
      if path:
        paths.append(path)
  return sorted(set(paths))


def is_post_write_verification_target(path):
  """post-write-verification 規律の対象ファイルかを判定する"""
  if path.startswith("docs/archive/"):
    return False
  if path == "TODO_NEXT_SESSION.md":
    return True
  if any(path.startswith(prefix) for prefix in POST_WRITE_VERIFICATION_DIR_PREFIXES):
    return True
  if path.startswith("docs/reviews/"):
    name = Path(path).name
    return (
      name.startswith("reopen-classification-")
      or "-audit-" in name
    ) and name.endswith(".md")
  return False


def list_post_write_verification_targets(cwd):
  """未コミット変更のうち post-write-verification 対象を返す"""
  return [
    path
    for path in list_changed_files(cwd)
    if is_post_write_verification_target(path)
  ]


def is_forbidden_post_write_pending_change(path, verification_targets):
  """post-write-verification pending 中に禁止する変更かを判定する"""
  if path.startswith("tools/") and path.endswith(".py"):
    return True
  if path.startswith("templates/"):
    return True
  if path.startswith("docs/disciplines/"):
    non_discipline_targets = [
      target
      for target in verification_targets
      if not target.startswith("docs/disciplines/")
    ]
    return bool(non_discipline_targets)
  return False


def list_forbidden_post_write_pending_changes(cwd, verification_targets):
  """post-write-verification pending 中の禁止変更を返す"""
  return [
    path
    for path in list_changed_files(cwd)
    if is_forbidden_post_write_pending_change(path, verification_targets)
  ]


def load_post_write_manifests(cwd):
  """post-write-verification manifest を読み込む"""
  manifest_dir = Path(cwd) / ".reviewcompass" / "post-write-verification"
  if not manifest_dir.exists():
    return []
  manifests = []
  # 同じ対象を覆う manifest が複数ある場合は、ファイル名が新しいものを優先する。
  # 命名は post-write-YYYY-MM-DD-NNN.yaml の辞書順を前提にする。
  for path in sorted(manifest_dir.glob("*.yaml"), reverse=True):
    try:
      data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
      continue
    if isinstance(data, dict):
      data["_path"] = str(path.relative_to(cwd))
      manifests.append(data)
  return manifests


def verifier_requirements_satisfied(manifest):
  """required_verifiers が completed_verifiers で満たされているかを返す（旧形式フォールバック用）"""
  required = set(manifest.get("required_verifiers") or [])
  if not required:
    return False
  completed = set(manifest.get("completed_verifiers") or [])
  return required.issubset(completed)


def coverage_matrix_satisfied(manifest, target_files):
  """verifications[] の各 required_verifier が全 target_files を網羅しているかを確認する

  verifications[] が存在しない場合は None を返す（呼び出し側で旧形式へフォールバック）。
  存在する場合は、required_verifiers の各検証者について verifications[] の中に
  全 target_files を target_files として含むエントリがあるかを確認する。
  """
  verifications = manifest.get("verifications")
  if not isinstance(verifications, list) or not verifications:
    return None

  required = set(manifest.get("required_verifiers") or [])
  if not required:
    return False

  target_set = set(target_files)
  master_sha256 = manifest.get("target_sha256") or {}

  for verifier in required:
    verifier_has_valid_entry = False
    for entry in verifications:
      if entry.get("verifier") != verifier:
        continue
      entry_targets = set(entry.get("target_files") or [])
      if not target_set.issubset(entry_targets):
        continue
      entry_sha256 = entry.get("target_sha256")
      if not isinstance(entry_sha256, dict):
        continue
      sha256_matches = all(
        entry_sha256.get(t) == master_sha256.get(t)
        for t in target_files
      )
      if sha256_matches:
        verifier_has_valid_entry = True
        break
    if not verifier_has_valid_entry:
      return False
  return True


def unresolved_substantive_count(manifest):
  """manifest の未解決本質的指摘件数を整数で返す"""
  value = manifest.get("unresolved_substantive_findings", 0)
  try:
    return int(value)
  except (TypeError, ValueError):
    return 0


def file_sha256(path):
  """ファイル内容の sha256 を返す。読めない場合は None。"""
  try:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
  except OSError:
    return None


def manifest_hashes_match_current_files(cwd, manifest, target_files):
  """manifest の target_sha256 が現在の対象ファイル内容と一致するかを返す"""
  actual_hashes = {
    target: file_sha256(Path(cwd) / target)
    for target in target_files
  }
  return manifest_hashes_match_values(manifest, target_files, actual_hashes)


def manifest_hashes_match_values(manifest, target_files, actual_hashes):
  """manifest の target_sha256 が指定 hash と一致するかを返す"""
  expected = manifest.get("target_sha256")
  if not isinstance(expected, dict) or not expected:
    return False

  for target in target_files:
    expected_hash = expected.get(target)
    if not expected_hash:
      return False
    actual_hash = actual_hashes.get(target)
    if actual_hash != expected_hash:
      return False
  return True


def load_yaml_file(path):
  """YAML ファイルを dict/list として読み込む。読めない場合は None。"""
  try:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))
  except (OSError, yaml.YAMLError):
    return None


def resolve_review_run_path(cwd, run_dir, value):
  """review run 内の相対パスを実ファイルパスへ解決する"""
  if not value:
    return None
  path = Path(value)
  if path.is_absolute():
    return path
  candidate_from_cwd = Path(cwd) / path
  if candidate_from_cwd.exists():
    return candidate_from_cwd
  return Path(run_dir) / path


def review_run_traceability_satisfied(cwd, manifest):
  """review_run 宣言付き manifest の raw/rounds/triage/summary 整合を検査する

  review_run がない旧 manifest は対象外として True を返す。
  """
  review_run = manifest.get("review_run")
  if review_run is None:
    return True
  if not isinstance(review_run, dict):
    return False

  run_path = review_run.get("path")
  if not run_path:
    return False
  run_dir = Path(cwd) / run_path
  if not run_dir.is_dir():
    return False

  target_manifest_path = run_dir / "target-manifest.yaml"
  rounds_path = run_dir / "rounds.yaml"
  triage_path = run_dir / "triage.yaml"
  summary_path = review_run.get("summary_path")
  if summary_path:
    summary_file = resolve_review_run_path(cwd, run_dir, summary_path)
  else:
    summary_file = run_dir / "model-result-summary.yaml"

  required_paths = [
    target_manifest_path,
    rounds_path,
    triage_path,
    summary_file,
  ]
  if any(path is None or not Path(path).is_file() for path in required_paths):
    return False

  rounds = load_yaml_file(rounds_path)
  triage = load_yaml_file(triage_path)
  summary = load_yaml_file(summary_file)
  if not isinstance(rounds, dict):
    return False
  if not isinstance(triage, dict):
    return False
  if not isinstance(summary, dict):
    return False

  model_results = rounds.get("model_results")
  if not isinstance(model_results, list) or not model_results:
    return False

  required_verifiers = set(manifest.get("required_verifiers") or [])
  model_ids = set()
  for result in model_results:
    if not isinstance(result, dict):
      return False
    model_id = result.get("model_id")
    raw_path = result.get("raw_path")
    raw_sha256 = result.get("raw_sha256")
    parse_status = result.get("parse_status")
    if not model_id or not raw_path or not raw_sha256:
      return False
    if parse_status not in ("parsed", "parse_failed"):
      return False

    raw_file = resolve_review_run_path(cwd, run_dir, raw_path)
    if raw_file is None or not raw_file.is_file():
      return False
    if file_sha256(raw_file) != raw_sha256:
      return False
    model_ids.add(model_id)

  if required_verifiers and not required_verifiers.issubset(model_ids):
    return False

  summary_models = summary.get("models")
  if not isinstance(summary_models, list):
    return False
  summary_by_model = {
    item.get("model_id"): item
    for item in summary_models
    if isinstance(item, dict) and item.get("model_id")
  }
  if not model_ids.issubset(set(summary_by_model)):
    return False

  triage_items = triage.get("items")
  if not isinstance(triage_items, list):
    return False
  triaged_models = set()
  for item in triage_items:
    if not isinstance(item, dict):
      return False
    source_model = item.get("source_model")
    source_raw_path = item.get("source_raw_path")
    decision_status = item.get("decision_status")
    final_label = item.get("final_label")
    if source_model:
      triaged_models.add(source_model)
    if source_raw_path:
      raw_file = resolve_review_run_path(cwd, run_dir, source_raw_path)
      if raw_file is None or not raw_file.is_file():
        return False
    if decision_status == "human_required":
      return False
    if decision_status != "decided":
      return False
    if final_label not in ("must-fix", "should-fix", "leave-as-is"):
      return False

  for model_id in model_ids:
    summary_item = summary_by_model[model_id]
    triage_status = summary_item.get("triage_status")
    if model_id not in triaged_models and triage_status != "no_findings":
      return False
    if triage_status not in ("triaged", "no_findings"):
      return False

  return True


def evaluate_post_write_manifest_state(cwd, target_files):
  """対象ファイル群に対する post-write-verification manifest 状態を返す"""
  actual_hashes = {
    target: file_sha256(Path(cwd) / target)
    for target in target_files
  }
  return evaluate_post_write_manifest_state_for_hashes(cwd, target_files, actual_hashes)


def evaluate_post_write_manifest_state_for_hashes(cwd, target_files, actual_hashes):
  """指定 sha256 群に対する post-write-verification manifest 状態を返す"""
  target_set = set(target_files)
  for manifest in load_post_write_manifests(cwd):
    manifest_targets = set(manifest.get("target_files") or [])
    if not target_set.issubset(manifest_targets):
      continue
    if not manifest_hashes_match_values(manifest, target_files, actual_hashes):
      continue
    if unresolved_substantive_count(manifest) > 0:
      return "human_required", manifest
    coverage_ok = coverage_matrix_satisfied(manifest, target_files)
    if coverage_ok is None:
      coverage_ok = verifier_requirements_satisfied(manifest)
    if (
      manifest.get("status") == "completed"
      and coverage_ok
      and review_run_traceability_satisfied(cwd, manifest)
      and unresolved_substantive_count(manifest) == 0
    ):
      return "completed", manifest
  return "pending", None


def validate_post_write_completion_for_targets(cwd, target_files, actual_hashes=None):
  """post-write 対象ファイルの完了 manifest があるか検査する"""
  post_write_targets = [
    path
    for path in target_files
    if is_post_write_verification_target(path)
  ]
  state = {
    "target_files": post_write_targets,
    "manifest_status": "not_applicable" if not post_write_targets else "pending",
    "manifest_path": None,
  }
  if not post_write_targets:
    return state, []

  if actual_hashes is None:
    actual_hashes = {
      target: file_sha256(Path(cwd) / target)
      for target in post_write_targets
    }
  else:
    actual_hashes = {
      target: actual_hashes.get(target)
      for target in post_write_targets
    }

  manifest_status, manifest = evaluate_post_write_manifest_state_for_hashes(
    cwd,
    post_write_targets,
    actual_hashes,
  )
  state["manifest_status"] = manifest_status
  if manifest:
    state["manifest_path"] = manifest.get("_path")
  if manifest_status == "completed":
    return state, []
  if manifest_status == "human_required":
    return state, [
      "post-write-verification に未解決の本質的指摘があります: "
      + ", ".join(post_write_targets)
    ]
  return state, [
    "post-write-verification 未完了の staged ファイルがあります: "
    + ", ".join(post_write_targets)
  ]


def load_all_feature_specs(cwd):
  """ReviewCompass の全 feature spec.json を読み込む"""
  specs = {}
  missing = []
  for feature in FEATURE_ORDER:
    spec_data = load_spec_json(cwd, feature)
    if spec_data is None:
      missing.append(feature)
    else:
      specs[feature] = spec_data
  return specs, missing


def summarize_workflow_state(specs):
  """next 出力用に workflow_state だけを抽出する"""
  return {
    feature: spec_data.get("workflow_state", {})
    for feature, spec_data in specs.items()
  }


def phase_stage_value(specs, feature, phase, stage):
  """workflow_state.<phase>.<stage> の真偽値を返す"""
  return bool(
    specs
    .get(feature, {})
    .get("workflow_state", {})
    .get(phase, {})
    .get(stage, False)
  )


def all_features_stage_true(specs, phase, stage):
  """全 feature で指定 phase/stage が true かを返す"""
  return all(phase_stage_value(specs, feature, phase, stage) for feature in FEATURE_ORDER)


def build_stage_next_action(feature, phase, stage, reason):
  """機能単位 stage の next_action を作る"""
  return {
    "kind": "stage",
    "feature": feature,
    "phase": phase,
    "stage": stage,
    "reason": reason,
  }


def build_cross_stage_next_action(phase, stage, reason):
  """機能横断 stage の next_action を作る"""
  return {
    "kind": "cross_feature_stage",
    "feature": "all_features",
    "phase": phase,
    "stage": stage,
    "reason": reason,
  }


def collect_recheck_items(specs, phase):
  """指定 phase に影響する upstream recheck 項目を集める"""
  items = []
  for feature in FEATURE_ORDER:
    recheck = specs.get(feature, {}).get("recheck", {})
    if not recheck.get("upstream_change_pending", False):
      continue
    impacted = recheck.get("impacted_downstream_phases", [])
    if phase in impacted:
      items.append({
        "feature": feature,
        "impacted_downstream_phases": impacted,
      })
  return items


def augment_cross_feature_next_action(cwd, specs, next_action):
  """機能横断段に必要な確認情報を付加する"""
  if next_action.get("kind") != "cross_feature_stage":
    return next_action

  phase = next_action.get("phase")
  stage = next_action.get("stage")
  augmented = dict(next_action)

  recheck_items = collect_recheck_items(specs, phase)
  if recheck_items:
    augmented["recheck_items"] = recheck_items

  if stage == "review-wave":
    pending_path = Path(cwd) / ".reviewcompass" / "learning/workflow/carry-forward-register/reviewcompass-import.yaml"
    augmented["pending_cross_feature_findings"] = {
      "file": "learning/workflow/carry-forward-register/reviewcompass-import.yaml",
      "unresolved_count": count_unresolved_findings(pending_path),
    }

  return augmented


def resolve_next_action(specs):
  """ReviewCompass 現行 workflow_state から次に許可される作業を決める"""
  for phase in PHASE_ORDER:
    stages = PHASE_STAGES[phase]

    if phase in CROSS_FEATURE_PHASES:
      for stage in stages:
        if not all_features_stage_true(specs, phase, stage):
          return build_cross_stage_next_action(
            phase,
            stage,
            f"{phase}.{stage} が全 feature で完了していません",
          )
      continue

    for feature in FEATURE_ORDER:
      if not phase_stage_value(specs, feature, phase, "drafting"):
        return build_stage_next_action(
          feature,
          phase,
          "drafting",
          f"{feature} の {phase}.drafting が未完了です",
        )
      if not phase_stage_value(specs, feature, phase, "triad-review"):
        return build_stage_next_action(
          feature,
          phase,
          "triad-review",
          f"{feature} の {phase}.triad-review が未完了です",
        )

    for stage in ("review-wave", "alignment", "approval"):
      if stage in stages and not all_features_stage_true(specs, phase, stage):
        return build_cross_stage_next_action(
          phase,
          stage,
          f"{phase}.{stage} が全 feature で完了していません",
        )

  return {
    "kind": "completed",
    "feature": None,
    "phase": None,
    "stage": None,
    "reason": "すべての workflow_state が完了しています",
  }


def format_next_human_output(verdict, exit_code, next_action, reasons, current_state_dict):
  """next サブコマンドの人間可読出力を整形する"""
  lines = [
    f"[VERDICT] {verdict}（exit {exit_code}）",
    "[NEXT ACTION]",
    f"  kind: {next_action.get('kind')}",
    f"  feature: {next_action.get('feature')}",
    f"  phase: {next_action.get('phase')}",
    f"  stage: {next_action.get('stage')}",
    f"  reason: {next_action.get('reason')}",
    "[REASON]",
  ]
  if reasons:
    for reason in reasons:
      lines.append(f"  - {reason}")
  else:
    lines.append("  - 問題は検出されませんでした")
  lines.append("[CURRENT STATE]")
  lines.append(json.dumps(current_state_dict, ensure_ascii=False, indent=2))
  return "\n".join(lines)


def cmd_next(args):
  """next サブコマンドのエントリポイント"""
  cwd = Path.cwd()
  in_progress_files = list_in_progress_files(cwd)
  maintenance_action = None

  if in_progress_files:
    in_progress_action = build_in_progress_next_action(cwd, in_progress_files[0])
    if in_progress_action.get("kind") != "maintenance_in_progress":
      next_action = in_progress_action
      current_state = {"in_progress_files": in_progress_files}
      reasons = []
      verdict, exit_code = "OK", 0
    else:
      maintenance_action = in_progress_action

  if not in_progress_files or maintenance_action:
    verification_targets = list_post_write_verification_targets(cwd)
    if verification_targets:
      manifest_state, manifest = evaluate_post_write_manifest_state(cwd, verification_targets)
      if manifest_state == "completed":
        if maintenance_action:
          next_action = maintenance_action
          current_state = {
            "in_progress_files": in_progress_files,
            "post_write_manifest": manifest.get("_path"),
          }
          reasons = []
          verdict, exit_code = "OK", 0
        else:
          specs, missing = load_all_feature_specs(cwd)
          if missing:
            next_action = {
              "kind": "unknown",
              "feature": None,
              "phase": None,
              "stage": None,
              "reason": "必要な spec.json が不足しています",
            }
            current_state = {"missing_features": missing, "manifest": manifest}
            reasons = [f"{feature} の spec.json が見つかりません" for feature in missing]
            verdict, exit_code = "DEVIATION", 2
          else:
            next_action = augment_cross_feature_next_action(
              cwd,
              specs,
              resolve_next_action(specs),
            )
            current_state = {
              "feature_order": FEATURE_ORDER,
              "workflow_state": summarize_workflow_state(specs),
              "post_write_manifest": manifest.get("_path"),
            }
            reasons = []
            verdict, exit_code = "OK", 0
      else:
        forbidden_files = list_forbidden_post_write_pending_changes(cwd, verification_targets)
        if forbidden_files:
          next_action = {
            "kind": "post_write_policy_violation",
            "target_files": verification_targets,
            "forbidden_files": forbidden_files,
            "feature": None,
            "phase": None,
            "stage": None,
            "reason": "post-write-verification pending 中に禁止された変更があります",
          }
          current_state = {
            "post_write_verification_targets": verification_targets,
            "forbidden_files": forbidden_files,
          }
          if maintenance_action:
            current_state["in_progress_files"] = in_progress_files
          reasons = [
            f"{path} は post-write-verification pending 中に変更してはいけません"
            for path in forbidden_files
          ]
          verdict, exit_code = "DEVIATION", 2
        elif manifest_state == "human_required":
          next_action = {
            "kind": "post_write_human_decision_required",
            "target_files": verification_targets,
            "manifest": manifest.get("_path"),
            "feature": None,
            "phase": None,
            "stage": None,
            "reason": "post-write-verification に未解決の本質的指摘があります",
          }
          current_state = {
            "post_write_verification_targets": verification_targets,
            "manifest": manifest,
          }
          if maintenance_action:
            current_state["in_progress_files"] = in_progress_files
          reasons = ["未解決の本質的指摘について人間判断が必要です"]
          verdict, exit_code = "OK", 0
        else:
          next_action = {
            "kind": "post_write_verification",
            "target_files": verification_targets,
            "feature": None,
            "phase": None,
            "stage": None,
            "reason": "post-write-verification 対象の未コミット変更があります",
          }
          current_state = {"post_write_verification_targets": verification_targets}
          if maintenance_action:
            current_state["in_progress_files"] = in_progress_files
          reasons = []
          verdict, exit_code = "OK", 0
    else:
      if maintenance_action:
        next_action = maintenance_action
        current_state = {"in_progress_files": in_progress_files}
        reasons = []
        verdict, exit_code = "OK", 0
      else:
        specs, missing = load_all_feature_specs(cwd)
        if missing:
          next_action = {
            "kind": "unknown",
            "feature": None,
            "phase": None,
            "stage": None,
            "reason": "必要な spec.json が不足しています",
          }
          current_state = {"missing_features": missing}
          reasons = [f"{feature} の spec.json が見つかりません" for feature in missing]
          verdict, exit_code = "DEVIATION", 2
        else:
          next_action = augment_cross_feature_next_action(
            cwd,
            specs,
            resolve_next_action(specs),
          )
          current_state = {
            "feature_order": FEATURE_ORDER,
            "workflow_state": summarize_workflow_state(specs),
          }
          reasons = []
          verdict, exit_code = "OK", 0

  if args.json:
    print(format_next_json_output(verdict, exit_code, next_action, reasons, current_state))
  else:
    print(format_next_human_output(verdict, exit_code, next_action, reasons, current_state))

  action_dict = {"subcommand": "next", "args": {}}
  log_path = args.log_path if args.log_path else DEFAULT_LOG_PATH
  try:
    append_log(log_path, action_dict, verdict, exit_code, reasons, current_state)
  except OSError as e:
    print(f"warning: ログ書き込みに失敗しました（処理は続行）: {e}", file=sys.stderr)

  return exit_code


def build_reopen_in_progress_data(args, pending_gates):
  """reopen-start で生成する in-progress データを作る"""
  return {
    "process_id": "reopen-procedure",
    "feature": args.feature,
    "classification": args.classification,
    "started_at": f"{args.date}T00:00:00+09:00",
    "trigger": args.trigger,
    "classification_basis": args.basis,
    "completed_steps": [],
    "next_step": "第1過程：判定とフラグ差し戻し",
    "step_number": 1,
    "pending_gates": pending_gates,
    "current_blocker": None,
  }


def write_reopen_in_progress(cwd, date, data):
  """reopen in-progress YAML を書き出す"""
  path = Path(cwd) / "stages" / "in-progress" / f"reopen-procedure-{date}.yaml"
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  return path


def cmd_reopen_start(args):
  """reopen-start サブコマンドのエントリポイント"""
  cwd = Path.cwd()
  pending_gates = REOPEN_TRIGGER_MAP.get(args.classification)
  if pending_gates is None:
    verdict, exit_code = "DEVIATION", 2
    reasons = [f"classification {args.classification} は trigger_map に存在しません"]
    next_action = {
      "kind": "reopen_start_failed",
      "classification": args.classification,
      "feature": args.feature,
      "phase": None,
      "stage": None,
      "reason": "未定義の reopen classification です",
    }
    current_state = {"known_classifications": sorted(REOPEN_TRIGGER_MAP.keys())}
  else:
    data = build_reopen_in_progress_data(args, pending_gates)
    path = write_reopen_in_progress(cwd, args.date, data)
    verdict, exit_code = "OK", 0
    reasons = []
    next_action = {
      "kind": "reopen_started",
      "file": str(path.relative_to(cwd)),
      "classification": args.classification,
      "feature": args.feature,
      "pending_gates": pending_gates,
      "phase": None,
      "stage": None,
      "reason": "reopen in-progress ファイルを生成しました",
    }
    current_state = data

  if args.json:
    print(format_next_json_output(verdict, exit_code, next_action, reasons, current_state))
  else:
    print(format_next_human_output(verdict, exit_code, next_action, reasons, current_state))

  action_dict = {
    "subcommand": "reopen-start",
    "args": {
      "classification": args.classification,
      "feature": args.feature,
      "basis": args.basis,
      "date": args.date,
      "trigger": args.trigger,
    },
  }
  log_path = args.log_path if args.log_path else DEFAULT_LOG_PATH
  try:
    append_log(log_path, action_dict, verdict, exit_code, reasons, current_state)
  except OSError as e:
    print(f"warning: ログ書き込みに失敗しました（処理は続行）: {e}", file=sys.stderr)

  return exit_code


def main():
  # 共通オプション（サブコマンドの前後どちらでも受け取れるよう親パーサに集約、仕様 §4 共通オプション）
  common_parser = argparse.ArgumentParser(add_help=False)
  common_parser.add_argument(
    "--json",
    action="store_true",
    help="出力を JSON 形式に切り替える（仕様 §7.3）",
  )
  common_parser.add_argument(
    "--log-path",
    default=None,
    help=f"ログ書き出し先の上書き（既定 {DEFAULT_LOG_PATH}、仕様 §8.2）",
  )

  parser = argparse.ArgumentParser(
    description=(
      "ワークフロー事前検査スクリプト（補助層 C 段階 2、"
      "仕様 docs/operations/WORKFLOW_PRECHECK.md）"
    ),
    parents=[common_parser],
  )

  sub = parser.add_subparsers(dest="subcommand", required=True)

  # spec-set サブコマンド（仕様 §5.1）
  ss = sub.add_parser(
    "spec-set",
    help="workflow_state の変更を判定する",
    parents=[common_parser],
  )
  ss.add_argument("feature", help="対象機能名（例：foundation／runtime／…）")
  ss.add_argument("phase", help="対象フェーズ（intent／feature-partitioning／requirements 等）")
  ss.add_argument("stage", help="対象段（drafting／triad-review／review-wave／alignment／approval 等）")
  ss.add_argument("new_value", help="設定したい新しい真偽値（true または false）")
  ss.add_argument(
    "--rationale",
    default=None,
    help="この変更を行う理由（任意、ログ記録用、仕様 §5.1）",
  )

  # commit サブコマンド（仕様 §5.2）
  cs = sub.add_parser(
    "commit",
    help="git commit の事前検査を行う",
    parents=[common_parser],
  )
  cs.add_argument(
    "--rationale",
    required=True,
    help="このコミットを行う理由（必須、利用者承認の出典を含めることを推奨、仕様 §5.2）",
  )

  # push サブコマンド（仕様 §5.3）
  ps = sub.add_parser(
    "push",
    help="git push の事前検査を行う",
    parents=[common_parser],
  )
  ps.add_argument(
    "--rationale",
    required=True,
    help="この push を行う理由（必須、利用者承認の出典を含めることを推奨、仕様 §5.3）",
  )

  ap = sub.add_parser(
    "autonomous-plan",
    help="自律・並列モード実行計画の事前検査を行う",
    parents=[common_parser],
  )
  ap.add_argument("plan_path", help="検査対象の自律・並列モード実行計画 YAML")

  apt = sub.add_parser(
    "autonomous-plan-template",
    help="自律・並列モード実行計画のテンプレートを書き出す",
    parents=[common_parser],
  )
  apt.add_argument("--run-id", required=True, help="実行計画の run_id")
  apt.add_argument("--out", required=True, help="テンプレート YAML の出力先")

  apr = sub.add_parser(
    "autonomous-plan-record-integration",
    help="自律・並列モード台帳へ統合結果を追記する",
    parents=[common_parser],
  )
  apr.add_argument("--ledger", required=True, help="更新対象の履歴台帳 YAML")
  apr.add_argument("--status", required=True, help="統合結果 completed / blocked / rejected")
  apr.add_argument("--tests", required=True, help="実行したテストまたは未実行理由")
  apr.add_argument("--decision", required=True, help="統合判断の要約")

  ac = sub.add_parser(
    "audit-commit",
    help="指定 commit の post-write-verification 漏れを監査する",
    parents=[common_parser],
  )
  ac.add_argument("commitish", help="監査対象 commit（例：HEAD）")

  sub.add_parser(
    "next",
    help="現在の workflow_state から次に許可される作業を返す",
    parents=[common_parser],
  )

  rs = sub.add_parser(
    "reopen-start",
    help="reopen classification から in-progress ファイルを生成する",
    parents=[common_parser],
  )
  rs.add_argument("--classification", required=True, help="手戻り種別（例：D-1）")
  rs.add_argument("--feature", required=True, help="対象 feature 名")
  rs.add_argument("--basis", required=True, help="種別判定根拠ファイル")
  rs.add_argument("--date", required=True, help="in-progress ファイル名に使う日付（YYYY-MM-DD）")
  rs.add_argument("--trigger", required=True, help="reopen 起動理由")

  args = parser.parse_args()

  if args.subcommand == "spec-set":
    sys.exit(cmd_spec_set(args))
  elif args.subcommand == "commit":
    sys.exit(cmd_commit(args))
  elif args.subcommand == "push":
    sys.exit(cmd_push(args))
  elif args.subcommand == "autonomous-plan":
    sys.exit(cmd_autonomous_plan(args))
  elif args.subcommand == "autonomous-plan-template":
    sys.exit(cmd_autonomous_plan_template(args))
  elif args.subcommand == "autonomous-plan-record-integration":
    sys.exit(cmd_autonomous_plan_record_integration(args))
  elif args.subcommand == "audit-commit":
    sys.exit(cmd_audit_commit(args))
  elif args.subcommand == "next":
    sys.exit(cmd_next(args))
  elif args.subcommand == "reopen-start":
    sys.exit(cmd_reopen_start(args))
  else:
    parser.print_help(sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
  main()

```

## FILE: tools/api_providers/run_review.py

```text
"""tools/api_providers/run_review.py

複数 role を同じ review-run ディレクトリへ集約して実行する薄い orchestrator。
raw / parsed / rounds / summary の生成は run_role.py の成果物関数を再利用する。
"""
import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import yaml  # noqa: E402

from tools.api_providers.config_loader import (  # noqa: E402
  load_config,
  resolve_connection_settings,
  resolve_role,
  resolve_variant,
)
from tools.api_providers.providers import get_provider  # noqa: E402
from tools.api_providers.response_formatter import (  # noqa: E402
  format_response,
  parse_response_text,
)
from tools.api_providers.run_role import (  # noqa: E402
  build_prompt,
  update_review_run_artifacts,
)

ROLES = ["primary", "adversarial", "judgment"]
NORMALIZED_SEVERITY = {"CRITICAL", "ERROR", "WARN", "INFO"}


def _load_yaml_dict(path: Path) -> Dict[str, Any]:
  if not path.exists():
    return {}
  data = yaml.safe_load(path.read_text(encoding="utf-8"))
  return data if isinstance(data, dict) else {}


def _dump_yaml(path: Path, data: Dict[str, Any]) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _call_provider(provider, prompt: str) -> Tuple[str, int, float]:
  start = time.monotonic()
  response_text = provider.send_request(prompt)
  return response_text, 1, time.monotonic() - start


def _normalize_severity(value: Any) -> str:
  severity = str(value or "INFO").upper()
  return severity if severity in NORMALIZED_SEVERITY else "INFO"


def _load_parsed_findings(review_run_dir: Path, parsed_path: Optional[str]) -> List[Dict[str, Any]]:
  if not parsed_path:
    return []
  parsed_file = review_run_dir / parsed_path
  data = _load_yaml_dict(parsed_file)
  findings = data.get("findings")
  return findings if isinstance(findings, list) else []


def initialize_triage_draft(review_run_dir: str) -> None:
  """parsed findings から human_required の triage 下書きを生成する。"""
  run_dir = Path(review_run_dir)
  rounds = _load_yaml_dict(run_dir / "rounds.yaml")
  model_results = rounds.get("model_results")
  if not isinstance(model_results, list):
    model_results = []

  now = datetime.now(timezone.utc).isoformat()
  items: List[Dict[str, Any]] = []
  for model_result in model_results:
    if not isinstance(model_result, dict):
      continue
    if model_result.get("parse_status") != "parsed":
      continue
    findings = _load_parsed_findings(run_dir, model_result.get("parsed_path"))
    for index, finding in enumerate(findings, start=1):
      if not isinstance(finding, dict):
        continue
      severity_original = finding.get("severity", "INFO")
      items.append({
        "finding_id": (
          f"{run_dir.name}-{model_result.get('model_id')}-"
          f"{model_result.get('role')}-{index:03d}"
        ),
        "run_id": run_dir.name,
        "source_model": model_result.get("model_id"),
        "source_round": rounds.get("round_id"),
        "source_raw_path": model_result.get("raw_path"),
        "source_parsed_path": model_result.get("parsed_path"),
        "severity_original": severity_original,
        "severity_normalized": _normalize_severity(severity_original),
        "target_location": finding.get("target_location"),
        "plain_language_summary": finding.get("description"),
        "final_label": None,
        "decision_status": "human_required",
        "decision_actor": None,
        "decision_actor_type": "human",
        "decision_at": None,
        "decision_reason": finding.get("rationale"),
        "applied_files": [],
        "superseded_by": None,
      })

  _dump_yaml(
    run_dir / "triage.yaml",
    {
      "run_id": run_dir.name,
      "triage_status": "draft",
      "generated_at": now,
      "decision_actor": None,
      "decision_actor_type": "human",
      "items": items,
    },
  )


def write_review_summary_markdown(review_run_dir: str) -> str:
  """model-result-summary.yaml からユーザ提示用 Markdown を生成する。"""
  run_dir = Path(review_run_dir)
  summary = _load_yaml_dict(run_dir / "model-result-summary.yaml")
  models = summary.get("models")
  if not isinstance(models, list):
    models = []

  lines = [
    f"# Review run summary: {run_dir.name}",
    "",
    "| model_id | parse_status | triage_status | findings | severity | raw |",
    "| --- | --- | --- | ---: | --- | --- |",
  ]
  for item in models:
    if not isinstance(item, dict):
      continue
    severity_counts = item.get("findings_count_by_severity") or {}
    severity_text = ", ".join(
      f"{key}:{value}" for key, value in sorted(severity_counts.items())
    )
    lines.append(
      "| {model_id} | {parse_status} | {triage_status} | {findings_count} | {severity} | {raw_path} |".format(
        model_id=item.get("model_id"),
        parse_status=item.get("parse_status"),
        triage_status=item.get("triage_status"),
        findings_count=item.get("findings_count", 0),
        severity=severity_text or "-",
        raw_path=item.get("raw_path"),
      )
    )
  lines.extend([
    "",
    "## Next steps",
    "",
    "1. Read raw responses for any parse_failed or triage_pending model.",
    "2. Move finding-level judgments into triage.yaml.",
    "3. Resolve human_required items before treating the run as complete.",
  ])
  content = "\n".join(lines) + "\n"
  (run_dir / "review_summary.md").write_text(content, encoding="utf-8")
  return content


def _parse_argv(argv: Optional[List[str]]) -> argparse.Namespace:
  parser = argparse.ArgumentParser(
    description="3 role API review を同じ review-run に集約して実行する。",
  )
  parser.add_argument("--variant", default=None, help="variant 名。未指定なら default")
  parser.add_argument("--target", required=True, help="対象文書ファイルパス")
  parser.add_argument("--phase", required=True, help="段名")
  parser.add_argument("--criteria", required=True, help="観点識別子")
  parser.add_argument("--review-run-dir", required=True, help="review-run 成果物ディレクトリ")
  parser.add_argument("--round-id", default="round-1", help="round ID")
  parser.add_argument("--config", default="config/api-settings.yaml", help="API 設定ファイル")
  parser.add_argument(
    "--prior-finding",
    action="append",
    default=[],
    help="前段役の所見ファイルパス（複数指定可）",
  )
  return parser.parse_args(argv)


def _run_one_role(args, config: Dict[str, Any], role: str) -> int:
  """1 role を実行して review-run 成果物へ反映する。"""
  variant_name = None if args.variant == "default" else args.variant
  variant_config = resolve_variant(config, variant_name)
  role_config = resolve_role(variant_config, role)
  connection_defaults = config.get("connection", {})
  connection_settings = resolve_connection_settings(role_config, connection_defaults)

  provider_name = role_config["provider"]
  model = role_config["model"]
  provider_cls = get_provider(provider_name)
  provider = provider_cls(
    model=model,
    timeout_seconds=connection_settings.get("timeout_seconds", 60),
    max_retries=connection_settings.get("max_retries", 1),
  )

  prompt = build_prompt(
    args.target,
    args.phase,
    args.criteria,
    args.prior_finding,
    provider_name=provider_name,
    model=model,
  )
  response_text, attempts, duration_seconds = _call_provider(provider, prompt)
  try:
    findings = parse_response_text(response_text)
  except Exception:
    update_review_run_artifacts(
      args.review_run_dir,
      round_id=args.round_id,
      target_path=args.target,
      phase=args.phase,
      criteria=args.criteria,
      role=role,
      provider=provider_name,
      model=model,
      prompt=prompt,
      response_text=response_text,
      attempts=attempts,
      duration_seconds=duration_seconds,
      parse_status="parse_failed",
      findings=None,
      formatted_output=None,
    )
    return 1

  output = format_response(
    role=role,
    provider=provider_name,
    model=model,
    attempts=attempts,
    duration_seconds=round(duration_seconds, 3),
    findings=findings,
  )
  update_review_run_artifacts(
    args.review_run_dir,
    round_id=args.round_id,
    target_path=args.target,
    phase=args.phase,
    criteria=args.criteria,
    role=role,
    provider=provider_name,
    model=model,
    prompt=prompt,
    response_text=response_text,
    attempts=attempts,
    duration_seconds=duration_seconds,
    parse_status="parsed",
    findings=findings,
    formatted_output=output,
  )
  return 0


def main(argv: Optional[List[str]] = None) -> int:
  args = _parse_argv(argv)
  exit_code = 0
  try:
    config = load_config(args.config)
    for role in ROLES:
      role_exit_code = _run_one_role(args, config, role)
      if role_exit_code != 0:
        exit_code = 1
    initialize_triage_draft(args.review_run_dir)
    summary_markdown = write_review_summary_markdown(args.review_run_dir)
    sys.stdout.write(summary_markdown)
    return exit_code
  except Exception as exc:
    sys.stderr.write(f"エラー：{type(exc).__name__}: {exc}\n")
    return 1


if __name__ == "__main__":
  sys.exit(main())

```

## FILE: tools/api_providers/run_role.py

```text
"""tools/api_providers/run_role.py

API 経路で 1 役を 1 回実行し、結果を標準出力に YAML で返す。
任意指定の出力先がある場合は raw / parsed / review-run 成果物も保存する。
計画書 §5.9.7.1（入出力契約）と §5.23.12.3（プロンプト雛形はフェーズ 4 で整備）を参照。
"""
import argparse
import hashlib
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 直接実行（python3 tools/api_providers/run_role.py）にも import 経由にも対応する。
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import yaml  # noqa: E402

from tools.api_providers.config_loader import (  # noqa: E402
  load_config,
  resolve_connection_settings,
  resolve_role,
  resolve_variant,
)
from tools.api_providers.providers import get_provider  # noqa: E402
from tools.api_providers.response_formatter import (  # noqa: E402
  format_response,
  parse_response_text,
)


_PROMPT_TEMPLATE_DIR = Path(__file__).resolve().parent / "prompt_templates"
_PROVIDER_PROMPT_TEMPLATES = {
  "anthropic-api": "anthropic_review.md",
  "openai-api": "openai_review.md",
  "gemini-api": "gemini_review.md",
}


def _render_prompt_template(template: str, values: Dict[str, str]) -> str:
  """元テンプレート上の placeholder だけを 1 回置換する。"""
  pattern = re.compile(r"{{\s*([A-Za-z_][A-Za-z0-9_]*)\s*}}")

  def replace(match: re.Match) -> str:
    key = match.group(1)
    return values.get(key, match.group(0))

  return pattern.sub(replace, template)


def _select_prompt_template(provider_name: Optional[str]) -> Tuple[str, str]:
  """provider に応じたプロンプトテンプレート ID と本文を返す。"""
  template_file = _PROVIDER_PROMPT_TEMPLATES.get(
    provider_name or "",
    "default_review.md",
  )
  template_path = _PROMPT_TEMPLATE_DIR / template_file
  if not template_path.exists():
    template_file = "default_review.md"
    template_path = _PROMPT_TEMPLATE_DIR / template_file
  return template_file.removesuffix(".md"), template_path.read_text(encoding="utf-8")


def build_prompt(
  target_path: str,
  phase: str,
  criteria: str,
  prior_finding_paths: List[str],
  provider_name: Optional[str] = None,
  model: Optional[str] = None,
) -> str:
  """対象ファイル内容・段名・観点・前段所見からプロンプト文字列を組み立てる。

  provider ごとの差異を吸収するため、専用テンプレートがあればそれを使う。
  """
  target_content = Path(target_path).read_text(encoding="utf-8")
  prior_parts = []
  for i, prior_path in enumerate(prior_finding_paths, start=1):
    prior_content = Path(prior_path).read_text(encoding="utf-8")
    prior_parts.append(f"# 前段所見 {i}：\n{prior_content}")

  prompt_id, template = _select_prompt_template(provider_name)
  return _render_prompt_template(
    template,
    {
      "prompt_id": prompt_id,
      "provider_name": provider_name or "unknown-provider",
      "model": model or "unknown-model",
      "phase": phase,
      "criteria": criteria,
      "target_path": target_path,
      "target_content": target_content,
      "prior_findings": "\n\n".join(prior_parts) if prior_parts else "なし",
    },
  )


def _call_provider(provider, prompt: str) -> Tuple[str, int, float]:
  """プロバイダーを呼び出し、レスポンス文字列・attempts・所要時間を返す。

  send_request 内部のリトライは内側で処理されるため、本層では attempts=1 と記録する。
  詳細な attempts 計測はサブサイクル 4 完成後の改良対象。
  """
  start = time.monotonic()
  response_text = provider.send_request(prompt)
  duration = time.monotonic() - start
  return response_text, 1, duration


def _sha256_text(value: str) -> str:
  """文字列の sha256 を返す。"""
  return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
  """ファイル内容の sha256 を返す。"""
  return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_text(path: Path, content: str) -> None:
  """親ディレクトリを作って UTF-8 テキストを書き込む。"""
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(content, encoding="utf-8")


def _load_yaml_dict(path: Path) -> Dict[str, Any]:
  """YAML dict を読み込む。存在しない場合は空 dict。"""
  if not path.exists():
    return {}
  data = yaml.safe_load(path.read_text(encoding="utf-8"))
  return data if isinstance(data, dict) else {}


def _dump_yaml(path: Path, data: Dict[str, Any]) -> None:
  """YAML dict を UTF-8 で書き込む。"""
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _safe_artifact_stem(model: str) -> str:
  """モデル ID を artifact ファイル名に使える最小表記へ変換する。"""
  safe_chars = []
  for char in model:
    if char.isalnum() or char in (".", "-", "_"):
      safe_chars.append(char)
    else:
      safe_chars.append("-")
  return "".join(safe_chars).strip("-") or "model"


def _write_raw_response(raw_out: Optional[str], response_text: str) -> Optional[str]:
  """明示 raw-out があれば provider 生応答を保存し sha256 を返す。"""
  if not raw_out:
    return None
  path = Path(raw_out)
  _write_text(path, response_text)
  return _sha256_file(path)


def _write_parsed_response(parsed_out: Optional[str], formatted_output: str) -> Optional[str]:
  """明示 parsed-out があれば整形済み YAML を保存し sha256 を返す。"""
  if not parsed_out:
    return None
  path = Path(parsed_out)
  _write_text(path, formatted_output)
  return _sha256_file(path)


def _relative_to_run(run_dir: Path, path: Path) -> str:
  """review-run ディレクトリからの相対パスを返す。"""
  try:
    return str(path.relative_to(run_dir))
  except ValueError:
    return str(path)


def _severity_counts(findings: Optional[List[Dict[str, Any]]]) -> Dict[str, int]:
  """所見重大度ごとの件数を返す。"""
  counts: Dict[str, int] = {}
  for finding in findings or []:
    if not isinstance(finding, dict):
      continue
    severity = finding.get("severity") or "UNKNOWN"
    counts[str(severity)] = counts.get(str(severity), 0) + 1
  return counts


def _upsert_by_keys(items: List[Dict[str, Any]], new_item: Dict[str, Any], keys: List[str]) -> None:
  """keys が一致する既存 dict を置き換え、なければ追加する。"""
  for index, item in enumerate(items):
    if all(item.get(key) == new_item.get(key) for key in keys):
      items[index] = new_item
      return
  items.append(new_item)


def update_review_run_artifacts(
  review_run_dir: str,
  *,
  round_id: str,
  target_path: str,
  phase: str,
  criteria: str,
  role: str,
  provider: str,
  model: str,
  prompt: str,
  response_text: str,
  attempts: int,
  duration_seconds: float,
  parse_status: str,
  findings: Optional[List[Dict[str, Any]]],
  formatted_output: Optional[str],
) -> None:
  """1 回の API 応答を review-run 成果物へ反映する。"""
  run_dir = Path(review_run_dir)
  raw_dir = run_dir / "raw"
  parsed_dir = run_dir / "parsed"
  model_stem = _safe_artifact_stem(model)
  raw_path = raw_dir / f"{model_stem}.{round_id}.txt"
  parsed_path = parsed_dir / f"{model_stem}.{round_id}.yaml"

  _write_text(raw_path, response_text)
  raw_sha256 = _sha256_file(raw_path)
  parsed_sha256 = None
  if formatted_output is not None:
    _write_text(parsed_path, formatted_output)
    parsed_sha256 = _sha256_file(parsed_path)

  target_file = Path(target_path)
  target_sha256 = _sha256_file(target_file)
  now = datetime.now(timezone.utc).isoformat()

  _dump_yaml(
    run_dir / "target-manifest.yaml",
    {
      "run_id": run_dir.name,
      "target_files": [
        {
          "path": target_path,
          "sha256": target_sha256,
        },
      ],
    },
  )

  rounds_path = run_dir / "rounds.yaml"
  rounds = _load_yaml_dict(rounds_path)
  model_results = rounds.get("model_results")
  if not isinstance(model_results, list):
    model_results = []

  model_result = {
    "model_id": model,
    "provider": provider,
    "role": role,
    "treatment": role,
    "invocation_path": "api",
    "raw_path": _relative_to_run(run_dir, raw_path),
    "raw_sha256": raw_sha256,
    "parsed_path": _relative_to_run(run_dir, parsed_path) if formatted_output is not None else None,
    "parsed_sha256": parsed_sha256,
    "parse_status": parse_status,
    "formatted_by": "parser",
    "formatted_by_actor_type": "orchestrator",
    "formatted_by_actor": "run_role.py",
    "formatted_at": now,
    "follow_up_action": "triage" if parse_status == "parsed" else "format_pending",
    "attempts": attempts,
    "duration_seconds": round(duration_seconds, 3),
  }
  _upsert_by_keys(model_results, model_result, ["model_id", "role"])

  rounds.update({
    "round_id": round_id,
    "purpose": phase,
    "invocation_timestamp": now,
    "target_files": [
      {
        "path": target_path,
        "sha256": target_sha256,
      },
    ],
    "criteria": criteria,
    "prompt_sha256": _sha256_text(prompt),
    "model_results": model_results,
  })
  _dump_yaml(rounds_path, rounds)

  summary_path = run_dir / "model-result-summary.yaml"
  summary = _load_yaml_dict(summary_path)
  summary_models = summary.get("models")
  if not isinstance(summary_models, list):
    summary_models = []
  findings_count = len(findings or [])
  summary_model = {
    "model_id": model,
    "raw_path": _relative_to_run(run_dir, raw_path),
    "parse_status": parse_status,
    "triage_status": "no_findings" if parse_status == "parsed" and findings_count == 0 else "triage_pending",
    "findings_count": findings_count,
    "findings_count_by_severity": _severity_counts(findings),
    "must_fix_count": 0,
    "should_fix_count": 0,
    "leave_as_is_count": 0,
    "human_required_count": 0,
  }
  _upsert_by_keys(summary_models, summary_model, ["model_id"])
  summary.update({
    "run_id": run_dir.name,
    "models": summary_models,
  })
  _dump_yaml(summary_path, summary)


def _parse_argv(argv: Optional[List[str]]) -> argparse.Namespace:
  """引数解析。計画書 §5.9.7.1 の長オプション 6 種＋ --config に対応。"""
  parser = argparse.ArgumentParser(
    description="API 経路で 1 役を 1 回実行し、結果を標準出力に YAML で返す。",
  )
  parser.add_argument(
    "--role",
    required=True,
    choices=["primary", "adversarial", "judgment"],
    help="役名（必須）",
  )
  parser.add_argument(
    "--variant",
    default=None,
    help="variant 名。未指定なら default を使う",
  )
  parser.add_argument(
    "--target",
    required=True,
    help="対象文書ファイルパス（必須）",
  )
  parser.add_argument(
    "--phase",
    required=True,
    help="段名（例：requirements_triad_review、必須）",
  )
  parser.add_argument(
    "--criteria",
    required=True,
    help="観点識別子（例：観点-1、必須）",
  )
  parser.add_argument(
    "--prior-finding",
    action="append",
    default=[],
    help="前段役の所見ファイルパス（複数指定可）",
  )
  parser.add_argument(
    "--config",
    default="config/api-settings.yaml",
    help="API 設定ファイルパス（既定 config/api-settings.yaml）",
  )
  parser.add_argument(
    "--raw-out",
    default=None,
    help="provider 生応答の保存先。parse 成否に関係なく保存する",
  )
  parser.add_argument(
    "--parsed-out",
    default=None,
    help="整形済み YAML の保存先。parse 成功時のみ保存する",
  )
  parser.add_argument(
    "--review-run-dir",
    default=None,
    help="review-run 成果物ディレクトリ。raw/parsed/rounds/summary を更新する",
  )
  parser.add_argument(
    "--round-id",
    default="round-1",
    help="review-run に記録する round_id",
  )
  return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
  """メイン処理。エラー時は標準エラーに理由を書いて非ゼロを返す。"""
  args = _parse_argv(argv)
  try:
    config = load_config(args.config)
    variant_config = resolve_variant(config, args.variant)
    role_config = resolve_role(variant_config, args.role)
    connection_defaults = config.get("connection", {})
    connection_settings = resolve_connection_settings(role_config, connection_defaults)

    provider_name = role_config["provider"]
    model = role_config["model"]
    provider_cls = get_provider(provider_name)
    provider = provider_cls(
      model=model,
      timeout_seconds=connection_settings.get("timeout_seconds", 60),
      max_retries=connection_settings.get("max_retries", 1),
    )

    prompt = build_prompt(
      args.target,
      args.phase,
      args.criteria,
      args.prior_finding,
      provider_name=provider_name,
      model=model,
    )
    response_text, attempts, duration_seconds = _call_provider(provider, prompt)
    _write_raw_response(args.raw_out, response_text)
    try:
      findings = parse_response_text(response_text)
    except Exception:
      if args.review_run_dir:
        update_review_run_artifacts(
          args.review_run_dir,
          round_id=args.round_id,
          target_path=args.target,
          phase=args.phase,
          criteria=args.criteria,
          role=args.role,
          provider=provider_name,
          model=model,
          prompt=prompt,
          response_text=response_text,
          attempts=attempts,
          duration_seconds=duration_seconds,
          parse_status="parse_failed",
          findings=None,
          formatted_output=None,
        )
      raise
    output = format_response(
      role=args.role,
      provider=provider_name,
      model=model,
      attempts=attempts,
      duration_seconds=round(duration_seconds, 3),
      findings=findings,
    )
    _write_parsed_response(args.parsed_out, output)
    if args.review_run_dir:
      update_review_run_artifacts(
        args.review_run_dir,
        round_id=args.round_id,
        target_path=args.target,
        phase=args.phase,
        criteria=args.criteria,
        role=args.role,
        provider=provider_name,
        model=model,
        prompt=prompt,
        response_text=response_text,
        attempts=attempts,
        duration_seconds=duration_seconds,
        parse_status="parsed",
        findings=findings,
        formatted_output=output,
      )
    sys.stdout.write(output)
    return 0
  except Exception as exc:
    sys.stderr.write(f"エラー：{type(exc).__name__}: {exc}\n")
    return 1


if __name__ == "__main__":
  sys.exit(main())

```

## FILE: tools/api_providers/review_triage.py

```text
"""tools/api_providers/review_triage.py

review-run の triage 下書きを一覧化し、人判断の反映と manifest 雛形生成を行う。
"""
import argparse
import hashlib
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import yaml  # noqa: E402

FINAL_LABELS = ("must-fix", "should-fix", "leave-as-is")
IMPORTANT_SEVERITIES = ("CRITICAL", "ERROR")
TRIAGE_DECIDE_APPROVAL_ACTIONS = ("review_triage_decide", "review_run_triage")
MANIFEST_APPROVAL_ACTIONS = ("review_run_manifest", "review_run_triage")
APPLY_FIXES_APPROVAL_ACTIONS = ("review_run_apply_fixes", "review_run_triage")
FIX_LABELS = ("must-fix", "should-fix")
POST_WRITE_VERIFICATION_DIR_PREFIXES = (
  "docs/plan/",
  "docs/disciplines/",
  "docs/operations/",
  "docs/notes/",
  "docs/experiments/",
)
POST_WRITE_VERIFICATION_MD_DIR_PREFIXES = (
  ".reviewcompass/specs/",
  "intent/",
  "templates/",
)
POST_WRITE_VERIFICATION_FILE_PATHS = (
  "AGENTS.md",
  "TODO_NEXT_SESSION.md",
)
POST_WRITE_VERIFICATION_FILE_PREFIXES = (
  "runtime/prompts/",
  "tools/api_providers/prompt_templates/",
)


def _load_yaml_dict(path: Path) -> Dict[str, Any]:
  data = yaml.safe_load(path.read_text(encoding="utf-8"))
  return data if isinstance(data, dict) else {}


def _dump_yaml(path: Path, data: Dict[str, Any]) -> None:
  path.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _sha256_file(path: Path) -> str:
  return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse_git_status_path(line: str) -> Optional[str]:
  """git status --short の行から path を取り出す。"""
  if len(line) < 4:
    return None
  path = line[3:]
  if " -> " in path:
    path = path.split(" -> ", 1)[1]
  return path.strip()


def _is_post_write_target(path: str) -> bool:
  """post-write-verification 対象の md 文書パスかを返す。"""
  if path.startswith("docs/archive/"):
    return False
  if path in POST_WRITE_VERIFICATION_FILE_PATHS:
    return True
  if any(path.startswith(prefix) for prefix in POST_WRITE_VERIFICATION_DIR_PREFIXES):
    return True
  if not path.endswith(".md"):
    return False
  if any(path.startswith(prefix) for prefix in POST_WRITE_VERIFICATION_FILE_PREFIXES):
    return True
  if any(path.startswith(prefix) for prefix in POST_WRITE_VERIFICATION_MD_DIR_PREFIXES):
    return True
  if path.startswith("docs/reviews/"):
    name = Path(path).name
    return (
      name.startswith("reopen-classification-")
      or "-audit-" in name
    ) and name.endswith(".md")
  return False


def _current_git_post_write_targets(cwd: Path) -> List[str]:
  """現在の git 変更から post-write 対象を返す。git 外では空リスト。"""
  try:
    result = subprocess.run(
      ["git", "status", "--short", "--untracked-files=all"],
      cwd=str(cwd),
      capture_output=True,
      text=True,
      timeout=10,
      check=False,
    )
  except (OSError, subprocess.SubprocessError):
    return []
  if result.returncode != 0:
    return []
  targets = []
  for line in result.stdout.splitlines():
    path = _parse_git_status_path(line)
    if path and _is_post_write_target(path):
      targets.append(path)
  return sorted(set(targets))


def _find_git_root(start: Path) -> Path:
  """start から上位へ .git を探し、見つからなければ現在ディレクトリを返す。"""
  current = start.resolve()
  if current.is_file():
    current = current.parent
  for candidate in [current] + list(current.parents):
    if (candidate / ".git").exists():
      return candidate
  return Path.cwd()


def _resolve_path(path: str, base_dir: Optional[Path] = None) -> Path:
  candidate = Path(path)
  if candidate.is_absolute():
    return candidate
  return (base_dir or Path.cwd()) / candidate


def _recommendation_for(item: Dict[str, Any]) -> Dict[str, str]:
  severity = str(item.get("severity_normalized") or item.get("severity_original") or "INFO").upper()
  if severity in ("CRITICAL", "ERROR"):
    return {
      "label": "must-fix",
      "reason": "仕様・契約・比較可能性に影響する可能性があるため、人判断の優先度が高い。",
    }
  if severity == "WARN":
    return {
      "label": "should-fix",
      "reason": "後続の読みやすさや保守性に影響する可能性があるため、可能なら反映する。",
    }
  return {
    "label": "leave-as-is",
    "reason": "情報提供または軽微な表現指摘として扱い、必要時だけ反映する。",
  }


def _severity_for(item: Dict[str, Any]) -> str:
  return str(item.get("severity_normalized") or item.get("severity_original") or "INFO").upper()


def _is_important_item(item: Dict[str, Any], final_label: Optional[str] = None) -> bool:
  """重要件として人承認を要求する finding かを返す。"""
  label = final_label if final_label is not None else item.get("final_label")
  return _severity_for(item) in IMPORTANT_SEVERITIES or label == "must-fix"


def _load_approval_record(path: Optional[str]) -> Dict[str, Any]:
  if not path:
    return {}
  approval = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
  return approval if isinstance(approval, dict) else {}


def _resolve_record_path(path_value: str, run_dir: Path, base_dir: Path) -> Path:
  path = Path(path_value)
  if path.is_absolute():
    return path
  base_candidate = base_dir / path
  if base_candidate.exists():
    return base_candidate
  return run_dir / path


def _proxy_decision_errors(
  approval: Dict[str, Any],
  run_dir: Path,
  approval_path: Optional[Path],
  required_finding_ids: List[str],
  final_labels: Optional[Dict[str, str]],
) -> List[str]:
  errors = []
  proxy_model_id = approval.get("proxy_model_id")
  if not isinstance(proxy_model_id, str) or not proxy_model_id.strip():
    errors.append("proxy_model_id is required")

  proxy_decisions = approval.get("proxy_decisions")
  if not isinstance(proxy_decisions, dict):
    return errors + ["proxy_decisions must be a mapping"]

  base_dir = approval_path.parent if approval_path else run_dir
  for finding_id in sorted(set(required_finding_ids)):
    decision_ref = proxy_decisions.get(finding_id)
    if not isinstance(decision_ref, str) or not decision_ref:
      errors.append(f"proxy_decisions missing: {finding_id}")
      continue

    decision_path = _resolve_record_path(decision_ref, run_dir, base_dir)
    if not decision_path.is_file():
      errors.append(f"proxy decision file missing: {decision_ref}")
      continue

    decision = _load_yaml_dict(decision_path)
    if decision.get("approved_by") != "proxy_model":
      errors.append(f"{finding_id}: decision approved_by must be proxy_model")
    if decision.get("finding_id") != finding_id:
      errors.append(f"{finding_id}: decision finding_id mismatch")
    if decision.get("proxy_model_id") != proxy_model_id:
      errors.append(f"{finding_id}: proxy_model_id mismatch")

    for key in (
      "decision_prompt_path",
      "selected_option",
      "final_label",
      "rationale",
      "raw_response_path",
    ):
      value = decision.get(key)
      if not isinstance(value, str) or not value.strip():
        errors.append(f"{finding_id}: {key} is required")

    candidate_options = decision.get("candidate_options")
    if not isinstance(candidate_options, list) or not candidate_options:
      errors.append(f"{finding_id}: candidate_options is required")

    source_raw_paths = decision.get("source_raw_paths")
    if not isinstance(source_raw_paths, list) or not source_raw_paths:
      errors.append(f"{finding_id}: source_raw_paths is required")
    elif not all(isinstance(item, str) and item.strip() for item in source_raw_paths):
      errors.append(f"{finding_id}: source_raw_paths must contain paths")

    rejected_options = decision.get("rejected_options")
    if not isinstance(rejected_options, dict) or not rejected_options:
      errors.append(f"{finding_id}: rejected_options is required")

    expected_label = final_labels.get(finding_id) if final_labels else None
    if expected_label and decision.get("final_label") != expected_label:
      errors.append(f"{finding_id}: final_label mismatch")

    raw_response_path = decision.get("raw_response_path")
    if isinstance(raw_response_path, str) and raw_response_path.strip():
      raw_path = _resolve_record_path(raw_response_path, run_dir, decision_path.parent)
      if not raw_path.is_file():
        errors.append(f"{finding_id}: raw_response_path missing")
      elif raw_path.stat().st_size == 0:
        errors.append(f"{finding_id}: raw_response_path empty")

    decision_prompt_path = decision.get("decision_prompt_path")
    if isinstance(decision_prompt_path, str) and decision_prompt_path.strip():
      prompt_path = _resolve_record_path(decision_prompt_path, run_dir, decision_path.parent)
      if not prompt_path.is_file():
        errors.append(f"{finding_id}: decision_prompt_path missing")

    if isinstance(source_raw_paths, list):
      for source_raw_path in source_raw_paths:
        if not isinstance(source_raw_path, str) or not source_raw_path.strip():
          continue
        source_path = _resolve_record_path(source_raw_path, run_dir, decision_path.parent)
        if not source_path.is_file():
          errors.append(f"{finding_id}: source_raw_paths missing: {source_raw_path}")
  return errors


def _approval_errors(
  approval: Dict[str, Any],
  run_dir: Path,
  approval_path: Optional[Path],
  allowed_actions: tuple,
  required_finding_ids: List[str],
  final_labels: Optional[Dict[str, str]] = None,
) -> List[str]:
  errors = []
  if not approval:
    return ["approval record is required"]
  if approval.get("approved_action") not in allowed_actions:
    errors.append("approved_action does not allow this review-run action")
  approved_by = approval.get("approved_by")
  if approved_by not in ("user", "proxy_model"):
    errors.append("approved_by must be user or proxy_model")
  if approval.get("review_run_id") != run_dir.name:
    errors.append("review_run_id does not match")
  if approval.get("summary_presented_to_user") is not True:
    errors.append("summary_presented_to_user must be true")
  if approval.get("triage_presented_to_user") is not True:
    errors.append("triage_presented_to_user must be true")
  if approval.get("consumed") is True:
    errors.append("approval record is already consumed")

  approved_ids = approval.get("approved_finding_ids")
  approved_id_set = set(approved_ids) if isinstance(approved_ids, list) else set()
  missing_ids = sorted(set(required_finding_ids) - approved_id_set)
  if missing_ids:
    errors.append(f"approved_finding_ids missing: {', '.join(missing_ids)}")

  approved_labels = approval.get("approved_final_labels")
  if final_labels and isinstance(approved_labels, dict):
    mismatched = [
      finding_id
      for finding_id, label in final_labels.items()
      if approved_labels.get(finding_id) != label
    ]
    if mismatched:
      errors.append(f"approved_final_labels mismatch: {', '.join(sorted(mismatched))}")
  if approved_by == "proxy_model":
    errors.extend(
      _proxy_decision_errors(
        approval,
        run_dir,
        approval_path,
        required_finding_ids,
        final_labels,
      )
    )
  return errors


def _require_review_run_approval(
  run_dir: Path,
  approval_record_path: Optional[str],
  allowed_actions: tuple,
  required_finding_ids: List[str],
  final_labels: Optional[Dict[str, str]] = None,
) -> None:
  if not required_finding_ids:
    return
  approval = _load_approval_record(approval_record_path)
  approval_path = Path(approval_record_path) if approval_record_path else None
  errors = _approval_errors(
    approval,
    run_dir,
    approval_path,
    allowed_actions,
    required_finding_ids,
    final_labels,
  )
  if errors:
    raise ValueError("approval gate failed: " + "; ".join(errors))


def _triage_path(run_dir: Path) -> Path:
  return run_dir / "triage.yaml"


def _summary_path(run_dir: Path) -> Path:
  return run_dir / "model-result-summary.yaml"


def list_pending(review_run_dir: str) -> str:
  """human_required の triage item を Markdown 表で返す。"""
  run_dir = Path(review_run_dir)
  triage = _load_yaml_dict(_triage_path(run_dir))
  items = triage.get("items")
  if not isinstance(items, list):
    items = []

  lines = [
    f"# Pending triage: {run_dir.name}",
    "",
    "| finding_id | model | severity | summary | recommendation | reason |",
    "| --- | --- | --- | --- | --- | --- |",
  ]
  for item in items:
    if not isinstance(item, dict):
      continue
    if item.get("decision_status") != "human_required":
      continue
    recommendation = _recommendation_for(item)
    lines.append(
      "| {finding_id} | {model} | {severity} | {summary} | {label} | {reason} |".format(
        finding_id=item.get("finding_id"),
        model=item.get("source_model"),
        severity=item.get("severity_normalized") or item.get("severity_original"),
        summary=item.get("plain_language_summary"),
        label=recommendation["label"],
        reason=recommendation["reason"],
      )
    )
  return "\n".join(lines) + "\n"


def _count_summary_for_model(items: List[Dict[str, Any]], model_id: str) -> Dict[str, int]:
  counts = {
    "must_fix_count": 0,
    "should_fix_count": 0,
    "leave_as_is_count": 0,
    "human_required_count": 0,
  }
  for item in items:
    if item.get("source_model") != model_id:
      continue
    if item.get("decision_status") == "human_required":
      counts["human_required_count"] += 1
      continue
    label = item.get("final_label")
    if label == "must-fix":
      counts["must_fix_count"] += 1
    elif label == "should-fix":
      counts["should_fix_count"] += 1
    elif label == "leave-as-is":
      counts["leave_as_is_count"] += 1
  return counts


def refresh_summary_from_triage(review_run_dir: str) -> None:
  """triage の決定状態を model-result-summary.yaml に反映する。"""
  run_dir = Path(review_run_dir)
  triage = _load_yaml_dict(_triage_path(run_dir))
  summary = _load_yaml_dict(_summary_path(run_dir))
  items = triage.get("items")
  models = summary.get("models")
  if not isinstance(items, list):
    items = []
  if not isinstance(models, list):
    models = []

  models_with_items = {
    item.get("source_model")
    for item in items
    if isinstance(item, dict) and item.get("source_model")
  }
  for model in models:
    if not isinstance(model, dict):
      continue
    model_id = model.get("model_id")
    if not model_id or model_id not in models_with_items:
      continue
    counts = _count_summary_for_model(items, model_id)
    model.update(counts)
    if counts["human_required_count"] > 0:
      model["triage_status"] = "triage_pending"
    else:
      model["triage_status"] = "triaged"
  _dump_yaml(_summary_path(run_dir), summary)


def decide_item(
  review_run_dir: str,
  finding_id: str,
  final_label: str,
  decision_reason: str,
  decision_actor: str,
  approval_record_path: Optional[str] = None,
) -> bool:
  """1 finding の人判断を反映する。見つかった場合 True。"""
  run_dir = Path(review_run_dir)
  triage = _load_yaml_dict(_triage_path(run_dir))
  items = triage.get("items")
  if not isinstance(items, list):
    items = []

  found = False
  now = datetime.now(timezone.utc).isoformat()
  for item in items:
    if not isinstance(item, dict):
      continue
    if item.get("finding_id") != finding_id:
      continue
    if _is_important_item(item, final_label):
      _require_review_run_approval(
        run_dir,
        approval_record_path,
        TRIAGE_DECIDE_APPROVAL_ACTIONS,
        [finding_id],
        {finding_id: final_label},
      )
    item["final_label"] = final_label
    item["decision_status"] = "decided"
    item["decision_actor"] = decision_actor
    item["decision_actor_type"] = "human" if decision_actor == "human" else "agent"
    item["decision_at"] = now
    item["decision_reason"] = decision_reason
    found = True
    break

  if not found:
    return False

  unresolved = [
    item for item in items
    if isinstance(item, dict) and item.get("decision_status") == "human_required"
  ]
  triage["triage_status"] = "draft" if unresolved else "decided"
  _dump_yaml(_triage_path(run_dir), triage)
  refresh_summary_from_triage(review_run_dir)
  return True


def _path_string(path: Path) -> str:
  try:
    return str(path.relative_to(Path.cwd()))
  except ValueError:
    return str(path)


def unresolved_human_required_count(review_run_dir: str) -> int:
  """human_required が残る件数を返す。"""
  triage = _load_yaml_dict(_triage_path(Path(review_run_dir)))
  count = 0
  for item in triage.get("items", []):
    if isinstance(item, dict) and item.get("decision_status") == "human_required":
      count += 1
  return count


def _current_target_sha256(
  target_files: List[str],
  fallback: Dict[str, str],
  base_dir: Path,
) -> Dict[str, str]:
  """対象ファイルの現在 sha256 を返す。存在しない場合は fallback を使う。"""
  values: Dict[str, str] = {}
  for target in target_files:
    target_path = _resolve_path(target, base_dir)
    if target_path.is_file():
      values[target] = _sha256_file(target_path)
    elif target in fallback:
      values[target] = fallback[target]
  return values


def _verification_entries(models: List[str], target_files: List[str], target_sha256: Dict[str, str]) -> List[Dict[str, Any]]:
  """required verifier ごとの coverage matrix を作る。"""
  return [
    {
      "verifier": model,
      "target_files": list(target_files),
      "target_sha256": dict(target_sha256),
    }
    for model in models
  ]


def build_manifest_template(review_run_dir: str) -> Dict[str, Any]:
  """post-write-verification manifest 雛形を返す。"""
  run_dir = Path(review_run_dir)
  git_root = _find_git_root(run_dir)
  target_manifest = _load_yaml_dict(run_dir / "target-manifest.yaml")
  rounds = _load_yaml_dict(run_dir / "rounds.yaml")
  triage = _load_yaml_dict(run_dir / "triage.yaml")
  summary_path = run_dir / "model-result-summary.yaml"
  target_files = [
    item.get("path")
    for item in target_manifest.get("target_files", [])
    if isinstance(item, dict) and item.get("path")
  ]
  current_targets = _current_git_post_write_targets(git_root)
  if current_targets:
    target_files = sorted(set(target_files).union(current_targets))
  fallback_sha256 = {
    item.get("path"): item.get("sha256")
    for item in target_manifest.get("target_files", [])
    if isinstance(item, dict) and item.get("path") and item.get("sha256")
  }
  target_sha256 = _current_target_sha256(target_files, fallback_sha256, git_root)
  models = [
    item.get("model_id")
    for item in rounds.get("model_results", [])
    if isinstance(item, dict) and item.get("model_id")
  ]
  unresolved = unresolved_human_required_count(review_run_dir)

  status = "completed" if unresolved == 0 else "pending"
  return {
    "status": status,
    "target_files": target_files,
    "target_sha256": target_sha256,
    "required_verifiers": models,
    "completed_verifiers": models,
    "unresolved_substantive_findings": unresolved,
    "verifications": _verification_entries(models, target_files, target_sha256),
    "review_run": {
      "path": _path_string(run_dir),
      "summary_path": _path_string(summary_path),
    },
    "notes": "Generated template; verify target_files cover current post-write targets before use.",
  }


def assert_manifest_ready(
  review_run_dir: str,
  approval_record_path: Optional[str] = None,
) -> None:
  """manifest 生成可能か確認し、未判断があれば例外にする。"""
  run_dir = Path(review_run_dir)
  unresolved = unresolved_human_required_count(review_run_dir)
  if unresolved > 0:
    raise ValueError(f"human_required remains: {unresolved}")
  triage = _load_yaml_dict(_triage_path(run_dir))
  items = triage.get("items")
  if not isinstance(items, list):
    items = []
  important_ids = [
    item.get("finding_id")
    for item in items
    if isinstance(item, dict)
    and item.get("finding_id")
    and item.get("decision_status") == "decided"
    and _is_important_item(item)
  ]
  _require_review_run_approval(
    run_dir,
    approval_record_path,
    MANIFEST_APPROVAL_ACTIONS,
    sorted(set(important_ids)),
  )


def assert_apply_fixes_ready(
  review_run_dir: str,
  approval_record_path: Optional[str] = None,
) -> None:
  """API review 所見への修正適用を始めてよいか機械判定する。"""
  run_dir = Path(review_run_dir)
  unresolved = unresolved_human_required_count(review_run_dir)
  if unresolved > 0:
    raise ValueError(f"human_required remains: {unresolved}")

  triage = _load_yaml_dict(_triage_path(run_dir))
  items = triage.get("items")
  if not isinstance(items, list):
    items = []
  final_labels = {}
  required_ids = []
  for item in items:
    if not isinstance(item, dict):
      continue
    finding_id = item.get("finding_id")
    final_label = item.get("final_label")
    if (
      finding_id
      and item.get("decision_status") == "decided"
      and final_label in FIX_LABELS
    ):
      required_ids.append(finding_id)
      final_labels[finding_id] = final_label

  _require_review_run_approval(
    run_dir,
    approval_record_path,
    APPLY_FIXES_APPROVAL_ACTIONS,
    sorted(set(required_ids)),
    final_labels,
  )


def write_manifest(
  review_run_dir: str,
  out_path: str,
  approval_record_path: Optional[str] = None,
) -> Path:
  """完了 manifest をファイルへ書き、出力先 path を返す。"""
  assert_manifest_ready(review_run_dir, approval_record_path)
  manifest = build_manifest_template(review_run_dir)
  output = resolve_manifest_output_path(out_path)
  output.parent.mkdir(parents=True, exist_ok=True)
  _dump_yaml(output, manifest)
  return output


def resolve_manifest_output_path(out_path: str) -> Path:
  """manifest 出力先を解決する。auto は当日の次番号を返す。"""
  if out_path != "auto":
    return Path(out_path)
  manifest_dir = Path.cwd() / ".reviewcompass" / "post-write-verification"
  manifest_dir.mkdir(parents=True, exist_ok=True)
  prefix = f"post-write-{date.today().isoformat()}-"
  max_number = 0
  for path in manifest_dir.glob(f"{prefix}*.yaml"):
    suffix = path.stem.removeprefix(prefix)
    try:
      max_number = max(max_number, int(suffix))
    except ValueError:
      continue
  return manifest_dir / f"{prefix}{max_number + 1:03d}.yaml"


def _parse_argv(argv: Optional[List[str]]) -> argparse.Namespace:
  parser = argparse.ArgumentParser(description="review-run triage helper")
  subparsers = parser.add_subparsers(dest="command", required=True)

  list_parser = subparsers.add_parser("list-pending")
  list_parser.add_argument("--review-run-dir", required=True)

  decide_parser = subparsers.add_parser("decide")
  decide_parser.add_argument("--review-run-dir", required=True)
  decide_parser.add_argument("--finding-id", required=True)
  decide_parser.add_argument("--final-label", required=True, choices=FINAL_LABELS)
  decide_parser.add_argument("--decision-reason", required=True)
  decide_parser.add_argument("--decision-actor", required=True)
  decide_parser.add_argument("--approval-record")

  manifest_parser = subparsers.add_parser("manifest-template")
  manifest_parser.add_argument("--review-run-dir", required=True)
  manifest_parser.add_argument("--approval-record")

  write_manifest_parser = subparsers.add_parser("write-manifest")
  write_manifest_parser.add_argument("--review-run-dir", required=True)
  write_manifest_parser.add_argument("--out", required=True)
  write_manifest_parser.add_argument("--approval-record")

  apply_fixes_parser = subparsers.add_parser("assert-apply-fixes-ready")
  apply_fixes_parser.add_argument("--review-run-dir", required=True)
  apply_fixes_parser.add_argument("--approval-record")

  return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
  args = _parse_argv(argv)
  try:
    if args.command == "list-pending":
      sys.stdout.write(list_pending(args.review_run_dir))
      return 0
    if args.command == "decide":
      found = decide_item(
        args.review_run_dir,
        args.finding_id,
        args.final_label,
        args.decision_reason,
        args.decision_actor,
        args.approval_record,
      )
      if not found:
        sys.stderr.write(f"finding_id not found: {args.finding_id}\n")
        return 1
      return 0
    if args.command == "manifest-template":
      assert_manifest_ready(args.review_run_dir, args.approval_record)
      sys.stdout.write(
        yaml.safe_dump(
          build_manifest_template(args.review_run_dir),
          allow_unicode=True,
          sort_keys=False,
        )
      )
      return 0
    if args.command == "write-manifest":
      output = write_manifest(args.review_run_dir, args.out, args.approval_record)
      sys.stdout.write(f"{output}\n")
      return 0
    if args.command == "assert-apply-fixes-ready":
      assert_apply_fixes_ready(args.review_run_dir, args.approval_record)
      sys.stdout.write("apply_fixes_ready: true\n")
      return 0
  except Exception as exc:
    sys.stderr.write(f"エラー：{type(exc).__name__}: {exc}\n")
    return 1
  return 1


if __name__ == "__main__":
  sys.exit(main())

```

## FILE: tests/tools/test_check_workflow_action.py

```text
"""ワークフロー事前検査スクリプト tools/check-workflow-action.py の単体テスト

対象仕様：docs/operations/WORKFLOW_PRECHECK.md
対象範囲：spec-set サブコマンド（範囲案 2 のうち、MVP 第 1 ラウンドで先行実装）

TDD 規律（AGENTS.md 入口規律）に従い、本テストはスクリプト実装前に作成。
実行方法：
  cd /Users/Daily/Development/ReviewCompass
  python3 -m unittest tests.tools.test_check_workflow_action -v
"""

import json
import hashlib
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

from tools.api_providers.review_triage import write_manifest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "check-workflow-action.py"
FIXTURE_BASE = REPO_ROOT / "tests" / "fixtures" / "spec-json-cases"

FEATURE_ORDER = [
  "foundation",
  "runtime",
  "evaluation",
  "analysis",
  "workflow-management",
  "self-improvement",
  "conformance-evaluation",
]


def run_script(args, cwd):
  """check-workflow-action.py をサブプロセスで実行して結果を返す"""
  return subprocess.run(
    ["python3", str(SCRIPT)] + list(args),
    cwd=str(cwd),
    capture_output=True,
    text=True,
    timeout=10,
  )


def _write_spec(cwd, feature, implementation_state):
  """next サブコマンド用の最小 spec.json を作る"""
  spec_dir = Path(cwd) / ".reviewcompass" / "specs" / feature
  spec_dir.mkdir(parents=True, exist_ok=True)
  complete_five_stage = {
    "drafting": True,
    "triad-review": True,
    "review-wave": True,
    "alignment": True,
    "approval": True,
  }
  workflow_state = {
    "intent": {
      "drafting": True,
      "review": True,
      "approval": True,
      "reference": "stages/intent.yaml",
    },
    "feature-partitioning": {
      "candidate-proposal": True,
      "approval": True,
      "reference": "stages/feature-partitioning/2026-05-24-proposal.md",
    },
    "requirements": dict(complete_five_stage),
    "design": dict(complete_five_stage),
    "tasks": dict(complete_five_stage),
    "implementation": dict(implementation_state),
  }
  spec = {
    "feature_name": feature,
    "language": "ja",
    "created_at": "2026-06-02T00:00:00+09:00",
    "updated_at": "2026-06-02T00:00:00+09:00",
    "workflow_state": workflow_state,
    "reopened": {},
    "recheck": {
      "upstream_change_pending": False,
      "impacted_downstream_phases": [],
    },
  }
  (spec_dir / "spec.json").write_text(
    json.dumps(spec, ensure_ascii=False, indent=2),
    encoding="utf-8",
  )


def _write_specs_for_next(cwd, states_by_feature):
  """指定されない feature は implementation 未着手として spec.json を作る"""
  untouched = {
    "drafting": False,
    "triad-review": False,
    "review-wave": False,
    "alignment": False,
    "approval": False,
  }
  for feature in FEATURE_ORDER:
    _write_spec(cwd, feature, states_by_feature.get(feature, untouched))


def _write_post_write_manifest(cwd, manifest_name, content):
  """post-write-verification manifest を作る"""
  manifest_dir = Path(cwd) / ".reviewcompass" / "post-write-verification"
  manifest_dir.mkdir(parents=True, exist_ok=True)
  (manifest_dir / manifest_name).write_text(
    yaml.safe_dump(content, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )


def _sha256_file(path):
  """ファイル内容の sha256 を返す"""
  return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _write_review_run(cwd, run_id, models, omit_summary=False, omit_triage_model=None):
  """post-write review run の最小成果物を作る"""
  run_dir = Path(cwd) / "docs" / "notes" / "review-runs" / run_id
  raw_dir = run_dir / "raw"
  raw_dir.mkdir(parents=True, exist_ok=True)

  target = Path(cwd) / "docs" / "notes" / "review-target.md"
  target.parent.mkdir(parents=True, exist_ok=True)
  if not target.exists():
    target.write_text("レビュー対象\n", encoding="utf-8")

  model_results = []
  triage_items = []
  summary_models = []
  for model in models:
    raw_path = raw_dir / f"{model}.round-1.txt"
    raw_path.write_text(f"{model} raw response\n", encoding="utf-8")
    raw_sha = _sha256_file(raw_path)
    model_results.append({
      "model_id": model,
      "provider": f"{model}-provider",
      "role": model,
      "treatment": model,
      "invocation_path": "api",
      "raw_path": f"raw/{model}.round-1.txt",
      "raw_sha256": raw_sha,
      "parsed_path": None,
      "parsed_sha256": None,
      "parse_status": "parse_failed",
      "follow_up_action": "triage",
    })
    if model != omit_triage_model:
      triage_items.append({
        "finding_id": f"{run_id}-{model}-001",
        "source_model": model,
        "source_round": f"{run_id}-round-1",
        "source_raw_path": f"raw/{model}.round-1.txt",
        "source_parsed_path": None,
        "severity_original": "INFO",
        "severity_normalized": "INFO",
        "final_label": "leave-as-is",
        "decision_status": "decided",
        "target_location": "docs/notes/review-target.md",
        "plain_language_summary": "問題なし。",
        "decision_reason": "テスト用の完了記録。",
        "applied_files": [],
        "superseded_by": None,
      })
    summary_models.append({
      "model_id": model,
      "raw_path": f"raw/{model}.round-1.txt",
      "parse_status": "parse_failed",
      "triage_status": "triaged",
      "findings_count": 1,
      "must_fix_count": 0,
      "should_fix_count": 0,
      "leave_as_is_count": 1,
      "human_required_count": 0,
    })

  (run_dir / "target-manifest.yaml").write_text(
    yaml.safe_dump(
      {
        "run_id": run_id,
        "target_files": [
          {
            "path": "docs/notes/review-target.md",
            "sha256": _sha256_file(target),
          },
        ],
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  (run_dir / "rounds.yaml").write_text(
    yaml.safe_dump(
      {
        "round_id": f"{run_id}-round-1",
        "purpose": "post_write_verification",
        "target_files": [
          {
            "path": "docs/notes/review-target.md",
            "sha256": _sha256_file(target),
          },
        ],
        "model_results": model_results,
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  (run_dir / "triage.yaml").write_text(
    yaml.safe_dump(
      {
        "run_id": run_id,
        "items": triage_items,
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  if not omit_summary:
    (run_dir / "model-result-summary.yaml").write_text(
      yaml.safe_dump(
        {
          "run_id": run_id,
          "models": summary_models,
        },
        allow_unicode=True,
        sort_keys=False,
      ),
      encoding="utf-8",
    )

  return run_dir


def _assert_script_invoked(testcase, result):
  """スクリプトが実際に起動したことを確認する厳密性確保のヘルパー

  Python はスクリプトファイルが存在しないとき exit 2 を返す。これは仕様 §7.1 の
  逸脱判定 exit 2 と一致するため、判定だけでは「スクリプト未実装」と
  「正当な逸脱検出」を区別できない。本ヘルパーは stderr にファイルなし
  エラーが含まれないことを確認することで両者を区別し、実装前の偶然通過を
  防ぐ。実装完了後は無効化されない（実害なく動作し続ける）。
  """
  for marker in ("No such file or directory", "can't open file"):
    testcase.assertNotIn(
      marker, result.stderr,
      f"スクリプトが起動できていない（実装前の状態か）。stderr: {result.stderr}",
    )


def _write_autonomous_parallel_plan(cwd, overrides=None):
  """自律・並列モード実行計画の最小正常形を作る"""
  overrides = overrides or {}
  plan = {
    "mode": "autonomous_parallel",
    "run_id": "ap-001",
    "authorization": {
      "approved_by": "user",
      "approval_record_path": "docs/notes/approval.md",
      "summary_presented_to_user": True,
      "triage_presented_to_user": True,
    },
    "tasks": [
      {
        "task_id": "task-a",
        "source_finding_ids": ["finding-a"],
        "assignee": {
          "kind": "subthread",
          "worktree_policy": "separate_worktree",
        },
        "allowed_paths": ["src/a.py"],
        "forbidden_paths": [".git/"],
        "depends_on": [],
        "expected_tests": ["pytest tests/test_a.py"],
        "stop_conditions": ["important_decision_requires_approval"],
      },
      {
        "task_id": "task-b",
        "source_finding_ids": ["finding-b"],
        "assignee": {
          "kind": "subthread",
          "worktree_policy": "separate_worktree",
        },
        "allowed_paths": ["src/b.py"],
        "forbidden_paths": [".git/"],
        "depends_on": [],
        "expected_tests": ["pytest tests/test_b.py"],
        "stop_conditions": ["important_decision_requires_approval"],
      },
    ],
    "integration_gate": {
      "requires_main_session_review": True,
      "requires_diff_scope_check": True,
      "requires_tests": True,
      "requires_decision_basis_review": True,
    },
    "history": {
      "ledger_path": "docs/logs/autonomous-parallel/ap-001.yaml",
      "record_task_assignments": True,
      "record_decision_basis": True,
      "record_integration_result": True,
      "retention": "preserve",
    },
    "outputs_policy": {
      "implementation_diff": "commit_candidate",
      "verification_summary": "required",
      "decision_basis": "preserve_if_used",
      "work_noise": "exclude",
    },
  }
  for key, value in overrides.items():
    if value is None:
      plan.pop(key, None)
    else:
      plan[key] = value

  path = Path(cwd) / "autonomous-parallel-plan.yaml"
  path.write_text(
    yaml.safe_dump(plan, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  return path


class AutonomousParallelPlanTests(unittest.TestCase):
  """自律・並列モード実行計画の機械ガード"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_valid_plan_returns_zero(self):
    """正常な実行計画は OK になる"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["current_state"]["task_count"], 2)

  def test_valid_plan_writes_history_ledger(self):
    """正常な実行計画は後追い用の履歴台帳を書き出す"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    ledger_path = cwd / "docs" / "logs" / "autonomous-parallel" / "ap-001.yaml"
    self.assertTrue(ledger_path.exists())
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
    self.assertEqual(ledger["run_id"], "ap-001")
    self.assertEqual(ledger["verdict"], "OK")
    self.assertEqual(ledger["task_ids"], ["task-a", "task-b"])
    self.assertEqual(ledger["history"]["record_decision_basis"], True)

  def test_missing_authorization_returns_two(self):
    """人間または proxy_model の承認記録がなければ逸脱にする"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(
      cwd,
      {"authorization": None},
    )

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("authorization", "\n".join(data["reasons"]))

  def test_subthread_without_separate_worktree_returns_two(self):
    """別スレッド実装が分離 worktree でなければ逸脱にする"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    plan["tasks"][0]["assignee"]["worktree_policy"] = "same_repo_write"
    plan_path.write_text(
      yaml.safe_dump(plan, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertIn("separate_worktree", "\n".join(data["reasons"]))

  def test_overlapping_parallel_paths_returns_two(self):
    """依存関係のない並列タスクが同じパスを書く場合は逸脱にする"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    plan["tasks"][1]["allowed_paths"] = ["src/a.py"]
    plan_path.write_text(
      yaml.safe_dump(plan, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertIn("allowed_paths", "\n".join(data["reasons"]))

  def test_missing_integration_gate_returns_two(self):
    """統合ゲートが不足していれば逸脱にする"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(
      cwd,
      {
        "integration_gate": {
          "requires_main_session_review": True,
          "requires_diff_scope_check": True,
          "requires_tests": True,
        },
      },
    )

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertIn("requires_decision_basis_review", "\n".join(data["reasons"]))

  def test_missing_history_returns_two(self):
    """履歴保存設定がなければ逸脱にする"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(
      cwd,
      {"history": None},
    )

    result = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertIn("history", "\n".join(data["reasons"]))

  def test_template_command_writes_valid_autonomous_plan(self):
    """テンプレート生成コマンドはそのまま検査可能な実行計画を書く"""
    cwd = Path(self.tmpdir)
    out_path = cwd / "plan.yaml"

    result = run_script(
      [
        "autonomous-plan-template",
        "--run-id", "ap-template-001",
        "--out", str(out_path),
      ],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertTrue(out_path.exists())

    plan = yaml.safe_load(out_path.read_text(encoding="utf-8"))
    self.assertEqual(plan["mode"], "autonomous_parallel")
    self.assertEqual(plan["run_id"], "ap-template-001")
    self.assertEqual(
      plan["history"]["ledger_path"],
      "docs/logs/autonomous-parallel/ap-template-001.yaml",
    )

    check = run_script(["autonomous-plan", str(out_path), "--json"], cwd=cwd)
    self.assertEqual(check.returncode, 0, check.stderr)

  def test_record_integration_updates_history_ledger(self):
    """統合結果記録コマンドは既存台帳に統合結果を追記する"""
    cwd = Path(self.tmpdir)
    plan_path = _write_autonomous_parallel_plan(cwd)
    check = run_script(["autonomous-plan", str(plan_path), "--json"], cwd=cwd)
    self.assertEqual(check.returncode, 0, check.stderr)

    ledger_path = cwd / "docs" / "logs" / "autonomous-parallel" / "ap-001.yaml"
    result = run_script(
      [
        "autonomous-plan-record-integration",
        "--ledger", str(ledger_path),
        "--status", "completed",
        "--tests", "python3 -m unittest tests.tools.test_check_workflow_action -v",
        "--decision", "main_session accepted scoped diff",
      ],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
    self.assertEqual(ledger["integration_result"]["status"], "completed")
    self.assertEqual(
      ledger["integration_result"]["decision"],
      "main_session accepted scoped diff",
    )
    self.assertEqual(
      ledger["integration_result"]["tests"],
      "python3 -m unittest tests.tools.test_check_workflow_action -v",
    )


class SpecSetExitCodeTests(unittest.TestCase):
  """spec-set サブコマンドの終了コード判定

  仕様 §6.1 spec-set の判定ロジック、§7.1 終了コード体系を検査する。
  """

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _copy_fixture(self, fixture_name):
    """fixture を一時ディレクトリにコピーしてそのパスを返す"""
    src = FIXTURE_BASE / fixture_name
    dst = Path(self.tmpdir) / fixture_name
    shutil.copytree(src, dst)
    return dst

  def test_approval_with_alignment_true_returns_zero(self):
    """ケース A：requirements の前段がすべて true、approval を true にする → exit 0

    仕様 §6.1 段の依存チェック：alignment=true なら approval=true に進める
    """
    cwd = self._copy_fixture("case-a-ready-for-approval")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )
    self.assertEqual(
      result.returncode, 0,
      f"alignment=true なので approval=true は通過すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )

  def test_approval_with_alignment_false_returns_two(self):
    """ケース B：alignment が false で approval を true にする → exit 2

    仕様 §6.1 段の依存チェック：alignment=false なら approval=true は逸脱
    """
    cwd = self._copy_fixture("case-b-approval-blocked")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 2,
      f"alignment=false なので approval=true は逸脱すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    self.assertIn(
      "DEVIATION", result.stdout,
      f"逸脱判定の場合は stdout に DEVIATION が含まれるべき。stdout: {result.stdout}",
    )

  def test_design_drafting_with_requirements_approved_returns_zero(self):
    """ケース C：requirements.approval=true で design.drafting=true にする → exit 0

    仕様 §6.1 フェーズの依存チェック：上流フェーズの approval=true なら次フェーズの drafting に進める
    """
    cwd = self._copy_fixture("case-c-approved")
    result = run_script(
      ["spec-set", "foundation", "design", "drafting", "true"],
      cwd=cwd,
    )
    self.assertEqual(
      result.returncode, 0,
      f"requirements.approval=true なので design.drafting=true は通過すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )

  def test_design_drafting_with_requirements_not_approved_returns_two(self):
    """ケース D：requirements.approval=false で design.drafting=true にする → exit 2

    仕様 §6.1 フェーズの依存チェック：上流フェーズの approval=false なら次フェーズの drafting は逸脱
    """
    cwd = self._copy_fixture("case-d-design-blocked")
    result = run_script(
      ["spec-set", "foundation", "design", "drafting", "true"],
      cwd=cwd,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 2,
      f"requirements.approval=false なので design.drafting=true は逸脱すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    self.assertIn(
      "DEVIATION", result.stdout,
      f"逸脱判定の場合は stdout に DEVIATION が含まれるべき。stdout: {result.stdout}",
    )

  def test_setting_true_stage_to_false_returns_one(self):
    """ケース E：現状 true の段を false に戻す → exit 1（reopen 警告）

    仕様 §6.1 new-value が false の場合：当該段が true だったら reopen 警告
    """
    cwd = self._copy_fixture("case-a-ready-for-approval")
    result = run_script(
      ["spec-set", "foundation", "requirements", "alignment", "false"],
      cwd=cwd,
    )
    self.assertEqual(
      result.returncode, 1,
      f"true → false は reopen 警告で exit 1。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )


class SpecSetOutputTests(unittest.TestCase):
  """spec-set サブコマンドの出力形式

  仕様 §7.2 人間可読出力、§7.3 JSON 出力を検査する。
  """

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _copy_fixture(self, fixture_name):
    src = FIXTURE_BASE / fixture_name
    dst = Path(self.tmpdir) / fixture_name
    shutil.copytree(src, dst)
    return dst

  def test_deviation_output_contains_verdict_keyword(self):
    """逸脱出力に [VERDICT] DEVIATION が含まれる（仕様 §7.2）"""
    cwd = self._copy_fixture("case-b-approval-blocked")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )
    self.assertIn(
      "DEVIATION", result.stdout,
      f"逸脱時の出力に DEVIATION の文字列が含まれるべき。\n"
      f"stdout: {result.stdout}",
    )

  def test_ok_output_contains_verdict_keyword(self):
    """通過出力に [VERDICT] OK が含まれる（仕様 §7.2）"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )
    self.assertIn(
      "OK", result.stdout,
      f"通過時の出力に OK の文字列が含まれるべき。\n"
      f"stdout: {result.stdout}",
    )

  def test_json_output_with_flag_for_ok(self):
    """--json で OK 判定が JSON 出力に切り替わる（仕様 §7.3）"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true", "--json"],
      cwd=cwd,
    )
    self.assertEqual(result.returncode, 0)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["exit_code"], 0)
    self.assertIn("action", data)
    self.assertIn("current_state", data)

  def test_json_output_with_flag_for_deviation(self):
    """--json で DEVIATION 判定が JSON 出力に切り替わる（仕様 §7.3）"""
    cwd = self._copy_fixture("case-b-approval-blocked")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true", "--json"],
      cwd=cwd,
    )
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertEqual(data["exit_code"], 2)
    self.assertGreater(
      len(data["reasons"]), 0,
      "逸脱時は reasons に 1 件以上の理由が含まれるべき",
    )


class SpecSetLoggingTests(unittest.TestCase):
  """ログ取得（MVP 必須、仕様 §8）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _copy_fixture(self, fixture_name):
    src = FIXTURE_BASE / fixture_name
    dst = Path(self.tmpdir) / fixture_name
    shutil.copytree(src, dst)
    return dst

  def test_log_file_is_appended_after_invocation(self):
    """スクリプト実行後にログファイルが追記される（仕様 §8.1 JSON Lines 形式）"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    log_path = cwd / "workflow-precheck.log"
    self.assertFalse(log_path.exists(), "事前にログファイルは存在しない前提")
    result = run_script(
      [
        "spec-set", "foundation", "requirements", "approval", "true",
        "--log-path", str(log_path),
      ],
      cwd=cwd,
    )
    self.assertEqual(result.returncode, 0)
    self.assertTrue(
      log_path.exists(),
      "スクリプト実行後にログファイルが作成されるべき",
    )
    log_content = log_path.read_text()
    self.assertGreater(
      len(log_content.strip()), 0,
      "ログに 1 行以上記録されるべき",
    )
    log_entry = json.loads(log_content.strip().splitlines()[0])
    self.assertIn("timestamp", log_entry)
    self.assertIn("action", log_entry)
    self.assertIn("verdict", log_entry)
    self.assertIn("exit_code", log_entry)

  def test_rationale_is_recorded_in_log(self):
    """spec-set で --rationale を渡すとログに記録される（仕様 §5.1）"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    log_path = cwd / "workflow-precheck.log"
    rationale = "利用者承認「ア」によりテストとして起動"
    result = run_script(
      [
        "spec-set", "foundation", "requirements", "approval", "true",
        "--rationale", rationale,
        "--log-path", str(log_path),
      ],
      cwd=cwd,
    )
    self.assertEqual(result.returncode, 0)
    log_entry = json.loads(log_path.read_text().strip().splitlines()[0])
    self.assertEqual(
      log_entry["action"]["args"]["rationale"], rationale,
      "ログの action.args.rationale に渡した値が記録されるべき",
    )


class SpecSetArgumentValidationTests(unittest.TestCase):
  """引数妥当性の検査（仕様 §5.1）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _copy_fixture(self, fixture_name):
    src = FIXTURE_BASE / fixture_name
    dst = Path(self.tmpdir) / fixture_name
    shutil.copytree(src, dst)
    return dst

  def test_invalid_feature_name_returns_nonzero(self):
    """存在しない機能名 → 非 0 終了"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    result = run_script(
      ["spec-set", "nonexistent-feature", "requirements", "approval", "true"],
      cwd=cwd,
    )
    _assert_script_invoked(self, result)
    self.assertNotEqual(
      result.returncode, 0,
      "存在しない feature は判定不能で非 0 終了すべき",
    )

  def test_invalid_phase_returns_nonzero(self):
    """無効なフェーズ名 → 非 0 終了"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    result = run_script(
      ["spec-set", "foundation", "nonexistent-phase", "approval", "true"],
      cwd=cwd,
    )
    _assert_script_invoked(self, result)
    self.assertNotEqual(
      result.returncode, 0,
      "存在しないフェーズは判定不能で非 0 終了すべき",
    )

  def test_invalid_value_returns_nonzero(self):
    """true／false 以外の値 → 非 0 終了"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "maybe"],
      cwd=cwd,
    )
    _assert_script_invoked(self, result)
    self.assertNotEqual(
      result.returncode, 0,
      "true／false 以外の値は引数エラーで非 0 終了すべき",
    )


class NextNavigationTests(unittest.TestCase):
  """next サブコマンドのワークフローナビゲーション判定"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_next_returns_evaluation_implementation_drafting_after_runtime_triad_review(self):
    """runtime triad-review 完了後は evaluation implementation drafting を返す"""
    cwd = Path(self.tmpdir)
    runtime_done = {
      "drafting": True,
      "triad-review": True,
      "review-wave": False,
      "alignment": False,
      "approval": False,
    }
    foundation_done = dict(runtime_done)
    _write_specs_for_next(
      cwd,
      {
        "foundation": foundation_done,
        "runtime": runtime_done,
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "stage")
    self.assertEqual(data["next_action"]["feature"], "evaluation")
    self.assertEqual(data["next_action"]["phase"], "implementation")
    self.assertEqual(data["next_action"]["stage"], "drafting")

  def test_next_review_wave_reports_recheck_and_pending_findings(self):
    """review-wave では recheck と pending-cross-feature-findings の確認情報を返す"""
    cwd = Path(self.tmpdir)
    implementation_ready = {
      "drafting": True,
      "triad-review": True,
      "review-wave": False,
      "alignment": False,
      "approval": False,
    }
    _write_specs_for_next(
      cwd,
      {feature: dict(implementation_ready) for feature in FEATURE_ORDER},
    )
    foundation_spec_path = cwd / ".reviewcompass" / "specs" / "foundation" / "spec.json"
    foundation_spec = json.loads(foundation_spec_path.read_text(encoding="utf-8"))
    foundation_spec["recheck"] = {
      "upstream_change_pending": True,
      "impacted_downstream_phases": ["implementation"],
    }
    foundation_spec_path.write_text(
      json.dumps(foundation_spec, ensure_ascii=False, indent=2),
      encoding="utf-8",
    )
    pending_path = cwd / ".reviewcompass" / "learning/workflow/carry-forward-register/reviewcompass-import.yaml"
    pending_path.write_text(
      "# 機能横断レビューで扱う所見の集約\n\n"
      "### A-001：未消化の波及所見\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "cross_feature_stage")
    self.assertEqual(data["next_action"]["phase"], "implementation")
    self.assertEqual(data["next_action"]["stage"], "review-wave")
    self.assertEqual(
      data["next_action"]["recheck_items"],
      [
        {
          "feature": "foundation",
          "impacted_downstream_phases": ["implementation"],
        }
      ],
    )
    self.assertEqual(
      data["next_action"]["pending_cross_feature_findings"]["unresolved_count"],
      1,
    )

  def test_next_prioritizes_in_progress_file(self):
    """進行中ファイルがあれば新規作業ではなく resume を返す"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "manual-process-2026-06-02.yaml").write_text(
      "process_id: manual-process\n"
      "next_step: 第3過程：連鎖再実施\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "resume_in_progress")
    self.assertEqual(
      data["next_action"]["file"],
      "stages/in-progress/manual-process-2026-06-02.yaml",
    )

  def test_next_reads_maintenance_in_progress(self):
    """maintenance の進行中ファイルがあれば通常ワークフローより優先する"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "maintenance-2026-06-03-codex-adapter.yaml").write_text(
      "process_id: maintenance\n"
      "title: Codex adapter migration\n"
      "reason: Codex 稼働前に Claude 前提の入口記述を整理する\n"
      "required_action: inspect_remaining_claude_assumptions\n"
      "blocked_normal_workflow: true\n"
      "allowed_scope:\n"
      "  - docs/operations/\n"
      "  - TODO_NEXT_SESSION.md\n"
      "completion_conditions:\n"
      "  - Codex 新規セッションで TODO から開始できる\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "maintenance_in_progress")
    self.assertEqual(
      data["next_action"]["file"],
      "stages/in-progress/maintenance-2026-06-03-codex-adapter.yaml",
    )
    self.assertEqual(data["next_action"]["process_id"], "maintenance")
    self.assertEqual(data["next_action"]["title"], "Codex adapter migration")
    self.assertEqual(
      data["next_action"]["required_action"],
      "inspect_remaining_claude_assumptions",
    )
    self.assertTrue(data["next_action"]["blocked_normal_workflow"])
    self.assertEqual(
      data["next_action"]["allowed_scope"],
      ["docs/operations/", "TODO_NEXT_SESSION.md"],
    )
    self.assertEqual(
      data["next_action"]["completion_conditions"],
      ["Codex 新規セッションで TODO から開始できる"],
    )

  def test_next_prioritizes_post_write_over_maintenance(self):
    """maintenance 中でも書き込み後検証対象があれば post-write を優先する"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "maintenance-2026-06-03-codex-adapter.yaml").write_text(
      "process_id: maintenance\n"
      "title: Codex adapter migration\n"
      "required_action: inspect_remaining_claude_assumptions\n",
      encoding="utf-8",
    )
    target = cwd / "docs" / "notes" / "codex-maintenance.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("maintenance 中の検証対象文書\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")
    self.assertEqual(
      data["next_action"]["target_files"],
      ["docs/notes/codex-maintenance.md"],
    )
    self.assertEqual(
      data["current_state"]["in_progress_files"],
      ["stages/in-progress/maintenance-2026-06-03-codex-adapter.yaml"],
    )

  def test_next_reads_reopen_in_progress_next_step(self):
    """reopen の進行中ファイルから next_step と required_action を返す"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "reopen-procedure-2026-06-02.yaml").write_text(
      "process_id: reopen-procedure\n"
      "started_at: 2026-06-02T00:00:00+09:00\n"
      "completed_steps: [\"第1過程：判定とフラグ差し戻し\", \"第2過程：正本修正\"]\n"
      "next_step: 第3過程：連鎖再実施\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "  - stages/requirements.yaml#approval\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "reopen_in_progress")
    self.assertEqual(data["next_action"]["process_id"], "reopen-procedure")
    self.assertEqual(data["next_action"]["next_step"], "第3過程：連鎖再実施")
    self.assertEqual(data["next_action"]["required_action"], "rerun_alignment_approval_chain")
    self.assertEqual(
      data["next_action"]["pending_gates"],
      ["stages/requirements.yaml#alignment", "stages/requirements.yaml#approval"],
    )

  def test_next_reopen_prefers_step_number_over_next_step_text(self):
    """reopen は next_step の表記ゆれより step_number を優先する"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "reopen-procedure-2026-06-02.yaml").write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第三工程：表記ゆれ\n"
      "step_number: 3\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#alignment\n"
      "current_blocker: null\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "reopen_in_progress")
    self.assertEqual(data["next_action"]["step_number"], 3)
    self.assertEqual(data["next_action"]["required_action"], "rerun_alignment_approval_chain")

  def test_next_reopen_human_blocker_requires_wait(self):
    """reopen の current_blocker があれば人間承認待ちを返す"""
    cwd = Path(self.tmpdir)
    _write_specs_for_next(cwd, {})
    in_progress_dir = cwd / "stages" / "in-progress"
    in_progress_dir.mkdir(parents=True)
    (in_progress_dir / "reopen-procedure-2026-06-02.yaml").write_text(
      "process_id: reopen-procedure\n"
      "next_step: 第3過程：連鎖再実施\n"
      "pending_gates:\n"
      "  - stages/requirements.yaml#approval\n"
      "current_blocker: stages/requirements.yaml#approval（人間承認待ち）\n",
      encoding="utf-8",
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "reopen_in_progress")
    self.assertEqual(data["next_action"]["required_action"], "wait_for_human_approval")
    self.assertEqual(
      data["next_action"]["current_blocker"],
      "stages/requirements.yaml#approval（人間承認待ち）",
    )

  def test_next_prioritizes_post_write_verification_for_target_doc_changes(self):
    """対象 docs 文書の未コミット変更があれば post-write-verification を返す"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証対象の正本文書\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")
    self.assertEqual(data["next_action"]["target_files"], ["docs/notes/new-policy.md"])

  def test_next_post_write_verification_target_matrix(self):
    """規律で定義された post-write-verification 対象だけを検出する"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target_paths = [
      "TODO_NEXT_SESSION.md",
      "docs/experiments/foo.md",
      "docs/notes/foo.md",
      "docs/operations/foo.md",
      "docs/plan/foo.md",
      "docs/reviews/2026-06-02-audit-foo.md",
      "docs/reviews/reopen-classification-2026-06-02.md",
    ]
    non_target_paths = [
      ".reviewcompass/specs/foundation/spec.json",
      "docs/archive/foo.md",
      "docs/reviews/2026-06-02-impl-triad-review.md",
      "docs/reviews/audit-summary.md",
    ]
    for path in target_paths + non_target_paths:
      file_path = cwd / path
      file_path.parent.mkdir(parents=True, exist_ok=True)
      file_path.write_text(f"{path}\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")
    self.assertEqual(data["next_action"]["target_files"], sorted(target_paths))

  def test_next_uses_completed_post_write_manifest_to_return_to_workflow(self):
    """完了 manifest が対象ファイルを覆う場合は通常 workflow に戻る"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証済みの正本文書\n", encoding="utf-8")
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/new-policy.md"],
        "target_sha256": {
          "docs/notes/new-policy.md": _sha256_file(target),
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 0,
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "stage")
    self.assertEqual(data["next_action"]["feature"], "foundation")

  def test_next_does_not_report_policy_violation_after_manifest_completion(self):
    """完了 manifest がある場合は pending 中の禁止混在として扱わない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証済みの正本文書\n", encoding="utf-8")
    runner = cwd / "tools" / "post_write_verify_new_policy.py"
    runner.parent.mkdir(parents=True, exist_ok=True)
    runner.write_text("# 検証完了後の通常実装変更\n", encoding="utf-8")
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/new-policy.md"],
        "target_sha256": {
          "docs/notes/new-policy.md": _sha256_file(target),
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 0,
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "stage")

  def test_next_does_not_complete_manifest_after_target_content_changes(self):
    """manifest 作成後に対象ファイルが変わった場合は完了扱いしない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証済みの正本文書\n", encoding="utf-8")
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/new-policy.md"],
        "target_sha256": {
          "docs/notes/new-policy.md": _sha256_file(target),
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 0,
      },
    )
    target.write_text("検証後に追記された正本文書\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")

  def test_next_does_not_complete_manifest_with_empty_required_verifiers(self):
    """required_verifiers が空の manifest は完了扱いしない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証者未指定の正本文書\n", encoding="utf-8")
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/new-policy.md"],
        "required_verifiers": [],
        "completed_verifiers": [],
        "unresolved_substantive_findings": 0,
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")

  def test_next_requires_human_decision_for_unresolved_substantive_findings(self):
    """manifest に未解決の本質的指摘があれば人間判断待ちを返す"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("本質的指摘ありの正本文書\n", encoding="utf-8")
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "pending_human",
        "target_files": ["docs/notes/new-policy.md"],
        "target_sha256": {
          "docs/notes/new-policy.md": _sha256_file(target),
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 1,
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_human_decision_required")
    self.assertEqual(data["next_action"]["target_files"], ["docs/notes/new-policy.md"])

  def test_next_uses_latest_post_write_manifest_when_multiple_exist(self):
    """同一対象の manifest が複数ある場合はファイル名が新しいものを優先する"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("複数 manifest の正本文書\n", encoding="utf-8")
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/new-policy.md"],
        "target_sha256": {
          "docs/notes/new-policy.md": _sha256_file(target),
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 0,
      },
    )
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-002.yaml",
      {
        "status": "pending_human",
        "target_files": ["docs/notes/new-policy.md"],
        "target_sha256": {
          "docs/notes/new-policy.md": _sha256_file(target),
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 1,
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_human_decision_required")
    self.assertEqual(
      data["next_action"]["manifest"],
      ".reviewcompass/post-write-verification/post-write-2026-06-02-002.yaml",
    )

  def test_next_deviation_when_new_runner_created_during_post_write_verification(self):
    """post-write-verification pending 中の新規 runner 作成は逸脱"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "new-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証対象の正本文書\n", encoding="utf-8")
    runner = cwd / "tools" / "post_write_verify_new_policy.py"
    runner.parent.mkdir(parents=True, exist_ok=True)
    runner.write_text("# 独自検証 runner\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertEqual(data["next_action"]["kind"], "post_write_policy_violation")
    self.assertEqual(
      data["next_action"]["forbidden_files"],
      ["tools/post_write_verify_new_policy.py"],
    )

  def test_next_deviation_when_template_changes_during_post_write_verification(self):
    """post-write-verification pending 中の template 変更は逸脱"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "operations" / "workflow.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証対象の運用文書\n", encoding="utf-8")
    template = cwd / "templates" / "todo" / "TODO_NEXT_SESSION.template.md"
    template.parent.mkdir(parents=True, exist_ok=True)
    template.write_text("再発防止としてのテンプレート変更\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_policy_violation")
    self.assertEqual(
      data["next_action"]["forbidden_files"],
      ["templates/todo/TODO_NEXT_SESSION.template.md"],
    )

  def test_next_deviation_when_discipline_change_is_mixed_with_other_post_write_target(self):
    """post-write-verification pending 中に規律変更が混ざる場合は逸脱"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "operations" / "workflow.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("検証対象の運用文書\n", encoding="utf-8")
    discipline = cwd / "docs" / "disciplines" / "discipline_approval_operation.md"
    discipline.parent.mkdir(parents=True, exist_ok=True)
    discipline.write_text("越境した規律変更\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_policy_violation")
    self.assertEqual(
      data["next_action"]["forbidden_files"],
      ["docs/disciplines/discipline_approval_operation.md"],
    )

  def test_next_allows_discipline_post_write_when_it_is_the_only_target(self):
    """規律ファイル単独の変更は post-write-verification 対象として扱う"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    discipline = cwd / "docs" / "disciplines" / "discipline_approval_operation.md"
    discipline.parent.mkdir(parents=True, exist_ok=True)
    discipline.write_text("正式手続き後の規律変更\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["next_action"]["kind"], "post_write_verification")
    self.assertEqual(
      data["next_action"]["target_files"],
      ["docs/disciplines/discipline_approval_operation.md"],
    )

  def test_next_ignores_workflow_stage_spec_changes_for_post_write_verification(self):
    """.reviewcompass/specs 配下は post-write-verification ではなく通常 workflow で扱う"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    spec_doc = cwd / ".reviewcompass" / "specs" / "foundation" / "requirements.md"
    spec_doc.write_text("ワークフロー段で検証される文書\n", encoding="utf-8")

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertNotEqual(data["next_action"]["kind"], "post_write_verification")


class PostWriteCoverageMatrixTests(unittest.TestCase):
  """manifest の verifications[] による coverage matrix チェック"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_next_accepts_manifest_with_full_coverage_and_matching_sha256(self):
    """verifications[] で全検証者が全ファイルを見て sha256 も一致した manifest は完了と判定する"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target_a = cwd / "docs" / "notes" / "policy-a.md"
    target_b = cwd / "docs" / "notes" / "policy-b.md"
    target_a.parent.mkdir(parents=True, exist_ok=True)
    target_a.write_text("ポリシーA\n", encoding="utf-8")
    target_b.write_text("ポリシーB\n", encoding="utf-8")
    sha_a = _sha256_file(target_a)
    sha_b = _sha256_file(target_b)
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/policy-a.md", "docs/notes/policy-b.md"],
        "target_sha256": {
          "docs/notes/policy-a.md": sha_a,
          "docs/notes/policy-b.md": sha_b,
        },
        "required_verifiers": ["google", "openai-55"],
        "completed_verifiers": ["google", "openai-55"],
        "unresolved_substantive_findings": 0,
        "verifications": [
          {
            "verifier": "google",
            "target_files": ["docs/notes/policy-a.md", "docs/notes/policy-b.md"],
            "target_sha256": {
              "docs/notes/policy-a.md": sha_a,
              "docs/notes/policy-b.md": sha_b,
            },
          },
          {
            "verifier": "openai-55",
            "target_files": ["docs/notes/policy-a.md", "docs/notes/policy-b.md"],
            "target_sha256": {
              "docs/notes/policy-a.md": sha_a,
              "docs/notes/policy-b.md": sha_b,
            },
          },
        ],
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(
      data["next_action"]["kind"], "stage",
      f"全検証者が全ファイルを見て sha256 一致の manifest は通常ワークフローに戻るべき。"
      f"next_action: {data['next_action']}",
    )

  def test_next_rejects_manifest_when_verifications_lack_per_entry_sha256(self):
    """verifications[] に per-entry target_sha256 がない manifest は完了と判定しない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target_a = cwd / "docs" / "notes" / "policy-a.md"
    target_b = cwd / "docs" / "notes" / "policy-b.md"
    target_a.parent.mkdir(parents=True, exist_ok=True)
    target_a.write_text("ポリシーA\n", encoding="utf-8")
    target_b.write_text("ポリシーB\n", encoding="utf-8")
    sha_a = _sha256_file(target_a)
    sha_b = _sha256_file(target_b)
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/policy-a.md", "docs/notes/policy-b.md"],
        "target_sha256": {
          "docs/notes/policy-a.md": sha_a,
          "docs/notes/policy-b.md": sha_b,
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 0,
        "verifications": [
          {
            "verifier": "google",
            "target_files": ["docs/notes/policy-a.md", "docs/notes/policy-b.md"],
            # target_sha256 が意図的に欠落
          },
        ],
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertNotEqual(
      data["next_action"]["kind"], "stage",
      "verifications[] 内の per-entry target_sha256 が欠落した manifest は完了扱いしてはいけない",
    )
    self.assertEqual(
      data["next_action"]["kind"], "post_write_verification",
    )

  def test_next_rejects_manifest_when_verifier_entry_sha256_mismatches_master(self):
    """verifications[] の sha256 がマスターと不一致の場合は完了と判定しない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target_a = cwd / "docs" / "notes" / "policy-a.md"
    target_a.parent.mkdir(parents=True, exist_ok=True)
    target_a.write_text("ポリシーA\n", encoding="utf-8")
    sha_a = _sha256_file(target_a)
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/policy-a.md"],
        "target_sha256": {
          "docs/notes/policy-a.md": sha_a,
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 0,
        "verifications": [
          {
            "verifier": "google",
            "target_files": ["docs/notes/policy-a.md"],
            "target_sha256": {
              "docs/notes/policy-a.md": "deadbeef" * 8,  # 不正な sha256
            },
          },
        ],
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertNotEqual(
      data["next_action"]["kind"], "stage",
      "verifications[] エントリの sha256 がマスターと不一致の manifest は完了扱いしてはいけない",
    )
    self.assertEqual(
      data["next_action"]["kind"], "post_write_verification",
    )

  def test_next_rejects_manifest_when_verifier_covers_only_partial_files(self):
    """分業（検証者ごとに異なるファイルのみ）の manifest は完了と判定しない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target_a = cwd / "docs" / "notes" / "policy-a.md"
    target_b = cwd / "docs" / "notes" / "policy-b.md"
    target_a.parent.mkdir(parents=True, exist_ok=True)
    target_a.write_text("ポリシーA\n", encoding="utf-8")
    target_b.write_text("ポリシーB\n", encoding="utf-8")
    sha_a = _sha256_file(target_a)
    sha_b = _sha256_file(target_b)
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/policy-a.md", "docs/notes/policy-b.md"],
        "target_sha256": {
          "docs/notes/policy-a.md": sha_a,
          "docs/notes/policy-b.md": sha_b,
        },
        "required_verifiers": ["google", "openai-55"],
        "completed_verifiers": ["google", "openai-55"],
        "unresolved_substantive_findings": 0,
        "verifications": [
          {
            "verifier": "google",
            "target_files": ["docs/notes/policy-a.md"],
          },
          {
            "verifier": "openai-55",
            "target_files": ["docs/notes/policy-b.md"],
          },
        ],
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertNotEqual(
      data["next_action"]["kind"], "stage",
      "分業（各検証者が全ファイルを見ていない）は完了扱いしてはいけない",
    )
    self.assertEqual(
      data["next_action"]["kind"], "post_write_verification",
      f"分業の manifest は post_write_verification を継続すべき。"
      f"next_action: {data['next_action']}",
    )

  def test_next_falls_back_to_completed_verifiers_without_verifications_field(self):
    """verifications[] がない旧形式 manifest は completed_verifiers でフォールバック判定する"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    target = cwd / "docs" / "notes" / "legacy-policy.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("旧形式の正本文書\n", encoding="utf-8")
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": ["docs/notes/legacy-policy.md"],
        "target_sha256": {
          "docs/notes/legacy-policy.md": _sha256_file(target),
        },
        "required_verifiers": ["google"],
        "completed_verifiers": ["google"],
        "unresolved_substantive_findings": 0,
      },
    )

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(
      data["next_action"]["kind"], "stage",
      "verifications[] なし旧形式は completed_verifiers で完了判定し通常ワークフローに戻るべき",
    )


class PostWriteReviewRunTraceabilityTests(unittest.TestCase):
  """review_run 宣言付き manifest の raw/rounds/triage/summary 機械検査"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _write_manifest_for_review_run(self, cwd, run_id):
    changed_targets = ["docs/notes/review-target.md"]
    run_dir = Path(cwd) / "docs" / "notes" / "review-runs" / run_id
    for path in sorted(run_dir.rglob("*")):
      if path.is_file():
        changed_targets.append(str(path.relative_to(cwd)))
    models = ["claude-sonnet-4-6", "gpt-5.4", "gemini-3.1-pro-preview"]
    _write_post_write_manifest(
      cwd,
      "post-write-2026-06-02-001.yaml",
      {
        "status": "completed",
        "target_files": changed_targets,
        "target_sha256": {
          path: _sha256_file(Path(cwd) / path)
          for path in changed_targets
        },
        "required_verifiers": models,
        "completed_verifiers": models,
        "unresolved_substantive_findings": 0,
        "review_run": {
          "path": f"docs/notes/review-runs/{run_id}",
          "summary_path": f"docs/notes/review-runs/{run_id}/model-result-summary.yaml",
        },
      },
    )

  def test_next_accepts_manifest_when_review_run_traceability_is_complete(self):
    """raw、rounds、triage、summary が全モデル分そろう manifest は完了と判定する"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    run_id = "traceability-complete"
    _write_review_run(
      cwd,
      run_id,
      ["claude-sonnet-4-6", "gpt-5.4", "gemini-3.1-pro-preview"],
    )
    self._write_manifest_for_review_run(cwd, run_id)

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(
      data["next_action"]["kind"], "stage",
      f"review_run の raw/rounds/triage/summary がそろう manifest は完了すべき。"
      f"next_action: {data['next_action']}",
    )

  def test_next_rejects_manifest_when_review_summary_is_missing(self):
    """summary artifact がない review_run は完了と判定しない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    run_id = "missing-summary"
    _write_review_run(
      cwd,
      run_id,
      ["claude-sonnet-4-6", "gpt-5.4", "gemini-3.1-pro-preview"],
      omit_summary=True,
    )
    self._write_manifest_for_review_run(cwd, run_id)

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(
      data["next_action"]["kind"], "post_write_verification",
      "モデル別 summary artifact がない review_run は完了扱いしてはいけない",
    )

  def test_next_rejects_manifest_when_required_model_raw_is_missing(self):
    """required_verifiers の raw が欠ける review_run は完了と判定しない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    run_id = "missing-raw"
    run_dir = _write_review_run(
      cwd,
      run_id,
      ["claude-sonnet-4-6", "gpt-5.4", "gemini-3.1-pro-preview"],
    )
    (run_dir / "raw" / "gpt-5.4.round-1.txt").unlink()
    self._write_manifest_for_review_run(cwd, run_id)

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(
      data["next_action"]["kind"], "post_write_verification",
      "required_verifiers の raw ファイルが欠ける review_run は完了扱いしてはいけない",
    )

  def test_next_rejects_manifest_when_model_is_absent_from_triage(self):
    """rounds にいるモデルが triage に出ていない review_run は完了と判定しない"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    run_id = "missing-triage-model"
    _write_review_run(
      cwd,
      run_id,
      ["claude-sonnet-4-6", "gpt-5.4", "gemini-3.1-pro-preview"],
      omit_triage_model="gpt-5.4",
    )
    self._write_manifest_for_review_run(cwd, run_id)

    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(
      data["next_action"]["kind"], "post_write_verification",
      "rounds にいるモデルが triage に出ていない review_run は完了扱いしてはいけない",
    )


class PostWriteReviewRunEndToEndTests(unittest.TestCase):
  """review-run から manifest 生成、next 完了認定までの統合テスト"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_next_accepts_manifest_generated_from_review_triage_helper(self):
    """review_triage.write_manifest が生成した厳格 manifest で next が通常 workflow に戻る"""
    cwd = Path(self.tmpdir)
    _init_git_repo(cwd)
    _write_specs_for_next(cwd, {})
    run_id = "e2e-review-run"
    run_dir = _write_review_run(
      cwd,
      run_id,
      ["claude-sonnet-4-6", "gpt-5.4", "gemini-3.1-pro-preview"],
    )
    manifest_path = (
      cwd
      / ".reviewcompass"
      / "post-write-verification"
      / "post-write-2026-06-03-999.yaml"
    )

    write_manifest(str(run_dir), str(manifest_path))
    result = run_script(["next", "--json"], cwd=cwd)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(
      data["next_action"]["kind"], "stage",
      f"review_triage.write_manifest 生成 manifest は next で完了認定されるべき。"
      f"next_action: {data['next_action']}",
    )
    self.assertEqual(
      data["current_state"]["post_write_manifest"],
      ".reviewcompass/post-write-verification/post-write-2026-06-03-999.yaml",
    )


class ReopenStartTests(unittest.TestCase):
  """reopen-start サブコマンドの trigger_map 解決と in-progress 生成"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_reopen_start_generates_in_progress_file_for_d_1(self):
    """D-1 から pending_gates を解決して in-progress YAML を生成する"""
    cwd = Path(self.tmpdir)
    result = run_script(
      [
        "reopen-start",
        "--classification", "D-1",
        "--feature", "runtime",
        "--basis", "docs/reviews/reopen-classification-2026-06-02.md",
        "--date", "2026-06-02",
        "--trigger", "design で requirements の不整合を検出",
        "--json",
      ],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["next_action"]["kind"], "reopen_started")
    self.assertEqual(
      data["next_action"]["pending_gates"],
      [
        "stages/requirements.yaml#alignment",
        "stages/requirements.yaml#approval",
        "stages/design.yaml#alignment",
        "stages/design.yaml#approval",
      ],
    )
    in_progress = cwd / "stages" / "in-progress" / "reopen-procedure-2026-06-02.yaml"
    self.assertTrue(in_progress.exists())
    generated = yaml.safe_load(in_progress.read_text(encoding="utf-8"))
    self.assertEqual(generated["process_id"], "reopen-procedure")
    self.assertEqual(generated["classification"], "D-1")
    self.assertEqual(generated["feature"], "runtime")
    self.assertEqual(generated["next_step"], "第1過程：判定とフラグ差し戻し")

  def test_reopen_start_invalid_classification_returns_deviation(self):
    """未定義 classification は fail-closed で逸脱"""
    cwd = Path(self.tmpdir)
    result = run_script(
      [
        "reopen-start",
        "--classification", "Z-9",
        "--feature", "runtime",
        "--basis", "docs/reviews/reopen-classification-2026-06-02.md",
        "--date", "2026-06-02",
        "--trigger", "invalid",
        "--json",
      ],
      cwd=cwd,
    )

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")


def _init_git_repo(tmpdir):
  """temp dir に git リポジトリを初期化し、初回コミットと .reviewcompass 構造を準備する

  commit／push サブコマンドのテスト用ヘルパー。
  """
  for cmd in [
    ["git", "init", "-q", "-b", "main"],
    ["git", "config", "user.email", "test@example.com"],
    ["git", "config", "user.name", "Test User"],
    ["git", "config", "commit.gpgsign", "false"],
  ]:
    subprocess.run(cmd, cwd=str(tmpdir), check=True, capture_output=True)
  # 初回コミット（空でないリポジトリにする）
  (Path(tmpdir) / ".gitignore").write_text("")
  subprocess.run(
    ["git", "add", ".gitignore"], cwd=str(tmpdir), check=True, capture_output=True
  )
  subprocess.run(
    ["git", "commit", "-qm", "initial"],
    cwd=str(tmpdir), check=True, capture_output=True,
  )
  # .reviewcompass 構造を準備（pending ファイルの土台）
  pending_dir = Path(tmpdir) / ".reviewcompass"
  pending_dir.mkdir()
  pending_file = pending_dir / "learning/workflow/carry-forward-register/reviewcompass-import.yaml"
  pending_file.write_text("# 機能横断レビューで扱う所見の集約\n")
  # pending ファイルもコミットして作業ツリーを clean な初期状態にする
  subprocess.run(
    ["git", "add", "learning/workflow/carry-forward-register/reviewcompass-import.yaml"],
    cwd=str(tmpdir), check=True, capture_output=True,
  )
  subprocess.run(
    ["git", "commit", "-qm", "add pending file"],
    cwd=str(tmpdir), check=True, capture_output=True,
  )
  return pending_file


def _set_pending_findings(pending_file, unresolved_count=0, resolved_count=0):
  """pending ファイルに未消化／対処済み所見を設定する"""
  lines = ["# 機能横断レビューで扱う所見の集約\n"]
  for i in range(unresolved_count):
    lines.append(f"\n### A-{i+1:03d}：テスト用未消化所見\n")
    lines.append("詳細内容...\n")
  for i in range(resolved_count):
    n = unresolved_count + i + 1
    lines.append(f"\n### A-{n:03d}：テスト用対処済み所見 ✅ 対処済み（2026-05-25）\n")
    lines.append("詳細内容...\n")
  pending_file.write_text("".join(lines))


def _stage_file(tmpdir, relpath, content):
  """ファイルを作成して git add 状態にする"""
  full = Path(tmpdir) / relpath
  full.parent.mkdir(parents=True, exist_ok=True)
  full.write_text(content)
  subprocess.run(
    ["git", "add", relpath], cwd=str(tmpdir), check=True, capture_output=True
  )


def _write_commit_approval(tmpdir, target_files, consumed=False):
  """commit 事前検査用のユーザ承認レコードを書く"""
  approval_dir = Path(tmpdir) / ".reviewcompass" / "approvals"
  approval_dir.mkdir(parents=True, exist_ok=True)
  approval_path = approval_dir / "commit-approval.json"
  approval_path.write_text(
    json.dumps(
      {
        "approved_action": "commit",
        "approved_by": "user",
        "approved_at": "2026-06-03T00:00:00+09:00",
        "rationale": "利用者がコミットを明示承認",
        "target_files": target_files,
        "expires_after_commit": True,
        "consumed": consumed,
      },
      ensure_ascii=False,
      indent=2,
    ),
    encoding="utf-8",
  )
  return approval_path


def _write_completed_post_write_manifest(tmpdir, target_files):
  """対象ファイルを覆う完了 post-write manifest を書く"""
  target_sha256 = {
    relpath: _sha256_file(Path(tmpdir) / relpath)
    for relpath in target_files
  }
  _write_post_write_manifest(
    tmpdir,
    "post-write-2026-06-03-999.yaml",
    {
      "status": "completed",
      "target_files": target_files,
      "target_sha256": target_sha256,
      "required_verifiers": ["google"],
      "completed_verifiers": ["google"],
      "unresolved_substantive_findings": 0,
    },
  )


class CommitExitCodeTests(unittest.TestCase):
  """commit サブコマンドの終了コード判定（仕様 §6.2）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    self.pending_file = _init_git_repo(self.tmpdir)

  def test_commit_with_no_pending_and_normal_changes_returns_zero(self):
    """未消化所見 0 件 + 通常変更 + ユーザ承認あり → exit 0"""
    _set_pending_findings(self.pending_file, unresolved_count=0, resolved_count=2)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(self.tmpdir, ["notes.md"])
    result = run_script(
      ["commit", "--rationale", "テスト用 commit、利用者承認の出典あり"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 0,
      f"未消化所見なし＋通常変更のみは通過すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )

  def test_commit_with_pending_findings_returns_one(self):
    """未消化所見 1 件以上 → exit 1（警告）"""
    _set_pending_findings(self.pending_file, unresolved_count=1)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(self.tmpdir, ["notes.md"])
    result = run_script(
      ["commit", "--rationale", "未消化所見ありの場面のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 1,
      f"未消化所見ありは警告で exit 1。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    self.assertIn(
      "WARN", result.stdout,
      f"警告判定の出力に WARN が含まれるべき。stdout: {result.stdout}",
    )

  def test_commit_with_spec_json_change_returns_one(self):
    """spec.json の変更含む → exit 1（要注意変更の警告）"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(
      self.tmpdir,
      ".reviewcompass/specs/foundation/spec.json",
      '{"feature_name":"foundation"}',
    )
    _write_commit_approval(self.tmpdir, [".reviewcompass/specs/foundation/spec.json"])
    result = run_script(
      ["commit", "--rationale", "spec.json 更新のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 1,
      f"spec.json 変更は要注意変更として警告 exit 1。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )

  def test_commit_with_plan_doc_change_returns_one(self):
    """計画書（docs/plan/ 配下）の変更含む → exit 1"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "docs/plan/test-plan.md", "# テスト計画")
    _write_completed_post_write_manifest(self.tmpdir, ["docs/plan/test-plan.md"])
    _write_commit_approval(self.tmpdir, ["docs/plan/test-plan.md"])
    result = run_script(
      ["commit", "--rationale", "計画書追加のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 1,
      f"docs/plan/ 配下の変更は要注意で警告 exit 1。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )

  def test_commit_with_credential_file_returns_two(self):
    """ファイル名に credentials を含む変更 → exit 2（危険変更）"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "credentials.json", '{"key":"dummy"}')
    _write_commit_approval(self.tmpdir, ["credentials.json"])
    result = run_script(
      ["commit", "--rationale", "credentials を含むファイルのテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 2,
      f"credentials を含むファイル名は危険変更として逸脱 exit 2。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    self.assertIn(
      "DEVIATION", result.stdout,
      f"逸脱判定の出力に DEVIATION が含まれるべき。stdout: {result.stdout}",
    )

  def test_commit_without_user_approval_returns_two(self):
    """ユーザ承認レコードなし → exit 2（逸脱）"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    result = run_script(
      ["commit", "--rationale", "承認なし commit のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 2,
      f"承認レコードなしの commit は逸脱 exit 2。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    self.assertIn("ユーザ承認レコード", result.stdout)

  def test_commit_with_consumed_user_approval_returns_two(self):
    """消費済み承認レコード → exit 2（逸脱）"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(self.tmpdir, ["notes.md"], consumed=True)
    result = run_script(
      ["commit", "--rationale", "消費済み承認のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    self.assertIn("消費済み", result.stdout)

  def test_commit_with_approval_scope_mismatch_returns_two(self):
    """承認対象と staged ファイルが一致しない → exit 2（逸脱）"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "notes.md", "# テスト用ノート")
    _write_commit_approval(self.tmpdir, ["other.md"])
    result = run_script(
      ["commit", "--rationale", "承認対象不一致のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    self.assertIn("承認対象外", result.stdout)

  def test_commit_with_post_write_target_without_manifest_returns_two(self):
    """post-write 対象文書が staged され、完了 manifest がなければ exit 2"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "TODO_NEXT_SESSION.md", "# 次セッション")
    _write_commit_approval(self.tmpdir, ["TODO_NEXT_SESSION.md"])
    result = run_script(
      ["commit", "--rationale", "post-write 未検証の遮断テスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    self.assertIn("post-write-verification 未完了", result.stdout)

  def test_commit_with_post_write_target_and_completed_manifest_returns_zero(self):
    """post-write 対象文書が staged されても完了 manifest があれば exit 0"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(self.tmpdir, "TODO_NEXT_SESSION.md", "# 次セッション")
    _write_completed_post_write_manifest(self.tmpdir, ["TODO_NEXT_SESSION.md"])
    _write_commit_approval(self.tmpdir, ["TODO_NEXT_SESSION.md"])
    result = run_script(
      ["commit", "--rationale", "post-write 検証済み commit のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 0,
      f"完了 manifest がある post-write 対象 commit は通過すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )

  def test_commit_with_operations_doc_and_completed_manifest_returns_zero(self):
    """docs/operations 配下の対象文書も completed manifest があれば exit 0"""
    _set_pending_findings(self.pending_file, unresolved_count=0)
    _stage_file(
      self.tmpdir,
      "docs/operations/WORKFLOW_PRECHECK.md",
      "# WORKFLOW_PRECHECK",
    )
    _write_completed_post_write_manifest(
      self.tmpdir,
      ["docs/operations/WORKFLOW_PRECHECK.md"],
    )
    _write_commit_approval(self.tmpdir, ["docs/operations/WORKFLOW_PRECHECK.md"])
    result = run_script(
      ["commit", "--rationale", "operations 文書検証済み commit のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 0, result.stdout)

  def test_commit_rationale_is_required(self):
    """commit に --rationale なし → 非 0 終了（仕様 §5.2 必須）"""
    _stage_file(self.tmpdir, "notes.md", "test")
    result = run_script(["commit"], cwd=self.tmpdir)
    self.assertNotEqual(
      result.returncode, 0,
      f"--rationale は必須のため非 0 終了すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    # 厳密化：実装前は「サブコマンド不明」で非 0 になるが、
    # 実装後は --rationale 不足で非 0 になることを区別する
    self.assertIn(
      "rationale", result.stderr.lower(),
      f"--rationale 不足のエラーメッセージは stderr に 'rationale' を含むべき。\n"
      f"stderr: {result.stderr}",
    )


class PushExitCodeTests(unittest.TestCase):
  """push サブコマンドの終了コード判定（仕様 §6.3）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    self.pending_file = _init_git_repo(self.tmpdir)

  def test_push_with_clean_tree_returns_zero(self):
    """作業ツリーが clean → exit 0"""
    result = run_script(
      ["push", "--rationale", "clean な状態のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 0,
      f"作業ツリー clean は通過すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )

  def test_push_with_dirty_tree_returns_two(self):
    """作業ツリーが dirty（未追跡ファイルあり）→ exit 2"""
    (Path(self.tmpdir) / "untracked.md").write_text("# 未追跡")
    result = run_script(
      ["push", "--rationale", "dirty な状態のテスト"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 2,
      f"作業ツリー dirty は逸脱 exit 2。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    self.assertIn(
      "DEVIATION", result.stdout,
      f"逸脱判定の出力に DEVIATION が含まれるべき。stdout: {result.stdout}",
    )

  def test_push_rationale_is_required(self):
    """push に --rationale なし → 非 0 終了（仕様 §5.3 必須）"""
    result = run_script(["push"], cwd=self.tmpdir)
    self.assertNotEqual(
      result.returncode, 0,
      f"--rationale は必須のため非 0 終了すべき。\n"
      f"stdout: {result.stdout}\nstderr: {result.stderr}",
    )
    # 厳密化：実装前は「サブコマンド不明」で非 0 になるが、
    # 実装後は --rationale 不足で非 0 になることを区別する
    self.assertIn(
      "rationale", result.stderr.lower(),
      f"--rationale 不足のエラーメッセージは stderr に 'rationale' を含むべき。\n"
      f"stderr: {result.stderr}",
    )


class AuditCommitTests(unittest.TestCase):
  """audit-commit サブコマンドの post-write 遡及監査"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    _init_git_repo(self.tmpdir)

  def _commit_file(self, relpath, content, message):
    _stage_file(self.tmpdir, relpath, content)
    subprocess.run(
      ["git", "commit", "-qm", message],
      cwd=str(self.tmpdir),
      check=True,
      capture_output=True,
    )

  def test_audit_commit_detects_post_write_target_without_manifest(self):
    """指定 commit に post-write 対象があり manifest がなければ exit 2"""
    self._commit_file("TODO_NEXT_SESSION.md", "# 次セッション", "add todo")
    result = run_script(["audit-commit", "HEAD", "--json"], cwd=self.tmpdir)
    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("TODO_NEXT_SESSION.md", data["current_state"]["post_write_targets"])

  def test_audit_commit_detects_root_commit_post_write_target_without_manifest(self):
    """root commit の post-write 対象追加も監査対象に含める"""
    tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, tmpdir)
    for cmd in [
      ["git", "init", "-q", "-b", "main"],
      ["git", "config", "user.email", "test@example.com"],
      ["git", "config", "user.name", "Test User"],
      ["git", "config", "commit.gpgsign", "false"],
    ]:
      subprocess.run(cmd, cwd=str(tmpdir), check=True, capture_output=True)
    _stage_file(tmpdir, "TODO_NEXT_SESSION.md", "# root todo")
    subprocess.run(
      ["git", "commit", "-qm", "root todo"],
      cwd=str(tmpdir),
      check=True,
      capture_output=True,
    )

    result = run_script(["audit-commit", "HEAD", "--json"], cwd=tmpdir)

    _assert_script_invoked(self, result)
    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertIn("TODO_NEXT_SESSION.md", data["current_state"]["post_write_targets"])

  def test_audit_commit_accepts_post_write_target_with_matching_manifest(self):
    """指定 commit の post-write 対象を覆う manifest があれば exit 0"""
    self._commit_file("TODO_NEXT_SESSION.md", "# 次セッション", "add todo")
    _write_completed_post_write_manifest(self.tmpdir, ["TODO_NEXT_SESSION.md"])
    result = run_script(["audit-commit", "HEAD", "--json"], cwd=self.tmpdir)
    _assert_script_invoked(self, result)
    self.assertEqual(
      result.returncode, 0,
      f"matching manifest should pass.\nstdout: {result.stdout}\nstderr: {result.stderr}",
    )


class CommitPushOutputTests(unittest.TestCase):
  """commit／push の JSON 出力検査（仕様 §7.3）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)
    self.pending_file = _init_git_repo(self.tmpdir)

  def test_commit_json_output(self):
    """commit に --json で JSON 出力に切り替わる"""
    _write_commit_approval(self.tmpdir, [])
    result = run_script(
      ["commit", "--rationale", "JSON 出力のテスト", "--json"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    data = json.loads(result.stdout)
    self.assertIn("verdict", data)
    self.assertIn("action", data)
    self.assertEqual(
      data["action"]["subcommand"], "commit",
      "JSON 出力の action.subcommand は 'commit' であるべき",
    )
    self.assertIn("commit_approval", data["current_state"])

  def test_push_json_output(self):
    """push に --json で JSON 出力に切り替わる"""
    result = run_script(
      ["push", "--rationale", "JSON 出力のテスト", "--json"],
      cwd=self.tmpdir,
    )
    _assert_script_invoked(self, result)
    data = json.loads(result.stdout)
    self.assertIn("verdict", data)
    self.assertIn("action", data)
    self.assertEqual(
      data["action"]["subcommand"], "push",
      "JSON 出力の action.subcommand は 'push' であるべき",
    )


if __name__ == "__main__":
  unittest.main()

```

## FILE: tests/tools/test_workflow_management_implementation_drafting.py

```text
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT = REPO_ROOT / ".reviewcompass" / "specs" / "workflow-management" / "implementation-drafting.md"


def test_workflow_management_implementation_drafting_report_exists():
  assert REPORT.exists()


def test_workflow_management_implementation_drafting_report_tracks_autonomous_helpers():
  text = REPORT.read_text(encoding="utf-8")
  required_fragments = [
    "# workflow-management implementation drafting 棚卸し",
    "## 実装済み",
    "autonomous-plan",
    "autonomous-plan-template",
    "autonomous-plan-record-integration",
    "## 未充足",
    "## drafting 完了判断",
  ]
  for fragment in required_fragments:
    assert fragment in text


def test_workflow_management_implementation_drafting_report_mentions_verification():
  text = REPORT.read_text(encoding="utf-8")
  assert "python3 -m unittest tests.tools.test_check_workflow_action -v" in text
  assert "python3 -m pytest tests/tools/test_session_record_contract.py -q" in text

```

## FILE: tools/api_providers/tests/test_run_review.py

```text
# tools/api_providers/tests/test_run_review.py
# 複数モデル review-run orchestrator の TDD テスト。

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import yaml

from tools.api_providers.run_review import main


def _make_config(tmp_path):
  config_path = tmp_path / "api-settings.yaml"
  config_path.write_text(
    """
connection:
  timeout_seconds: 60
  max_retries: 1
default:
  primary:
    path: api
    provider: anthropic-api
    model: claude-sonnet-4-6
  adversarial:
    path: api
    provider: openai-api
    model: gpt-5.4
  judgment:
    path: api
    provider: gemini-api
    model: gemini-3.1-pro-preview
""",
    encoding="utf-8",
  )
  return config_path


def _make_provider_factory(responses):
  """provider 名に応じたモック provider class を返す factory。"""
  def factory(provider_name):
    mock_instance = MagicMock()
    mock_instance.send_request.return_value = responses[provider_name]
    return MagicMock(return_value=mock_instance)

  return factory


def test_run_review_executes_three_roles_and_creates_summary_and_triage(tmp_path, monkeypatch, capsys):
  """3 役を同じ review-run に集約し、summary と triage 下書きを生成する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("レビュー対象\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  responses = {
    "anthropic-api": """
findings:
  - severity: ERROR
    target_location: target.md
    description: 契約違反の可能性
    rationale: 仕様に影響する
""",
    "openai-api": "findings: []\n",
    "gemini-api": """
findings:
  - severity: WARN
    target_location: target.md
    description: 説明不足
    rationale: 読み手に補足が必要
""",
  }

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--variant", "default",
        "--target", str(target),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
        "--config", str(config_path),
      ]
    )

  assert exit_code == 0
  output = capsys.readouterr().out
  assert "claude-sonnet-4-6" in output
  assert "gpt-5.4" in output
  assert "gemini-3.1-pro-preview" in output
  assert "triage_pending" in output

  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  summary = yaml.safe_load(
    (review_run_dir / "model-result-summary.yaml").read_text(encoding="utf-8")
  )
  triage = yaml.safe_load((review_run_dir / "triage.yaml").read_text(encoding="utf-8"))

  assert [item["role"] for item in rounds["model_results"]] == [
    "primary",
    "adversarial",
    "judgment",
  ]
  assert len(summary["models"]) == 3
  assert (review_run_dir / "review_summary.md").is_file()
  assert summary["models"][1]["triage_status"] == "no_findings"
  assert summary["models"][0]["triage_status"] == "triage_pending"

  assert triage["triage_status"] == "draft"
  assert len(triage["items"]) == 2
  assert {item["source_model"] for item in triage["items"]} == {
    "claude-sonnet-4-6",
    "gemini-3.1-pro-preview",
  }
  assert all(item["decision_status"] == "human_required" for item in triage["items"])
  assert all(item["final_label"] is None for item in triage["items"])


def test_run_review_continues_after_one_role_parse_failure(tmp_path, monkeypatch):
  """1 役が parse 失敗しても raw を残し、他役の実行と summary 生成を続ける。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  monkeypatch.setenv("GEMINI_API_KEY", "test-key")
  target = tmp_path / "target.md"
  target.write_text("レビュー対象\n", encoding="utf-8")
  config_path = _make_config(tmp_path)
  review_run_dir = tmp_path / "review-run"
  responses = {
    "anthropic-api": "findings: [broken\n",
    "openai-api": "findings: []\n",
    "gemini-api": "findings: []\n",
  }

  with patch(
    "tools.api_providers.run_review.get_provider",
    side_effect=_make_provider_factory(responses),
  ):
    exit_code = main(
      [
        "--target", str(target),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
        "--config", str(config_path),
      ]
    )

  assert exit_code == 1
  summary = yaml.safe_load(
    (review_run_dir / "model-result-summary.yaml").read_text(encoding="utf-8")
  )
  statuses = {item["model_id"]: item["parse_status"] for item in summary["models"]}
  assert statuses["claude-sonnet-4-6"] == "parse_failed"
  assert statuses["gpt-5.4"] == "parsed"
  assert statuses["gemini-3.1-pro-preview"] == "parsed"
  assert (review_run_dir / "raw" / "claude-sonnet-4-6.round-1.txt").is_file()
  triage = yaml.safe_load((review_run_dir / "triage.yaml").read_text(encoding="utf-8"))
  assert triage["triage_status"] == "draft"

```

## FILE: tools/api_providers/tests/test_run_role.py

```text
# tools/api_providers/tests/test_run_role.py
# run_role エントリポイントのテスト（サブサイクル 4-C、TDD 先行）。
# 計画書 §5.9.7.1 の入出力契約に準拠する。
# プロバイダーは MagicMock で置換し、in-process でテストする。

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# プロジェクトルートを sys.path に追加
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import pytest
import yaml

from tools.api_providers.run_role import build_prompt, main


# --- fixtures ---


@pytest.fixture
def tmp_target_file(tmp_path):
  target = tmp_path / "target.md"
  target.write_text("対象文書の内容\n要件の本文を記載", encoding="utf-8")
  return target


@pytest.fixture
def tmp_prior_finding(tmp_path):
  prior = tmp_path / "prior.yaml"
  prior.write_text(
    "findings:\n  - severity: WARN\n    description: 前段の所見\n",
    encoding="utf-8",
  )
  return prior


@pytest.fixture
def tmp_config(tmp_path):
  config_path = tmp_path / "api-settings.yaml"
  config_path.write_text(
    """
connection:
  timeout_seconds: 60
  max_retries: 1
default:
  primary:
    path: api
    provider: anthropic-api
    model: claude-opus-4-7
  adversarial:
    path: api
    provider: anthropic-api
    model: claude-sonnet-4-6
  judgment:
    path: api
    provider: anthropic-api
    model: claude-opus-4-7
""",
    encoding="utf-8",
  )
  return config_path


def _make_mock_provider(send_response="findings: []\n", side_effect=None):
  """get_provider をモック化する補助関数。"""
  mock_instance = MagicMock()
  if side_effect is not None:
    mock_instance.send_request.side_effect = side_effect
  else:
    mock_instance.send_request.return_value = send_response
  mock_cls = MagicMock(return_value=mock_instance)
  return mock_cls, mock_instance


# --- 1. build_prompt の正常系 ---


def test_build_prompt_includes_target_content(tmp_target_file):
  """build_prompt の出力に対象文書の内容が含まれる。"""
  prompt = build_prompt(str(tmp_target_file), "requirements_triad_review", "観点-1", [])
  assert "対象文書の内容" in prompt
  assert "要件の本文を記載" in prompt


def test_build_prompt_includes_phase(tmp_target_file):
  """build_prompt の出力に段名が含まれる。"""
  prompt = build_prompt(str(tmp_target_file), "design_triad_review", "観点-1", [])
  assert "design_triad_review" in prompt


def test_build_prompt_includes_criteria(tmp_target_file):
  """build_prompt の出力に観点識別子が含まれる。"""
  prompt = build_prompt(str(tmp_target_file), "requirements", "観点-3", [])
  assert "観点-3" in prompt


def test_build_prompt_includes_prior_finding(tmp_target_file, tmp_prior_finding):
  """build_prompt の出力に前段所見の内容が含まれる。"""
  prompt = build_prompt(
    str(tmp_target_file),
    "requirements",
    "観点-1",
    [str(tmp_prior_finding)],
  )
  assert "前段の所見" in prompt


def test_build_prompt_includes_multiple_prior_findings(tmp_target_file, tmp_path):
  """build_prompt が複数の前段所見をすべて含む。"""
  p1 = tmp_path / "prior1.yaml"
  p1.write_text(
    "findings:\n  - description: 所見 アルファ\n", encoding="utf-8"
  )
  p2 = tmp_path / "prior2.yaml"
  p2.write_text(
    "findings:\n  - description: 所見 ベータ\n", encoding="utf-8"
  )
  prompt = build_prompt(
    str(tmp_target_file),
    "requirements",
    "観点-1",
    [str(p1), str(p2)],
  )
  assert "所見 アルファ" in prompt
  assert "所見 ベータ" in prompt


def test_build_prompt_uses_anthropic_specific_template(tmp_target_file):
  """anthropic-api では code fence / review wrapper を禁止する専用テンプレートを使う。"""
  prompt = build_prompt(
    str(tmp_target_file),
    "post_write_verification",
    "観点-1",
    [],
    provider_name="anthropic-api",
    model="claude-sonnet-4-6",
  )
  assert "model_id: claude-sonnet-4-6" in prompt
  assert "Do not wrap the YAML in Markdown code fences" in prompt
  assert "Do not use review:" in prompt
  assert "top-level key must be exactly findings" in prompt


def test_build_prompt_uses_default_template_for_unknown_provider(tmp_target_file):
  """未知 provider では共通テンプレートへ fallback する。"""
  prompt = build_prompt(
    str(tmp_target_file),
    "post_write_verification",
    "観点-1",
    [],
    provider_name="unknown-provider",
    model="unknown-model",
  )
  assert "prompt_id: default_review" in prompt
  assert "top-level key must be exactly findings" in prompt
  assert "findings: []" in prompt


def test_build_prompt_does_not_replace_placeholders_inside_target_content(tmp_path):
  """対象文書内の template placeholder 文字列は本文として保持する。"""
  target = tmp_path / "target.md"
  target.write_text(
    "# Target\n{{ prior_findings }}\n{{ target_path }}\n",
    encoding="utf-8",
  )

  prompt = build_prompt(
    str(target),
    "post_write_verification",
    "観点-1",
    [],
    provider_name="anthropic-api",
    model="claude-sonnet-4-6",
  )

  assert "# Target\n{{ prior_findings }}\n{{ target_path }}" in prompt


def test_build_prompt_renders_prior_findings_in_provider_template(
  tmp_target_file,
  tmp_prior_finding,
):
  """provider template 経由でも前段所見がプロンプトへ入る。"""
  prompt = build_prompt(
    str(tmp_target_file),
    "post_write_verification",
    "観点-1",
    [str(tmp_prior_finding)],
    provider_name="openai-api",
    model="gpt-5.4",
  )

  assert "# 前段所見 1" in prompt
  assert "前段の所見" in prompt


# --- 2. main の正常系 ---


def test_main_outputs_formatted_yaml(tmp_target_file, tmp_config, monkeypatch, capsys):
  """main が正常系で整形済み YAML を標準出力に書く。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  mock_response = """
findings:
  - severity: WARN
    target_location: a.md
    description: テスト所見
    rationale: テスト根拠
"""
  mock_cls, _ = _make_mock_provider(send_response=mock_response)
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "requirements_triad_review",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
      ]
    )
  assert exit_code == 0
  captured = capsys.readouterr()
  parsed = yaml.safe_load(captured.out)
  assert parsed["role"] == "primary"
  assert parsed["provider"] == "anthropic-api"
  assert parsed["model"] == "claude-opus-4-7"
  assert parsed["attempts"] == 1
  assert len(parsed["findings"]) == 1
  assert parsed["findings"][0]["severity"] == "WARN"


def test_main_duration_seconds_is_present(
  tmp_target_file, tmp_config, monkeypatch, capsys
):
  """main の出力に duration_seconds（所要時間）が含まれる。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  mock_cls, _ = _make_mock_provider()
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "requirements",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
      ]
    )
  captured = capsys.readouterr()
  parsed = yaml.safe_load(captured.out)
  assert "duration_seconds" in parsed
  assert isinstance(parsed["duration_seconds"], (int, float))
  assert parsed["duration_seconds"] >= 0


# --- 3. main の異常系 ---


def test_main_missing_required_args_raises():
  """必須引数が不足していたら SystemExit（argparse 既定動作）。"""
  with pytest.raises(SystemExit):
    main(["--role", "primary"])  # --target, --phase, --criteria が欠落


def test_main_provider_error_returns_nonzero(
  tmp_target_file, tmp_config, monkeypatch, capsys
):
  """プロバイダーが例外を投げたら非ゼロ終了、標準エラーに理由を出力。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  mock_cls, _ = _make_mock_provider(side_effect=RuntimeError("API 呼び出し失敗"))
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "requirements",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
      ]
    )
  assert exit_code != 0
  captured = capsys.readouterr()
  assert "エラー" in captured.err or "error" in captured.err.lower()


# --- 4. variant 切替 ---


def test_main_uses_variant_when_specified(
  tmp_target_file, tmp_path, monkeypatch, capsys
):
  """--variant が指定されたら variants から役設定を取得する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  monkeypatch.setenv("OPENAI_API_KEY", "test-key")
  config_path = tmp_path / "api-settings.yaml"
  config_path.write_text(
    """
connection:
  timeout_seconds: 60
  max_retries: 1
default:
  primary:
    path: api
    provider: anthropic-api
    model: claude-opus-4-7
variants:
  openai_variant:
    primary:
      path: api
      provider: openai-api
      model: gpt-test
""",
    encoding="utf-8",
  )
  mock_cls, _ = _make_mock_provider()
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    main(
      [
        "--role", "primary",
        "--variant", "openai_variant",
        "--target", str(tmp_target_file),
        "--phase", "requirements",
        "--criteria", "観点-1",
        "--config", str(config_path),
      ]
    )
  captured = capsys.readouterr()
  parsed = yaml.safe_load(captured.out)
  assert parsed["provider"] == "openai-api"
  assert parsed["model"] == "gpt-test"


# --- 5. raw / parsed / review-run 成果物 ---


def test_main_writes_raw_out_before_parse_failure(
  tmp_target_file, tmp_config, tmp_path, monkeypatch, capsys
):
  """parse 失敗時でも --raw-out に provider 生応答を保存する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  raw_out = tmp_path / "raw.txt"
  mock_cls, _ = _make_mock_provider(send_response="not: [valid\n")
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "requirements",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
        "--raw-out", str(raw_out),
      ]
    )

  assert exit_code != 0
  assert raw_out.read_text(encoding="utf-8") == "not: [valid\n"
  captured = capsys.readouterr()
  assert "エラー" in captured.err


def test_main_writes_parsed_out_on_parse_success(
  tmp_target_file, tmp_config, tmp_path, monkeypatch
):
  """parse 成功時に --parsed-out へ整形済み YAML を保存する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  parsed_out = tmp_path / "parsed.yaml"
  mock_response = """
findings:
  - severity: INFO
    target_location: a.md
    description: 指摘なし
    rationale: テスト
"""
  mock_cls, _ = _make_mock_provider(send_response=mock_response)
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "requirements",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
        "--parsed-out", str(parsed_out),
      ]
    )

  assert exit_code == 0
  parsed = yaml.safe_load(parsed_out.read_text(encoding="utf-8"))
  assert parsed["role"] == "primary"
  assert parsed["model"] == "claude-opus-4-7"
  assert parsed["findings"][0]["severity"] == "INFO"


def test_main_updates_review_run_artifacts(
  tmp_target_file, tmp_config, tmp_path, monkeypatch
):
  """--review-run-dir 指定時に raw、parsed、rounds、summary、target manifest を生成する。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  review_run_dir = tmp_path / "review-run"
  mock_response = """
findings:
  - severity: WARN
    target_location: a.md
    description: 要確認
    rationale: テスト
"""
  mock_cls, _ = _make_mock_provider(send_response=mock_response)
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
      ]
    )

  assert exit_code == 0
  raw_path = review_run_dir / "raw" / "claude-opus-4-7.round-1.txt"
  parsed_path = review_run_dir / "parsed" / "claude-opus-4-7.round-1.yaml"
  assert raw_path.is_file()
  assert parsed_path.is_file()

  target_manifest = yaml.safe_load(
    (review_run_dir / "target-manifest.yaml").read_text(encoding="utf-8")
  )
  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  summary = yaml.safe_load(
    (review_run_dir / "model-result-summary.yaml").read_text(encoding="utf-8")
  )

  assert target_manifest["target_files"][0]["path"] == str(tmp_target_file)
  model_result = rounds["model_results"][0]
  assert model_result["model_id"] == "claude-opus-4-7"
  assert model_result["raw_path"] == "raw/claude-opus-4-7.round-1.txt"
  assert model_result["parsed_path"] == "parsed/claude-opus-4-7.round-1.yaml"
  assert model_result["parse_status"] == "parsed"
  assert len(model_result["raw_sha256"]) == 64
  assert len(model_result["parsed_sha256"]) == 64

  summary_model = summary["models"][0]
  assert summary_model["model_id"] == "claude-opus-4-7"
  assert summary_model["parse_status"] == "parsed"
  assert summary_model["triage_status"] == "triage_pending"
  assert summary_model["findings_count"] == 1
  assert summary_model["findings_count_by_severity"]["WARN"] == 1


def test_main_updates_review_run_artifacts_on_parse_failure(
  tmp_target_file, tmp_config, tmp_path, monkeypatch
):
  """parse 失敗時も review-run に raw と parse_failed 状態を残す。"""
  monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
  review_run_dir = tmp_path / "review-run"
  mock_cls, _ = _make_mock_provider(send_response="findings: [broken\n")
  with patch("tools.api_providers.run_role.get_provider", return_value=mock_cls):
    exit_code = main(
      [
        "--role", "primary",
        "--target", str(tmp_target_file),
        "--phase", "post_write_verification",
        "--criteria", "観点-1",
        "--config", str(tmp_config),
        "--review-run-dir", str(review_run_dir),
        "--round-id", "round-1",
      ]
    )

  assert exit_code != 0
  raw_path = review_run_dir / "raw" / "claude-opus-4-7.round-1.txt"
  assert raw_path.read_text(encoding="utf-8") == "findings: [broken\n"

  rounds = yaml.safe_load((review_run_dir / "rounds.yaml").read_text(encoding="utf-8"))
  summary = yaml.safe_load(
    (review_run_dir / "model-result-summary.yaml").read_text(encoding="utf-8")
  )
  model_result = rounds["model_results"][0]
  assert model_result["parse_status"] == "parse_failed"
  assert model_result["parsed_path"] is None
  assert model_result["follow_up_action"] == "format_pending"
  summary_model = summary["models"][0]
  assert summary_model["parse_status"] == "parse_failed"
  assert summary_model["triage_status"] == "triage_pending"

```

## FILE: tools/api_providers/tests/test_review_triage.py

```text
# tools/api_providers/tests/test_review_triage.py
# review-run triage 補助コマンドの TDD テスト。

import sys
from datetime import date
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
  sys.path.insert(0, str(_PROJECT_ROOT))

import yaml

from tools.api_providers.review_triage import _is_post_write_target, main


def _write_review_run(tmp_path):
  run_dir = tmp_path / "review-run"
  raw_dir = run_dir / "raw"
  raw_dir.mkdir(parents=True)
  raw_file = raw_dir / "claude-sonnet-4-6.round-1.txt"
  raw_file.write_text("raw\n", encoding="utf-8")
  target = tmp_path / "target.md"
  target.write_text("target\n", encoding="utf-8")
  raw_sha = "0" * 64
  target_sha = "1" * 64
  (run_dir / "target-manifest.yaml").write_text(
    yaml.safe_dump(
      {
        "run_id": run_dir.name,
        "target_files": [
          {
            "path": str(target),
            "sha256": target_sha,
          },
        ],
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  (run_dir / "rounds.yaml").write_text(
    yaml.safe_dump(
      {
        "round_id": "round-1",
        "target_files": [
          {
            "path": str(target),
            "sha256": target_sha,
          },
        ],
        "model_results": [
          {
            "model_id": "claude-sonnet-4-6",
            "provider": "anthropic-api",
            "role": "primary",
            "raw_path": "raw/claude-sonnet-4-6.round-1.txt",
            "raw_sha256": raw_sha,
            "parse_status": "parsed",
          },
          {
            "model_id": "gpt-5.4",
            "provider": "openai-api",
            "role": "adversarial",
            "raw_path": "raw/gpt-5.4.round-1.txt",
            "raw_sha256": "2" * 64,
            "parse_status": "parsed",
          },
        ],
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  (run_dir / "model-result-summary.yaml").write_text(
    yaml.safe_dump(
      {
        "run_id": run_dir.name,
        "models": [
          {
            "model_id": "claude-sonnet-4-6",
            "raw_path": "raw/claude-sonnet-4-6.round-1.txt",
            "parse_status": "parsed",
            "triage_status": "triage_pending",
            "findings_count": 1,
            "must_fix_count": 0,
            "should_fix_count": 0,
            "leave_as_is_count": 0,
            "human_required_count": 1,
          },
          {
            "model_id": "gpt-5.4",
            "raw_path": "raw/gpt-5.4.round-1.txt",
            "parse_status": "parsed",
            "triage_status": "no_findings",
            "findings_count": 0,
            "must_fix_count": 0,
            "should_fix_count": 0,
            "leave_as_is_count": 0,
            "human_required_count": 0,
          },
        ],
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  (run_dir / "triage.yaml").write_text(
    yaml.safe_dump(
      {
        "run_id": run_dir.name,
        "triage_status": "draft",
        "items": [
          {
            "finding_id": "finding-001",
            "source_model": "claude-sonnet-4-6",
            "source_round": "round-1",
            "source_raw_path": "raw/claude-sonnet-4-6.round-1.txt",
            "severity_original": "ERROR",
            "severity_normalized": "ERROR",
            "target_location": "target.md",
            "plain_language_summary": "契約違反の可能性",
            "final_label": None,
            "decision_status": "human_required",
            "decision_actor": None,
            "decision_actor_type": "human",
            "decision_at": None,
            "decision_reason": "仕様に影響する",
            "applied_files": [],
            "superseded_by": None,
          },
        ],
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  return run_dir


def _write_review_run_approval(run_dir, action, finding_ids=None, final_labels=None):
  """review-run 用のユーザ承認レコードを書く"""
  approval_path = run_dir / "approval.json"
  approval_path.write_text(
    yaml.safe_dump(
      {
        "approved_action": action,
        "approved_by": "user",
        "review_run_id": run_dir.name,
        "summary_presented_to_user": True,
        "triage_presented_to_user": True,
        "approved_finding_ids": finding_ids or ["finding-001"],
        "approved_final_labels": final_labels or {"finding-001": "must-fix"},
        "consumed": False,
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  return approval_path


def _write_proxy_decision(run_dir, finding_id="finding-001", final_label="must-fix"):
  """proxy_model 判断レコードと raw を review-run 配下に書く。"""
  decision_dir = run_dir / "proxy-decisions"
  decision_dir.mkdir()
  prompt_path = decision_dir / f"{finding_id}.prompt.md"
  prompt_path.write_text("proxy prompt with options and source raw\n", encoding="utf-8")
  raw_path = decision_dir / f"{finding_id}.raw.txt"
  raw_path.write_text("proxy raw response\n", encoding="utf-8")
  decision_path = decision_dir / f"{finding_id}.decision.yaml"
  decision_path.write_text(
    yaml.safe_dump(
      {
        "finding_id": finding_id,
        "approved_by": "proxy_model",
        "proxy_model_id": "gemini-3.1-pro-preview",
        "decision_prompt_path": f"proxy-decisions/{finding_id}.prompt.md",
        "source_raw_paths": ["raw/claude-sonnet-4-6.round-1.txt"],
        "candidate_options": [
          {
            "id": "option_1",
            "summary": "修正する",
          },
          {
            "id": "option_2",
            "summary": "延期する",
          },
        ],
        "selected_option": "option_1",
        "final_label": final_label,
        "rationale": "契約違反を防ぐため採用する",
        "rejected_options": {
          "option_2": "後続で手戻りが大きい",
        },
        "raw_response_path": f"proxy-decisions/{finding_id}.raw.txt",
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  return decision_path


def _write_proxy_approval(run_dir, action, decision_path, final_label="must-fix"):
  """review-run 用の proxy_model 承認レコードを書く。"""
  approval_path = run_dir / "approval-proxy.yaml"
  approval_path.write_text(
    yaml.safe_dump(
      {
        "approved_action": action,
        "approved_by": "proxy_model",
        "proxy_model_id": "gemini-3.1-pro-preview",
        "review_run_id": run_dir.name,
        "summary_presented_to_user": True,
        "triage_presented_to_user": True,
        "approved_finding_ids": ["finding-001"],
        "approved_final_labels": {"finding-001": final_label},
        "proxy_decisions": {
          "finding-001": str(decision_path.relative_to(run_dir)),
        },
        "consumed": False,
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )
  return approval_path


def test_is_post_write_target_includes_prompt_and_agent_md_candidates():
  """レビュー挙動・agent 挙動を変える md は post-write 対象に含める。"""
  target_paths = [
    "AGENTS.md",
    "intent/INTENT.md",
    "intent/DESIGN_PRINCIPLES.md",
    "templates/todo/TODO_NEXT_SESSION.template.md",
    "templates/review/manual_dogfooding_review_template.md",
    "runtime/prompts/primary_detection/primary_reviewer.prompt.md",
    "runtime/prompts/adversarial_review/adversarial_reviewer.prompt.md",
    "runtime/prompts/judgment/judgment_reviewer.prompt.md",
    "tools/api_providers/prompt_templates/anthropic_review.md",
    "tools/api_providers/prompt_templates/openai_review.md",
    ".reviewcompass/specs/workflow-management/design.md",
  ]

  assert all(_is_post_write_target(path) for path in target_paths)


def test_is_post_write_target_excludes_structured_templates_for_separate_audit():
  """構造化 template は md post-write ではなく別監査へ寄せる。"""
  excluded_paths = [
    "config/api-settings.yaml",
    ".reviewcompass/specs/workflow-management/yaml-audit-spec.yaml",
    "runtime/config/config.yaml.template",
    "runtime/schemas/finding.schema.json",
    "templates/specs/spec.json.template",
  ]

  assert not any(_is_post_write_target(path) for path in excluded_paths)


def test_list_pending_outputs_plain_markdown_with_recommendation(tmp_path, capsys):
  """未判断 item を平易な説明と推薦案付き Markdown で出力する。"""
  run_dir = _write_review_run(tmp_path)

  exit_code = main(["list-pending", "--review-run-dir", str(run_dir)])

  assert exit_code == 0
  output = capsys.readouterr().out
  assert "finding-001" in output
  assert "契約違反の可能性" in output
  assert "must-fix" in output
  assert "仕様・契約" in output


def test_decide_updates_triage_and_model_summary(tmp_path):
  """人判断を triage と model-result-summary に反映する。"""
  run_dir = _write_review_run(tmp_path)
  approval_path = _write_review_run_approval(run_dir, "review_triage_decide")

  exit_code = main(
    [
      "decide",
      "--review-run-dir", str(run_dir),
      "--finding-id", "finding-001",
      "--final-label", "must-fix",
      "--decision-reason", "契約に影響するため修正する",
      "--decision-actor", "human",
      "--approval-record", str(approval_path),
    ]
  )

  assert exit_code == 0
  triage = yaml.safe_load((run_dir / "triage.yaml").read_text(encoding="utf-8"))
  item = triage["items"][0]
  assert item["decision_status"] == "decided"
  assert item["final_label"] == "must-fix"
  assert item["decision_actor"] == "human"
  assert triage["triage_status"] == "decided"

  summary = yaml.safe_load(
    (run_dir / "model-result-summary.yaml").read_text(encoding="utf-8")
  )
  model = summary["models"][0]
  assert model["triage_status"] == "triaged"
  assert model["must_fix_count"] == 1
  assert model["human_required_count"] == 0


def test_decide_blocks_important_finding_without_user_approval(tmp_path, capsys):
  """ERROR / must-fix 相当の重要件は承認レコードなしでは decide できない。"""
  run_dir = _write_review_run(tmp_path)

  exit_code = main(
    [
      "decide",
      "--review-run-dir", str(run_dir),
      "--finding-id", "finding-001",
      "--final-label", "must-fix",
      "--decision-reason", "契約に影響するため修正する",
      "--decision-actor", "codex",
    ]
  )

  assert exit_code == 1
  captured = capsys.readouterr()
  assert "approval" in captured.err
  triage = yaml.safe_load((run_dir / "triage.yaml").read_text(encoding="utf-8"))
  assert triage["items"][0]["decision_status"] == "human_required"


def test_manifest_template_records_review_run_and_unresolved_count(tmp_path, capsys):
  """完了 manifest 雛形を review_run 参照と coverage matrix 付きで出力する。"""
  run_dir = _write_review_run(tmp_path)
  decide_approval = _write_review_run_approval(run_dir, "review_triage_decide")
  main(
    [
      "decide",
      "--review-run-dir", str(run_dir),
      "--finding-id", "finding-001",
      "--final-label", "must-fix",
      "--decision-reason", "契約に影響するため修正する",
      "--decision-actor", "human",
      "--approval-record", str(decide_approval),
    ]
  )
  manifest_approval = _write_review_run_approval(run_dir, "review_run_manifest")

  exit_code = main(
    [
      "manifest-template",
      "--review-run-dir", str(run_dir),
      "--approval-record", str(manifest_approval),
    ]
  )

  assert exit_code == 0
  manifest = yaml.safe_load(capsys.readouterr().out)
  assert manifest["status"] == "completed"
  assert manifest["unresolved_substantive_findings"] == 0
  assert manifest["review_run"]["path"] == str(run_dir)
  assert manifest["review_run"]["summary_path"].endswith("model-result-summary.yaml")
  assert manifest["required_verifiers"] == ["claude-sonnet-4-6", "gpt-5.4"]
  assert [entry["verifier"] for entry in manifest["verifications"]] == [
    "claude-sonnet-4-6",
    "gpt-5.4",
  ]
  assert manifest["verifications"][0]["target_files"] == manifest["target_files"]
  assert manifest["verifications"][0]["target_sha256"] == manifest["target_sha256"]


def test_manifest_template_fails_when_human_required_remains(tmp_path, capsys):
  """未判断 finding が残る場合は manifest 雛形を出力しない。"""
  run_dir = _write_review_run(tmp_path)

  exit_code = main(["manifest-template", "--review-run-dir", str(run_dir)])

  assert exit_code == 1
  captured = capsys.readouterr()
  assert "human_required" in captured.err


def test_write_manifest_creates_file_after_all_decisions(tmp_path):
  """write-manifest は解決済み review-run から manifest ファイルを書く。"""
  run_dir = _write_review_run(tmp_path)
  output_path = tmp_path / "post-write-2026-06-03-999.yaml"
  decide_approval = _write_review_run_approval(run_dir, "review_triage_decide")
  main(
    [
      "decide",
      "--review-run-dir", str(run_dir),
      "--finding-id", "finding-001",
      "--final-label", "must-fix",
      "--decision-reason", "契約に影響するため修正する",
      "--decision-actor", "human",
      "--approval-record", str(decide_approval),
    ]
  )
  manifest_approval = _write_review_run_approval(run_dir, "review_run_manifest")

  exit_code = main(
    [
      "write-manifest",
      "--review-run-dir", str(run_dir),
      "--out", str(output_path),
      "--approval-record", str(manifest_approval),
    ]
  )

  assert exit_code == 0
  manifest = yaml.safe_load(output_path.read_text(encoding="utf-8"))
  assert manifest["status"] == "completed"
  assert manifest["verifications"][1]["verifier"] == "gpt-5.4"


def test_write_manifest_auto_chooses_next_post_write_name(tmp_path, monkeypatch, capsys):
  """--out auto は .reviewcompass/post-write-verification の次番号へ manifest を書く。"""
  cwd = tmp_path / "repo"
  cwd.mkdir()
  monkeypatch.chdir(cwd)
  existing_dir = cwd / ".reviewcompass" / "post-write-verification"
  existing_dir.mkdir(parents=True)
  today = date.today().isoformat()
  (existing_dir / f"post-write-{today}-001.yaml").write_text(
    "status: completed\n",
    encoding="utf-8",
  )
  run_dir = _write_review_run(cwd)
  decide_approval = _write_review_run_approval(run_dir, "review_triage_decide")
  main(
    [
      "decide",
      "--review-run-dir", str(run_dir),
      "--finding-id", "finding-001",
      "--final-label", "must-fix",
      "--decision-reason", "契約に影響するため修正する",
      "--decision-actor", "human",
      "--approval-record", str(decide_approval),
    ]
  )
  manifest_approval = _write_review_run_approval(run_dir, "review_run_manifest")

  exit_code = main(
    [
      "write-manifest",
      "--review-run-dir", str(run_dir),
      "--out", "auto",
      "--approval-record", str(manifest_approval),
    ]
  )

  assert exit_code == 0
  output = capsys.readouterr().out
  created_path = existing_dir / f"post-write-{today}-002.yaml"
  assert str(created_path) in output
  assert created_path.is_file()
  manifest = yaml.safe_load(created_path.read_text(encoding="utf-8"))
  assert manifest["status"] == "completed"


def test_write_manifest_blocks_important_decisions_without_approval(tmp_path, capsys):
  """重要件を含む review-run は manifest 生成時にも承認レコードを要求する。"""
  run_dir = _write_review_run(tmp_path)
  triage = yaml.safe_load((run_dir / "triage.yaml").read_text(encoding="utf-8"))
  item = triage["items"][0]
  item["decision_status"] = "decided"
  item["final_label"] = "must-fix"
  item["decision_actor"] = "codex"
  item["decision_actor_type"] = "human"
  (run_dir / "triage.yaml").write_text(
    yaml.safe_dump(triage, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  output_path = tmp_path / "post-write-2026-06-03-999.yaml"

  exit_code = main(
    [
      "write-manifest",
      "--review-run-dir", str(run_dir),
      "--out", str(output_path),
    ]
  )

  assert exit_code == 1
  assert not output_path.exists()
  captured = capsys.readouterr()
  assert "approval" in captured.err


def test_assert_apply_fixes_ready_blocks_when_human_required_remains(tmp_path, capsys):
  """未判断 finding が残る間は修正適用へ進めない。"""
  run_dir = _write_review_run(tmp_path)

  exit_code = main(
    [
      "assert-apply-fixes-ready",
      "--review-run-dir", str(run_dir),
    ]
  )

  assert exit_code == 1
  captured = capsys.readouterr()
  assert "human_required" in captured.err


def test_assert_apply_fixes_ready_requires_user_approval_for_fix_labels(tmp_path, capsys):
  """must-fix / should-fix の修正適用は利用者承認なしでは進めない。"""
  run_dir = _write_review_run(tmp_path)
  triage = yaml.safe_load((run_dir / "triage.yaml").read_text(encoding="utf-8"))
  item = triage["items"][0]
  item["decision_status"] = "decided"
  item["final_label"] = "must-fix"
  item["decision_actor"] = "human"
  item["decision_actor_type"] = "human"
  (run_dir / "triage.yaml").write_text(
    yaml.safe_dump(triage, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )

  exit_code = main(
    [
      "assert-apply-fixes-ready",
      "--review-run-dir", str(run_dir),
    ]
  )

  assert exit_code == 1
  captured = capsys.readouterr()
  assert "approval" in captured.err


def test_assert_apply_fixes_ready_passes_after_user_approval(tmp_path):
  """修正対象 finding が利用者承認済みなら修正適用へ進める。"""
  run_dir = _write_review_run(tmp_path)
  triage = yaml.safe_load((run_dir / "triage.yaml").read_text(encoding="utf-8"))
  item = triage["items"][0]
  item["decision_status"] = "decided"
  item["final_label"] = "must-fix"
  item["decision_actor"] = "human"
  item["decision_actor_type"] = "human"
  (run_dir / "triage.yaml").write_text(
    yaml.safe_dump(triage, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  approval_path = _write_review_run_approval(
    run_dir,
    "review_run_apply_fixes",
    finding_ids=["finding-001"],
    final_labels={"finding-001": "must-fix"},
  )

  exit_code = main(
    [
      "assert-apply-fixes-ready",
      "--review-run-dir", str(run_dir),
      "--approval-record", str(approval_path),
    ]
  )

  assert exit_code == 0


def test_assert_apply_fixes_ready_passes_after_proxy_model_approval(tmp_path):
  """proxy_model の判断証跡が揃っていれば修正適用へ進める。"""
  run_dir = _write_review_run(tmp_path)
  triage = yaml.safe_load((run_dir / "triage.yaml").read_text(encoding="utf-8"))
  item = triage["items"][0]
  item["decision_status"] = "decided"
  item["final_label"] = "must-fix"
  item["decision_actor"] = "gemini-3.1-pro-preview"
  item["decision_actor_type"] = "proxy_model"
  (run_dir / "triage.yaml").write_text(
    yaml.safe_dump(triage, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  decision_path = _write_proxy_decision(run_dir)
  approval_path = _write_proxy_approval(
    run_dir,
    "review_run_apply_fixes",
    decision_path,
  )

  exit_code = main(
    [
      "assert-apply-fixes-ready",
      "--review-run-dir", str(run_dir),
      "--approval-record", str(approval_path),
    ]
  )

  assert exit_code == 0


def test_assert_apply_fixes_ready_blocks_proxy_approval_without_raw(tmp_path, capsys):
  """proxy decision の raw response が欠ける場合は fail-closed する。"""
  run_dir = _write_review_run(tmp_path)
  triage = yaml.safe_load((run_dir / "triage.yaml").read_text(encoding="utf-8"))
  item = triage["items"][0]
  item["decision_status"] = "decided"
  item["final_label"] = "must-fix"
  item["decision_actor"] = "gemini-3.1-pro-preview"
  item["decision_actor_type"] = "proxy_model"
  (run_dir / "triage.yaml").write_text(
    yaml.safe_dump(triage, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  decision_path = _write_proxy_decision(run_dir)
  (run_dir / "proxy-decisions" / "finding-001.raw.txt").unlink()
  approval_path = _write_proxy_approval(
    run_dir,
    "review_run_apply_fixes",
    decision_path,
  )

  exit_code = main(
    [
      "assert-apply-fixes-ready",
      "--review-run-dir", str(run_dir),
      "--approval-record", str(approval_path),
    ]
  )

  assert exit_code == 1
  captured = capsys.readouterr()
  assert "raw_response_path" in captured.err


def test_assert_apply_fixes_ready_blocks_proxy_approval_without_options(tmp_path, capsys):
  """proxy に提示した候補案セットが欠ける場合は fail-closed する。"""
  run_dir = _write_review_run(tmp_path)
  triage = yaml.safe_load((run_dir / "triage.yaml").read_text(encoding="utf-8"))
  item = triage["items"][0]
  item["decision_status"] = "decided"
  item["final_label"] = "must-fix"
  item["decision_actor"] = "gemini-3.1-pro-preview"
  item["decision_actor_type"] = "proxy_model"
  (run_dir / "triage.yaml").write_text(
    yaml.safe_dump(triage, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  decision_path = _write_proxy_decision(run_dir)
  decision = yaml.safe_load(decision_path.read_text(encoding="utf-8"))
  decision.pop("candidate_options")
  decision_path.write_text(
    yaml.safe_dump(decision, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  approval_path = _write_proxy_approval(
    run_dir,
    "review_run_apply_fixes",
    decision_path,
  )

  exit_code = main(
    [
      "assert-apply-fixes-ready",
      "--review-run-dir", str(run_dir),
      "--approval-record", str(approval_path),
    ]
  )

  assert exit_code == 1
  captured = capsys.readouterr()
  assert "candidate_options" in captured.err

```

## FILE: .reviewcompass/specs/workflow-management/implementation-drafting.md

```text
# workflow-management implementation drafting 棚卸し

## 目的

workflow-management implementation.drafting の現時点の実装状況を、後続の triad-review と利用者判断で追えるようにする。

今回のターゲットは、自律・並列実行をできるだけ人の承認なしで進め、事後に履歴を確認できるようにすることである。不可逆操作である commit、push、spec.json 更新、フェーズ移行は引き続き人間の明示承認を要求する。

## 実装済み

### 自律・並列実行計画ガード

`tools/check-workflow-action.py autonomous-plan <plan.yaml>` を実装済み。

検査内容：

- `mode: autonomous_parallel` と `run_id`
- 人間または `proxy_model` の承認記録
- レビュー結果サマリと三段階トリアージの提示済みフラグ
- task ごとの `source_finding_ids`、担当、許可パス、期待テスト、停止条件
- 別スレッドまたはサブ担当の `separate_worktree`
- 依存関係のない並列 task の `allowed_paths` 衝突
- 統合ゲート
- 生成物分類
- 履歴台帳設定

### 自律・並列実行計画テンプレート

`tools/check-workflow-action.py autonomous-plan-template --run-id <run-id> --out <plan.yaml>` を実装済み。

生成される YAML は `autonomous-plan` の必須フィールドを満たし、そのまま検査可能である。実作業では、生成後に `tasks[]` の `source_finding_ids`、`allowed_paths`、`expected_tests` を実対象へ差し替える。

### 自律・並列実行履歴台帳

`autonomous-plan` 実行時に `docs/logs/autonomous-parallel/<run-id>.yaml` へ履歴台帳を書き出す。

台帳には、`run_id`、verdict、reasons、task IDs、承認根拠、統合ゲート、出力分類、current_state を記録する。

### 統合結果追記

`tools/check-workflow-action.py autonomous-plan-record-integration --ledger <ledger.yaml> --status <status> --tests "<tests>" --decision "<decision>"` を実装済み。

統合後に既存台帳へ `integration_result` を追記し、次を後から確認できる。

- 統合状態：`completed`、`blocked`、`rejected`
- 実行したテストまたは未実行理由
- メインセッション LLM の統合判断

### 正本仕様

`docs/operations/WORKFLOW_PRECHECK.md` に、次のサブコマンド仕様を追記済み。

- `autonomous-plan`
- `autonomous-plan-template`
- `autonomous-plan-record-integration`

## 未充足

workflow-management 全体の T-001〜T-011 は、まだ一括完了ではない。

現時点で特に残る事項：

- T-001〜T-003：`stages/` 配下の 9 ファイル体制と stage schema の実装は未完了部分がある。
- T-005：front-matter checker の独立モジュール化は未完了。
- T-006：不可逆操作ゲートは commit/push/spec-set を中心に実装済みだが、設計上の 4 種類すべてを専用モジュールへ分離する作業は未完了。
- T-007：reopen resolver の専用モジュール化は未完了。ただし `reopen-start` と `next` による進行中ファイル処理は部分実装済み。
- T-008：in-progress manager の専用モジュール化は未完了。ただし `next` は in-progress を優先して読める。
- T-009〜T-011：運用文書、規律変更接合面、統合テスト全体は未完了事項が残る。

今回の実装は、T-004 の検査スクリプト本体と、自律・並列実行を安全に始めて履歴を残すための追加ガードに集中している。

## 検証

実行済み：

- `python3 -m unittest tests.tools.test_check_workflow_action -v`
- `python3 -m pytest tests/tools/test_session_record_contract.py -q`
- `python3 -m pytest tests/tools/test_workflow_management_implementation_drafting.py -q`
- `python3 tools/check-workflow-action.py next --json`

結果：

- `tests.tools.test_check_workflow_action` は通過
- `tests/tools/test_session_record_contract.py` は通過
- `tests/tools/test_workflow_management_implementation_drafting.py` は通過予定の棚卸し検査
- `next` は `workflow-management / implementation / drafting` を返す

## drafting 完了判断

現時点では、workflow-management implementation.drafting の下書き成果物として、本棚卸しを作成した段階である。

推薦判断：

1. 本棚卸しをもとに implementation.drafting の triad-review へ進める。
2. triad-review では、T-004 周辺の実装を重点的に確認し、T-001〜T-011 全体の未充足を drafting 完了の阻害要因とするか、後続 implementation task として扱うかを判定する。
3. spec.json の `workflow-management.implementation.drafting=true` 更新は、人間の明示承認後に行う。

```

## FILE: .reviewcompass/specs/workflow-management/reviews/2026-06-04-implementation-triad-review-prep.md

```text
---
spec: workflow-management
phase: implementation
stage: triad-review-prep
date: 2026-06-04
author:
  identity: main session LLM
  role: preparer
review_mode: api_mediated_independent_3way
---

# workflow-management implementation triad-review 準備

## 目的

workflow-management implementation.drafting の完了を受け、次段の triad-review で
レビュー対象の取りこぼしを防ぎ、各モデルの raw response から main session LLM が
三段階トリアージを行えるようにする。

## レビュー対象

- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/design.md`
- `.reviewcompass/specs/workflow-management/tasks.md`
- `.reviewcompass/specs/workflow-management/spec.json`
- `tools/check-workflow-action.py`
- `tools/api_providers/run_review.py`
- `tools/api_providers/run_role.py`
- `tools/api_providers/review_triage.py`
- `tests/tools/test_check_workflow_action.py`
- `tests/tools/test_workflow_management_implementation_drafting.py`
- `tools/api_providers/tests/test_run_review.py`
- `tools/api_providers/tests/test_run_role.py`
- `tools/api_providers/tests/test_review_triage.py`
- `.reviewcompass/specs/workflow-management/implementation-drafting.md`
- `docs/operations/WORKFLOW_PRECHECK.md`
- `docs/operations/SESSION_WORKFLOW_GUIDE.md`
- `docs/notes/2026-06-04-proxy-review-parallel-implementation-plan.md`

## 証跡パス

今回の review-run ID は `2026-06-04-workflow-management-implementation-review-run` とする。
成果物は次を予定する。

- `.reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/target-manifest.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/rounds.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/model-result-summary.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/triage.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/review_summary.md`
- `docs/logs/autonomous-parallel/2026-06-04-workflow-management-implementation-review-run.yaml`

## 必須規律

- 各モデルの返答は structured YAML だけに依存せず、raw response として保存する。
- main session LLM は raw response を読み、三段階トリアージを作成する。
- 重要所見は、修正案・判断理由・採用案を示し、承認または proxy decision の記録後に実装へ進む。
- proxy decision を使う場合も、人間の代行判断として扱い、判断理由と候補案を後から追える形で残す。
- レビュー結果の要約は、モデル別所見、三段階トリアージ、重要所見の扱いをまとめて提示する。

## レビュー観点

- フェーズ内ワークフロー手順が正本と一致しているか。
- 自律・並列実行で、人間ゲート、proxy decision、コミット承認の境界が曖昧になっていないか。
- サブ担当 LLM の成果物、ログ、統合記録を後から追えるか。
- 機械判定で取りこぼしや順序違反を検出できるか。
- テストが規律違反を実装前に検出できるか。

## 推薦手順

1. 上記レビュー対象をプロンプトに含め、独立3モデルへ API 経由で投げる。
2. 各モデルの raw response を保存する。
3. main session LLM が raw response を読み、重要・推奨・保留の三段階トリアージにまとめる。
4. 重要所見について、平易な説明、候補案、推薦案を提示する。
5. 承認または proxy decision の記録後に、必要な実装作業を切り出す。
6. 並列化できる実装作業は、統合者を main session LLM として分担可能性を判定する。

## 次アクション

`workflow-management / implementation / triad-review` を実行する。実行後はこの準備メモを
照合表として使い、レビュー対象の欠落、raw response の欠落、三段階トリアージの欠落、
重要所見ゲートの欠落がないか確認する。

```

## FILE: docs/operations/WORKFLOW_PRECHECK.md

```text
# WORKFLOW_PRECHECK：ワークフロー事前検査スクリプトの正本仕様

最終更新：2026-06-04（自律・並列実行計画 `autonomous-plan` と履歴台帳ガードを追加）／2026-06-03（commit 時 post-write-verification 監査と audit-commit 追加、commit 承認レコードガード追加。Codex adapter migration：段階 3 hook 記述を実行環境 adapter 方針へ整理）／2026-05-25 セッション 24（新設、補助層 C 段階 2 の仕様確定）
位置付け：運用文書（`docs/operations/` 配下）、計画書 §5.8 補助層 C の段階 2 の正本仕様

本文書は計画書 §5.8 補助層 C 共存モデルの **段階 2（外部スクリプトによる機械的判定）** の仕様を定める。段階 2 の実装は本文書を入力として進める。仕様の変更には利用者明示承認が必要（規律 §0.2 計画書方針変更に準じる）。

## 採用承認の出典

- 「共存モデルの採用」（2026-05-25 セッション 24、補助層 C 共存モデルの採用、計画書方針変更）
- 「A から順に進める」（2026-05-25 セッション 24、文書反映の着手順序指示）
- 「次に進む」（2026-05-25 セッション 24、段階 2 仕様策定への着手）
- 「範囲案 2」（2026-05-25 セッション 24、対象範囲を spec.json ＋ commit ＋ push に確定）
- 「論点 A は、実装テスト段階でも効果測定やデバッグで必要になるのではないか？」（2026-05-25 セッション 24、実行ログ取得を MVP 必須として位置付け）
- 「論点 B は、渡す」（2026-05-25 セッション 24、`--rationale` 引数の採用）
- 「論点 C は別文書」（2026-05-25 セッション 24、本文書の独立新設）
- 「ア」（2026-05-25 セッション 24、派生論点の中間案採用と本文書起草の承認）

## 1. 概要と位置付け

### 1.1 何のための仕様か

ワークフロー事前検査スクリプト（以降「本スクリプト」）は、私（LLM、メインセッション）が ReviewCompass の開発作業を進めるとき、不可逆操作（spec.json 修正・git commit・git push）の **直前に呼び出して、当該操作が現在のワークフロー状態と整合するかを機械的に判定する** ためのコマンドラインツール。

### 1.2 共存モデル全体での位置付け

計画書 §5.8 補助層 C 共存モデルは 3 段階の役割分担で構成される：

- **段階 1（LLM 規律、恒久層）**：これから何をするかを応答内で明示、本スクリプトを呼び、出力を解釈して次の行動を決める
- **段階 2（外部スクリプト、本仕様の対象）**：spec.json／git／規律ファイル／持ち越し所見を読み、引数の処理が現状で適切かを判定して返す
- **段階 3（実行環境別 hook adapter）**：ツール呼び出し（Edit／Write／Bash 等）の前に段階 2 を自動で走らせ、逸脱なら遮断

本スクリプトは段階 2 の本体。段階 1 と段階 3 の両方から呼ばれ得る。

### 1.3 関連文書

- 計画書 §5.8 補助層 C（採用方針の正本）
- 議論メモ：[docs/notes/2026-05-25-workflow-pre-check-and-discipline-consolidation.md](../notes/2026-05-25-workflow-pre-check-and-discipline-consolidation.md)（議論経緯）
- TODO §3 セクション D（残作業の管理）
- spec.json 正本スキーマ：計画書 §5.24
- 運営ガイド：[docs/operations/SESSION_WORKFLOW_GUIDE.md](SESSION_WORKFLOW_GUIDE.md)

## 2. 共存モデルにおける段階 2 の役割

### 2.1 単一責任

段階 2 は **判定のみ** を行う。承認や合意の取得、状態の書き換え、エスカレーションは行わない。

具体的に：

- **行う**：状態を読み、判定して結果を返す、判定履歴をログに残す
- **行わない**：spec.json の書き換え（それは段階 1 が承認後に行う）、利用者への問い合わせ（それは段階 1 の役割）、強制遮断（それは段階 3 のフック設定の役割）

### 2.2 段階間のインターフェース

``\`
段階 1（LLM）：意図宣言
  ↓ 引数を渡してスクリプトを呼び出す
段階 2（本スクリプト）
  ↓ 終了コード ＋ 標準出力（人間可読 or JSON）
段階 1（LLM）：出力を解釈して処理続行可否を判断
``\`

段階 3 導入後は、段階 1 が呼び忘れた場合に各実行環境の hook adapter が同じスクリプトを自動発動する。

## 3. 適用範囲（範囲案 2）

### 3.1 対象とする処理

3 つの不可逆操作を対象とする：

1. **spec.json の `workflow_state` 修正**：機能単位 spec.json の段の真偽値を変更する操作
2. **git commit**：作業ツリーの変更を確定する操作
3. **git push**：ローカルコミットを `origin` に送る操作

### 3.2 適用範囲外（将来拡張の候補）

範囲案 2 では次は対象としない（範囲案 3 への拡張時に検討）：

- 仕様文書ファイル（`design.md`／`requirements.md`／`tasks.md`／`implementation.md` 等）の編集前検査
- 計画書（`docs/plan/`）の編集前検査
- 応答テキストのみの判断（例：「完了」「承認済」の断定）は段階 2 では機械判定不可、段階 1 規律の責務

### 3.3 拡張時の責務

将来の範囲案 3 への拡張は、本文書を改訂して仕様を追加する（規律 §0.2 計画書方針変更に該当、利用者明示承認必須）。

## 4. サブコマンド体系

3 つのサブコマンドを持つ：

``\`
check-workflow-action.py spec-set <feature> <phase> <stage> <new-value> [--rationale "<理由>"]
check-workflow-action.py commit --rationale "<理由>"
check-workflow-action.py push --rationale "<理由>"
check-workflow-action.py autonomous-plan <plan.yaml>
check-workflow-action.py autonomous-plan-template --run-id <run-id> --out <plan.yaml>
check-workflow-action.py autonomous-plan-record-integration --ledger <ledger.yaml> --status <status> --tests "<tests>" --decision "<decision>"
check-workflow-action.py audit-commit <commit-ish>
guarded-git-commit.py -m "<commit message>" --rationale "<理由>"
``\`

共通オプション：

- `--json`：機械可読の JSON 出力に切り替え（未指定時は人間可読）
- `--log-path <path>`：ログ書き出し先の上書き（既定 `docs/logs/workflow-precheck.log`）
- `--help`：使い方表示

## 5. 引数仕様

### 5.1 `spec-set` サブコマンド

``\`
check-workflow-action.py spec-set <feature> <phase> <stage> <new-value> [--rationale "<理由>"]
``\`

引数：

| 引数 | 必須 | 値の例 | 説明 |
|---|---|---|---|
| `<feature>` | 必須 | `foundation`／`runtime`／…／`conformance-evaluation` | 対象機能名、`stages/feature-dependency.yaml` の `features` キーと一致 |
| `<phase>` | 必須 | `intent`／`feature-partitioning`／`requirements`／`design`／`tasks`／`implementation` | 対象フェーズ |
| `<stage>` | 必須 | `drafting`／`triad-review`／`review-wave`／`alignment`／`approval` 等 | 対象段、フェーズにより値が異なる（計画書 §5.5） |
| `<new-value>` | 必須 | `true`／`false` | 設定したい新しい真偽値 |
| `--rationale` | 任意 | 自由文字列 | この変更を行う理由（ログ記録用、判定には影響しない） |

`--rationale` を任意とする理由：`spec-set` は機械的整合判定が中心、理由を渡しても判定そのものは変わらない。ただしログ記録のため渡すことを推奨。

### 5.2 `commit` サブコマンド

``\`
check-workflow-action.py commit --rationale "<理由>"
``\`

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `--rationale` | **必須** | このコミットを行う理由、利用者承認の発言出典を含めることを推奨 |

`--rationale` を必須とする理由：commit は不可逆操作のため、なぜ実行するかの根拠を残すべき。

commit は利用者の職掌範囲であり、LLM は利用者の明示指示なしに実行しない。機械判定では、`--rationale` に加えて `.reviewcompass/approvals/commit-approval.json` のユーザ承認レコードを必須とする。

承認レコードの最小形：

``\`json
{
  "approved_action": "commit",
  "approved_by": "user",
  "approved_at": "2026-06-03T00:00:00+09:00",
  "rationale": "利用者がコミットを明示承認",
  "target_files": ["path/to/file.md"],
  "expires_after_commit": true,
  "consumed": false
}
``\`

`target_files` は staged ファイルの許可範囲。`"*"` を含む場合は全 staged ファイルを許可する。`consumed: true` は消費済みとして逸脱扱いにする。

実行時は直接 `git commit` ではなく、次のラッパーを使う：

``\`
tools/guarded-git-commit.py -m "<commit message>" --rationale "<理由>"
``\`

このラッパーは `check-workflow-action.py commit` を先に実行し、exit 2 なら遮断する。exit 1（WARN）は既定では停止し、利用者判断で続行する場合だけ `--allow-warn` を付ける。commit 成功後、`expires_after_commit` が false でない承認レコードは `consumed: true` に更新する。

限界：repo 内スクリプトだけでは「承認レコードを誰が作成したか」を完全には保証できない。強い保証には、段階 3 hook adapter または実行環境側で、承認レコードの発行・更新を利用者操作に限定する必要がある。

また、commit 対象の staged ファイルに post-write-verification 対象（`docs/operations/`、`TODO_NEXT_SESSION.md` 等）が含まれる場合、対象ファイル群の現在 sha256 を覆う completed manifest を必須とする。manifest がない、sha256 が一致しない、coverage matrix が不足する、未解決本質的指摘がある場合は exit 2 とする。

### 5.3 `push` サブコマンド

``\`
check-workflow-action.py push --rationale "<理由>"
``\`

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `--rationale` | **必須** | この push を行う理由、利用者承認の発言出典を含めることを推奨 |

`--rationale` を必須とする理由：push は origin に影響する不可逆操作、なぜ実行するかの根拠を残すべき。

### 5.4 `audit-commit` サブコマンド

``\`
check-workflow-action.py audit-commit <commit-ish>
``\`

指定 commit の変更ファイルを読み、post-write-verification 対象が含まれる場合に completed manifest が存在するかを遡及監査する。`<commit-ish>` は `HEAD` や commit hash を指定できる。root commit も監査対象に含める。

commit 済みの見落とし検出用であり、通常は commit 直前の `commit` precheck が主経路。`audit-commit` は commit 内の対象ファイル内容を `git show <commit-ish>:<path>` で読み、その sha256 と現在リポジトリ内に存在する manifest の `target_sha256` を照合する。

この監査は「対象 commit 時点に manifest が存在したか」を証明する時点監査ではなく、「現在のリポジトリ状態で、その commit 内容に対応する検証記録が存在するか」を確認する是正監査である。したがって、見落とし後に追加した manifest による是正完了を認める。

`<commit-ish>` が解決できない場合は逸脱（exit 2）とする。

### 5.5 `autonomous-plan` サブコマンド

``\`
check-workflow-action.py autonomous-plan <plan.yaml>
``\`

自律・並列モードで実装作業を始める前に、実行計画 YAML を検査する。目的は、並列化できる作業だけを切り出し、重要判断の停止条件と統合時の確認点を明示し、後から判断履歴を追える台帳を残すこと。

計画 YAML は最低限、次を持つ。

- `mode: autonomous_parallel`
- `run_id`
- `authorization`：`approved_by`、`approval_record_path`、`summary_presented_to_user`、`triage_presented_to_user`
- `tasks[]`：`task_id`、`source_finding_ids`、`assignee`、`allowed_paths`、`depends_on`、`expected_tests`、`stop_conditions`
- `integration_gate`：メインセッション確認、差分範囲確認、テスト確認、判断根拠確認
- `outputs_policy`：実装差分、検証結果、判断根拠、作業ノイズの扱い
- `history`：`ledger_path`、`record_task_assignments`、`record_decision_basis`、`record_integration_result`、`retention`

`history.ledger_path` は `docs/logs/autonomous-parallel/` 配下とする。`autonomous-plan` は検査結果をこの台帳へ YAML として書き出し、後から `run_id`、task ID、承認根拠、統合ゲート、出力分類、判定結果を確認できるようにする。

### 5.6 `autonomous-plan-template` サブコマンド

``\`
check-workflow-action.py autonomous-plan-template --run-id <run-id> --out <plan.yaml>
``\`

自律・並列モード実行計画の最小テンプレートを生成する。生成物は `autonomous-plan` の必須フィールドをすべて含み、そのまま検査可能である。実作業では、生成後に `tasks[]` の `source_finding_ids`、`allowed_paths`、`expected_tests` を実対象へ差し替える。

### 5.7 `autonomous-plan-record-integration` サブコマンド

``\`
check-workflow-action.py autonomous-plan-record-integration --ledger <ledger.yaml> --status <status> --tests "<tests>" --decision "<decision>"
``\`

自律・並列モードの統合後に、既存の履歴台帳へ `integration_result` を追記する。`status` は `completed`、`blocked`、`rejected` のいずれか。`tests` には実行したテストまたは未実行理由、`decision` にはメインセッション LLM による統合判断の要約を記録する。

## 6. 判定ロジック

### 6.1 `spec-set` の判定

対象機能の spec.json（`.reviewcompass/specs/<feature>/spec.json`）を読み、次を機械判定：

#### `<new-value>` が `true` の場合（段を通過済みにする）

- **段の依存チェック**：同フェーズ内で当該段より前の段がすべて `true` か
  - 例：`requirements approval true` → `requirements alignment` が `true` か
  - 例：`design drafting true` → `requirements approval` が `true` か
- **フェーズの依存チェック**：上流フェーズの最終段（`approval`）が `true` か
  - 例：`design drafting true` → `requirements approval` が `true`、`feature-partitioning approval` が `true`、`intent approval` が `true`
- **機能横断段の整合**：`intent`／`feature-partitioning` は全機能で同じ値を持つべき（計画書 §5.24.4）。当該機能の値だけを変えると不整合
- **承認発言の有無は判定しない**：それは段階 1 規律の責務

#### `<new-value>` が `false` の場合（reopen に相当）

- 一般に許容（reopen 手続きの一部）
- ただし当該段が `true` だった場合は警告：「reopen を実施しています、reopen 手続き（計画書 §5.6）に従っていますか」

### 6.2 `commit` の判定

`git status` と `git diff --cached` を読み、次を機械判定：

- **ユーザ承認レコードの確認**：`.reviewcompass/approvals/commit-approval.json` を読み、`approved_action=commit`、`approved_by=user`、未消費、かつ staged ファイルが `target_files` の範囲内であることを確認
  - レコードなし、形式不正、消費済み、承認対象外ファイルがある場合：逸脱（exit 2）、commit を遮断推奨
- **post-write-verification 対象の完了確認**：staged ファイルに post-write-verification 対象が含まれる場合、対象ファイル群と現在 sha256 を覆う completed manifest があることを確認
  - manifest なし、sha256 不一致、coverage matrix 不足、未解決本質的指摘ありの場合：逸脱（exit 2）、commit を遮断推奨
- **持ち越し所見の確認**：`learning/workflow/carry-forward-register/reviewcompass-import.yaml` を読み、未消化所見の件数を出力
  - 未消化所見が 1 件以上ある場合：警告（exit 1）、commit は可能だが要注意
  - 0 件の場合：OK（exit 0）
- **対象ファイルの分類**：staged されたファイルを次の 3 群に分類して出力
  - 通常変更：仕様文書（`*.md`）、ソースコード（`*.py` 等）
  - 要注意変更：`spec.json`、`docs/plan/` 配下、計画書、規律ファイル
  - 危険変更：`.git/` 内、`secrets`／`credentials` を含むファイル名
- **要注意変更がある場合**：警告（exit 1）、根拠の確認を促す
- **危険変更がある場合**：逸脱（exit 2）、commit を遮断推奨

### 6.3 `push` の判定

`git status` と `git log` を読み、次を機械判定：

- **作業ツリーの clean 性**：未コミット変更がある場合は逸脱（exit 2）
- **ローカル先行コミット数**：`origin/main` から進んでいるコミット数を出力
- **直近 5 コミットの題名要約**：利用者が push 前に確認しやすい形で出力
- **push 先**：`origin/main` 以外への push が要求されていれば警告（exit 1）

### 6.4 `audit-commit` の判定

`git diff-tree --root --no-commit-id --name-only -r <commit-ish>` で指定 commit の変更ファイルを取得し、post-write-verification 対象だけを抽出する。

- 対象なし：OK（exit 0）
- 対象あり、かつ commit 内ファイル内容 sha256 を覆う completed manifest がある：OK（exit 0）
- 対象あり、manifest がない／sha256 不一致／coverage matrix 不足／未解決本質的指摘あり：逸脱（exit 2）
- `<commit-ish>` が解決できない：逸脱（exit 2）

### 6.5 `autonomous-plan` の判定

実行計画 YAML を読み、次を fail-closed で判定する。

- `mode` が `autonomous_parallel` である
- `run_id` がある
- `authorization.approved_by` が `user` または `proxy_model` である
- レビュー結果サマリと三段階トリアージが提示済みである
- 各 task に `source_finding_ids`、`allowed_paths`、`expected_tests`、`important_decision_requires_approval` 停止条件がある
- 別スレッドまたはサブ担当の task は `assignee.worktree_policy: separate_worktree` である
- 依存関係のない並列 task 同士で `allowed_paths` が衝突しない
- `integration_gate` の 4 条件がすべて `true` である
- `outputs_policy.work_noise` が `exclude` であり、作業ノイズを本線 repo に取り込まない
- `history` が台帳パス、タスク割当記録、判断根拠記録、統合結果記録、保存方針を持つ

検査に通った場合も、通らなかった場合も、`history.ledger_path` が妥当なら台帳を生成する。これにより、自律実行の開始可否、止まった理由、並列 task の境界、統合時の確認点を後から追跡できる。

## 7. 出力形式

### 7.1 終了コード体系

- `0`：問題なし、処理続行可
- `1`：警告あり、呼び出し側の判断で続行可
- `2`：逸脱検出、呼び出し側が遮断推奨

### 7.2 人間可読出力（既定）

標準出力に次の構造：

``\`
[VERDICT] OK / WARN / DEVIATION（exit <code>）
[ACTION] <サブコマンド名 ＋ 引数の要約>
[REASON]
  - <理由 1>
  - <理由 2>
[CURRENT STATE]
  <現状の要約、複数行可>
``\`

例（spec-set 逸脱の場合）：

``\`
[VERDICT] DEVIATION（exit 2）
[ACTION] spec-set foundation requirements approval true
[REASON]
  - workflow_state.requirements.alignment が false です（approval の前提が満たされていません）
[CURRENT STATE]
  foundation.requirements:
    drafting: true
    triad-review: true
    review-wave: true
    alignment: false  ← 問題箇所
    approval: false
``\`

### 7.3 JSON 出力（`--json` 指定時）

機械処理向けの構造化出力。段階 3 フック導入時に使う想定：

``\`json
{
  "verdict": "DEVIATION",
  "exit_code": 2,
  "action": {
    "subcommand": "spec-set",
    "args": {
      "feature": "foundation",
      "phase": "requirements",
      "stage": "approval",
      "new_value": true,
      "rationale": "..."
    }
  },
  "reasons": [
    "workflow_state.requirements.alignment が false です（approval の前提が満たされていません）"
  ],
  "current_state": {
    "foundation": {
      "requirements": {
        "drafting": true,
        "triad-review": true,
        "review-wave": true,
        "alignment": false,
        "approval": false
      }
    }
  }
}
``\`

## 8. ログ取得（MVP 必須）

### 8.1 書式

JSON Lines 形式（1 行 ＝ 1 判定）。`--json` 出力と同じ構造に `timestamp` を追加：

``\`json
{"timestamp":"2026-05-25T15:30:00+09:00","action":{"subcommand":"spec-set","args":{...,"rationale":"..."}},"verdict":"OK","exit_code":0,"reasons":[],"current_state":{...}}
``\`

### 8.2 配置

- 既定パス：`docs/logs/workflow-precheck.log`
- `--log-path` で上書き可（テスト時の隔離用）

### 8.3 取得方針（MVP）

- 毎回の判定を 1 行追記
- ローテーションは MVP では実装しない（将来検討、計画書 §5.8 第 5 層「処理表面積の抑制」と整合）
- 削除は手動操作のみ

### 8.4 ログの活用先

- テスト失敗時のデバッグ
- 規律遵守率の事後計測（議論メモ §「派生論点」、self-improvement の効果測定指標と接続）
- 誤判定の事後追跡

## 9. テスト方針

### 9.1 テストの種類

- **ユニットテスト**：Python 標準の `unittest` で実装
- **対象**：各サブコマンドの正常系・異常系
- **配置**：`tests/tools/test_check_workflow_action.py`

### 9.2 fixture 構造

``\`
tests/fixtures/spec-json-cases/
├── all-true/                  # すべての段が true の状態
│   └── spec.json
├── requirements-alignment-false/  # alignment が false の状態
│   └── spec.json
├── design-drafting-blocked/   # requirements.approval が false の状態
│   └── spec.json
└── …
``\`

### 9.3 必須テストケース

- **正常系**：
  - `spec-set foundation requirements approval true` ＋ alignment=true → exit 0
  - `commit` ＋ pending 所見 0 件 ＋ 通常変更のみ ＋ 有効なユーザ承認レコード → exit 0
  - `commit` ＋ post-write 対象文書 ＋ 有効なユーザ承認レコード ＋ completed manifest → exit 0
  - `audit-commit HEAD` ＋ post-write 対象文書 ＋ matching completed manifest → exit 0
  - `guarded-git-commit` ＋ 有効なユーザ承認レコード → commit 実行、承認レコード消費済み
  - `push` ＋ 作業ツリー clean ＋ 先行 1 コミット → exit 0
- **警告系**：
  - `commit` ＋ pending 所見 1 件以上 → exit 1
  - `commit` ＋ spec.json 変更含む → exit 1
  - `spec-set <stage> false` ＋ 現状 true → exit 1（reopen 警告）
- **逸脱系**：
  - `spec-set foundation requirements approval true` ＋ alignment=false → exit 2
  - `spec-set foundation design drafting true` ＋ requirements.approval=false → exit 2
  - `push` ＋ 作業ツリー dirty → exit 2
  - `commit` ＋ ユーザ承認レコードなし／消費済み／承認対象外 staged ファイルあり → exit 2
  - `commit` ＋ post-write 対象文書 ＋ completed manifest なし → exit 2
  - `audit-commit HEAD` ＋ post-write 対象文書 ＋ completed manifest なし → exit 2
  - `guarded-git-commit` ＋ ユーザ承認レコードなし → commit しない
  - `commit` ＋ `.git/` 内ファイル含む → exit 2

### 9.4 TDD の遵守（入口規律）

実装は次の順序で進める：

1. 期待される入出力に基づきテストを作成（実装コードは書かない）
2. テストを実行し、失敗を確認
3. テストが正しいことを確認できた段階でコミット
4. テストをパスさせる実装を進める
5. 実装中はテストを変更せず、コードを修正し続ける
6. すべてのテストが通過するまで繰り返す

## 10. 配置場所とディレクトリ構造

``\`
tools/
├── check-workflow-action.py        # スクリプト本体（実行ファイル、shebang あり）
├── guarded-git-commit.py           # commit 承認レコード検査つき git commit ラッパー
└── workflow_precheck/              # 補助モジュール（必要に応じて分割）
    ├── __init__.py
    ├── spec_loader.py              # spec.json 読み込み
    ├── git_reader.py               # git status／diff 読み込み（subprocess 経由）
    ├── pending_findings.py         # learning/workflow/carry-forward-register/reviewcompass-import.yaml 読み込み
    ├── judges.py                   # 判定ロジック（spec_set／commit／push）
    ├── output.py                   # 人間可読／JSON 出力の整形
    └── logger.py                   # ログ書き出し

tests/
├── tools/
│   └── test_check_workflow_action.py
└── fixtures/
    └── spec-json-cases/

docs/
├── logs/
│   └── workflow-precheck.log       # 実行ログ（自動生成、gitignore 候補）
└── operations/
    └── WORKFLOW_PRECHECK.md        # 本文書
``\`

ログファイル `docs/logs/workflow-precheck.log` は実行時に増え続けるため、`.gitignore` への追加を検討（個別判断、利用者と相談）。

## 11. 段階 1 規律との接続

### 11.1 段階 1 が本スクリプトをいつ呼ぶか

段階 1（LLM）の規律として、不可逆操作の **直前に必ず** 本スクリプトを呼ぶ：

- spec.json の `workflow_state` を変更する Edit／Write の直前 → `spec-set` 呼び出し
- `git commit` の直前 → `commit` 呼び出し。実行は原則 `guarded-git-commit.py` 経由
- `git push` の直前 → `push` 呼び出し

### 11.2 出力の解釈と次の行動

- exit 0：処理続行
- exit 1：警告内容を応答に明示、利用者に判断を求めるか自律続行かを規律で決める
- exit 2：処理を止めて利用者に報告

### 11.3 段階 1 規律の文書化（残作業）

段階 1 規律の具体的な文言（`AGENTS.md`、`CLAUDE.md`、または規律ファイルに追加する文）は、本仕様確定後の **項目 3：段階 1 の規律化** で起草する（TODO §3 D 残作業項目 3、利用者明示承認必須）。Codex では `AGENTS.md`、Claude Code では `CLAUDE.md` が入口規律になる。

## 12. 段階 3 フック導入時の拡張余地

### 12.1 発動条件

各実行環境の hook adapter（ツール呼び出し前のフック）で、次のとき本スクリプトを自動発動：

- **Edit／Write** で対象パスが `spec.json` を含む → `spec-set` 自動呼び出し
- **Bash** で commit 系コマンドを含む → `commit` 自動呼び出し
- **Bash** で push 系コマンドを含む → `push` 自動呼び出し

### 12.2 引数の取得方法

hook adapter は、ツール呼び出しの引数を受け取る。Edit の `file_path`、Bash の `command` 文字列から、本スクリプトの引数を自動構築：

- 例：Edit `file_path` が `.reviewcompass/specs/foundation/spec.json` → `spec-set` の `<feature>` を `foundation` に
- 例：Bash `command` が `git commit ...` → `commit` を呼ぶ

引数の自動抽出ロジックは各 adapter の hook 側スクリプトに実装する。Claude Code では `.claude/hooks/pre-tool-use.sh` 等、Codex では `.codex/hooks/` と `.codex/hooks.json` 等の配置に従う。

### 12.3 fail-closed の実現

- フック側で本スクリプトの exit code を見て、`exit code ≥ 2` ならツール呼び出しを遮断
- exit 1 は警告だけ表示してツール呼び出しを通す
- exit 0 はそのまま通す

### 12.4 段階 3 導入の前提

- 段階 2 のスクリプトが安定動作している（小規模運用の実測完了）
- 段階 1 規律が確立されている
- 段階 3 導入は利用者明示承認必須（規律 §0.2、フェーズ 4 以降）

## 13. 実測結果（段階 2 小規模運用、2026-05-25 セッション 24）

本節は仕様確定後の段階 2 スクリプト実装と動作確認の実測結果を記録する。仕様 §14 残作業項目 2「段階 2 の小規模運用による実測」の成果。

### 13.1 実測の範囲

- 実 `.reviewcompass/specs/<feature>/spec.json` に対する spec-set サブコマンド
- 一時 git リポジトリでの commit／push サブコマンド（実 repo は汚さない）
- 引数妥当性検査の挙動

### 13.2 実測シナリオと結果

14 シナリオを実行、すべて想定どおりの判定（OK／WARN／DEVIATION）：

| 番号 | 種別 | 入力概要 | 想定 | 実測 |
|---|---|---|---|---|
| 1 | spec-set | foundation design drafting true | OK | OK |
| 2 | spec-set | foundation tasks drafting true（design 未承認） | DEVIATION | DEVIATION |
| 3 | spec-set | foundation requirements alignment false（reopen） | WARN | WARN |
| 4 | spec-set --json | foundation design drafting true | OK の JSON 出力 | OK の JSON |
| 5 | commit | 実 repo、staged 0、未消化 0 | OK | OK |
| 6 | push | 実 repo、tree clean、ahead 0 | OK | OK |
| 7 | spec-set | conformance-evaluation design drafting true | OK | OK |
| 8 | spec-set | foundation intent approval true（機能横断段） | OK | OK |
| 9 | spec-set | foundation requirements drafting false（reopen） | WARN | WARN |
| 10 | spec-set 引数 | foundation nonexistent-phase | 非 0 ＋ エラー | 非 0、有効値列挙 |
| 11 | commit | 未消化所見 1 件 | WARN | WARN |
| 12 | commit | spec.json 変更含む | WARN | WARN |
| 13 | commit | credentials.json 含む（危険変更） | DEVIATION | DEVIATION |
| 14 | push | dirty tree | DEVIATION | DEVIATION |

### 13.3 確認できた仕様準拠

- spec-set の判定（仕様 §6.1）：同フェーズ前段依存・上流フェーズ approval 依存・reopen 警告がすべて期待どおり動作
- commit の分類（仕様 §6.2）：通常／要注意（spec.json／docs/plan/）／危険（credentials／secret）の 3 分類が機能
- push の clean 性検査（仕様 §6.3）：未追跡ファイル 1 件でも dirty 検知、origin 未設定時も処理続行
- 終了コード体系（仕様 §7.1）：0／1／2 が想定どおり
- ログ取得（仕様 §8）：JSON Lines 形式で全シナリオの判定が追記される
- 引数妥当性検査（仕様 §5.1）：無効な値で適切なエラーメッセージと有効値の列挙

### 13.4 実測中に発見・是正した小さな問題

- 人間可読出力の真偽値表記が Python 慣習の "True/False" だったため、仕様 §7.2 サンプル準拠の小文字 "true/false" に統一（コミット `662bffb` で対処）
- `docs/logs/workflow-precheck.log` を `.gitignore` に追加（仕様 §10 の利用者と相談事項を確定、コミット `662bffb`）

### 13.5 観察事項（修正不要）

- `origin/main` 未設定時の push：「(リモート origin/main が未設定または取得失敗)」と表記して処理続行、実用上問題なし
- commit で staged ファイル 0 件の場合：OK 判定だが、実際の git commit はファイルなしで失敗するため、スクリプトとしては問題なし
- 直近 5 コミットの表示：commit メッセージが長くても折り返さずに 1 行表示（情報密度を優先）

### 13.6 結論

段階 2 スクリプトは仕様 §1〜§9 のとおり動作することを実測で確認。次の残作業項目（§14、旧 §13）に進める前提条件は揃った。

## 14. 仕様確定後の作業順序

本文書の正本化後、TODO §3 D の残作業を次の順で進める：

1. **段階 2 のスクリプト実装**（TDD で実装、tests／tools 配下に成果物）
2. **段階 2 の小規模運用による実測**（コスト・効果の数値検証）
3. **段階 1 の規律化**（`AGENTS.md`、`CLAUDE.md`、または規律ファイルに薄く追加、利用者明示承認）
4. **規律統廃合の本格議論**（実測データを踏まえて、active 規律 18 件 → 12 件程度、利用者明示承認）
5. **段階 3 のフック導入**（仕様調査、対象ツールの絞り込み、フェーズ 4 以降、利用者明示承認）

## 15. 本仕様の改訂規律

- 本仕様の変更は規律 §0.2 計画書方針変更に準じる（利用者明示承認必須）
- 改訂時は最終更新日付を更新、改訂履歴を末尾に追記
- 範囲拡張（範囲案 3 への移行など）は §3.3 に従う

## 16. 改訂履歴

- 2026-05-25 セッション 24：新設（採用承認の出典は冒頭「採用承認の出典」節を参照）
- 2026-05-25 セッション 24：§13 実測結果を追加、既存 §13〜§15 を §14〜§16 に繰り下げ（14 シナリオの実測完了に伴う追記）

```

## FILE: docs/operations/SESSION_WORKFLOW_GUIDE.md

```text
# SESSION_WORKFLOW_GUIDE：セッション運営ガイドライン

最終更新：2026-06-04（review-run 後の proxy_model 判断代行手順を正本化、セッション記録の作成手順を正本化）／2026-06-03（Codex adapter migration：Claude Code 固定の作業環境記述を adapter 方針へ整理）／2026-05-30（セッション 41：§4.2 モデル割り当てを計画書 §5.9.1・実態に整合。「主役＝メインセッション」の誤記を訂正し、メイン LLM は 3 役のいずれにもならないことを明記、モデル能力配分規律へ更新）／2026-05-23（セッション 21：用語「遡及／波及」の二軸的定義への訂正、段集合の責務分離による 5 段化を反映）

本文書は ReviewCompass の開発セッションを確実に回すための運用ガイドラインである。セッション 19 で発覚した「ワークフロー把握不足のまま着手」「用語混同（遡及／波及）」等の失態と検討不足を踏まえ、次セッション以降が同じ失敗を繰り返さないよう手順と判断指針を明示する。

本文書は運用文書（`docs/operations/` 配下）であり、計画書（`docs/plan/`）の方針を**実行可能な手順**に落とし込んだもの。計画書の改定なしに本文書だけを更新できる位置付け。

## 1. セッション開始時の必読フロー（5 分以内）

セッション開始時は **作業着手前に必ず**次を順番に確認する。確認なしの着手は失態の原因となる（セッション 19 §0 の経験）。

### 1.1 必読 5 件

順序は重要：

1. **`TODO_NEXT_SESSION.md`**（最新進捗）
   - 前セッション末尾の到達点、次の作業候補、未消化所見
   - 「§0 重要事項」「§1 起動手順」「§3 次の作業候補」を最低限読む
   - 直近の `docs/sessions/session-*.md` も併読し、TODO に圧縮された経緯の詳細を確認する

2. **計画書 §5.4〜§5.7**（ワークフロー手続き）
   - §5.4：軽量化方針（思想は継承、実装は 1／10）
   - §5.5：9 ファイル体制と段階層構造（drafting → triad-review → review-wave → alignment → approval の 5 段、責務分離による 5 段化が確定済み 2026-05-23。計画書改定は第 2 段階で実施）
   - §5.6：reopen 手続きの機械強制（手戻り種別の二次元表記）
   - §5.7：session 跨ぎ時の状態管理（`stages/in-progress/`）

3. **計画書 §5.23 と §5.23.12**（dogfooding ／ サブエージェント方式）
   - §5.23：手動 dogfooding 計画
   - §5.23.12：サブエージェント方式（中間経路、`subagent_mediated`）の運用条件

4. **`learning/workflow/carry-forward-register/reviewcompass-import.yaml`**（持ち越し所見）
   - 機能横断波及所見の未消化件数と内容を把握
   - 要件 review-wave／alignment／approval で対処予定の件（過去のセッション 19 で旧 alignment-gate として実施した分は完了済み）

5. **`docs/extraction-mapping.md`**（抽出進捗）
   - 各機能の状態（未着手／抽出中／抽出済／確認済）
   - 機能ごとの実施履歴

### 1.2 確認後の git 状態把握

- `git log --oneline -10`：直近のコミット履歴
- `git status`：未コミット変更の有無

### 1.3 ワークフロー上の現在位置の確認

- 現在どのフェーズか（intent ／ requirements ／ design ／ tasks ／ implementation）
- 現在どの段か（drafting ／ triad-review ／ review-wave ／ alignment ／ approval の 5 段）
- 残機能と消化予定所見

## 2. ワークフロー段の役割と順序

### 2.1 全体構造（責務分離による 5 段化、2026-05-23 利用者明示承認）

``\`
intent 層（人間担当）
  ↓
機能分離（§3.1 で 7 機能体制を確定済み）
  ↓
requirements 段：drafting → triad-review → review-wave → alignment → approval
  ↓
design 段：drafting → triad-review → review-wave → alignment → approval
  ↓
tasks 段：drafting → triad-review → review-wave → alignment → approval
  ↓
implementation 段：drafting → triad-review → review-wave → alignment → approval
``\`

旧記述（drafting → review-wave → alignment-gate の 3 段）は次の 2 段階の改定により旧式化：

- alignment-gate を alignment（LLM 自動判定）と approval（人間または別モデル承認）の 2 段に分割
- drafting と triad-review を別段に分離（責務分離）

合計で 5 段化（drafting／triad-review／review-wave／alignment／approval）。計画書 §5.5 の改定は第 2 段階で実施し、それまでは本ガイドラインの 5 段記述が運用上の正本。

### 2.2 各段の役割（責務分離後）

- **drafting**：各機能の草案作成のみ。1 機能ずつ独立に進める。actor=llm（または human）。tasks 段の drafting では、対象機能の設計書 §14 要件追跡表（Req 受入単位 × 担当タスク単位）を骨格として tasks.md を作成する。
- **triad-review**：機能内の 3 役レビュー（主役・敵対役・判定役）と機能内対処の実施。手動 dogfooding または subagent_mediated（サブエージェント仲介方式）で実施。actor=llm
- **review-wave**：複数機能を横断する複数ラウンドレビュー。機能横断波及所見の集約・対処、および **7 モデル比較実験の 2 回目（同根問題評価）と同根問題集約**（2026-05-27 セッション 34 追記、(ニ) (Q2) 採用、2026-05-28 セッション 35 で 2 回方式に訂正）。7 モデル比較実験は **2 回方式** で実施し、1 回目は機能ごとの triad-review 段で機能内 must-fix／should-fix を評価して機能内対処を完了させ、2 回目（本段）は全機能の triad-review 完了後に機能横断波及所見と同根所見（異なる機能で同じ性格の所見が独立に発見された組）を評価して一貫した対処方針で全該当機能の仕様文書に反映する。詳細は計画書 §5.5 機能横断段の作業内容 ／ §5.9.6 N モデル比較実験の実施タイミングを参照
- **alignment**：LLM 自動判定による整合確認段（旧 alignment-gate を分割した前半、actor=llm）
- **approval**：人間または別モデル（§5.12 人間代役機構）による承認段（旧 alignment-gate を分割した後半、actor=human または proxy_model）

drafting と triad-review を別段にする理由：誰が何をしたかを段単位で明確に記録するため。草案作成者と判定者を分ける規律（§5.4）が段の構造上で機械検査可能になる。

### 2.3 段の進め方の規律

- **drafting 段の草案完成** → 当該機能の triad-review 段に進む（機能単位で逐次進行）
- **triad-review 段で 3 役レビューと機能内対処** を完了 → 当該機能の drafting／triad-review がそろう
- **全機能で drafting ＋ triad-review を完了** してから review-wave に進む（部分的に review-wave を始めない）
- **review-wave の所見を消化** してから alignment に進む
- **alignment で LLM 自動判定** を通過してから approval に進む
- **approval で利用者または別モデル承認** を得てから次フェーズに進む

### 2.4 「次の機能の drafting に進むべき」状況の判断

triad-review 段で 3 役レビューを行った所見が **機能横断の波及所見**だった場合、当該機能の triad-review で対処せず、`learning/workflow/carry-forward-register/reviewcompass-import.yaml` に持ち越して **次の機能の drafting に進む**。これがセッション 19 の中盤で確立された運用パターン。

## 3. 修正案件の波及種別と処理段

### 3.1 用語の使い分け（二軸的定義、2026-05-23 訂正）

両用語は **対象方向が異なる正当な技術用語** であり、優劣はない：

- **遡及（そきゅう）**：**上流フェーズへの影響**。下流段の作業で発見された問題が、上流段（過去フェーズ）の修正を要するもの。例：実装段で発見した不整合が要件段の書き直しを要する
- **波及（はきゅう）**：**同フェーズ内の他機能（フィーチャー）への影響**。ある機能のレビューが別機能との不整合を露出させるもの。例：foundation 要件の修正が runtime／evaluation 要件にも影響する

セッション 19 中盤で、私（メインセッション）が「foundation の遡及修正」と表現したことを利用者が「波及であり alignment wave の範囲」と訂正した。これは A-001 が **同フェーズ内（要件段）の他機能（foundation／runtime）への影響** であって、上流フェーズへの修正ではない、という意味だった。私はこれを「遡及は悪、波及は善」と誤一般化していたが、後のセッションで利用者から再訂正があり、本ガイドラインを二軸的定義に書き直した（2026-05-23）。

### 3.2 修正案件の 4 種別（＋ 2 補助種別）

レビューで露出する所見は次の種別に分類する：

| 種別 | 内容 | 例 |
|---|---|---|
| **機能内対処** | 当該機能の仕様修正のみで完結 | 表現修正、機能内の語彙不統一訂正 |
| **波及（同フェーズ・横方向）** | 同フェーズ内の他機能の仕様修正も必要 | A-001：foundation 要件と runtime 要件の `not_run` 欠落 |
| **遡及（上流フェーズ・縦方向）** | 上流フェーズの仕様修正が必要 | 設計段で「要件段の Req 6 受入 8 に矛盾あり」と発見 |
| **遡及 ＋ 波及（縦 ＋ 横）** | 上流フェーズの複数機能に影響 | 設計段で発見した要件段の不整合が複数機能の要件文書に波及 |

補助種別：

- **leave-as-is（修正不要）**：判定役が「修正不要」と判断したもの、対処せず記録のみ
- **延期**：「将来フェーズで対処」と判定役が明示したもの（例：F-004 の配置時対処）

### 3.3 種別ごとの処理段と方法

#### (a) 機能内対処

- **発見されるタイミング**：drafting 段（起草者の自己発見）／ triad-review 段（3 役レビュー）
- **処理する段**：当該機能の **triad-review 段** で対処（drafting に戻して草案修正、または triad-review 段内で直接修正）
- **方法**：当該機能の仕様文書を直接修正
- **次段への進行**：当該機能の triad-review 段が `completed` 状態になってから次機能へ
- **記録先**：レビュー記録（`.reviewcompass/specs/<機能>/reviews/<日付>-<種別>.md`）の §4 統合節に「対処済み」と記録

##### (a-1) must-fix 所見の対処手順（2026-05-25 セッション 25 規律、深掘り議論の義務化）

triad-review 段で判定役が must-fix と判定した所見の対処は、起草者（LLM または人間）が独自判断で仕様文書を修正することを禁ずる。利用者と必ず議論し、各所見の対処方針を 1 件ずつ平易な日本語で説明して合意を得てから反映する。

**手順**：

1. must-fix 所見を 1 件ずつ取り上げる。複数所見が論理的に連動する場合は連動単位でまとめる（例：F-001 と F-007 が同一事象を別観点で扱う場合）
2. 各所見について、対処方針の提案を次の構造で平易に説明する：
   - その判断が必要になった経緯（要件文書や上流文書からの導出）
   - 候補案の列挙（必ず複数）
   - 各候補案の利点と弱点
   - **後段で発生し得る問題の深掘り**：下流仕様（他機能の design／tasks／implementation）、対象アプリへの配置可能性、機械検証時の挙動、実装フェーズの運用、将来の拡張性
   - 推奨案とその根拠
3. 「現状維持」を推奨する場合も、現状維持の弱点を検証してから示す
4. 一括処理（複数論点を一気に決着）を避け、各論点を個別に深掘りする
5. 利用者の判断を得てから、仕様文書を 1 件ずつ Edit で修正する
6. 各修正後に grep または Read で機械的に照合し、反映を確認する
7. レビュー記録（reviews/...）の §4 統合節に「対処方針・利用者承認の出典・反映箇所」を記録する

**深掘りの具体内容**（推奨案を提示する際に必ず想定する事項）：

- foundation 機能の場合：対象アプリへの配置可能性、計画書非配置、要件 7（リポジトリ内資産の規則）との整合
- 値域・語彙の固定：将来拡張時の改訂コスト、機械検証時の不正値検出
- 責務境界：foundation と runtime（または他機能）の責務分離、上流が下流の実装方針に踏み込まない原則
- 不変性：成果物の追記性、生証拠は不変の原則
- 依存関係：他機能が当該仕様を取り込む際の参照可否

**禁則**：

- 利用者と議論せずに must-fix 所見の対処内容を独自に確定する
- 「現状維持を推奨」と表層的に提案する（弱点検証を欠く）
- 候補案を 1 つしか提示しない（代替案との比較を欠く）
- 後段影響を想定しない推奨

本規律の出典：2026-05-25 セッション 25 の foundation／design must-fix 対処での手順違反事例（利用者の問いかけ「foundationのmust_fixについては、議論しなくて良いのか」と「(イ)で後段に問題発生はないか」「一連の提案は、表層的で深掘りされていない。先ほどの指摘がなければ、下流でreopen案件になっていた」）。詳細は当該セッションのレビュー記録 [.reviewcompass/specs/foundation/reviews/2026-05-25-design-triad-review.md](../../.reviewcompass/specs/foundation/reviews/2026-05-25-design-triad-review.md) を参照。

##### (a-2) review-run 後の proxy_model 判断代行手順

API 経由の review-run 後に、人間の個別判断を proxy_model が代行する場合も、メインセッション LLM が重要件を独自に確定して実装へ進むことを禁ずる。proxy_model 代行は「人間判断を省略する」ものではなく、判断主体を別モデルへ移す運用である。

**役割分担**：

1. メインセッション LLM は raw レビューを集約し、三段階トリアージの下書きを作る。parsed YAML だけでなく raw response も読み、同根所見をまとめ、`must-fix` ／ `should-fix` ／ `leave-as-is` の候補を作る
2. メインセッション LLM は重要件ごとに、平易な問題説明、候補案、各案の利点と弱点、後段影響、推薦案を作る
3. proxy_model は重要件の採用案・判断理由・最終ラベルを決定する。実装は担当しない
4. メインセッション LLM は proxy_model の raw response を保存し、`proxy-decisions/<finding-id>.decision.yaml` と `approval-proxy-<日付>.yaml` に構造化する
5. 機械ガードは proxy decision の充足を検査する。未判断、raw 欠落、候補案欠落、採用案欠落、判断理由欠落、triage 最終ラベルとの不一致があれば実装へ進まない
6. メインセッション LLM は機械ガード通過後、採用された修正だけを TDD で実装する
7. コミット・プッシュ・spec.json 更新・フェーズ移行は人間の明示承認を要求する。proxy_model はこれらの不可逆操作を代行しない

**重要件の判定閾値**：

- `must-fix`、`ERROR`、`CRITICAL` は必ず重要件として扱う
- `should-fix` でも、上流仕様、データ契約、機械ガード、証跡保持、ワークフロー権限境界、複数モデルの同根指摘に関わるものは重要件として扱う
- 同根指摘とは、複数モデルの所見が同じ対象ファイル・同じ出力契約・同じ機械ガード・同じ証跡・同じ原因に触れているものをいう。表現が異なっても、対象または原因が一致する場合は同根として扱う
- 正本削除、機械ガード削除、重要件閾値の引き下げ、承認証跡の削除、検証対象範囲の縮小は、コミット等と同じく人間の明示承認を要する不可逆操作として扱う
- 判断に迷うものは重要件側に倒し、proxy_model 判断または人間判断へ回す

**proxy_model への入力証跡**：

- proxy_model へ渡す判断材料には、メインセッション LLM の要約だけでなく、元 review raw への参照または抜粋を必ず含める
- `proxy-decisions/<finding-id>.prompt.md` に、元 review raw 参照、問題説明、候補案セット、推薦案、判断してほしい最終ラベルを保存する
- `proxy-decisions/<finding-id>.decision.yaml` には、`candidate_options`、`source_raw_paths`、`decision_prompt_path`、採用案、棄却案理由、判断理由、最終ラベルを保存する
- proxy_model が元 review raw を読めない形の判断材料しか受け取っていない場合、その decision は実装着手の承認証跡として扱わない
- 現行の軽量ガードは、proxy_model_id の文字列一致、decision file の finding_id 一致、final_label 一致、prompt/raw/候補案証跡の存在を検査する。API 署名や暗号学的な生成元証明は将来課題とする

**証跡配置**：

- `raw/`：各モデルの生応答
- `triage.yaml`：メインセッション LLM による三段階トリアージ
- `proxy-decisions/<finding-id>.prompt.md`：proxy_model に渡した判断材料
- `proxy-decisions/<finding-id>.raw.txt`：proxy_model の生応答
- `proxy-decisions/<finding-id>.decision.yaml`：採用案、判断理由、最終ラベル、棄却案理由
- `approval-proxy-<日付>.yaml`：実装着手を許可する proxy approval record

**並列化可能な単位**：

- proxy_model への判断依頼は、同根所見クラスタ単位で並列化できる
- TDD 実装は、互いに同じファイルを更新しない実装単位、または入出力契約が独立しているタスク単位で並列化できる
- 共通スキーマ・共通ビルダー・同一ファイルを触る修正は直列で扱う
- 生成物、共有 helper、推移的契約、同じ出力 manifest、同じ traceability 出力を共有する修正は直列で扱う
- 並列実装の統合前に、メインセッション LLM が triage、proxy decision、テスト結果、ファイル差分を再照合する
- 並列処理で新しい判断問題が出た場合、その単位は停止し、proxy_model 判断または人間判断へ戻す
- 承認済み finding の実装中に見つけた未承認の便乗リファクタ、隣接挙動変更、対象外 cleanup は実施しない。必要なら新しい判断問題として停止する

**実装サブ担当 LLM の扱い**：

- 実装サブ担当 LLM は、原則として別スレッドかつ分離 worktree で扱う
- 同じ repo での並列実装は原則禁止し、読み取り調査または差分を残さない確認に限定する
- メインセッション LLM は、対象 finding、proxy decision、触ってよいファイル、期待テスト、禁止事項、停止条件を実装サブ担当へ渡す
- 実装サブ担当は、指定範囲外のファイル変更、判断変更、コミット、プッシュ、spec.json 更新、フェーズ移行を行わない
- 実装サブ担当が新しい判断問題、上流仕様への疑義、許可ファイル外の修正必要性を見つけた場合、その作業単位を停止してメインセッション LLM に戻す

**別スレッド生成物の扱い**：

- 別スレッド・分離 worktree で発生した生成物は、実装差分、検証結果、判断根拠、作業ノイズに分類する
- 実装差分は、メインセッション LLM が確認したうえで本線 worktree への取り込み候補にする
- 検証結果と判断根拠は、必要な要約だけを review-run、session record、または docs/notes に保存する
- 判断に影響した失敗試行、失敗パッチ、途中ログは work_noise から decision_basis へ昇格し、メインセッション LLM が要約または該当箇所を保存する
- 作業ノイズは本線 repo に取り込まない。作業ログ、一時メモ、途中のテスト出力、失敗パッチ案は原則としてサブ worktree 側に閉じる
- 本線へ戻す標準単位は、パッチ、テスト結果サマリ、未解決事項の 3 点とする

#### (b) 波及（同フェーズ・他機能への影響）

- **発見されるタイミング**：triad-review 段（3 役が他機能との不整合に気づく）／ review-wave 段（機能横断レビュー）
- **処理する段**：**review-wave 段**（フェーズ終端の機能横断段、全機能の drafting ＋ triad-review 完了後に開始）
- **方法**：
  1. triad-review 段で波及と判定されたら **当該機能では対処せず**、`learning/workflow/carry-forward-register/reviewcompass-import.yaml` に追記
  2. 「次の機能の drafting」に進む（個別機能の段では対処しない）
  3. 全機能の drafting ＋ triad-review が完了したら、review-wave 段で集約消化
  4. 影響を受ける全機能の仕様文書を一括修正（依存順を守る、例：foundation を先に修正してから runtime）
- **記録先**：`learning/workflow/carry-forward-register/reviewcompass-import.yaml` の各所見項目、消化後は「✅ 対処済み（日付）」追記

#### (c) 遡及（上流フェーズへの影響）

- **発見されるタイミング**：任意の下流段（triad-review／review-wave／alignment／approval のいずれか）
- **処理方法**：**reopen 手続き（10 ステップ、§5.6）** を起動。当該段の作業を停止し、上流フェーズに戻る
- **手戻り種別判定**：N（intent）／R（requirements）／D（design）／A（tasks）／I（implementation）× 深さ 0〜4 の二次元表記で判定
- **再実施対象決定**：第 7 ステップで `stages/reopen-procedure.yaml` の trigger_map（再実施対象段の決定表）を参照して機械決定。actor=human の段（approval 等）に来たら作業を止めて承認待ち
- **記録先**：種別判定の根拠を `docs/reviews/reopen-classification-<日付>.md` に残す、機能単位 spec.json の `reopened` 履歴と `recheck` フラグを更新

#### (d) 遡及 ＋ 波及の組合せ

- **発見されるタイミング**：任意の下流段
- **処理方法**：reopen で上流フェーズに戻り、上流フェーズの review-wave 段で波及所見として集約消化、その後下流に伝播
  1. **第 1 段階**：reopen 手続きで上流フェーズに戻り、影響範囲を特定（trigger_map）
  2. **第 2 段階**：上流フェーズで `learning/workflow/carry-forward-register/reviewcompass-import.yaml` に波及所見として追記し、当該フェーズの review-wave 段で消化
  3. **第 3 段階**：上流フェーズの alignment ＋ approval を再実施
  4. **第 4 段階**：下流フェーズの alignment ＋ approval を再実施（trigger_map で連鎖再実施対象として決定）
- **記録先**：reopen 記録 ＋ `learning/workflow/carry-forward-register/reviewcompass-import.yaml` の両方

#### (e) leave-as-is と延期

- **leave-as-is**：判定役が「修正不要」と判断したもの。対処せず、レビュー記録に判定根拠を残すのみ
- **延期**：将来のフェーズで対処する判定。レビュー記録に延期理由と対処予定フェーズを残し、当該フェーズ着手時のチェックリストに追記

### 3.4 振り分け判断のフロー（triad-review 段で実施）

triad-review 段の判定役は、各所見について次の振り分けを行う：

``\`
所見発見
  ↓
当該機能の仕様修正のみで完結するか？
  ├── YES → 機能内対処（triad-review 段内で対処）
  └── NO
      ↓
  他機能の仕様修正も必要か？
  ├── YES（同フェーズ内のみ） → learning/workflow/carry-forward-register/reviewcompass-import.yaml に追記、review-wave 段で処理
  ├── YES（上流フェーズに戻る必要あり、単機能） → reopen 手続きを起動
  └── YES（上流フェーズに戻る必要あり、複数機能） → reopen ＋ 上流の review-wave で集約処理
  
別判定：
  ├── 修正不要 → leave-as-is（記録のみ）
  └── 将来フェーズで対処 → 延期（チェックリスト追記）
``\`

### 3.5 段ごとの露出と処理段の対応表

| 段 | 主に露出する所見 | 当該段内で処理する所見 | 次段に持ち越す所見 |
|---|---|---|---|
| drafting | 起草中の自己発見 | 機能内（草案に直接反映） | なし |
| triad-review | 機能内 ／ 波及 ／ 遡及 | **機能内** のみ | 波及 → review-wave、遡及 → reopen |
| review-wave | 波及（横断ラウンド中の追加発見も） | **波及** | 遡及あり → reopen |
| alignment | 自動判定の不整合検出 | （自動判定が通過するまで前段に戻す） | 遡及あり → reopen |
| approval | 重大見落とし、利用者または別モデルによる指摘 | （承認しない） | reopen で上流戻し |

### 3.6 機能横断波及所見の管理ルール

- 各機能の triad-review 段で発見されたら、即時 `learning/workflow/carry-forward-register/reviewcompass-import.yaml` に追記
- 追記項目：所見 ID（A-XXX 形式）、検出セッション、波及範囲（影響を受ける機能と仕様箇所）、対処方針、依存関係
- review-wave／alignment／approval の機能横断段着手時、全件を消化対象とする
- 消化後、各所見に「✅ 対処済み（YYYY-MM-DD、要件 review-wave）」ラベルを追加

## 4. サブエージェント方式の運用条件

### 4.1 採用根拠（計画書 §5.23.12 由来）

- メインセッションが主役、サブエージェントが敵対役・判定役を担う中間経路
- 手動 dogfooding と実行時経由の中間に位置
- フェーズ 1 から運用可能、追加料金なし（セッション 19 で実証）

### 4.2 モデル割り当て（規律）

3 役（主役・敵対役・判定役）はすべて独立したサブエージェントが担い、**メイン LLM（コンシェルジュ＝起草者）は 3 役のいずれにもならない**（計画書 §5.9.1、起草者と判定者の分離規律 §0.3）。メイン LLM は草案作成と三役レビュー結果の取りまとめのみを担う。

各役のモデルは `reviewcompass.yaml` で指定する。**推奨既定**：主役 Opus 4.7 ／ 敵対役 Sonnet 4.6 ／ 判定役 Opus 4.7（計画書 §5.9.1）。利用者が yaml で変更可能。

**モデル能力配分の規律（計画書 §5.9.1、2026-05-25 セッション 25 の foundation／design triad-review 実験により制定）**：

- **主役と敵対役は必ず異なるモデルを使う**（敵対役の独立性確保のため）
- 判定役は主役または敵対役と同じモデルを使うことを許容する
- 敵対役と判定役には、反証生成と責務境界判断を担う十分な能力のモデルを割り当てる

旧規律「3 役で異なるモデルファミリーを使う（モデル多様化）」「同モデル使用は禁止」は **撤回された**。モデル多様化単独ではバイアス低減効果が限定的で、能力配分の方が重要と判明したため（実験記録 [../notes/2026-05-25-triad-review-model-allocation-experiment.md](../notes/2026-05-25-triad-review-model-allocation-experiment.md) 由来）。

**実態の配置例**：foundation tasks triad-review（2026-05-26）では「主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7」（実験(エ)継続、design triad-review と同配置）。いずれの役もサブエージェントで、メインセッション（起草者 Opus 4.7）は 3 役のいずれにも入っていない。

### 4.3 サブエージェント呼び出し時の規律

- **プロンプトに自己完結性を持たせる**：サブエージェントは別 session で、メインの作業文脈を共有しない
- **計画書引用は事後検証**：サブエージェントの計画書引用には §番号誤りが発生しうる（セッション 19 で実証）。メインセッションが grep で確認する
- **ファイル書き込みは原則禁止**：読み取りと分析のみ。例外的にレビュー記録の §2 や `learning/workflow/carry-forward-register/reviewcompass-import.yaml` への直接追記を許容
- **モデル指定**：利用中の adapter が提供する model / provider 指定方法に従う。Claude Code では Agent ツールの `model` パラメータで `"sonnet"`／`"haiku"` を指定していた。Codex や外部 API 経由では、各 adapter の手引きと `config/api-settings.yaml` の provider 設定を参照する

### 4.4 レビュー記録の必須フィールド（§5.4 起草者と判定者の分離）

レビュー記録の front-matter に次を必須化：

``\`yaml
author:
  identity: <adapter_main_session>
  model: <model-id>
  role: drafter
reviewer:
  identity: <adapter_reviewer_session>
  model: <model-id>
  role: final_judgment
  separation_from_author: true
``\`

`author.identity` と `reviewer.identity` が異名であることを機械検査の対象とする。

Claude Code 運用時の例では `claude_code_main_session` / `claude_code_subagent` を使っていた。Codex 運用時は `codex_main_session`、外部 API 検証者、または各 adapter が定義する識別子を使う。重要なのは provider 名ではなく、起草者と判定者が分離していることを記録できること。

### 4.5 mode 値（計画書 §5.23.12.5 由来）

レビュー記録の `mode` は `subagent_mediated`（正式値）。foundation のレビューモード語彙正本（Requirement 6 受入 6）の 3 値のうちのひとつ。

## 5. 利用者判断が必要な論点の見極め

### 5.1 利用者判断必須の項目

次のいずれかに該当する場合、LLM は単独で確定せず、利用者の明示承認を仰ぐ：

- **計画書方針変更**：計画書の節追加・修正（例：§5.18.13 への記述追加、§5.23.12 新節）
- **大規模再設計**：素材から大幅に削減・再構成する場合（例：workflow-management の 156 行 9 要件 → 8 要件）
- **機能横断の権限分担**：複数機能にまたがる責務分担の決定（例：A-007 の self-improvement と workflow-management の権限調停）
- **判定境界の判断**：must-fix／should-fix／leave-as-is の境界が曖昧な場合
- **承認・コミット・push・フェーズ移行**：すべて利用者明示承認必須（計画書 §5.19.6 由来）
- **作業の打ち切り・先送りの誘導**：利用者の明示承認なく「続きは次セッションで」等と作業を終了・先送りに誘導しない（2026-05-31 セッション 42 追記）

### 5.2 LLM が自律的に決められる項目

- **抽出時のクリーニング作業の細部**（機能名置換、自己適用前提除去等）
- **観点 5（検証可能性）の機械判定可能な所見の指摘**
- **レビュー記録の構造化**（front-matter、節構成）

### 5.3 判断の記録規律

利用者判断の結果は次の場所に記録：

- **計画書方針変更**：計画書の該当節に決定日付付きで記載
- **機能横断対処方針**：`learning/workflow/carry-forward-register/reviewcompass-import.yaml` の該当所見に対処方針として追記
- **重大論点**：レビュー記録の §1 主役レビュー、§4 統合の「利用者判断履歴」節に記録

### 5.4 セッション記録の作成規律

原則として毎セッション、セッション終了時または重要判断後に `docs/sessions/session-<N>-<YYYY-MM-DD>.md` を作成または更新する。特に、重要な判断・承認・レビュー結果・修正経緯が発生した場合は必須とする。これは会話全文の逐語ログではなく、後で経緯を確認できる要約記録とする。

`<N>` は `docs/sessions/` に存在する既存の最大セッション番号に 1 を加えた番号とする。同日の複数セッションでも番号を進め、同じ番号を再利用しない。
1 session につき 1 ファイルとし、同一 session 内で重要判断が複数回発生した場合は同じファイルへ追記する。重要判断ごとに別番号を消費しない。
並行セッションや未コミット作業により採番が衝突した場合、メインセッション LLM は既存記録・git 状態・未コミット差分を確認し、利用者が採番を確定するまで正式な新規セッション記録を作成しない。採番確定前に記録が必要な場合は、`docs/sessions/drafts/session-<YYYY-MM-DD>-<short-topic>.md` に一時草案を置き、正式番号確定後に `docs/sessions/session-<N>-<YYYY-MM-DD>.md` へ移動する。移動後は draft ファイルを残さず、正式ファイルに草案内容が統合済みであることを確認する。

メインセッション LLM はセッション記録の草案作成責任を持つ。利用者判断の引用・承認範囲・未確定事項に曖昧さがある場合は、記録前に利用者へ確認する。
コンテキスト切れや中断により当該 LLM が記録できない場合、次セッションが草案を引き継ぐ。草案がない場合は、TODO、review-run、approval record、git diff から経緯を再構成して記録する。

最低限、次を記録する：

- このセッションで実施した作業
- 利用者が承認した判断と、その対象
- API レビューや独立検証の結果と三段階トリアージ
- 修正した主要ファイルと検証結果
- 失敗・見落とし・再発防止に必要な気づき
- 次セッションへの引き継ぎ

推奨見出しは既存 session 記録と同型とし、最低限次を含める：

1. サマリ（このセッションでやったこと）
2. 気づき・特筆点
3. コミット一覧（該当する場合）
4. 次セッションへの引き継ぎ

`TODO_NEXT_SESSION.md` は次セッション向けの入口メモであり、詳細な経緯記録の正本ではない。詳細経緯は `docs/sessions/` に残し、TODO には必要な参照だけを置く。

## 6. コミット規律

### 6.1 コミット単位

- **計画書更新 ＋ 基盤整備**：1〜2 コミット（セッション冒頭の方針確定、運用ファイル整備）
- **機能ごとに 1 コミット**：仕様文書 ＋ 運用文書 ＋ レビュー記録の 3 ファイル（または schema/template 等の関連ファイル）
- **機能横断段（review-wave／alignment／approval）**：1 コミット（複数機能の小修正をまとめる）

### 6.2 コミット順序

依存マップ順（計画書 §3.1 phase_order）に従う：

1. foundation
2. runtime
3. evaluation
4. analysis
5. workflow-management
6. self-improvement
7. conformance-evaluation

### 6.3 コミットメッセージ規律

- **平易な日本語**：英語技術用語の連発を避け、完全な日本語の文で書く
- **題名**：機能名 ＋ 作業種別（例：「foundation 機能の requirements 抽出と 3 役レビュー」）
- **本文**：作成・更新ファイルの列挙、主な反映内容、機能横断所見の持ち越し有無
- **Co-Authored-By**：利用中の adapter と利用者方針に従う。Claude Code 運用時の履歴では `Claude Opus 4.7 (1M context) <noreply@anthropic.com>` を使っていたが、Codex 運用では自動付与を前提にしない

### 6.4 コミット前確認

- `git status` で対象ファイルを確認
- `git diff --cached` で内容確認（必要に応じて）
- `--no-verify` や `--no-gpg-sign` は使わない（規律）

### 6.5 push

push は **利用者明示承認**を仰いでから実行。LLM が自律的に push しない。

## 7. 用語ガイド

### 7.1 「遡及」と「波及」（二軸的定義、2026-05-23 訂正）

両用語は対象方向で使い分ける：

- **遡及（そきゅう）**：上流フェーズへの影響（時間軸＝過去方向）
- **波及（はきゅう）**：同フェーズ内の他機能への影響（横方向＝機能間）

両方とも正当な技術用語で、避けるべき／推奨という関係ではない。所見の性格を正確に表すために使い分ける。

### 7.2 判定値の使い分け

- **must-fix**：仕様の致命的または重要な欠落、修正必須
- **should-fix**：仕様の改善余地、修正推奨
- **leave-as-is**：仕様として問題なし、修正不要

### 7.3 機能内と機能横断

- **機能内対処**：当該機能の drafting 段で本セッション内に修正
- **機能横断持ち越し**：`learning/workflow/carry-forward-register/reviewcompass-import.yaml` に集約、review-wave／alignment／approval の機能横断段で対処

### 7.4 サブエージェント関連

- **メインセッション**：作業の入口となる LLM session。草案作成とレビュー結果の取りまとめを担い、3 役レビューの判定者とは分離する
- **サブエージェント**：敵対役・判定役を実行する別 session または外部 API 検証者。Claude Code では Agent ツール経由、Codex 運用では adapter が利用可能な実行形に従う
- **mode = `subagent_mediated`**：サブエージェント方式のレビュー記録の mode 値

### 7.5 計画書の節番号

- 計画書（`docs/plan/reconstruction-plan-2026-05-21.md`）の節番号は §X.Y 形式
- 引用時は **メインセッションで grep 確認**してから記述（サブエージェントの §番号誤り対策）

## 8. セッション 19 で得られた教訓（参考）

本ガイドラインは次の経験を反映している：

### 8.1 ワークフロー確認の失態

セッション 19 開始時、私（メインセッション）は計画書 §5.4〜§5.7 を読まずに foundation requirements の抽出を始めた。中盤で利用者が「ワークフローを再度読む」と指摘し、intent 段の所在（過去セッションで作成済み）、dogfeeding の §5.23 での既存記述、機能横断レビューの段位置（review-wave／alignment-gate）を確認することになった。**着手前の必読フロー（§1）はこの失態の再発防止策**。

### 8.2 用語混同（遡及／波及）

セッション 19 中盤で A-001（foundation の `not_run` 欠落）発見時、私が「foundation の遡及修正」と表現した。利用者が「遡及ではなく波及。本来は alignment wave の範囲」と訂正。**§3.1 の用語の使い分けはこの訂正を反映**。

### 8.3 機能横断波及所見の集約管理ファイルの新設

A-001 発見時、利用者の指示で `learning/workflow/carry-forward-register/reviewcompass-import.yaml` を新設して集約管理する運用パターンが確立した。これ以降、A-003／A-004／A-005／A-007／A-008 が同ファイルに追記され、要件 review-wave で一括消化された。

### 8.4 サブエージェントの計画書引用誤り

セッション 19 中盤、敵対役（Sonnet 4.6）が計画書 §5.18.11 を引用したが、実体は §5.18.2 周辺の別箇所だった（引用内容自体は正当）。**§4.3 の事後検証はこの経験を反映**。

### 8.5 サブエージェントの直接書き込みパターン

セッション 19 後半、敵対役が自発的に `learning/workflow/carry-forward-register/reviewcompass-import.yaml` に直接追記するパターンを確立。メインセッションを介さない効率化として、後続セッションでも継続予定。

### 8.6 利用者判断の見極め不足

セッション 19 中で、サブエージェント方式の正式採用、A-007 の権限調停（案 1／案 2）、解釈論点 α／う など、利用者判断が必要な論点が複数発生した。**§5 の利用者判断必須項目はこの経験を反映**。

## 9. 関連文書

- 計画書：[../plan/reconstruction-plan-2026-05-21.md](../plan/reconstruction-plan-2026-05-21.md)（§5.4〜§5.8 ワークフロー、§5.23／§5.23.12 dogfooding／サブエージェント方式、§5.19.6 利用者判断の運用ルール）
- 抽出進捗：[../extraction-mapping.md](../extraction-mapping.md)
- 機能横断波及所見：[../../learning/workflow/carry-forward-register/reviewcompass-import.yaml](../../learning/workflow/carry-forward-register/reviewcompass-import.yaml)
- レビュー記録雛形：[../../templates/review/manual_dogfooding_review_template.md](../../templates/review/manual_dogfooding_review_template.md)
- TODO：[../../TODO_NEXT_SESSION.md](../../TODO_NEXT_SESSION.md)

## 10. 本ガイドラインの改訂規律

- 本ガイドラインは運用文書であり、計画書の改定なしに更新可能
- 各セッションの経験から新たな教訓が得られた場合、§8 に追記
- 規律変更（§2〜§7）は利用者明示承認後に反映
- 改訂時は最終更新日付を更新

```

## FILE: docs/notes/2026-06-04-proxy-review-parallel-implementation-plan.md

```text
# proxy review 判断代行と並列実装の正本化計画メモ

作成日：2026-06-04

## 目的

API review-run 後に、メインセッション LLM が raw レビューを集約して三段階トリアージし、重要件の判断を proxy_model が代行し、実装作業を必要に応じて別スレッド・分離 worktree へ切り出せるようにする。

本メモは、会話上の運用案を正本と機械ガードへ落とすための計画メモである。正本は `docs/operations/SESSION_WORKFLOW_GUIDE.md` と workflow-management 仕様であり、本メモは作業計画と段階導入の記録に限定する。

## 正本化する事項

1. メインセッション LLM は raw review を読み、モデル別要約、同根所見集約、三段階トリアージ下書き、候補案、推薦案を作る。
2. proxy_model は重要件について、採用案、判断理由、棄却案理由、最終ラベルを決める。
3. 機械ガードは proxy decision、raw response、候補案、採用案、判断理由、triage との整合を検査する。
4. 実装サブ担当 LLM は、原則として別スレッドかつ分離 worktree で扱う。
5. 別スレッド生成物は、実装差分、検証結果、判断根拠、作業ノイズに分類する。
6. 作業ノイズは本線 repo に取り込まない。
7. コミット、プッシュ、spec.json 更新、フェーズ移行は人間の明示承認を要求し、proxy_model は代行しない。

## 今回の実装範囲

- `review_triage.py` の approval record 検査で `approved_by: proxy_model` を扱う。
- proxy approval では `proxy_decisions` に finding ごとの decision file を要求する。
- decision file には `approved_by: proxy_model`、`proxy_model_id`、`decision_prompt_path`、`source_raw_paths`、`candidate_options`、`selected_option`、`final_label`、`rationale`、`rejected_options`、`raw_response_path` を要求する。
- `raw_response_path` の実体が存在しなければ fail-closed にする。
- `decision_prompt_path` と `source_raw_paths` の実体が存在しなければ fail-closed にする。
- `candidate_options` が空または欠落していれば fail-closed にする。
- `approved_final_labels` と decision file の `final_label` が一致しなければ fail-closed にする。

## 今回はまだ実装しない事項

- 別スレッド作成や分離 worktree 作成の自動化。
- サブ担当への依頼テンプレート生成。
- サブ担当差分の許可ファイル外変更検査。
- triage / proxy decision / diff / test result の統合照合コマンド。

これらは、proxy approval gate が安定した後に段階的に追加する。

## 追加対応：自律・並列モード実行前ガード

自律・並列モードは、実装を始める前に実行計画 YAML を作り、`tools/check-workflow-action.py autonomous-plan <plan.yaml>` で機械検査する。

このガードは、次の事項を fail-closed で検査する。

1. 実行計画が `mode: autonomous_parallel` と `run_id` を持つ。
2. 人間または `proxy_model` の承認記録があり、レビュー結果サマリと三段階トリアージが利用者へ提示済みである。
3. 各タスクに `source_finding_ids`、担当、許可パス、期待テスト、停止条件がある。
4. 別スレッドまたはサブ担当へ渡すタスクは `separate_worktree` を使う。
5. 依存関係のない並列タスクが同じ `allowed_paths` を更新しない。
6. 統合ゲートとして、メインセッション確認、差分範囲確認、テスト確認、判断根拠確認を要求する。
7. 生成物分類として、実装差分、検証結果、判断根拠、作業ノイズの扱いを明示し、作業ノイズは本線 repo へ取り込まない。
8. `history.ledger_path` を `docs/logs/autonomous-parallel/` 配下に置き、task 割当、判断根拠、統合結果を後から追えるようにする。

重要件の修正は、レビュー結果の三段階トリアージ後に、候補案、推薦案、判断理由を提示し、承認または proxy decision が記録されるまで実装に進めない。自律実行中でも、`important_decision_requires_approval` が停止条件として各タスクに入っていない計画は逸脱とする。

```

## FILE: docs/logs/autonomous-parallel/2026-06-04-workflow-management-implementation-review-run-plan.yaml

```text
mode: autonomous_parallel
run_id: 2026-06-04-workflow-management-implementation-review-run
authorization:
  approved_by: user
  approval_record_path: .reviewcompass/specs/workflow-management/reviews/2026-06-04-implementation-triad-review-prep.md
  summary_presented_to_user: true
  triage_presented_to_user: true
tasks:
  - task_id: target-bundle
    source_finding_ids:
      - workflow-management-implementation-triad-review-prep
    assignee:
      kind: main_session
      worktree_policy: same_worktree
    allowed_paths:
      - .reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/review-target.md
      - .reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/target-source-manifest.yaml
    forbidden_paths:
      - .git/
    depends_on: []
    expected_tests:
      - python3 -m pytest tests/tools/test_workflow_management_implementation_triad_prep.py -q
    stop_conditions:
      - important_decision_requires_approval
  - task_id: api-primary
    source_finding_ids:
      - workflow-management-implementation-triad-review-prep
    assignee:
      kind: main_session
      worktree_policy: same_worktree
    allowed_paths:
      - .reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/raw/claude-sonnet-4-6.round-1.txt
      - .reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/parsed/claude-sonnet-4-6.round-1.yaml
    forbidden_paths:
      - .git/
    depends_on:
      - target-bundle
    expected_tests:
      - test -s .reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/raw/claude-sonnet-4-6.round-1.txt
    stop_conditions:
      - important_decision_requires_approval
  - task_id: api-adversarial
    source_finding_ids:
      - workflow-management-implementation-triad-review-prep
    assignee:
      kind: main_session
      worktree_policy: same_worktree
    allowed_paths:
      - .reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/raw/gpt-5.4.round-1.txt
      - .reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/parsed/gpt-5.4.round-1.yaml
    forbidden_paths:
      - .git/
    depends_on:
      - target-bundle
    expected_tests:
      - test -s .reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/raw/gpt-5.4.round-1.txt
    stop_conditions:
      - important_decision_requires_approval
  - task_id: api-judgment
    source_finding_ids:
      - workflow-management-implementation-triad-review-prep
    assignee:
      kind: main_session
      worktree_policy: same_worktree
    allowed_paths:
      - .reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/raw/gemini-3.1-pro-preview.round-1.txt
      - .reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/parsed/gemini-3.1-pro-preview.round-1.yaml
    forbidden_paths:
      - .git/
    depends_on:
      - target-bundle
    expected_tests:
      - test -s .reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/raw/gemini-3.1-pro-preview.round-1.txt
    stop_conditions:
      - important_decision_requires_approval
  - task_id: aggregate-review-run
    source_finding_ids:
      - workflow-management-implementation-triad-review-prep
    assignee:
      kind: main_session
      worktree_policy: same_worktree
    allowed_paths:
      - .reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/target-manifest.yaml
      - .reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/rounds.yaml
      - .reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/model-result-summary.yaml
      - .reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/triage.yaml
      - .reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/review_summary.md
    forbidden_paths:
      - .git/
    depends_on:
      - api-primary
      - api-adversarial
      - api-judgment
    expected_tests:
      - python3 -m pytest tests/tools/test_workflow_management_implementation_triad_prep.py -q
    stop_conditions:
      - important_decision_requires_approval
integration_gate:
  requires_main_session_review: true
  requires_diff_scope_check: true
  requires_tests: true
  requires_decision_basis_review: true
history:
  ledger_path: docs/logs/autonomous-parallel/2026-06-04-workflow-management-implementation-review-run.yaml
  record_task_assignments: true
  record_decision_basis: true
  record_integration_result: true
  retention: preserve
outputs_policy:
  implementation_diff: commit_candidate
  verification_summary: required
  decision_basis: preserve_if_used
  work_noise: exclude

```

## FILE: docs/logs/autonomous-parallel/2026-06-04-workflow-management-implementation-review-run.yaml

```text
run_id: 2026-06-04-workflow-management-implementation-review-run
mode: autonomous_parallel
verdict: OK
exit_code: 0
reasons: []
task_ids:
- target-bundle
- api-primary
- api-adversarial
- api-judgment
- aggregate-review-run
authorization:
  approved_by: user
  approval_record_path: .reviewcompass/specs/workflow-management/reviews/2026-06-04-implementation-triad-review-prep.md
  summary_presented_to_user: true
  triage_presented_to_user: true
history:
  ledger_path: docs/logs/autonomous-parallel/2026-06-04-workflow-management-implementation-review-run.yaml
  record_task_assignments: true
  record_decision_basis: true
  record_integration_result: true
  retention: preserve
integration_gate:
  requires_main_session_review: true
  requires_diff_scope_check: true
  requires_tests: true
  requires_decision_basis_review: true
outputs_policy:
  implementation_diff: commit_candidate
  verification_summary: required
  decision_basis: preserve_if_used
  work_noise: exclude
current_state:
  mode: autonomous_parallel
  run_id: 2026-06-04-workflow-management-implementation-review-run
  task_count: 5
  parallel_task_count: 1
  checked_gates:
  - requires_main_session_review
  - requires_diff_scope_check
  - requires_tests
  - requires_decision_basis_review
  history_ledger_path: docs/logs/autonomous-parallel/2026-06-04-workflow-management-implementation-review-run.yaml
  plan_path: docs/logs/autonomous-parallel/2026-06-04-workflow-management-implementation-review-run-plan.yaml

```
