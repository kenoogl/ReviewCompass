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
4. 機能横断段の場合、`feature_order` フィールドで `feature-dependency.yaml#feature_order` を参照する（旧称 `phase_order`。Requirement 8 受入 2 の由来注記を参照）。
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
6. 本検査スクリプトは next サブコマンドを標準のワークフロー遷移入口として提供し、`workflow_state`、`stages/in-progress/`、post-write-verification pending、reopen pending、上流成果物が下流成果物より新しい状態から次に実行すべき作業を機械的に返す。完了済み workflow であっても、intent が feature-partitioning より新しい場合は機能分割確認、requirements が design より新しい場合は design 再確認、tasks が implementation 成果物より新しい場合は implementation 再確認のように、上流から下流への再展開を next action として返す。
7. 本検査スクリプトは post-write target detection と manifest verification を workflow-management の実装契約として扱う。post-write-verification 対象の未コミット変更がある場合、通常 workflow へ進ませず、completed manifest の `target_files`、`target_sha256`、`required_verifiers`、`verifications[]`、`unresolved_substantive_findings` に基づいて完了可否を判定する。
8. 本機能は `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml` を、判定点ごとに読み込む規律文書と入力資料の機械可読マップとして所有する。`next` はこのマップを読み、`next_action.required_disciplines` と `next_action.required_inputs` を返す。判定点ごとの `effective prompt` は、このマップが示す元資料を束ねて生成・記録する。`next` は生成した prompt の `effective_prompt_path`、`effective_prompt_sha256`、`effective_prompt_loaded` を `next_action.effective_prompt` に含める。元資料をすべて読めない場合は `effective_prompt_loaded: false` とし、fail-closed で通常作業へ進ませない。review-run 実行時は `rounds.yaml` に `effective_prompt_path` と `effective_prompt_sha256` を記録する。

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
5. 本機能はコミット直前ゲートで commit 承認レコードを要求する。承認レコードは `approved_action=commit`、`approved_by=user`、未消費状態、staged ファイルの被覆に加え、staged 内容と一致する `target_sha256` を対象ファイルごとに保持しなければならない。`target_sha256` が欠落、形式不正、または staged 内容と不一致の場合は fail-closed で遮断する。

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
7. 本機能は、通常の `next_action` と異なる side track、または `next` 判定自体の欠陥修復に着手する場合、ファイル編集前に `process_id: maintenance` の進行中ファイルを作成することを要求する。maintenance 進行中ファイルは `trigger`、`mainline_blocked_by`、`allowed_scope`、`allowed_files`、`completion_conditions` を保持する。

### Requirement 7：多層防御の位置付け

**目的**：保守担当者が、本機能（軽量版 YAML 検査機構）が多層防御の第 1 層であることを理解し、過剰な期待をしないようにする。100% の規律遵守は原理的に不可能であり、複数層を重ねて実効遵守率を引き上げる方針。

#### 受入基準

1. 本機能は自身を多層防御の第 1 層として位置付け、第 1 層が解決しない失敗モード（中身の空疎、検査スクリプトの呼び出し依存、in-progress ファイルの自己申告性、文脈圧力下での規律低下、§5.8 由来）を明文化する。
2. 本機能は第 2〜5 層（git フックによる外部強制、フェーズ境目の利用者監査、定期事後監査、処理表面積の抑制方針）をフェーズ 4 以降の宿題として参照する。
3. 本機能は第 5 層（処理表面積の抑制方針）の運用ルール「新規規律を追加するときは既存規律 1 つ以上を統廃合する」を本機能の運用ルールに反映する（フェーズ 4 までは利用者の意識に依拠、機械強制は第 5 層導入時に検討）。
4. 本機能は第 1 層の限界を運用文書に明示し、利用者の期待値を整える。
5. 本機能は自律・並列実行を行う場合の安全契約として、自律 plan と履歴 ledger を検査対象に含める。自律 plan は run ID、依存順、recheck 対象、許可パス、期待テストを明示し、履歴 ledger は実行結果、統合判断、検証コマンド、未解決 blocker を追跡する。未記録依存や上流 recheck の下流反映が必要になった場合は、統合判断に戻るまで当該作業を進めない。

### Requirement 8：機能依存マップの一元化

**目的**：保守担当者が、機能間の処理順と依存関係を 1 箇所で管理できるようにする。各フェーズの YAML がこのマップを参照することで、機能の追加・削除や依存関係の変更が 1 箇所のみの修正で完結する。

