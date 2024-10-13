# Nem todos os estados fazem isso, mas, em alguns, pareceres requeridos por um mesmo paciente são compilados em um único link
# O fato de o link conter um ou mais pareceres altera a maneira como iremos raspar as informações do parecer.
# Para lidar com isso, dividimos a base em duas.

# Seria possível utilizar um só código para lidar com ambos os casos, mas isso aumentaria o tempo necessário para
# raspar os dados, já que teríamos de utilizar a solução mais demorada também para os casos mais simples, de um parecer

import pandas as pd
from datetime import datetime

df = pd.concat([pd.read_excel('enatjus-Medicamentos-20240930121319-Estado DF - Distrito Federal.xlsx'),
               pd.read_excel('enatjus-Medicamentos-20240930123805-Estado MA - Maranhão.xlsx'),
               pd.read_excel('enatjus-Medicamentos-20240930144122-Estado PE - Pernambuco.xlsx'),
               pd.read_excel('enatjus-Medicamentos-20240930150458-Estado RN - Rio Grande do Norte.xlsx'),
               pd.read_excel('enatjus-Medicamentos-20240930160020-Estado ES - Espírito Santo.xlsx'),
               pd.read_excel('enatjus-Medicamentos-20240930162347-Estado GO - Goiás.xlsx'),
               pd.read_excel('enatjus-Medicamentos-20240930170034-Estado PR - Paraná.xlsx'),
               pd.read_excel('enatjus-Medicamentos-20240930174002-Estado SE - Sergipe.xlsx'),
               pd.read_excel('enatjus-Medicamentos-20240930181910-Estado RJ - Rio de Janeiro.xlsx'),
               pd.read_excel('enatjus-Medicamentos-20240930194337-Estado MS - Mato Grosso do Sul.xlsx'),
               pd.read_excel('enatjus-Medicamentos-20240930201753-Estado MT - Mato Grosso.xlsx'),
               pd.read_excel('enatjus-Medicamentos-20240930214313-Estado SP - São Paulo.xlsx'),
               pd.read_excel('enatjus-Medicamentos-20241001125028-Estado RS - Rio Grande do Sul.xlsx'),
               pd.read_excel('enatjus-Medicamentos-20241001150325-Estado Nacional.xlsx'),
               pd.read_excel('enatjus-Medicamentos-20241001154253-Estado BA - Bahia.xlsx')])

df['estado'].value_counts()

duplicates_mask = df.duplicated(subset='id', keep=False)

df_unique = df[~duplicates_mask]
df_duplicates = df[duplicates_mask]

df_unique.to_excel('itens_unicos' + datetime.now().strftime("%Y%m%d%H%M%S") + '.xlsx', index=False)
df_duplicates.to_excel('duplicatas' + datetime.now().strftime("%Y%m%d%H%M%S") + '.xlsx', index=False)
df.to_excel('pareceresCompilados-' + datetime.now().strftime("%Y%m%d%H%M%S") + '.xlsx', index=False)