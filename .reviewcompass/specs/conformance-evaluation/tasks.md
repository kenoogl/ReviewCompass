---
spec: conformance-evaluation
phase: tasks
stage: drafting
author:
  identity: claude-code-main-session
  model: claude-opus-4-7
  role: drafter
created_at: 2026-05-29
language: ja
---

# Tasks Document：conformance-evaluation

## 概要（Overview）

本文書は `conformance-evaluation`（ReviewCompass の 7 番目の独立機能、**下流 → 上流の逆方向**で実装コードから上流文書を推定・照合する機能）の実装タスクを列挙する。本機能は 2 モード（**照合チェックモード＝本筋**：既存上流文書と推定結果を比較して意図ずれを検出／**文書生成モード＝傍流・人協働**：上流文書のないコードベースから骨子を推定）を持ち、両モードで同一の **6 criteria 構造**（requirements ／ design の 2 軸 × 3 criteria）を使う。実装適合レビュー（順方向）は吸収せず `runtime`／`analysis` の連携に残す（Req 8）。

タスクは設計文書（design.md）の所有モデル単位でまとめる。本機能の所有物は、モード切替（§3）／文書生成モード（§6）／照合チェックモード（§7）／6 criteria 検査構造（§8）／推定モデル（§9）／比較モデル（§10）／3 役レビュー機構の適用（§11）／評価記録（§12）／依存関係の連想配列構造（§13）／他機能との接合面（§14）／機械検査（§18）／テスト戦略（§19）である。

## タスク粒度と方針（Granularity and Policy）

- **粒度**：1 タスク ＝ 1 つの所有モデル領域。design.md の節と必ずしも 1 対 1 でなく、密接に関連する節は同じタスクにまとめる（self-improvement／workflow-management T-001〜の粒度方針を継承）
- **一気通貫**：1 タスクは「起草・実装・テスト・コミット」まで止めず連続で進められる単位
- **依存順**：前提タスクが完了してから後続タスクに進む。データの流れ（design §1：入力＝実装コード → 推定 → 比較 → 評価記録）を依存順の基本とする
- **自律進行**：実装段で per-task 承認は取らず、コミット・プッシュ・spec.json 更新・フェーズ移行のみ明示承認（規律 [[implementation-autonomy]] 準拠）
- **段階的導入**：第 1 期（フェーズ 1〜3）は手動 grep ／ find による半自動運用、自動化はフェーズ 4 で段階的に進める（design §18.4 ／ §19.3）。各タスクの完了条件は第 1 期スコープ（手動運用が機械的に検証可能なこと）で判定する
- **contract consumer 原則**：foundation が所有する語彙正本（スキーマ・メタデータ契約・検証器状態語彙・レビューモード語彙・証拠区分語彙・`adversarial_outcome` 語彙・信頼度ラベル）を再定義せず参照のみで使用（依存：hard、Req 7 受入 3、design §14.1）。runtime／evaluation／workflow-management の出力は入力源として読む（依存：review）
- **本筋と傍流の分離**：照合チェックモード（本筋）と文書生成モード（傍流・人協働）を明示的に分離（Decision 1）。両モードの推定プロセスと既存文書扱いは異なる
- **二段階方式と遮断の徹底**：照合チェックモードは「第 1 段階＝推定（既存上流文書を遮断、feature-partitioning のみ入力に尊重）→ 第 2 段階＝比較」（Req 3 受入 1）。遮断は技術的手段で実装し、推定役プロンプトへの既存上流文書混入を MV-6 で fail-closed 検知（遮断必須、design §18.3）
- **fail-closed の粒度別適用**：機械検査（§18）は MV ID 別に fail-closed 粒度を区別（遮断必須＝MV-6／遮断推奨＝MV-1・MV-2・MV-3／警告続行可＝MV-4・MV-5・MV-7、design §18.3）

`conformance-evaluation` 全体で 14 タスク。

## タスク一覧（Task List）

### T-001：成果物配置の準備

- **対応設計節**：design.md §6.3 ／ §7 ／ §12.2 配置先、§18.2 検査スクリプト所在
- **対応要件**：Requirement 6 受入 2（評価記録の配置）、Requirement 8 受入 4（ディレクトリ分離）
- **責務**：本機能の成果物の物理配置を新設する。評価記録の配置先 `<対象アプリ>/.reviewcompass/specs/<feature>/conformance/`（`reviews/` とは別ディレクトリ、Req 8 受入 4）、文書生成モードの推定出力先 `<対象アプリ>/.reviewcompass/conformance/inferred/<日付>/`（feature-partitioning-candidates.md ／ intent-reference.md ／ specs/<feature>/）、6 criteria 検査仕様の配置先 `schemas/review-criteria/`、検査スクリプト配置先 `tools/`、テスト配置先 `tests/conformance-evaluation/` を新設し、各ディレクトリに配置目的を記す README を置く。空ディレクトリは `.gitkeep` で Git 追跡可能にする（self-improvement T-001 の方針継承）
- **前提タスク**：なし（起点）
- **成果物**：
  - `tools/conformance_evaluation/` パッケージのディレクトリ＋`.gitkeep`（命名規約：import 対象パッケージはアンダースコア、単独 CLI スクリプト `tools/conformance-evaluation-check.py` はハイフン。self-improvement topic-105 と同方針）
  - `tools/conformance_evaluation/schemas/.gitkeep`（ツール内部スキーマの配置）
  - `schemas/review-criteria/README.md`（6 criteria 検査仕様 `conformance_evaluation.yaml` の配置説明、実体配置は implementation.drafting で完了 → DVT-C001 解除）
  - `docs/operations/CONFORMANCE_EVALUATION.md`（**既存ファイル**、design §20.1 の A-001 で既存と判明）への追記（配置規則・対象アプリ側パス規則の説明、`conformance/` と `reviews/` の分離。topic-118／F-018 で既存ファイルへの追記と明記）
  - `tests/conformance-evaluation/.gitkeep`
  - `tools/README.md` への追記（`conformance-evaluation-check.py` の配置先・命名規約）
- **完了条件**：
  1. `conformance/` と `reviews/` の分離方針が運用文書（CONFORMANCE_EVALUATION.md）に明記され、評価記録は `conformance/<日付>-<mode>.md` のパス規則に従う（MV-3 連動）
  2. 文書生成モードの推定出力先パス規則（§6.3 の 3 経路）が運用文書に明記される
  3. `schemas/review-criteria/` ／ `tools/conformance_evaluation/` ／ `tests/conformance-evaluation/` が存在し `.gitkeep` で Git 追跡可能である
  4. `tools/README.md` に命名規約（パッケージ＝アンダースコア／単独 CLI＝ハイフン）が明記される
