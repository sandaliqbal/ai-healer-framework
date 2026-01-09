from pathlib import Path
from playwright.sync_api import Page
import os

ARTIFACT_DIR = Path(os.getcwd() + "/test_artifacts")
ARTIFACT_DIR.mkdir(exist_ok=True)


def collect_dom(page: Page, failure_id: str) -> str:
    dom_path = None
    try:
        dom = page.content()
        path = ARTIFACT_DIR / f"{failure_id}_dom.html"
        path.write_text(dom)
        dom_path = str(path)
    except Exception as e:
        print(e)
    return dom_path


def collect_a11y(page: Page, failure_id: str) -> str:
    a11y = None
    page.wait_for_timeout(3000)
    try:
        snapshot = page.locator("body").aria_snapshot()
        path = ARTIFACT_DIR / f"{failure_id}_a11y.yaml"
        with open(path, "w") as f:
            f.write(snapshot)
        a11y = str(path)
    except Exception as e:
        print(e)
    return a11y


def collect_screenshot(page: Page, failure_id: str) -> str:
    scrnshot = None
    try:
        path = ARTIFACT_DIR / f"{failure_id}_screenshot.png"
        page.screenshot(path=str(path))
        scrnshot = str(path)
    except Exception as e:
        print(e)
    return scrnshot
