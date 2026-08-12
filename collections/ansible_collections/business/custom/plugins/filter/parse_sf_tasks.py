# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Zachary LeBlanc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
    name: parse_sf_tasks
    short_description: Parse a Salesforce "Activities" report email into structured account/opportunity/task data
    version_added: "1.0.0"
    description:
        - Parses the grouped HTML table found in a Salesforce report export email (e.g. an "Activities" or "Tasks"
          report grouped by Company / Account and Related To) into a nested list of accounts, each containing their
          opportunities, each containing their individual tasks.
        - The Salesforce report table represents grouping with C(rowspan) V(th) cells rather than repeating the
          account/opportunity on every row, so this filter re-associates each task row with its account and
          opportunity context.
        - Within each opportunity, tasks are sorted by date descending. Within each account, opportunities are sorted
          by their latest task date descending.
    positional: _input
    options:
        _input:
            description: Raw HTML content of the Salesforce report email body.
            type: str
            required: true
    requirements:
        - beautifulsoup4
'''

EXAMPLES = r'''
- name: Parse Salesforce tasks from a report email body
  ansible.builtin.set_fact:
    sf_accounts: "{{ gmail_label_search.messages[0].body | business.custom.parse_sf_tasks }}"

- name: Flatten to a single list of tasks across all accounts/opportunities
  ansible.builtin.set_fact:
    sf_tasks: >-
      {{ sf_accounts
         | map(attribute='opportunities') | flatten
         | map(attribute='tasks') | flatten }}
'''

RETURN = r'''
_value:
    description: List of accounts, each with their nested opportunities and tasks.
    type: list
    elements: dict
    contains:
        account:
            description: Account (Company) name.
            type: str
        account_url:
            description: Salesforce URL for the account.
            type: str
        opportunities:
            description: Opportunities ("Related To") grouped under this account.
            type: list
            elements: dict
            contains:
                opportunity:
                    description: Opportunity name.
                    type: str
                opportunity_url:
                    description: Salesforce URL for the opportunity.
                    type: str
                tasks:
                    description: Individual task/activity records for this opportunity.
                    type: list
                    elements: dict
                    contains:
                        account:
                            description: Account name (duplicated from the parent account for standalone use).
                            type: str
                        account_url:
                            description: Salesforce URL for the account.
                            type: str
                        opportunity:
                            description: Opportunity name (duplicated from the parent opportunity for standalone use).
                            type: str
                        opportunity_url:
                            description: Salesforce URL for the opportunity.
                            type: str
                        subject:
                            description: Task subject.
                            type: str
                        task_url:
                            description: Salesforce URL for the task.
                            type: str
                        date:
                            description: Task date, as displayed in the report (e.g. C(3/11/2026)).
                            type: str
                        comments:
                            description: Task comments/description text.
                            type: str
'''

from datetime import datetime

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.text.converters import to_text

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


def _clean_text(text):
    """Normalize whitespace while preserving intentional line breaks within the text."""
    if not text:
        return ""
    text = text.replace("\xa0", " ")
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(lines).strip()


def _extract_link(cell):
    """Return (text, url) for a table cell, preferring the text/href of its first anchor."""
    if cell is None:
        return "", ""
    anchor = cell.find("a")
    if anchor is not None:
        return _clean_text(anchor.get_text()), anchor.get("href", "")
    return _clean_text(cell.get_text()), ""


def _parse_date(date_str):
    """Parse report date strings like '3/11/2026' into datetime for sorting."""
    if not date_str:
        return datetime.min
    for fmt in ("%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return datetime.min


def _latest_task_date(opportunity):
    """Return the most recent task date for an opportunity, or datetime.min if none."""
    tasks = opportunity.get("tasks") or []
    if not tasks:
        return datetime.min
    return max(_parse_date(task.get("date")) for task in tasks)


def _sort_accounts(accounts):
    """Sort tasks (date desc) within each opp, then opps (latest task date desc) within each account."""
    for account in accounts:
        for opportunity in account["opportunities"]:
            opportunity["tasks"].sort(key=lambda task: _parse_date(task.get("date")), reverse=True)
        account["opportunities"].sort(key=_latest_task_date, reverse=True)
    return accounts


def parse_sf_tasks(html_content):
    """Parse a Salesforce report HTML export into a list of account/opportunity/task groups."""
    if not HAS_BS4:
        raise AnsibleFilterError(
            "The parse_sf_tasks filter requires the 'beautifulsoup4' Python package. "
            "Install it with: pip install beautifulsoup4"
        )

    if not html_content:
        return []

    soup = BeautifulSoup(to_text(html_content), "html.parser")
    table = soup.find("table", class_="reportTable")
    if table is None:
        raise AnsibleFilterError("Could not find a Salesforce 'reportTable' table in the provided HTML.")

    tbody = table.find("tbody") or table

    accounts = []
    current_account = None
    current_opportunity = None

    for row in tbody.find_all("tr", recursive=False):
        if "dataRow" not in row.get("class", []):
            continue

        for header in row.find_all("th", recursive=False):
            header_classes = header.get("class", [])
            name, url = _extract_link(header)

            if "grouping0" in header_classes:
                current_account = {
                    "account": name,
                    "account_url": url,
                    "opportunities": [],
                }
                accounts.append(current_account)
                current_opportunity = None
            elif "grouping1" in header_classes:
                if current_account is None:
                    raise AnsibleFilterError(
                        "Encountered an opportunity grouping cell before any account grouping cell."
                    )
                current_opportunity = {
                    "opportunity": name,
                    "opportunity_url": url,
                    "tasks": [],
                }
                current_account["opportunities"].append(current_opportunity)

        if current_account is None or current_opportunity is None:
            raise AnsibleFilterError("Encountered a task row without an active account/opportunity context.")

        cells = row.find_all("td", recursive=False)
        if len(cells) < 3:
            continue

        subject, subject_url = _extract_link(cells[0])
        date = _clean_text(cells[1].get_text())
        comments = _clean_text(cells[2].get_text())

        current_opportunity["tasks"].append(
            {
                "account": current_account["account"],
                "account_url": current_account["account_url"],
                "opportunity": current_opportunity["opportunity"],
                "opportunity_url": current_opportunity["opportunity_url"],
                "subject": subject,
                "task_url": subject_url,
                "date": date,
                "comments": comments,
            }
        )

    return _sort_accounts(accounts)


class FilterModule:
    """Ansible core jinja2 filters for parsing Salesforce report HTML."""

    def filters(self):
        return {
            "parse_sf_tasks": parse_sf_tasks,
        }
