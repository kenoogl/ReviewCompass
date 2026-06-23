from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]

ACTIVE_ADAPTER_SURFACES = [
  "CLAUDE.md",
  "templates/todo/TODO_NEXT_SESSION.template.md",
]

LEGACY_ADAPTER_GUIDANCE_PATHS = [
  "docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md",
  "docs/operations/WORKFLOW_NAVIGATION_FOR_CODEX.md",
]

CANONICAL_ADAPTER_GUIDANCE_PATHS = [
  ".reviewcompass/guidance/WORKFLOW_NAVIGATION_FOR_CLAUDE.md",
  ".reviewcompass/guidance/WORKFLOW_NAVIGATION_FOR_CODEX.md",
]

LEGACY_DEPLOY_FACING_OPERATION_GUIDANCE = {
  "docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md",
}

LEGACY_RUNTIME_DISCIPLINE_PATHS = [
  "docs/disciplines/discipline_workflow_precheck_invocation.md",
  "docs/disciplines/discipline_normal_output_minimization.md",
]

ACTIVE_DISCIPLINE_ROOT_CONSUMERS = [
  "learning/workflow/schemas/proposal.schema.json",
  "tools/self_improvement/proposal_model.py",
  "tools/self_improvement/impact_analysis.py",
  "tools/self_improvement/machine_verification.py",
]


def _read(path):
  return (ROOT / path).read_text(encoding="utf-8")


def test_adapter_entrypoints_do_not_reference_legacy_operation_guidance():
  findings = []
  for surface in ACTIVE_ADAPTER_SURFACES:
    text = _read(surface)
    for legacy_path in LEGACY_ADAPTER_GUIDANCE_PATHS:
      if legacy_path in text:
        findings.append(f"{surface} -> {legacy_path}")

  assert findings == []


def test_adapter_guidance_files_exist_only_in_reviewcompass_guidance():
  for canonical_path, legacy_path in zip(
    CANONICAL_ADAPTER_GUIDANCE_PATHS,
    LEGACY_ADAPTER_GUIDANCE_PATHS,
  ):
    assert (ROOT / canonical_path).is_file()
    assert not (ROOT / legacy_path).exists()


def test_deploy_manifest_does_not_include_legacy_operation_guidance():
  data = yaml.safe_load(_read("deploy-manifest.yaml"))
  includes = {entry["path"] for entry in data["include"]}

  assert LEGACY_DEPLOY_FACING_OPERATION_GUIDANCE.isdisjoint(includes)


def test_effective_prompt_artifacts_do_not_embed_legacy_guidance_paths():
  prompt_dir = ROOT / ".reviewcompass" / "runtime" / "effective-prompts"
  findings = []
  for prompt_path in sorted(prompt_dir.glob("*.prompt.md")):
    text = prompt_path.read_text(encoding="utf-8")
    for legacy_path in LEGACY_ADAPTER_GUIDANCE_PATHS + LEGACY_RUNTIME_DISCIPLINE_PATHS:
      if legacy_path in text:
        findings.append(f"{prompt_path.relative_to(ROOT)} -> {legacy_path}")

  assert findings == []


def test_runtime_consumers_do_not_reference_legacy_runtime_discipline_paths():
  runtime_surfaces = [
    ".claude/hooks/README.md",
    ".codex/hooks/README.md",
    "tools/README.md",
  ]

  findings = []
  for surface in runtime_surfaces:
    text = _read(surface)
    for legacy_path in LEGACY_RUNTIME_DISCIPLINE_PATHS:
      if legacy_path in text:
        findings.append(f"{surface} -> {legacy_path}")

  assert findings == []


def test_active_discipline_root_consumers_do_not_require_legacy_docs_root():
  findings = []
  forbidden = "docs/disciplines/discipline_"
  for surface in ACTIVE_DISCIPLINE_ROOT_CONSUMERS:
    text = _read(surface)
    if forbidden in text:
      findings.append(f"{surface} -> {forbidden}")

  assert findings == []