#### 受入基準

1. 本機能は `feature-dependency.yaml` を機能間処理順と依存関係の一元保管先とする。開発リポジトリでは `stages/feature-dependency.yaml` に置く。対象アプリでは feature-partitioning の承認結果を `.reviewcompass/feature-dependency.yaml` として実体化する（設計記録 `docs/notes/2026-06-10-deployment-multi-llm-entry-design.md` §3.5 由来、2026-06-12 反映）。
2. 本ファイルは最低限、`features`（機能ごとの `depends_on` 列挙）と `feature_order`（機能間処理順）を含む。`depends_on` の値は単純なリスト構造（例：`[foundation, runtime]`）、または依存種別（`hard`／`review`）を持つ連想配列構造（例：`foundation: hard, runtime: review`）の両方を許容する。後者は `conformance-evaluation` のように依存性の強度を区別する機能で使う（計画書 §5.5 行 368〜373 由来）。**由来注記**：旧称 `phase_order`（計画書 §5.5 および `stages/feature-partitioning/2026-05-24-proposal.md` の表記）は `feature_order` と同一物である。過去記録（レビュー記録・分割提案書・計画書）は書き換えず、本注記で読み解く（語彙調停 案 A、MLE-DEC-001、2026-06-12 利用者決定）。
3. 各フェーズの YAML（`requirements.yaml`／`design.yaml`／`tasks.yaml`／`implementation.yaml`）の草案段とレビュー波段は `feature_order: <feature-dependency.yaml#feature_order>` の参照を持つ。
4. 機能の追加・削除や依存関係の変更は本ファイル 1 箇所の修正で完結する（計画書 §5.5 選択肢 X：独立 YAML 参照方式）。
5. 機能間依存マップの所有者は本機能であり、`runtime`／`evaluation` 等の他機能は再定義せず参照のみとする。
6. 検査ツール（Requirement 2）は feature 一覧と機能順を `feature-dependency.yaml` の `feature_order` キーから解決する。探索はツール実行時のカレントディレクトリを基準に、相対パス `.reviewcompass/feature-dependency.yaml` → `stages/feature-dependency.yaml` → `feature-dependency.yaml` の順で行い、最初に存在したファイル 1 つだけを読む。親ディレクトリへの遡上探索は行わない。直下の `feature-dependency.yaml` は標準 2 配置（受入 1：対象アプリ＝`.reviewcompass/`、開発リポジトリ＝`stages/`）のいずれにも該当しない配置への後方互換の受け皿であり、標準配置としては使わない。「一元保管先」（受入 1）とは、この探索で選ばれる実行文脈ごとの単一ファイルを指し、同一実行で複数ファイルを併読しない。ソース直書きの既定機能順（`tools/check-workflow-action.py` 内の既定定数）は `next` 判定では解決結果で上書きされる（2026-06-12 反映、MLE-C-001。探索基準の精密化は triad-review クラスタ A・F1・F2 対処）。
7. 検査ツールは `feature_order` が `depends_on` と矛盾しない順序であること（依存される機能［依存先］を、依存する機能［依存元］より先に置くこと。例：runtime が foundation に依存する場合、foundation を runtime より先に置く）、および循環依存がないことを機械検査する。違反時、`next` は `next_action.kind: unknown` を返し、違反内容を出力の `reasons` 配列に理由として列挙し、verdict は DEVIATION（exit code 2、fail-closed）とする（2026-06-12 反映、MLE-C-003。出力形式の明記は triad-review クラスタ B・D・F3 対処）。
8. feature 一覧が解決できない場合のうち、`feature-dependency.yaml` がどの探索先にも存在しない、または `feature_order` キーが未定義の場合、検査ツールはエラーではなく `next_action.kind: feature_definition_required`（verdict OK、exit code 0）を返し、intent／feature-partitioning の実施と、承認された分割結果（依存の根拠と順序の導出を含む）の `feature-dependency.yaml` への記録を案内する（2026-06-12 反映、MLE-C-002）。
9. 受入 6 の探索で選ばれた（最初に存在した）1 ファイルが、YAML として読めない（パース不能）、空（内容なし）、または最上位が連想配列でない場合は、未定義と区別して遮断する。これらはファイルそのものの破損・構造異常であり、読み込み後の値の整合検査（受入 7）とは別であって、判定は受入 9 を受入 7 より先に行う。`next` は `next_action.kind: unknown`（既存の判定種別。受入 7 の整合違反と同じ kind で、WORKFLOW_DISCIPLINE_MAP.yaml に登録済み）を返し、破損ファイルのパスと内容確認を促す理由（空の場合は `feature_order` の記録を促す理由）を `reasons` 配列に列挙し、verdict は DEVIATION（exit code 2、fail-closed）とする。破損を立ち上げ案内で覆い隠さない（2026-06-12 反映、MLE-DEC-005。同日の triad-review F4 では現挙動の明文化（案 a）をいったん採ったが、利用者決定により遮断へ改めた。FUP-2026-06-12-001 の解消。境界の精密化は同日 triad-review 対処）。

