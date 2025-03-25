# -*- coding: utf-8 -*-
# Copyright (c) 2018, Resilient Tech and contributors
# For license information, please see license.txt

import json
import csv

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

def make_payment(docname, uid, data):
    data = json.loads(data)

    payment_entries = read_csv('payment_entries.csv')
    bi_name = next((entry['name'] for entry in payment_entries if entry['account'] == data['from_account']), None)
    if not bi_name:
        raise ValueError("Bank Integration Settings not found for the given account")

    bi_settings = read_csv('bank_integration_settings.csv')
    bi = next((entry for entry in bi_settings if entry['name'] == bi_name), None)
    if not bi:
        raise ValueError("Bank Integration Settings not found")

    data['from_account'] = bi['bank_account_no']

    bank = get_bank_api(bi['bank_name'], bi['username'], bi['password'], doctype="Payment Entry", docname=docname,
        uid=uid, data=data)