- **テスト要件**：ディレクトリ存在検査、README 存在検査、`.gitkeep` 存在検査、パス規則の文言 grep 検査、`conformance/`／`reviews/` 分離の文言検査

### T-002：モード切替モデル（Mode Switch Model）

- **対応設計節**：design.md §3 モード切替モデル、§16 Decision 7（明示指定、自動判定なし）
- **対応要件**：Requirement 1 受入 4（2 モード）
- **責務**：照合チェックモード（check）と文書生成モード（generation）の 2 モードを切り替える入口を実装。**モード判定は明示指定のみ**（自動判定は行わない、Decision 7）。CLI またはパラメータで `check` ／ `generation` を受け取り、対応するパイプライン（T-003 ／ T-004）に振り分ける。両モードが共有する 6 criteria 構造（T-005）と 3 役レビュー機構（T-008）への参照を確立する
- **前提タスク**：T-001
- **成果物**：
  - `tools/conformance_evaluation/mode_switch.py`（check／generation の明示指定処理、パイプライン振り分け）
- **完了条件**：
  1. モードが `check` ／ `generation` の明示指定で受け取られ、未知の値が fail-closed になることが機械検証される
  2. 自動判定のロジックが存在しない（明示指定のみ）ことが運用文書に明示される（Decision 7）
  3. 各モードへの**ディスパッチ機構（つなぎ口＝インタフェース）が確立**される（check → T-004、generation → T-003）。完了条件は実体パイプラインの完成でなく**インタフェースの確立**で判定し、T-002 ↔ T-003／T-004 の循環を避ける（topic-120／G-005 対処、2026-05-29 セッション 39）
- **テスト要件**：モード判定テスト（check／generation／未知値 fail-closed）、振り分けテスト、明示指定のみの文書検査

### T-003：文書生成モード（Generation Model、傍流・人協働）

- **対応設計節**：design.md §6.1〜§6.7
- **対応要件**：Requirement 2 受入 1〜7
- **責務**：上流文書のないコードベースから上流文書の骨子を **人協働で** 推定生成する。4 階層の扱い分け（§6.2）：feature-partitioning は機械的候補提示 → 人が境界決定、intent は参考情報として推察 → 人が補完、requirements ／ design は自動推定 → 人が修正、tasks は対象外。出力先パス規則（§6.3、Req 2 受入 2）。各推定文書は最低 3 節（Introduction ／ Boundary Context ／ Requirements 相当）＋実装コード参照を最低 1 件含む（Req 2 受入 3、MV-4 ／ MV-5 連動）。推定根拠の保持（§6.4、Req 2 受入 4）。人間判断の必要性の明示（§6.5、Req 2 受入 5）。各推定段階に 3 役レビュー機構を適用（§6.6 ／ T-008）。実行記録を `conformance/<日付>-generation.md` に保管（§6.7、Req 2 受入 7）
- **前提タスク**：T-002、T-006（推定モデル）、T-008（3 役レビュー機構）
- **成果物**：
  - `tools/conformance_evaluation/generation_mode.py`（4 階層の扱い分け ＋ 推定生成 ＋ 人協働の判断必要性明示）
- **完了条件**：
  1. 4 階層が扱い分けされる（feature-partitioning ／ intent は人協働、requirements ／ design は自動推定、tasks 対象外）ことが機械検証される
  2. 推定文書が §6.3 のパス規則で出力される
  3. 各推定文書が最低 3 節（Introduction ／ Boundary Context ／ Requirements 相当）を含む（MV-4）
  4. 各推定要素に実装コード参照（`<ファイルパス>:<行範囲>`）が最低 1 件含まれる（MV-5）
  5. 人間判断の必要性が推定結果に明示される（特に feature-partitioning ／ intent）
  6. 実行記録が `conformance/<日付>-generation.md` に保管される（`mode_internal: generation`、T-009 連動）
- **テスト要件**：4 階層扱い分けテスト、パス規則テスト、3 節必須テスト（MV-4）、コード参照テスト（MV-5）、人間判断明示テスト、実行記録保管テスト、**feature-partitioning 候補提示の出力形式テスト（topic-117／F-008 対処）**

### T-004：照合チェックモード（Check Model、本筋・二段階方式）

- **対応設計節**：design.md §7.1〜§7.9
- **対応要件**：Requirement 3 受入 1〜8
- **責務**：二段階方式（§7.1）を実装。**第 1 段階＝推定**：既存 feature-partitioning を入力として尊重しつつ、他の既存上流文書（intent／requirements／design）を**遮断**した状態で実装コードから design ／ requirements を推定（intent は最後に参考情報）。**第 2 段階＝比較**：既存上流文書を読み込み推定結果と比較、食い違いを列挙（T-007 比較モデル）。既存上流文書の遮断手法（§7.3）：推定役プロンプトへの混入禁止＋自律ファイル探索禁止条項、MV-6 で fail-closed 検知（遮断必須）。feature-partitioning だけ例外とする理由は照合成立性（§7.2）。intent は参考情報扱い（§7.5、Req 3 受入 3）。機能分割自体の食い違い検出はオプション（§7.6、Req 3 受入 4、標準動作外）。4 段重大度の付与（§7.7、Req 3 受入 5）。実行記録を `conformance/<日付>-check.md` に保管（§7.9、Req 3 受入 8）
- **前提タスク**：T-002、T-006（推定）、T-007（比較）、T-008（3 役レビュー機構）
- **成果物**：
  - `tools/conformance_evaluation/check_mode.py`（二段階方式 ＋ 遮断手法 ＋ feature-partitioning 例外 ＋ 4 段重大度）
- **完了条件**：
  1. 二段階方式（第 1 段階推定 → 第 2 段階比較）が順序どおり実行されることが機械検証される
  2. 第 1 段階で既存上流文書（intent／requirements／design）が遮断され、推定役プロンプトに既存上流文書のパス・内容が含まれないことが MV-6 で検知される（混入時は **遮断必須＝即時停止**、design §18.3）
  3. feature-partitioning だけは推定時入力として尊重される（照合成立性のため、§7.2）
  4. intent は参考情報として比較され must-fix 判定の対象外（Req 3 受入 3）
  5. 機能分割食い違い検出は利用者明示要求時のみのオプションで、標準動作に含まれない（Req 3 受入 4）
  6. 食い違いに 4 段重大度（CRITICAL／ERROR／WARN／INFO）が付与される（foundation 語彙参照）
  7. 実行記録が `conformance/<日付>-check.md` に保管される（`mode_internal: check`、T-009 連動）
