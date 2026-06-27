from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from lxml import etree
import time
import os
import random

BASE_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = BASE_DIR.parent
HISTORY_DIR = BASE_DIR / "msghistory"
HISTORY_FILE = HISTORY_DIR / "history.txt"
PROFILE_DIR = BASE_DIR / "selenium_chrome_profile"
STEALTH_JS = BASE_DIR / "stealth.min.js"
if not STEALTH_JS.exists():
    STEALTH_JS = WORKSPACE_DIR / "stealth.min.js"

os.makedirs(HISTORY_DIR, exist_ok=True)

options = Options()
options.add_argument(f"--user-data-dir={PROFILE_DIR}")

driver = webdriver.Chrome(options=options)
wait_10s = WebDriverWait(driver, 10)
wait_2m = WebDriverWait(driver, 120)

def write_history():
    print ("start write history")
    f = open(HISTORY_FILE, mode = "w", encoding = "utf-8")
    html = driver.page_source
    xpath = etree.HTML(html)
    history_list = xpath.xpath("/html/body/div[3]/div[2]/div/div/div[1]/div/div")
    for history in history_list:
        try:
            date = history.xpath("./div[1]/text()")[0]
            sender = history.xpath("./div[2]/a/@title")[0]

            # if sender == "origin name":
            #    sender = "new name"
            # if sender == "origin name":
            #    sender = "new name"

            msg = "".join(history.xpath(".//div[@class = 'cnt f-brk']/p//text()"))

            data = date + " " + sender + " " + msg
        except:
            pass
        else:
            f.write(data+'\n')
    f.close()

with open(STEALTH_JS, encoding="utf-8") as f:
    js = f.read()
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js})

try:
    driver.get("https://music.163.com/#/msg/m/private")
    try:
        driver.switch_to.frame("contentFrame")
        wait_10s.until(EC.presence_of_element_located((By.XPATH, "//*[normalize-space(text())='请用你的云音乐账号登录']")))
    except TimeoutException:
        try:
            wait_2m.until(EC.element_to_be_clickable((By.XPATH, "//*[normalize-space(text())='查看更多消息']")))
        except TimeoutException:
            print ("please select the friend you want to get message with him")
        else:
            moremsg = driver.find_element(By.XPATH, "//*[normalize-space(text())='查看更多消息']")
            moremsg.click()
            time.sleep(2)
            scroll_element = driver.find_element(By.XPATH, "//div[@class = 'n-chat u-scroll1 j-flag']")
            page_source_private = " "
            driver.execute_script("arguments[0].scrollTop += -2000", scroll_element)
            time.sleep(0.1)
            while driver.page_source != page_source_private:
                page_source_private = driver.page_source
                driver.execute_script("arguments[0].scrollTop += -2000", scroll_element)
                refresh_time = 0
                while driver.page_source == page_source_private and refresh_time <=15:
                    time.sleep(0.5)
                    refresh_time += 0.5
                time.sleep(random.uniform(0.1, 0.2))
            write_history()
            print ("success")
    else:
        print("please run login.py to login first,then run this program")

    time.sleep(2)
finally:
    driver.quit()
