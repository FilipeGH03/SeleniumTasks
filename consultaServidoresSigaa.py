from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import time
import csv

# Nomes dos docentes
nomes = ["ADELIA PEREIRA MIRANDA","ADRIANO MAFRA", "ALANA MOTTA GERLACH"
, "Alexandre Vanzuitta", "ANDREY AUGUSTO ALVES DE OLIVEIRA", "ANTONIO CARLOS ESPIT", "ANTONIO CARLOS PEDROSO", "Caio Cesar Oba Ramos", "Cesar Ademar Hermes", "Claudia Cambruzzi", "Claudia Damo Bertoli", "CLAUDIA REGINA THOMAS BERTUCINI", "Cláudio Adalberto Koller", "Claudio Keske", "DALILA TELES LEAO MARTINS", "Deivis Elton Schickmann Frainer", "DENNIS DONATO PIASECKI", "Deolinda Maria Vieira Filha Carneiro", "EDIVALTRYS INAYVE PISSINATI DE REZENDE", "Fabricio Alves Oliveira", "Fátima Peres Zago De Oliveira", "FIORAVANTE PROVINO BRUN", "Geraldo Jose Rodrigues", "GILMAR SILVÉRIO DA ROCHA", "HENRIQUE SCHETINGER FILHO", "Illyushin Zaak Saraiva", "IZABELLE FERNANDES DA SILVA", "Joao Batista Ferreira Souza Da Silva", "JOAO PAULO ORLANDO",
"Juarez De Lima", "KARLA PAOLA PICOLI", "Leandro Mondini", "Leila Minatti Andrade", "LEVON BOLIGIAN", "Lidiane Visintin", "LOUISE FARIAS DA SILVEIRA", "Luciano Rosa", "Luiz Leandro Dos Reis Fortaleza", "MARCELO NOTTI MIRANDA", "Marcio Pereira Soares",
"MARIA AMELIA PELLIZZETTI", "Maria Auxiliadora Bezerra De Araujo", "MARIA FLAVIA SOARES PINTO CARVALHO", "MARIA PAULA SEIBEL BROCK", "Marilane Maria Wolff Paim", "Marina Farias Martins", "MARLON CORDEIRO DOMENECH", "Mauro Bittencourt Dos Santos", "Neila De Toledo E Toledo", "Paulo Mafra De Almeida Costa", "Paulo Ricardo Garcia Martins", "RAFAEL BOSSE BRINHOSA", "Regiane Regis Momm", "Robert Lenoch", "Silvana Cony Quinteiro", "SILVIA REGIA CHAVES DE FREITAS SIMOES", "Susana Taule Pinol", "Tiago Luiz Moda", "Uberson Rossa", "VANESSA MICHELS", "Vera Lúcia Freitas Paniz", "VITAL PEREIRA DOS SANTOS JUNIOR" ]
nomes_não_encontrados = []


# Configurar Selenium
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# options.add_argument('--headless')  # Ative depois que funcionar
options.add_argument('user-agent=Mozilla/5.0')

driver = webdriver.Chrome(options=options)


def extrair_semestres(nome):
    print(f"Buscando por: {nome}")
    url_busca = "https://sig.ifc.edu.br/sigaa/public/docente/busca_docentes.jsf"
    driver.get(url_busca)

    try:
        campo_nome = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "form:nome"))
        )
        campo_nome.clear()
        campo_nome.send_keys(nome)
        campo_nome.send_keys(Keys.RETURN)
    except:
        print("❌ Campo de nome não encontrado.")
        return []

    try:
        link = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "ver página pública"))
        )
        link.click()
    except:
        print("❌ Link 'ver página pública' não encontrado.")
        nomes_não_encontrados.append(nome)
        return []

    try:
        link_disciplinas = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Disciplinas Ministradas"))
        )
        link_disciplinas.click()
        # print(driver.find_element(By.ID, "disciplinas-docente").get_attribute("innerHTML"))
    except:
        print("❌ Aba de disciplinas não encontrada.")
    
        return []


    # Clique em todas as abas de nível de ensino
    abas_desejadas = ["Médio", "Integrado", "Técnico", "Graduação", "Pós-Graduação"]
    semestres = set()

    for nome_aba in abas_desejadas:
        try:
            aba = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, f"//span[contains(@class, 'x-tab-strip-text') and contains(text(), '{nome_aba}')]"))
            )
            driver.execute_script("arguments[0].click();", aba)
            time.sleep(0.5)  # esperar conteúdo carregar
            
            # Coleta real via Selenium, não BeautifulSoup
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#disciplinas-docente .anoPeriodo"))
            )
            periodos = driver.find_elements(By.CSS_SELECTOR, "td.anoPeriodo")
            
            for p in periodos:
                texto = p.text.strip()
                match = re.match(r"^(20[2-9][0-9])[.](1|2)$", texto)
                if match:
                    ano, semestre = match.groups()
                    if int(ano) >= 2023:
                        semestres.add(f"{ano}.{semestre}")

        except:
            print(f"⚠️ Aba '{nome_aba}' não encontrada ou sem conteúdo.")


    return sorted(semestres)

resultados = []


for nome in nomes:
    semestres = extrair_semestres(nome)
    print(f"{nome} ministrou disciplinas nos semestres: {semestres}")
    print("-" * 60)

    status = "Não encontrado" if nome in nomes_não_encontrados else "Encontrado"
    resultados.append({
        "Nome do Docente": nome,
        "Semestres Ministrados": ", ".join(semestres),
        "Status": status
    })

print("📄 Resultados finais:", resultados)

# Salvar no CSV
try:
    with open("docentes_semestres.csv", mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Nome do Docente", "Semestres Ministrados", "Status"])
        writer.writeheader()
        writer.writerows(resultados)
    print("✅ Arquivo 'docentes_semestres.csv' salvo com sucesso.")
except Exception as e:
    print(f"❌ Erro ao salvar o CSV: {e}")
    

driver.quit()
