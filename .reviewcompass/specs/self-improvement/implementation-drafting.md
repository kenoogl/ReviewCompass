# self-improvement implementation 再確認記録

## 2026-06-08 tasks 再確認への対応

intent の「レビュー収集処理を事前設定の写像にしない」意図に伴い、self-improvement tasks.md の変更を implementation 観点で再確認した。

- T-002 の入力モデルは、`tools/self_improvement/input_model.py` と `tests/self-improvement/test_t002_input_model.py` で受けられている
- T-003 の signal_extraction は、`tools/self_improvement/signal_extraction.py`、`tools/self_improvement/schemas/signal.schema.json`、`tests/self-improvement/test_t003_signal_extraction.py` で受けられている
- T-004 の提案モデルは、`tools/self_improvement/proposal_model.py`、`learning/workflow/schemas/proposal.schema.json`、`tests/self-improvement/test_t004_proposal_model.py` で受けられている
- T-007 の履歴とロールバックは、`tools/self_improvement/rollback_model.py`、`learning/workflow/schemas/rollback.schema.json`、`tests/self-improvement/test_t007_rollback_model.py` で受けられている

確認結果として、実装済み self-improvement はレビュー収集を事前設定の写像として扱わず、上流出力と観察事実を入力モデルで保持し、signal 抽出、提案生成、履歴・ロールバックに分けて扱う。追加の実装変更は不要。

## 検証

- `.venv/bin/python3 -m pytest tests/self-improvement -q`：pass
