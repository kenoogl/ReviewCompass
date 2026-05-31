# あなたへの依頼

あなたは ReviewCompass プロジェクトの独立検証者です。新規律「post-write-verification（書き込み後の独立検証）」の 3 草案を批判的に検証してください。あなたはこの議論の文脈を一切共有しておらず、起草者の解釈・判断理由・議論ログは渡されていません（情報最小化、枠組み伝染バイアス回避）。下記の合意内容・書き込み結果・既存正本（照合用抜粋）のみを根拠に判断してください。

---

## 1. 合意内容（利用者承認済みの確定事項、決定箇条書きのみ）

- **(A) 適用範囲**：ワークフロー段（drafting → triad-review → review-wave → alignment → approval）の外側にある正本文書
- **(B-1) 検証者**：複数体並列、既定 3 体、Anthropic ／ OpenAI ／ Google の独立系統、yaml 可変。**既定モデル識別子は実験ノート §2.1（7 モデル比較実験で実証済み）由来：claude-sonnet-4-6（Anthropic）／ gpt-5.5（OpenAI）／ gemini-3.1-pro-preview（Google）**。**small=1 体の既定は Google `gemini-3.5-flash`**（起草者系統＝ Anthropic と原理的に独立、同モデル衝突を予防）
- **(B-2) 情報提供**：合意内容と書き込み結果のみ渡す。起草者の解釈・判断理由・議論ログは渡さない
- **(D) 失敗時挙動**：1 件でも検出があれば一律阻止
- **(E) 規律所在**：新規律ファイル＋計画書 §5.8 補助層 D の両方
- **過去遡及**：遡及しない、再オープン手続きで都度修正
- **絞り込み**：ワークフロー段の外側に限定（多層防御の役割分担、ワークフロー段で検証される仕様文書・レビュー記録は対象外）
- **規模制御**：小規模＝ 1 体／大規模＝ 3 体、判定迷いは大規模側。**small=1 体も独立系統必須**（起草者系統と異なるモデルを使う）
- **改訂手続き**：**本規律成立後の改訂時**は改訂前規律に従う＋**影響評価を実施**（影響評価結果を改訂記録に残す）。破壊的変更は利用者明示承認必須
- **フォールバック方針**：独立系統が利用できない場合は**書き込みを fail-closed で阻止し、人間エスカレーション**（§5.13 通知機構経由）。同一系統内代替は既定で認めない（独立性要件を保持）。利用者明示承認時のみ例外的に代替可
- **実装段階**：補助層 C と同構造の 3 段（段階 1 ＝ LLM 自律／段階 2 ＝書き込み後フック（フェーズ 4 第 2 サイクル以降）／段階 3 ＝ Git/IDE フックによる commit/push 時の機械的な検証起動と阻止）
- **検査観点**：4 項目（agreement_reflection／reference_accuracy／existing_record_consistency／internal_logic）
- **再検証ループ**：起草者と検証者間の自律的な差し戻し修正ループ（ループ中は LLM 同士で完結、人間関与なし）。上限超過時のみ人間エスカレーション（§5.13 通知機構経由）
- **自己適用ブートストラップ例外**：本規律自身の初回起草は本規律成立前のため対象外、代わりに独立系統（OpenAI／Google）での検証を発効条件とする
- **適用範囲の精緻化**：`docs/reviews/` は監査記録 `*-audit-*.md` と再オープン記録 `reopen-classification-*.md` のみ。プロジェクト直下は `TODO_NEXT_SESSION.md` のみ。仕様文書・レビュー記録は `.reviewcompass/specs/` 全体を除外（ワークフロー段で検証）
- **YAML 参照表記**：`reviewcompass.yaml#review.post_write_verification`（草案 3 yaml が `review:` 配下に置かれる構成と整合）
- **§5.8 構造整合**：補助層 D は既存の補助層 A/B/C 箇条書きにも D 項目として追加し（操作 A-1）、加えて独立小節（操作 A-2）も新設する（A/B/C と同じ箇条書き形式での追加＋独立小節の両立）
- **更新 D の引用符**：§5.9.6 (d) の正本は一重カギカッコ「...」を使用（機械的置換時の文字列一致のため重要）

