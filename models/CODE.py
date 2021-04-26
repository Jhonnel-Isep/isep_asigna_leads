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


	def area_agente(self):

		# Incialmente se trae el area a la cual corresponde la iniciativa:
		area_lead = self.area_lead

		# Buscamos los agentes segun el area en el cual trabajan:
		area_agent = self.env['res.users'].search([('NOMBRE DE LA VARIABLE', '=', area_lead)])
		# Esto es para el caso en el cual en res.users se agrege el campo son esta el area del agente. 
		# El NOMBRE DE LA VARIABLE (en OpenEduCat) es 'name' (model=op.area.course)

		agentes_misma_area = []

		for agentes in area_agent:
			agentes_misma_area.append(agentes.id)

		if (len(agentes_misma_area) == 0):
			# Caso de lista vacia
		
		else:
			return agentes_misma_area



	def num_max_leads(self):

		# Treamos el campo de la cantidad de leads maximos, la lista de agentes y la lista con la cantidad de leads por agente:
		max_leads = self.max_leads
		li_agentes = self.list_agentes
		li_cant_leads = self.list_cant_leads


	
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