# -*- coding: utf-8 -*-
"""
*********************************************************
Código para la asignación automática de las iniciativas
*********************************************************

Input: 
    
    Base de datos de Producción, "final" y archivos de excel con los países

A. Tablas:
    
1. crm_team
2. res_users
3. crm_lead
4. res_partner
5. paises.xls (archivo de excel con la información de los países
               y horarios de los asesores de venta de LATAM)
6. spain.xls
7.

B. Calendarios de las fechas festivas de los países de los asesores de venta


@author: Mariela Perdomo León
mperdomo@isep.com
Febrero 2021.
"""


#%% Importando los paquetes necesarios:

import pandas as pd # Manipulación de la data, por ejemplo: dataframe
from pandas.tseries.holiday import *  #Para el calendario
from pandas.tseries.offsets import CustomBusinessDay #Para el calendario
import numpy as np #Funciones matemáticas, permiten realizar cálculos
import seaborn as sb #Paquete de visualización basado en matplotlib, permite hacer gráficos estadísticos
import datetime #Permite mostrar el tiempo de ejecución, fecha y hora del script
    
from sklearn import tree #Paquete de ML,incluye diferentes algoritmos, como por ejemplo: decision tree
from sklearn.model_selection import KFold # Para el Decision Tree
from sklearn.metrics import accuracy_score #Métricas
from sklearn.model_selection import cross_val_score #Métricas

import pydotplus # Para crear el gráfico del Decision Tree 
from IPython.display import Image  # Muestra la imagen del gráfico

from datetime import datetime, date # Import datetime class from datetime module 


#%% Tiempo de ejecución del script con su fecha y hora:

fecha_ejecucion=datetime.now()    

print('Fecha_de_ejecucion=', fecha_ejecucion)

#%% Conexión con PostgreSQL:

import psycopg2 #Paquete para conectar con PostgreSQL a través de Python 

#Datos de la base de datos para la conexión:
con= psycopg2.connect(database="final", user="postgres_sql", password="iseplatam2021",host= "128.199.6.176", port="5432") 

print("Database opened successfully")


#%% Importación de la tablas necesarias
    
# 1. crm_team y res_users, especificamente los equipos de ventas junto con el personal
# de esos equipos:

cursor1=con.cursor()

cursor1.execute("select crm_team.id, crm_team.name,res_users.id, res_users.login, res_partner.name from crm_team inner join res_users on crm_team.id = res_users.sale_team_id inner join res_partner on res_users.partner_id = res_partner.id  order by crm_team.id")
crm_team2=[]
for fila in cursor1:
    lista1=list(fila)
    crm_team2.append(lista1)
#con.close()

# 2. Importando las iniciativas
 
cursor2=con.cursor()

#Items de las inciativas:
#cursor2.execute("SELECT create_date,name,x_curso_id, contact_name, type, state_id, city, country_id, email_from, user_id, x_contactonuevoodup12, x_contactonuevoodup,x_precontactonuevodup, team_id, company_id, x_ga_source, description FROM public.crm_lead WHERE extract (year from create_date) = '2021' and extract (month from CREATE_DATE) = '2' and type = 'lead';") # FEBRERO 2021
cursor2.execute("SELECT crm_lead.create_date,crm_lead.name,crm_lead.x_curso_id,product_template.name, crm_lead.contact_name, crm_lead.type, crm_lead.state_id, crm_lead.city, crm_lead.country_id, crm_lead.email_from, crm_lead.user_id,res_partner.name, crm_lead.x_contactonuevoodup12, crm_lead.x_contactonuevoodup,crm_lead.x_precontactonuevodup, crm_lead.team_id, crm_lead.company_id, crm_lead.x_ga_source, crm_lead.description FROM crm_lead inner join res_users on crm_lead.user_id =res_users.id inner join res_partner on res_users.partner_id = res_partner.id inner join product_template on crm_lead.x_curso_id = product_template.id  WHERE extract (year from crm_lead.create_date) = '2021' and extract (month from crm_lead.create_date) = '3' and crm_lead.type = 'lead';") #MES MARZO DE 2021

lead=[]   
for fila in cursor2:
      lista2=list(fila)
      lead.append(lista2)
#con.close()

