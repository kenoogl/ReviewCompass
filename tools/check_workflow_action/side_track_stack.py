"""Side track stack helpers for workflow-management T-017."""

from pathlib import Path

import yaml


DEFAULT_SIDE_TRACK_STACK_PATH = "stages/in-progress/side-track-stack.yaml"
SCHEMA_VERSION = "side-track-stack-v1"


def empty_stack():
  return {
    "schema_version": SCHEMA_VERSION,
    "frames": [],
  }


def _result(verdict, reasons, stack=None, next_required_action=None, operation_mode=None):
  response = {
    "verdict": verdict,
    "reasons": reasons,
  }
  if stack is not None:
    response["stack"] = stack
  if next_required_action is not None:
    response["next_required_action"] = next_required_action
  if operation_mode is not None:
    response["operation_mode"] = operation_mode
  return response


def _load_stack(path):
  path = Path(path)
  if not path.exists():
    return empty_stack(), []
  try:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
  except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
    return empty_stack(), [f"side track stack を読めません: {path}: {exc}"]
  if data is None:
    return empty_stack(), []
  if not isinstance(data, dict):
    return empty_stack(), ["side track stack は mapping である必要があります"]
  data.setdefault("schema_version", SCHEMA_VERSION)
  data.setdefault("frames", [])
  return data, []


def _write_stack(path, stack):
  path = Path(path)
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(yaml.safe_dump(stack, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _validate_push_frame(stack, frame):
  reasons = []
  staged_files = frame.get("staged_file_set")
  allowed_files = frame.get("allowed_files")
  if isinstance(staged_files, list) and isinstance(allowed_files, list):
    allowed = set(allowed_files)
    out_of_scope = [
      path for path in staged_files
      if isinstance(path, str) and path not in allowed
    ]
    if out_of_scope:
      reasons.append("staged_file_set が allowed_files を超えています: " + ", ".join(out_of_scope))
  else:
    reasons.append("allowed_files と staged_file_set は list である必要があります")

  frames = stack.get("frames")
  max_depth = frame.get("max_depth", 2)
  if isinstance(frames, list) and isinstance(max_depth, int):
    if len(frames) + 1 > max_depth:
      reasons.append(f"max_depth を超過しています: {len(frames) + 1} > {max_depth}")
  else:
    reasons.append("frames は list、max_depth は integer である必要があります")

  return reasons


def current(path=None):
  """Read the current stack without mutating it."""
  stack_path = Path(path or DEFAULT_SIDE_TRACK_STACK_PATH)
  stack, reasons = _load_stack(stack_path)
  return _result(
    "DEVIATION" if reasons else "OK",
    reasons,
    stack=stack,
    operation_mode="read_only",
  )


def push_frame(path, frame):
  """Push a frame to the stack file."""
  stack, reasons = _load_stack(path)
  if not isinstance(frame, dict):
    reasons.append("side track frame は mapping である必要があります")
  else:
    reasons.extend(_validate_push_frame(stack, frame))
  if reasons:
    return _result("DEVIATION", reasons, stack=stack, operation_mode="mutating")
  stack["frames"].append(frame)
  _write_stack(path, stack)
  return _result("OK", [], stack=stack, operation_mode="mutating")


def _state_refs_resolved(frame):
  return_to = frame.get("return_to")
  if not isinstance(return_to, dict):
    return False
  refs = return_to.get("state_refs")
  if not isinstance(refs, list):
    return False
  for ref in refs:
    if not isinstance(ref, str) or not ref:
      return False
    if ref.startswith("missing"):
      return False
  return True


def _pop_from_stack(stack, frame_id, current_staged_file_digest=None):
  reasons = []
  frames = stack.get("frames")
  if not isinstance(frames, list):
    return _result("DEVIATION", ["frames は list である必要があります"], stack=stack)

  if not frames:
    return _result("DEVIATION", ["side track stack が空です"], stack=stack)

  top = frames[-1]
  if top.get("frame_id") != frame_id:
    return _result("DEVIATION", ["side track stack は LIFO で top frame だけを pop できます"], stack=stack)

  if not _state_refs_resolved(top):
    reasons.append("return_to の state_refs を解決できません")

  expected_digest = top.get("staged_file_digest")
  if (
    current_staged_file_digest is not None
    and expected_digest is not None
    and current_staged_file_digest != expected_digest
  ):
    reasons.append("staged_file_digest が side track 開始時と一致しません")

  if reasons:
    return _result(
      "DEVIATION",
      reasons,
      stack=stack,
      next_required_action="repair_workflow_state",
      operation_mode="mutating",
    )

  popped = dict(top)
  remaining = dict(stack)
  remaining["frames"] = frames[:-1]
  response = _result("OK", [], stack=remaining, operation_mode="mutating")
  response["popped_frame"] = popped
  response["next_required_action"] = top.get("return_to", {}).get("required_action")
  return response


def pop_frame(stack_or_path, frame_id, current_staged_file_digest=None):
  """Pop the top frame from a stack object or stack file."""
  if isinstance(stack_or_path, (str, Path)):
    path = Path(stack_or_path)
    stack, reasons = _load_stack(path)
    if reasons:
      return _result("DEVIATION", reasons, stack=stack, operation_mode="mutating")
    result = _pop_from_stack(stack, frame_id, current_staged_file_digest)
    if result.get("verdict") == "OK":
      _write_stack(path, result["stack"])
    return result
  return _pop_from_stack(stack_or_path, frame_id, current_staged_file_digest)
