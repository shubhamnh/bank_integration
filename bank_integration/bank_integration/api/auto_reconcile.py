# -*- coding: utf-8 -*-
# Copyright (c) 2018, Resilient Tech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import csv
import os
from datetime import datetime, timedelta

def read_csv(file_path):
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]

def reconcile_with_payment_entries(transaction, account):
    transaction = dict(transaction)

    filters = {
        "reference_no": transaction["reference_number"].lstrip("0"),
        "reference_date": [
            (datetime.strptime(transaction["date"], "%Y-%m-%d") - timedelta(days=7)).strftime("%Y-%m-%d"),
            (datetime.strptime(transaction["date"], "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d"),
        ],
        "clearance_date": "",
    }

    if float(transaction["withdrawal"]) > 0:
        filters["paid_from"] = account
        filters["paid_amount"] = float(transaction["withdrawal"])
    elif float(transaction["deposit"]) > 0:
        filters["paid_to"] = account
        filters["paid_amount"] = float(transaction["deposit"])

    payment_entries = read_csv('payment_entries.csv')

    matching_entries = [
        entry for entry in payment_entries
        if all(filters[key] == entry[key] for key in filters)
    ]

    if len(matching_entries) != 1:
        return 0

    transaction["payment_entries"] = [
        {
            "payment_document": "Payment Entry",
            "payment_entry": matching_entries[0]["name"],
            "allocated_amount": matching_entries[0]["paid_amount"],
        }
    ]

    return 1

def reconcile_with_journal_entries(transaction, account):
    journal_entries = read_csv('journal_entries.csv')

    matching_entries = [
        entry for entry in journal_entries
        if entry["cheque_no"].lstrip("0") == transaction["reference_number"].lstrip("0")
        and (datetime.strptime(entry["cheque_date"], "%Y-%m-%d") - timedelta(days=7)).strftime("%Y-%m-%d") <= transaction["date"] <= (datetime.strptime(entry["cheque_date"], "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        and entry["clearance_date"] == ""
    ]

    for journal_entry in matching_entries:
        journal_entry_accounts = read_csv('journal_entry_accounts.csv')
        matching_accounts = [
            account_entry for account_entry in journal_entry_accounts
            if account_entry["parenttype"] == journal_entry["doctype"]
            and account_entry["parent"] == journal_entry["name"]
            and account_entry["account"] == account
            and (
                (float(transaction["withdrawal"]) > 0 and float(account_entry["credit_in_account_currency"]) == float(transaction["withdrawal"]))
                or (float(transaction["deposit"]) > 0 and float(account_entry["debit_in_account_currency"]) == float(transaction["deposit"]))
            )
        ]

        if not matching_accounts:
            continue

        transaction["payment_entries"] = [
            {
                "payment_document": "Journal Entry",
                "payment_entry": journal_entry["name"],
                "allocated_amount": float(transaction["withdrawal"]) if float(transaction["withdrawal"]) > 0 else float(transaction["deposit"]),
            }
        ]

        return 1
    return 0

def reconcile_transactions(uid, bank_account):
    account = bank_account
    transactions = read_csv('bank_transactions.csv')

    transactions = [
        transaction for transaction in transactions
        if transaction["docstatus"] == "1"
        and float(transaction["unallocated_amount"]) > 0
        and transaction["bank_account"] == bank_account
        and transaction["reference_number"] != ""
    ]

    count = 0

    for transaction in transactions:
        if reconcile_with_payment_entries(transaction, account):
            count += 1
        elif reconcile_with_journal_entries(transaction, account):
            count += 1

    print(f"Reconciled {count} transactions.")