---

## 2. 書き込み結果（草案 1〜3、再々々版＝修正版）

### 2.1 草案 1：新規律ファイル `docs/disciplines/discipline_post_write_verification.md`

````markdown
---
name: post-write-verification
description: ワークフロー段の外側にある正本文書への書き込み後、起草者と異なるサブエージェントによる独立検証を必須化（既定 3 体、独立系統）。1 件でも検出があれば一律阻止（2026-05-31 セッション 41 新設）
metadata:
  type: feedback
---

ワークフロー段（drafting → triad-review → review-wave → alignment → approval）の外側にある正本文書への書き込み後、書いた本人とは別のサブエージェントによる独立検証を必ず実施する。1 件でも検出があれば書き込みを差し戻し、修正してから再検証する。

**適用範囲：**

- 対象：`docs/plan/` ／ `docs/disciplines/` ／ `docs/operations/` ／ `docs/notes/` ／ `docs/experiments/`（各ディレクトリ全体）／ `docs/reviews/`（**監査記録 `*-audit-*.md` と再オープン記録 `reopen-classification-*.md` のみ**、yaml の `include_dirs_conditional` 参照）／プロジェクト直下では `TODO_NEXT_SESSION.md`（yaml の `include_root_files` 参照）
- 対象外：`.reviewcompass/specs/`（ワークフロー段で検証）、spec.json 状態変更（補助層 C [[workflow-precheck-invocation]] で検証）、`docs/archive/`、テスト用一時ファイル
- 新規ディレクトリ：判定に迷えば対象側に倒す

**検証者の要件：**

- 独立性：起草者と異なるモデル
- 複数体並列：大規模時は既定 3 体、Anthropic ／ OpenAI ／ Google の独立系統（**既定モデル識別子は実験ノート §2.1 由来：`claude-sonnet-4-6` ／ `gpt-5.5` ／ `gemini-3.1-pro-preview`**、`reviewcompass.yaml#review.post_write_verification.verifiers` で可変）
- small 時は 1 体、**既定は Google `gemini-3.5-flash`（起草者系統＝ Anthropic と原理的に独立、yaml の `small_verifier` で可変）**。small=1 体でも**起草者系統と異なる独立系統を必ず使う**（同モデル衝突を予防、利用者判断 2026-05-31 セッション 41）
- 情報最小化：合意内容（決定事項の箇条書きのみ、判断理由文を含まない）と書き込み結果のみ渡す。起草者の解釈・判断理由・議論ログは渡さない（枠組み伝染バイアス回避、§5.9.6 (d) と同思想——同節「起草後に別モデルへ点検依頼」は当該節時点では案として記載だったが、本規律で**確定化**）
- フォールバック：独立系統が利用できない環境では**書き込みを fail-closed で阻止し、人間エスカレーション**（§5.13 通知機構経由）。同一系統内代替は既定では認めない（独立性要件を保持）。利用者が個別事案ごとに明示承認した場合に限り例外的に代替可（記録に残す）

**発火規模制御：**

- 小規模（既存節への 1〜2 行追記・字句修正・既存リスト項目追加）：1 体検証
- 大規模（新節起草・構造変更・複数節改訂）：3 体検証
- 判定に迷えば大規模側に倒す

**検査観点 4 項目（yaml の `inspection_criteria` と対応）：**

1. `agreement_reflection`：合意内容が書き込みに反映されているか
2. `reference_accuracy`：数値・出典・固有名詞が正本と一致するか
3. `existing_record_consistency`：既存記述との齟齬がないか
4. `internal_logic`：内部の論理矛盾がないか

**失敗時の挙動：**

- 検出があれば**深刻度問わず一律阻止**、コミットも含めて先に進めない
- 深刻度（高／中／低）は検証者の**報告フォーマット用途**であり、阻止判定には使わない（一律阻止）
- 再検証ループは `retry_policy.max_retries`（既定 5、起草者と検証者間の自律的な差し戻し修正ループを想定しているため、§5.9.7 の API リトライ既定値より大きく設定）まで、**ループ中は LLM 同士で自律完結し人間関与なし**。上限超過時のみ人間エスカレーション（§5.13 通知機構経由）

