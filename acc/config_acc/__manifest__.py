{
    'name' : 'Configuraciones varias de Agencia Cordoba Conectividad',
    'version' : '1.0',
    'author' : 'Adolfo Arbach',
    'description' : """
Configuraciones varias de ACC
""",
    'depends' : ['base','crm','project','sale','sale_project','l10n_ar'],
    'data' : ['security/ir.model.access.csv',
              'security/groups.xml',
              'security/crm_stages.xml',
              'view/crm_view.xml',
              'view/menu.xml'],
    'installable' : True,
    'application' : True,
}