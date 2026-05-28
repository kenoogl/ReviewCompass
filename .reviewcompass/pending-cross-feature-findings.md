# 機能横断レビューで扱う所見の集約

最終更新：2026-05-23（用語「遡及／波及」を二軸的定義に訂正）

本文書は、各機能の triad-review 段で露出した **機能横断の波及所見**を集約する。これらは個別機能の triad-review 段では対処せず、要件フェーズの **review-wave**（複数機能を横断する複数ラウンドレビュー、計画書 §5.5）または **alignment／approval**（フェーズ終端の機能横断整合確認、責務分離による 5 段化後の段集合）で扱う。

## 1. 集約の根拠

機能横断の波及（はきゅう）所見は、ある機能のレビューが **同フェーズ内の別機能** との不整合を露出させる現象。性格として：

- **波及と遡及の使い分け**：波及は同フェーズ内の他機能への影響、遡及は上流フェーズへの影響。両者は対象方向が異なる正当な技術用語で、優劣はない（二軸的定義、2026-05-23）。本ファイルが集約するのは **波及（同フェーズ・機能間）** のもの
- **発生原因**：機能間の整合は機能を増やすほど明らかになる通常現象（過去の作業の過失ではない）
- **段の所属**：個別機能の drafting 段の責務ではなく、review-wave／alignment／approval の機能横断段の責務（§5.5、責務分離による 5 段化を反映）
- **持ち越し管理**：本ファイルで集約し、各フェーズの機能横断段（review-wave／alignment／approval）着手時に消化

## 2. 運用ルール

- 各機能の drafting 段の local review で機能横断の波及所見が出たら、本ファイルに追記する
- 追記項目は、所見 ID（元レビュー記録）、波及範囲（影響を受ける機能と仕様箇所）、対処方針、検出セッション・日付
- 要件 review-wave 着手時、本ファイルの全件を消化対象とする
- 消化後、該当所見を本ファイルから「対処済み」節に移動するか、削除する

## 3. 未消化の所見

### A-001：validator_status 正本 4 値のうち not_run が両仕様で欠落 ✅ 対処済み（2026-05-23、要件 review-wave）

- **対処内容**：foundation Req 6 受入 10 を 4 値（`not_run`／`passed`／`failed`／`blocked`）に拡張、runtime Req 6 受入 2 で foundation 4 値への参照を明示
- **検出**：セッション 19、runtime requirements の敵対役レビュー（Sonnet 4.6）
- **記録**：[.reviewcompass/specs/runtime/reviews/2026-05-22-requirements.md](specs/runtime/reviews/2026-05-22-requirements.md) §2 独立発見 A-001
- **重大度**：WARN
- **判定**：must-fix（runtime レビューの判定役 Haiku 4.5 が認定）
- **波及範囲**：
  - **runtime**：`.reviewcompass/specs/runtime/requirements.md` §Requirement 6 受入 2 の `validator_status` 語彙（現在 3 値「passed／failed／blocked」、`not_run` 欠落）
  - **foundation**：`.reviewcompass/specs/foundation/requirements.md` §Requirement 6 受入 10 の `validator_status` 語彙（現在 3 値、同様の欠落）
- **正本との不整合**：計画書 §5.18.7 行 2239 で `validator_status` の正本値は `not_run`／`passed`／`failed`／`blocked` の 4 値、所有者は foundation
- **対処方針**：runtime Req 6 受入 2 と foundation Req 6 受入 10 の両方に `not_run` を追加。foundation を語彙正本として明示し、runtime は再定義せずに参照
- **依存関係**：runtime の修正は foundation の修正と同時に行う必要がある（順序：foundation が正本所有なので foundation を先に直す）

### A-003：evidence_class 正本 4 値のうち analysis_blocked が foundation 仕様で欠落 ✅ 対処済み（2026-05-23、要件 review-wave）

- **対処内容**：foundation Req 6 受入 8 を 4 値（`valid`／`invalid`／`exploratory`／`analysis_blocked`）に拡張、evaluation Req 1 受入 1 と Req 6 受入 4 で foundation 4 値への参照を明示
- **検出**：セッション 19、evaluation requirements の敵対役レビュー（Sonnet 4.6）
- **記録**：[.reviewcompass/specs/evaluation/reviews/2026-05-22-requirements.md](specs/evaluation/reviews/2026-05-22-requirements.md) §2 独立発見 A-003
- **重大度**：WARN
- **判定**：must-fix（evaluation レビューの判定役 Haiku 4.5 が認定、ただし本セッションでは持ち越し）
- **波及範囲**：
  - **foundation**：`.reviewcompass/specs/foundation/requirements.md` §Requirement 6 受入 8 の `evidence_class` 語彙（現在 3 値「valid／invalid／exploratory」、`analysis_blocked` 欠落）
  - **evaluation**：`.reviewcompass/specs/evaluation/requirements.md` §Requirement 6 受入 4「致命的失敗と探索的部分分析を区別する」への正本語彙参照が未明示
- **正本との不整合**：計画書 §5.17.3 行 2031〜2038 で 4 状態区分（`valid`／`invalid`／`exploratory`／`analysis_blocked`）が正本として明示。`analysis_blocked` は「必要入力の不足、または実行未終了、または検証が前提不足で結論不能」を表す
- **対処方針**：foundation Req 6 受入 8 に `analysis_blocked` を追加し 4 値に拡張。evaluation Req 6 受入 4 に foundation 4 値語彙への明示参照を追加
- **依存関係**：foundation 修正（語彙正本所有者）を先、evaluation 修正を後

### A-004：evaluation に経路別差分出力の受入基準が欠落 ✅ 対処済み（2026-05-23、要件 review-wave）

