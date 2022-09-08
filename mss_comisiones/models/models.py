# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta

class mss_comisiones(models.Model):
     _name = 'mss_comisiones.mss_comisiones'
     _description = 'mss_comisiones.mss_comisiones'

     sale_amount_min = fields.Float(string='Monto de venta mínimo')
     sale_amount_max = fields.Float(string="Monto de venta máximo")
     sale_commision = fields.Float(string='Comisión de venta')
     sale_level = fields.Selection([('1', 'Nivel 1'), ('2', 'Nivel 2'), ('3', 'Nivel 3')], string='Nivel')
     commision_status = fields.Boolean(string='Activo')



class mss_commission_to_pay(models.Model):
     _name= 'mss_commissions.commissions_to_pay'
     _description = 'Registro de las comisiones a pagar'

     sale_id = fields.Many2one(string='Nota de Venta', comodel_name='sale.order', required=True)
     seller_id = fields.Many2one(string='Vendedor(a)', comodel_name='hr.employee', required=True)
     sale_amount = fields.Float(string="Monto de la Nota", store=True)
     commission_amount = fields.Float(string="Monto de comisión", compute="_commission_amount", store=True)
     sale_date = fields.Datetime(string='Fecha venta')
     commission_pay_date = fields.Datetime(string='Fecha pago de comisión')
     commission_paid = fields.Float(string="Comision pagada")
          # fields.Many2one(
          # 'res.users', string='Salesperson', index=True, tracking=2, default=lambda self: self.env.user,
          # domain=lambda
          #      self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]".format(
          #      self.env.ref("sales_team.group_sale_salesman").id
          # ), )
          #fields.Many2one(string='Usuario', comodel_name='res.users', required=True)

     def pay_commissions(self):
          print ('boton header')

     @api.depends('commission_amount', 'sale_amount')
     def _commission_amount(self):
          for record in self:
               record.commission_amount = float(record.sale_amount) * 0.1

class CustomSaleOrder(models.Model):
     _inherit = 'sale.order'

     seller_id = fields.Many2one(string='Vendedor(a)', comodel_name='hr.employee', required=True)
     commission_paid = fields.Boolean(String="Comisión pagada", default="False")


class LogGetCommissions(models.Model):
     _name = 'mss_commissions.loggetcommissions'
     _description = 'Generación de registros para pago de comisiones'

     logdate = fields.Datetime(string="Fecha")
     logcomments = fields.Text(string="Comentarios")
     logstatus = fields.Boolean(string="Generados", readonly=True)

     def button_generar(self):
          print('hola desde el boton')
          self.logstatus = True
          orders = self.env['sale.order'].search([('invoice_status', '=', 'invoiced'), ('commission_paid', '=', False)])
          for order in orders:
               # Buscar que no exista ya la Orden en la tabla de pago de comisiones
               registered_orders = self.env['mss_commissions.loggetcommissions'].search_count([('sale_id', '=', order.id)])

               # Si no existe la Orden
               if registered_orders == 0:
                    print('search():', order, order.name, order.seller_id, order.seller_id.id)
                    empleado = self.env['hr.employee'].search([('id', '=', order.seller_id.id)])
                    print('search():', empleado, empleado.id, empleado.parent_id, empleado.name)
                    print('search():', empleado.id, empleado.parent_id.name, empleado.name)
                    _commissions_to_pay = {
                         'sale_id': order.id,
                         'seller_id': order.seller_id.id,
                         'sale_amount': order.amount_total,
                         'commission_amount': 0.0,
                         'sale_date': order.date_order,
                         'commission_paid': False
                    }
                    print(_commissions_to_pay)
                    self.env['mss_commissions.commissions_to_pay'].create(_commissions_to_pay)


     #logdate
     #logcomments
     #logstatus
     #loguserid

     # @api.onchange('seller_id')
     # def _seller_id_change(self):
     #      print('cambio de valor...seller_id')
     #
     # @api.onchange('payment_term_id')
     # def onchange_payment_term_id(self):
     #      print ('cambio de valor...payment_term_id')
     #
     # @api.onchange('state')
     # def onchange_state(self):
     #      print('cambio de valor...state')



# class mss_comisiones_registradas(models.Model):
#      _name = 'mss_comisiones.mss_comisiones_registradas'
#      _description = 'Comisiones registradas para empleados'
#
#      sale_id = fields.Many2one(string='venta',comodel_name='sale.order')
#      sale_amount = fields.Monetary(string='Monto venta', currency_field='company_currency', tracking=True,
#                                    translate=True)
#      seller_id = fields.Many2one(string='Vendedor', comodel_name='hr.employee')
#      sale_date = sale_id.date_order
#      sale_commission_date_payment = fields.Datetime(string='Fecha')
#      employee_pay_id = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user)
#      commision_status = fields.Boolean(string='Pagada')
#
#      company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True,
#                                         relation="res.currency")
#      company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)

     #_sql_constraints = [
     #     ('sale_amount', 'unique(sale_amount,sale_commision,sale_level', 'Ya existe un registro con los mismos valores!')]

#    partner_type = fields.Selection('hr.employee', related='resource_id.name')

#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
