from odoo import models, api, fields
from .FeriadosLatam import FeriadosLatam
from .AutoLeadLogRegister import AutoLeadLogRegister
import datetime


class CrmLead(models.Model):
	_inherit = 'crm.lead'

	@api.model
	def create(self, values):
		self.agente        = values.get('user_id')
		self.telf          = values.get('phone')
		self.mail          = values.get('email_from')
		self.localidad     = values.get('country_id')
		self.fecha_entrada = values.get('date_open')
		self.area_lead 	   = values.get('x_area_id')	

		# Main - Ejecucion de filtros
		if not self.agente:

			if self.localidad == 68:
				espana 		 = self.env['security.role'].browse(139).user_ids
				self.agentes = self.diccionario_agentes(espana) 
			else:
				latam 		 = self.env['security.role'].browse(140).user_ids
				self.agentes = self.diccionario_agentes(latam)

			# Primera etapa de filtrado
			vacaciones_status = self.filtro_vacaciones()
			feriado_status 	  = self.filtro_feriado()
			horario_status    = self.filtro_horario()

			# Asignacion de agente caso 1
			anterior_status   = self.asigna_anterior_agente()

			attrs = {
				# Primera etapa filtrado
				'pais_lead'        : self.localidad, 
				'filtro_vacaciones'          : vacaciones_status,
				'filtro_feriado'             : feriado_status,
				'filtro_horario'             : horario_status,
				'filtro_atendido_previamente': anterior_status
			}

			if (anterior_status == True):
				agent = self.viejo_lead()
				values.update({'user_id': agent})
				attrs['agente_lead'] = agent

			# Segunda etapa de filtrado
			if anterior_status == False: 
				area_status 		    = self.filtro_area_agente()
				preferencia_pais_status = self.filtro_preferencia_pais()
				max_lead_status         = self.filtro_num_max_leads()

				# Asignacion de agente caso 2
				agent = self.asigna_nuevo_agente()
				values.update({'user_id': agent})
				attrs['agente_lead'] = agent

				attrs['filtro_area_curso'] = area_status
				attrs['filtro_pais']       = preferencia_pais_status
				attrs['filtro_max_lead']   = max_lead_status	
				
			self.env['lead.logs'].create(attrs)
			# Fin pasar info al log

		res = super(CrmLead, self).create(values)
		return res


	def diccionario_agentes(self, li_agentes):
		self.list_agentes    = []
		self.list_cant_leads = []
		self.list_tasat_conv = []
		self.dic_agents      = {}

		for agente in li_agentes:

			self.list_agentes.append(agente.id)
			cant_leads  = 0
			tasa_conv   = []
			leads_agent = self.env['crm.lead'].search([('user_id', '=', agente.id)])

			for leads in leads_agent:

				if (leads.type == 'lead'):
					cant_leads += 1

				tasa_conv.append(leads.probability)

			self.list_cant_leads.append(cant_leads)

			try:
				tasat_conv = sum(tasa_conv) / len(tasa_conv)

			except:
				tasat_conv = 0

			self.list_tasat_conv.append(tasat_conv)
		
		# Diccionario base de agentes
		self.dic_agents = {
			'Agente'		 	 : self.list_agentes, 
			'Numero de Leads'    : self.list_cant_leads, 
			'Tasa de Conversion' : self.list_tasat_conv
			}

		return self.dic_agents


	def filtro_vacaciones(self):
		now 	     = datetime.datetime.now()
		dia 		 = int(now.strftime("%d"))
		mes 		 = int(now.strftime("%m"))
		fecha_actual = (mes,dia)

		# Traemos a los agentes de la lista de agentes del diccionario:
		aux_list_agentes 	= self.list_agentes
		aux_list_cant_leads = self.list_cant_leads
		aux_list_tasat_conv = self.list_tasat_conv

		black_list = []
		foo = 0

		ejecucion = False
		
		for agente in self.list_agentes:
			vacaciones = self.env['atributos.agentes'].search([('agente_name', '=', agente)])

			if (vacaciones.vacaciones_inicio != False) or (vacaciones.vacaciones_fin != False):

				inicio_vacaciones = (
					int(vacaciones.vacaciones_inicio.strftime("%m")), 
					int(vacaciones.vacaciones_inicio.strftime("%d"))
					)

				fin_vacaciones    = (
					int(vacaciones.vacaciones_fin.strftime("%m")), 
					int(vacaciones.vacaciones_fin.strftime("%d"))
					)

				if (fecha_actual[1] >= inicio_vacaciones[1]) and (fecha_actual[0] == inicio_vacaciones[0]) or (fecha_actual[0] > inicio_vacaciones[0]) and (fecha_actual[0] <= fin_vacaciones[0]):
					black_list.append(foo)
					ejecucion = True
			
			foo += 1

		for index in sorted(black_list, reverse=True):
			del aux_list_agentes[index]
			del aux_list_cant_leads[index]
			del aux_list_tasat_conv[index]

		# Filtrado
		if (len(aux_list_agentes) > 0) and (ejecucion == True):
			self.list_agentes 	 = aux_list_agentes
			self.list_cant_leads = aux_list_cant_leads
			self.list_tasat_conv = aux_list_tasat_conv
			return True


	def filtro_feriado(self):

		feriados = FeriadosLatam()
		now      = datetime.datetime.now()
		dia      = int(now.strftime("%d"))
		mes      = int(now.strftime("%m"))
		fecha    = (mes, dia) 

		paises = []
		foo    = 0
		ejecucion = False

		aux_list_agentes 	= self.list_agentes
		aux_list_cant_leads = self.list_cant_leads
		aux_list_tasat_conv = self.list_tasat_conv

		indices_agentes = []

		feriados_mexico    = feriados.mexico()
		feriados_colombia  = feriados.colombia()
		feriados_salvador  = feriados.salvador()
		feriados_nicaragua = feriados.nicaragua()
		feriados_venezuela = feriados.venezuela()
		feriados_honduras  = feriados.honduras()

		for i in feriados_mexico:
			if fecha==i:
				paises.append(156)
				ejecucion = True
		for i in feriados_colombia:
			if fecha==i:
				paises.append(49)
				ejecucion = True
		for i in feriados_salvador:
			if fecha==i:
				paises.append(209)
				ejecucion = True
		for i in feriados_nicaragua:
			if fecha==i:
				paises.append(164)
				ejecucion = True
		for i in feriados_venezuela:
			if fecha==i:
				paises.append(238)
				ejecucion = True
		for i in feriados_honduras:
			if fecha==i:
				paises.append(299)
				ejecucion = True


		for agente in aux_list_agentes:
			pais_agente = self.env['res.users'].browse(agente).country_id.id

			if pais_agente in paises:
				indices_agentes.append(aux_list_agentes.index(agente))
		
		for indice in sorted(indices_agentes, reverse=True):
			del aux_list_agentes[indice]
			del aux_list_cant_leads[indice]
			del aux_list_tasat_conv[indice]

		# Filtrado
		if (len(aux_list_agentes) > 0) and (ejecucion == True):
			self.list_agentes 	 = aux_list_agentes
			self.list_cant_leads = aux_list_cant_leads
			self.list_tasat_conv = aux_list_tasat_conv
			return True
		else:
			return False


	def filtro_horario(self):
		semana = int(datetime.datetime.now().weekday())
		hora   = int(datetime.datetime.now().strftime('%H'))
		minu   = int(datetime.datetime.now().strftime('%M'))

		aux_list_agentes 	= self.list_agentes
		aux_list_cant_leads = self.list_cant_leads
		aux_list_tasat_conv = self.list_tasat_conv

		ejecucion = False
		indices_agentes = []
		def_agentes = []
		def_leads = []
		def_tasa = []
		paises = []

		if (hora-4 in range(9,17)) and (semana in range(4)):
			paises.append(238)

		if (hora-5 in range(9,17)) and (semana in range(5)):
			if (semana == 5):
				if (hora-5 < 12):
					paises.append(49)
					paises.append(156)
				else:
					paises.append(156)
			else:
				paises.append(49)
				paises.append(156)


		if (hora-6 in range(9,17)) and (semana in range(5)):
			if (semana == 5):
				paises.append(156)
			else:
				paises.append(164)
				paises.append(209)
				paises.append(156)


		if (hora-7 in range(9,17)) and (semana in range(5)):
			paises.append(156)


		for agente in aux_list_agentes:
			pais_agente = self.env['res.users'].browse(agente).country_id.id

			if pais_agente in paises:
				ejecucion = True
				indices_agentes.append(aux_list_agentes.index(agente))
		
		for indice in sorted(indices_agentes, reverse=True):

			if not(indice in indices_agentes):
				def_agentes.append(aux_list_agentes[indice])
				def_leads.append(aux_list_cant_leads[indice])
				def_tasa.append(aux_list_tasat_conv[indice])

		# Filtrado
		if (len(def_agentes) > 0) and (ejecucion == True):
			self.list_agentes 	 = def_agentes
			self.list_cant_leads = def_leads
			self.list_tasat_conv = def_tasa
			return True
		else:
			return False		

	def viejo_lead(self):

		agente = ''
		aux    = False
		aux2   = False
		todos_leads = self.env['crm.lead'].search([])

		telefonos = []
		emails    = []
		agentes   = []

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
				aux  = False
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

		viejo_agente = ''
		
		for agente in self.dic_agents["Agente"]:
				if agente == self.viejo_lead():
					viejo_agente = agente
					break
		if viejo_agente:
			return True
		else:
			 return False

	
	def filtro_area_agente(self):
		
		agentes_misma_area = []
		
		aux_agentes = self.list_agentes
		
		area_lead   = self.area_lead
		area_agent  = self.env['atributos.agentes'].search([('area_curso', '=', area_lead)])
		
		for agente in area_agent:
			agentes_misma_area.append(agente.agente_name.id)

		coincidencias = list( set(aux_agentes) & set(agentes_misma_area) )

		if (len(coincidencias) > 0) and (area_lead != None):
			
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

		aux_agentes = self.list_agentes

		lead_pais = self.localidad
		agen_pais = self.env['res.users'].search([('security_role_ids', '=', 'Ventas / Asesor'), ('country_id', '=', lead_pais)])

		agentes_mismo_pais = []
		for agentes in agen_pais:
			agentes_mismo_pais.append(agentes.id)


		set_agentes_disponibles = set(aux_agentes)
		set_agentes_mismo_pais  = set(agentes_mismo_pais)

		coincidencias = set_agentes_disponibles & set_agentes_mismo_pais
		
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


	def filtro_num_max_leads(self):

		li_agentes    = self.list_agentes
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

		agentes    = []
		tasas      = []
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
		menor = 10000
		lista = []
		index = 0
		mayor = 0

		for i in self.list_cant_leads:
			if i < menor:
				menor = i

		for i in self.list_cant_leads:
			if i == menor:
				lista.append(self.list_agentes[index])    
			index += 1

		index = 0
		for i in lista:

			if i > mayor:
				mayor = i
				index += 1

		agente = lista[index-1]

		return agente