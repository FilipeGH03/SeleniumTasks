# === IMPORTAÇÕES ===
import os
import re
import csv
import time
import datetime
import unicodedata
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# === CONFIGURAÇÃO DO NAVEGADOR ===
options = Options()
options.add_argument("--start-maximized")
# options.add_argument('--headless') # Descomente esta linha se quiser rodar em background
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

# === FUNÇÕES DE NAVEGAÇÃO E INTERAÇÃO COM A PÁGINA DO CNPq ===

# Abre a página inicial do CNPq
def open_cnpq_homepage():
    print("Acessando a página do CNPq...")
    driver.get("https://buscatextual.cnpq.br/buscatextual/busca.do?metodo=apresentar")

# Marca o checkbox para buscar todos os currículos (sem filtros)
def check_all_curricula():
    try:
        checkbox = wait.until(EC.element_to_be_clickable((By.ID, "buscarDemais")))
        checkbox.click()
        print("Checkbox 'Buscar todos os currículos' marcado.")
    except Exception as e:
        print(f"Erro ao marcar o checkbox: {e}")

# Insere um nome no campo de busca
def enter_search_name(name):
    try:
        campo_nome = wait.until(EC.presence_of_element_located((By.ID, "textoBusca")))
        campo_nome.clear()
        campo_nome.send_keys(name)
        print(f"Nome '{name}' inserido no campo de busca.")
    except Exception as e:
        print(f"Erro ao inserir nome: {e}")

# Clica no botão de buscar
def click_search_button():
    try:
        botao_buscar = wait.until(EC.element_to_be_clickable((By.ID, "botaoBuscaFiltros")))
        botao_buscar.click()
        print("Botão de busca clicado.")
    except Exception as e:
        print(f"Erro ao clicar no botão de busca: {e}")

# Conta o número de resultados retornados pela busca
def count_search_results():
    try:
        resultados = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.resultado ol li")))
        return len(resultados)
    except Exception as e:
        print(f"Erro ao contar resultados: {e}")
        return 0

# Clica no primeiro resultado retornado pela busca
def click_result_by_index(index=0):
    try:
        resultados = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.resultado ol li a")))
        if index < 0 or index >= len(resultados):
            print(f"Índice {index} fora do intervalo de resultados ({len(resultados)} encontrados).")
            return True
        resultado = resultados[index]
        driver.execute_script("arguments[0].scrollIntoView(true);", resultado)
        resultado.click()
        print(f"Resultado {index + 1} clicado.")
    except Exception as e:
        print(f"Erro ao clicar no resultado {index + 1}: {e}")
        return True

# Abre o currículo detalhado via botão
def open_lattes_cv():
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

# Fecha o modal de currículo
def close_modal():
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "moldal-interna")))
        time.sleep(1)
        botao_fechar = wait.until(EC.element_to_be_clickable((By.ID, "idbtnfechar")))
        driver.execute_script("arguments[0].scrollIntoView(true);", botao_fechar)
        time.sleep(0.5)
        botao_fechar.click()
        print("modal fechado.")
    except Exception as e:
        print(f"Erro ao abrir currículo: {e}")

# === FUNÇÕES PARA ACESSO ÀS SEÇÕES DE PRODUÇÃO ===

# Clica no link "Indicadores da Produção"
def click_production_indicators():
    try:
        iframe = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "iframe-modal")))
        driver.switch_to.frame(iframe)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        links = driver.find_elements(By.TAG_NAME, "a")

        def normalize(text):
            return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn').upper().strip()

        alvo = None
        for link in links:
            if "INDICADORES DA PRODUCAO" in normalize(link.text):
                alvo = link
                break

        if not alvo:
            raise Exception("Link 'Indicadores da Produção' não encontrado!")

        driver.execute_script("arguments[0].click();", alvo)
        print("Clique realizado em 'Indicadores da Produção'.")
    except Exception as e:
        print(f"Erro ao clicar em 'Indicadores da Produção': {e}")
    finally:
        driver.switch_to.default_content()

