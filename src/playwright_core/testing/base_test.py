import pytest
from playwright.sync_api import Page

from playwright_core.config.settings import Settings


class BaseTest:
    page: Page
    settings: Settings

    @pytest.fixture(autouse=True)
    def _inject_common_dependencies(self, page: Page, settings: Settings) -> None:
        self.page = page
        self.settings = settings
