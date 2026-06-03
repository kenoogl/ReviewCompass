# analysis implementation recheck triage recommendation

run_id: `2026-06-04-implementation-recheck-run`

## Model Summary

| model | raw | parse | findings |
| --- | --- | --- | ---: |
| claude-sonnet-4-6 | `raw/claude-sonnet-4-6.round-1.txt` | parsed | 0 |
| gpt-5.4 | `raw/gpt-5.4.round-1.txt` | parsed | 5 |
| gemini-3.1-pro-preview | `raw/gemini-3.1-pro-preview.round-1.txt` | parsed | 2 |

## Recommended Triage

| finding_id | recommendation | plain explanation | recommended action |
| --- | --- | --- | --- |
| `2026-06-04-implementation-recheck-run-gpt-5.4-adversarial-001` | should-fix | `conformance-evaluation` の JSON が壊れて読めない場合も `missing` 扱いになり、欠落と読取失敗の区別が弱い。仕様の enum は 4 値で `conformance_evaluation_unreadable` を明示していないため、実装修正だけでなく仕様との整合確認が必要。 | T-002 の失敗理由を、現行 4 値のまま `detail` と `failure_id` で区別するか、新 enum を追加するかを人が選ぶ。 |
| `2026-06-04-implementation-recheck-run-gpt-5.4-adversarial-002` | must-fix | reports の `mode_comparison_report.json` が `mode` という非正本フィールドを数えており、正式な `review_mode` を見ていない。入力に `mode` が無いと空集計になり得る。 | `review_mode` を集計対象に変更し、テストで `mode` ではなく `review_mode` 由来であることを固定する。 |
| `2026-06-04-implementation-recheck-run-gpt-5.4-adversarial-003` | leave-as-is | 現行ガードは foundation 語彙名のプロパティに `enum` が置かれた場合を検出する設計で、analysis 所有語彙 `maturity_label` 等は foundation 語彙集合に含めていない。今回の指摘は現行入力では誤検出を示していない。 | 今回は変更しない。将来、foundation 語彙の参照スキーマが実体化したら比較強化を検討する。 |
| `2026-06-04-implementation-recheck-run-gpt-5.4-adversarial-004` | should-fix | `intake_failure_report` が `failure_id`、`affected_destinations`、`detected_at` など設計上の最低項目を持っていない。下流が「どこに影響する失敗か」を機械判断しにくい。 | schema と writer に設計上の最低項目を追加し、T-002 テストで必須化する。 |
| `2026-06-04-implementation-recheck-run-gpt-5.4-adversarial-005` | should-fix | `target_id` は設計上 optional だが、claim→evidence のようなエントリ単位参照では実質必要になる。現行スキーマはファイル粒度への劣化を防ぎきれない。 | まず参照解決テストを強化し、エントリ単位参照が必要な箇所では `target_id` を要求する条件付き検査を追加する。 |
| `2026-06-04-implementation-recheck-run-gemini-3.1-pro-preview-judgment-001` | must-fix | upstream evaluation の実体パスは `experiments/analysis/` だが、no-write ガードがこのパスを見ていない。上流成果物を書き換えないという境界検査が抜けている。 | `_EVALUATION_PATH_MARKERS` に `experiments/analysis/` を追加し、検出テストを追加する。 |
| `2026-06-04-implementation-recheck-run-gemini-3.1-pro-preview-judgment-002` | must-fix | `evidence_refs` が裸の文字列配列になっている。設計は `*_refs` を `{ref_type, target_path, target_id}` 形式に統一すると定めている。 | role/mode diff schemas と builders/tests を構造化参照配列へ変更する。 |

## Count

- must-fix: 3
- should-fix: 3
- leave-as-is: 1

## Approval Boundary

The must-fix items above require human approval before implementation.
