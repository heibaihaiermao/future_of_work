from playwright.sync_api import sync_playwright

def login_and_save_state():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://psjobs-emploisfp.psc-cfp.gc.ca/")

        input("Login + MFA manually, then press ENTER...")

        context.storage_state(path="storage_state.json")
        browser.close()

login_and_save_state()