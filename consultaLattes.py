### Incompleto ###

import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import time
import csv
import re

options = Options()
options.add_argument("--start-maximized")  # Abre em tela cheia
# options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)


def start():
    # Acessa a página inicial do CNPq
    print("Acessando a página do CNPq...")
    driver.get("https://buscatextual.cnpq.br/buscatextual/busca.do?metodo=apresentar")

def searchAll():
    try:
        # Clica no checkbox para buscar todos os currículos
        checkbox = wait.until(EC.element_to_be_clickable((By.ID, "buscarDemais")))
        checkbox.click()
        print("Checkbox 'Buscar todos os currículos' marcado.")
    except Exception as e:
        print(f"Erro ao marcar o checkbox: {e}")


def insertName(name):
    try:
        # Localiza o campo de texto pelo novo ID e insere o nome
        campo_nome = wait.until(EC.presence_of_element_located((By.ID, "textoBusca")))
        campo_nome.clear()
        campo_nome.send_keys(name)
        print(f"Nome '{name}' inserido no campo de busca.")
    except Exception as e:
        print(f"Erro ao inserir nome: {e}")
        
def click_search():
    try:
        # Clica no botão de busca (ID corrigido para 'botaoBuscaFiltros')
        botao_buscar = wait.until(EC.element_to_be_clickable((By.ID, "botaoBuscaFiltros")))
        botao_buscar.click()
        print("Botão de busca clicado.")
    except Exception as e:
        print(f"Erro ao clicar no botão de busca: {e}")

def click_first_result():
    try:
        # Aguarda o primeiro resultado aparecer e clica no link do nome
        primeiro_resultado = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.resultado ol li a"))
        )
        primeiro_resultado.click()
        print("Primeiro resultado clicado.")
    except Exception as e:
        print(f"Erro ao clicar no primeiro resultado: {e}")        

def openLattes():
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "moldal-interna")))
        time.sleep(1)
        botao_abrir = wait.until(EC.element_to_be_clickable((By.ID, "idbtnabrircurriculo")))

        driver.execute_script("arguments[0].scrollIntoView(true);", botao_abrir)
        time.sleep(0.5)
        botao_abrir.click()

        print("Currículo aberto via fluxo normal.")
    except Exception as e:
        print(f"Erro ao abrir currículo: {e}")

def extrair_producao(nome):
    try:
        # Espera o currículo carregar e tenta encontrar os artigos
        # Tenta encontrar artigos usando diferentes seletores
        artigos_elementos = []
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'artigos-completos')]")))
            artigos_elementos = driver.find_elements(By.XPATH, "//div[contains(@class, 'artigo-completo')]")
        except Exception:
            try:
                artigos_elementos = driver.find_elements(By.XPATH, "//div[contains(@class, 'artigo')]")
            except Exception:
                pass

        print(f"Artigos encontrados: {len(artigos_elementos)}")
        # Exemplo: buscar todos os elementos <span> que contenham textos relevantes em toda a página
        spans_relevantes = driver.find_elements(By.XPATH, "//span[contains(text(), '')]")
        print(f"Total de spans encontrados na página: {len(spans_relevantes)}")
        # Você pode filtrar ou processar esses elementos conforme necessário
        for span in spans_relevantes:
            texto = span.text.strip()
            if texto:
                print(f"Span encontrado: {texto}")
        resultados = []
        for artigo_elem in artigos_elementos:
            spans = artigo_elem.find_elements(By.TAG_NAME, "span")
            texto_spans = " ; ".join([span.text for span in spans if span.text.strip()])
            texto_principal = artigo_elem.text
            texto_completo = f"{texto_spans} ; {texto_principal}" if texto_spans else texto_principal

            if nome.split()[0].upper() in texto_completo.upper():
                resultados.append([nome, texto_completo])

        # Salva os resultados em um arquivo CSV
        with open("producao_lattes.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Nome", "Artigo"])
            if resultados:
                writer.writerows(resultados)
                print(f"{len(resultados)} artigos salvos em producao_lattes.csv")
            else:
                print("Nenhum artigo encontrado para este nome.")
    except Exception as e:
        print(f"Erro ao extrair produção: {e}")

os.system('cls' if os.name == 'nt' else 'clear')
start()
searchAll()
insertName("Diogenes Dezen")
click_search()
click_first_result()
openLattes()
extrair_producao("Diogenes Dezen")

input("Pressione Enter para continuar após marcar a caixa de seleção...")