- **テスト要件**：二段階方式の順序テスト、遮断テスト（MV-6 混入検知 → 遮断必須）、feature-partitioning 例外テスト（**＋ feature-partitioning が推定モジュールに渡される肯定確認テスト、topic-117／F-008 対処**）、intent 参考情報テスト、オプション機能テスト（**CLI 引数 `--check-partitioning` の付与／不付与で標準動作に含まれないことを確認、topic-118／F-012 対処**）、4 段重大度テスト、実行記録保管テスト

### T-005：6 criteria 検査構造（Six Criteria Structure）

- **対応設計節**：design.md §8.1〜§8.5
- **対応要件**：Requirement 1 受入 5、Requirement 4 受入 1〜5
- **責務**：6 criteria（requirements conformance 3 ＋ design conformance 3、§8.1）を符号化。axis（requirements ／ design の 2 値）と criterion-1〜6 の ID を定義（F-004 対処）。照合対象から除外する 3 階層（feature-partitioning ／ intent ／ tasks、§8.2、Req 4 受入 2）。各 criterion のサブ構造（要点／詳細抽出／深掘り／該当なし、§5.9.2 規律継承、§8.3）。実装適合との分離（§8.4、本機能の責務外）。検査仕様を `schemas/review-criteria/conformance_evaluation.yaml` として整備（§8.5、Req 4 受入 5、implementation.drafting で配置済み → DVT-C001 解除）
- **前提タスク**：T-001
- **成果物**：
  - `tools/conformance_evaluation/criteria.py`（6 criteria の axis ／ criterion ID 定義 ＋ 除外階層判定）
  - `schemas/review-criteria/conformance_evaluation.yaml`（6 criteria の検査仕様。implementation.drafting で配置済み、DVT-C001 解除）
- **完了条件**：
  1. 6 criteria（requirements 3 ＋ design 3）が axis（**requirements ／ design の 2 値**）× criterion ID（criterion-1〜6）で符号化され、未知の axis ／ criterion が fail-closed になる。**intent は axis の 3 値目にせず、参考情報専用フィールド `reference_axis` に分離**するため、2 値 fail-closed が intent 差異記録（design §10.5）を弾かない（topic-111／G-003 対処、2026-05-29 セッション 39）
  2. 照合対象から除外する 3 階層（feature-partitioning ／ intent ／ tasks）が機械検証される（照合対象に含めない）
  3. 各 criterion がサブ構造（要点／詳細抽出／深掘り／該当なし）を持つ（§5.9.2 規律継承）
  4. `conformance_evaluation.yaml` は 6 criteria を網羅し、推定（T-006）・比較（T-007）の検査構造と整合することを確認する（implementation.drafting で配置済み、DVT-C001 解除）
- **テスト要件**：6 criteria 符号化テスト、axis ／ criterion 値域テスト、除外階層テスト、サブ構造テスト、`conformance_evaluation.yaml` 整合テスト

### T-006：推定モデル（Estimation Model）

- **対応設計節**：design.md §9.1〜§9.5
- **対応要件**：Requirement 1 受入 1（推定方向）、Requirement 2 受入 1（生成モードの推定）、Requirement 3 受入 1（照合モードの推定）
- **責務**：実装コードから上流文書（requirements ／ design 中心、intent 参考）を推定。**推定順序：design 先行 → requirements 逆算**（§9.2、Decision 10、F-008 対処、順序依存を機械保証）。推定対象の階層別扱い（§9.3）。推定根拠の保持（§9.4、`<ファイルパス>:<行範囲>` 形式、MV-5 連動）。推定の信頼度（§9.5、high ／ medium ／ low、**foundation 語彙体系の信頼度ラベルを参照**、A-013 対処済み、Decision 11）
- **前提タスク**：T-005
- **成果物**：
  - `tools/conformance_evaluation/estimation_model.py`（design 先行 → requirements 逆算の順序 ＋ 推定根拠保持 ＋ 信頼度判定）
- **完了条件**：
  1. 推定順序が design 先行 → requirements 逆算で実行されることが単体テストで機械検証される（§9.2、F-008 対処）
  2. 推定根拠が `<ファイルパス>:<行範囲>` 形式で保持される（MV-5 連動）
  3. 信頼度が high ／ medium ／ low で判定され、**foundation 語彙正本を参照**（再定義しない、A-013 対処済み、Decision 11、§14.1）
  4. 推定対象の階層別扱い（requirements ／ design 中心、intent 参考、feature-partitioning ／ tasks 対象外）が機械検証される
- **テスト要件**：推定順序テスト（design → requirements）、推定根拠形式テスト、信頼度判定テスト（foundation 語彙参照の確認）、階層別扱いテスト、サンプルアプリ（1000 行規模、§19.1）での推定受入テスト

### T-007：比較モデル（Comparison Model）

- **対応設計節**：design.md §10.1〜§10.7
- **対応要件**：Requirement 3 受入 2（食い違い検出）、Requirement 3 受入 3（intent 差異記録）
- **責務**：既存上流文書と推定上流文書を比較し食い違いを列挙。比較対象粒度（§10.2、6 criteria の各 criterion）。比較アルゴリズム（§10.3）：3 対応関係（節の有無 ／ 節内の主張・受入基準の対応 ／ 実装コードへの言及齟齬）のいずれかに不整合があれば「食い違い」（Req 3 受入 2）。食い違いの記録形式（§10.4）。intent の差異記録（§10.5、所見メタとして記録、must-fix 対象外、Req 3 受入 3）。比較結果の出力（§10.6）。**finding_id ／ judgment_id 発番ルール（§10.7、CF-NNN ／ JD-NNN、A-002 対処、Decision 9）**
- **前提タスク**：T-006
- **成果物**：
  - `tools/conformance_evaluation/comparison_model.py`（3 対応関係の判定 ＋ 食い違い記録 ＋ CF-NNN ／ JD-NNN 発番）
- **完了条件**：
  1. 3 対応関係（節有無 ／ 主張対応 ／ コード言及齟齬）が判定され、いずれかの不整合で食い違いと記録される（Req 3 受入 2）
  2. 比較対象粒度が 6 criteria の各 criterion 単位である（T-005 連動）
  3. intent の差異が所見メタとして記録され must-fix 対象外であることが機械検証される（Req 3 受入 3）
  4. finding_id（CF-NNN）／ judgment_id（JD-NNN）の発番が §10.7 の規則どおり機能する（採番衝突がない。self-improvement topic-99 の教訓に倣い、移動・分散があっても重複しない走査範囲を確認）
- **テスト要件**：3 対応関係判定テスト、criterion 単位粒度テスト、intent 差異記録テスト（must-fix 対象外、`reference_axis` フィールドへの記録、topic-111 連動）、CF-NNN ／ JD-NNN 発番テスト（衝突回避＋**最初の採番（CF-001）・3 桁 → 4 桁拡張（999 → 1000）の境界、topic-118／F-011 対処**）、既存上流文書ありサンプルアプリでの照合受入テスト

