import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import re
from datetime import datetime
import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from selenium.common.exceptions import TimeoutException
from requests.exceptions import ReadTimeout

df = pd.read_excel('debug1.xlsx')

servico = Service(ChromeDriverManager().install())

navegador = webdriver.Chrome(service=servico)

infos_nota = []
infos_paciente = []

MAX_RETRIES = 5  # Número máximo de tentativas

for link in df['link_site']:
    print(link)
    retries = 0
    success = False
    
    requisicao = requests.get(link, timeout=30)
    requisicao_bs = bs(requisicao.content, features="html.parser")
    nota = requisicao_bs.find('div', id='conteudo')    
    
    nota_id = re.search(r'idNotaTecnica=(\d+)', link).group(1)
    
    tabela1 = nota.find('div', id='formParecer').find_all('div')
    paciente_idade = tabela1[1].find('input')['value'].strip()
    paciente_genero = tabela1[3].find('input', checked=True).find_parent().text.strip()
    paciente_cidade = tabela1[7].find('select', id='txtCidade').find('option').text.strip() if tabela1[7].find('select', id='txtCidade').find('option') else 'NA'
    advogado_nome = tabela1[10].find('input')['value'].strip()
    advogado_numOAB = tabela1[12].find('input')['value'].strip()
    advogado_instituicao = tabela1[14].find('option', selected=True).text.strip() if tabela1[14].find('option', selected=True) else 'NA'
    processo_justica = tabela1[17].find('option', selected=True).text.strip() if tabela1[17].find('option', selected=True) else 'NA'
    processo_vara = tabela1[19].find('input')['value'].strip()
    
    while retries < MAX_RETRIES and not success:  # Modifique a condição do loop while aqui
        try:
            navegador.get(link)
            tabs_selector = "ul.nav.nav-tabs.nav-notatecnica li"
            tabs = navegador.find_elements(By.CSS_SELECTOR, tabs_selector)

            for i in range(len(tabs)):        
                 # Localize o elemento novamente para evitar a referência obsoleta
                tab = navegador.find_elements(By.CSS_SELECTOR, tabs_selector)[i]

                # Mova-se para o elemento e clique nele
                actions = ActionChains(navegador)
                actions.move_to_element(tab).perform()
                tab.click()
                time.sleep(2)

                # Você pode obter o HTML da página inteira
                innerHTML = navegador.execute_script("return document.body.innerHTML")

                # Criar um objeto BeautifulSoup para analisar o código HTML
                soup = bs(innerHTML, 'html.parser')
                tabela2 = soup.find('div', id='formParecer').find_all('div')        

                diagnostico_cid = tabela2[23].find('select', id='txtCid').find('option').text.strip() if tabela2[23].find('select', id='txtCid').find('option') else 'NA'
                diagnostico_nome = tabela2[25].find('input')['value'].strip()

                tecnologia_tipo = tabela2[31].find('option', selected=True).text.strip()
                tecnologia_registro = tabela2[33].find('option', selected=True).text.strip() if tabela2[33].find('option', selected=True) else 'NA'
                tecnologia_comercial = tabela2[37].find('option').text.strip() if tabela2[37].find('option') else "NA"
                tecnologia_principio = tabela2[39].find('option').text.strip() if tabela2[39].find('option') else 'NA'
                tecnologia_viaAdministracao = tabela2[45].find('input')['value'].strip() if tabela2[45].find('input')['value'].strip() else 'NA'
                tecnologia_posologia = tabela2[47].find('textarea').text.strip()
                tecnologia_continuo = tabela2[49].find('option', selected=True).text.strip() if tabela2[49].find('option', selected=True) else 'NA'
                tecnologia_offlabel = tabela2[55].find('option', selected=True).text.strip() if tabela2[55].find('option', selected=True) else 'NA'
                tecnologia_PCDT = tabela2[57].find('option', selected=True).text.strip() if tabela2[57].find('option', selected=True) else 'NA'
                tecnologia_incorporacao = tabela2[59].find('option', selected=True).text.strip() if tabela2[59].find('option', selected=True) else 'NA'
                tecnologia_ondeSUS = tabela2[61].find('option', selected=True).text.strip() if tabela2[61].find('option', selected=True) else 'NA'
                tecnologia_oncologico = tabela2[63].find('option', selected=True).text.strip() if tabela2[63].find('option', selected=True) else 'NA'

                outrasTec_generico = soup.find('div', id='formParecer').find('select', id='selExisteGenerico').find('option', selected=True).text.strip() if soup.find('div', id='formParecer').find('select', id='selExisteGenerico').find('option', selected=True) else 'NA'
                outrasTec_similar = soup.find('div', id='formParecer').find('select', id='selExisteBiossimilar').find('option', selected=True).text.strip() if soup.find('div', id='formParecer').find('select', id='selExisteBiossimilar').find('option', selected=True) else 'NA'

                evidencias_CONITEC = tabela2[126].find('option', selected=True).text.strip() if tabela2[126].find('option', selected=True) else 'NA'

                conclusao_resultado = tabela2[131].find('option', selected=True).text.strip() if tabela2[131].find('option', selected=True) else 'NA'
                conclusao_motivacao = tabela2[133].find('textarea').text.strip()
                conclusao_evidencias = tabela2[138].find('option', selected=True).text.strip() if tabela2[138].find('option', selected=True) else 'NA'
                conclusao_urgencia = tabela2[141].find('option', selected=True).text.strip() if tabela2[141].find('option', selected=True) else 'NA'
                conclusao_anexos = 'https://www.cnj.jus.br/e-natjus/' + tabela2[161].find('a')['href'] if tabela2[161].find('a') else 'NA'

                natjus_responsavel = tabela2[151].find('option', selected=True).text.strip()
                instituicao_responsavel = tabela2[153].find('input')['value'].strip()
                tutoria = tabela2[155].find('input')['value'].strip()
                #outras = tabela2[157].find('textarea').text.strip()

                infos_nota.append([link, natjus_responsavel, nota_id, tecnologia_tipo, conclusao_resultado,
                                   paciente_idade, paciente_genero, paciente_cidade, advogado_instituicao,
                                   processo_justica, processo_vara, diagnostico_cid, diagnostico_nome, tecnologia_tipo, 
                                   tecnologia_registro, tecnologia_comercial, tecnologia_principio, tecnologia_viaAdministracao,
                                   tecnologia_posologia, tecnologia_continuo, tecnologia_offlabel, tecnologia_PCDT,
                                   tecnologia_incorporacao, tecnologia_ondeSUS, tecnologia_oncologico, outrasTec_generico,
                                   outrasTec_similar, evidencias_CONITEC, conclusao_resultado, conclusao_motivacao,
                                   conclusao_evidencias, conclusao_urgencia, conclusao_anexos, instituicao_responsavel,
                                   tutoria])                
                
            success = True  # Se o código for bem-sucedido, defina a variável como True
        except AttributeError:
            retries += 1  # Incremente a contagem de tentativas
            print("Erro AttributeError, tentando novamente...")
            time.sleep(3)
            continue  # Se houver um AttributeError, repita o loop
        except TimeoutException:  # Adicione esta cláusula para lidar com a TimeoutException
            retries += 1
            print("Erro TimeoutException, tentando novamente...")
            time.sleep(3)
            continue
        except ReadTimeout:  # Adicione esta cláusula para lidar com o erro de tempo limite de leitura
            retries += 1
            print("Erro de leitura (ReadTimeout), tentando novamente...")
            time.sleep(3)
            continue

    if retries == MAX_RETRIES:
        print("Número máximo de tentativas atingido para o link:", link)
        # Você pode adicionar código adicional aqui para lidar com a falha

    retries = 0  # Redefina a contagem de tentativas para o próximo link

notas_df = pd.DataFrame(infos_nota)

agora = datetime.now().strftime("%Y%m%d%H%M%S")
nome_arquivo = "debug1-" + agora + ".xlsx"
notas_df.to_excel(nome_arquivo, index=False)