#Observación: 
# Cuando se importa las iniciativas con el nombre del comercial (como en el
# caso de la línea 69) se cargan  menos cantidad, que cuando no se incorpora 
# el nombre (linea 68). Esto es porque en la base de datos hay casillas vacías 
# para el campo comercial en varias fechas.
# Cuando se hace el inner join sólo se trae información donde hayan elementos
# en común.

#%% Equipo de Ventas:
    
equipodeventas=np.array(crm_team2)
 
# Creando el data frame con las etiquetas en las columnas:
    
team_df = pd.DataFrame()

team_df['Equipo de ventas']= equipodeventas[:,0]
team_df['crm_team_name']= equipodeventas[:,1]
team_df['sale_agent_id']= equipodeventas[:,2]
team_df['login']= equipodeventas[:,3]
team_df['name']= equipodeventas[:,4]

#%% Asesores de venta de España:
    
condicionlogica=team_df.loc[:,'sale_agent_id']=='42'
spain_agent=team_df.loc[condicionlogica]
condicionlogica=team_df.loc[:,'sale_agent_id']=='56'
spain_agent=spain_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='72'
spain_agent=spain_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='78'
spain_agent=spain_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='81'
spain_agent=spain_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='91'
spain_agent=spain_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='92'
spain_agent=spain_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='94'
spain_agent=spain_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='96'
spain_agent=spain_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='99'
spain_agent=spain_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='158'
spain_agent=spain_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='183'
spain_agent=spain_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='217'
spain_agent=spain_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='233'
spain_agent=spain_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='235'
spain_agent=spain_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='247'
spain_agent=spain_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='254'
spain_agent=spain_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='277'
spain_agent=spain_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='279'
spain_agent=spain_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='312'
spain_agent=spain_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='200000969'
spain_agent=spain_agent.append(team_df.loc[condicionlogica])

# Selecciona sólo algunas columnas:
    
#asesoresspain=spain_agent.iloc[:, [0,1,3,4]] 
asesoresspain=spain_agent

#Actualización de los índices:
asesoresspain.index = range(asesoresspain.shape[0])

#Convirtiendo sale_agent_id y crm_team_id a int64. 
#Observación: Cuando se importa desde PostgreSQL, llega a Python como un objeto, 
#sin embargo, ellos son números, es importante modificarlo. Si no se hace no 
#se pueden hacer operaciones con ellos:
    
asesoresspain["sale_agent_id"] = pd.to_numeric(asesoresspain["sale_agent_id"])
asesoresspain["Equipo de ventas"] = pd.to_numeric(asesoresspain["Equipo de ventas"])
#%% Agentes de venta de Latinoamérica:
    
condicionlogica=team_df.loc[:,'sale_agent_id']=='313'
latam_agent=team_df.loc[condicionlogica]   
condicionlogica=team_df.loc[:,'sale_agent_id']=='100000008'
latam_agent=latam_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='100000009'
latam_agent=latam_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='100000091'
latam_agent=latam_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='100000098'
latam_agent=latam_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='100000123'
latam_agent=latam_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='100000127'
latam_agent=latam_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='100000128'
latam_agent=latam_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='100000175'
latam_agent=latam_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='100000194'
latam_agent=latam_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='100000195'
latam_agent=latam_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='100000221'
latam_agent=latam_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='200000010'
latam_agent=latam_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='200000043'
latam_agent=latam_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='200000044'
latam_agent=latam_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='200000045'
latam_agent=latam_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='200000046'
latam_agent=latam_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='200000055'
latam_agent=latam_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='200000058'
latam_agent=latam_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='200000061'
latam_agent=latam_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='200000063'
latam_agent=latam_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='200000069'
latam_agent=latam_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='200000375'
latam_agent=latam_agent.append(team_df.loc[condicionlogica])
condicionlogica=team_df.loc[:,'sale_agent_id']=='200000953'
latam_agent=latam_agent.append(team_df.loc[condicionlogica])

# Selecciona sólo algunas columnas:
    
#asesoreslatam=latam_agent.iloc[:, [0,1,3,4]] 
asesoreslatam=latam_agent

#Actualización de los índices:
asesoreslatam.index = range(asesoreslatam.shape[0])

