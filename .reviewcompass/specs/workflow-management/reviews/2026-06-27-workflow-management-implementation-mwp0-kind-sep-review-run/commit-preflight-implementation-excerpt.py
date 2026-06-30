# tools/check-workflow-action.py より抜粋
# _commit_preflight_next_action 関数（行 4151-4223）
# commit-preflight サブコマンドが呼び出す kind 解決ロジック

def _commit_preflight_next_action(cwd, in_progress_files):
  """commit 指示入口で見る現在の workflow action を副作用なしに組み立てる。"""
  if in_progress_files:
    return build_in_progress_next_action(cwd, in_progress_files[0])
    # build_in_progress_next_action の返す kind 値は別関数の実装に依存する

  verification_targets = list_post_write_verification_targets(cwd)
  if verification_targets:
    manifest_state, manifest = evaluate_post_write_manifest_state(
      cwd,
      verification_targets,
    )
    if manifest_state != "completed":
      action = {
        "kind": "verification_pending",
        "verification_type": "post_write_verification",
        "required_action": "run_post_write_verification",
        "target_files": verification_targets,
        "manifest_status": manifest_state,
        "manifest": manifest.get("_path") if isinstance(manifest, dict) else None,
        "reason": "post-write-verification 対象の未完了変更があります",
      }
      if isinstance(manifest, dict) and manifest.get("codes"):
        action["codes"] = manifest.get("codes")
      return action

  commit_unit_state, _ = validate_commit_unit_record(cwd)
  commit_unit_codes = commit_unit_state.get("codes") or []
  if commit_unit_state.get("exists") and "COMMIT_MIXING_RISK" in commit_unit_codes:
    record = commit_unit_state.get("record") or {}
    return {
      "kind": "commit_mixing_risk",
      "required_action": "split_or_refresh_commit_unit",
      "target_files": record.get("target_files") or record.get("allowed_files") or [],
      "extra_staged_files": (
        commit_unit_state.get("current_state", {}).get("extra_staged_files") or []
      ),
      "path": commit_unit_state.get("path"),
      "feature": None,
      "phase": None,
      "stage": None,
      "reason": "commit unit の allowed files 外の staged file が混入しています",
    }
  if commit_unit_state.get("exists") and "STALE_COMMIT_UNIT" in commit_unit_codes:
    record = commit_unit_state.get("record") or {}
    return {
      "kind": "commit_unit_stale",
      "required_action": "refresh_commit_unit",
      "target_files": record.get("target_files") or record.get("allowed_files") or [],
      "path": commit_unit_state.get("path"),
      "feature": None,
      "phase": None,
      "stage": None,
      "reason": "commit unit が現在の staged 内容と一致しません",
    }

  specs, missing = load_all_feature_specs(cwd)
  if missing:
    return {
      "kind": "unknown",
      "required_action": "repair_workflow_state",
      "reason": "必要な spec.json が不足しています",
      "missing_features": missing,
    }

  commit_stop_point = resolve_normal_workflow_commit_stop_point_action(cwd, specs)
  if commit_stop_point:
    return commit_stop_point
    # resolve_normal_workflow_commit_stop_point_action が返す kind 値は別関数の実装に依存する

  return {
    "kind": "commit_candidate",
    "required_action": "prepare_commit",
    "reason": "commit 指示入口で遮断すべき active workflow unit はありません",
  }
