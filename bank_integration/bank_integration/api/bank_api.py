# -*- coding: utf-8 -*-
# Copyright (c) 2018, Resilient Tech and contributors
# For license information, please see license.txt

import pickle
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By

class BankAPI:
    def __init__(
        self,
        username=None,
        password=None,
        timeout=30,
        logged_in=0,
        doctype=None,
        docname=None,
        uid=None,
        resume=False,
        data=None,
    ):
        self.username = username
        self.password = password
        self.timeout = timeout
        self.logged_in = logged_in
        self.doctype = doctype
        self.docname = docname
        self.uid = uid or self.random_string(7)
        self.cache_key = "bank_" + self.uid
        self.data = data

        if getattr(self, "init"):
            self.init()

        if resume:
            self.resume_session()
        else:
            self.login()

    def login(self):
        pass

    def logout(self):
        pass

    def setup_browser(self):
        self.br = webdriver.Chrome(options=self.get_options(), port=12345)

    def get_options(self):
        options = Options()
        options.add_argument("window-size=990,1200")
        options.add_argument("--headless")
        options.add_experimental_option("w3c", False)
        return options

    def emit_js(self, js):
        pass

    def show_msg(self, msg):
        pass

    def get_resume_info(self):
        return {
            "executor_url": self.br.command_executor._url,
            "session_id": self.br.session_id,
        }

    def resume_session(self):
        cached = self.get_cache(self.cache_key)
        if not cached:
            self.throw("Unable to find session info in cache")

        self.data = cached["data"]
        resume_info = cached["resume_info"]

        self.br = webdriver.Remote(
            command_executor=resume_info["executor_url"], options=self.get_options()
        )
        self.br.close()
        self.br.session_id = resume_info["session_id"]

    def wait_until(self, ec, timeout=None, throw=True):
        try:
            return WebDriverWait(self.br, timeout or self.timeout).until(ec)
        except TimeoutException:
            self.handle_exception(throw)

    def switch_to_frame(self, selector, selector_type="name"):
        self.br.switch_to.default_content()
        self.wait_until(
            EC.frame_to_be_available_and_switch_to_it(
                (getattr(By, selector_type.upper()), selector)
            )
        )

    def get_element(
        self, selector, selector_type="name", timeout=None, throw=True, now=False
    ):
        if not now:
            return self.wait_until(
                EC.visibility_of_element_located(
                    (getattr(By, selector_type.upper()), selector)
                ),
                timeout=timeout,
                throw=throw,
            )
        else:
            try:
                return self.br.find_element(
                    getattr(By, selector_type.upper()), selector
                )
            except NoSuchElementException:
                self.handle_exception(throw, selector)

    def handle_exception(self, throw, selector=None):
        if throw == "ignore":
            pass
        elif throw:
            if not selector:
                self.throw(
                    "Timed out waiting for element to be present", screenshot=True
                )
            else:
                self.throw("Element not found: " + selector)
        else:
            raise

    def throw(self, message, screenshot=False):
        if screenshot:
            self.save_screenshot("payment_error_{}.png".format(self.uid))
        self.logout()
        raise Exception(message)

    def save_for_later(self):
        self.set_cache(
            self.cache_key,
            {"resume_info": self.get_resume_info(), "data": self.data},
        )

    def delete_cache(self):
        self.delete_cache_key(self.cache_key)

    def random_string(self, length):
        import random
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def save_screenshot(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.br.get_screenshot_as_png())

    def get_cache(self, key):
        if os.path.exists(key):
            with open(key, 'rb') as f:
                return pickle.load(f)
        return None

    def set_cache(self, key, value):
        with open(key, 'wb') as f:
            pickle.dump(value, f)

    def delete_cache_key(self, key):
        if os.path.exists(key):
            os.remove(key)

class AnyEC:
    """Use with WebDriverWait to combine expected_conditions
    in an OR.
    """

    def __init__(self, *args):
        self.ecs = args

    def __call__(self, driver):
        driver._found_element = None
        for fn in self.ecs:
            try:
                if fn(driver):
                    element = getattr(fn, "locator", None)
                    if element:
                        driver._found_element = element
                    elif "alert" in str(fn):
                        driver._found_element = "alert"
                    return True
            except:
                pass
