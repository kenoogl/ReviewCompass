# WORKFLOW_MANAGEMENT：所定手続き管理機能の運用文書

最終更新：2026-05-22（フェーズ 1 抽出、requirements 部分のみの骨子）

本文書は ReviewCompass の `workflow-management`（所定手続き管理機能、旧 `implementation-governance`）の運用上の役割と契約を解説する。形式仕様は [.reviewcompass/specs/workflow-management/requirements.md](../../.reviewcompass/specs/workflow-management/requirements.md) を参照する。

## 1. 役割

`workflow-management` は ReviewCompass の所定手続き（intent から implementation までの段集合）の定義と機械強制を担う機能である。先行プロジェクトでは大規模機構（実行台帳・独立再導出パーサ・節ハッシュ等）として組み上がっていたが、ReviewCompass では計画書 §5.4「軽量化方針」により **思想は継承、実装は 1／10** を目標とする再設計を行った。

具体的には：

- **所定手続きの段集合 YAML 静的列挙**：9 ファイル体制（intent／feature-partitioning／feature-dependency／requirements／design／tasks／implementation／reopen-procedure／cross-spec-alignment）
- **軽量版検査スクリプト**：証跡ファイル存在 ＋ 必須節充足のみで段完了を判定
- **起草者と判定者の分離**：レビュー記録 front-matter の `author`／`reviewer` 異名必須
- **不可逆操作の直前ゲート**：spec.json 承認／コミット／プッシュ／フェーズ移行のみが対象
- **reopen 手続きの機械強制**：手戻り種別の二次元表記 ＋ `trigger_map` で連鎖再実施
- **session 跨ぎ状態管理**：`stages/in-progress/` で進行中状態を明示
- **多層防御の第 1 層位置付け**：第 2〜5 層はフェーズ 4 以降の宿題
- **機能依存マップの一元化**：`feature-dependency.yaml` で機能間処理順と依存を 1 箇所管理

## 2. 設計の根本姿勢

- **思想は継承、実装は 1／10**：先行プロジェクトの大規模機構の思想は引き継ぐが、実装規模を 1/10 に削減
- **証拠ベースの完了判定**：主張ではなく証跡 artifact の存在で完了を判定
- **fail-closed の最小集合**：機械ゲートを不可逆操作の直前にのみ集中
- **静的列挙の徹底**：Markdown 節からの動的解析を行わない、YAML 静的列挙のみ
- **多層防御の認識**：第 1 層の限界を明示し、過剰な期待を避ける

## 3. 8 つの要件領域（要約）

| 要件 | 領域 | 何を定めるか |
|---|---|---|
| Requirement 1 | 段集合の静的列挙 | 9 ファイル体制、`stages/<process_id>.yaml` |
| Requirement 2 | 軽量版検査スクリプト | 証跡ファイル存在 ＋ 必須節充足のみ、結論不能なら fail |
| Requirement 3 | 起草者と判定者の分離 | front-matter `author`／`reviewer` 異名必須、サブエージェント方式対応 |
| Requirement 4 | 不可逆操作の直前ゲート | spec.json 承認／コミット／プッシュ／フェーズ移行のみ |
| Requirement 5 | reopen 手続きの機械強制 | 手戻り種別二次元表記、`trigger_map` 連鎖再実施 |
| Requirement 6 | session 跨ぎ状態管理 | `stages/in-progress/`、session 開始時標準フロー |
| Requirement 7 | 多層防御の第 1 層位置付け | 第 1 層の限界明示、第 2〜5 層はフェーズ 4 以降 |
| Requirement 8 | 機能依存マップの一元化 | `feature-dependency.yaml`、依存変更は 1 箇所のみ |

各要件の受入基準の詳細は [.reviewcompass/specs/workflow-management/requirements.md](../../.reviewcompass/specs/workflow-management/requirements.md) を参照。

## 4. 削減した部分（先行プロジェクトとの違い）

計画書 §5.4 で削除確定：

- 節ハッシュ（`section_content_hash`）と陳腐化／改竄検知
- supersedes リンクによる旧台帳保全
- grandfathering と format-migration 機構
- 権威マップ（独立文書）と独立再導出パーサ
- 通過マーカーの後続確認（二次防御）

これらは多層防御の第 2〜5 層（フェーズ 4 以降の宿題）で再導入の余地を残す。

## 5. 受け入れるリスク（明文化、§5.4 由来）

- 段集合の正本が YAML に固定されるため、Markdown 文書側で段集合が変わった場合に YAML との整合は人手で取る必要がある
- 検査スクリプト自体が呼ばれない経路を機械検知しない（人間がフェーズ境目で確認する前提）
- 中身の妥当性（記述内容の品質）は判定しない（第 1 層の限界）
- in-progress ファイルの自己申告性（嘘・古い・欠落の余地）

これらは多層防御の他層で補完する前提とする。

## 6. 他機能との関係

- **`foundation`**：状態軸語彙（`run_status`／`validator_status`／`human_signoff_status`／`evidence_class`）を参照（依存）
- **`runtime`**：実行記録のメタデータが本機能の検査対象になる
- **`evaluation`**：所定手続きの実行結果に対する評価要求を受ける
- **`analysis`**：所定手続きの実行履歴を可視化用に取り込む
- **`self-improvement`**：本機能の運用結果から改善提案の入力を提供
- **`conformance-evaluation`**：本機能の所定手続きが実装された場合に、その実行成果物の上流文書との適合性を評価

## 7. 後続セッションでの追加予定

本文書は requirements 部分のみの骨子。次のセッション以降で次を追加：

- design.md 抽出に基づく設計の説明（計画書 §5.4〜§5.8 全体の統合）
- 9 ファイル体制の各 YAML の具体スキーマ
- 検査スクリプトの実装方針（フェーズ 3 スタブ対応）
- 多層防御の第 2〜5 層の段階的導入計画（フェーズ 4 以降）

## 8. 関連文書

- 形式仕様：[.reviewcompass/specs/workflow-management/requirements.md](../../.reviewcompass/specs/workflow-management/requirements.md)
- 計画書 §5.4〜§5.8：[軽量化方針／段階層構造／reopen 機械強制／session 跨ぎ状態管理／多層防御](../plan/reconstruction-plan-2026-05-21.md)
- 計画書 §5.20.2 workflow-management 行：[抽出対応表](../extraction-mapping.md)
- 機能横断波及所見：[.reviewcompass/pending-cross-feature-findings.md](../../.reviewcompass/pending-cross-feature-findings.md)
- 隣接機能：[foundation](FOUNDATION.md)、[runtime](RUNTIME.md)、[evaluation](EVALUATION.md)、[analysis](ANALYSIS.md)