#Convirtiendo sale_agent_id y crm_team_id a int64. 
#Observación: Cuando se importa desde PostgreSQL, llega a Python como un objeto, 
#sin embargo, ellos son números, es importante modificarlo. Si no se hace no 
#se pueden hacer operaciones con ellos:
    
asesoreslatam["sale_agent_id"] = pd.to_numeric(asesoreslatam["sale_agent_id"])
asesoreslatam["Equipo de ventas"] = pd.to_numeric(asesoreslatam["Equipo de ventas"])

#Para determinar el tipo de estructuras de los elementos que están en la tabla
#asesoreslatam.dtypes


#%% Iniciativas:
    
np_crm_lead=np.array(lead)

# Creando el data frame con las etiquetas en las columnas:

lead_df = pd.DataFrame()
lead_df['Creado el']= np_crm_lead[:,0]
lead_df['Iniciativa']= np_crm_lead[:,1]  
lead_df['ID del Curso']= np_crm_lead[:,2] 
lead_df['Nombre del Curso']= np_crm_lead[:,3]      
lead_df['Nombre del contacto']= np_crm_lead[:,4] 
lead_df['Type']= np_crm_lead[:,5]  
lead_df['Estado']= np_crm_lead[:,6]  
lead_df['Ciudad']= np_crm_lead[:,7] 
lead_df['Pais']= np_crm_lead[:,8] 
lead_df['Email from']= np_crm_lead[:,9] 
lead_df['Comercial_id']= np_crm_lead[:,10] 
lead_df['Name_Comercial']= np_crm_lead[:,11] 
lead_df['Actual']= np_crm_lead[:,12] 
lead_df['Contacto']= np_crm_lead[:,13]
lead_df['Iniciativa2']= np_crm_lead[:,14]
lead_df['Equipo de ventas']= np_crm_lead[:,15]
lead_df['Compañia']= np_crm_lead[:,16]
lead_df['Origen']= np_crm_lead[:,17]
lead_df['Descripción']= np_crm_lead[:,18]

lead_df.head()

#Cantidad de Iniciativas por líder
lead_df.groupby('Name_Comercial').size()

#%% Horarios y Países de los asesores de venta:

    
# Se importara la información de los horarios y países desde un archivo
# de excel, dado que en la base de datos no se cuenta con la información.


#LATAM
paiseshorarioslatam =pd.read_excel('paises.xls')

#Países
paises=paiseshorarioslatam.iloc[:, [0,4]] 

# Uniendo los DataFrame por medio de merge:
    
asesoreslatam2 = pd.merge(asesoreslatam, paises, on='sale_agent_id')

#Cantidad de asesores por país de LATAM:
#asesoreslatam2.groupby('pais').size()    

#España

spain =pd.read_excel('spain.xls')
spain2=spain.iloc[:, [0,2]] 

# Uniendo los DataFrame por medio de merge:

asesoresspain2 = pd.merge(asesoresspain, spain2, on='sale_agent_id')

#%% Equipo completo de asesores de ventas (España y Latam)

sales_team = pd.concat([asesoresspain2, asesoreslatam2])

#El 01/03/2021 se incorporan 2 asesores al equipo de ventas de España
#Tomar en consideracion esto (Información enviada por Manel Arroyo el 25/02/2021)

sb.catplot(x="pais",data=sales_team,kind="count")

  
#%% Calendario de días festivos para los países de los asesores de venta:

# España

class EsBusinessCalendar(AbstractHolidayCalendar):
   rules = [
     Holiday('Año Nuevo', month=1, day=1),
     Holiday('Epifanía del Señor', month=1, day=6),
     Holiday('Viernes Santo', month=4, day=2),
     Holiday('Día del Trabajador', month=5, day=1),
     Holiday('Asunción de la Virgen', month=8, day=15),
     Holiday('Día de la Hispanidad', month=10, day=12),
     Holiday('Todos los Santos', month=11, day=1),
     Holiday('Día Constitución', month=12, day=6),
     Holiday('Inmaculada Concepción', month=12, day=8),
     Holiday('Navidad', month=12, day=25)
   ]

es_BD = CustomBusinessDay(calendar=EsBusinessCalendar())
s = pd.date_range('2021-01-01', end='2021-12-31', freq=es_BD)
spain_calendar = pd.DataFrame(s, columns=['Spain'])

#%% México