- **対処内容**：evaluation Req 9 に受入 7 を追加（3 経路別の所見差分を analysis 向けに提供、最低限の構造化形式 4 要素を明示）。analysis Req 7 受入 3 と整合
- **検出**：セッション 19、analysis requirements の敵対役レビュー（Sonnet 4.6）
- **記録**：[.reviewcompass/specs/analysis/reviews/2026-05-22-requirements.md](specs/analysis/reviews/2026-05-22-requirements.md) §2 独立発見 A-004
- **重大度**：WARN
- **判定**：must-fix（analysis レビューの判定役 Haiku 4.5 が認定、ただし本セッションでは持ち越し）
- **波及範囲**：
  - **analysis**：`.reviewcompass/specs/analysis/requirements.md` §Requirement 7 受入 3「3 経路の所見出力の差分を可視化に渡す」が成立するには、evaluation 側に対応する出力責務が必要
  - **evaluation**：`.reviewcompass/specs/evaluation/requirements.md` に「3 経路（レビューモード）別の所見差分を analysis 向け出力として提供する」受入基準を追加する必要
- **対処方針**：evaluation の Requirement 4（構造化された証拠の出力）または Requirement 9（レビューモードの区別）に「3 経路別差分の analysis 向け出力」受入基準を追加。analysis 側 Req 7 受入 3 はそのまま
- **依存関係**：evaluation 側の修正のみで成立、analysis 側は変更不要

### A-005：conformance-evaluation の feature-dependency 依存記述反映予定 ✅ 対処済み（2026-05-23、要件 review-wave 確認）

- **対処内容**：workflow-management Req 8 受入 2 で連想配列構造（hard/review）対応のスキーマ拡張、conformance-evaluation Req 7 で依存種別の連想配列構造を明示。両仕様の整合を 2026-05-23 の review-wave で確認済み
- **検出**：セッション 19、workflow-management requirements の敵対役レビュー（Sonnet 4.6）
- **記録**：[.reviewcompass/specs/workflow-management/reviews/2026-05-22-requirements.md](specs/workflow-management/reviews/2026-05-22-requirements.md) §2 独立発見 A-005
- **重大度**：WARN
- **判定**：must-fix（workflow-management レビューの判定役 Haiku 4.5 が認定）
- **workflow-management 側**：本セッション内で対処済み（Req 8 受入 2 のスキーマ定義を依存種別対応に拡張）
- **conformance-evaluation 側（残課題）**：将来の conformance-evaluation requirements.md 作成時に、計画書 §5.5 行 368〜373 の連想配列構造（`foundation: hard`／`runtime: review`／`evaluation: review`／`workflow-management: review`）を仕様内で明示する必要
- **対処方針**：conformance-evaluation 抽出時に、`Requirement N（feature-dependency.yaml への依存記述）`を追加するか、Boundary Context の隣接期待で依存種別を明示
- **依存関係**：本所見は workflow-management 側のスキーマ拡張で部分対処済み。残るは conformance-evaluation 側の対応のみ

### A-007：self-improvement と workflow-management の規律変更権・手続き実行権の調停ルール未定義 ✅ 対処済み（2026-05-23、要件 review-wave、利用者判断 案 2）

- **対処内容**：利用者承認の案 2（workflow-management の所定手続き経由で実体変更）を採用。self-improvement Req 1 受入 4 を「変更の提案権を持ち、実体変更は workflow-management の所定手続き経由で実行」に修正。workflow-management の Boundary Context 隣接期待に「self-improvement からの規律変更提案を所定手続きの入力として受け取り、承認後に本機能が実体変更を実施」を追加。規律変更を不可逆操作（Req 4 受入 1）の対象として扱う
- **検出**：セッション 19、self-improvement requirements の敵対役レビュー（Sonnet 4.6）
- **記録**：[.reviewcompass/specs/self-improvement/reviews/2026-05-22-requirements.md](specs/self-improvement/reviews/2026-05-22-requirements.md) §2 独立発見（機能横断）
- **重大度**：WARN
- **波及範囲**：
  - **self-improvement**：`.reviewcompass/specs/self-improvement/requirements.md` Requirement 1 受入 4（「規律ファイルの作成・更新・退避・統廃合の責務を持つ」）
  - **workflow-management**：`.reviewcompass/specs/workflow-management/requirements.md` Requirement 2 受入 3 および Requirement 6（「規律の昇格・退避・統廃合を所定手続き drafting → review → approval に従って実行」）
- **不整合内容**：規律ファイルの変更権（self-improvement が正本所有者として直接変更）と手続き実行権（workflow-management が所定手続きを踏んで実行）が二機能に分散しており、その調停ルールが両仕様のいずれにも明示されていない。self-improvement が直接変更する場合に workflow-management の手続きをバイパスするケースが発生するかが不明確。
- **対処方針**：self-improvement Req 1 受入 4 に「規律の変更は workflow-management の所定手続き経由で実行する（または self-improvement が直接変更する権限範囲を明示する）」という調停条件を追加。あるいは workflow-management 側に「self-improvement からの変更要求を手続き起動の入力とする」旨を明示
- **依存関係**：両機能の仕様を同時に参照して整合させる必要がある。どちらが先でも可

### A-008：conformance-evaluation から self-improvement への出力方向記述が仕様間で非対称 ✅ 対処済み（2026-05-23、要件 review-wave 確認）