**実装段階（補助層 C §5.8 と同構造のフェーズ別スケジュール）：**

- **段階 1（フェーズ 1〜3、現状）**：LLM が自律的に書き込み完了を認識し、サブエージェントを呼び出して検証する。阻止は LLM 自律判断
- **段階 2（フェーズ 4 第 2 サイクル以降）**：書き込み後フックスクリプトによる機械的な検証起動と阻止
- **段階 3（スコープ外、将来）**：Git/IDE フックによる機械的な検証起動と阻止（commit／push 時のフックで未検証の書き込みを検出して差し戻す）

**自己適用（メタ適用）：**

- **本規律成立後の改訂時**は本規律を適用する。ただし**改訂前規律の設定**に従って検証者を起動する。初回起草については下記ブートストラップ例外参照
- 改訂時は**変更の影響評価を実施**する（既存設定の意味変化、新規必須項目の追加、依存関係の変化、過去成果物への波及等を点検し、影響評価結果を改訂記録に残す）
- 改訂内容に破壊的変更（既存設定の意味変化、新しい必須項目の追加等）がある場合は利用者明示承認必須（§0.2 計画書方針変更と同等の扱い）
- **初回起草のブートストラップ例外**：本規律自身および計画書 §5.8 補助層 D 新節・yaml 骨子の 2026-05-31 セッション 41 での初回起草は、本規律成立前のため対象外。代わりに**独立系統（OpenAI／Google）での検証を本規律の発効条件**とする（同セッション内の Anthropic 系統 2 回検証では独立性不十分。利用者判断 2026-05-31）

**過去成果物：**

- 遡及適用しない
- 過去分の誤りは再オープン手続き（§5.6）で発見の都度修正

**Why:** 2026-05-31 セッション 41 で計画書 §5.12.11 ／ §5.9.6 ／ §5.5 alignment の 3 件改訂で、いずれも独立検証で高深刻度の誤りが検出された。本規律自身の起草でも、既存規律フォーマット未準拠・草案間不整合・自己適用循環定義など 24 件（前回 12 ＋ 再検証 12）が独立検証で検出された。起草者の自己検証では捕まらない誤りが書き込み段階で系統的に混入することが実証されたため、書き込みを「合意内容の機械的清書」ではなく「書き込み＋独立検証」の不可分な単位として扱う。費用対効果と体験への配慮から、ワークフロー段で検証される文書は対象外（多層防御の役割分担）。

**How to apply:**

- 対象文書の書き込み完了を起点に `reviewcompass.yaml#review.post_write_verification` 設定で検証者を起動（段階別に手段が異なる、上記実装段階節）
- 書き込み規模を判定（`scale_classification`、判定不能なら large）
- 検証者には合意内容（決定箇条書きのみ）と書き込み結果のみ渡す（`information_policy`）
- 検査観点 4 項目で評価、深刻度を報告フォーマットとして使用
- 1 件でも検出があれば `fail_action: block_all` で阻止、起草者が修正、再検証
- 再検証ループは上限まで、超過は人間エスカレーション

**関連規律：**

- 計画書 §5.8 補助層 D（多層防御の整理として並列記述）
- 計画書 §5.9.6 (d)（同思想、本規律で「案」から「確定」へ昇格）
- [[facts-vs-interpretation]]（書き込み前の機械的照合と相補的）
- [[workflow-precheck-invocation]]（補助層 C、spec.json 状態変更の事前検査と相補的）
````

### 2.2 草案 2：計画書への 4 か所更新

#### 更新 A：§5.8 補助層 D の追加（2 つの編集操作に分解、構造整合性確保）

##### 操作 A-1：既存の補助層リスト（行 737 配下の箇条書き、A／B／C と並ぶ箇所）に **D の箇条書き項目を追加**

挿入位置：補助層 C の箇条書き（行 746〜756 付近）の直後、補助層リストの末尾

