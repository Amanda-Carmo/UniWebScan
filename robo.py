# REPOSITÓRIO: https://github.com/4rfel/Robo-Selenium.git
# AUTOR: Rafael dos Santos

import os
from time import sleep, time
from typing import List

import pyautogui
from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        ElementNotInteractableException,
                                        InvalidElementStateException,
                                        NoSuchElementException,
                                        StaleElementReferenceException)

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Robo:
    def __init__(self, options:FirefoxOptions, timeout:float=10, max_attempts:int=3) -> None:
        self.ignored_exceptions = (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException, ElementClickInterceptedException, InvalidElementStateException)
        self.first:bool = True
        self.max_attempts:int = max_attempts
        self.timeout:float = timeout

        self.browser = webdriver.Firefox(options=options)


    def switch_to_iframe(self, by:By, value:str, *, max_attempts:int=None, driver:WebElement=None) -> WebElement:
        self.browser.switch_to.default_content()
        attempts = 0
        max_attempts = self.max_attempts if max_attempts is None else max_attempts
        driver = self.browser if driver is None else driver
        while attempts < max_attempts:
            try:
                iframe = self.wait_until_find(by, value, driver=driver)
                self.browser.switch_to.frame(iframe)
                return iframe
            except self.ignored_exceptions:
                attempts += 1
                sleep(1)
        raise ValueError(f"Elemento não encontrado: {by} {value}")

    def wait_until_element_text_is(self, by:By, value:str, text, *, max_attempts:int=None, driver:WebElement=None) -> WebElement:
        if isinstance(text, str):
            texts = [text]
        else:
            texts = text
        attempts = 0
        max_attempts = self.max_attempts if max_attempts is None else max_attempts
        driver = self.browser if driver is None else driver
        while attempts < max_attempts:
            try:
                element = self.wait_until_find(by, value, driver=driver)
                if not element:
                    attempts += 1
                    continue
                if element.text in texts:
                    return element
            except self.ignored_exceptions:
                attempts += 1
                sleep(1)
        raise ValueError(f"Elemento não encontrado: {by} {value}")

    def wait_until_element_text_is_not(self, by:By, value:str, text, *, max_attempts:int=None, driver:WebElement=None) -> WebElement:
        if isinstance(text, str):
            texts = [text]
        else:
            texts = text
        attempts = 0
        max_attempts = self.max_attempts if max_attempts is None else max_attempts
        driver = self.browser if driver is None else driver

        while attempts < max_attempts:
            try:
                element = self.wait_until_find(by, value, driver=driver)
                if not element:
                    attempts += 1
                    continue
                if element.text not in texts:
                    return element
            except self.ignored_exceptions:
                attempts += 1
                sleep(1)
        raise ValueError(f"Elemento não encontrado: {by} {value}")

    def wait_until_element_indexed_text_is(self, by:By, value:str, index, text, *, max_attempts:int=None, driver:WebElement=None) -> WebElement:
        if isinstance(text, str):
            texts = [text]
        else:
            texts = text
        attempts = 0
        max_attempts = self.max_attempts if max_attempts is None else max_attempts
        driver = self.browser if driver is None else driver

        while attempts < max_attempts:
            try:
                elements = self.wait_until_find_multiple(by, value, driver=driver)
                if not elements or len(elements) <= index:
                    attempts += 1
                    continue
                if elements[index].text in texts:
                    return elements[index]
            except self.ignored_exceptions:
                attempts += 1
                sleep(1)
        raise ValueError(f"Elemento não encontrado: {by} {value}")

    def wait_until_element_indexed_text_is_not(self, by:By, value:str, index, text, *, max_attempts:int=None, driver:WebElement=None) -> WebElement:
        if isinstance(text, str):
            texts = [text]
        else:
            texts = text
        attempts = 0
        max_attempts = self.max_attempts if max_attempts is None else max_attempts
        driver = self.browser if driver is None else driver

        while attempts < max_attempts:
            try:
                elements = self.wait_until_find_multiple(by, value, driver=driver)
                if not elements or len(elements) <= index:
                    attempts += 1
                    continue
                if elements[index].text not in texts:
                    return elements[index]
            except self.ignored_exceptions:
                attempts += 1
                sleep(1)
        raise ValueError(f"Elemento não encontrado: {by} {value}")

    def wait_until_element_exists(self, by:By, value:str, *, max_attempts:int=None, driver:WebElement=None) -> WebElement:
        attempts = 0
        max_attempts = self.max_attempts if max_attempts is None else max_attempts
        driver = self.browser if driver is None else driver
        while attempts < max_attempts:
            try:
                pyautogui.moveRel(0, 1, duration = 0.1)
                # sleep(0.1)
                pyautogui.moveRel(0, -1, duration = 0.1)
                element = self.wait_until_find(by, value, driver=driver)
                if not element:
                    attempts += 1
                    continue
                return element
            except self.ignored_exceptions:
                attempts += 1
                sleep(1)
        raise ValueError(f"Elemento não encontrado: {by} {value}")

    def wait_until_element_not_exists(self, by:By, value:str, *, max_attempts:int=None, driver:WebElement=None) -> WebElement:
        attempts = 0
        max_attempts = self.max_attempts if max_attempts is None else max_attempts
        driver = self.browser if driver is None else driver
        prev_element = None
        while attempts < max_attempts:
            try:
                pyautogui.moveRel(0, 1, duration = 0.1)
                # sleep(0.1)
                pyautogui.moveRel(0, -1, duration = 0.1)
                element = self.wait_until_find(by, value, driver=driver)
                if not element:
                    attempts += 1
                    return element
                else:
                    if prev_element != element and prev_element != None:
                        return element
                    prev_element = element
            except self.ignored_exceptions:
                attempts += 1
                sleep(1)
        raise ValueError(f"Elemento não encontrado: {by} {value}")


    def wait_until_find(self, by:By, value:str, *, timeout:float=None, driver:WebElement=None) -> WebElement:
        timeout = self.timeout if timeout is None else timeout
        driver = self.browser if driver is None else driver
        try:
            element = WebDriverWait(driver, timeout, ignored_exceptions=self.ignored_exceptions).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except:
            return False

    def wait_until_find_click(self, by:By, value:str, *, max_attempts:int=None, driver:WebElement=None) -> WebElement:
        attempts = 0
        max_attempts = self.max_attempts if max_attempts is None else max_attempts
        driver = self.browser if driver is None else driver
        while attempts < max_attempts:
            try:
                ok = self.wait_until_find(by, value, driver=driver)
                if not ok:
                    continue
                ok.click()
                return ok
            except self.ignored_exceptions:
                attempts += 1
                sleep(1)
        raise ValueError(f"Elemento não encontrado: {by} {value}")

    def wait_until_find_double_click(self, by:By, value:str, *, max_attempts:int=None, driver:WebElement=None) -> WebElement:
        attempts = 0
        max_attempts = self.max_attempts if max_attempts is None else max_attempts
        driver = self.browser if driver is None else driver
        while attempts < max_attempts:
            try:
                ok = self.wait_until_find(by, value, driver=driver)
                if not ok:
                    continue
                ActionChains(driver).double_click(ok).perform()
                return ok
            except self.ignored_exceptions:
                attempts += 1
                sleep(1)
        raise ValueError(f"Elemento não encontrado: {by} {value}")

    def wait_until_find_send_keys(self, by:By, value:str, keys:str, *, max_attempts:int=None, driver:WebElement=None) -> WebElement:
        attempts = 0
        max_attempts = self.max_attempts if max_attempts is None else max_attempts
        driver = self.browser if driver is None else driver

        while attempts < max_attempts:
            try:
                text = self.wait_until_find(by, value, driver=driver)
                if not text:
                    continue
                text.clear()
                text.send_keys(keys)
                return text
            except self.ignored_exceptions:
                attempts += 1
                sleep(1)
        raise ValueError(f"Elemento não encontrado: {by} {value}")

    def wait_until_find_multiple(self, by:By, value:str, timeout:float=None, driver:WebElement=None) -> List[WebElement]:
        timeout = self.timeout if timeout is None else timeout
        driver = self.browser if driver is None else driver

        try:
            elements = WebDriverWait(driver, timeout, ignored_exceptions=self.ignored_exceptions).until(
                EC.presence_of_all_elements_located((by, value))
            )
            return elements
        except:
            return False

    def wait_until_find_multiple_click(self, by:By, value:str, index:int, *, max_attempts:int=None, driver:WebElement=None) -> List[WebElement]:
        attempts = 0
        max_attempts = self.max_attempts if max_attempts is None else max_attempts
        driver = self.browser if driver is None else driver

        while attempts < max_attempts:
            try:
                elements = self.wait_until_find_multiple(by, value, driver=driver)
                if not elements or len(elements) <= index:
                    continue
                elements[index].click()
                return elements
            except self.ignored_exceptions:
                attempts += 1
                sleep(1)
        raise ValueError(f"Elemento não encontrado: {by} {value}")

    def wait_until_find_multiple_double_click(self, by:By, value:str, index:int, *, max_attempts:int=None, driver:WebElement=None) -> List[WebElement]:
        attempts = 0
        max_attempts = self.max_attempts if max_attempts is None else max_attempts
        driver = self.browser if driver is None else driver

        while attempts < max_attempts:
            try:
                elements = self.wait_until_find_multiple(by, value, driver=driver)
                if not elements or len(elements) <= index:
                    continue
                ActionChains(driver).double_click(elements[index]).perform()
                return elements
            except self.ignored_exceptions:
                attempts += 1
                sleep(1)
        raise ValueError(f"Elemento não encontrado: {by} {value}")

    def wait_until_find_multiple_send_keys(self, by:By, value:str, index:int, keys:str, *, max_attempts:int=None, driver:WebElement=None) -> List[WebElement]:
        attempts = 0
        max_attempts = self.max_attempts if max_attempts is None else max_attempts
        driver = self.browser if driver is None else driver

        while attempts < max_attempts:
            try:
                text = self.wait_until_find_multiple(by, value, driver=driver)[index]
                if not text:
                    continue
                text.clear()
                text.send_keys(keys)
                return text
            except self.ignored_exceptions:
                attempts += 1
                sleep(1)
        raise ValueError(f"Elemento não encontrado: {by} {value}")

    def go_to_url(self, url:str, *, timeout:float=3, max_tries:int=3):
        self.browser.get(url)
        t = time()
        tries = 0
        while True:
            if self.browser.execute_script("return document.readyState") == "complete":
                return
            if time() - t > timeout:
                self.browser.execute_script("location.reload(true);")
                tries += 1
            if tries < max_tries:
                raise ValueError(f"Não foi possível acessar a url, url desejada: {url}  url atual: {self.browser.current_url}")

    def wait_until_text_click(self, by:By, value:str, text:str, *, timeout:float=None, max_attempts:int=None, driver:WebElement=None):
        found = False
        timeout = self.timeout if timeout is None else timeout
        driver = self.browser if driver is None else driver
        max_attempts = self.max_attempts if max_attempts is None else max_attempts
        while not found:
            try:
                elements = self.wait_until_find_multiple(by, value, timeout=timeout, driver=driver)
                for element in elements:
                    if str(element.text).strip() == text:
                        found = True
                        element.click()
                        break
            except self.ignored_exceptions:
                pass


    def quit(self):
        self.browser.quit()