- **対処内容**：conformance-evaluation Boundary Context の self-improvement 記述を「本機能の 12 criteria 検査結果を規律改善の入力として提供する（self-improvement が本機能の出力を読む方向）」に修正済み。self-improvement requirements.md 行 33 の「conformance-evaluation から...を入力源として活用可能」と方向一致。2026-05-23 の review-wave で両仕様の整合を確認
- **検出**：セッション 19、conformance-evaluation requirements の敵対役レビュー（Sonnet 4.6）
- **記録**：[.reviewcompass/specs/conformance-evaluation/reviews/2026-05-22-requirements.md](specs/conformance-evaluation/reviews/2026-05-22-requirements.md) §2.3 独立発見（機能横断）A-008
- **重大度**：WARN
- **波及範囲**：
  - **conformance-evaluation**：`.reviewcompass/specs/conformance-evaluation/requirements.md` §Boundary Context 隣接仕様の期待「`self-improvement`：規律レベル戻し（文書とは別経路）を受け取り、規律改善の入力とする」の方向記述が逆または不明確
  - **self-improvement**：`.reviewcompass/specs/self-improvement/requirements.md` 行 33 では「conformance-evaluation から規律遵守検査の適合性評価結果を入力源として活用可能」と self-improvement が conformance-evaluation の出力を読む方向を記載
- **不整合内容**：conformance-evaluation の隣接期待記述は「self-improvement から規律レベル戻しを受け取る（self-improvement を入力源とする）」かのように読める文言になっているが、feature-dependency.yaml の依存記述に `self-improvement` は含まれておらず、Out of scope 記述（「規律レベルの戻し：self-improvement の workflow 改善が扱う、本機能のスコープ外」）とも矛盾する。self-improvement 側は「conformance-evaluation の出力を活用する」方向を明示しており、情報の流れは conformance-evaluation → self-improvement が正しいと考えられる。
- **対処方針**：conformance-evaluation の隣接期待記述を「`self-improvement`：本機能の 12 criteria 検査結果を規律改善の入力として提供する（self-improvement が本機能の出力を読む、依存方向は外部化）」等の表現に修正し、方向を一致させる。feature-dependency.yaml に self-improvement を含まないことは現状のままで整合（依存なし、出力先として参照されるのみ）
- **依存関係**：conformance-evaluation 側の記述修正のみで成立。self-improvement 側は変更不要

### A-009：旧 paper-interface 由来の「論文」表現が foundation／evaluation／analysis／conformance-evaluation の文言で残存 ✅ 対処済み（2026-05-24、セッション 23 approval 前最終調整、第 1 波＋第 2 波の 2 段階対処）

- **対処内容（第 1 波、foundation／analysis、2026-05-24 セッション 23）**：
  - foundation Req Boundary Context Out of scope の「`analysis` の論文用記述生成」を「`analysis` の報告書記述生成」に修正（行 39）
  - analysis Req の Boundary Context In scope（行 18）／Out of scope（行 23）／Requirement 8 受入 1（行 128）／受入 1 太字見出し（行 132）／受入 5（行 136）／Change Intent（行 145）の計 6 箇所で「論文」を「報告書」に統一
  - 行 5 の歴史的経緯記述（「先行プロジェクトでは `paper-interface`（論文向け）と呼ばれていた」）は経緯説明のため保持
- **対処内容（第 2 波、evaluation／conformance-evaluation、2026-05-24 セッション 23）**：
  - evaluation Req Introduction（行 7）の「（運用ダッシュボード、週次、監査、論文等）は `analysis` が担う」を「報告書等」に修正
  - evaluation Req Boundary Context Out of scope（行 23）の「`analysis` 向けの読み物（運用ダッシュボード／週次／監査／論文）生成」を「報告書」に修正
  - conformance-evaluation Req Boundary Context 隣接仕様（行 32）の「論文向け原データ」を「報告書向け原データ」に修正
- **保持対象（先行プロジェクトでの呼称として歴史的経緯を残す）**：
  - analysis 行 5：`paper-interface`（論文向け）の歴史的経緯記述
  - self-improvement 行 24・164：「論文化からの分離」「旧 R6 の論文化からの分離」（先行プロジェクト旧 Requirement 6 の呼称、利用者明示判断 2026-05-24 セッション 23 案 β「保持」採用）
- **検出経緯**：
  - 第 1 波：foundation の requirements.approval 取得直前の要件文書要約提示の中で利用者が指摘（「論文化という言葉があるが、元々 paper-interface という機能の名残。現在は analysis で報告書を対象とする」）
  - 第 2 波：evaluation の requirements.approval 取得直前に「波及範囲の完了性確認」のため全 7 機能 requirements.md を grep で全件確認、追加 3 箇所を発見
- **利用者指摘の出典**：「論文化という言葉があるが、元々 paper-interface という機能の名残。現在は analysis で報告書を対象とする」「(ア)、論文ではなく報告書とする」（第 1 波、2026-05-24 セッション 23）／「推奨案」「ア」（第 2 波の全件確認と修正対象 4 箇所、2026-05-24 セッション 23）
- **重大度**：INFO
- **判定**：must-fix（用語整合）
- **波及範囲（最終）**：
  - **foundation**：`.reviewcompass/specs/foundation/requirements.md` 行 39（Boundary Context Out of scope）の 1 箇所
  - **analysis**：`.reviewcompass/specs/analysis/requirements.md` 行 18／23／128／132／136／145 の 6 箇所
  - **evaluation**：`.reviewcompass/specs/evaluation/requirements.md` 行 7（Introduction）／行 23（Boundary Context Out of scope）の 2 箇所
  - **conformance-evaluation**：`.reviewcompass/specs/conformance-evaluation/requirements.md` 行 32（Boundary Context 隣接仕様）の 1 箇所
