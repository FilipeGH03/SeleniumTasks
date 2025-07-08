import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException


def contar_arquivos_downloads():
    pasta_downloads = os.path.expanduser('~/Downloads')
    return len([f for f in os.listdir(pasta_downloads) if os.path.isfile(os.path.join(pasta_downloads, f))])

def esperar_downloads(arquivos_antes):
    while True:
        time.sleep(1)  # Espera 1 segundo entre as verificações
        arquivos_atual = contar_arquivos_downloads()
        if arquivos_atual > arquivos_antes:
            print(f"Download concluído. {arquivos_atual - arquivos_antes} arquivo(s) baixado(s).")
            return
        time.sleep(0.5)


# Inicia o navegador
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)

# Acessa a página da lista de cursos
driver.get("https://sig.ifc.edu.br/sigaa/public/curso/lista.jsf?nivel=G&aba=p-ensino")

# Aguarda o carregamento da tabela com os cursos
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "listagem")))


try:
    # Espera o botão do alerta de cookies ficar clicável
    cookie_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn.btn-primary")))
    cookie_btn.click()
    print("Alerta de cookies fechado.")
except TimeoutException:
    # Se não aparecer, segue tranquilo
    print("Alerta de cookies não apareceu.")

# Coleta os links de cursos (usando o atributo title)
links = driver.find_elements(By.XPATH, "//a[@title='Visualizar Página do Curso']")

# Coleta os HREFs (URL dos cursos) para não perder os elementos depois da navegação
hrefs = [link.get_attribute("href") for link in links]

print(f"Serão acessadas {len(hrefs)} páginas de curso...")

# Visita cada link
for href in hrefs:
    driver.get(href)

    # Espera o menu (onde está o hover) ficar visível
    menu_hover = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "primeiro")))

    # Passa o mouse sobre o elemento
    actions = ActionChains(driver)
    actions.move_to_element(menu_hover).perform()

    # Agora espera o link "Projeto Pedagógico do Curso" aparecer
    ppc_link = wait.until(EC.visibility_of_element_located((By.LINK_TEXT, "Projeto Pedagógico do Curso")))

    # Clica no link
    ppc_link.click()

    # Esperar a página do PPC carregar (ex: pelo subtítulo)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "titulo")))

    # Aguardar o botão de download com a classe "download"
    download_link = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "download")))
    
    # Clicar para iniciar o download
    download_link.click()
    arquivos_antes = contar_arquivos_downloads()
    esperar_downloads(arquivos_antes)
    # Espera opcional para garantir o download (pode ajustar se necessário)

    
# Encerra
driver.quit()
