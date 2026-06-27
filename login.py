from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

BASE_DIR = Path(__file__).resolve().parent
PROFILE_DIR = BASE_DIR / "selenium_chrome_profile"
PAGE_SOURCE_FILE = BASE_DIR / "page_source.html"

options = Options()
options.add_argument(f"--user-data-dir={PROFILE_DIR}")

driver = webdriver.Chrome(options=options)
wait_10s = WebDriverWait(driver, 10)
wait_2m = WebDriverWait(driver, 120)

try:
    driver.get("https://music.163.com")

    wait_10s.until(EC.element_to_be_clickable((By.XPATH, '//a[@data-action="login"]')))
    login_bottom = driver.find_element(By.XPATH, '//a[@data-action="login"]')
    login_bottom.click()
    
    html = driver.page_source
    with open(PAGE_SOURCE_FILE, mode="w", encoding="utf-8") as f:
        f.write(html)
    try:
        wait_2m.until(EC.presence_of_element_located((By.XPATH, '//div[@class="head f-fl f-pr"]')))
        time.sleep(2)
    except TimeoutException:
        print("timeout,please try again later")
    
finally:
    driver.quit()