- **正本との不整合**：計画書 §5.14 行 1566「論文化に限らず運用ダッシュボード・週次レポート・監査レポート・収束過程の可視化まで含めて担当」、および analysis Req 8 で確定済みの 4 出力先体制との文言食い違い
- **対処方針**：「論文」表現を「報告書」に統一。歴史的経緯（paper-interface の旧名、旧 Requirement 6 の呼称）は明示的に保持
- **処理段**：4 機能とも requirements の drafting／triad-review／review-wave／alignment が true、approval が false の状態で発見。reopen 手続きを起動せず approval 前の最終調整として処理（規律 §0.2 不可逆操作には未到達）
- **依存関係**：4 機能の修正は独立、すべて本セッション内で完了
- **波及範囲完了性の確認**：第 2 波の全件 grep（2026-05-24 セッション 23）により、本所見の波及範囲は完了。残存「論文」3 箇所はすべて歴史的経緯として明示的に保持判断済み

### A-010：conformance-evaluation の推定プロセス論点 A・B 対処（軽量 reopen） ✅ 対処済み（2026-05-24、セッション 23 末）

- **対処内容**：conformance-evaluation の推定プロセスについて、利用者考察により浮上した構造的論点 2 件を対処：
  - **論点 A（機能分離のタイミング）**：本筋（照合チェック）では既存 feature-partitioning を所与として扱い、独立の推定・照合対象から外す。傍流（文書生成、リバースエンジニアリング）は人協働を前提とした推定支援機能と位置付け、完全自動推定は目指さない
  - **論点 B（既存文書バイアス防止）**：照合チェックモードで二段階方式（推定 → 比較）を採用、既存 feature-partitioning だけは推定時の入力として尊重（照合成立性のため）、他の既存上流文書（intent ／ requirements ／ design）は推定時に技術的に遮断（バイアス防止）
  - **評価軸の絞り込み（案 Y）**：4 軸 12 criteria → **2 軸 6 criteria**（requirements ／ design × 3 criteria）に絞る。intent は参考情報、feature-partitioning と tasks は照合対象外
  - **推定段階の triad-review 適用**：推定段階と照合段階の両方に 3 役レビュー機構を適用、軽量／本格の使い分けを定義
- **対処範囲**：
  - **計画書 §5.10 改訂**：§5.10.1（主要用途を本筋／傍流で整理）、§5.10.2（2 軸 6 criteria に絞る）、§5.10.3（推定段階にも triad-review 適用）、§5.10.6（v3-plan §3.3 の扱いを本筋／傍流で整理）、§5.10.7（criteria 数の更新）、§5.10.9 新設（モード別の既存文書扱いルール）、§5.10.10 新設（推定段階の triad-review 適用方針）
  - **conformance-evaluation/requirements.md 改訂**：Boundary Context、Requirement 1〜5、Change Intent
  - **議論メモ**：[docs/notes/2026-05-24-conformance-evaluation-論点-a-b.md](docs/notes/2026-05-24-conformance-evaluation-論点-a-b.md) に経緯・改訂イメージ・最終結論を記録
- **検出経緯**：セッション 23 末、conformance-evaluation requirements approval 取得直前の要件文書要約提示の中で利用者が考察・指摘
- **利用者指摘の出典（主要なもの）**：
  - 「論文化という言葉があるが、元々paper-interfaceという機能の名残。現在はanalysisで報告書を対象とする」（A-009 の指摘、論点 A の起点）
  - 「目的が照合であるのなら、intentから機能分割をせず、design > requirementsまでできたところで、既存の機能分割を与えるべきか？そうしないと照合できない」（論点 B と照合成立性の両立に関する指摘）
  - 「上流文書がない場合は、リバースエンジニアリング。この場合には人と協働で分析を進めることが効率的。これは傍流。一方、仕様駆動開発を使って構築したコードの要件充足判断が本筋」（本筋／傍流の整理）
  - 「これは議論の点がおかしい。どうして機能分割を対象とするのか？」（評価軸の絞り込みの示唆）
  - 「実装からの上流文書推定は、構造的側面からの記述でよいと思う。意図は参考情報としての位置づけ。さらに、タスク分解は不要」（評価軸の絞り込み方針）
  - 「(イ) 案 Y」（2 軸 6 criteria 採用）
  - 「(ア)、一気にやってしまう。上記の骨子に加え、上流文書生成の過程に triad-review の必要性を検討」（推定段階の triad-review 適用）
- **重大度**：WARN（要件文書の構造的整合性に関わる）
- **判定**：must-fix（approval 前に対処、案 Y 採用）
- **波及範囲（最終）**：
  - **conformance-evaluation**：`.reviewcompass/specs/conformance-evaluation/requirements.md` の Boundary Context、Requirement 1〜5、Change Intent（複数受入の追加・改訂）
  - **計画書**：`docs/plan/reconstruction-plan-2026-05-21.md` §5.10.1／§5.10.2／§5.10.3／§5.10.6／§5.10.7 改訂、§5.10.9／§5.10.10 新設
- **処理段**：conformance-evaluation の requirements 段で発見。既に approval 取得済み（commit 8edefbf）状態だったため、approval を一度取り消し（false に戻し）、軽量 reopen として処理。実装基盤未整備（stages/reopen-procedure.yaml 未作成、計画書 §5.6 の 10 ステップ完全列挙未確定）により形式的 reopen 手続きの正式起動は実施せず、利用者明示承認に基づく軽量対処
- **対処方針の選択肢と利用者判断**：
  - (ア) 形式的 reopen 手続きの基盤整備を先に実施
  - (イ) 軽量に進める（approval 前の最終調整と同じ精神）→ **採用**（利用者明示承認 2026-05-24 セッション 23）
