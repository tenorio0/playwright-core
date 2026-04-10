import re
from pathlib import Path

from playwright.sync_api import Locator, Page, expect

from playwright_core.reporting.evidence_collector import capture_step


class BasePage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")

    def locator(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def navigate_to(self, path: str = "") -> None:
        path = path.lstrip("/")
        url = f"{self.base_url}/{path}" if path else self.base_url
        self.page.goto(url)

    def reload(self) -> None:
        self.page.reload()

    def go_back(self) -> None:
        self.page.go_back()

    def go_forward(self) -> None:
        self.page.go_forward()

    def click(self, selector: str) -> None:
        self.locator(selector).click()

    def double_click(self, selector: str) -> None:
        self.locator(selector).dblclick()

    def right_click(self, selector: str) -> None:
        self.locator(selector).click(button="right")

    def fill(self, selector: str, value: str) -> None:
        self.locator(selector).fill(value)

    def clear(self, selector: str) -> None:
        self.locator(selector).clear()

    def type_text(self, selector: str, value: str) -> None:
        self.locator(selector).press_sequentially(value)

    def press_key(self, selector: str, key: str) -> None:
        self.locator(selector).press(key)

    def hover(self, selector: str) -> None:
        self.locator(selector).hover()

    def check(self, selector: str) -> None:
        self.locator(selector).check()

    def uncheck(self, selector: str) -> None:
        self.locator(selector).uncheck()

    def select_option(self, selector: str, value: str) -> None:
        self.locator(selector).select_option(value=value)

    def get_value(self, selector: str) -> str:
        return self.locator(selector).input_value()

    def get_text(self, selector: str) -> str:
        return self.locator(selector).inner_text().strip()

    def get_attribute(self, selector: str, name: str) -> str | None:
        return self.locator(selector).get_attribute(name)

    def count(self, selector: str) -> int:
        return self.locator(selector).count()

    def is_visible(self, selector: str) -> bool:
        return self.locator(selector).is_visible()

    def is_enabled(self, selector: str) -> bool:
        return self.locator(selector).is_enabled()

    def is_checked(self, selector: str) -> bool:
        return self.locator(selector).is_checked()

    def wait_for_visibility(self, selector: str) -> Locator:
        locator = self.locator(selector)
        expect(locator).to_be_visible()
        return locator

    def wait_for_hidden(self, selector: str) -> Locator:
        locator = self.locator(selector)
        expect(locator).to_be_hidden()
        return locator

    def wait_for_enabled(self, selector: str) -> Locator:
        locator = self.locator(selector)
        expect(locator).to_be_enabled()
        return locator

    def scroll_to_element(self, selector: str) -> None:
        self.locator(selector).scroll_into_view_if_needed()

    def scroll_to_top(self) -> None:
        self.page.evaluate("window.scrollTo(0, 0)")

    def scroll_to_bottom(self) -> None:
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    def scroll_by(self, x: int = 0, y: int = 0) -> None:
        self.page.evaluate("(coords) => window.scrollBy(coords.x, coords.y)", {"x": x, "y": y})

    def wait_for_load_state(self, state: str = "load") -> None:
        self.page.wait_for_load_state(state)

    def take_screenshot(self, path: str, full_page: bool = True) -> None:
        screenshot_path = Path(path)
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(path=str(screenshot_path), full_page=full_page)

    def take_evidence(self, description: str, full_page: bool = True) -> str:
        return capture_step(self.page, description=description, full_page=full_page)

    def takeScreenshot(self, description: str, full_page: bool = True) -> str:
        return self.take_evidence(description=description, full_page=full_page)

    def assert_text(self, selector: str, expected_text: str) -> None:
        expect(self.locator(selector)).to_have_text(expected_text)

    def assert_contains_text(self, selector: str, expected_text: str) -> None:
        expect(self.locator(selector)).to_contain_text(expected_text)

    def assert_visible(self, selector: str) -> None:
        expect(self.locator(selector)).to_be_visible()

    def assert_hidden(self, selector: str) -> None:
        expect(self.locator(selector)).to_be_hidden()

    def assert_enabled(self, selector: str) -> None:
        expect(self.locator(selector)).to_be_enabled()

    def assert_url_contains(self, value: str) -> None:
        expect(self.page).to_have_url(re.compile(f".*{re.escape(value)}.*"))

    def assert_title_contains(self, value: str) -> None:
        expect(self.page).to_have_title(re.compile(f".*{re.escape(value)}.*"))
