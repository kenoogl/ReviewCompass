# conformance-evaluation implementation 再確認記録

## 2026-06-08 tasks 再確認への対応

intent の「レビュー収集処理を事前設定の写像にしない」意図に伴い、conformance-evaluation tasks.md の変更を implementation 観点で再確認した。

- T-004 の照合チェックモードは、`tools/conformance_evaluation/check_mode.py`、`tools/conformance_evaluation/machine_verification.py`、`tests/conformance-evaluation/test_conformance_evaluation.py` で受けられている
- T-006 の推定モデルは、`tools/conformance_evaluation/estimation_model.py` と `tests/conformance-evaluation/test_conformance_evaluation.py` で受けられている
- T-007 の比較モデルは、`tools/conformance_evaluation/comparison_model.py` と `tests/conformance-evaluation/test_conformance_evaluation.py` で受けられている
- T-014 の契約所有候補と仕様更新草案は、`tools/conformance_evaluation/contract_ownership.py`、`tests/conformance-evaluation/test_contract_ownership.py`、`tests/conformance-evaluation/test_spec_update_adoption.py` で受けられている

確認結果として、実装済み conformance-evaluation はレビュー収集を事前設定の写像として扱わず、実装コードからの推定、既存上流文書との比較、契約所有候補と仕様更新草案の出力によって、コードと仕様の乖離を構造化して扱う。追加の実装変更は不要。

## 検証

- `.venv/bin/python3 -m pytest tests/conformance-evaluation -q`：pass
