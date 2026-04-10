import time
import shutil
from pathlib import Path

import pytest
from playwright.sync_api import Page

from playwright_core.config.settings import Settings
from playwright_core.driver.driver_factory import DriverFactory
from playwright_core.reporting.evidence_collector import (
    build_safe_test_name,
    finish_test_evidence,
    start_test_evidence,
)
from playwright_core.reporting.pdf_evidence_report import (
    PdfEvidenceReport,
    build_procedural_report_path,
)


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings()


@pytest.fixture
def driver_factory(settings: Settings) -> DriverFactory:
    factory = DriverFactory(settings)
    factory.launch()
    return factory


@pytest.fixture
def set_up(driver_factory: DriverFactory) -> Page:
    return driver_factory.get_page()


@pytest.fixture
def tear_down(driver_factory: DriverFactory):
    yield
    driver_factory.close()


@pytest.fixture
def page(set_up: Page, tear_down) -> Page:
    yield set_up


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture(autouse=True)
def test_lifecycle(request, page: Page, settings: Settings):
    test_name = request.node.name
    task_name = Path(str(request.node.path)).stem
    temp_screenshots_dir = Path(settings.temp_screenshots_dir) / task_name / build_safe_test_name(test_name)
    start_time = time.perf_counter()
    evidence_token = start_test_evidence(test_name, temp_screenshots_dir)
    print(f"[SETUP] Starting test: {test_name}")
    yield

    duration_seconds = time.perf_counter() - start_time
    test_report = getattr(request.node, "rep_call", None)
    status = "passed"
    error_message = None

    if test_report:
        if test_report.failed:
            status = "failed"
            error_message = str(test_report.longrepr)[:1500]
        elif test_report.skipped:
            status = "skipped"

    evidence_steps = finish_test_evidence(evidence_token)
    if not evidence_steps:
        fallback_path = temp_screenshots_dir / f"{build_safe_test_name(test_name)}_{status}.png"
        fallback_path.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(fallback_path), full_page=True)
        evidence_steps.append(
            {
                "description": "Final page state",
                "screenshot_path": str(fallback_path),
            }
        )

    report_path = build_procedural_report_path(
        reports_dir=settings.pdf_reports_dir,
        task_name=task_name,
        test_name=test_name,
    )
    PdfEvidenceReport(str(report_path)).build(
        [
            {
                "name": test_name,
                "status": status,
                "duration_seconds": duration_seconds,
                "evidence_steps": evidence_steps,
                "error_message": error_message,
            }
        ]
    )

    if temp_screenshots_dir.exists():
        shutil.rmtree(temp_screenshots_dir, ignore_errors=True)

    print(f"[TEARDOWN] Captured {len(evidence_steps)} evidence item(s) for the PDF report.")
    print(f"[REPORT] PDF evidence generated at: {report_path}")
    print(f"[TEARDOWN] Finishing test: {test_name}")
