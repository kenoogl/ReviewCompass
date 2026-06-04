# Proxy decision request: self-improvement implementation review-run

あなたは proxy_model として、self-improvement implementation.triad-review の重要所見について、人間の代わりに実装可否判断を行う。コミット、プッシュ、spec.json 更新、フェーズ移行は承認しない。ここで承認できるのは、重要所見に対する実装修正方針だけである。

## 入力証跡

- review-run summary: raw-review-triage-summary.md
- Claude raw: raw/claude-sonnet-4-6.round-1.txt
- GPT raw: raw/gpt-5.4.round-1.txt
- Gemini raw: raw/gemini-3.1-pro-preview.round-1.txt

## 判断対象

各 cluster について、候補 A/B/C から1つを選ぶ。

### SI-IMPL-MF-001: motivating_evidence の必須3項目検証

問題: `proposal_model.py` の evidence 検証が集合比較の向きで壊れ、正しい証拠を不正扱いする可能性がある。

- A: must-fix。`source/location/observation` がすべて存在することを `issubset` 等で正しく検査し、正常系・欠落系テストを追加/修正する。
- B: should-fix。既存テストが通っているため後続に回す。
- C: leave-as-is。現状の比較式で十分とみなす。

推薦: A。提案 YAML の中核検証であり、正しい入力を壊す可能性がある。

### SI-IMPL-MF-002: proposed_change の仕様・schema・実装の型不整合

問題: gpt-5.4 は仕様が文字列本文を想定すると指摘し、実装/schema は object 固定。Claude も type-specific schema の弱さを指摘。

- A: must-fix。正本を再確認し、実装・schema・テストを同じ契約へ揃える。第1案は object を正本とするなら requirements/design の例を追従させず、実装側だけではなく schema 条件を強化する。文字列正本なら実装/schemaを文字列対応へ変える。
- B: should-fix。実装は object で動いているため、review-wave へ延期する。
- C: leave-as-is。Python 側検査があるため schema 不整合は許容する。

推薦: A。ただし最初の修正では design/tasks の正本が object 構造を要求しているかを確認し、最小の契約整合にする。

### SI-IMPL-MF-003: 平均採用日数が廃止済み `approved_at` に依存

問題: `effect_measurement.py` が `approved_at` を読むが、A-019/DVT-S001 後の正本では `approved_at` は廃止され、`materialized_at` またはファイル配置時点との契約になっている。

- A: must-fix。`approved_at` 依存をやめ、正本の時系列契約に合うフィールドへ変更し、テストで 0.0 固定にならないことを検証する。
- B: should-fix。論文用メトリクス段階まで延期する。
- C: leave-as-is。現状の 0.0 を未知値として許容する。

推薦: A。効果測定7指標の一つが空振りするため、self-improvement の目的に直撃する。

### SI-IMPL-MF-004: T-011 traceability gate の文書形式依存

問題: `traceability.py` の test level / key regression / requirements traceability の判定が、実際の日本語表や token と合わず、正しい実装でも失敗または無効化する可能性がある。

- A: must-fix。文書表の実体に合わせて parser/期待値を修正し、T-011 が実際に pass/fail する意味あるゲートになるようにする。
- B: should-fix。現行テストが pass しているため、次の実装段で扱う。
- C: leave-as-is。T-011 は参考テストなので現状でよい。

推薦: A。最終 traceability gate が壊れていると implementation.triad-review 完了判断が空洞化する。

### SI-IMPL-MF-005: aspirational → enforced の承認ゲート

問題: `ApprovalModel.approve()` の status_change 正式化が通常承認と同じ語彙で通り、特別ゲートとして弱い可能性がある。

- A: must-fix。status_change to enforced には通常承認とは別の明示語句または専用 evidence を要求し、テストで通常承認では通らないことを確認する。
- B: should-fix。正本語彙の追加判断が必要なため、運用文書に延期理由を記す。
- C: leave-as-is。通常の明示承認で十分とみなす。

推薦: A。正式規律化は権限上重要な操作であり、普通の承認と同じでは設計意図が弱まる。

### SI-IMPL-MF-006: new_discipline の関係明示が機械検証可能でない

問題: `relationship_notes` が空でなければ通るため、tasks.md が要求する「機械検証可能な関係明示」の定義がない。

- A: must-fix。`relationship_notes` に機械検証可能な最低構造を定義する。例: `related_disciplines` 配列または `relationship_notes` 内の `[[discipline_*]]` 参照を要求し、テスト化する。
- B: should-fix。topic-108/F-012 として DVT に延期理由を記す。
- C: leave-as-is。非空文字列で十分とみなす。

推薦: A。tasks が「定義してからテスト化」と明示しており、現状は未完了に近い。

### SI-IMPL-MF-007: RB 採番の全4ディレクトリ走査

問題: gpt-5.4 は `rollback_model.py#next_rollback_id` が rollback 配下のみを走査し、全4ディレクトリ走査ルールに反すると指摘。

- A: must-fix。正本で RB も全4ディレクトリ走査が必要なら実装・テストを修正する。WP/RB の名前空間分離も同時に確認する。
- B: should-fix。RB は rollback 専用 ID なので、正本側の表現を限定し、実装は維持する。
- C: leave-as-is。rollback 配下のみで十分。

推薦: A寄り。ただし WP と RB の名前空間分離が正しいなら、実装修正ではなく正本文書の明確化になる可能性がある。

### SI-IMPL-MF-008: 運用文書が self-improvement に規律直接更新権があるように読める

問題: docs/operations/SELF_IMPROVEMENT.md が出力に `docs/disciplines/` 更新を含め、提案権のみという権限分離と矛盾する可能性がある。

- A: must-fix。運用文書を「提案 YAML と証跡を出す。実体変更は workflow-management 経由」と明確化し、直接更新と読める表現を修正する。
- B: should-fix。実装の MV-1 が守るため、文書は後で直す。
- C: leave-as-is。文書の表現は問題ない。

推薦: A。権限分離は self-improvement の中心仕様で、文書の誤読は運用事故につながる。

## 出力形式

次の YAML のみを返す。説明文や Markdown は不要。

```yaml
proxy_model_id: gpt-5.5
decisions:
  - cluster_id: SI-IMPL-MF-001
    selected_option: A
    final_label: must-fix
    rationale: "..."
    rejected_options:
      - option_id: B
        reason: "..."
      - option_id: C
        reason: "..."
```

全8 cluster を必ず含める。
