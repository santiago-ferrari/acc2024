{   
    'active': True,
    'author': 'Adolfo Arbach',
    'category': 'base.module_category_knowledge_management',
    'data': [   
                'data/sequence.xml',
                'data/datos_iniciales.xml',
                #'data/account_chart_pa.xml',
                #'data/account_tax_chart.xml',
                'security/security.xml',
                #'reports/presupuesto.xml',
                #'reports/presupuesto_compensacion.xml',
                'view/account_move.xml',
                'view/product_template.xml',                
                'view/purchase_order.xml',
                'wizard/compensacion_presupuesto.xml',
                'wizard/create_lineas_presupuesto.xml',
                'wizard/report/presupuesto.xml',
                'view/presupuesto.xml',
                'security/ir.model.access.csv',
                'view/menu.xml',             
            ],
 
    'depends': [
        'account','purchase','date_range','product',
    ],
    'auto_install': False,    
    'description': """
Administración presupuestaria para municipios, comunas y entes gubernamentales
=============
Modulo para gestión pública municipal presupuestaria/contable. El módulo crea presupuestos.
""",
    'application': True,
    'installable': True,
    'license': 'AGPL-3',
    'name': u'Administracion presupuestaria/contable',
    'test': [],
    'version': '16.0',
    'website': ''
}