### T-008：3 役レビュー機構の適用（Triad Review Application）

- **対応設計節**：design.md §11.1〜§11.4
- **対応要件**：Requirement 2 受入 6、Requirement 3 受入 6／7、Requirement 5 受入 1〜8
- **責務**：3 役レビュー機構（主役 → 敵対役 → 判定役）を **推定段階と照合段階の両方** に適用（§11.1）。軽量／本格の使い分け（§11.2、Req 5 受入 2）：本格適用＝feature-partitioning 推定（傍流）・requirements 推定・照合段階、軽量適用＝design 推定・intent 推察。§5.9 規律の流用（§11.3）：モデル多様化・ファイル遮断・β 逐次方式・重大度語彙 4 段・所見メタデータ必須化（severity ／ judgment ／ depth ／ evidence_type ／ verifying_commands）・3 方式比較データ（`findings_by_method`）・レビューモード語彙（**foundation 参照**）。API 経路と障害対応（§11.4、§5.9.7 流用、タイムアウト・リトライ・部分失敗）。**責務境界（topic-113／F-001 対処、2026-05-29 セッション 39）**：本タスクは §5.9 規律のメタ情報（severity ／ judgment ／ depth ／ evidence_type ／ verifying_commands）の流用のみを担い、axis ／ criterion_id の生成・参照は推定（T-006）・比較（T-007）の責務。よって前提タスクは T-001 のみで足り、T-005（6 criteria 定義）を直接の前提に必要としない（過剰な直列化を避ける）
- **前提タスク**：T-001（T-005 を直接の前提にしない理由は上記責務境界を参照）
- **成果物**：
  - `tools/conformance_evaluation/triad_review.py`（軽量／本格の使い分け ＋ §5.9 規律流用 ＋ API 障害対応）
- **完了条件**：
  1. 3 役レビュー機構が推定段階・照合段階の両方で適用される（§11.1）
  2. 軽量／本格の使い分けが §11.2 の対応どおり判定される（本格＝requirements 推定・照合等、軽量＝design 推定・intent 推察）
  3. §5.9 規律（モデル多様化・ファイル遮断・β 逐次・重大度 4 段・所見メタ必須・findings_by_method）が適用される
  4. レビューモード語彙・重大度語彙・信頼度ラベルが **foundation 正本を参照**（再定義しない）
  5. API 障害対応（タイムアウト・リトライ・部分失敗の検知と扱い）が §5.9.7 から流用される
- **テスト要件**：両段階適用テスト、軽量／本格使い分けテスト、§5.9 規律適用テスト、foundation 語彙参照テスト、API 障害対応テスト（タイムアウト・リトライ・部分失敗）

### T-009：評価記録の type 値と配置（Evaluation Record Type and Placement）

- **対応設計節**：design.md §12.1〜§12.4
- **対応要件**：Requirement 6 受入 1〜5
- **責務**：評価記録の `type` 値を `conformance_evaluation` に統合（§12.1、生成／照合の区別は内部フィールド）。配置先 `conformance/<日付>-<mode>.md`（§12.2、`reviews/` と別、Req 8 受入 4）。front-matter の構造（§12.3）：`mode_internal: generation` ／ `check`、`author` ／ `reviewer`（§5.4 規律、異名必須）、**`target_commit`（conformance-evaluation 所有）と `materialization_commit_hash`（self-improvement 所有）の整合ルール（G10 対処、A-016 対処済み、§12.3）**。関連実行記録への参照（§12.4、runtime ／ evaluation ／ workflow-management、Req 6 受入 5）
- **前提タスク（硬い依存と緩い依存を区別、topic-114／F-002 対処、2026-05-29 セッション 39）**：硬い依存（着手前提）＝T-003、T-004。緩い依存（完了検証前提＝起草は先行可だが完了条件のクローズ前に成果物が必要）＝T-006（推定、finding_id ／ axis ／ criterion_id の形式）、T-007（比較、judgment_id の形式）。self-improvement の硬い／緩い依存区別を流用
- **成果物**：
  - `tools/conformance_evaluation/evaluation_record.py`（type 統合 ＋ front-matter ＋ 関連参照）
  - `tools/conformance_evaluation/schemas/evaluation_record.schema.json`（評価記録 front-matter スキーマ）
- **完了条件**：
  1. 評価記録の `type` が `conformance_evaluation` に統合される（MV-1）
  2. `mode_internal` が `generation` ／ `check` のいずれかである（MV-2）
  3. 評価記録が `conformance/` ディレクトリに配置され `reviews/` と混在しない（MV-3）
  4. `author` ／ `reviewer` が §5.4 規律に従い異名で明示される
  5. `target_commit`（本機能所有）と `materialization_commit_hash`（self-improvement 所有）の独立性・整合ルールが §12.3 と整合する（A-016 対処済み）
  6. runtime ／ evaluation ／ workflow-management の関連実行記録への参照が保持される
- **テスト要件**：type 統合テスト（MV-1）、mode_internal テスト（MV-2）、ディレクトリ分離テスト（MV-3）、author／reviewer 異名テスト、commit hash 整合テスト、関連参照テスト

### T-010：依存関係の連想配列構造（Associative Dependency Structure）

- **対応設計節**：design.md §13.1〜§13.5
- **対応要件**：Requirement 7 受入 1〜5
- **責務**：`stages/feature-dependency.yaml` における本機能の依存記述を**連想配列構造**（`depends_on: {feature_name: dependency_type}`）で表現（§13.1、他機能の単純リストと異なる）。依存種別 2 値（`hard` ／ `review`、§13.2）。依存記述の確定値（§13.3）：`foundation: hard` ／ `runtime: review` ／ `evaluation: review` ／ `workflow-management: review`。**workflow-management のスキーマ拡張（連想配列許容、Req 8 受入 2）との整合（§13.4）**。phase_order の最後（§13.5、依存先がすべて先に完了）
- **前提タスク**：T-001
- **成果物**：
  - `stages/feature-dependency.yaml` への本機能の連想配列構造エントリ（または design 参照先の確定記述）
- **完了条件**：
  1. 本機能の依存記述が連想配列構造（`{feature_name: dependency_type}`）で表現される（他機能の単純リストと区別）
  2. 依存種別が `hard` ／ `review` の 2 値で区別される（未知値は fail-closed）
  3. 確定値（foundation: hard ／ runtime: review ／ evaluation: review ／ workflow-management: review）と一致する
  4. workflow-management のスキーマ拡張（Req 8 受入 2 の連想配列許容）と整合する（DVT-C002 解除済 2026-05-29：workflow-management T-002 の feature-dependency.schema.json／完了条件2 と仕様レベルで完全一致を確認）
  5. phase_order の最後に位置付けられる
