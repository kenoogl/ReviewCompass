---
date: 2026-06-21
record_type: working-note
status: draft
topic: llm-boundary-and-postwrite-prompt-mechanization
related:
  - docs/notes/working/2026-06-21-workflow-operation-mechanization-improvement-plan.md
  - docs/notes/working/2026-06-21-effective-prompt-freshness-audit-plan.md
  - docs/notes/working/2026-06-20-api-review-prompt-audit-discussion-record.md
  - .reviewcompass/guidance/WORKFLOW_DISCIPLINE_MAP.yaml
  - .reviewcompass/guidance/WORKFLOW_NAVIGATION.md
  - .reviewcompass/guidance/discipline_post_write_verification.md
  - .reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md
---

# LLM 境界と Post-write Prompt 機械化計画

## 1. 目的

この計画は、workflow 実行で LLM に残す処理と、機械処理へ寄せる処理を明確に分離するためのもの。

今回の失敗では、`post_write_policy_violation` の地点から先で次の問題が起きた。

- 読むべき effective prompt を固定入力として扱い切れなかった
- post-write review に進んでよい地点かを十分に固定しなかった
- API に渡す prompt をその場で組み立てた
- review target の本文ではなく、パスと SHA だけを渡した
- prompt quality gate を API 実行前に機械的に通さなかった

この結果、API review-run の結果は有効なレビュー証跡として扱えないものになった。

以後は、LLM の判断力を使う箇所を review / judgment そのものに限定し、手順選択・材料選定・prompt 合成・実行可否判定は機械処理へ寄せる。

## 2. 基本原則

### 2.1 LLM 処理を残す場所

LLM 処理を残してよいのは、言語的判断が本質である箇所に限る。

- API reviewer が source / target / criteria を読み、finding を出す
- adversarial / judgment が prompt 品質やレビュー結果を判断する
- main LLM が機械出力を読み、利用者へ説明する
- main LLM が機械出力に基づき、許可された次操作を実行する

ただし、main LLM がその場で手順を合成してはいけない。実行できるのは、機械出力で許可された操作だけとする。

### 2.2 LLM 処理を残さない場所

次は LLM に委ねない。

- `next --json` の地点から読む effective prompt を決めること
- 複数の規律文書から effective prompt をその場で合成すること
- API review / proxy decision の対象ファイルを選ぶこと
- source bundle に入れる本文範囲を自由判断で決めること
- API に渡す prompt の骨格を自由作文すること
- prompt が送信可能かを目視判断だけで決めること
- review-run / proxy-run / commit / push などの実行可否を雰囲気で決めること

これらは、固定マップ、operation contract、source bundle builder、prompt template、prompt audit によって決定的に処理する。

## 3. 到達像

理想状態では、作業は次の順に進む。

1. `next --json` が唯一の workflow 地点を返す。
2. その地点に対応する canonical effective prompt を機械的に返す。
3. main LLM はその effective prompt を読むだけで、追加合成しない。
4. effective prompt が次に使う operation contract を指す。
5. operation contract が入力、出力、許可操作、停止条件を決める。
6. source bundle builder が対象本文を非要約で展開する。
7. prompt builder が固定テンプレートから API 用 prompt を生成する。
8. prompt audit が API 送信前に品質を機械検査する。
9. audit が通った場合だけ API review-run / proxy-run を実行する。
10. review / judgment の判断結果を main LLM が読み、許可された後処理へ進む。

この流れで LLM が担当するのは、6 までの選定・合成ではなく、9 以降のレビュー判断と説明である。

## 4. Post-write 系の優先対応

今回の直接原因は post-write 系なので、最初にここを固定する。

対象地点:

- `post_write_policy_violation`
- `post_write_verification`
- `post_write_human_decision_required`

特に `post_write_policy_violation` は、変更後に review へ進む前の安全停止地点である。この地点で API review prompt を作成してよいか、review-run へ進んでよいか、何を直すべきかを機械的に分ける必要がある。

