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

     sale_id = fields.Many2one(string='Nota de Venta', comodel_name='sale.order', required=True, readonly=True)
     seller_id = fields.Many2one(string='Vendedor(a)', comodel_name='hr.employee', required=True, readonly=True)
     seller_level = fields.Selection([('1', 'Nivel 1'), ('2', 'Nivel 2'), ('3', 'Nivel 3')], string='Nivel', readonly=True)
     sale_amount = fields.Float(string="Monto de la Nota", store=True, readonly=True)
     commission_amount = fields.Float(string="Monto de comisión", store=True, readonly=True)     # compute="_commission_amount", store=True)
     sale_date = fields.Datetime(string='Fecha venta', readonly=True)
     commission_pay_date = fields.Datetime(string='Fecha pago de comisión', readonly=True)
     commission_paid = fields.Float(string="Comision pagada", readonly=True)
     commision_status = fields.Boolean(string="Pagada", readonly=True)

     def pay_commissions(self):
          print ('boton header')
          order_paid = True
          for record in self:
               record.commision_status = True
               if record.commission_paid == 0.0:
                    record.commission_pay_date = datetime.strftime(fields.Datetime.context_timestamp(record, datetime.now()), "%Y-%m-%d %H:%M:%S")
                    record.commission_paid = record.commission_amount
                    sellers = self.env['mss_commissions.commissions_to_pay'].search([('sale_id', '=', record.sale_id.id)])
                    print(sellers)
                    print('seller.comission_status')
                    for seller in sellers:
                         print(seller)
                         if not seller.commision_status:
                              order_paid = False
                    print(order_paid)
                    if order_paid:
                         print(record.sale_id.id)
                         order = self.env['sale.order'].search([('id', '=', record.sale_id.id)])
                         order.write({
                              'commission_paid': True
                         })
                         print(order)

class CustomSaleOrder(models.Model):
     _inherit = 'sale.order'

     seller_id = fields.Many2one(string='Vendedor(a)', comodel_name='hr.employee', required=True)
     commission_paid = fields.Boolean(String='Comisión pagada', default=False, readonly=True)


