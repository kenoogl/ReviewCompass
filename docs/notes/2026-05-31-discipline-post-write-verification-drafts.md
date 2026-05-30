# post-write-verification 規律：独立系統検証待ち草案

作成：2026-05-31（セッション 41）
状態：**独立系統（OpenAI／Google）での検証完了まで確定保留**

## 0. 本ファイルの位置づけ

本ファイルは新規律「書き込み後の独立検証（post-write-verification）」の草案 3 種を、独立系統での検証完了までの仮置き場として保存するもの。本規律自身が「自分の起草も書き込み後検証必須」と定めるため、独立系統での検証なしに正式位置（`docs/disciplines/` ／計画書 §5.8）へ書き込むことは規律の精神を破る（2026-05-31 セッション 41 利用者判断、可能性 C「ブートストラップ例外を撤回・狭隘化＋独立系統必須」を採用）。

## 1. 経緯と本セッション内での独立検証の履歴

- 2026-05-31 セッション 41 にて本規律の必要性が議論され、論点 A〜E の 6 論点が確定（議論ログ `2026-05-30-section-5-12-revision-log.md` 参照）
- 本セッション内で 2 回の独立検証を実施：
  1. 初回（Anthropic Sonnet）：12 件指摘 → 修正
  2. 2 回目（Anthropic Sonnet が GPT-5.5 視点を代行）：12 件指摘 → 修正
- 利用者判断：いずれも Anthropic 系統で、本規律が定める「独立 3 系統」を満たさない。**独立系統（OpenAI／Google）での検証が必須**

## 2. 次セッションでの実施事項

1. 既存の実験基盤（`tools/experiments/_experiment_n_model.py` 等、OpenAI／Anthropic／Google の独立 3 系統呼び出し済み）を流用して、本ファイルの 3 草案を独立系統で検証
2. 検査観点 4 項目（agreement_reflection／reference_accuracy／existing_record_consistency／internal_logic）で評価
3. 1 件でも検出があれば修正、再検証
4. 全検証者から「齟齬なし」が返ったら、正式位置（規律ファイル新設＋計画書 §5.8 補助層 D 追加＋ §5.12.8 リスト更新＋ §5.9.6 (d) 更新）に書き込み・コミット
5. 本ファイルは正式書き込み完了後、`docs/notes/archive/` 配下に移動（履歴保全）

## 3. 確定事項（決定 1〜6、議論ログから抜粋）

| 論点 | 確定 |
|---|---|
| A 適用範囲 | ワークフロー段の外側にある正本文書 |
| B-1 検証者人数 | 複数体並列、既定 3 体、Anthropic ／ OpenAI ／ Google の独立系統、yaml 可変 |
| B-2 情報提供 | 合意内容（決定事項の箇条書きのみ）と書き込み結果のみ。判断理由・議論ログは渡さない |
| D 失敗時挙動 | 1 件でも検出があれば一律阻止 |
| E 規律所在 | 新規律ファイル＋計画書 §5.8 補助層 D の両方 |
| 過去遡及 | 遡及しない、再オープンで都度修正 |
| 追加 1（絞り込み） | ワークフロー段の外側に限定（多層防御の役割分担） |
| 追加 2（規模制御） | 小規模＝1 体／大規模＝3 体 |
| 追加 3（改訂手続き） | 改訂前規律に従う＋影響評価。破壊的変更は利用者明示承認必須 |
| 追加 4（実装段階） | 段階 1（LLM 自律）／段階 2（書き込み後フック）／段階 3（Git/IDE フック）の 3 段 |

---

## 4. 草案 1（再々版）：新規律ファイル `docs/disciplines/discipline_post_write_verification.md`

````markdown
---
name: post-write-verification
description: ワークフロー段の外側にある正本文書への書き込み後、起草者と異なるサブエージェントによる独立検証を必須化（既定 3 体、独立系統）。1 件でも検出があれば一律阻止（2026-05-31 セッション 41 新設）
metadata:
  type: feedback
---

ワークフロー段（drafting → triad-review → review-wave → alignment → approval）の外側にある正本文書への書き込み後、書いた本人とは別のサブエージェントによる独立検証を必ず実施する。1 件でも検出があれば書き込みを差し戻し、修正してから再検証する。

