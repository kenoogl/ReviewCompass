# 機能横断レビューで扱う所見の集約

最終更新：2026-05-23（用語「遡及／波及」を二軸的定義に訂正）

本文書は、各機能の local-review 段で露出した **機能横断の波及所見**を集約する。これらは個別機能の local-review 段では対処せず、要件フェーズの **review-wave**（複数機能を横断する複数ラウンドレビュー、計画書 §5.5）または **alignment／approval**（フェーズ終端の機能横断整合確認、責務分離による 5 段化後の段集合）で扱う。

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

## 4. 対処済みの所見

（本セッションでの新規作成時、未消化のみ）
