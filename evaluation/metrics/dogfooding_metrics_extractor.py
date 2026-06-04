"""dogfooding deployment メトリクス抽出器。"""
import json
from pathlib import Path

import yaml


FINAL_LABELS = ("must-fix", "should-fix", "leave-as-is")


def _load_yaml_dict(path):
  """YAML object を読み、読めない場合は空 dict を返す。"""
  if not path or not Path(path).is_file():
    return {}
  data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
  return data if isinstance(data, dict) else {}


def _count_values(values):
  """値ごとの出現回数を返す。"""
  counts = {}
  for value in values:
    counts[value] = counts.get(value, 0) + 1
  return counts


def _split_test_commands(value):
  """台帳の tests 文字列を概算コマンド数へ分割する。"""
  if not isinstance(value, str) or not value.strip():
    return []
  return [part.strip() for part in value.split(";") if part.strip()]


class DogfoodingMetricsExtractor:
  """dogfooding 記録から論文用メトリクスの入口スキーマを抽出する。"""

  def extract(self, review_run_dir, workflow_log_path, ledger_path=None):
    review_run_dir = Path(review_run_dir)
    workflow_log_path = Path(workflow_log_path)
    ledger_path = Path(ledger_path) if ledger_path else None

    summary = _load_yaml_dict(review_run_dir / "model-result-summary.yaml")
    triage = _load_yaml_dict(review_run_dir / "triage.yaml")
    clusters = _load_yaml_dict(review_run_dir / "must-fix-clusters.yaml")
    ledger = _load_yaml_dict(ledger_path)

    return {
      "artifact_id": "dogfooding_deployment_metrics",
      "metric_level": "dogfooding_deployment",
      "review_run": self._extract_review_run(summary, triage, clusters),
      "workflow_precheck": self._extract_workflow_precheck(workflow_log_path),
      "implementation": self._extract_implementation(ledger),
      "derivation": {
        "source_artifacts": [
          str(review_run_dir / "model-result-summary.yaml"),
          str(review_run_dir / "triage.yaml"),
          str(review_run_dir / "must-fix-clusters.yaml"),
          str(workflow_log_path),
          str(ledger_path) if ledger_path else "",
        ],
        "source_fields": [
          "model-result-summary.yaml.models[]",
          "triage.yaml.items[]",
          "must-fix-clusters.yaml.clusters[]",
          "workflow-precheck.log[].verdict",
          "workflow-precheck.log[].exit_code",
          "ledger.integration_result",
        ],
      },
    }

  def _extract_review_run(self, summary, triage, clusters_data):
    """review-run の raw / triage / 重要所見を集計する。"""
    models = summary.get("models") if isinstance(summary.get("models"), list) else []
    items = triage.get("items") if isinstance(triage.get("items"), list) else []
    clusters = (
      clusters_data.get("clusters")
      if isinstance(clusters_data.get("clusters"), list)
      else []
    )
    triage_label_counts = {label: 0 for label in FINAL_LABELS}
    for item in items:
      if not isinstance(item, dict):
        continue
      label = item.get("final_label")
      if label in triage_label_counts:
        triage_label_counts[label] += 1

    raw_paths = set()
    human_required_count = 0
    finding_count = 0
    for model in models:
      if not isinstance(model, dict):
        continue
      raw_path = model.get("raw_path")
      if isinstance(raw_path, str) and raw_path:
        raw_paths.add(raw_path)
      finding_count += int(model.get("findings_count") or 0)
      human_required_count += int(model.get("human_required_count") or 0)

    return {
      "run_id": summary.get("run_id") or triage.get("run_id"),
      "model_count": len([model for model in models if isinstance(model, dict)]),
      "raw_response_count": len(raw_paths),
      "finding_count": finding_count,
      "human_required_count": human_required_count,
      "triage_label_counts": triage_label_counts,
      "important_cluster_count": len([
        cluster for cluster in clusters if isinstance(cluster, dict)
      ]),
      "decision_actor": triage.get("decision_actor"),
      "decision_actor_type": triage.get("decision_actor_type"),
    }

  def _extract_workflow_precheck(self, workflow_log_path):
    """workflow-precheck.log の JSON Lines を集計する。"""
    entries = []
    skipped_line_count = 0
    if workflow_log_path.is_file():
      for line in workflow_log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
          continue
        try:
          entry = json.loads(line)
        except json.JSONDecodeError:
          skipped_line_count += 1
          continue
        if isinstance(entry, dict):
          entries.append(entry)

    verdicts = [entry.get("verdict") for entry in entries]
    subcommands = []
    commit_approval_failure_count = 0
    in_progress_block_count = 0
    for entry in entries:
      action = entry.get("action")
      if isinstance(action, dict):
        subcommands.append(action.get("subcommand"))
      reasons = entry.get("reasons")
      reason_text = "\n".join(reasons) if isinstance(reasons, list) else ""
      if "承認レコード" in reason_text or "commit_approval" in reason_text:
        commit_approval_failure_count += 1
      if "stages/in-progress" in reason_text:
        in_progress_block_count += 1

    return {
      "total_checks": len(entries),
      "by_verdict": _count_values(verdicts),
      "by_subcommand": _count_values(subcommands),
      "blocked_count": len([entry for entry in entries if entry.get("exit_code") == 2]),
      "warning_count": len([entry for entry in entries if entry.get("exit_code") == 1]),
      "commit_approval_failure_count": commit_approval_failure_count,
      "in_progress_block_count": in_progress_block_count,
      "skipped_line_count": skipped_line_count,
    }

  def _extract_implementation(self, ledger):
    """自律実行台帳の統合結果を集計する。"""
    integration_result = ledger.get("integration_result")
    if not isinstance(integration_result, dict):
      integration_result = {}
    test_commands = _split_test_commands(integration_result.get("tests"))
    return {
      "status": integration_result.get("status"),
      "test_command_count": len(test_commands),
      "decision": integration_result.get("decision"),
    }