- **依存関係**：計画書改訂と requirements.md 改訂は本セッション内で完了、design 段着手前の必須対処事項として TODO §3 セクション C に登録、本対処完了により C は「完了済み」に更新

### A-011：analysis／design の 3 役差分集約ファイルが evaluation 接合面に存在しない ✅ 対処済み（2026-05-26、セッション 28）

- **対処内容**：evaluation 要件 9 受入 8 として「3 役別の所見差分を analysis 機能向け出力として提供」を新設、設計書に `roles/role_diff_report.json` 新設と「§3 役所見差分報告」節新設、§配置の根拠 ／ §analysis への接合面 ／ §要件追跡表 を更新。analysis 設計書の §レビュー収束過程の可視化モデル §1 出典記述と注記を更新、§上流機能との接合面（evaluation）に追加。evaluation/spec.json の requirements.approval を false に戻し軽量再オープン手続きで処理（A-013 と同型、2 件目）。利用者明示承認「案 3」「候補案 A」「案 α」「承認」「はい」x 複数（2026-05-26 セッション 28）
- **検出**：セッション 25、analysis／design.triad-review（2026-05-25）。主役（Sonnet 4.6）F-001 と敵対役（Opus 4.7）A-001 の連動所見、判定役（Opus 4.7）が must-fix／波及と判定
- **記録**：[.reviewcompass/specs/analysis/reviews/2026-05-25-design-triad-review.md](specs/analysis/reviews/2026-05-25-design-triad-review.md)（本セッション後段で新設予定）
- **重大度**：ERROR（敵対役独立発見 A-001 と判定役判定）
- **判定**：must-fix（判定役 Opus 4.7 が認定）
- **波及範囲**：
  - **analysis**：`.reviewcompass/specs/analysis/design.md` §レビュー収束過程の可視化モデル §1（行 326〜338）の `role_diff.json` の出典記述「計画書 §5.9.6 の `findings_by_method` 由来」が、`evaluation` の analysis 向け接合面 5 ファイル（`comparisons/treatment_comparisons.json`／`phase_comparisons.json`／`classifications/exclusion_report.json`／`caveats/caveat_register.json`／`modes/mode_diff_report.json`）に該当するファイルを持たない
  - **evaluation**：`.reviewcompass/specs/evaluation/design.md` §`analysis` への接合面（行 597〜607）に 3 役（主役・敵対役・判定役）の差分集約成果物が未明示。§分析成果物配置（行 97〜134）にも該当ディレクトリ・ファイルが未配置
- **不整合内容**：analysis 設計の判断 7（`evaluation` 派生）と分離規則 1（逆流禁止）に従えば、3 役差分は `evaluation` を経由して読むべきだが、対応する `evaluation` 成果物が存在せず、レビュー記録フロントマターからの直接読み込みになる経路が暗黙に発生する
- **対処方針**：候補案 A（利用者明示承認 2026-05-25 セッション 25、「(ア)」）。`evaluation` 設計に 3 役差分の集約成果物を新設する：
  - **evaluation 設計改訂**：
    - §分析成果物配置に `roles/` ディレクトリと `roles/role_diff_report.json` を追加（`modes/mode_diff_report.json` と対称配置）
    - §`analysis` への接合面に `roles/role_diff_report.json` を追加（既存 5 ファイル → 6 ファイル）
    - §レビューモード差分報告と同様の形式で「3 役所見差分報告」節を新設、最低限の構造化形式項目（`feature`／`role`／`findings_summary`（`by_severity` ＋ `by_final_label` ＋ `by_counter_status`、ただし役による条件付き必須）／`target`）を定義
    - §要件追跡表または §下流仕様への影響を更新
  - **analysis 設計改訂**：
    - §レビュー収束過程の可視化モデル §1 の出典記述を「`experiments/analysis/roles/role_diff_report.json` 由来」に書き換え
    - §上流機能との接合面（`evaluation` との接合面）の読み取りファイル一覧に `roles/role_diff_report.json` を追加
- **処理段**：design レビュー波段（残り 3 機能（workflow-management／self-improvement／conformance-evaluation）の drafting＋triad-review 完了後）で消化。本セッション内では追記のみで、analysis／design.md 本体は修正せず
- **依存関係**：`evaluation` 設計を先に改訂し、`analysis` 設計を後で修正する依存順
- **連動所見**：本所見と関連して、A-003（counter_status 集計の追加）も `role_diff_report.json` の構造に含めるべき内容（`findings_summary.by_counter_status`）であり、設計改訂時に同時に反映する

### A-012：self-improvement と workflow-management の時系列契約・完了通知形式 ✅ 対処済み（2026-05-26、セッション 28）

- **対処内容**：workflow-management 設計書 判断 7 を「A-012 対処で時系列契約・完了通知形式を詳細化」に拡張、self-improvement design §13.5 の合意点を受け入れる詳細（時系列契約／入力経路／完了通知形式／ロールバック責務／整合性検査タイミング）を追記。§下流仕様への影響の self-improvement 行を相互参照に更新。要件レベルでは既存記述（workflow-management 要件書 行 34 Boundary Context）で足り、軽量再オープン手続きは不要と判断。利用者明示承認「はい」（2026-05-26 セッション 28）
- **検出**：セッション 27、self-improvement／design.triad-review（2026-05-26）。主役（Sonnet 4.6）F-008 と敵対役（Opus 4.7）A-003 の連動所見、判定役（Opus 4.7）が must-fix／波及と判定
- **記録**：[.reviewcompass/specs/self-improvement/reviews/2026-05-26-design-triad-review.md](specs/self-improvement/reviews/2026-05-26-design-triad-review.md)
- **重大度**：F-008 WARN／A-003 ERROR（敵対役独立発見）
- **判定**：must-fix（判定役 Opus 4.7 が認定）、両所見とも波及（workflow-management 機能設計改訂を要する）
- **波及範囲**：
  - **self-improvement**：`.reviewcompass/specs/self-improvement/design.md` §13.5 で時系列契約と完了通知形式を「提案」として詳細記述済み（本セッション 27 で対処、利用者明示承認「候補 1」2026-05-26）。本機能側の合意点は確定
  - **workflow-management**：`.reviewcompass/specs/workflow-management/design.md` 側で本機能の提案する時系列契約・完了通知形式を受け入れる設計改訂が必要（design レビュー波段で実施予定）