- **テスト要件**：連想配列構造解釈テスト、hard ／ review 区別テスト、確定値整合テスト、workflow-management スキーマ整合テスト（consumer 側、producer 側 workflow-management は機能横断段で対をなす）、phase_order テスト

### T-011：他機能との接合面（Interfaces with Other Features）

- **対応設計節**：design.md §14.1〜§14.6
- **対応要件**：Boundary Context 隣接期待（foundation ／ runtime ／ evaluation ／ analysis ／ workflow-management ／ self-improvement の 6 機能）
- **責務**：6 機能との接合面を整備。**foundation**（§14.1、依存 hard）：スキーマ・メタデータ契約・各語彙・信頼度ラベルを再定義せず参照。**runtime**（§14.2、依存 review）：実装コードのレビュー実行記録を入力源として読む。**evaluation**（§14.3、依存 review、G10 対処）：評価結果との突き合わせ詳細（経路別差分 ／ severity 集計 ／ `role_diff_report.json`（A-011 対処済み））。**workflow-management**（§14.4、依存 review）：所定手続きの実行履歴と上流文書の整合確認。**analysis**（§14.5、G10 対処）：6 criteria 検査結果を機械可読出力スキーマで提供（analysis が 4 出力先に取り込む）。**self-improvement**（§14.6、G10 対処）：6 criteria 検査結果を規律改善の入力として提供（self-improvement が本機能の出力を読む方向、本機能の `depends_on` には含まれない）。`target_commit`（本機能所有）と `materialization_commit_hash`（self-improvement 所有）の独立性（A-016 対処済み）
- **前提タスク**：T-006、T-007、T-009
- **成果物**：
  - `tools/conformance_evaluation/interfaces.py`（consumer 側＝foundation 語彙参照・runtime ／ evaluation ／ workflow-management 入力読み取り、producer 側＝analysis ／ self-improvement 向け出力）
- **完了条件**：
  1. foundation 語彙正本を再定義せず参照のみで使用していることが機械検証される（grep 検査）
  2. runtime ／ evaluation ／ workflow-management の出力を入力源として読める（依存 review）
  3. evaluation 接合面の突き合わせ詳細（`role_diff_report.json`（A-011 対処済み）を含む）が §14.3 と整合する
  4. analysis 向け出力が機械可読スキーマで提供される（§14.5、analysis Req 8 受入 5 由来）
  5. self-improvement 向け出力（6 criteria 検査結果）が提供され、方向が「conformance-evaluation → self-improvement」である（§14.6、本機能の depends_on には含まれない）
  6. `target_commit` ／ `materialization_commit_hash` の独立性（A-016 対処済み）が §12.3 ／ §14.6 と整合する
- **テスト要件**：foundation 語彙不再定義テスト（grep）、3 機能入力読み取りテスト、evaluation 突き合わせテスト、analysis 出力スキーマテスト、self-improvement 出力方向テスト、commit hash 独立性テスト

### T-012：機械検査の具体手段（Machine Verification）

- **対応設計節**：design.md §18.1〜§18.4
- **対応要件**：Requirement 6（評価記録の機械検査）、Requirement 8 受入 4（ディレクトリ分離検査）
- **責務**：7 つの機械検査ポイント（§18.1）を実装。**MV-1**：`type: conformance_evaluation` 設定（grep）。**MV-2**：`mode_internal` が check ／ generation（grep ＋値照合）。**MV-3**：`conformance/` と `reviews/` のディレクトリ分離（find ＋照合）。**MV-4**：推定文書の必須 3 節（grep）。**MV-5**：推定根拠の実装コード参照（grep ＋形式照合）。**MV-6**：既存上流文書遮断の事前検査（推定役プロンプトに既存上流文書混入なし＋自律探索禁止条項、grep ＋プロンプトログ）。**MV-7**：foundation 受入番号照合（G9 対処、本機能の `foundation Requirement N 受入 M` 記述が foundation requirements.md と一致、grep ＋機械照合）。**fail-closed の粒度別適用（§18.3）**：遮断必須＝MV-6 ／ 遮断推奨＝MV-1・MV-2・MV-3 ／ 警告続行可＝MV-4・MV-5・MV-7。第 1 期は手動 grep ／ find、フェーズ 4 で段階自動化（§18.4、DVT-C003）。**MV-6 の第 1 期最小仕様（topic-116／F-007 対処、2026-05-29 セッション 39、Sonnet API 別案＝段階的具体化を採用）**：推定役プロンプトログの必須フィールド（時刻 ／ 実行 ID ／ プロンプト全文）、格納先ディレクトリ命名規則（例 `logs/estimation/<run_id>/prompt.log`）、MV-6 実行用 grep 雛形 2 条件（(a) 既存上流文書パスの不在確認 (b) 自律探索禁止条項の存在確認）を tasks に記述する。技術手段の詳細確定（プロセス隔離等）は DVT-C004（フェーズ 4 第 2 サイクル）連動で予約
- **前提タスク（硬い依存と緩い依存を区別、topic-114／F-002 対処）**：硬い依存（着手前提）＝T-003、T-004、T-009。緩い依存（完了検証前提）＝T-006（MV-5 の推定根拠形式の検査対象 ／ MV-7 の foundation 参照記述の検査対象）
- **成果物**：
  - `tools/conformance-evaluation-check.py`（MV-1〜MV-7 の検査。第 1 期は手動 grep の補助、自動化はフェーズ 4 第 1〜2 サイクル）
  - `docs/operations/CONFORMANCE_EVALUATION.md` への MV-1〜MV-7 の検査手順記述
- **完了条件**：
  1. MV-1〜MV-7 の各検査が定義どおり機能する（§18.1）
  2. fail-closed の粒度が MV ID 別に区別される（遮断必須＝MV-6 ／ 遮断推奨＝MV-1〜3 ／ 警告続行可＝MV-4・5・7、§18.3）
  3. MV-6（遮断必須）は推定役プロンプトへの既存上流文書混入を検知し即時停止する（T-004 連動）
  4. MV-7 が foundation requirements.md の最新受入番号と本機能の参照を機械照合する（foundation 改訂追従）
  5. 検査結果が評価記録本文の「機械検査結果」節に記録される
  6. workflow-management の `check-workflow-action.py` との責務分担（§18.2）が運用文書に明示される
- **テスト要件**：MV-1〜MV-7 の各検査テスト（正常系 ／ 異常系）、fail-closed 粒度別テスト（遮断必須 ／ 推奨 ／ 警告続行）、MV-6 混入検知テスト、MV-7 番号照合テスト、責務分担の文書検査

### T-013：テスト戦略全体の整備（Test Strategy）

