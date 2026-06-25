# 決定事項：proxy 裁定レコードの配置（コード正本）

本ファイルは検証者に渡す合意事項の箇条書きである（判断理由・議論ログは含めない）。

- 正本は実装コード。`tools/make-proxy-approval.py` が固定名で生成する配置を正とする。
- 裁定ファイルは `decisions/<suffix>.yaml`。`<suffix>` は `<model>-<role>-<連番>`。
- 束ねファイルは `proxy-approval.yaml`。その `proxy_decisions` は `decisions/<suffix>.yaml` を指す。
- proxy_model への判断プロンプトと生応答は review-run 直下に保存する。ファイル名は実行時に指定でき、特定名を断定しない。
- 旧表記 `proxy-decisions/<finding-id>.{prompt.md,raw.txt,decision.yaml}`、`proxy-decision-prompts/`、`<batch>.raw.yaml`、`<batch>.decisions-input.yaml` は現行コードが生成しないため除去する。
- `proxy-approval.yaml` 自体は `decision_scope` を持たない。`proxy_allowed` と `human_only` の境界は別レコード（Requirement 14 の `record_human_decision` の `decision_scope`）が機械判定で enforce する。