class EsBusinessCalendar2(AbstractHolidayCalendar):
   rules = [
     Holiday('Año Nuevo', month=1, day=1),
     Holiday('Día de la Constitución Mexicana', month=2, day=1),
     Holiday('Natalicio de Benito Juárez', month=3, day=15),
     Holiday('Domingo de Resurreción', month=4, day=4),
     Holiday('Día del Trabajador', month=5, day=1),
     Holiday('Día de la Independencia', month=9, day=16),
     Holiday('Revolución Mexicana', month=11, day=15),
     Holiday('Navidad', month=12, day=25)
   ]

b = CustomBusinessDay(calendar=EsBusinessCalendar2(), weekmask = 'Mon Tue Wed Thu Fri Sat')
mexico_calendar=pd.date_range(start='2021-01-01',end='2021-12-31', freq=b)
mexico_calendar = pd.DataFrame(mexico_calendar, columns=['Mexico'])
#%% Colombia

class EsBusinessCalendar3(AbstractHolidayCalendar):
   rules = [
     Holiday('Año Nuevo', month=1, day=1),
     Holiday('Día de los Reyes Magos', month=1, day=11),
     Holiday('Día de San José', month=3, day=22),
     Holiday('Jueves Santo', month=4, day=1),
     Holiday('Viernes Santo', month=4, day=2),
     Holiday('Día del Trabajador', month=5, day=1),
     Holiday('Día de la Ascensión', month=5, day=17),
     Holiday('Corpus Cristi', month=6, day=7),
     Holiday('Sagrado Corazón', month=6, day=14),
     Holiday('San Pedro y San Pablo', month=7, day=5),
     Holiday('Día de la Independencia', month=7, day=20),
     Holiday('Batalla de Boyacá', month=8, day=7),
     Holiday('La asunción de la Virgen', month=8, day=16),
     Holiday('Día de la Raza', month=10, day=18),
     Holiday('Día de los Difuntos', month=11, day=1),
     Holiday('Independencia de Cartagena', month=11, day=15),
     Holiday('Día de la Inmaculada Concepción', month=12, day=8),
     Holiday('Navidad', month=12, day=25)
   ]

c = CustomBusinessDay(calendar=EsBusinessCalendar3(), weekmask = 'Mon Tue Wed Thu Fri Sat')
colombia_calendar=pd.date_range(start='2021-01-01',end='2021-12-31', freq=c)
colombia_calendar = pd.DataFrame(colombia_calendar, columns=['Colombia'])
#%% El Salvador

class EsBusinessCalendar4(AbstractHolidayCalendar):
   rules = [
     Holiday('Año Nuevo', month=1, day=1),
     Holiday('Jueves Santo', month=4, day=1),
     Holiday('Viernes Santo', month=4, day=2),
     Holiday('Sábado Santo', month=4, day=3),
     Holiday('Domingo Santo', month=4, day=4),
     Holiday('Día del Trabajador', month=5, day=1),
     Holiday('Día de la Madre', month=5, day=10),
     Holiday('Día del Padre', month=6, day=17),
     Holiday('Fiestas de San Salvador', month=8, day=5),
     Holiday('Celebración del Divino Salvador del Mundo', month=8, day=6),
     Holiday('Día de la Independencia', month=9, day=15),
     Holiday('Día de los Difuntos', month=11, day=2),
     Holiday('Navidad', month=12, day=25)
   ]

d = CustomBusinessDay(calendar=EsBusinessCalendar4(), weekmask = 'Mon Tue Wed Thu Fri Sat')
elsalvador_calendar=pd.date_range(start='2021-01-01',end='2021-12-31', freq=d)
elsalvador_calendar = pd.DataFrame(elsalvador_calendar, columns=['El Salvador'])

#%% Nicaragua

class EsBusinessCalendar5(AbstractHolidayCalendar):
   rules = [
     Holiday('Año Nuevo', month=1, day=1),
     Holiday('Jueves Santo', month=4, day=1),
     Holiday('Viernes Santo', month=4, day=2),
     Holiday('Domingo Santo', month=4, day=4),
     Holiday('Día del Trabajador', month=5, day=1),
     Holiday('Día de la Revolución', month=7, day=19),
     Holiday('Traída de Santo Domingo de Guzmán', month=8, day=1),
     Holiday('Dejada de Santo Domingo de Guzmán', month=8, day=10),
     Holiday('Batalla de San Jacinto', month=9, day=14),
     Holiday('Independencia de Nicaragua', month=9, day=15),
     Holiday('Inmaculada Concepción de María', month=12, day=8),
     Holiday('Navidad', month=12, day=25)
   ]
   
