from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import datetime
import time
import requests
from requests.exceptions import RequestException, Timeout
from urllib3.exceptions import ReadTimeoutError
from tenacity import retry, stop_after_attempt, wait_exponential
import re

def clean_text(text):
    # Remove or replace illegal characters
    text = re.sub(r'[\000-\010]|[\013-\014]|[\016-\037]', "", text)
    # Replace other problematic characters
    text = text.replace('\x0b', ' ').replace('\x0c', ' ')
    return text

def save_preview(df):
    # Clean the DataFrame
    for column in df.columns:
        df[column] = df[column].astype(str).apply(clean_text)
    
    # Save to Excel
    try:
        df.to_excel("enatjus-NotaTecnicaCompleta-pareceresUnicos-" + datetime.now().strftime("%Y%m%d%H%M%S") + ".xlsx", index=False)
    except Exception as e:
        print(f"Error saving Excel file: {str(e)}")
        # Fallback to CSV if Excel fails
        csv_filename = "enatjus-NotaTecnicaCompleta-pareceresUnicos-" + datetime.now().strftime("%Y%m%d%H%M%S") + ".csv"
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f"Saved as CSV instead: {csv_filename}")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_page(url):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response
    except (RequestException, Timeout, ReadTimeoutError) as e:
        print(f"Error fetching {url}: {str(e)}. Retrying...")
        raise

if __name__ == '__main__':
    df = pd.read_excel('enatjus-NotaTecnicaCompleta-pareceresUnicos-20241006030332.xlsx')

    # Convert all columns to object type
    for col in df.columns:
        df[col] = df[col].astype(object)

    infos_nota = []

    indice = 7901

    for i in range(indice, len(df)):
        print(i)

        link = df['link_site'][i]
        
        try:
            requisicao = fetch_page(link)
            requisicao_bs = bs(requisicao.content, features="html.parser")
            nota = requisicao_bs.find('div', id='conteudo')
            
            if nota.find('table'):
                tabela1 = nota.find('table').find('tbody').find_all('td')
            else:
                continue
                
            df.at[i, 'nota_id'] = clean_text(tabela1[0].get_text().strip())
            df.at[i, 'tecnologia'] = clean_text(tabela1[1].get_text().strip())
            df.at[i, 'conclusao'] = clean_text(tabela1[2].get_text().strip())
            df.at[i, 'status'] = clean_text(tabela1[3].get_text().strip())
            
            tabela2 = nota.find('div', id='formParecer').find_all('div')
            
            df.at[i, 'paciente_idade'] = clean_text(tabela2[1].find('input')['value'].strip())
            df.at[i, 'paciente_genero'] = clean_text(tabela2[3].find('input', checked=True).find_parent().text.strip())
            df.at[i, 'paciente_cidade'] = clean_text(tabela2[7].find('select', id='txtCidade').find('option').text.strip())
            df.at[i, 'advogado_nome'] = clean_text(tabela2[10].find('input')['value'].strip())
            df.at[i, 'advogado_numOAB'] = clean_text(tabela2[12].find('input')['value'].strip())
            df.at[i, 'advogado_instituicao'] = clean_text(tabela2[14].find('option', selected=True).text.strip() if tabela2[14].find('option', selected=True) else 'NA')
            df.at[i, 'processo_justica'] = clean_text(tabela2[17].find('option', selected=True).text.strip() if tabela2[17].find('option', selected=True) else 'NA')
            df.at[i, 'processo_vara'] = clean_text(tabela2[19].find('input')['value'].strip())
            df.at[i, 'diagnostico_cid'] = clean_text(tabela2[23].find('select', id='txtCid').find('option').text.strip() if tabela2[23].find('select', id='txtCid').find('option') else 'NA')
            df.at[i, 'diagnostico_nome'] = clean_text(tabela2[25].find('input')['value'].strip())
            df.at[i, 'tecnologia_tipo'] = clean_text(tabela2[31].find('option', selected=True).text.strip())
            df.at[i, 'tecnologia_registro'] = clean_text(tabela2[33].find('option', selected=True).text.strip() if tabela2[33].find('option', selected=True) else 'NA')
            df.at[i, 'tecnologia_comercial'] = clean_text(tabela2[37].find('option').text.strip() if tabela2[37].find('option') else "NA")
            df.at[i, 'tecnologia_principio'] = clean_text(tabela2[39].find('option').text.strip() if tabela2[39].find('option') else 'NA')
            df.at[i, 'tecnologia_viaAdministracao'] = clean_text(tabela2[45].find('input')['value'].strip() if tabela2[45].find('input')['value'].strip() else 'NA')
            df.at[i, 'tecnologia_posologia'] = clean_text(tabela2[47].find('textarea').text.strip())
            df.at[i, 'tecnologia_continuo'] = clean_text(tabela2[49].find('option', selected=True).text.strip() if tabela2[49].find('option', selected=True) else 'NA')
            df.at[i, 'tecnologia_offlabel'] = clean_text(tabela2[55].find('option', selected=True).text.strip() if tabela2[55].find('option', selected=True) else 'NA')
            df.at[i, 'tecnologia_PCDT'] = clean_text(tabela2[57].find('option', selected=True).text.strip() if tabela2[57].find('option', selected=True) else 'NA')
            df.at[i, 'tecnologia_incorporacao'] = clean_text(tabela2[59].find('option', selected=True).text.strip() if tabela2[59].find('option', selected=True) else 'NA')
            df.at[i, 'tecnologia_ondeSUS'] = clean_text(tabela2[61].find('option', selected=True).text.strip() if tabela2[61].find('option', selected=True) else 'NA')
            df.at[i, 'tecnologia_oncologico'] = clean_text(tabela2[63].find('option', selected=True).text.strip() if tabela2[63].find('option', selected=True) else 'NA')
            df.at[i, 'outrasTec_generico'] = clean_text(tabela2[70].find('option', selected=True).text.strip() if tabela2[70].find('option', selected=True) else 'NA')
            df.at[i, 'outrasTec_similar'] = clean_text(tabela2[72].find('option', selected=True).text.strip() if tabela2[72].find('option', selected=True) else 'NA')
            df.at[i, 'evidencias_CONITEC'] = clean_text(tabela2[111].find('option', selected=True).text.strip())
            df.at[i, 'conclusao_resultado'] = clean_text(tabela2[116].find('option', selected=True).text.strip())
            df.at[i, 'conclusao_motivacao'] = clean_text(tabela2[118].find('textarea').text.strip())
            df.at[i, 'conclusao_evidencias'] = clean_text(tabela2[120].find('option', selected=True).text.strip())
            df.at[i, 'conclusao_urgencia'] = clean_text(tabela2[123].find('option', selected=True).text.strip())
            df.at[i, 'conclusao_anexos'] = clean_text('https://www.cnj.jus.br/e-natjus/' + tabela2[137].find('a')['href'] if tabela2[137].find('a')['href'] else 'NA')
            df.at[i, 'natjus_responsavel'] = clean_text(tabela2[129].find('option', selected=True).text.strip())
            df.at[i, 'inst_responsavel'] = clean_text(tabela2[131].find('input')['value'].strip())
            df.at[i, 'apoio_tutoria'] = clean_text(tabela2[133].find('option', selected=True).text.strip())
            
            if i % 50 == 0:
                save_preview(df)
                print("Salvo.")

            time.sleep(2)
        
        except Exception as e:
            print(f"Failed to process {link} after retries: {str(e)}")
            continue

    save_preview(df)