from odoo import models, api, fields

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
			self.asigna_agente()
			values.update({'user_id': self.viejo_lead()})

		res = super(CrmLead, self).create(values)
		return res

	def asigna_agente(self):
		list_agentes = []
		list_cant_leads = []
		list_tasat_conv = []

		if (self.localidad == 68):

			li_agentes = self.env['security.role'].browse(2).user_ids ### --> COLOCAR EL ID DEL ROL DE ESPAÑA <-- ###

			for agente in li_agentes:
            
				list_agentes.append(agente.id)

				cant_leads = 0
				tasa_conv = []

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

			self.dic_agents = {'Agente':list_agentes, 'Numero de Leads':list_cant_leads, 'Tasa de Conversion':list_tasat_conv}



		else:

			li_agentes = self.env['security.role'].browse(3).user_ids ### --> COLOCAR EL ID DEL ROL DE LATAM <-- ###

			for agente in li_agentes:

				if not(agente.country_id.name.lower() in self.filtro_feriado()):

					list_agentes.append(agente.id)

					cant_leads = 0
					tasa_conv = []

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

			self.dic_agents = {'Agente':list_agentes, 'Numero de Leads':list_cant_leads, 'Tasa de Conversion':list_tasat_conv}


	def filtro_feriado(self):

		import datetime

		now = datetime.datetime.now()
		dia = int(now.strftime("%d"))
		mes = int(now.strftime("%m"))

		fecha = (mes, dia)

		paises=[]
		#mes, dia
		mexico = [(1,1),(2,1),(3,15),(4,4),(5,1),(9,16),(11,15),(12,25)]
		colombia = [(1,1),(1,11),(3,22),(5,1),(5,17),(6,7),(6,14),(7,5),(7,20),(8,7),(8,16),(10,18),(11,1),(11,15),(12,8),(12,25)]
		salvador = [(1,1),(5,1),(5,10),(6,17),(8,5),(8,6),(9,15),(11,2),(12,25)]
		nicaragua = [(1,1),(5,1),(7,19),(8,1),(8,10),(9,14),(9,15),(12,8),(12,25)]

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

		return paises


	def filtro_horario(self):

		import datetime

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

		lead_pais = self.localidad
		agen_pais = self.env['res.users'].search([('security_role_ids', '=', 'Ventas / Asesor'), ('country_id', '=', lead_pais)])

		agentes_mismo_pais = []

		for agentes in agen_pais:
			agentes_mismo_pais.append(agentes.id)

		if (len(agentes_mismo_pais) == 0):
			##########
			# Llamar a la siguiente condición (numero maximo de leads) y retornarle la lista de agentes anterior a este filtro
			##########

		else:
			return agentes_mismo_pais


	
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

		else:
			agente = self.selec_agente()

			##########
			# Este 'else' es para colocar la funcion que se debe ejecutar en el caso de que el lead no haya sido atendido antes.
			##########

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