## 5. Canonical Effective Prompt 計画

### 5.1 配置

各地点用の effective prompt は、runtime の一時生成物ではなく、canonical artifact として扱う。

候補配置:

```text
.reviewcompass/guidance/effective-prompts/
  next-action-post-write-policy-violation.prompt.md
  next-action-post-write-verification.prompt.md
  next-action-post-write-human-decision-required.prompt.md
```

配置名は実装前に既存の `.reviewcompass/runtime/effective-prompts/` との関係を確認して確定する。

### 5.2 `post_write_policy_violation` prompt に含める内容

この prompt は、次を固定本文として持つ。

- 現在地点の意味: post-write policy violation は review 実行地点ではなく、未検証変更の整理地点である
- 許可される作業: 状態確認、変更分類、必要証跡の計画、違反解消のための準備
- 禁止される作業: API review-run 実行、post-write manifest 作成、review 結果の確定扱い、commit
- 次に使う operation contract: `post_write_policy_violation.inspect`
- 出力契約: main LLM は「未検証変更の分類」「次に必要な機械処理」「停止条件」を報告する
- API prompt 生成へ進める条件: `next_action.kind == post_write_verification` に遷移していること

重要なのは、この内容をその場で `WORKFLOW_NAVIGATION.md` と `discipline_post_write_verification.md` から合成しないことである。

### 5.3 Freshness 監査との接続

canonical effective prompt は元文書から生成される派生物なので、元文書が変われば更新が必要になる。

そのため、`2026-06-21-effective-prompt-freshness-audit-plan.md` の監査対象に、canonical effective prompt を含める。

受入条件:

- source refs が現在の `WORKFLOW_DISCIPLINE_MAP.yaml` と一致する
- source SHA が現在の元文書と一致する
- 再生成結果と canonical prompt が一致する
- stale の場合は通常作業ではなく regeneration / audit action を返す

## 6. Operation Contract 計画

### 6.1 `post_write_policy_violation.inspect`

目的:

未検証変更を、review に進められる状態か、先に整理が必要な状態かへ機械的に分類する。

入力:

- `git status --short`
- `git diff --name-only`
- `next --json`
- `WORKFLOW_DISCIPLINE_MAP.yaml`
- post-write 対象に関する既存ルール

出力:

```yaml
operation_id: post_write_policy_violation.inspect
verdict: OK | BLOCKED
current_next_action_kind: post_write_policy_violation
changed_files: []
file_groups:
  guidance_changes: []
  tool_changes: []
  test_changes: []
  runtime_artifacts: []
  docs_notes: []
allowed_next_operations: []
forbidden_next_operations:
  - run_post_write_review
  - create_post_write_manifest
  - commit
required_resolution: []
```

この operation は read-only とする。

### 6.2 `post_write_verification.prepare_source_bundle`

目的:

`next_action.kind == post_write_verification` に到達した後、review target の本文を機械的に展開する。

入力:

- review 対象ファイル一覧
- git diff
- 対応する source refs
- review scope

出力:

```yaml
source_bundle:
  target_files:
    - path: null
      sha256: null
      content_mode: full_text | non_summary_excerpt
      content_ref: null
  source_materials:
    - path: null
      sha256: null
      content_mode: full_text | non_summary_excerpt
      content_ref: null
  exclusions: []
```

禁止事項:

- path / SHA だけの bundle
- main LLM の要約だけの bundle
- target と source material の混同

### 6.3 `post_write_verification.build_api_review_prompt`

目的:

source bundle と固定テンプレートから API review prompt を生成する。

出力 prompt の必須構造:

- Review Purpose
- User Review Requirements
- Target Materials
- Source Materials
- Review Criteria
- Non-goals / Out of Scope
- Main Preanalysis
- Required Checks
- Output Contract
- Sensitive Information Check

受入条件:

- target 本文が prompt 内にある
- source materials が path-only ではない
- 1 prompt 1 primary judgment になっている
- output contract が runner と一致する
- variant は設定キーから解決され、手選択しない