- **対応設計節**：design.md §19.1〜§19.4、§20.3 起草完了基準
- **対応要件**：本機能全要件の機械的合否判定、要件追跡表（§15）の双方向整合、DVT 解除確認
- **責務**：design.md §19 で定義された 8 モデル × 3 テストレベル（単体 ／ 結合 ／ 受入）をすべて Python テストとして整備、pytest で一括実行可能にする。重点ポイント（§19.2：既存上流文書の遮断（MV-6）／ feature-partitioning の例外扱い ／ 推定の信頼度 ／ 6 criteria の網羅 ／ 推定順序（design 先行 → requirements 逆算）／ foundation 受入番号照合（MV-7）／ contract ownership map と spec update proposals）。テストデータ取得元（§19.4：サンプルアプリのコード ／ 既存上流文書 ／ 既存 feature-partitioning）。要件追跡表（design §15）と各タスク本文の対応要件欄の双方向整合チェック（self-improvement T-011 の方針継承）。**遅延確認事項テーブル（DVT）内の未解除項目がない、または延期理由が明記されている**ことを完了条件にゲート化
- **前提タスク**：T-001 ／ T-002 ／ T-003 ／ T-004 ／ T-005 ／ T-006 ／ T-007 ／ T-008 ／ T-009 ／ T-010 ／ T-011 ／ T-012
- **成果物**：`tests/conformance-evaluation/` 配下のテストファイル群（推定 ／ 比較 ／ モード切替 ／ 3 役レビュー ／ 評価記録 ／ 依存関係 ／ 機械検査の各テスト＋要件追跡整合テスト）
- **完了条件**：すべての pytest が pass、8 モデル × 3 テストレベルを網羅、foundation 語彙正本の参照のみ使用が機械検証される、6 criteria の網羅、推定順序（design → requirements）が単体テストで検証される、二段階方式と遮断（MV-6）が網羅される、contract ownership map と spec update proposals が検証される、要件追跡表の双方向整合が機械チェックされる、DVT 内の未解除項目がない（または延期理由が明記されている）
- **テスト要件**：すべての pytest が pass、回帰なし、要件追跡表の双方向整合チェック、DVT ゲート化、サンプルアプリでの両モード End-to-End 受入テスト

### T-014：契約所有候補と仕様更新草案（Contract Ownership and Spec Update Drafts）

- **対応設計節**：design.md §13.6 契約所有候補と仕様更新草案
- **対応要件**：Requirement 9 受入 1〜5
- **責務**：照合チェックで見つかった実装由来契約を contract ownership map に登録し、requirements.md, design.md, tasks.md のどこへ反映すべきかを provisional に分類する。spec update proposals を評価記録に含め、draft-only spec update artifacts を `conformance/<日付>-spec-update-drafts/` に出力する。草案は `apply_status: draft_only` を持ち、実際の requirements.md, design.md, tasks.md は直接書き換えない。ownership-unclear または carry_forward の契約は `needs_human_decision: true` とする。
- **前提タスク**：T-004、T-007、T-009
- **成果物**：
  - `tools/conformance_evaluation/contract_ownership.py`（contract ownership map、spec update proposals、draft-only spec update artifacts）
  - `tests/fixtures/conformance-evaluation/*contract-ownership.yaml`（代表 fixture）
  - `.reviewcompass/specs/<feature>/conformance/<日付>-spec-update-drafts/*.md`（必要時に生成される草案）
- **完了条件**：
  1. contract ownership map が契約 ID、所有候補、証跡参照、関連クラスタを保持する
  2. primary owner に応じて requirements.md, design.md, tasks.md の更新候補へ分類できる
  3. spec update proposals が評価記録に出力される
  4. draft-only spec update artifacts がファイルとして生成され、仕様本文を直接変更しない
  5. 人間判断が必要な候補を `needs_human_decision` で明示できる
- **テスト要件**：contract ownership map の値域検査、update candidate 分類テスト、spec update proposals 出力テスト、draft-only spec update artifacts 生成テスト、requirements.md, design.md, tasks.md を直接変更しないことの回帰テスト

### T-015：機能横断 drift workflow の正式化

- **対応設計節**：design.md §13.6 契約所有候補と仕様更新草案、§19 テスト戦略
- **対応要件**：Requirement 9 受入 1〜5、および機能横断 conformance check の carry-forward 所見 XDI-CE-001
- **責務**：cross-feature drift workflow を conformance-evaluation の正式運用として定義する。`tools/conformance-evaluation-cross-feature.py` を標準 CLI 入口、`tools/conformance_evaluation/cross_feature_workflow.py` を内部 workflow 実装とし、code → ownership fixture、check record、spec update drafts、spec adoption、spec triad traceability test、commit の順に進め、実装由来契約を requirements.md／design.md／tasks.md の三文書から追跡可能にする。cross-feature drift clustering と contract ownership outputs は単発のドラフト生成成果物ではなく、再実行可能な workflow として扱う。
- **前提タスク**：T-014
- **成果物**：
  - `tests/fixtures/conformance-evaluation/cross-feature-contract-ownership.yaml`
  - `tools/conformance-evaluation-cross-feature.py`
  - `tools/conformance_evaluation/cross_feature_workflow.py`
  - `.reviewcompass/specs/_cross_feature/conformance/<日付>-check.md`
  - `.reviewcompass/specs/_cross_feature/conformance/<日付>-spec-update-drafts/*.md`
  - `tools/conformance_evaluation/spec_triad_traceability.py`
  - `tests/conformance-evaluation/test_spec_update_adoption.py`
  - `docs/operations/CONFORMANCE_EVALUATION.md`
  - 採用判断と再実行手順を記録する tasks 更新
- **完了条件**：
  1. cross-feature drift clustering が全 7 機能を代表する drift item を保持し、関連クラスタと証跡参照を失わない
  2. contract ownership outputs が対象仕様ファイル単位に畳み込まれ、requirements.md、design.md、tasks.md の更新候補へ分類される
  3. `ownership-unclear` または `carry_forward` の item は `needs_human_decision: true` として follow-up implementation decision に残る
  4. `_cross_feature` の check record と spec update drafts が、単一機能の conformance output と同じ形で再生成できる
  5. spec triad traceability test が、各 XDI ID を対象 feature の requirements.md／design.md／tasks.md すべてから追跡できることを検査する
  6. `docs/operations/CONFORMANCE_EVALUATION.md` に cross-feature drift workflow の手順が記録され、commit までの運用順序が説明される
- **テスト要件**：代表 fixture の 7 機能被覆テスト、cross-feature drift clustering のクラスタ保持テスト、contract ownership outputs の target file 分類テスト、`needs_human_decision` 判定テスト、`tools/conformance_evaluation/spec_triad_traceability.py` と `tests/conformance-evaluation/test_spec_update_adoption.py` による spec triad traceability test、`docs/operations/CONFORMANCE_EVALUATION.md` の cross-feature drift workflow 記述検査