**適用範囲：**

- 対象：`docs/plan/` ／ `docs/disciplines/` ／ `docs/operations/` ／ `docs/notes/` ／ `docs/experiments/` ／ `docs/reviews/` ／プロジェクト直下の主要 `.md`（`TODO_NEXT_SESSION.md` 等）
- 対象外：`.reviewcompass/specs/`（ワークフロー段で検証）、spec.json 状態変更（補助層 C [[workflow-precheck-invocation]] で検証）、`docs/archive/`、テスト用一時ファイル
- 新規ディレクトリ：判定に迷えば対象側に倒す

**検証者の要件：**

- 独立性：起草者と異なるモデル
- 複数体並列：既定 3 体、Anthropic ／ OpenAI ／ Google の独立系統（`reviewcompass.yaml#post_write_verification.verifiers` で可変）
- small 時は 1 体、既定は Anthropic `claude-sonnet-4-6`（yaml の `small_verifier` で可変）
- 情報最小化：合意内容（決定事項の箇条書きのみ、判断理由文を含まない）と書き込み結果のみ渡す。起草者の解釈・判断理由・議論ログは渡さない（枠組み伝染バイアス回避、§5.9.6 (d) と同思想——同節「起草後に別モデルへ点検依頼」は当該節時点では案として記載だったが、本規律で**確定化**）
- フォールバック：独立系統が利用できない環境では yaml の `on_unavailable` 設定に従う（既定：同一系統内の別モデルで代替、その旨を記録に残す）

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
- 再検証ループは `retry_policy.max_retries`（既定 5、§5.9.7 のリトライ既定 3 より大きいのは「人間との対話を伴う差し戻し」のため）まで、超過は人間エスカレーション（§5.13 通知機構経由）

**実装段階（補助層 C §5.8 と同構造のフェーズ別スケジュール）：**

- **段階 1（フェーズ 1〜3、現状）**：LLM が自律的に書き込み完了を認識し、サブエージェントを呼び出して検証する。阻止は LLM 自律判断
- **段階 2（フェーズ 4 第 2 サイクル以降）**：書き込み後フックスクリプトによる機械的な検証起動と阻止
- **段階 3（スコープ外、将来）**：Git/IDE フックによる書き込み直前阻止

**自己適用（メタ適用）：**

- 本規律の**改訂時**は本規律を適用する。ただし**改訂前規律の設定**に従って検証者を起動する（保守的、改訂中の規律で改訂前を検証する循環を避ける）
- 改訂内容に破壊的変更（既存設定の意味変化、新しい必須項目の追加等）がある場合は利用者明示承認必須（§0.2 計画書方針変更と同等の扱い）
- **初回起草のブートストラップ例外**：本規律自身および草案 2（§5.8 補助層 D 新節）・草案 3（yaml 骨子）の 2026-05-31 セッション 41 での初回起草は、本規律成立前のため対象外。代わりに**独立系統（OpenAI／Google）での検証を本規律の発効条件**とする（同セッション内の Anthropic 系統 2 回検証では独立性不十分。利用者判断 2026-05-31）

**過去成果物：**

- 遡及適用しない
- 過去分の誤りは再オープン手続き（§5.6）で発見の都度修正

**Why:** 2026-05-31 セッション 41 で計画書 §5.12.11 ／ §5.9.6 ／ §5.5 alignment の 3 件改訂で、いずれも独立検証で高深刻度の誤りが検出された。本規律自身の起草でも、既存規律フォーマット未準拠・草案間不整合・自己適用循環定義など 24 件（前回 12 ＋ 再検証 12）が独立検証で検出された。起草者の自己検証では捕まらない誤りが書き込み段階で系統的に混入することが実証されたため、書き込みを「合意内容の機械的清書」ではなく「書き込み＋独立検証」の不可分な単位として扱う。費用対効果と体験への配慮から、ワークフロー段で検証される文書は対象外（多層防御の役割分担）。

**How to apply:**