### Requirement 9：既存システムへの後追い intent 追加時の下流再展開

**目的**：保守担当者が、既に requirements／design／tasks／implementation が存在するシステムへ intent を後から追加した場合でも、仕様駆動開発の順序を崩さず、既存設計との衝突確認を含めて下流工程へ進められるようにする。

#### 受入基準

1. 本機能は、既存システムで intent が追加または修正された場合、機能分割で受け皿 feature を判定し、受け皿がある feature は reopen 対象、受け皿がない場合は新 feature 候補として扱う。
2. 本機能は、既存 requirements に似た記述があることだけを理由に処理を終了しない。該当 feature を reopen し、requirements／design／tasks／implementation の各段で、修正不要か修正必要かを判定して記録する。
3. 本機能は、下流工程の各段で既存仕様との衝突確認を要求する。新しい要件や設計が既存設計、既存タスク、既存実装と矛盾する可能性がある場合は、衝突候補として記録し、reopen record の `current_blocker` に人間承認待ちを設定するか、該当 phase の approval gate で停止する。停止解除には、判定対象 gate、feature scope、判断、理由、証跡、判定者を `downstream_impact_decisions` に記録することを必要とする。
4. 本機能は、コード由来の仕様差分抽出を `conformance-evaluation` の評価記録として受け取り、正式な requirements／design／tasks／implementation 更新は本機能の reopen 手続きで進める。受け取り対象の評価記録は、最低限 `feature`、`phase`、`classification`、`code_refs`、`existing_spec_refs`、`reasoning_summary`、`needs_human_decision` を持つ候補一覧を含む。
5. 本機能は、後追い intent 追加が既存 implementation まで影響する可能性を持つ場合、`impacted_downstream_phases` に requirements、design、tasks、implementation を含める。各段で `existing_sufficient` と判定する場合も、その判定対象 gate、feature scope、理由、証跡、判定者を `downstream_impact_decisions` に残す。
6. 本機能は、ReviewCompass 自身を試行対象にした場合も、通常の所定手続きとして扱う。試行中にワークフロー手続きの不足が見つかった場合は、本線作業と side track を区別し、必要なら `stages/in-progress/maintenance-*.yaml` を作成する。maintenance 進行中ファイルは、本線の `mainline_blocked_by`、許可範囲、許可ファイル、完了条件を持ち、完了時は `stages/completed/maintenance-*.yaml` に移す。

### Requirement 10：review-wave 横断確認の要約コマンド

**目的（Objective）**：保守担当者が、review-wave（機能横断段）の横断確認で用いる指標を、手動集計ではなく機械的に生成・再現できるようにする。集計漏れや報告の揺れを防ぐ。本要件は Requirement 1 が定める「段集合 YAML による静的列挙」と Requirement 2 の検査スクリプトを土台に、横断確認の指標化を機能内の静的検査として位置づける（新しい意図を要さない。2026-06-14 reopen R-0、利用者決定）。

#### 受入基準（Acceptance Criteria）