### 6.4 `post_write_verification.audit_api_review_prompt`

目的:

API に送る前に prompt 自体を機械検査し、失敗した prompt を送信させない。

検査項目:

- target file body が含まれている
- source material body が含まれている
- path-only セクションで終わっていない
- 要約禁止の場面で summary 表記がない
- 複数の独立判断を押し込んでいない
- output contract が期待 schema と一致する
- runner / variant / role が用途と一致する
- prompt source refs と生成 manifest が残っている

失敗時:

- API review-run を起動しない
- invalid prompt を証跡として保存する場合も、invalid と明記する
- review result としては扱わない

## 7. TDD 実装順序

### Phase 0: 現状事故を regression test 化

まず、今回の悪い prompt を抽象化した fixture を作る。

失敗させる条件:

- target が path と SHA だけ
- source material が path と SHA だけ
- `post_write_policy_violation` のまま review-run を開始しようとする
- prompt audit を通さず API runner を呼ぶ

期待:

- prompt audit は DEVIATION
- runner は起動不可
- next operation は `post_write_policy_violation.inspect` へ戻る

### Phase 1: Effective Prompt 固定化テスト

追加するテスト:

- `post_write_policy_violation` が canonical prompt path を返す
- prompt source refs からその場で合成しない
- prompt 本文に許可操作・禁止操作・次 operation が含まれる
- stale canonical prompt は通常 action として返らない

この時点では実装せず、まずテストを失敗させる。

### Phase 2: Inspect Operation テスト

追加するテスト:

- dirty worktree で変更ファイルを分類できる
- guidance / tools / tests / docs notes を別 cluster に分ける
- review-run / commit が forbidden として出る
- read-only でファイルを書かない

### Phase 3: Source Bundle Builder テスト

追加するテスト:

- target 本文を full text または non-summary excerpt として出す
- path-only bundle を拒否する
- source と target の役割を区別する
- SHA と本文が一致する

### Phase 4: Prompt Builder / Prompt Audit テスト

追加するテスト:

- source bundle から固定構造の prompt を作る
- target 本文なし prompt を拒否する
- 複数主判断 prompt を拒否する
- runner / output contract 不一致を拒否する
- variant は `config/api-settings.yaml` の default key から解決される

### Phase 5: Runner Gate テスト

追加するテスト:

- audit OK でのみ API runner が起動できる
- audit DEVIATION では runner が起動しない
- invalid prompt 由来の response を valid review-run として登録しない

## 8. 実装順序

1. この計画を承認する。
2. Phase 0 の regression test だけを追加する。
3. テスト失敗を確認する。
4. テスト追加 commit を作る。
5. Phase 1 以降を小さく分けて実装する。
6. 各 phase で test pass 後に commit する。
7. 最後に、今回の guidance relocation 作業へ戻り、正しい post-write flow で review をやり直す。

## 9. 現在の作業への適用

現在の guidance relocation 作業では、まだ uncommitted changes が残っている。

この状態では、次をしてはいけない。

- その場で API review prompt を作文する
- path-only prompt で API review を実行する
- invalid review-run を post-write verification 証跡として使う
- post-write manifest を手で確定する

先に行うべきこと:

1. `post_write_policy_violation` 用の固定 effective prompt を作る計画を承認する。
2. その prompt と operation contract の red test を追加する。
3. post-write prompt generation / audit の red test を追加する。
4. 実装後に、正しい経路で guidance relocation の post-write verification へ戻る。

## 10. 判断

LLM 処理は完全に排除しない。排除すべきなのは、手順選択・材料選定・prompt 合成の揺れである。

review / judgment という本来 LLM に任せるべき判断は残す。ただし、その判断に入る前の入力作成と gate は機械処理で固定する。

この方針により、API review の品質は reviewer model の気分ではなく、source bundle、prompt template、prompt audit、runner gate の再現性に支えられる。