- 対象文書の書き込み完了を起点に `reviewcompass.yaml#post_write_verification` 設定で検証者を起動（段階別に手段が異なる、上記実装段階節）
- 書き込み規模を判定（`scale_classification`、判定不能なら large）
- 検証者には合意内容（決定箇条書きのみ）と書き込み結果のみ渡す（`information_policy`）
- 検査観点 4 項目で評価、深刻度を報告フォーマットとして使用
- 1 件でも検出があれば `fail_action: block_all` で阻止、起草者が修正、再検証
- 再検証ループは上限まで、超過は人間エスカレーション

**関連規律：**

- 計画書 §5.8 補助層 D（草案 2 で新設予定）
- 計画書 §5.9.6 (d)（同思想、本規律で「案」から「確定」へ昇格——草案 2 で §5.9.6 (d) を同期更新）
- [[facts-vs-interpretation]]（書き込み前の機械的照合と相補的）
- [[workflow-precheck-invocation]]（補助層 C、spec.json 状態変更の事前検査と相補的）
````

## 5. 草案 2（再々版）：計画書への 4 か所更新

### 更新 A：§5.8 補助層 D 新節を追加（新規）

挿入位置：§5.8 の補助層 C 節の後

```
#### 5.8 補助層 D：書き込み後の独立検証（2026-05-31 セッション 41 新設）

ワークフロー段（drafting → triad-review → review-wave → alignment → approval）の外側にある正本文書（docs/plan/, docs/disciplines/, docs/operations/, docs/notes/, docs/experiments/, docs/reviews/, プロジェクト直下の主要 .md）への書き込みが終わったら、書いた本人とは別のサブエージェント（既定 3 体、Anthropic ／ OpenAI ／ Google の独立系統）による独立検証を必ず実施する。1 件でも検出があれば書き込みを差し戻す。ワークフロー段で検証される仕様文書・レビュー記録は対象外（多層防御の役割分担）。

実装段階は補助層 C と同構造の 3 段（段階 1＝LLM 自律、段階 2＝書き込み後フック、段階 3＝Git/IDE フック）。現状は段階 1、段階 2 はフェーズ 4 第 2 サイクル以降の実装宿題。

書き込み規模に応じて検証者数を可変（小規模＝1 体、大規模＝3 体）。規律本体は規律ファイル [docs/disciplines/discipline_post_write_verification.md](../disciplines/discipline_post_write_verification.md)、yaml 設定は `reviewcompass.yaml#post_write_verification` を参照。
```

### 更新 B：§5.8 既存記述 2 箇所の整合更新（具体文言）

- **行 735**：「補助層（本セッション後半で追加、§5.12・§5.13、2026-05-25 セッション 24 で補助層 C 追加）」
  → 「補助層（本セッション後半で追加、§5.12・§5.13、2026-05-25 セッション 24 で補助層 C 追加、**2026-05-31 セッション 41 で補助層 D 追加**）」
- **行 757**：「補助層 A／B／**C** は第 1 層と第 2 層の中間に位置し……補助層 C は処理開始時の事前検査で規律遵守を構造的に強化する。」
  → 「補助層 A／B／C／**D** は第 1 層と第 2 層の中間に位置し……補助層 C は処理開始時の事前検査、**補助層 D は書き込み後の独立検証で規律遵守を構造的に強化する**。」

### 更新 C：§5.12.8 多層防御リストに補助層 D を追加

§5.12.8 のリスト末尾 補助層 C の次に追加：

```
- 補助層 D：書き込み後の独立検証（§5.8 補助層 D 節、2026-05-31 セッション 41 新設）
```

### 更新 D：§5.9.6 (d) の「案」を「確定」に昇格

§5.9.6 (d) 内の「加えて『起草後に別モデルへ点検を依頼する』案が検討中（実験ノート §3.4.2、現状は案として記載）」
→ 「加えて『起草後に別モデルへ点検を依頼する』は **2026-05-31 セッション 41 で確定化**（規律 [docs/disciplines/discipline_post_write_verification.md](../disciplines/discipline_post_write_verification.md)、計画書 §5.8 補助層 D を参照）」

## 6. 草案 3（再々版）：`reviewcompass.yaml` の節骨子

```yaml
review:
  post_write_verification:
    enabled: true
    reference_discipline: docs/disciplines/discipline_post_write_verification.md
    reference_plan_section: "計画書 §5.8 補助層 D"

    scope:
      include_dirs: [docs/plan/, docs/disciplines/, docs/operations/, docs/notes/, docs/experiments/, docs/reviews/]
      include_root_files: [TODO_NEXT_SESSION.md]
      exclude_dirs: [.reviewcompass/specs/, docs/archive/]
      principle: "ワークフロー段の外側にある正本文書が対象。判定に迷えば対象側に倒す"

    trigger:
      on: file_write_to_scoped_path
      detection_stage_1: llm_self_invocation        # 段階1（現状）：LLM 自律で検証を呼び出す
      detection_stage_2: post_edit_hook_script      # 段階2（フェーズ4以降）：書き込み後フックスクリプト
      detection_stage_3: git_or_ide_hook            # 段階3（将来）：Git/IDE フック

    scale_classification:
      small_criteria: [既存節への1-2行追記, 字句修正・誤字訂正, 既存リスト項目の追加]
      large_criteria: [新節の起草, 構造変更（節の並べ替え・分割）, 複数節にまたがる改訂]
      default_on_ambiguous: large

    scale_based_verifier_count: {small: 1, large: 3}

    verifiers:                                       # large 時の独立 3 系統
      - {provider: anthropic-api, model: claude-sonnet-4-6}
      - {provider: openai-api,    model: gpt-5.5}
      - {provider: google-api,    model: gemini-3.1-pro-preview}
    small_verifier: {provider: anthropic-api, model: claude-sonnet-4-6}

    on_unavailable:                                  # 系統が利用できない場合のフォールバック
      policy: fallback_to_same_provider              # 同一系統内の別モデルで代替
      record_fallback: true                          # 代替したことを記録に残す

    information_policy:
      pass_agreement: true                           # 決定事項の箇条書きのみ
      pass_agreement_format: "decisions_only_no_reasoning"  # 判断理由文を含まないフォーマット
      pass_writeup: true                             # 書き込み結果
      pass_reasoning: false                          # 起草者の解釈・判断理由は渡さない
      pass_discussion_log: false                     # 議論ログも渡さない

    inspection_criteria:                             # 規律本体の検査観点 4 項目と対応
      - agreement_reflection
      - reference_accuracy
      - existing_record_consistency
      - internal_logic

    severity_definition:                             # 報告フォーマット用途、阻止判定には使わない
      _note: "block_all により深刻度問わず一律阻止。本定義は検証者の報告フォーマット用途のみ"
      high: 設計の核心・出典・数値の誤り、配置の根本問題
      medium: 表現の曖昧・接合の不明瞭
      low: 表記揺れ・体裁の不統一

    fail_action: block_all                           # 深刻度問わず一律阻止

    retry_policy:
      max_retries: 5                                 # §5.9.7 のリトライ既定 3 より大きいのは人間との対話を伴う差し戻しのため
      on_max_exceeded: escalate_to_human_via_5_13   # §5.13 人間への通知機構経由でエスカレーション
