"""Explicit mode switch for conformance-evaluation."""


class ModeSwitchError(ValueError):
  """Raised when mode selection is not explicit and valid."""


class ModeSwitch:
  def __init__(self, handlers):
    self.handlers = dict(handlers)

  def dispatch(self, mode: str, payload: dict):
    if mode not in {"check", "generation"}:
      raise ModeSwitchError(f"unknown_mode: {mode}")
    if mode not in self.handlers:
      raise ModeSwitchError(f"handler_missing: {mode}")
    return self.handlers[mode](payload)

  def has_auto_detection(self) -> bool:
    return False

