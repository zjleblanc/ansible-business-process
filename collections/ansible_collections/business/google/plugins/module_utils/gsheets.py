# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Zachary LeBlanc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Shared Google Sheets helpers for the business.google collection.

Provides A1-notation range building and value coercion so every module in
this collection that reads or writes Sheets cells behaves consistently.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
import re

COLUMN_LETTER_RE = re.compile(r"^[A-Za-z]+$")


def normalize_column(column):
    """Validate and return an uppercase column letter."""
    column = str(column).strip()
    if not COLUMN_LETTER_RE.match(column):
        raise ValueError(f"invalid column letter: {column}")
    return column.upper()


def quote_sheet(sheet):
    """Quote a worksheet name for A1 notation."""
    escaped = sheet.replace("'", "''")
    return f"'{escaped}'"


def column_range(sheet, column):
    """Return A1 range for an entire column on a worksheet."""
    return f"{quote_sheet(sheet)}!{column}:{column}"


def cell_range(sheet, column, row):
    """Return A1 range for a single cell."""
    return f"{quote_sheet(sheet)}!{column}{row}"


def coerce_cell_value(value):
    """Return a scalar Google Sheets accepts (str, int, float, bool).

    Ansible may pass dict/list for type=raw when the rendered value looks like
    JSON; the API rejects those as struct_value unless serialized to text.
    """
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, default=str, separators=(",", ":"))
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value
    return str(value)
