# 7 モデル比較実験 — 外部 AI 評価者向けインデックス

作成：2026-05-29（セッション40）。本文書は、ReviewCompass の「7 モデル比較実験」を**別の AI（外部評価者）に評価依頼する**ために、評価に必要な実験計画・結果文書・元データ・計画書・対象文書の所在を一覧にしたもの。すべてのパスはリポジトリルート（`/Users/Daily/Development/ReviewCompass/`）からの相対表記。

**論文版（現在の参照点）**：**タグ `paper-data-v1-2026-05-29`**。データセット管理方針（`docs/experiments/dataset-management.md`）に従う。本文書の集計値・結論は、その方針 §7 CHANGELOG に記録された条件下のデータに基づく。外部評価依頼時は本タグを併記すること。

---

## 0. この実験は何か（30 秒概要）

- **目的**：ReviewCompass の「人間代役機構（計画書 §5.12）」の権限範囲チューニングに使う実証データの取得。仕様駆動レビューで出た所見（finding）に対する**修正方針の判定**を、7 モデル＋人本人＝8 者で並列に行い、判断の一致度・ばらつきを測る。
- **測っているもの（正直な射程）**：レビューの「**裁定の質**」（所見をどう裁くか）。所見を「見つける力（発見力）」や「後続の手戻り低減（効果）」は本実験の射程外（実験ノート §6.15.1 参照）。
- **対象**：仕様 7 機能（foundation／runtime／evaluation／analysis／workflow-management／self-improvement／conformance-evaluation）の **tasks 段** triad-review（三役レビュー）で出た所見、計 122 論点（topic）。2 回方式（1 回目＝機能別 topic-1〜120、2 回目＝機能横断 topic-121〜122）。
- **評価してほしい観点の例**：実験設計の妥当性、結論（起草者バイアス・代役候補序列等）の妥当性、指標の適切さ、統計的な弱さ、見落とし。

---

## 1. 実験計画・方法論（まずここを読む）

**正本文書**：`docs/experiments/n-model-comparison.md`（約 1240 行、2 層構成）

| 節 | 内容 |
|---|---|
| §1 | 検証目的・ケース選定方針 |
| §2 | 共通フレームワーク。**§2.6 に事前登録した 12 観点**（評価レンズ、事後追加禁止の対象） |
| §3 | プロンプト設計・出力 YAML 形式・**§3.4 マルチターン対話プロトコル＋§3.4.2 枠組み伝染バイアス対策**（重要：プロンプトの枠組みがレビュアーを誘導する問題と緩和策） |

**補足**：計画書側の位置づけ
- `docs/plan/reconstruction-plan-2026-05-21.md`
  - **§5.9.6**（行 975〜、N モデル比較実験への発展・実施タイミング・2 回方式）
  - **§5.12**（行付近、人間代役機構＝この実験のデータの使い道。行 727 補助層 A、§5.12.11 アサイン権限は未起草で改訂予定）

---

## 2. 実験結果の文書（分析・集計・結論）

**正本文書**：`docs/experiments/n-model-comparison.md`

| 節 | 内容 |
|---|---|
| §4〜§5 | foundation（topic-1〜17）・runtime（topic-18〜33）のケースと結果 |
| §6.1〜§6.12 | 事前登録 12 観点ごとの考察（foundation＋runtime 中心） |
| §6.13 | foundation＋runtime の統計集計（32 件、モデル別人本人一致率表 §6.13.2 ほか） |
| **§6.14** | **全機能統合集計**（残り 5 機能 topic-34〜120＋機能横断 topic-121〜122）。§6.14.2 起草者バイアス、§6.14.6 モデル別人本人一致率（全機能） |
| **§6.15** | **事後発見の指標 8 件＋特徴的所見 8 件**（事前登録 12 観点と区別）。confidence 較正・case_scores 分離度など。§6.15.4 §5.12 改訂への含意 |

**主要な結論（評価対象）**：
- 起草者（Opus 4.7）は自案に係留し、自起草機能で一致率が下がる（workflow-management 60%・self-improvement 66%）。
- 代役候補序列：GPT-5.5 86%＞Sonnet-CLI 85%＞GPT-5.4 83%。Opus（起草者）75%。
- confidence は較正不良（特に Gemini 系は不一致時も 0.94-0.95）。
- case_scores は接戦（割れ）で差が小さい（割れ 3.29 vs 一致 4.65）。

---

## 3. 元データ（生データ）

> **重要：実験の対象段は tasks 段のみ**。7 モデル比較実験はセッション31（foundation tasks 段）で開始したため、それ以前に完了した **requirements 段・design 段の実験データは存在しない**。requirements/design 段はレビュー記録は残っているが（§5 参照、design 段は三役レビュー済み）、7 モデル比較にはかけていない。design／implementation 段は実験の将来候補（実験ノート §1.3、未実施）。

**場所**：`tools/experiments/results/`（計 946 ファイル）

