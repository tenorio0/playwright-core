import re
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from pathlib import Path

from playwright.sync_api import Page


@dataclass
class EvidenceContext:
    test_name: str
    safe_test_name: str
    output_dir: Path
    steps: list[dict[str, str]] = field(default_factory=list)
    sequence: int = 0


_CURRENT_EVIDENCE_CONTEXT: ContextVar[EvidenceContext | None] = ContextVar(
    "current_evidence_context",
    default=None,
)


def build_safe_test_name(test_name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", test_name).strip("_") or "test_case"


def start_test_evidence(test_name: str, output_dir: str | Path) -> Token[EvidenceContext | None]:
    context = EvidenceContext(
        test_name=test_name,
        safe_test_name=build_safe_test_name(test_name),
        output_dir=Path(output_dir),
    )
    context.output_dir.mkdir(parents=True, exist_ok=True)
    return _CURRENT_EVIDENCE_CONTEXT.set(context)


def finish_test_evidence(token: Token[EvidenceContext | None]) -> list[dict[str, str]]:
    context = _CURRENT_EVIDENCE_CONTEXT.get()
    _CURRENT_EVIDENCE_CONTEXT.reset(token)
    if context is None:
        return []
    return list(context.steps)


def capture_step(page: Page, description: str, full_page: bool = True) -> str:
    context = _CURRENT_EVIDENCE_CONTEXT.get()
    if context is None:
        raise RuntimeError("No active evidence context was found for the current test.")

    context.sequence += 1
    safe_description = re.sub(r"[^A-Za-z0-9_.-]+", "_", description).strip("_").lower() or "step"
    screenshot_path = context.output_dir / (
        f"{context.safe_test_name}_{context.sequence:02d}_{safe_description}.png"
    )
    page.screenshot(path=str(screenshot_path), full_page=full_page)
    context.steps.append(
        {
            "description": description,
            "screenshot_path": str(screenshot_path),
        }
    )
    return str(screenshot_path)
