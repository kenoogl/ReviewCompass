# Self-Improvement Machine Verification

`tools/self-improvement-check.py` は self-improvement が所有する workflow 改善提案の安全検査を担当する。

## Scope

- `MV-1`: self-improvement による `docs/disciplines/discipline_*.md` 直接書き込みを検出する。
- `MV-2`: 提案 YAML の必須 7 フィールドを検査する。
- `MV-3`: `materialization_commit_hash` が null の場合は未実体化として正常にスキップし、非 null の場合だけ `git cat-file -e` で実在を検査する。
- `MV-4`: `status: superseded` の提案に `superseded_by`、`superseded_at`、`reopen_reason` があることを検査する。

## Responsibility Boundary

`tools/check-workflow-action.py` は全体 workflow の段階遷移、commit / push 事前検査、post-write verification を担当する。

`tools/self-improvement-check.py` は self-improvement の提案 YAML と workflow 改善履歴に閉じた検査を担当する。規律ファイル本体の変更を実行せず、直接書き込みを `MV-1` で fail-closed にする。

## Manual Commands

- `python3 tools/self-improvement-check.py mv1 --actor-feature self-improvement --changed-file docs/disciplines/discipline_x.md --json`
- `python3 tools/self-improvement-check.py all --actor-feature self-improvement --proposal-path learning/workflow/approved-updates/WP-001.yaml --metric-date 2026-06-04 --json`

検査結果は `learning/workflow/metrics/<日付>-machine-verification.yaml` に記録する。