- **判定結果**：`topic-<N>-<model>.yaml`。1 ターン目の応答。`<model>` は次の 8 種：
  - `sonnet-4-6-api`（API 経由 Sonnet、122 件）／`sonnet-4-6-cli`（CLI 経由 Sonnet、120 件）
  - `gpt-5-5`（122）／`gpt-5-4`（122）／`gemini-3-5-flash`（122）／`gemini-3-1-pro-preview`（122）
  - `opus-4-7`（起草者＝メインセッション自身の判断、69 件。topic-53〜120 のみ）
  - `human`（人本人判定、107 件。割れ案件は全保存、完全一致案件は一部のみ＝人本人＝多数派と解釈）
- **マルチターン最終判定**：`topic-<N>-<model>-final.yaml`（質問返し後の 2 ターン目最終判定）。`-turn2` は中間。
- **各 YAML の中身**：`response_text` に判定 YAML（`decision`／`rationale`／`confidence`／`turns_used`／`uncertainty_factors`／`assumed_context`／`case_scores`／`comment_to_human`）が文字列で埋め込まれている。`human` ファイルは利用者本人の判定。

**topic → 機能・段階の対応**：

| topic | 機能 | 回 | モデル数 |
|---|---|---|---|
| 1〜17 | foundation | 1 回目 | 7（人本人含む 8 者） |
| 18〜33 | runtime | 1 回目 | 7 |
| 34〜52 | evaluation | 1 回目 | 6（Opus なし） |
| 53〜75 | analysis | 1 回目 | 7 |
| 76〜98 | workflow-management | 1 回目 | 7 |
| 99〜110 | self-improvement | 1 回目 | 7 |
| 111〜120 | conformance-evaluation | 1 回目 | 7 |
| 121〜122 | 機能横断（A-018／A-019） | 2 回目 | 5 API＋人本人（Opus／Sonnet-CLI はファイル未保存、判定は §6.14.3 に記録） |

**プロンプト（各論点に与えた入力）**：`tools/experiments/prompts/topic-<N>.txt`（132 件）。評価者は所見の提示形式・候補案・事実欄を確認できる。

---

## 4. 実験基盤コードと集計スクリプト

**場所**：`tools/experiments/`、`tools/api_providers/`

- **実験エンジン**：`tools/experiments/_experiment_n_model.py`（1 論点を 1 モデルに投げる本体。`--provider`／`--model`／`--prompt-file`／`--history-file`／`--turn-number`）
- **モデル抽象層**：`tools/api_providers/`（`providers.py`＝Anthropic／OpenAI／Gemini の抽象、`run_role.py`、`config_loader.py`、`response_formatter.py`、`tests/`）
- **実行スクリプト**（機能別、`_temp` は暫定）：`_run_eval_experiment_<feature>_temp.py`、マルチターン続行は `_run_eval_experiment_<feature>_multi_turn_temp.py`、機能横断 2 回目は `_run_eval_experiment_cross_feature_round2_temp.py`
- **プロンプト生成**：`_generate_eval_prompts_<feature>_temp.py`
- **起草者（Opus）判断生成**：`_generate_opus_judgments_<feature>_temp.py`
- **集計スクリプト**（結論の再現に使う）：
  - `_aggregate_<feature>_eval_temp.py`（機能別の両軸 2 表：1 ターン目応答分布＋最終判定分布）
  - `_aggregate_agreement_all_temp.py`（全機能のモデル別人本人一致率＝§6.14.6 の元）
  - `_aggregate_metrics_all_temp.py`（別案率・質問返し率・分岐度＝§6.15 の元）
  - `_aggregate_calib_scores_temp.py`（confidence 較正・case_scores 分離度＝§6.15 の元）
- **代理回答（マルチターン）**：`proxy_responses_<feature>_temp.yaml`（質問返し時に事実のみ回答した内容）
- **実行方法**：必ず venv の Python を直接指定（`/Users/Daily/Development/ReviewCompass/.venv/bin/python3`、環境変数・PyYAML のため）

---

## 5. 評価対象の所見の出所＋三役レビュー自体の評価データ

> **2 つの評価レイヤーがある**。本インデックスの主題（7 モデル比較）はレビューの「**裁定の質**」を測る。一方、下記の triad-review 記録は、レビューの「**生成の質**」（発見力・根拠性・敵対役の有効性）を評価するための独立したデータでもある。外部評価者は両レイヤーを別個に評価できる。

### 5a. 三役レビュー自体の評価データ（レビュー生成の質）

各機能の `reviews/<日付>-tasks-triad-review.md` は、所見の出所であると同時に、**三役レビュー（主役 Sonnet 4.6 ／ 敵対役 Opus 4.7 ／ 判定役 Opus 4.7）の質を評価する構造化データ**を含む：

- **主役所見一覧**：ID・観点・severity（CRITICAL/ERROR/WARN/INFO）・target_location・description・**evidence_type（fact/inference/mixed）**
- **敵対役**：主役所見ごとの **counter_status（同意／counter_evidence_raised＝反証）**＋独立発見一覧
- **判定役**：judgment（must-fix/should-fix/leave-as-is）・波及種別（機能内対処/波及/遡及/延期）・根拠
- **front-matter**：by_severity・by_judgment の集計

