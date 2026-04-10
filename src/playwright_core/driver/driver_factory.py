from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from playwright_core.config.settings import Settings


class DriverFactory:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    def launch(self) -> Page:
        self._playwright = sync_playwright().start()
        browser_launcher = getattr(self._playwright, self.settings.browser_name, None)

        if browser_launcher is None:
            supported = ("chromium", "firefox", "webkit")
            raise ValueError(
                f"Unsupported browser '{self.settings.browser_name}'. "
                f"Supported browsers: {', '.join(supported)}."
            )

        self._browser = browser_launcher.launch(
            headless=self.settings.headless,
            slow_mo=self.settings.slow_mo,
        )
        self._context = self._browser.new_context(
            viewport={
                "width": self.settings.viewport_width,
                "height": self.settings.viewport_height,
            }
        )
        self._page = self._context.new_page()
        self._page.set_default_timeout(self.settings.default_timeout)
        return self._page

    def get_page(self) -> Page:
        if self._page is None:
            raise RuntimeError("Page is not initialized. Call launch() before accessing the page.")
        return self._page

    def close(self) -> None:
        if self._context:
            self._context.close()
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
