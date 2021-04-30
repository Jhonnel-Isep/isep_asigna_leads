{ 
    'name': 'Asigna leads', 
    'description': 'Asigna leads automaticamente a agentes de ventas en funcion de disponibilidad y tasa de conversión', 
    'author': 'Jhonnel Nuñez, Farjan Rondón', 
    
    'depends': [
        'base', 
        'crm', 
        'sales_team', 
        'security_user_roles'
    ],
    
    'data': [
        'views/AtributosAgentes.xml',  
        'views/AutoLeadLogRegister.xml',

        'menu/isep_asigna_leads_menu.xml'
    ],
    
    'application': True, 
}