これで評価できる軸：**発見力**（所見件数・severity 分布・敵対役の独立発見数）／**根拠性**（evidence_type 分布・target_location の具体性）／**敵対役の有効性**（反証率）／**判定役の分類傾向**。

**集計サマリ（2026-05-29 作成）**：`docs/experiments/triad-review-summary-2026-05-29.md`。全7機能の front-matter を集計（主役 114 件・敵対役 93 件・判定 161 件、must32%/should45%/leave21%、敵対役反証率 28%（記載4機能））。算出スクリプト：`tools/experiments/_aggregate_triad_review_temp.py`。

**限界**：上記サマリは front-matter 集計（反証分布は記載 4 機能のみ、本文の counter_status 手集計で補完可能・未実施）。**効果（後続の手戻り低減）は未測定**。7 モデル実験のような統制された比較ではない（三役配置は全機能同一）。

### 5b. tasks 段 triad-review 記録（＝7 モデル実験の所見の出所でもある）：

- `.reviewcompass/specs/foundation/reviews/2026-05-26-tasks-triad-review.md`
- `.reviewcompass/specs/runtime/reviews/2026-05-27-tasks-triad-review.md`
- `.reviewcompass/specs/evaluation/reviews/2026-05-27-tasks-triad-review.md`
- `.reviewcompass/specs/analysis/reviews/2026-05-28-tasks-triad-review.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-05-28-tasks-triad-review.md`
- `.reviewcompass/specs/self-improvement/reviews/2026-05-29-tasks-triad-review.md`
- `.reviewcompass/specs/conformance-evaluation/reviews/2026-05-29-tasks-triad-review.md`

**上流段（requirements／design）のレビュー記録（実験データではないが、仕様の成立経緯として参照可）**：
- requirements 段：`.reviewcompass/specs/<機能>/reviews/2026-05-22-requirements.md`（7 機能。三役レビュー形式ではない初期レビュー）
- design 段：`.reviewcompass/specs/<機能>/reviews/2026-05-2[56]-design-triad-review.md`（7 機能。**三役レビュー済みだが 7 モデル比較実験はかけていない**）

**所見が指していた仕様文書本体**：`.reviewcompass/specs/<機能>/{requirements.md, design.md, tasks.md}`（7 機能）。

**機能横断（2 回目）の所見**：`learning/workflow/carry-forward-register/reviewcompass-import.yaml`（旧 Markdown source 由来の A-017／A-018／A-019、すべて対処済み）。

---

## 6. 文脈・前提（評価の妥当性判断に必要な背景）

- **プロジェクト全体像**：`README.md`、運営ガイド `docs/operations/SESSION_WORKFLOW_GUIDE.md`（仕様駆動レビューの 5 段ワークフロー、三役レビューの定義）
- **計画書**：`docs/plan/reconstruction-plan-2026-05-21.md`
- **規律**：`docs/disciplines/`（レビュー運用の規律。`README.md` に一覧）

---

## 7. 既知の限界・注意（評価者が踏まえるべき点）

実験ノート §6.14.5／§6.15 に詳述。要点：

1. **データの非均質性**：判定支援資料（foundation のみ使用）、枠組み伝染バイアス緩和（セッション39 から導入）、マルチターン継続の有無が機能間で揃っていない。単純な機能間比較は不可。
2. **モデル別カバー範囲の差**：Opus は topic-53〜120 のみ（68 件）、evaluation（topic-34〜52）は 6 モデルで Opus なし、機能横断 2 回目（topic-121〜122）は 5 API のみ。
3. **機能横断 2 回目は n=2**：統計的に弱い。
4. **完全一致案件の人本人判定**：一部未保存（analysis 完全一致 15 件等）。「完全一致＝人本人は多数派に同意（一括承認）」と解釈して集計。
5. **起草者（Opus）はメインセッション自身**：評価者・起草者・集計者が同一という構造的バイアスの可能性（§6.15 で自己観察として記録）。**外部 AI 評価はこのバイアスの独立チェックとして特に価値がある**。
6. **事前登録（§2.6 の 12 観点）と事後発見（§6.15）の区別**：論文の誠実性のため両者を分けている。評価者はこの区別の妥当性も見てほしい。

---

## 8. 評価者への推奨手順

1. §0〜§1（本書）で全体像と方法論を把握
2. `n-model-comparison.md` §1〜§3（計画）→ §6.13〜§6.15（結果・結論）を読む
3. 結論を疑う：`tools/experiments/results/` の生データと集計スクリプトで主要数値を再現・検証
4. 所見の質を疑う：`reviews/` の三役レビュー記録と `specs/` の対象文書を突き合わせ
5. §7 の限界を踏まえ、設計・結論・指標・統計の弱さ・見落としを指摘