1. 本機能は、review-wave の横断確認指標を機械生成する要約コマンド（Requirement 2 の検査スクリプトのサブコマンド、または同等の helper）を提供する。読み取り元は次とし、手動集計に依存しない：各 feature の spec.json の `workflow_state` と `recheck`、`stages/in-progress/`、機能依存マップ（Requirement 8 の `feature_order`）、各 review-run の `triage.yaml`（triage 件数の算出元）、機能横断持ち越し所見記録（carry-forward register、`learning/workflow/carry-forward-register/`）。各指標の厳密な算出定義（フィールド対応・集計規則）の詳細は design で確定する。
2. 本コマンドの出力項目は最低限、次を含む：feature coverage（機能ごとの段到達状況）、各機能の phase／stage 状態、triage の未解決（unresolved）件数・draft 件数・human_required 件数、recheck 状態（`upstream_change_pending` と `impacted_downstream_phases`）、依存状況（`feature_order` と未充足依存）、carry-forward（機能横断持ち越し所見）の未消化件数。
3. 本コマンドは出力形式として Markdown と JSON の両方を提供し、両者は情報同等とする。JSON は機械処理用に安定したスキーマ（キー構造・型）を持ち、その確定は design で行う。Markdown は人が読む横断確認用とする。
4. 本コマンドは結論不能（必要な記録が解析不能・欠落。解析不能の範囲は Requirement 2 受入 4 に従う）の場合、合格や完了を主張しない。機械可読な失敗シグナルとして**非ゼロ終了コード**を返し、JSON 出力に不能を示す機械可読な `status` を含め、Markdown でも完了と誤読されない明示をする。部分集計値を完了として扱わない（第 1 層の限界・fail-closed と整合、Requirement 2 受入 4・Requirement 7）。
5. 本コマンドは集計（読み取り）に徹し、`spec.json`・フェーズ状態・トリアージ判断を書き換えない（Requirement 3 受入 5 の proxy_model 非代行範囲、および Requirement 4 受入 1 の不可逆操作と整合）。書き出しは自身の要約出力に限り、保存先は `.reviewcompass/specs/_cross_feature/reviews/` とする（保存はオプションで既定は標準出力。自身の要約出力の書き出しは状態変更に当たらない）。

由来：D-001（review-wave summary command）。要件正本は `docs/notes/2026-06-04-implementation-review-wave-improvements.md` と `docs/notes/2026-06-05-future-development-candidates.md`。分類は 2026-06-14 reopen R-0（`docs/reviews/reopen-classification-2026-06-14-wm-review-wave-summary-command.md`）。実装は仕様確定後に TDD で行う正順の手続きとする。

### Requirement 11：重要決定の出典検査（裁定負荷対策）

**目的（Objective）**：保守担当者が、重要決定（不可逆操作・規律変更・仕様／計画変更に限定）の確定について、出典の有無・束ね・逐語一致・内容性を機械検査できるようにし、一括承認のなかに重要な件が埋もれて正しく裁定されないまま確定する誤り（裁定負荷）を防ぐ。本要件は新しい規律を導入するのではなく、既存規律 `discipline_approval_operation`（確定記述に出典必須・出典なし禁止・機械検査は承認の代替でない）と `discipline_plain_explanation_each_step`（重要承認は 1 件ずつ）を機械強制するものであり、Requirement 1 が定める静的検査と Requirement 4 が定める不可逆操作の直前ゲートの範囲に位置づける（新しい意図を要さない。2026-06-15 reopen R-0、利用者決定）。

#### 受入基準（Acceptance Criteria）

