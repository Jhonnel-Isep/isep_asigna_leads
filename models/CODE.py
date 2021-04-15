from odoo import models, api, fields

class CrmLead(models.Model):
	_inherit = 'crm.lead'

	@api.model
	def create(self, values): # Cuando se crea el lead se ejecuta para asignar agente
		self.agente = values.get('user_id')
		self.telf = values.get('phone')
		self.mail = values.get('email_from')
		self.localidad = values.get('country_id')
		# 68 = España, 
		
		#if self.viejo_lead():
		#	values.update({'user_id': self.viejo_lead()})

		if not self.agente:
			self.asigna_agente()
			values.update({'user_id': self.selec_agente()})

		res = super(CrmLead, self).create(values)
		return res

	# def viejo_lead(self):
	# 	#todos_leads = # Farjan leads (telf[0], correo[1] el agente[2] "actual") [[telf,telf...],[mail,mail...],[agente,agente...]]

	# 	todos_leads = self.env['crm.lead'].search([])

	# 	telefonos = []
	# 	emails = []
	# 	agentes = []

	# 	for lead in todos_leads:
	# 		telefonos.append(lead.phone)
	# 		emails.append(lead.email_from)
	# 		agentes.append(lead.user_id)

	# 	li_todos_leads = [telefonos, emails, agentes]
		
	# 	for telf in li_todos_leads[0]:
	# 		if self.telf  == telf:
	# 			indice = li_todos_leads[0].index(telf)
	# 			agente =  li_todos_leads[2][indice]
			

	# 	for mail in li_todos_leads[1]:
	# 		if self.mail  == mail:
	# 			indice = li_todos_leads[1].index(mail)
	# 			agente =  li_todos_leads[2][indice]
			
	# 	return agente.id


	def asigna_agente(self):
		list_agentes = []
		list_cant_leads = []
		list_tasat_conv = []

		if (self.localidad == 68):

			li_agentes = self.env['security.role'].browse(139).user_ids ### --> COLOCAR EL ID DEL ROL DE ESPAÑA <-- ###

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

			li_agentes = self.env['security.role'].browse(140).user_ids ### --> COLOCAR EL ID DEL ROL DE LATAM <-- ###

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
				paises.append("salvador")
		for i in nicaragua:
			if fecha==i:
				paises.append("nicaragua")

		return paises


	def selec_agente(self):
		
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

		else:
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