```
- 補助層 D：書き込み後の独立検証（2026-05-31 セッション 41 新設、本節 §5.8 補助層 D 節の独立小節を参照）
  - ワークフロー段の外側にある正本文書への書き込み後、書いた本人とは別のサブエージェント（既定 3 体、Anthropic ／ OpenAI ／ Google の独立系統）による独立検証を必ず実施
  - 小規模時は 1 体、起草者系統と異なる独立系統を必須（既定 Google `gemini-3.5-flash`）。同モデル衝突を予防
  - 1 件でも検出があれば書き込みを差し戻す、深刻度問わず一律阻止
  - 詳細は本節下の独立小節および規律ファイル docs/disciplines/discipline_post_write_verification.md を参照
```

##### 操作 A-2：§5.8 補助層 D 独立小節を新設（補助層 C 節の後に追加）

挿入位置：§5.8 の補助層 C 節（段階 3 等の小節を含む）の後、`#### 5.8 補助層 D：...` という新しい見出しレベルで

```
#### 5.8 補助層 D：書き込み後の独立検証（2026-05-31 セッション 41 新設）

ワークフロー段（drafting → triad-review → review-wave → alignment → approval）の外側にある正本文書（docs/plan/, docs/disciplines/, docs/operations/, docs/notes/, docs/experiments/ の各全体／ docs/reviews/ は監査記録 `*-audit-*.md` と再オープン記録 `reopen-classification-*.md` のみ／プロジェクト直下では TODO_NEXT_SESSION.md）への書き込みが終わったら、書いた本人とは別のサブエージェント（既定 3 体、Anthropic ／ OpenAI ／ Google の独立系統）による独立検証を必ず実施する。1 件でも検出があれば書き込みを差し戻す。ワークフロー段で検証される仕様文書・レビュー記録（`.reviewcompass/specs/`）は対象外（多層防御の役割分担）。

**書き込み規模制御**：書き込み規模に応じて検証者数を可変。**大規模＝ 3 体**（既定モデル識別子は実験ノート §2.1 由来：claude-sonnet-4-6 ／ gpt-5.5 ／ gemini-3.1-pro-preview）。**小規模＝ 1 体**、起草者系統と異なる独立系統を必須とし、既定は Google `gemini-3.5-flash`（起草者系統＝ Anthropic と原理的に独立、同モデル衝突を予防）。

実装段階は補助層 C と同構造の 3 段（段階 1 ＝ LLM 自律、段階 2 ＝書き込み後フック、段階 3 ＝ Git/IDE フック）。現状は段階 1、段階 2 はフェーズ 4 第 2 サイクル以降の実装宿題。

規律本体は規律ファイル docs/disciplines/discipline_post_write_verification.md、yaml 設定は reviewcompass.yaml#review.post_write_verification を参照。
```

#### 更新 B：§5.8 既存記述 3 箇所の整合更新（具体文言）

- **行 735**：「補助層（本セッション後半で追加、§5.12・§5.13、2026-05-25 セッション 24 で補助層 C 追加）」
  → **更新後**：「補助層（本セッション後半で追加、§5.12・§5.13、2026-05-25 セッション 24 で補助層 C 追加、**2026-05-31 セッション 41 で補助層 D 追加**）」

- **行 737（冒頭文）**：「第 1 層と第 2 層の間に、人間関与の頻度・即時性を調整し、処理開始時の逸脱予防を担う補助層を追加：」
  → **更新後**：「第 1 層と第 2 層の間に、人間関与の頻度・即時性を調整し、処理開始時の逸脱予防**および書き込み後の独立検証**を担う補助層を追加：」（既存の動詞構造「〜を調整し」を維持）

- **行 757**：2 つの独立した編集操作に分解：
  - **操作 1（文字列置換）**：「補助層 A／B／**C** は第 1 層と第 2 層の中間に位置し」 → 「補助層 A／B／C／**D** は第 1 層と第 2 層の中間に位置し」
  - **操作 2（末尾追加）**：行末「補助層 C は処理開始時の事前検査で規律遵守を構造的に強化する。」の直後に新文を追加：「**補助層 D は書き込み後の独立検証で規律遵守をさらに強化する**。」

#### 更新 C：§5.12.8 多層防御リストに補助層 D を追加