1. 本機能は、機械検査を可能にする構造化した重要決定の記録形式を定める。記録は最低限、決定 ID、重要種別（不可逆操作／規律変更／仕様・計画変更のいずれか）、決定文言、出典（出典の引用、セッション ID、出典発言を一意に特定するロケータ〔会話転写内の位置情報〕、当該出典が単一決定に対応するか複数決定で共有されるかの区分）を持つ。重要種別は不可逆操作・規律変更・仕様／計画変更に限定し、各種別の境界は既存の Requirement 4（不可逆操作の直前ゲート対象）を基準に判定する。仕様／計画変更は spec.json・requirements／design／tasks・計画文書の確定的変更を指し、軽微なタスク状態更新（段フラグの true/false 更新、進行中ファイルへの作業ログ追記など、新たな確定的決定を伴わない状態反映）とは区別する（境界の細目は design で確定）。本記録形式は going-forward の新規重要決定から適用し、過去の散文の決定台帳は遡及移行しない。記録形式の厳密なスキーマ（フィールド名・型・配置先・ロケータの表現）は design で確定する。
2. 本機能は、束ね検出を行う。複数の重要決定が同一の出典（同じ一回の承認発言）を共有している場合、それらを確定扱いにさせない（fail-closed、非ゼロ終了）。束ねの例外は原則認めず、避けられない場合も各決定が個別の出典・ロケータ・区分を持つことを確定の必要条件とする（束ね一括では確定させない）。束ね例外の適用（「避けられない場合」の判定）は機械が自動で認めず、機械は束ねを検出して fail-closed するに留め、例外適用は人の明示承認に委ねる。例外時の具体的な扱い・記録方法は design で確定するが、この「個別出典なしには確定させない」という必要条件は design で緩めない。
3. 本機能は、逐語照合を行う。各重要決定の出典の引用が、repo に取り込み済みの会話転写（層 1、`.reviewcompass/evidence/sessions/`）に逐語で存在するかを機械照合する。逐語で存在しない（言い換え・でっち上げ）場合は fail-closed とする。出典が現在進行中（未取り込み）のセッションの発言である場合は、確定操作（不可逆操作の直前ゲート）と転写取り込みの順序依存によるデッドロックを避けるため、次のとおり扱う。(i) 当該決定を「未検証（保留）」として記録し、検証済みの確定済み重要決定として扱わない（後続の確定や承認の根拠に用いない。直前ゲートを通過させて確定済みと見なすことはしない＝fail-closed の抜け道を作らない）。(ii) 直前ゲートは未取り込み出典の即時照合合格を確定の条件として強制しないことで作業の進行（コミット等）自体はブロックしないが、当該決定の「確定」は保留のままとする。(iii) 当該セッションの転写が層 1 へ取り込まれた後に逐語照合し、合格して初めて確定とする。取り込み・照合が行われない限り当該決定は未検証のままで、タイムアウト等で確定へ昇格させない。照合の対象範囲・正規化（空白・改行等）の規則、および保留状態の管理と後追い確定の順序制御の仕組みは design で確定する。
4. 本機能は、内容性検査を行う。「OK」「承認」等の内容を持たない返事だけを、重要決定の唯一の出典として認めない。検査は機械的に検出し fail-closed とする。内容なしとみなす語の判定基準は拡張可能なリストで管理し、その確定は design で行う。リストの拡張は規律変更扱いとし人の明示承認を要する。
5. 本機能は、検査（読み取り）に徹し、`spec.json`・フェーズ状態・決定記録そのものを書き換えない（Requirement 3 受入 5 の proxy_model 非代行範囲、および Requirement 4 受入 1 の不可逆操作と整合）。ただし `--verify-pending` による `verification_status`（pending → verified）と `verified_at` フィールドの更新のみを例外とし、design で明示的に確定する（書き換えられるフィールドは `verification_status`・`verified_at` の 2 フィールドに限定し、`statement`・`source`・`category` は書き換えない）。必要な記録が解析不能・欠落で結論不能の場合、合格や完了を主張せず、非ゼロ終了と機械可読な `status` で fail-closed とする（Requirement 2 受入 4・Requirement 7 と整合）。
6. 本機能の検査範囲は、出典の存在・束ね・逐語一致・内容性という機械的に判定可能なものに限定する。決定文言が利用者の意図を正しく汲んでいるかという意味一致の最終判断は機械で行わず、人または判定役（会話転写との突き合わせ）に委ねる。本機能は意味一致を「検証可能化」する（突き合わせに必要な出典と転写を提示する）ところまでを担う。
7. 本機能は、本検査を Requirement 2 の検査スクリプトのサブコマンドとして提供することを必須とする（基線）。加えて、Requirement 4 の不可逆操作の直前ゲート（commit 直前検査）へ組み込むかどうかは、組み込みの可否・発火条件を含めて design で確定する（設計上の拡張であり必須ではない）。これにより接続点を「必須のサブコマンド提供」と「設計判断の直前ゲート組み込み」に分け、達成条件を一意にする。

