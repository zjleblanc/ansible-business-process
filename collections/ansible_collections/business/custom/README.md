# business.custom

Ansible collection for custom filter plugins (and other small helpers) that don't fit under a service-specific
collection like `business.google`.

## Filters

- `parse_sf_tasks` -- Parses the grouped HTML table from a Salesforce report export email (e.g. an "Activities" or
  "Tasks" report grouped by Company / Account and Related To) into a list of accounts, each with their nested
  opportunities, each with their individual task records.

### `parse_sf_tasks`

Salesforce report emails render their grouped table using `rowspan` header cells for the Account and Related To
(Opportunity) columns instead of repeating those values on every row. This filter walks the table and re-associates
each task row with its account/opportunity context, returning:

```python
[
    {
        "account": "American Airlines, Inc.",
        "account_url": "https://redhatcrm.lightning.force.com/lightning/r/.../view",
        "opportunities": [
            {
                "opportunity": "Renewal - American Airlines, Inc. - 00545954",
                "opportunity_url": "https://redhatcrm.lightning.force.com/lightning/r/.../view",
                "tasks": [
                    {
                        "account": "American Airlines, Inc.",
                        "account_url": "https://redhatcrm.lightning.force.com/lightning/r/.../view",
                        "opportunity": "Renewal - American Airlines, Inc. - 00545954",
                        "opportunity_url": "https://redhatcrm.lightning.force.com/lightning/r/.../view",
                        "subject": "AAP Upgrade Review",
                        "task_url": "https://redhatcrm.lightning.force.com/lightning/r/.../view",
                        "date": "3/11/2026",
                        "comments": "Met with AA to explain upgrade process and requirements..."
                    }
                ]
            }
        ]
    }
]
```

Each task dictionary is flat and carries its parent `account`/`opportunity` metadata, so tasks remain self-contained
when flattened for iteration:

```yaml
- name: Parse Salesforce tasks from a report email body
  ansible.builtin.set_fact:
    sf_accounts: "{{ gmail_label_search.messages[0].body | business.custom.parse_sf_tasks }}"

- name: Flatten to a single list of tasks across all accounts/opportunities
  ansible.builtin.set_fact:
    sf_tasks: >-
      {{ sf_accounts
         | map(attribute='opportunities') | flatten
         | map(attribute='tasks') | flatten }}
```

## Requirements

- `beautifulsoup4`

Install with:

```bash
pip install beautifulsoup4
```
