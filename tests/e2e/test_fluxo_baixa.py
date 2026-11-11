import random
import uuid
from datetime import date, timedelta

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def pagina(page: Page) -> Page:
    """Página já autenticada."""
    page.goto("/login")
    page.get_by_label("Usuário").fill("admin")
    page.get_by_label("Senha").fill("admin123")
    page.get_by_role("button", name="Entrar").click()
    expect(page.get_by_role("heading", name="Títulos")).to_be_visible()
    return page


def cadastrar_titulo(pagina: Page, vencimento: str = "2030-01-10") -> str:
    """Cadastra um título a receber de 1.000,00 e devolve a descrição única."""
    descricao = f"Mensalidade {uuid.uuid4().hex[:8]}"
    pagina.get_by_role("link", name="Novo título").click()
    pagina.get_by_label("Tipo").select_option(label="A receber")
    pagina.get_by_label("Descrição").fill(descricao)
    pagina.get_by_label("Valor").fill("1000,00")
    pagina.get_by_label("Vencimento").fill(vencimento)
    pagina.get_by_role("button", name="Salvar").click()
    expect(pagina.get_by_role("status")).to_have_text("Título cadastrado.")
    return descricao


def baixar(pagina: Page, descricao: str, valor: str) -> None:
    linha = pagina.get_by_role("row").filter(has_text=descricao)
    linha.get_by_role("link", name="Baixar").click()
    pagina.get_by_label("Valor da baixa").fill(valor)
    pagina.get_by_label("Data do pagamento").fill("2026-11-05")
    pagina.get_by_role("button", name="Registrar baixa").click()


def test_baixa_parcial_deixa_saldo_600_e_status_parcial(pagina: Page):
    descricao = cadastrar_titulo(pagina)

    baixar(pagina, descricao, "400,00")

    expect(pagina.get_by_role("status")).to_contain_text("Baixa registrada")
    pagina.goto("/")  # volta à lista de títulos
    linha = pagina.get_by_role("row").filter(has_text=descricao)
    expect(linha.locator("[data-campo=saldo]")).to_have_text("600.00")
    expect(linha.locator("[data-campo=status]")).to_have_text("parcial")


def test_baixa_parcial_aparece_no_saldo_projetado(pagina: Page):
    # dia aleatório no futuro distante: nenhum outro título cai nele
    dia = (date(2040, 1, 1) + timedelta(days=random.randint(0, 20000))).isoformat()
    descricao = cadastrar_titulo(pagina, vencimento=dia)
    baixar(pagina, descricao, "400,00")
    expect(pagina.get_by_role("status")).to_contain_text("Baixa registrada")

    pagina.get_by_role("link", name="Fluxo de caixa").click()
    pagina.get_by_label("Início").fill(dia)
    pagina.get_by_label("Fim").fill(dia)
    pagina.get_by_role("button", name="Calcular").click()

    expect(pagina.locator("[data-campo=saldo-projetado]")).to_have_text("600.00")


def test_baixa_maior_que_o_saldo_mostra_erro_e_nao_muda_o_saldo(pagina: Page):
    descricao = cadastrar_titulo(pagina)

    baixar(pagina, descricao, "1500,00")

    expect(pagina.get_by_role("alert")).to_have_text(
        "O valor da baixa não pode ser maior que o saldo do título."
    )

    pagina.goto("/")
    linha = pagina.get_by_role("row").filter(has_text=descricao)
    expect(linha.locator("[data-campo=saldo]")).to_have_text("1000.00")
    expect(linha.locator("[data-campo=status]")).to_have_text("aberto")