# Clica no link "Diretório de grupos de pesquisa"
def click_search_groups():
    try:
        iframe = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "iframe-modal")))
        driver.switch_to.frame(iframe)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        links = driver.find_elements(By.TAG_NAME, "a")

        def normalize(text):
            return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn').upper().strip()

        alvo = None
        for link in links:
            if "GRUPOS DE PESQUISA" in normalize(link.text):
                alvo = link
                break

        if not alvo:
            raise Exception("Link 'Diretório de grupos de pesquisa' não encontrado!")

        driver.execute_script("arguments[0].click();", alvo)
        print("Clique realizado em 'Diretório de grupos de pesquisa'.")
    except Exception as e:
        print(f"Erro ao clicar em 'Diretório de grupos de pesquisa': {e}")
    finally:
        driver.switch_to.default_content()

#Pega a titulação do currículo
def get_curriculum_title():
    wait = WebDriverWait(driver, 50)
    try:
        # Espera a nova aba abrir
        wait.until(lambda driver: len(driver.window_handles) > 1)
        nova_aba = driver.window_handles[1]
        driver.switch_to.window(nova_aba)

        controls_list = wait.until(lambda driver: driver.find_elements(By.CLASS_NAME, "controls"))
        if len(controls_list) >= 2:
            title = controls_list[1].text.strip()
        else:
            title = ""
        print(f"Titulação encontrada: {title}"),
        driver.quit()
        return title
    except Exception as e:
        print(f"Erro ao obter titulação: {e}")
        driver.quit()
        return "Erro ao obter titulação"


# Seleciona o ano desejado no filtro (ou "Todos")
def select_year_filter(year="Todos"):
    try:
        iframe = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "iframe-modal")))
        driver.switch_to.frame(iframe)

        if driver.find_elements(By.XPATH, "//b[contains(text(), 'Não existem produções cadastradas para este currículo')]"):
            driver.switch_to.default_content()
            return 1

        select_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "select")))
        options = [opt.text.strip() for opt in select_element.find_elements(By.TAG_NAME, "option")]

        if str(year) not in options:
            raise ValueError(f"Ano '{year}' não está entre as opções disponíveis: {options}")

        Select(select_element).select_by_visible_text(str(year))
        print(f"Ano '{year}' selecionado com sucesso.")
    except Exception as e:
        print(f"Erro ao selecionar ano: {e}")
        if str(year).isdigit() and int(year) + 1 <= datetime.datetime.now().year:
            print(f"Selecionando ano {int(year) + 1} por padrão.")
            driver.switch_to.default_content()
            return select_year_filter(str(int(year) + 1))
        else:
            driver.switch_to.default_content()
            return 2
    finally:
        try:
            driver.switch_to.default_content()
        except:
            pass

# === FUNÇÃO PARA EXTRAÇÃO DOS DADOS DE PRODUÇÃO ===

# Extrai os dados da produção agrupando por seção (ex: Produção Bibliográfica)
def extract_sectioned_tables(name):
    results = []
    try:
        iframe = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "iframe-modal")))
        driver.switch_to.frame(iframe)
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "carregando-cont-indicadores")))

        last_height = 0
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        blocos = driver.find_elements(By.CSS_SELECTOR, "div.grafico")
        print(f"Total de blocos encontrados: {len(blocos)}")
        for bloco in blocos:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", bloco)
                time.sleep(0.3)
                try:
                    titulo_secao = bloco.find_element(By.TAG_NAME, "h2").text.strip()
                except:
                    titulo_secao = "Seção Desconhecida"
                print(titulo_secao)
            except Exception as e:
                print(f"Erro ao processar bloco: {e}")
            tabelas = bloco.find_elements(By.CSS_SELECTOR, "table")
            for tabela in tabelas:
                linhas = tabela.find_elements(By.XPATH, ".//tr")
                for linha in linhas:
                    colunas = linha.find_elements(By.XPATH, ".//td")
                    if len(colunas) >= 2:
                        descricao = colunas[0].text.strip()
                        total = colunas[-1].text.strip()
                        if descricao and total:
                            results.append([name, titulo_secao, descricao, total])
        print(f"{len(results)} registros com seções extraídos. Para o nome: {name}")
        return results
    except Exception as e:
        print(f"Erro ao extrair tabelas com seções: {e}")
    finally:
        driver.switch_to.default_content()

# === FUNÇÃO PARA SALVAR RESULTADOS EM CSV ===

