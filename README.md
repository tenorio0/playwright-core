# playwright-core

Reusable Playwright automation core for Python QA projects.

## Install

```bash
pip install "playwright-core @ git+https://github.com/tenorio0/playwright-core.git@main"
```

## Main Modules

- `playwright_core.config`
- `playwright_core.driver`
- `playwright_core.pages`
- `playwright_core.reporting`
- `playwright_core.testing`

## XML Runner

```bash
python -B -m playwright_core.testing.testng_runner automation/testng.xml
```