- **対処方針**：
  - 時系列契約：`approved`＝本機能の提案レビュー承認時点、`materialized_at`＝workflow-management の手続き完了時点（本機能の status は変えず補助フィールドとして追記）
  - 渡し方：承認済み提案 YAML を `git mv` で `learning/workflow/approved-updates/` に配置、workflow-management が手続き入力として読む
  - 完了通知形式：workflow-management が手続き完了時に `approved-updates/<日付>-<id>.yaml` に `materialized_at`（ISO 8601）と `materialization_commit_hash` を追記
  - ロールバック責務：`approved` だが未 `materialized` の状態でロールバックが必要になった場合、本機能が `superseded` に遷移させ workflow-management に通知
  - 整合性検査タイミング：`materialized_at` 記録後に遵守検査再実行
- **依存関係**：self-improvement 設計（本セッション 27 で対処済み）の §13.5 を正本提案とし、workflow-management 側がこれを受け入れる形で改訂

### A-013：信頼度ラベル 3 値を foundation 語彙体系に追加要請 ✅ 対処済み（2026-05-26、セッション 28）

- **対処内容**：foundation 要件 6 受入 11 として信頼度語彙（`confidence_label`：high／medium／low の 3 値）を追加、foundation 設計 §3.5 を新設して値域・意味・参照禁止対象を定義。判断 7 の所有語彙一覧、要件と設計の対応表、下流仕様への影響にも反映。計画書 §5.18.7 の表直後に補注追記。conformance-evaluation 設計 §9.5 ／ §14.1 ／ Decision 11 ／ 所見対処一覧を foundation 参照に書き換え。foundation／spec.json の requirements.approval を false に戻し軽量再オープン手続きで処理（A-010 と同型）。利用者明示承認「やり方 α」「はい」（2026-05-26 セッション 28）。foundation 要件の再 review-wave（他 6 機能への波及なしを grep で確認）／alignment（文書整合確認）／approval（利用者明示承認、spec.json requirements.approval を true に書き戻し）も完了（2026-05-26 セッション 28、別コミット）
- **検出**：セッション 27、conformance-evaluation／design.triad-review（2026-05-26）。敵対役（Opus 4.7）A-003 独立発見、判定役（Opus 4.7）が must-fix／波及と判定
- **記録**：[.reviewcompass/specs/conformance-evaluation/reviews/2026-05-26-design-triad-review.md](specs/conformance-evaluation/reviews/2026-05-26-design-triad-review.md)
- **重大度**：ERROR
- **判定**：must-fix（判定役 Opus 4.7 が認定、波及）
- **波及範囲**：
  - **conformance-evaluation**：`.reviewcompass/specs/conformance-evaluation/design.md` §9.5 で信頼度ラベル 3 値（high／medium／low）を独自定義。foundation 改訂後に foundation 参照に書き換え（本セッション 27 で対処済み、Decision 11）
  - **foundation**：`.reviewcompass/specs/foundation/requirements.md` Requirement 6 系（validator_status／evidence_class／adversarial_outcome 等の語彙正本管理）に「信頼度語彙（high／medium／low）」を追加する設計改訂が必要
- **対処方針**：foundation Requirement 6 に新規受入として「信頼度語彙：high／medium／low の 3 値、推定タスク用」を追加する設計改訂。本機能側は foundation 改訂後に design.md §9.5 を foundation 参照に書き換え
- **依存関係**：foundation 設計改訂を先、本機能側修正を後

### A-014：evaluation との接合面で「評価結果との突き合わせ」の具体内容詳細 ✅ 対処済み（2026-05-26、セッション 28）

- **対処内容**：evaluation 設計書 §conformance-evaluation への接合面に `mode_diff_report.json`（経路別差分）と `roles/role_diff_report.json`（3 役差分、A-011 連動）を追加、突き合わせ詳細を明示。conformance-evaluation 設計 §14.3 の合意点と整合。利用者明示承認「はい」（2026-05-26 セッション 28）
- **検出**：セッション 27、conformance-evaluation／design.triad-review（2026-05-26）。主役（Sonnet 4.6）F-006、判定役が must-fix／波及と判定
- **記録**：[.reviewcompass/specs/conformance-evaluation/reviews/2026-05-26-design-triad-review.md](specs/conformance-evaluation/reviews/2026-05-26-design-triad-review.md)
- **重大度**：WARN
- **判定**：must-fix（判定役 Opus 4.7 が認定、波及）
- **波及範囲**：
  - **conformance-evaluation**：`.reviewcompass/specs/conformance-evaluation/design.md` §14.3 で突き合わせ詳細を記述（本セッション 27 で対処済み）：突き合わせ対象＝経路別差分／severity 集計／`role_diff_report.json`（A-011 連動）、突き合わせ手順 3 ステップ
  - **evaluation**：`.reviewcompass/specs/evaluation/design.md` 側に conformance-evaluation 向けの出力経路（経路別差分／severity 集計）の整合確認が必要
