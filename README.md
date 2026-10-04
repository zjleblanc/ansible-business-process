# Ansible Business Process

Ansible automation for recurring sales and customer-support workflows: syncing Salesforce
account activity into a Google Sheets dashboard with AI-written summaries, and fetching,
AI-summarizing, and change-tracking Red Hat support cases with e-mail notifications. Each
workflow is a thin, AAP-ready playbook backed by purpose-built collections, with the platform
configuration (Controller job templates, credentials, EDA) and the custom Execution Environment
that runs them managed as code in this same repo.

This repo follows the conventions in [AGENTS.md](AGENTS.md) (the authoritative development guide
for both humans and AI coding agents working here) and the
[Red Hat CoP Ansible good practices](https://redhat-cop.github.io/automation-good-practices/).

## What's here

| Workflow | Playbook(s) | Docs |
|---|---|---|
| Salesforce → Google Sheets account dashboard | [`playbooks/pb_update_account_tasks.yml`](playbooks/pb_update_account_tasks.yml), [`playbooks/pb_gmail_tasks_report.yml`](playbooks/pb_gmail_tasks_report.yml) | — |
| Red Hat support case AI analysis | [`playbooks/pb_analyze_support_cases.yml`](playbooks/pb_analyze_support_cases.yml) | [Quick Start](docs/support-analyzer/QUICKSTART.md), [Examples](docs/support-analyzer/EXAMPLES.md), [LLM Configuration](docs/support-analyzer/LLM_CONFIGURATION.md), [Data Flow](docs/support-analyzer/DATA_FLOW.md) |
| Red Hat support case tracking + e-mail alerts | [`playbooks/pb_track_support_cases.yml`](playbooks/pb_track_support_cases.yml) | [Examples](docs/support-tracker/EXAMPLES.md), [Data Flow](docs/support-tracker/DATA_FLOW.md) |
| AAP configuration as code | [`playbooks/pb_deploy_aap_config.yml`](playbooks/pb_deploy_aap_config.yml) | [Usage Guide (AAP setup end-to-end)](docs/common/USAGE.md) |

Supporting pieces:

- **`collections/ansible_collections/business/`** — two local collections that back the
  workflows above:
  - [`business.google`](collections/ansible_collections/business/google/README.md) — Gmail
    search, Google Sheets read/update, and Salesforce-activity-email parsing filters.
  - [`business.support`](collections/ansible_collections/business/support/README.md) — Red Hat
    GraphQL case fetch, OpenAI-compatible LLM summarization, and Sheets-backed case tracking.
- **`tasks/`** — per-account task files included by the playbooks (`account_update.yml`,
  `account_analyze.yml`, `account_track.yml`).
- **`templates/`** — Jinja templates for the AI analysis report (Markdown/JSON) and the
  tracker's change-notification e-mail.
- **`aap_config/`** — Ansible Automation Platform Controller and EDA objects (projects,
  credential types, credentials, job templates, schedules) defined as code via
  `infra.aap_configuration`, deployed by `pb_deploy_aap_config.yml`. See the
  [aap-config-as-code skill](.cursor/skills/aap-config-as-code/README.md) for the patterns this
  repo follows.
- **`execution-environment/`** — the custom Execution Environment definition (and
  [README](execution-environment/README.md)) that bundles the Python/Galaxy dependencies the
  playbooks and collections need; built automatically by
  [`.github/workflows/build-execution-environment.yml`](.github/workflows/build-execution-environment.yml).
- **`rulebooks/`** — example `ansible-rulebook` sources for Event-Driven Ansible (webhook and
  range demos).
- **`scripts/`** — one-time developer tooling: `google_oauth_setup.py` (OAuth2 refresh-token
  helper) and `generate_pdf.js` (optional Puppeteer PDF export for the analyzer).
- **`docs/common/`** — cross-workflow guides:
  [GSuite service-account quick start](docs/common/GSUITE_QUICKSTART.md) and the
  [AAP/Controller end-to-end usage guide](docs/common/USAGE.md).
- **`CHANGELOG.md`** — history of notable changes to playbooks, collections, and configuration.

## Getting started

1. Install Ansible tooling and the Python dependencies the collections need:

   ```bash
   pip install -r execution-environment/requirements/requirements.txt
   ansible-galaxy collection install -r collections/requirements.yml
   ```

2. Pick a workflow above and follow its linked quick start / docs for credentials and variables.
   Secrets are supplied via an Ansible Vault file (`vault.yml`, gitignored) passed with `-e`.

3. Run a playbook with `ansible-navigator` (not `ansible-playbook` — see
   [AGENTS.md](AGENTS.md#playbook-design-standards)), e.g.:

   ```bash
   ansible-navigator run playbooks/pb_track_support_cases.yml -e @vault.yml -e @vars/accounts.yml
   ```

   Each playbook's header comment lists its own run examples.

4. To run any of this on AAP/Controller instead of the CLI, deploy the configuration in
   `aap_config/` and follow [docs/common/USAGE.md](docs/common/USAGE.md).

## Development

- **Conventions**: [AGENTS.md](AGENTS.md) is the authoritative guide for collection/module/task
  structure, naming, Jinja limits, and when to extract filter plugins — read it before adding or
  changing automation content.
- **CI**: [`.github/workflows/validate.yml`](.github/workflows/validate.yml) runs `ansible-lint`,
  a playbook syntax check, and a Markdown spell check on every push/PR;
  [`gitleaks.yml`](.github/workflows/gitleaks.yml) scans for committed secrets;
  [`spotter-ci.yml`](.github/workflows/spotter-ci.yml) runs Steampunk Spotter analysis;
  [`build-execution-environment.yml`](.github/workflows/build-execution-environment.yml) builds
  and publishes the EE image weekly and on PRs that touch it;
  [`demo-intelligent-cac-deploy.yml`](.github/workflows/demo-intelligent-cac-deploy.yml) is a
  manually-triggered, change-aware deploy of `aap_config/` and a project sync.
- **Local validation**:

  ```bash
  ansible-lint
  ansible-navigator run playbooks/pb_example.yml --mode stdout -- --syntax-check
  ```

## Contributing

Open an issue (see [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/) for bug/feature/docs
templates) or submit a PR. New roles, playbooks, or patterns should include a README/docs update
per [AGENTS.md](AGENTS.md#repository-documentation).
