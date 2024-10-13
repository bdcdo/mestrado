from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import re

servico = Service(ChromeDriverManager().install())
navegador = webdriver.Chrome(service=servico)

estados = ['AC - Acre', 'AL - Alagoas', 'AP - Amapá', 'AM - Amazonas', 'CE - Ceará', 'DF - Distrito Federal',
           'MA - Maranhão', 'MG - Minas Gerais', 'PA - Pará', 'PB - Paraíba', 'PE - Pernambuco', 'PI - Piauí',
           'RN - Rio Grande do Norte', 'RO - Rondônia', 'RR - Roraima', 'SC - Santa Catarina', 'TO - Tocantins',
           'ES - Espírito Santo', 'GO - Goiás', 'PR - Paraná', 'SE - Sergipe', 'RJ - Rio de Janeiro', 'BA - Bahia',
           'MS - Mato Grosso do Sul', 'MT - Mato Grosso', 'RS - Rio Grande do Sul', 'SP - São Paulo', 'Nacional']

option_names = estados

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