- **対処方針**：本機能 §14.3 の詳細記述を本機能側合意点として、evaluation 設計改訂で受け入れる形に整合
- **依存関係**：A-011（既存、evaluation の `roles/role_diff_report.json` 新設）と連動

### A-015：analysis との接合面の機械可読出力スキーマ ✅ 対処済み（2026-05-26、セッション 28）

- **対処内容**：analysis 設計書 §conformance-evaluation との接合面を conformance-evaluation §14.5 のスキーマ（必須フィールド 9 件＋任意フィールド 2 件）に準拠する記述に更新、旧暫定項目（conformance_run_ref／assessment_summary 等の取り込みスキーマ記述）を削除。conformance-evaluation 設計 §14.5 の合意点と整合。利用者明示承認「はい」（2026-05-26 セッション 28）
- **検出**：セッション 27、conformance-evaluation／design.triad-review（2026-05-26）。敵対役（Opus 4.7）A-008 独立発見、判定役が must-fix／波及と判定
- **記録**：[.reviewcompass/specs/conformance-evaluation/reviews/2026-05-26-design-triad-review.md](specs/conformance-evaluation/reviews/2026-05-26-design-triad-review.md)
- **重大度**：WARN
- **判定**：must-fix（判定役 Opus 4.7 が認定、波及）
- **波及範囲**：
  - **conformance-evaluation**：`.reviewcompass/specs/conformance-evaluation/design.md` §14.5 で機械可読出力スキーマを詳細記述（本セッション 27 で対処済み）：必須フィールド 9 件（feature／axis／criterion_id／severity／finding_id／correspondence_type／discrepancy_description／implementation_code_refs／judgment_id）、任意フィールド 2 件（target_commit／materialization_commit_hash）
  - **analysis**：`.reviewcompass/specs/analysis/design.md` 側で conformance-evaluation の評価記録スキーマを読む経路（接合面 §下流機能との接合面）の整合確認が必要
- **対処方針**：本機能 §14.5 のスキーマ詳細を本機能側合意点として、analysis 設計改訂で受け入れる形に整合
- **依存関係**：A-011（既存、analysis 側の `role_diff_report.json` 読み取り経路）と連動

### A-016：target_commit と self-improvement の materialization_commit_hash の整合ルール ✅ 対処済み（2026-05-26、セッション 28）

- **対処内容**：self-improvement 設計書 §13.6 表に「commit hash 整合ルール（A-016 対処）」行を追加、表の直後にサブセクション「target_commit と materialization_commit_hash の独立性」を新設、conformance-evaluation §12.3 の合意点を受け入れる相互参照を記述（両 commit の所有関係／同一文書で両 commit を扱う場面／本機能が conformance-evaluation 結果を取り込む場面）。要件レベルでは既存記述（self-improvement 要件書 行 33 Boundary Context）で足り、軽量再オープン手続きは不要と判断。利用者明示承認「はい」（2026-05-26 セッション 28）
- **検出**：セッション 27、conformance-evaluation／design.triad-review（2026-05-26）。敵対役（Opus 4.7）A-011 独立発見、判定役が must-fix／波及と判定
- **記録**：[.reviewcompass/specs/conformance-evaluation/reviews/2026-05-26-design-triad-review.md](specs/conformance-evaluation/reviews/2026-05-26-design-triad-review.md)
- **重大度**：WARN
- **判定**：must-fix（判定役 Opus 4.7 が認定、波及）
- **波及範囲**：
  - **conformance-evaluation**：`.reviewcompass/specs/conformance-evaluation/design.md` §12.3 で整合ルールを詳細記述（本セッション 27 で対処済み）：target_commit ＝実装コードのコミット、materialization_commit_hash ＝規律変更のコミット、両者は独立、規律改訂の影響を伴う conformance check 時のみ `related_artifacts.self_improvement` フィールドで参照
  - **self-improvement**：`.reviewcompass/specs/self-improvement/design.md` §13.5 と整合（self-improvement 側の materialization_commit_hash 定義と本機能の target_commit 定義が独立であることを相互参照で確認）
- **対処方針**：本機能 §12.3 の整合ルールを本機能側合意点として、self-improvement 設計改訂で受け入れる形に整合
- **依存関係**：A-012（既存、self-improvement と workflow-management の時系列契約）と連動

### A-017：機能横断波及の確認手順が tasks.md に明示されていない

- **検出**：セッション 30、foundation tasks 段の triad-review（2026-05-26）の主役所見 F-011
- **記録**：[.reviewcompass/specs/foundation/reviews/2026-05-26-tasks-triad-review.md](specs/foundation/reviews/2026-05-26-tasks-triad-review.md) §1 主役所見 F-011、§3.1 判定（波及種別）
- **重大度**：INFO
- **判定**：should-fix（判定役 Opus 4.7 が認定、波及種別「波及」）
- **利用者判定**：採用：案 1（pending-cross-feature-findings.md に A-017 として登録、機能横断段で全機能 tasks.md に一括対処）、2026-05-27 セッション 32 確定。7 モデル比較実験第 2 段階 topic-13 で 6 経路完全一致（全 API 経路 ＋ Sonnet CLI ＋ Opus 4.7 暗示推奨）＋利用者本人も案 1 を支持
- **波及範囲**：
  - **foundation**：`.reviewcompass/specs/foundation/tasks.md` 全体に機能横断波及の確認手順への明示的言及がない（読者が pending-cross-feature-findings.md への参照経路を持たない）
  - **runtime ／ evaluation ／ analysis ／ workflow-management ／ self-improvement ／ conformance-evaluation**：各機能の tasks.md 作成時に foundation と同様の構造を踏襲する見込みのため、本問題が再現する可能性