由来：裁定負荷対策（利用者決定の埋没防止）。動機事例は PLC-DEC-007 の誤記録（6 論点の一括確認表＋包括「OK」により、利用者発言と食い違う決定文言が裁定されないまま台帳化された。訂正記録は `docs/notes/2026-06-12-document-placement-stage2-decisions.md` の PLC-DEC-007 2026-06-13 訂正欄）。方針は 2026-06-13 利用者決定「(b) で対応」、検査方針（束ね検出・逐語照合・内容性、重要種別限定）の確定は 2026-06-14 利用者決定。分類は 2026-06-15 reopen R-0（`docs/reviews/reopen-classification-2026-06-15-wm-decision-source-lint.md`）。実装は仕様確定後に TDD で行う正順の手続きとする。

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
- 2026-06-08 の feature-partitioning 再確認により、intent の「レビュー収集処理を事前設定の写像にしない」意図は新機能追加を要さず、workflow-management では Requirement 2 の `next` による上流から下流への再展開、Requirement 4 の不可逆操作直前ゲート、Requirement 6 の session 跨ぎ状態管理、および Requirement 8 の機能依存マップ一元化で受けることを確認した。
- 2026-06-08 の reopen 判定修正により、完了済み workflow で上流正本が後続成果物より新しい場合は、`next` が単なる再確認ではなく `reopen_classification_required` を返し、reopen 分類と `reopen-start` へ進ませることを Requirement 2 の判定責務に含める。
- 2026-06-09 の再確認により、後追い intent 追加を既存システムに適用する場合は、既存 requirements の有無だけで終了せず、受け皿 feature を reopen して requirements／design／tasks／implementation へ順に再展開することを Requirement 9 に明示した。
- 2026-06-09 の判定点プロンプト方針確認により、`WORKFLOW_DISCIPLINE_MAP.yaml` を判定点ごとの `required_disciplines`／`required_inputs` の正本として Requirement 2 に明示した。将来の `effective prompt` はこのマップの元資料を束ねる。
- 2026-06-12 の reopen R-0（conformance 評価 `2026-06-12-completed-followup-conformance.md` の gap 反映）により、Requirement 8 へ feature 一覧解決の外出し（受入 6：`feature_order` キーと探索順）、整合検査（受入 7）、立ち上げ案内（受入 8：`feature_definition_required`）を追加した。語彙は利用者決定（案 A、MLE-DEC-001）により実装語彙 `feature_order` へ統一し、旧称 `phase_order` は受入 2 の由来注記で読み解く。実装は先行済み（コミット cde1f5c、maintenance side track `stages/completed/maintenance-2026-06-11-feature-order-generalization.yaml`）で、本改訂は仕様の追認である。
- 2026-06-12 の reopen R-0（parse-error-failclosed、MLE-DEC-005）により、Requirement 8 受入 9 を新設し、パース不能ファイルの扱いを立ち上げ案内（OK）から遮断（DEVIATION、fail-closed）へ改めた。本改訂は実装先行ではなく、仕様確定後に TDD で実装する正順の手続きである。
- 2026-06-14 の reopen R-0（review-wave-summary-command、D-001）により、Requirement 10 を新設し、review-wave 横断確認指標の機械生成（要約コマンド）を機能内の静的検査として要件化した。分類は意図文書を改めず既存「静的検査」（Requirement 1）の範囲に含める R-0 とした（2026-06-13 記録の R-1 ラベルと併記説明文の食い違いを 2026-06-14 に利用者と確認のうえ R-0 を採用。根拠は `docs/reviews/reopen-classification-2026-06-14-wm-review-wave-summary-command.md`）。本改訂は仕様確定後に TDD で実装する正順の手続きである。
- 2026-06-15 の reopen R-0（decision-source-lint）により、Requirement 11 を新設し、重要決定の出典検査（束ね検出・逐語照合・内容性）と構造化した重要決定の記録形式を要件化した。既存規律 `discipline_approval_operation`／`discipline_plain_explanation_each_step` の機械強制であり、意図文書を改めず既存「静的検査」（Requirement 1）と「不可逆操作の直前ゲート」（Requirement 4）の範囲に含める R-0 とした（根拠は `docs/reviews/reopen-classification-2026-06-15-wm-decision-source-lint.md`）。動機事例は PLC-DEC-007 の誤記録（裁定負荷）。本改訂は仕様確定後に TDD で実装する正順の手続きである。

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
- 参考：他機能の所見（A-001／A-003／A-004 とも 2026-05-23 対処済み）の対処履歴は carry-forward register 正本 [reviewcompass-import.yaml](../../../learning/workflow/carry-forward-register/reviewcompass-import.yaml) を参照

## 実装由来契約の波及トレース

- `XDI-WM-001`：post-write verification、commit approval、audit trail、autonomous ledger は、Requirement 2／3／4／8 の外部可視要件にまたがる。詳細な設計採用は design.md §実装由来契約の採用を正本とし、本 requirements.md は要件層から追跡可能であることを示す。
- `XDI-WM-002`：既存システムへの後追い intent 追加時に、受け皿 feature の reopen、下流工程の修正要否判定、既存設計との衝突確認、conformance-evaluation 評価記録の正式手続きへの取り込み、衝突候補発見時の停止・承認・記録を行う契約は Requirement 9 の外部可視要件に含める。詳細な設計・タスク化は design／tasks 段で確定する。