§5.12.8 のリストの**補助層 C の直後、第 2 層の直前**に追加：

```
- 補助層 D：書き込み後の独立検証（§5.8 補助層 D 節、2026-05-31 セッション 41 新設）
```

#### 更新 D：§5.9.6 (d) の「案」を「確定」に昇格

**正本の引用符は一重カギカッコ「...」**（機械的置換時の文字列一致のため重要）：

- **既存（置換対象、正本どおりの引用符表記）**：「加えて「起草後に別モデルへ点検を依頼する」案が検討中（実験ノート §3.4.2、現状は案として記載）」
- **更新後（強調表記なし、既存 (a)〜(e) 体裁と統一）**：「加えて「起草後に別モデルへ点検を依頼する」（実験ノート §3.4.2 の案）は 2026-05-31 セッション 41 で確定化（規律 docs/disciplines/discipline_post_write_verification.md、計画書 §5.8 補助層 D を参照）」

実験ノート §3.4.2 への参照は「(d) の案の出典」として維持。モデル識別子の由来（実験ノート §2.1）とは文脈が異なる点に注意。

### 2.3 草案 3：`reviewcompass.yaml` の節骨子

```yaml
# 参照表記：reviewcompass.yaml#review.post_write_verification
review:
  post_write_verification:
    enabled: true
    reference_discipline: docs/disciplines/discipline_post_write_verification.md
    reference_plan_section: "計画書 §5.8 補助層 D"

    scope:
      include_dirs:
        - docs/plan/
        - docs/disciplines/
        - docs/operations/
        - docs/notes/
        - docs/experiments/
      include_dirs_conditional:
        docs/reviews/:
          include_patterns:
            - "*-audit-*.md"
            - "reopen-classification-*.md"
          exclude_note: "ワークフロー段で検証される機能別レビュー記録（.reviewcompass/specs/*/reviews/）は別途 exclude_dirs で除外済み"
      include_root_files: [TODO_NEXT_SESSION.md]
      exclude_dirs:
        - .reviewcompass/specs/
        - docs/archive/
      principle: "ワークフロー段の外側にある正本文書が対象。判定に迷えば対象側に倒す"

    trigger:
      on: file_write_to_scoped_path
      detection_stage_1: llm_self_invocation
      detection_stage_2: post_edit_hook_script      # 段階2（フェーズ4第2サイクル以降）：書き込み後フックスクリプト
      detection_stage_3: git_or_ide_hook            # 段階3（将来）：commit/push 時の機械的な検証起動と阻止

    scale_classification:
      small_criteria: [既存節への1-2行追記, 字句修正・誤字訂正, 既存リスト項目の追加]
      large_criteria: [新節の起草, 構造変更（節の並べ替え・分割）, 複数節にまたがる改訂]
      default_on_ambiguous: large

    scale_based_verifier_count: {small: 1, large: 3}

    verifiers:
      - {provider: anthropic-api, model: claude-sonnet-4-6}      # 実験ノート §2.1
      - {provider: openai-api,    model: gpt-5.5}                # 実験ノート §2.1
      - {provider: google-api,    model: gemini-3.1-pro-preview} # 実験ノート §2.1
    small_verifier: {provider: google-api, model: gemini-3.5-flash}  # 起草者系統(Anthropic)と独立、同モデル衝突を予防

    on_unavailable:
      policy: fail_closed_and_escalate_via_5_13      # 書き込みを fail-closed で阻止 ＋ §5.13 経由エスカレーション（fail_closed は書き込み自体を未完了に戻す、on_max_exceeded とは異なる）
      same_provider_fallback_requires_explicit_approval: true
      record_when_fallback_used: true

    information_policy:
      pass_agreement: true
      pass_agreement_format: "decisions_only_no_reasoning"
      pass_writeup: true
      pass_reasoning: false
      pass_discussion_log: false

    inspection_criteria:
      - agreement_reflection
      - reference_accuracy
      - existing_record_consistency
      - internal_logic

    severity_definition:
      _note: "block_all により深刻度問わず一律阻止。本定義は検証者の報告フォーマット用途のみ"
      high: 設計の核心・出典・数値の誤り、配置の根本問題
      medium: 表現の曖昧・接合の不明瞭
      low: 表記揺れ・体裁の不統一

    fail_action: block_all

    retry_policy:
      max_retries: 5                                 # 起草者と検証者間の自律ループ（ループ中は LLM 同士で完結、人間関与なし）
      on_max_exceeded: escalate_to_human_via_5_13   # 上限超過時のみ §5.13 経由でエスカレーション（on_unavailable.policy と表記統一）
```

