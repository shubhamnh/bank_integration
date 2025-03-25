# -*- coding: utf-8 -*-
# Copyright (c) 2018, Resilient Tech and contributors
# For license information, please see license.txt

import csv
import json

def read_csv(file_path):
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]

def get_bank_api(bank_name, *args, **kwargs):
    from bank_integration.bank_integration.api.hdfc_bank_api import HDFCBankAPI
    api_map = {
        "HDFC Bank": HDFCBankAPI,
    }
    return api_map.get(bank_name)(*args, **kwargs)

def get_transactions(uid, from_account):
    bi_settings = read_csv('bank_integration_settings.csv')
    bi = next((entry for entry in bi_settings if entry['bank_account'] == from_account), None)
    if not bi:
        raise ValueError("Bank Integration Settings not found for the given account")

    account_name = next((entry['account_name'] for entry in bi_settings if entry['bank_account'] == from_account), None)
    data = {
        "bank_account": from_account,
        "from_account": account_name,
        "from_account_no": bi['bank_account_no'],
    }

    bank = get_bank_api(
        bi['bank_name'],
        bi['username'],
        bi['password'],
        doctype="Bank Account",
        uid=uid,
        data=data,
    )