```

---

## 7. 検証の実施手順（次セッション開始時）

既存実験基盤の流用：

1. 本ファイルの §3 確定事項を「合意内容」として整形
2. 本ファイルの §4／§5／§6 を「書き込み結果」として用意（実際は §5 の各更新文言を計画書の該当箇所に適用した想定差分）
3. `tools/experiments/_experiment_n_model.py` 等を流用して、Anthropic Sonnet ／ OpenAI GPT-5.5 ／ Google Gemini-3.1-pro-preview の 3 体に検査依頼
4. プロンプトは本セッション内 2 回の独立検証と同じ構造（合意内容＋書き込み結果＋検査観点 4 項目）。議論ログは渡さない
5. 1 件でも検出があれば修正、再検証
6. 全検証者から齟齬なしが返ったら、§4／§5 を正式位置に書き込み、コミット
7. 本ファイルを `docs/notes/archive/` に移動

## 8. 関連参照

- 議論ログ：[2026-05-30-section-5-12-revision-log.md](2026-05-30-section-5-12-revision-log.md)
- 本セッション 2 回の独立検証の指摘内容：本セッション transcript（後の `docs/sessions/session-41-2026-05-31.md` で参照可能）
- 既存実験基盤：`tools/experiments/_experiment_n_model.py` 等
- 既存規律フォーマット参考：`docs/disciplines/discipline_facts_vs_interpretation.md`
