from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class HomePage:
    URL = "https://www.flipkart.com/"

    # Use multiple product title selectors (Flipkart has different templates)
    RESULTS_CONTAINER = (By.CSS_SELECTOR, "div._1YokD2._3Mn1Gg")
    NAME_BIG_TILE = (By.CSS_SELECTOR, "div._4rR01T")   # e.g., mobiles
    NAME_SMALL_TILE = (By.CSS_SELECTOR, "a.s1Q9rs")    # e.g., accessories
    NAME_FASHION   = (By.CSS_SELECTOR, "a.IRpwTa")     # e.g., fashion

    # Prefer NAME locator (more stable than placeholder text)
    SEARCH_LOCATORS = [
        (By.NAME, "q"),
        (By.CSS_SELECTOR, "input[title*='Search' i]"),
        (By.CSS_SELECTOR, "form[action*='search'] input[type='text']"),
    ]

    def __init__(self, driver, timeout=30):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self):
        self.driver.get(self.URL)
        return self

    def _get_search_box(self):
        # First clickable/visible search box wins
        last_err = None
        for loc in self.SEARCH_LOCATORS:
            try:
                el = self.wait.until(EC.visibility_of_element_located(loc))
                # Prefer interactable
                try:
                    self.wait.until(EC.element_to_be_clickable(loc))
                except Exception:
                    pass
                return el
            except Exception as e:
                last_err = e
        raise last_err or RuntimeError("Search box not found")

    def _results_visible(self):
        # Any of the result name patterns present?
        try:
            for loc in (self.NAME_BIG_TILE, self.NAME_SMALL_TILE, self.NAME_FASHION):
                els = self.driver.find_elements(*loc)
                if any((e.text or "").strip() for e in els):
                    return True
            # fallback: main results container exists
            return len(self.driver.find_elements(*self.RESULTS_CONTAINER)) > 0
        except Exception:
            return False

    def search(self, query: str) -> bool:
        box = self._get_search_box()

        # Click, type, enter (with fallbacks)
        try:
            box.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", box)

        try:
            box.clear()
        except Exception:
            pass

        try:
            box.send_keys(query)
            box.send_keys(Keys.ENTER)
        except Exception:
            # JS fallback to set value then submit form
            self.driver.execute_script("arguments[0].value = arguments[1];", box, query)
            try:
                box.send_keys(Keys.RETURN)
            except Exception:
                self.driver.execute_script("arguments[0].form && arguments[0].form.submit();", box)

        # Build a robust wait: URL change OR results visible OR title reflects token
        token = next((t for t in query.split() if len(t) >= 3), query.split()[0]).lower()

        def any_success(drv):
            url = (drv.current_url or "").lower()
            title = (drv.title or "").lower()
            if "search?q=" in url:
                return True
            if token in title:
                return True
            if self._results_visible():
                return True
            return False

        self.wait.until(any_success)

        # Final success check to return a boolean (so your assert works)
        url = (self.driver.current_url or "").lower()
        title = (self.driver.title or "").lower()
        return "search?q=" in url or token in title or self._results_visible()

