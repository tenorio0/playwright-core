import subprocess
import sys
import xml.etree.ElementTree as ET
import os
from pathlib import Path


def _is_enabled(raw_value: str | None) -> bool:
    if raw_value is None:
        return True
    return raw_value.strip().lower() in {"true", "1", "yes"}


def _get_python_command(root: Path) -> str:
    windows_python = root / ".venv" / "Scripts" / "python.exe"
    unix_python = root / ".venv" / "bin" / "python"

    if windows_python.exists():
        return str(windows_python)

    if unix_python.exists():
        return str(unix_python)

    return sys.executable


def _load_execution_options(root: ET.Element) -> dict[str, str]:
    options: dict[str, str] = {}
    execution_node = root.find(".//execution")
    if execution_node is None:
        return options

    headed = execution_node.get("headed")
    slow_mo = execution_node.get("slow_mo")

    if headed is not None:
        options["HEADLESS"] = "false" if _is_enabled(headed) else "true"

    if slow_mo is not None and slow_mo.strip():
        options["SLOW_MO"] = slow_mo.strip()

    return options


def load_test_nodes(xml_path: str | Path) -> list[str]:
    resolved_xml_path = Path(xml_path).resolve()
    root_dir = resolved_xml_path.parent.parent

    if not resolved_xml_path.exists():
        raise FileNotFoundError(f"Execution file not found: {resolved_xml_path}")

    tree = ET.parse(resolved_xml_path)
    root = tree.getroot()

    test_nodes: list[str] = []
    for class_node in root.findall(".//class"):
        if not _is_enabled(class_node.get("enabled")):
            continue

        path = class_node.get("path")
        if not path:
            raise ValueError("Each <class> entry must define 'path'.")

        test_file = root_dir / path
        if not test_file.exists():
            raise FileNotFoundError(f"Configured test file was not found: {test_file}")

        test_nodes.append(path)

    if not test_nodes:
        raise ValueError(f"No enabled test classes were found in {resolved_xml_path.name}.")

    return test_nodes


def run_from_xml(xml_path: str | Path) -> int:
    resolved_xml_path = Path(xml_path).resolve()
    root_dir = resolved_xml_path.parent.parent
    python_command = _get_python_command(root_dir)
    tree = ET.parse(resolved_xml_path)
    root = tree.getroot()
    test_nodes = load_test_nodes(resolved_xml_path)
    execution_options = _load_execution_options(root)
    command = [python_command, "-B", "-m", "pytest", *test_nodes]
    environment = os.environ.copy()
    environment.update(execution_options)

    print("QA TestNG-style runner")
    print(f"Execution file: {resolved_xml_path}")
    print(f"Python: {python_command}")
    if execution_options:
        print("Execution options:")
        for key, value in execution_options.items():
            print(f"- {key}={value}")
    print("Selected tasks:")
    for test_node in test_nodes:
        print(f"- {test_node}")

    completed = subprocess.run(command, cwd=root_dir, env=environment)
    return completed.returncode


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python -m playwright_core.testing.testng_runner <xml_path>")
        return 1

    return run_from_xml(sys.argv[1])


if __name__ == "__main__":
    raise SystemExit(main())
