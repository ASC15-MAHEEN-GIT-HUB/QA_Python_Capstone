
import pytest
from pages.home_page import HomePage

@pytest.mark.parametrize("query", ["iphone 15", "laptop bag"])
def test_search_feature(query, driver):
    page = HomePage(driver).open()

    # Try searching
    result = page.search(query)

    # Debug info — prints always, even if it passes
    print("\nDEBUG URL:", driver.current_url)
    print("DEBUG TITLE:", driver.title)

    # Assert that search succeeded
    assert result, f"❌ Search failed for: {query}"
    print(f"✅ Searched successfully: {query}")
