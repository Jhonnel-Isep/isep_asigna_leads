from odoo import models, api, fields
from .FeriadosLatam import Feriados_Latam
import datetime


class CrmLead(models.Model):
	_inherit = 'crm.lead'

	@api.model
	def create(self, values):
		self.agente 	   = values.get('user_id')
		self.telf 		   = values.get('phone')
		self.mail 		   = values.get('email_from')
		self.localidad 	   = values.get('country_id')
		self.fecha_entrada = values.get('create_date')
		self.area_lead = values.get('x_area_id')	

		# Main - Ejecucion de filtros
		if not self.agente:

			if self.localidad == 68:
				espana = self.env['security.role'].browse(2).user_ids
				self.agentes = diccionario_agentes(espana) 
			else:
				latam = self.env['security.role'].browse(3).user_ids
				self.agentes = diccionario_agentes(latam)

			# Primera etapa de filtrado
			vacaciones_status = filtro_vacaciones()
			feriado_status    = filtro_feriado()
			horario_status    = filtro_horario()

			# Asignacion de agente caso 1
			anterior_status   = asigna_anterior_agente()

			# Segunda etapa de filtrado
			if anterior_status == False: 
				area_status 			= filtro_area_agente()
				preferencia_pais_status = filtro_preferencia_pais()
				max_lead_status 		= filtro_num_max_leads()

				# Asignacion de agente caso 2
				values.update({'user_id': asigna_nuevo_agente()})	

		# Pasar info al log
		attrs = {
			# Primera etapa filtrado
			'agente_lead'                 : values.get('user_id'),
    		'pais_lead' 				  : values.get('country_id'), 
    		'filtro_vacaciones'			  : vacaciones_status,
			'filtro_feriado'			  : feriado_status,
			'filtro_horario' 			  : horario_status,
			'filtro_atendido_previamente' : anterior_status,
			# Segunda etapa filtrado
			'filtro_area_curso' : area_status,
			'filtro_pais' 		: preferencia_pais_status,
    		'filtro_max_lead'   : max_lead_status
		}

		self.env['lead.logs'].self.AutoLeadLogRegister(attrs)	
		# Fin pasar info al log

		res = super(CrmLead, self).create(values)
		return res
	
	def diccionario_agentes(self, li_agentes):
		list_agentes    = []
		list_cant_leads = []
		list_tasat_conv = []
		dic_agents      = {}

		for agente in li_agentes:

			list_agentes.append(agente.id)
			cant_leads  = 0
			tasa_conv   = []
			leads_agent = self.env['crm.lead'].search([('user_id', '=', agente.id)])

			for leads in leads_agent:

				if (leads.type == 'lead'):
					cant_leads += 1

				tasa_conv.append(leads.probability)

			list_cant_leads.append(cant_leads)

			try:
				tasat_conv = sum(tasa_conv) / len(tasa_conv)

			except:
				tasat_conv = 0

			list_tasat_conv.append(tasat_conv)
		
		# Diccionario base de agentes
		dic_agents = {
			'Agente'		 	 : self.list_agentes, 
			'Numero de Leads'    : self.list_cant_leads, 
			'Tasa de Conversion' : self.list_tasat_conv
			}

		return dic_agents
		
	def filtro_vacaciones(self):
		now = datetime.datetime.now()
		dia = int(now.strftime("%d"))
		mes = int(now.strftime("%m"))
		fecha_actual = (mes,dia)

		# Traemos a los agentes de la lista de agentes del diccionario:
		aux_list_agentes 	= self.list_agentes
		aux_list_cant_leads = self.list_cant_leads
		aux_list_tasat_conv = self.list_tasat_conv

		foo=0
		
		for  i in self.list_agentes:

			vacaciones = self.env['atributos.agentes'].search([('agente_name', '=', i)])

			inicio_vacaciones = (int(vacaciones.vacaciones_inicio.strftime("%m")), int(vacaciones.vacaciones_inicio.strftime("%d")))
			fin_vacaciones = (int(vacaciones.vacaciones_fin.strftime("%m")), int(vacaciones.vacaciones_fin.strftime("%d")))

			if fecha_actual[1]>=inicio_vacaciones[1] and fecha_actual[0] == inicio_vacaciones[0] or fecha_actual[0]>inicio_vacaciones[0] and fecha_actual[0] <= fin_vacaciones[0]:
				del aux_list_agentes[foo]
				del aux_list_cant_leads[foo]
				del aux_list_tasat_conv[foo]
			foo += 1
		
		# Filtrado
		if len(aux_list_agentes)>0:
			self.list_agentes 	 = aux_list_agentes
			self.list_cant_leads = aux_list_cant_leads
			self.list_tasat_conv = aux_list_tasat_conv
			return True
		else:
			return False

	def filtro_feriado(self):

		feriados = FeriadosLatam.FeriadosLatam()
		now = datetime.datetime.now()
		dia = int(now.strftime("%d"))
		mes = int(now.strftime("%m"))
		fecha  = (mes, dia) 
		foo= 0
		paises = []
		aux_list_agentes 	= self.list_agentes
		aux_list_cant_leads = self.list_cant_leads
		aux_list_tasat_conv = self.list_tasat_conv

		feriados_mexico    = feriados.mexico()
		feriados_colombia  = feriados.colombia()
		feriados_salvador  = feriados.salvador()
		feriados_nicaragua = feriados.nicaragua()
		feriados_venezuela = feriados.venezuela()
		feriados_honduras  = feriados.honduras()

		for i in feriados_mexico:
			if fecha==i:
				paises.append(156)
		for i in feriados_colombia:
			if fecha==i:
				paises.append(49)
		for i in feriados_salvador:
			if fecha==i:
				paises.append(209)
		for i in feriados_nicaragua:
			if fecha==i:
				paises.append(164)
		for i in feriados_venezuela:
			if fecha==i:
				paises.append(238)
		for i in feriados_honduras:
			if fecha==i:
				paises.append(299)

		for i in aux_list_agentes:

			pais_agente = self.env['res.users'].browse(i).country_id.id

			if  pais_agente in paises:
				del aux_list_agentes[foo]
				del aux_list_cant_leads[foo]
				del aux_list_tasat_conv[foo]
			foo+=1

		# Filtrado
		if len(aux_list_agentes)>0:
			self.list_agentes 	 = aux_list_agentes
			self.list_cant_leads = aux_list_cant_leads
			self.list_tasat_conv = aux_list_tasat_conv
			return True		
		else:
			return False

	def filtro_horario(self):
		semana = int(self.fecha_entrada.weekday())
		hora = int(self.fecha_entrada.strftime('%H'))
		minu = int(self.fecha_entrada.strftime('%M'))

		paises = []

		if (hora-4 in range(9,17)) and (semana in range(4)):
			paises.append('venezuela')


		if (hora-5 in range(9,17)) and (semana in range(5)):
			if (semana == 5):
				if (hora-5 < 12):
					paises.append('colombia')
					paises.append('mexico (cdmx)')
				else:
					paises.append('mexico (cdmx)')
			else:
				paises.append('colombia')
				paises.append('mexico (cdmx)')


		if (hora-6 in range(9,17)) and (semana in range(5)):
			if (semana == 5):
				paises.append('mexico (la paz)')
			else:
				paises.append('nicaragua')
				paises.append('el salvador')
				paises.append('mexico (la paz)')


		if (hora-7 in range(9,17)) and (semana in range(5)):
			paises.append('tijuana')


		if (len(paises) == 0):
			self.viejo_lead()
			self.horario_status = False
		else:
			self.horario_status = True
			return paises
				

	def viejo_lead(self):

		aux = False
		aux2 = False
		todos_leads = self.env['crm.lead'].search([])

		telefonos = []
		emails = []
		agentes = []

		for lead in todos_leads:
			telefonos.append(lead.phone)
			emails.append(lead.email_from)
			agentes.append(lead.x_contactonuevoodup12) 
			# CAMPO "ACTUAL": x_contactonuevoodup12
			# Campo usado para pruebas en local: user_id

		li_todos_leads = [telefonos, emails, agentes]
			
		for telf in li_todos_leads[0]:
			if (self.telf == telf) and (self.telf != False):
				aux2 = True
				aux = False
				aux_indice = li_todos_leads[0].index(telf)
				aux_agente =  li_todos_leads[2][aux_indice].id
				break

			else:
				aux = True
			

		if (aux == True):

			for mail in li_todos_leads[1]:
				if (self.mail == mail) and (self.mail != False):
					aux2 = True
					aux_indice = li_todos_leads[1].index(mail)
					aux_agente =  li_todos_leads[2][aux_indice].id
					
					break

		if (aux2 == True):
			indice = aux_indice
			agente = aux_agente

			#return agente

		return agente

	def asigna_anterior_agente(self):
		
		for i in self.dic_agents["Agente"]:
				if i == viejo_lead():
					agent = i
					values.update({'user_id': self.viejo_lead()})					
					break
		if agent:
			return True
		else:
			 return False		


	
	def filtro_area_agente(self):

		# Traemos a los agentes de la lista de agentes del diccionario:
		aux_agentes = self.list_agentes

		# Traemos a todos los agentes los cuales se encuentran en el area del agente:
		area_lead = self.area_lead
		area_agent = self.env['atributos.agentes'].search([('area_curso', '=', area_lead)])
		

		agentes_misma_area = []
		for agente in area_agent:
			agentes_misma_area.append(agente.agente_name.id)

		coincidencias = list( set(aux_agentes) & set(agentes_misma_area) )

		if (len(coincidencias) > 0):
			
			indices = []
			for agente in coincidencias:
				indices.append(aux_agentes.index(agente))

			self.list_agentes = coincidencias

			tasa = []
			cant = []
			for indice in indices:
				tasa.append(self.list_tasat_conv[indice])
				cant.append(self.list_cant_leads[indice])

			self.list_cant_leads = cant
			self.list_tasat_conv = tasa

			return True
		
		else:
			return False
	
	def filtro_preferencia_pais(self):

		# Traemos los agentes de 'list_agentes':
		aux_agentes = self.list_agentes

		# Traemos los agentes que se encuentran disponibles segun el pais desde el cual se esta creando el lead:
		lead_pais = self.localidad
		agen_pais = self.env['res.users'].search([('security_role_ids', '=', 'Ventas / Asesor'), ('country_id', '=', lead_pais)])

		agentes_mismo_pais = []
		for agentes in agen_pais:
			agentes_mismo_pais.append(agentes.id)


		# Guardamos solo las coincidencias que hay entre las listas: (agentes_mismo_pais) y (agentes_disponibles):
		set_agentes_disponibles = set(aux_agentes)
		set_agentes_mismo_pais = set(agentes_mismo_pais)


		# Intersectamos los dos conjuntos para que se conserven las coincidencias:
		coincidencias = set_agentes_disponibles & set_agentes_mismo_pais
		
		# Finalmente tenemos los agentes que se mantuvieron a pesar de pasar por el filtro:
		agentes = list(coincidencias)

		if (len(agentes) > 0):

			indices = []
			for agente in agentes:
				indices.append(aux_agentes.index(agente))

			self.list_agentes = agentes

			tasa = []
			cant = []
			for indice in indices:
				tasa.append(self.list_tasat_conv[indice])
				cant.append(self.list_cant_leads[indice])

			self.list_cant_leads = cant
			self.list_tasat_conv = tasa

			return True

		else:

			return False


	def num_max_leads(self):

		li_agentes = self.list_agentes
		li_cant_leads = self.list_cant_leads
		li_tasat_conv = self.list_tasat_conv

		cant_max_leads = []
		for agente in li_agentes:
			atrb_agente = self.env['atributos.agentes'].search([('agente_name', '=', agente)])
			cant_max_leads.append(atrb_agente.max_leads)

		macro_list = []

		# FORMATO MACRO_LIST:
		# macro_list = [[agentes 1, cantidad de leads 1, cantidad maxima de leads 1], [... 2, ... 2, ...2]]

		for i in range(len(li_cant_leads)):
			aux_list = []

			aux_list.append(li_agentes[i])			
			aux_list.append(li_cant_leads[i])
			aux_list.append(cant_max_leads[i])

			macro_list.append(aux_list)

		agentes = []
		tasas = []
		cantidades = []
		for i in macro_list:
				
			if (i[1] < i[2]):
				agentes.append(i[0])
				indice = li_agentes.index(i[0])
				tasas.append(li_tasat_conv[indice])
				cantidades.append(li_cant_leads[indice])

		if (len(agentes) > 0):
			self.list_agentes = agentes
			self.list_cant_leads = cantidades
			self.list_tasat_conv = tasas

			return True

		else:

			return False	


	def asigna_nuevo_agente(self):

		menor=10000
		lista=[]
		index=0
		mayor=0

		for i in self.dic_agents["Numero de Leads"]:
			if i < menor:
				menor = i

		for i in self.dic_agents["Numero de Leads"]:
			if i == menor:
				lista.append(self.dic_agents["Agente"][index])    
			index += 1

		index = 0
		for i in lista:

			if i > mayor:
				mayor = i
				index += 1

		agente = lista[index-1]

		return agente