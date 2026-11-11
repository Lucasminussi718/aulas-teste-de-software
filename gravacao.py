import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://localhost:8000/login")
    page.get_by_role("textbox", name="Usuário").click()
    page.get_by_role("textbox", name="Usuário").fill("admin")
    page.get_by_role("textbox", name="Senha").click()
    page.get_by_role("textbox", name="Senha").fill("admin123")
    page.get_by_role("textbox", name="Senha").press("Enter")
    page.get_by_role("link", name="Novo título").click()
    page.get_by_role("textbox", name="Descrição").click()
    page.get_by_role("textbox", name="Descrição").fill("teste")
    page.get_by_role("textbox", name="Pessoa (fornecedor ou cliente)").click()
    page.get_by_role("textbox", name="Pessoa (fornecedor ou cliente)").fill("teste")
    page.get_by_role("textbox", name="Valor").click()
    page.get_by_role("textbox", name="Valor").fill("100")
    page.get_by_role("textbox", name="Vencimento").fill("2000-02-02")
    page.get_by_role("button", name="Salvar").click()
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
