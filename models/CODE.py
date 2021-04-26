from odoo import models, api, fields
import FeriadosLatam
import datetime


class CrmLead(models.Model):
	_inherit = 'crm.lead'

	@api.model
	def create(self, values):
		self.agente = values.get('user_id')
		self.telf = values.get('phone')
		self.mail = values.get('email_from')
		self.localidad = values.get('country_id')
		self.fecha_entrada = values.get('create_date')
		# 68 = España, 
	
		if not self.agente:
			self.diccionario_agentes()
			if self.asigna_anterior() == False: # Si no se asigna a un agente anterior
				self.area_agente()
				self.preferencia_pais()
				self.num_max_leads()
				values.update({'user_id': self.selec_agente()})	
					
			
		res = super(CrmLead, self).create(values)
		return res

	def diccionario_agentes(self): # Filtro 1 y 2
		self.list_agentes = []
		self.list_cant_leads = []
		self.list_tasat_conv = []
		dic_agents = {}

		if (self.localidad == 68):

			li_agentes = self.env['security.role'].browse(2).user_ids ### --> COLOCAR EL ID DEL ROL DE ESPAÑA <-- ###

			for agente in li_agentes:

				self.list_agentes.append(agente.id)

				cant_leads = 0
				tasa_conv = []

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

			self.dic_agents = {'Agente':self.list_agentes, 'Numero de Leads':self.list_cant_leads, 'Tasa de Conversion':self.list_tasat_conv}



		else:

			li_agentes = self.env['security.role'].browse(3).user_ids ### --> COLOCAR EL ID DEL ROL DE LATAM <-- ###

			for agente in li_agentes:

				if not(agente.country_id.name.lower() in self.filtro_feriado()): # Filtrado de agentes feriados
					if not(agente.country_id.name.lower() in self.filtro_horario): # Filtro de agentes Horario
						self.list_agentes.append(agente.id)

						cant_leads = 0
						tasa_conv = []	

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
					else:
						self.list_agentes.append(agente.id)

						cant_leads = 0
						tasa_conv = []	

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
			# Lista con filtro 1 y 2
			self.dic_agents = {'Agente':self.list_agentes, 'Numero de Leads':self.list_cant_leads, 'Tasa de Conversion':self.list_tasat_conv}
			# Final For lista filtro 1 y 2

			# Leads Fuera de Horario y Feriados
			if self.dic_agents == {}:
				li_agentes = self.env['security.role'].browse(3).user_ids ### --> COLOCAR EL ID DEL ROL DE LATAM <-- ###

				for agente in li_agentes:

					self.list_agentes.append(agente.id)

					cant_leads = 0
					tasa_conv = []

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

				self.dic_agents = {'Agente':self.list_agentes, 'Numero de Leads':self.list_cant_leads, 'Tasa de Conversion':self.list_tasat_conv}



	def asigna_anterior(self):
		
		for i in self.dic_agents["Agente"]:
				if i == viejo_lead():
					agent = i
					values.update({'user_id': self.viejo_lead()})					
					break
		if agent:
			return True
		else:
			 return False		
				
		
	def filtro_feriado(self):

		feriados = FeriadosLatam.Feriados_Latam()
		now = datetime.datetime.now()
		dia = int(now.strftime("%d"))
		mes = int(now.strftime("%m"))

		fecha = (mes, dia)

		paises=[]
		#mes, dia
		mexico = feriados.mexico()
		colombia = feriados.colombia()
		salvador = feriados.salvador()
		nicaragua = feriados.nicaragua()
		venezuela = feriados.venezuela()
		honduras = feriados.honduras()

		for i in mexico:
			if fecha==i:
				paises.append("mexico")
		for i in colombia:
			if fecha==i:
				paises.append("colombia")
		for i in salvador:
			if fecha==i:
				paises.append("el salvador")
		for i in nicaragua:
			if fecha==i:
				paises.append("nicaragua")
		for i in venezuela:
			if fecha==i:
				paises.append("venezuela")
		for i in honduras:
			if fecha==i:
				paises.append("honduras")

		return paises


	def filtro_horario(self):

		week = int(self.fecha_entrada.weekday())
		hora = int(self.fecha_entrada.strftime('%H'))
		minu = int(self.fecha_entrada.strftime('%M'))

		paises = []

		if (hora-4 in range(9,17)) and (week in range(4)):
			paises.append('venezuela')


		if (hora-5 in range(9,17)) and (week in range(5)):
			if (week == 5):
				if (hora-5 < 12):
					paises.append('colombia')
					paises.append('mexico (cdmx)')
				else:
					paises.append('mexico (cdmx)')
			else:
				paises.append('colombia')
				paises.append('mexico (cdmx)')


		if (hora-6 in range(9,17)) and (week in range(5)):
			if (week == 5):
				paises.append('mexico (la paz)')
			else:
				paises.append('nicaragua')
				paises.append('el salvador')
				paises.append('mexico (la paz)')


		if (hora-7 in range(9,17)) and (week in range(5)):
			paises.append('tijuana')


		if (len(paises) == 0):
			self.viejo_lead()

		else:
			return paises


	
	def preferencia_pais(self):

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


	def area_agente(self):

		# Traemos a los agentesde la lista de agentes del diccionario:
		aux_agentes = self.list_agentes

		# Traemos a todos los agentes los cuales se encuentran en el area del agente:
		area_lead = self.area_lead
		area_agent = self.env['res.users'].search([('NOMBRE DE LA VARIABLE', '=', area_lead)])
		

		agentes_misma_area = []
		for agente in area_agent:
			agentes_misma_area.append(agente.id)

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



	def num_max_leads(self):

		# SUPONIENDO QUE LA VARIBLE DE LA CANTIDAD MAXIMA DE LEADS ES: "max_leads".

		li_agentes = self.list_agentes
		li_cant_leads = self.list_cant_leads
		li_tasat_conv = self.list_tasat_conv

		cant_max_leads = []
		for agente in li_agentes:
			agent = slef.env['res.users'].browse(agente)
			cant_max_leads.append(agent.max_leads)

		macro_list = []
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
			agentes.append(lead.user_id) ### --> COLOCAR EL FIELD DE "ACTUAL" <-- ###

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



	def selec_agente(self):

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