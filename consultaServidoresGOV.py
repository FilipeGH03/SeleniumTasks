from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

# Configura o navegador com janela grande
options = Options()
options.add_argument("--start-maximized")  # Abre em tela cheia

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

# Lista onde os dados coletados serão armazenados
dados_servidores = []

def fechar_banner_cookies():
    try:
        botao_cookies = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Rejeitar cookies opcionais')]")
        ))
        botao_cookies.click()
        print("Banner de cookies fechado.")
    except:
        print("Banner de cookies não apareceu ou já foi fechado.")

def click_consultar():
    try:
        botao_consultar = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Consultar')]")
        ))
        botao_consultar.click()
        print("Botão 'Consultar' clicado.")
    except:
        print("Botão 'Consultar' não apareceu ou não foi encontrado.")

def buscar_servidor_por_nome(nome):
    driver.get("https://portaldatransparencia.gov.br/servidores/consulta")
    if nome == nomes[0]:
        fechar_banner_cookies()

    # Clica no botão "Nome"
    wait.until(EC.element_to_be_clickable((By.ID, "btn-nome-2"))).click()

    # Digita o nome
    campo_nome = wait.until(EC.presence_of_element_located((By.ID, "nome")))
    campo_nome.send_keys(nome)
    campo_nome.send_keys(Keys.ENTER)

    # Se necessário, descomente a linha abaixo:
    # wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Adicionar')]"))).click()

    click_consultar()

    try:
        tabela = wait.until(EC.presence_of_element_located((By.ID, "lista")))
        time.sleep(1)

        linhas = tabela.find_elements(By.CSS_SELECTOR, "tbody tr")

        if not linhas:
            print(f"Nenhum resultado encontrado para: {nome}")
            return

        primeira_linha = linhas[0]
        colunas = primeira_linha.find_elements(By.TAG_NAME, "td")

        if len(colunas) >= 9:
            nome_resultado = colunas[3].text
            orgao = colunas[4].text
            situacao = colunas[6].text
            cargo = colunas[8].text
            print(f"Nome: {nome_resultado}\nÓrgão: {orgao}\nSituação: {situacao}\nCargo: {cargo}")

            # Salva os dados na lista
            dados_servidores.append({
                "Nome buscado": nome,
                "Nome encontrado": nome_resultado,
                "Órgão": orgao,
                "Situação": situacao,
                "Cargo": cargo
            })
        else:
            print("Menos de 9 colunas encontradas.")
            dados_servidores.append({
                "Nome buscado": nome,
                "Nome encontrado": "Dados insuficientes",
                "Órgão": "Dados insuficientes",
                "Situação": "Dados insuficientes",
                "Cargo":  "Dados insuficientes"
            })
    except Exception as e:
        print(f"Erro ao capturar dados: {e}")

    # Limpa o filtro
    try:
        limpar = driver.find_element(By.ID, "btnLimparFiltrosSumario")
        limpar.click()
    except:
        print("Não foi possível limpar os filtros.")

def salvar_csv(nome_arquivo="servidores.csv"):
    with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as csvfile:
        campos = ["Nome buscado", "Nome encontrado", "Órgão", "Situação", "Cargo"]
        writer = csv.DictWriter(csvfile, fieldnames=campos)
        writer.writeheader()
        for linha in dados_servidores:
            writer.writerow(linha)
    print(f"Dados salvos em: {nome_arquivo}")

# ==== Exemplo de uso com vários nomes ====
nomes = ["ADELIA PEREIRA MIRANDA","ADRIANO MAFRA", "ALANA MOTTA GERLACH", "Alexandre Vanzuitta", "ANDREY AUGUSTO ALVES DE OLIVEIRA", "ANTONIO CARLOS ESPIT", "ANTONIO CARLOS PEDROSO", "Caio Cesar Oba Ramos", "Cesar Ademar Hermes", "Claudia Cambruzzi", "Claudia Damo Bertoli", "CLAUDIA REGINA THOMAS BERTUCINI", "Cláudio Adalberto Koller", "Claudio Keske", "DALILA TELES LEAO MARTINS", "Deivis Elton Schickmann Frainer", "DENNIS DONATO PIASECKI", "Deolinda Maria Vieira Filha Carneiro", "EDIVALTRYS INAYVE PISSINATI DE REZENDE", "Fabricio Alves Oliveira", "Fátima Peres Zago De Oliveira", "FIORAVANTE PROVINO BRUN", "Geraldo Jose Rodrigues", "GILMAR SILVÉRIO DA ROCHA", "HENRIQUE SCHETINGER FILHO", "Illyushin Zaak Saraiva", "IZABELLE FERNANDES DA SILVA", "Joao Batista Ferreira Souza Da Silva", "JOAO PAULO ORLANDO","Juarez De Lima", "KARLA PAOLA PICOLI", "Leandro Mondini", "Leila Minatti Andrade", "LEVON BOLIGIAN", "Lidiane Visintin", "LOUISE FARIAS DA SILVEIRA", "Luciano Rosa", "Luiz Leandro Dos Reis Fortaleza", "MARCELO NOTTI MIRANDA", "Marcio Pereira Soares","MARIA AMELIA PELLIZZETTI", "Maria Auxiliadora Bezerra De Araujo", "MARIA FLAVIA SOARES PINTO CARVALHO", "MARIA PAULA SEIBEL BROCK", "Marilane Maria Wolff Paim", "Marina Farias Martins", "MARLON CORDEIRO DOMENECH", "Mauro Bittencourt Dos Santos", "Neila De Toledo E Toledo", "Paulo Mafra De Almeida Costa", "Paulo Ricardo Garcia Martins", "RAFAEL BOSSE BRINHOSA", "Regiane Regis Momm", "Robert Lenoch", "Silvana Cony Quinteiro", "SILVIA REGIA CHAVES DE FREITAS SIMOES", "Susana Taule Pinol", "Tiago Luiz Moda", "Uberson Rossa", "VANESSA MICHELS", "Vera Lúcia Freitas Paniz", "VITAL PEREIRA DOS SANTOS JUNIOR" ]


print(len(nomes))
for nome in nomes:
    buscar_servidor_por_nome(nome)

salvar_csv()
driver.quit()