## 要件追跡（Requirements Traceability）

| 要件 | 対応タスク |
|------|-----------|
| Requirement 1 受入 1：下流→上流、4 階層 | T-006（推定）＋ T-005（§8.2 照合除外＝feature-partitioning／intent／tasks を対象外とする、topic-115 で追記） |
| Requirement 1 受入 2：上流文書なくてもよい | T-003（生成モード） |
| Requirement 1 受入 3：実装適合レビュー非吸収 | T-011（接合面 §14.2）＋スコープ前提 |
| Requirement 1 受入 4：2 モード | T-002（モード切替） |
| Requirement 1 受入 5：同一 6 criteria | T-005 |
| Requirement 2 受入 1：4 階層扱い分け | T-003 ＋ T-006（推定） |
| Requirement 2 受入 2：出力先パス規則 | T-001 ＋ T-003 |
| Requirement 2 受入 3：3 節必須 | T-003（MV-4） |
| Requirement 2 受入 4：推定根拠保持 | T-006（§9.4、MV-5） |
| Requirement 2 受入 5：人間判断必要性明示 | T-003 |
| Requirement 2 受入 6：3 役レビュー適用 | T-008 |
| Requirement 2 受入 7：実行記録保管 | T-003 ＋ T-009 |
| Requirement 3 受入 1：二段階方式 | T-004 |
| Requirement 3 受入 2：食い違い検出 | T-007（比較） |
| Requirement 3 受入 3：intent 参考情報 | T-004 ＋ T-007（§10.5） |
| Requirement 3 受入 4：機能分割食い違いオプション | T-004（§7.6） |
| Requirement 3 受入 5：4 段重大度 | T-004（foundation 語彙参照） |
| Requirement 3 受入 6／7：3 役レビュー（受入 7 の判定値保持） | T-008 ＋ T-007（judgment_id（JD-NNN）発番、§10.4／§10.7、topic-115 で追記） |
| Requirement 3 受入 8：実行記録保管 | T-004 ＋ T-009 |
| Requirement 4 受入 1：6 criteria | T-005 |
| Requirement 4 受入 2：照合対象除外 | T-005（§8.2） |
| Requirement 4 受入 3：サブ構造 | T-005（§8.3） |
| Requirement 4 受入 4：実装適合分離 | T-005（§8.4）＋スコープ前提 |
| Requirement 4 受入 5：検査仕様整備 | T-005（conformance_evaluation.yaml、DVT-C001） |
| Requirement 5 受入 1：両段階適用 | T-008 |
| Requirement 5 受入 2：軽量／本格 | T-008（§11.2） |
| Requirement 5 受入 3〜8：§5.9 規律流用 | T-008（§11.3／§11.4） |
| Requirement 6 受入 1：type 値統合 | T-009（MV-1） |
| Requirement 6 受入 2：配置先 | T-001 ＋ T-009（MV-3） |
| Requirement 6 受入 3：mode_internal | T-009（MV-2） |
| Requirement 6 受入 4：author／reviewer | T-009 |
| Requirement 6 受入 5：関連参照 | T-009 |
| Requirement 7 受入 1：連想配列構造 | T-010 |
| Requirement 7 受入 2：hard／review | T-010 |
| Requirement 7 受入 3：依存記述確定値 | T-010 |
| Requirement 7 受入 4：workflow-management スキーマ整合 | T-010（DVT-C002） |
| Requirement 7 受入 5：phase_order 最後 | T-010 |
| Requirement 8 受入 1：実装適合レビュー責務なし | T-011 ＋スコープ前提 |
| Requirement 8 受入 2：実装適合は §5.9／runtime に残る | T-011（§14.2） |
| Requirement 8 受入 3：3 軸性格差 | スコープ前提（概要章） |
| Requirement 8 受入 4：ディレクトリ分離 | T-001 ＋ T-009（MV-3） |
| Requirement 9 受入 1：contract ownership map | T-014 |
| Requirement 9 受入 2：requirements.md, design.md, tasks.md への分類 | T-014 |
| Requirement 9 受入 3：spec update proposals | T-014 |
| Requirement 9 受入 4：draft-only spec update artifacts | T-014 |
| Requirement 9 受入 5：needs_human_decision | T-014 |
| Boundary Context 隣接期待（6 機能） | T-011 |
| 機械検査（MV-1〜MV-7） | T-012 |

## テスト戦略の継承（Test Strategy Inheritance）

design.md §19 のテスト戦略を T-013 にまとめて継承する。各テストレベルの対応タスク：

- 単体テスト → T-002 ／ T-005 ／ T-006 ／ T-007 ／ T-009 ／ T-010 ／ T-012 個別 ＋ T-013 統合
- 結合テスト → T-003 ／ T-004 ／ T-008 ／ T-011 個別 ＋ T-013 統合
- 受入テスト → サンプルアプリ（1000 行規模、§19.1）での両モード End-to-End ＋ T-013 統合
- 異常系 fail-closed → 各タスクで fail-closed テスト（特に MV-6 遮断必須）＋ T-013 統合
- 境界条件 → T-006（推定順序）／ T-005（6 criteria 網羅）／ T-007（CF-NNN／JD-NNN 発番）＋ T-013 統合

## 完成判定基準（Completion Criteria）

本タスク文書は次を満たすときに完了とみなす：

- T-001〜T-014 のすべてが起草・実装・テスト・コミット完了
- design.md §20.3 起草完了基準の各項目が T-013 の統合テストで pass
- foundation が所有する語彙正本（スキーマ・メタデータ契約・各語彙・信頼度ラベル）を再定義せず参照のみで使用していることが機械検証される（§14.1、依存 hard）
- 二段階方式の遮断（MV-6 遮断必須）と推定順序（design 先行 → requirements 逆算）が機械検証される
- 6 criteria 検査構造（axis 2 値 × criterion-1〜6）が機械検証される
- 評価記録の type 統合（MV-1）・ディレクトリ分離（MV-3）が機械検証される
- 各タスクの成果物配置が design.md §12.2 ／ §18.2 と一致
- 各タスクの依存順が守られている（前提タスクなしで後続タスクを開始しない）
- 遅延確認事項テーブル（DVT）内の未解除項目がない（または延期理由が明記されている）

## 変更意図（Change Intent）

本タスク文書は conformance-evaluation 機能（下流 → 上流の逆方向、実装コードから上流文書を推定・照合）を実装するため、次を採用する：