---

## 3. 既存正本（照合用、抜粋）

### 3.1 既存規律ファイルのフォーマット（discipline_facts_vs_interpretation.md 全文）

````markdown
---
name: facts-vs-interpretation
description: 達成基準を事前宣言、編集後は機械的（grep／Read）照合、事実と解釈を別個に示し出典に辿れる形に（旧 3 規律統合：check-logs-and-git／separate-facts-from-interpretation／completion-verification-protocol、2026-05-25 セッション 24 統廃合）
metadata:
  type: feedback
---

事実は記憶でなく出典（ファイル行・コミット・ログ）で確認し、解釈と明示的に分けて示す。

**達成基準と検証のプロトコル：**

- 指示を受けたら冒頭で達成基準を箇条書きで宣言
- 編集後は grep／Read で機械的に照合し、出典を残す
- 報告の中心は「やったこと」でなく「達成基準と現状の照合結果」
- 完了承認後は基準を満たすまで作業継続

**事実と解釈の区別：**

- 完了・適合・GO を断定せず、検証可能な証拠と「満たした／満たさない」で示す
- 主張・報告は必ず出典（ファイル行・コミット）に辿れる形にする

**Why:** 旧 3 規律（check-logs-and-git／completion-verification-protocol／separate-facts-from-interpretation）を統合（2026-05-25 セッション 24）。事実根拠と機械的確認と解釈の分離は密接に関連する一連の規律で、一体運用が自然。

**How to apply:**

- 指示を受けたら冒頭で「達成基準の宣言」節を出力
- 編集後に grep／Read の出力を引用して「達成基準 N が満たされている」を機械的に証明
- 報告は「やったこと」ではなく「達成基準 N → 検証結果」の形式
- 機械化の一部は段階 2 スクリプト（[[workflow-precheck-invocation]]）が代行するが、宣言と報告の構造は LLM の責務
````

### 3.2 計画書 §5.8 多層防御の既存記述（補助層 A／B／C 節、行 735〜757）

```
#### 補助層（本セッション後半で追加、§5.12・§5.13、2026-05-25 セッション 24 で補助層 C 追加）

第 1 層と第 2 層の間に、人間関与の頻度・即時性を調整し、処理開始時の逸脱予防を担う補助層を追加：

- 補助層 A：人間代役機構（§5.12）
  - 軽い判断を外部モデルが代行、本人関与の頻度を下げる
  - マルチターン対話で文脈を踏まえた判断
  - 不可逆操作・承認系・CRITICAL／ERROR は代行不可、本人エスカレーション
- 補助層 B：人間への通知機構（§5.13）
  - 本人判断が必要な場面で外部チャネル（メール・LINE 等）に即時通知
- 補助層 C：処理開始時のワークフロー事前検査（共存モデル、2026-05-25 セッション 24 採用承認）
  - 処理が呼ばれる時点で、その処理が現在のワークフロー手順に適合するかを事前検査
  - 3 段階の役割分担（段階 1 ＝ LLM 規律／段階 2 ＝外部スクリプト／段階 3 ＝ Claude Code フック）

補助層 A／B／C は第 1 層と第 2 層の中間に位置し、本人関与の調整と逸脱予防の層として動く。補助層 A・B は相補的（代役で頻度を下げ、通知で即時性を確保）、補助層 C は処理開始時の事前検査で規律遵守を構造的に強化する。
```

### 3.3 計画書 §5.12.8 多層防御リスト（行 1718〜1729）

