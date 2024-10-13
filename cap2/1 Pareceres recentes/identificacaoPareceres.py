from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import math
import time

servico = Service(ChromeDriverManager().install())
navegador = webdriver.Chrome(service=servico)

estados = ['AC - Acre', 'AL - Alagoas', 'AP - Amapá', 'AM - Amazonas', 'CE - Ceará', 'DF - Distrito Federal',
           'MA - Maranhão', 'MG - Minas Gerais', 'PA - Pará', 'PB - Paraíba', 'PE - Pernambuco', 'PI - Piauí',
           'RN - Rio Grande do Norte', 'RO - Rondônia', 'RR - Roraima', 'SC - Santa Catarina', 'TO - Tocantins',
           'ES - Espírito Santo', 'GO - Goiás', 'PR - Paraná', 'SE - Sergipe', 'RJ - Rio de Janeiro', 'BA - Bahia',
           'MS - Mato Grosso do Sul', 'MT - Mato Grosso', 'RS - Rio Grande do Sul', 'SP - São Paulo', 'Nacional']

option_names = ['BA - Bahia', 'RS - Rio Grande do Sul', 'Nacional']

for option_name in option_names:
    info_resultados = []
    
    print(option_name)
    navegador.get("https://www.cnj.jus.br/e-natjus/pesquisaPublica.php")
    
    navegador.find_element('xpath', '//*[@id="frmPesquisa"]/div[5]/div[5]/div/span/span[1]/span/span[2]/b').click()
    options2 = WebDriverWait(navegador, 120).until(
        EC.visibility_of_all_elements_located((By.XPATH, '//ul[@id="select2-txtNatResponsavel-results"]/li'))
    )
    
    for option in options2:
        if option.text == option_name:
            option.click()
            break
    
    navegador.find_element('xpath', '/html/body/div[1]/div[1]/form/div[4]/div[2]/div/select').click()
    navegador.find_element('xpath', '//*[@id="selTipoTecnologia"]/option[2]').click()
    navegador.find_element('xpath', '//*[@id="btnPesquisar"]').click()
    
    try:
        element = WebDriverWait(navegador, 300).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="resultados"]'))
        )
        html = navegador.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        texto = soup.find('div', id='resultados').find('p').text.strip()
        resultado = re.search(r'de (\d+) resultados', texto)
        numero_resultados = resultado.group(1)
        print(numero_resultados)
        
    except NoSuchElementException:
        pass
    
    numero_maximo_paginas = math.ceil(int(numero_resultados)/50)
    
    if numero_maximo_paginas > 30:
        numero_maximo_paginas = 30
    
    max_retries = 3
    
    for pagina_numero in range(1, numero_maximo_paginas + 1):
        retries = 0
        while retries <= max_retries:
            try:
                element = WebDriverWait(navegador, 120).until(
                    EC.visibility_of_element_located((By.XPATH, '//*[@id="tbody"]/tr[1]'))
                )
                break
        
            except TimeoutException:
                retries += 1
                print(f"Timeout na página {pagina_numero}. Tentativa {retries} de {max_retries}.")
                if retries > max_retries:
                    print("Número máximo de retentativas alcançado. Saindo.")
                    break
        
        html = navegador.page_source
        soup = BeautifulSoup(html, 'html.parser')
        lista_de_tr = soup.find('div', attrs={'id': 'resultados'}).find('table').find('tbody').find_all('tr')
        
        for tr in lista_de_tr:
            dados = tr.find_all('td')

            identificacao = dados[0].text
            data = dados[1].text
            tecnologia = dados[2].text
            CID = dados[3].text
            responsavel = dados[4].text
            status = dados[5].text
            links = dados[6].find_all('a')
            linkSite = links[0].get("href").strip()
            linkSite = "https://www.cnj.jus.br/e-natjus/" + linkSite
            linkPDF = links[1].get("href").strip()
            linkPDF = "https://www.cnj.jus.br/e-natjus/" + linkPDF 

            info_resultados.append([option_name, identificacao, data, tecnologia, CID, responsavel, status, linkSite, linkPDF])
            
        if pagina_numero < numero_maximo_paginas:
            numero_pagina = navegador.find_element('xpath', f'//*[@id="pagination"]/nav/ul/li[{pagina_numero + 1}]/a')
            numero_pagina.click()
            time.sleep(1)
        else:
            resultados_df = pd.DataFrame(info_resultados, columns = ['estado', 'id', 'data', 'tecnologia',
                                                                     'CID', 'natjus_responsavel', 'status', 'link_site',
                                                                     'link_PDF'])

            resultados_df.to_excel("enatjus-Medicamentos-" + datetime.now().strftime("%Y%m%d%H%M%S") + "-Estado " +
                                   option_name + ".xlsx", index=False)         
            
            break