- **一気通貫粒度**：1 タスク ＝ 1 つの所有モデル領域。self-improvement／workflow-management の粒度方針を継承
- **所有モデル単位の分離**：モード切替 §3 を T-002、文書生成モード §6 を T-003、照合チェックモード §7 を T-004、6 criteria §8 を T-005、推定 §9 を T-006、比較 §10 を T-007、3 役レビュー §11 を T-008、評価記録 §12 を T-009、依存関係 §13 を T-010、接合面 §14 を T-011、機械検査 §18 を T-012、テスト戦略 §19 を T-013、契約所有候補と仕様更新草案 §13.6 を T-014 に対応付け
- **依存順の明示（topic-113／F-001 対処でフロー図を整合修正、2026-05-29 セッション 39）**：T-001（配置）から **T-005（6 criteria）・T-002（モード切替）・T-008（3 役）が並列に分岐**（いずれも T-001 のみを前提とし、T-008 は T-005 を直接の前提にしない＝責務境界 §T-008 参照）。T-005 → T-006（推定）→ T-007（比較）。T-002／T-006／T-007／T-008 がそろって → T-003（生成）／ T-004（照合）→ T-009（評価記録）→ T-010（依存）／ T-011（接合面）→ T-012（機械検査）→ T-013（統合テスト）。データの流れ（design §1：実装コード → 推定 → 比較 → 評価記録）を依存順の基本とする
- **本筋と傍流の分離**：照合チェックモード（本筋、T-004）と文書生成モード（傍流・人協働、T-003）を別タスクに分離（Decision 1）
- **二段階方式と遮断の徹底**：照合チェックは推定（遮断）→ 比較の順。MV-6 で遮断必須の fail-closed（design §18.3）
- **contract consumer 原則**：foundation 語彙正本を再定義せず参照のみ（§14.1、依存 hard）、runtime ／ evaluation ／ workflow-management の出力を入力源として読む（依存 review）
- **fail-closed の粒度別適用**：MV ID 別に遮断必須／遮断推奨／警告続行可を区別（§18.3）
- **テスト戦略の継承**：design §19 の 8 モデル × 3 テストレベルを T-013 で網羅
- **要件追跡表の双方向整合チェックを T-013 に組み込み**：self-improvement T-011 の方針を踏襲
- **遅延確認事項テーブル（DVT）の活用**：未確定事項（検査仕様の配置 ／ workflow-management スキーマ整合 ／ 検査自動化 ／ 推定役遮断の技術手段）を DVT で集約管理、T-013 完了条件で未解除項目がないことをゲート化
- **自律進行**：実装段で per-task 承認は取らず、コミット・プッシュ・spec.json 更新・フェーズ移行のみ明示承認（規律 [[implementation-autonomy]] 準拠）

---

## 遅延確認事項テーブル（Deferred Verification Table、DVT）

本テーブルは tasks 段で参照される未確定上流仕様または将来確定予定の事項を集約管理する。self-improvement／workflow-management の DVT 同型運用。

| ID | 関連タスク | 遅延内容 | 解除トリガー | 状態 |
|---|---|---|---|---|
| DVT-C001 | T-005 | 6 criteria 検査仕様 `schemas/review-criteria/conformance_evaluation.yaml` の実体配置（design §8.5、Req 4 受入 5） | implementation.drafting で検査仕様を実体配置し、T-005 完了条件との整合を再確認済み | 解除済み（2026-06-04 implementation.drafting） |
| DVT-C002 | T-010 | workflow-management のスキーマ拡張（Req 8 受入 2、依存記述の連想配列構造の許容）との整合。本機能の連想配列構造 consumer 側と workflow-management 側 producer が対をなす | 全機能の tasks triad-review 完了後の機能横断段（tasks フェーズの review-wave 段）で workflow-management 側のスキーマ実装と突き合わせ確認（topic-118／F-016 で括弧書きを明確化） | 解除済（2026-05-29 セッション40、機能横断段で仕様レベルの突き合わせ確認を実施。本機能 T-010 が期待する連想配列構造（`{機能名: 依存種別}`、hard ／ review、確定値 foundation:hard ／ runtime:review ／ evaluation:review ／ workflow-management:review）と、workflow-management T-002（feature-dependency.schema.json で連想配列を許容、完了条件2 が同一確定値を保持）が完全一致。実体（schema.json）は実装フェーズで実現） |
| DVT-C003 | T-012 | `tools/conformance-evaluation-check.py` による MV-1〜MV-7 の自動化（design §18.4）。第 1 期（フェーズ 1〜3）は手動 grep ／ find | フェーズ 4 第 1 サイクル（MV-1〜3・MV-7 自動化）・第 2 サイクル（MV-4〜6 自動化）着手時に T-012 完了条件と整合を再確認 | 未解除（フェーズ 4 以降まで延期） |
| DVT-C004 | T-004 | 推定役プロセスの隔離・既存上流文書遮断の技術手段（design §7.3 で「具体手法は design 段で確定」、§18.4 で chroot 環境での厳格遮断はフェーズ 4 第 2 サイクル検討） | フェーズ 4 第 2 サイクルで推定役プロセス隔離の実装時に T-004 完了条件・MV-6 と整合を再確認 | 未解除（フェーズ 4 第 2 サイクルまで延期） |

**運用ルール**：

- 本テーブルの「未解除」項目があるとき、関連タスクは完了判定可能だが、解除トリガー発火時に再評価が必須
- T-013 完了条件は本テーブル内の未解除項目がない（または延期理由が明記されている）ことをゲート化
- 新規の遅延項目が発生した場合は本テーブルに追記、解除時に「状態」を「解除済（日付、解除根拠）」に更新

---

## 機能横断段への持ち越し事項

本機能の triad-review 段で発見された機能横断波及所見は、carry-forward register 正本 `learning/workflow/carry-forward-register/reviewcompass-import.yaml` に追記し、tasks の機能横断段（review-wave）で消化する。既登録の機能横断所見 A-017（機能横断波及の確認手順が tasks.md に未明示）／A-018（foundation 語彙正本の所有件数の食い違い）／A-019（workflow-management T-010 の approved_update スキーマと self-improvement §8.4 の不一致）は機能横断段（tasks review-wave、2026-05-29 セッション40）で一括消化済み（未消化 0 件）。本機能の接合面に関わる A-011（evaluation の role_diff_report.json）／A-012（self-improvement と workflow-management の時系列契約）は ✅ 対処済み（2026-05-26 セッション 28）。なお design §20.1 が A-011／A-012 を「消化予定」と記載しているのは陳腐化の可能性があり（self-improvement topic-103／G-001 と同型）、triad-review で確認する。7 モデル評価 2 回目と同根問題集約は本機能では実施せず、機能横断段で一括実施する（2 回方式、計画書 §5.5 ／ §5.9.6）。DVT-C002（workflow-management スキーマ整合）も機能横断段で消化済み（解除済、2026-05-29 セッション40）。