- **対処方針**：tasks 段の機能横断段（review-wave）で全 7 機能の tasks.md に対して「機能横断波及の確認手順」節を一括で追加する。foundation 単体での先行対処は行わない（topic-13 議論で採用された方針：機能横断段で統一形式の一括対処が記述形式の不一致リスクを避けられる）
- **依存関係**：他の 6 機能の tasks.drafting と triad-review 完了後に、機能横断段で一括対処
- **状態**：登録済み、機能横断段（tasks review-wave）で消化予定（現時点では tasks 段は foundation の triad-review レビュー完了のみ、残 6 機能の tasks.drafting と triad-review が未着手）
- **組み込み判断（2026-05-27 セッション 34）**：運営ガイド §3.6 や計画書 §5.5 への組み込みは**現時点で不要**。理由：A-017 は個別所見であり、機能横断段で実施されれば消化される性質。汎用パターン化（運営ガイド ／ 計画書本体への手順追加）は、機能横断段の実施結果を見てから再評価する方が安全。**再評価のタイミング**：tasks 段の機能横断段（review-wave）で A-017 を消化した後、対処の効果と類似所見の再発有無を確認したうえで、汎用パターン化の要否を別途判断する。**利用者明示承認の出典**：「ｂ。以降推奨案で自律的に進める」（要確認 3 の処理方針として案 d ＝ pending に組み込み判断を追記、運営ガイド ／ 計画書本体は触らない、2026-05-27 セッション 34）。

### A-018：foundation 語彙正本の所有件数の食い違い（F-013 ／ A-005 同根問題）

- **検出**：セッション 35〜36、analysis tasks 段の triad-review（2026-05-28）の主役所見 F-013（Sonnet 4.6）と敵対役独立発見 A-005（Opus 4.7）の同根所見
- **記録**：[.reviewcompass/specs/analysis/reviews/2026-05-28-tasks-triad-review.md](specs/analysis/reviews/2026-05-28-tasks-triad-review.md) §1 主役所見 F-013、§2.2 独立発見 A-005、§3.1 判定（must-fix／波及）
- **重大度**：F-013 ERROR ／ A-005 ERROR（判定役の総合 severity 評価は ERROR と WARN の両論あり、敵対役反証で「上流不確定性が真因」のため WARN 寄りの解釈もありうる）
- **判定**：must-fix（判定役 Opus 4.7 が認定、波及種別「波及」）
- **波及範囲**：
  - **foundation**：`.reviewcompass/specs/foundation/design.md` で語彙正本の所有件数が複数箇所で食い違う：行 644（§完成判定基準で 4 件のみ列挙：`counter_status`／`validator_status`／`evidence_class`／`review_mode`）、行 736（6 件と記載）、§判断 7（§3／§4 委譲で曖昧）、§3.5（`confidence_label` 独立節として追加、A-013 由来）
  - **analysis**：`.reviewcompass/specs/analysis/tasks.md` 行 27 ／ 行 213-215 で foundation 語彙正本を「7 件」と数える（`counter_status`／`validator_status`／`evidence_class`／`review_mode`／`severity`／`final_label`／`confidence_label`）
  - **evaluation**：`.reviewcompass/specs/evaluation/tasks.md` 行 219 で foundation 語彙正本を「6 件」と数える（`confidence_label` を含まず）
- **不整合内容**：foundation 自身が所有する語彙正本の所有件数が foundation/design.md 内で複数箇所で食い違う（4 件 ／ 6 件 ／ 「§判断 7 で §3／§4 委譲」の 3 通り表記）。下流の analysis tasks（7 件）と evaluation tasks（6 件）は foundation 正本の数え方に依存するため、上流 foundation の確定なしには下流の整合が取れない。
- **対処方針**：
  - **第 1 段階（上流確定）**：foundation 側で語彙正本の所有件数を正式確定する。候補数値：4 件（行 644 ベース）／ 6 件（行 736 ベース、A-013 信頼度ラベル `confidence_label` を含む）／ 7 件（analysis の数え方、`severity` ／ `final_label` を含む）。foundation/design.md §判断 7 を改訂して所有件数と各語彙の所有者を明示確定
  - **第 2 段階（下流整合）**：foundation 確定後、analysis tasks 完成判定基準（行 213-215）と evaluation tasks 完成判定基準（行 219）の数字を確定値に書き換え。tasks.md 内の各タスク完了条件・テスト要件に登場する「foundation N 語彙の参照のみ使用」も同期更新
  - **第 3 段階（軽量再オープン）**：foundation requirements ／ design ／ tasks の該当箇所と analysis ／ evaluation の tasks 該当箇所を §5.23.13 軽量手続きで再オープンして同期更新
- **依存関係**：foundation 側の正式確定が先。analysis ／ evaluation 側の修正は foundation 確定後に同期更新
- **状態**：登録済み、機能横断段（tasks review-wave）で消化予定。**7 モデル比較実験の 2 回目**（機能横断段の 7 モデル評価、2026-05-28 セッション 35 で確定した 2 回方式）の評価対象としても扱う
- **検出経緯の注記**：本所見は本セッション 35 の縦整合チェック（依存マップ順）で発見されず、その後の analysis tasks の triad-review で主役 Sonnet 4.6 と敵対役 Opus 4.7 が独立に検出。敵対役は「foundation 側の確定が不在のまま analysis が 7 件と数えるのは越権参照」と severity 評価を補強。本所見は §5.23.13.3 末尾「セッション 34 整合性確保レビューの結果」の **残り 27 件**とは別系統の新規発見（縦整合チェックの範囲が下流 analysis／evaluation の数値表記までは及ばなかったことが露呈）

## 4. 対処済みの所見

（本セッションでの新規作成時、未消化のみ）