e = CustomBusinessDay(calendar=EsBusinessCalendar5(), weekmask = 'Mon Tue Wed Thu Fri Sat')
nicaragua_calendar=pd.date_range(start='2021-01-01',end='2021-12-31', freq=e)
nicaragua_calendar = pd.DataFrame(nicaragua_calendar, columns=['Nicaragua'])

#%% Mapeo de Datos:

#Se debe transformar varios datos de entrada en valores categóricos:

#Commercial_id
sales_team['Comercial_id']=sales_team['pais'].map({'España':76, 'MÉXICO': 100000006, 'COLOMBIA':100000006, 'EL SALVADOR':100000006, 'NICARAGUA':100000006, '':0 }).astype(int)

#Country Mapping
sales_team['Pais_id']=sales_team['pais'].map({'España':1, 'MÉXICO': 2, 'COLOMBIA':3, 'EL SALVADOR':4, 'NICARAGUA':5, '':0 }).astype(int)

sales_team.index = range(sales_team.shape[0])

#drop_elements = [ 'crm_team_name', 'login', 'name','pais']
#sales_team_encoded = sales_team.drop(drop_elements, axis=1)  

#Actualización de los índices:
#sales_team_encoded.index = range(sales_team_encoded.shape[0])


#sales_team_encoded['paisEncoded'] = pd.to_numeric(sales_team_encoded['paisEncoded'], downcast='float')

drop_elements2=['Nombre del Curso','Nombre del contacto','Type', 'Estado', 'Ciudad', 'Pais', 'Email from', 'Name_Comercial', 'Contacto','Iniciativa2', 'Compañia', 'Origen', 'Descripción']
lead_df_2 = lead_df.drop(drop_elements2, axis=1)

lead_df_2= lead_df

# Tabla con valores categóricos:

lead_df_2["ID del Curso"] = pd.to_numeric(lead_df_2["ID del Curso"])
lead_df_2["Comercial_id"] = pd.to_numeric(lead_df_2["Comercial_id"])
lead_df_2["Actual"] = pd.to_numeric(lead_df_2["Actual"])
lead_df_2["Equipo de ventas"] = pd.to_numeric(lead_df_2["Equipo de ventas"])

lead_df_2 = lead_df_2.fillna(5)

# Tabla que contiene valores categóricos de las iniciativas 
# especificamente, en las columnas: Comercial_id y Actual los lideres de 
# venta de España y LATAM.
 
lead_df_3=lead_df_2[(lead_df_2['Comercial_id']==76) & (lead_df_2['Actual']==76)]
lead_df_4=lead_df_2[(lead_df_2['Comercial_id']==100000006) & (lead_df_2['Actual']==100000006)]
lead_df_encoded=pd.concat([lead_df_3,lead_df_4])

#Actualización de los índices:
lead_df_encoded.index = range(lead_df_encoded.shape[0])


#%% Reglas:
    

#Revisión de los calendarios:

# Para la fecha:
fecha1 = date.today()
formato1 = "%Y-%m-%d "
hoy = datetime.today()
cadena = hoy.strftime(formato1)  
objeto_datetime = datetime.strptime(cadena, formato1)


# Paises activos 

spain_activo=spain_calendar[(spain_calendar['Spain']==objeto_datetime)]
mexico_activo=mexico_calendar[(mexico_calendar['Mexico']==objeto_datetime)]
colombia_activo=colombia_calendar[(colombia_calendar['Colombia']==objeto_datetime)]
elsalvador_activo=elsalvador_calendar[(elsalvador_calendar['El Salvador']==objeto_datetime)]
nicaragua_activo=nicaragua_calendar[(nicaragua_calendar['Nicaragua']==objeto_datetime)]