class LogGetCommissions(models.Model):
     _name = 'mss_commissions.loggetcommissions'
     _description = 'Generación de registros para pago de comisiones'

     logdate = fields.Datetime(string='Fecha', default=datetime.now(), readonly=True)
     logcomments = fields.Text(string='Comentarios')
     logstatus = fields.Boolean(string='Generados', readonly=True)


     def button_generar(self):
          print('hola desde el boton')
          commission_value = 0
          sale_sellers_to_pay = 0
          saleorder_no_commission = 0
          self.logstatus = True
          orders = self.env['sale.order'].search([('invoice_status', '=', 'invoiced'), ('commission_paid', '=', False)])
          for order in orders:
               # Buscar que no exista ya la Orden en la tabla de pago de comisiones
               registered_orders = self.env['mss_commissions.commissions_to_pay'].search_count([('sale_id', '=', order.id)])

               # Si no existe la Orden
               if registered_orders == 0:
                    print('La orden a pagar no ha sido registrada anteriormente, numero de orden:')
                    print(order.id)
                    # Buscamos en el catálogo de comisiones el valor para calcular la comisión del nivel N1
                    _commission_valuesN1 = self.env['mss_comisiones.mss_comisiones'].search([('sale_level', '=', 1), ('commision_status', '=', True)])
                    for _commission_value in _commission_valuesN1:
                         if order.amount_total >= _commission_value.sale_amount_min and order.amount_total <= _commission_value.sale_amount_max:
                              commission_value = _commission_value.sale_commision
                              break
                         else:
                              commission_value = 0.0
                    # Guardamos el registro para el pago de la comision a nivel N1
                    print('vendedor N1:')
                    print(order.seller_id.id)
                    sale_sellers_to_pay = sale_sellers_to_pay + 1
                    _commissions_to_pay = {
                         'sale_id': order.id,
                         'seller_id': order.seller_id.id,
                         'seller_level': '1',
                         'sale_amount': order.amount_total,
                         'commission_amount': commission_value,
                         'sale_date': order.date_order,
                         'commission_paid': 0.0,
                         'commision_status': False
                    }

                    if commission_value > 0.0:
                         self.env['mss_commissions.commissions_to_pay'].create(_commissions_to_pay)
                         print(_commissions_to_pay)
                    else:
                         saleorder_no_commission = saleorder_no_commission + 1
                         print('No hay comision a pagar')

                    #Buscamos el empleado de nivel superior N2
                    #print('search():', order, order.name, order.seller_id, order.seller_id.id)
                    empleado = self.env['hr.employee'].search([('id', '=', order.seller_id.id)])
                    #print('empleado:')
                    #print(empleado)
                    #print('empleado.parent_id.id:')
                    #print(empleado.parent_id.id)

                    if empleado.parent_id:
                         _commission_valuesN2 = self.env['mss_comisiones.mss_comisiones'].search(
                              [('sale_level', '=', 2), ('commision_status', '=', True)])
                         for _commission_value in _commission_valuesN2:
                              if order.amount_total >= _commission_value.sale_amount_min and order.amount_total <= _commission_value.sale_amount_max:
                                   commission_value = _commission_value.sale_commision
                                   break
                              else:
                                   commission_value = 0.0
                         # Guardamos el registro para el pago de la comision a nivel N2

                         print('vendedor N2:')
                         print(empleado.parent_id.id)
                         sale_sellers_to_pay = sale_sellers_to_pay + 1

                         _commissions_to_pay = {
                              'sale_id': order.id,
                              'seller_id': empleado.parent_id.id,
                              'seller_level': '2',
                              'sale_amount': order.amount_total,
                              'commission_amount': commission_value,
                              'sale_date': order.date_order,
                              'commission_paid': 0.0,
                              'commision_status': False
                         }
                         if commission_value > 0.0:
                              self.env['mss_commissions.commissions_to_pay'].create(_commissions_to_pay)
                              print(_commissions_to_pay)
                         else:
                              saleorder_no_commission = saleorder_no_commission + 1
                              print('No hay comision a pagar')

                    # Buscamos el empleado de nivel superior N3
                    #print('search():', order, order.name, order.seller_id, order.seller_id.id)
                         empleado = self.env['hr.employee'].search([('id', '=', empleado.parent_id.id)])

                         if empleado.parent_id:
                              _commission_valuesN3 = self.env['mss_comisiones.mss_comisiones'].search(
                                   [('sale_level', '=', 3), ('commision_status', '=', True)])
                              for _commission_value in _commission_valuesN3:
                                   if order.amount_total >= _commission_value.sale_amount_min and order.amount_total <= _commission_value.sale_amount_max:
                                        commission_value = _commission_value.sale_commision
                                        break
                                   else:
                                        commission_value = 0.0
                              # Guardamos el registro para el pago de la comision a nivel N3
                              print('vendedor N3:')
                              print(empleado.parent_id.id)
                              sale_sellers_to_pay = sale_sellers_to_pay + 1

                              _commissions_to_pay = {
                                   'sale_id': order.id,
                                   'seller_id': empleado.parent_id.id,
                                   'seller_level': '3',
                                   'sale_amount': order.amount_total,
                                   'commission_amount': commission_value,
                                   'sale_date': order.date_order,
                                   'commission_paid': 0.0,
                                   'commision_status': False
                              }
                              if commission_value > 0.0:
                                   self.env['mss_commissions.commissions_to_pay'].create(_commissions_to_pay)
                                   print(_commissions_to_pay)
                              else:
                                   saleorder_no_commission = saleorder_no_commission + 1
                                   print('No hay comision a pagar')

                    #Si el numero de vendedores a pagar tienen comision 0.0 no se debe realizar ningun pago y se pone la orden como pagada
                    print(sale_sellers_to_pay)
                    print(saleorder_no_commission)
                    if sale_sellers_to_pay == saleorder_no_commission:
                         print ('No hay pago de comisiones, establecemos la orden como pagada')
                         order.write({
                              'commission_paid': True
                         })


                    # print('search():', empleado, empleado.id, empleado.parent_id, empleado.name)
                    #print('search():', empleado.id, empleado.parent_id.name, empleado.name)

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
