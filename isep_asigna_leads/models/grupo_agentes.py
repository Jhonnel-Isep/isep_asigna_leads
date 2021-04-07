from odoo import models, fields
# Modulo para asignar automaticamente leads a agentes de ventas
# 
# 
#
# Queda pentiene:
# -Crear los grupo_agentes en la bdd y asignar los agentes a estos grupos 
#  (Los agentes estan en el excel)
# -La funcion que asigna el lead
# 
#
# Estructura:
# -Clase Acciones al crear lead
# -Clases con datos de dias festivos (Para calcular la asignacion del lead)
#--------------------------------------------------------------------------


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def create(self, values): # Cuando se crea el lead se ejecuta para asignar agente
        agente = values.get('user_id')
        self.localidad = values.get('country_id')
        # 68 = España, 

        if agente:
            agente = self.asigna_agente()
        

    def asigna_agente(self, values): # Aqui va la funcion que asigna el agente al lead
        
        list_agentes = []
        list_cant_leads = []
        list_tasat_conv = []

        if (self.localidad == 68):

          li_agentes = self.env['security.role'].browse().user_ids # id = ?

          for agente in li_agentes:

            list_agentes.append(agente)

            cant_leads = 0
            tasa_conv = []

            leads_agent = self.env['crm.lead'].search([('user_id', '=', agente.id)])

            for leads in leads_agent:

              if (leads.type == 'lead'):
                cant_leads += 1

              tasa_conv.append(leads.probability)

            list_cant_leads.append(cant_leads)
            tasat_conv = sum(tasa_conv) / len(tasa_conv)
            list_tasat_conv.append(tasat_conv)

          self.dic_agents = {'Agente':list_agentes, 'Numero de Leads':list_cant_leads, 'Tasa de Conversion':list_tasat_conv}



        else:

          li_agentes = self.env['security.role'].browse().user_ids # id = ?

          for agente in li_agentes:

            if not(agente.country_id.name.lower() in filtro_feriado()):
              # aqui se filtran agentes dia feriado
              list_agentes.append(agente)

              cant_leads = 0
              tasa_conv = []

              leads_agent = self.env['crm.lead'].search([('user_id', '=', agente.id)])

              for leads in leads_agent:

                if (leads.type == 'lead'):
                  cant_leads += 1

                tasa_conv.append(leads.probability)

              list_cant_leads.append(cant_leads)

              tasat_conv = sum(tasa_conv) / len(tasa_conv)
              list_tasat_conv.append(tasat_conv)

          self.dic_agents = {'Agente':list_agentes, 'Numero de Leads':list_cant_leads, 'Tasa de Conversion':list_tasat_conv}
          

    def selec_agente(self):
      menor=10000
      lista=[]
      index=0
      mayor=0
      for i in dic_agents["Numero de Leads"]:
           if i < menor:
               menor=i
      for i in dic_agents["Numero de Leads"]:
          if i ==menor:
              lista.append(dic_agents["Agente"][index])
          index+=1

      index=0
      for i in lista:
         if i > mayor:
             mayor =i
             index+=1
      agente = lista[index-1]

      return agente # retorna el agente seleccionado


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

#-----------------------------------------------------------

