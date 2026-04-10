import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    base_url: str = os.getenv("BASE_URL", "https://example.com")
    browser_name: str = os.getenv("BROWSER", "chromium")
    headless: bool = os.getenv("HEADLESS", "true").lower() == "true"
    slow_mo: int = int(os.getenv("SLOW_MO", "0"))
    default_timeout: int = int(os.getenv("DEFAULT_TIMEOUT", "10000"))
    viewport_width: int = int(os.getenv("VIEWPORT_WIDTH", "1440"))
    viewport_height: int = int(os.getenv("VIEWPORT_HEIGHT", "900"))
    temp_screenshots_dir: str = os.getenv(
        "TEMP_SCREENSHOTS_DIR",
        "test-results/evidence/.temp-screenshots",
    )
    pdf_reports_dir: str = os.getenv("PDF_REPORTS_DIR", "test-results/evidence/reports")