# Gera um CSV com os dados extraídos
def generate_csv(data, filename="producao.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["Nome", "Categoria", "Tipo", "Quantidade"])
        for group in data:
            for row in group:
                writer.writerow(row)
    print(f"Arquivo '{filename}' gerado com sucesso!")


def continue_search(name, year, progress_callback, i, total, index):
    if click_result_by_index(index): 
            results.append([[name, 'Usuario não encontrado', '', '']])
            if progress_callback:
                progress_callback(i, total)
            return 1
    click_production_indicators()
    match select_year_filter(year):
        case 1:
            results.append([[name, 'Nenhuma produção encontrada', '', '']])
            if progress_callback:
                progress_callback(i, total)
            return 1
        case 2:    
            results.append([[name, f'Não tem produções pós {year}', '', '']])
            if progress_callback:
                progress_callback(i, total)
            return 1        
    results.append(extract_sectioned_tables(name))
    if progress_callback:
        progress_callback(i, total)

# === FLUXO DE BUSCA PARA LISTA DE NOMES ===
results = []
# Executa a automação completa para uma lista de nomes
def run_search(name_list, year="Todos", progress_callback=None):
    total = len(name_list)
    for i, name in enumerate(name_list, 1):
        os.system('cls' if os.name == 'nt' else 'clear')
        open_cnpq_homepage()
        check_all_curricula()
        enter_search_name(name)
        click_search_button()
        x = count_search_results()
        print(f"Resultados encontrados para '{name}': {x}")
        if x > 1:
            for a in range(0,x):
                if continue_search(name + f" ({a+ 1})", year, progress_callback, i, total, a) == 1:
                    close_modal() 
                    continue    
                close_modal()
        else:
            if continue_search(name, year, progress_callback, i, total, 0) == 1:
                continue    
            # close_modal()
    generate_csv(results)

# === INTERFACE GRÁFICA (TKINTER) ===

# Inicia a busca ao clicar no botão da interface
# def start_gui_search():
#     nomes_texto = entrada_nomes.get("1.0", tk.END).strip()
#     nomes = [nome.strip() for nome in nomes_texto.split("\n") if nome.strip()]
#     if not nomes:
#         messagebox.showwarning("Aviso", "Insira ao menos um nome.")
#         return

#     ano = ano_var.get()
#     status_label.config(text="Iniciando busca...")
#     btn_iniciar.config(state=tk.DISABLED)
#     progresso_bar["value"] = 0
#     progresso_bar["maximum"] = len(nomes)

#     def update_progress(current, total):
#         progresso_bar["value"] = current
#         status_label.config(text=f"Processando {current}/{total}...")

#     def task():
#         try:
#             run_search(nomes, ano, progress_callback=update_progress)
#             status_label.config(text="Busca finalizada com sucesso.")
#         except Exception as e:
#             messagebox.showerror("Erro", str(e))
#             status_label.config(text="Erro durante a busca.")
#         finally:
#             btn_iniciar.config(state=tk.NORMAL)

#     Thread(target=task).start()

# === CONSTRUÇÃO DA JANELA PRINCIPAL ===

# janela = tk.Tk()
# janela.title("Extrator CNPq - Produção Lattes")
# janela.geometry("500x500")

# tk.Label(janela, text="Digite os nomes (um por linha):").pack(pady=5)
# entrada_nomes = scrolledtext.ScrolledText(janela, width=60, height=10)
# entrada_nomes.pack()

# tk.Label(janela, text="Pesquisar as produções a partir do ano:").pack(pady=5)
# ano_var = tk.StringVar(value="Todos")
# anos_opcoes = ["Todos"] + [str(ano) for ano in range(int((datetime.datetime.now()).year)-1, 1998, -1)]
# ano_menu = tk.OptionMenu(janela, ano_var, *anos_opcoes)
# ano_menu.pack()

# btn_iniciar = tk.Button(janela, text="Iniciar Extração", command=start_gui_search)
# btn_iniciar.pack(pady=10)

# progresso_bar = ttk.Progressbar(janela, orient="horizontal", length=400, mode="determinate")
# progresso_bar.pack(pady=10)

# status_label = tk.Label(janela, text="Aguardando...")
# status_label.pack()

# janela.mainloop()