```
#### 5.12.8 多層防御との関係

§5.8 の多層防御に 補助層 A として位置付ける：

- 第 1 層：軽量版 YAML 検査機構（既存）
- 補助層 A：人間代役機構（軽い判断を代行、本人関与を減らす、本節 §5.12）
- 補助層 B：人間への通知機構（§5.13）
- 補助層 C：処理開始時のワークフロー事前検査（共存モデル、§5.8 補助層 C 節、2026-05-25 セッション 24 採用）
- 第 2 層：git フック（スコープ外）
- 第 3 層：フェーズ境目の利用者監査（既存）
- 第 4 層：定期事後監査（スコープ外）
- 第 5 層：処理表面積の抑制方針（既存）
```

### 3.4 計画書 §5.9.6 (d) 枠組み伝染バイアス対策（行 1037〜1047、正本テキスト、**引用符は一重カギカッコ「...」**）

```
マルチターン対話とプロンプト設計の規律（正本、2026-05-31 セッション 41 で実験ノート §3.4 から格上げ）：

判定者へ投げる問題文の設計と、判定者が質問返しをしたときの対応の規律。

- (a) 質問返し時の代理回答：判定者が 1 ターン目で判定せず聞き返した場合、コンシェルジュ（メインセッション）が文脈を補う代理回答を返し、最大 5 ターンまで対話を続ける
- (b) 集計の両軸 2 表：1 ターン目応答の分布と最終判定の分布を別個に集計する
- (c) プロンプト設計の二律背反：バイアスをかけない（採用案を結論的に示さない、他所見の決定を見せない）と、必要な情報を供与する（事実・数値・ファイルパス・行番号・引用は完全に書く）のバランスを取る
- (d) 枠組み伝染バイアス対策：問題文起草者の枠組み・結論がレビューモデル群に伝染する現象への対策——深掘り欄に現所見への判定語（合う／不自然／誤記など）を書かない、両面に切れる事実を対称に併記する、前提を疑う別案を歓迎する。加えて「起草後に別モデルへ点検を依頼する」案が検討中（実験ノート §3.4.2、現状は案として記載）
- (e) 起草後の自己検査チェックリスト 9 項目で、上記が守られているか機械的に点検する（実験ノート §3.4.2）
```

---

## 4. 検査観点（4 項目）

各観点で問題がないかを判定し、問題があれば指摘してください：

1. **agreement_reflection**：合意内容（上記第 1 節）が書き込み（上記第 2 節）に正しく反映されているか
2. **reference_accuracy**：書き込み内の数値・出典・固有名詞（§番号・ファイルパス・行番号・モデル識別子等）が既存正本（上記第 3 節）と一致するか
3. **existing_record_consistency**：書き込みが既存正本との齟齬を生まないか（特に §5.8 補助層 A/B/C の既存記述、§5.12.8 多層防御リスト、§5.9.6 (d) との接合、引用符の一致）
4. **internal_logic**：3 草案間および草案内で論理矛盾がないか（特に自己適用ブートストラップ例外、再検証ループ、独立系統必須と small=1 体の整合、適用範囲の 3 草案間整合等）

---

## 5. 出力形式

下記の YAML 形式で返してください。コードブロックは不要、YAML 本体のみを出力してください。

```yaml
verifier_id: <あなた自身を一意に識別する文字列、例：openai-gpt-5.5>
findings:
  - severity: high  # high / medium / low
    criteria: agreement_reflection  # agreement_reflection / reference_accuracy / existing_record_consistency / internal_logic
    target_draft: 1  # 1 / 2 / 3
    target_location: "具体的な箇所（節名・行範囲・記述抜粋）"
    issue: "問題の説明"
    recommendation: "推奨修正"
verdict: BLOCK  # ALL_CLEAR / BLOCK
summary: "全体所見を 1〜2 文で"
```

**指示：**

- 検出がない観点は findings に含めず、verdict: ALL_CLEAR としてください
- 1 件でも検出があれば verdict: BLOCK としてください
- 推測や勘で粗探しをせず、上記第 1〜3 節の情報から明らかに判定できる問題のみを指摘してください
- 「設計判断の妥当性」（合意内容として既に確定済み）は検証対象外。あくまで「反映の正確性」「正本との整合」「内部矛盾」を見てください
- 各指摘は target_location で具体箇所を特定できる形で書いてください