#Actualización de los índices:
spain_activo.index = range(spain_activo.shape[0])
mexico_activo.index = range(mexico_activo.shape[0])
colombia_activo.index = range(colombia_activo.shape[0])
elsalvador_activo.index = range(elsalvador_activo.shape[0])
nicaragua_activo.index = range(nicaragua_activo.shape[0])

#DataFrame con los países de los asesores activos para la fecha de ejecución del código:
paises_activos=pd.concat([spain_activo,mexico_activo,colombia_activo, elsalvador_activo,nicaragua_activo], axis=1)



#%% Casos cuando los paises estan activos o no

   
#Todos los países:   

#Caso 1. Cuando todos los paises son 0    
# if len(spain_activo)==0:
#     salesteam2 = sales_team.drop(sales_team[sales_team['pais']=='España'].index)
#     if len(mexico_activo)==0:
#         salesteam2 = salesteam2.drop(salesteam2[salesteam2['pais']=='MÉXICO'].index)
#         if len(colombia_activo)==0:
#             salesteam2 = salesteam2.drop(salesteam2[salesteam2['pais']=='COLOMBIA'].index)
#             if len(elsalvador_activo)==0:
#                 salesteam2 = salesteam2.drop(salesteam2[salesteam2['pais']=='EL SALVADOR'].index)
#                 if len(nicaragua_activo)==0:
#                     salesteam2 = salesteam2.drop(salesteam2[salesteam2['pais']=='NICARAGUA'].index)
#                 else:
#                    salesteam2= sales_team 
#             else:
#                 salesteam2= sales_team
#         else:
#             salesteam2= sales_team
#     else:
#         salesteam2= sales_team
# else:
#     salesteam2= sales_team
        
# #Caso 2. Cuando es el 25/12
    
# if len(spain_activo)==0 and len(mexico_activo)==0 and len(colombia_activo)==0 and len(elsalvador_activo)==0 and len(nicaragua_activo)==0:
#     salesteam2 = sales_team.drop(sales_team[sales_team['pais']=='España'].index)
#     salesteam2 = salesteam2.drop(salesteam2[salesteam2['pais']=='MÉXICO'].index)
#     salesteam2 = salesteam2.drop(salesteam2[salesteam2['pais']=='COLOMBIA'].index)
#     salesteam2 = salesteam2.drop(salesteam2[salesteam2['pais']=='EL SALVADOR'].index)
#     salesteam2 = salesteam2.drop(salesteam2[salesteam2['pais']=='NICARAGUA'].index)
# else:
#     salesteam2 = sales_team 
    

 #%% Decision Tree:
    
# cv = KFold(n_splits=10) # Numero deseado de "folds" que haremos
# accuracies = list()
# max_attributes = len() #colocar el data frame con los valores categoricos
# depth_range = range(1, max_attributes + 1)

# # Testearemos la profundidad de 1a cantidad de atributos +1
# for depth in depth_range:
#       fold_accuracy = []
#       tree_model = tree.DecisionTreeClassifier(criterion='entropy',  # podría ser gini, pero utilizamos entradas categóricas
#                                               min_samples_split=20, # se refiere a la cantidad mínima de muestras que debe tener un nodo para poder subdividir.
#                                               min_samples_leaf=5   # cantidad mínima que puede tener una hoja final. Si tuviera menos, no se formaría esa hoja y “subiría” un nivel, su antecesor.
#                                               #max_depth = depth
#                                               #class_weight={1:3.5} 
#                                               ) # con esto compensamos los desbalances que hubiera.
#       for train_fold, valid_fold in cv.split(): #colocar el data frame con los valores categoricos
#         f_train = tabla.loc[train_fold] 
#         f_valid = tabla.loc[valid_fold] 

#         model = tree_model.fit(X = f_train.drop([], axis=1), y = f_train[]) #colocar la variable
#         valid_acc = model.score(X = f_valid.drop([], axis=1), 
#                                 y = f_valid[]) # calculamos la precision con el segmento de validacion
#         fold_accuracy.append(valid_acc)

#       avg = sum(fold_accuracy)/len(fold_accuracy)
#       accuracies.append(avg)
    
# # Mostramos los resultados obtenidos
# df = pd.DataFrame({"Max Depth": depth_range, "Average Accuracy": accuracies})
# df = df[["Max Depth", "Average Accuracy"]]
# print(df.to_string(index=False)) 
    
 





    
 