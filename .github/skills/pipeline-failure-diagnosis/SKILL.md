---
name: pipeline-failure-diagnosis
description: "Diagnose ML and MLOps pipeline failures in GitHub Actions, Azure Machine Learning, Python, YAML, Docker, dependency installation, data validation, model training, registration, and endpoint deployment. Use when a CI/CD job, Azure ML run, training job, or model deployment fails."
argument-hint: "Provide the failed pipeline run, job logs, error message, or files to investigate."
user-invocable: true
disable-model-invocation: false
---

# Pipeline Failure Diagnosis

## Purpose

Diagnose pipeline failures from evidence, identify the first meaningful failure, explain the root cause, and propose the smallest verified remediation. Cover the full path from GitHub Actions through Azure ML training, evaluation, model registration, and endpoint deployment.

## When To Use

Use this skill when:

- A GitHub Actions workflow fails or is stuck.
- An Azure ML command job, pipeline component, environment build, model registration, or endpoint deployment fails.
- A Python script works locally but fails in CI or Azure ML.
- YAML validation, interpolation, authentication, dependency, data, training, or serving errors occur.
- A deployment succeeds but health checks or prediction requests fail.

## Evidence Rules

- Ask for or inspect the complete failing step, its log context, workflow YAML, Azure ML YAML, entry-point script, and relevant requirements or environment files.
- Locate the earliest causal error rather than the last cascading error.
- Separate observed facts from hypotheses. State one falsifiable hypothesis before proposing a fix.
- Never claim a pipeline passed, a secret is valid, an artifact exists, or a cloud resource is reachable without evidence.
- Redact tokens, passwords, connection strings, signed URLs, and personally identifiable data from quoted logs.
- Do not retry destructive cloud operations or rotate credentials without explicit authorization.

## Procedure

1. **Classify the failure**
   - Identify the platform: GitHub Actions, Azure ML, Docker, Python, or endpoint.
   - Identify the stage: checkout, authentication, dependency setup, data access, training, evaluation, registration, deployment, or inference.
   - Record the run ID, job name, branch or commit, region, environment name, and timestamp when available.

2. **Find the first failure**
   - Read the failing step and the preceding 30 to 50 log lines.
   - Ignore secondary cancellation, timeout, cleanup, and downstream artifact errors until the first failure is understood.
   - Capture the exact error text, exit code, file path, line number, and referenced resource.

3. **Trace configuration and inputs**
   - Inspect workflow triggers, job dependencies, permissions, variables, secrets references, working directories, and artifact paths.
   - Inspect Azure ML compute, environment, input data, output paths, command strings, identities, and endpoint settings.
   - Check that relative paths are resolved from the intended repository or job working directory.

4. **Test the smallest discriminating check**
   - For YAML failures, validate YAML parsing and required keys.
   - For imports, compare declared dependencies with the selected runtime environment.
   - For data failures, inspect schema, columns, nulls, labels, file existence, and row counts without exposing sensitive records.
   - For model failures, run the smallest reproducible training or loading test.
   - For deployment failures, check artifact existence, model signature, environment compatibility, endpoint health, and request schema.

5. **Choose the root-cause fix**
   - Prefer correcting the producer of the bad value, path, artifact, dependency, or configuration.
   - Keep changes limited to the failing slice.
   - Add a regression check when the failure could recur.
   - Treat deployment approval, metric gates, and cloud resource deletion as separate explicit actions.

6. **Validate and report**
   - Rerun the same focused check that exposed the failure.
   - Run the narrowest relevant test, YAML validation, syntax check, or pipeline dry run.
   - If cloud execution is unavailable, report exactly what was validated locally and what remains unverified.

## Failure Checklist

### GitHub Actions

- Workflow YAML syntax and expression interpolation
- Trigger branch, path filters, and job dependency graph
- Runner OS and shell differences
- Repository or environment permissions
- Secret and variable names
- Working directory and artifact upload/download paths
- Python version, cache key, and dependency installation

### Azure Machine Learning

- Subscription, resource group, workspace, region, and identity
- Compute availability and quota
- Managed identity or service principal permissions
- Source directory and command entry point
- Environment image, Python version, and package installation
- Input URI, datastore, mount mode, schema, and authentication
- Output artifact paths and model registration name/version
- Endpoint deployment environment, scoring script, traffic, and health probes

### Runtime And Data

- Import errors and package version conflicts
- OS-specific path and shell behavior
- Missing files or incorrect relative paths
- Empty data, schema drift, null values, and invalid target labels
- Train/serve feature mismatch
- Serialization incompatibility
- Port binding, request method, JSON schema, and endpoint readiness

## Output Format

Return:

1. **Diagnosis:** the first meaningful failure and the most likely root cause.
2. **Evidence:** exact log facts, file paths, configuration values, and exit code.
3. **Discriminating check:** the smallest check used or still needed.
4. **Fix:** the smallest concrete code or configuration change.
5. **Validation:** commands or checks run and their results.
6. **Remaining risk:** cloud, credential, data, environment, or production checks not performed.

Do not present a speculative fix as a confirmed resolution.
