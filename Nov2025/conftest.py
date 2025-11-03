import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os, time
import pytest


@pytest.fixture
def driver():
    opts = Options()
    # opts.add_argument("--headless=new")  # uncomment if you don’t want Chrome to open
    opts.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    yield driver
    driver.quit()




import os, time, pytest

def save_ss(driver, item, folder="screenshots"):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{item.name}_{int(time.time())}.png")
    driver.save_screenshot(path)
    print(f"\n📸 {path}")
    return path

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("driver")
        if driver:
            try:
                save_ss(driver, item)
            except Exception as e:
                print(f"\n⚠️ screenshot failed: {e}")
