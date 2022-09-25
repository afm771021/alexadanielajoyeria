# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo.exceptions import ValidationError

class ad_comisiones(models.Model):
    _name = 'ad_comisiones.ad_comisiones'
    _description = 'Modelo para generacion de catalogo de comisiones'

    sale_criteria_type = fields.Selection([('I', 'Integrantes'), ('2', 'Monto Venta')], string='Criterio')
    sale_min = fields.Float(string='Mínimo')
    sale_max = fields.Float(string="Máximo")
    sale_commision_type = fields.Selection([('1', 'Monto'), ('2', 'Porcentaje')], string='Tipo Cálculo')
    sale_commision = fields.Float(string='Valor')
    sale_level = fields.Selection([('1', 'Nivel Lider'), ('2', 'Nivel Promotor')], string='Nivel')
    commision_status = fields.Boolean(string='Activo')

class CustomerAddInfo(models.Model):
    _inherit = 'res.partner'

    # Valor del crédito que tiene actualmente el venderor
    credit_amount = fields.Float(string='Crédito')
    # contacto que invito al vendedor actual
    guess_by = fields.Many2one(string='Invitador Por', comodel_name='res.partner')
    # RFC del vendedor
    vat = fields.Char(string='RFC', required=True, index=True)
    # Valor de comisiones ganadas
    commission_won = fields.Float(company_dependent=True)

    _sql_constraints = [
        ('vat', 'unique(vat)', 'Ya existe un registro con el mismo RFC !!')]

class CustomSaleOrder(models.Model):
    _inherit = 'sale.order'

    commission_paid = fields.Boolean(string='Comisión pagada', default=False, readonly=True)
    pending_amount = fields.Float(string='Saldo pendiente',compute="_pending_amount", readonly = True)


    @api.depends('partner_id')
    def _pending_amount(self):
        # se obtienen las facturas pendientes de pago y con pago parcial pendiente, se calcula y se muestra en pantalla
        sum_pending_payments = 0.0
        for record in self:
            pending_payments= self.env['account.move'].search([('partner_id', '=', record.partner_id.id),
                                            ('move_type', '=', 'out_invoice'),
                                            ('payment_state', 'in', ('not_paid','partial'))])
            for _pending_payment in pending_payments:
                sum_pending_payments = sum_pending_payments + _pending_payment.amount_residual

            record.pending_amount = sum_pending_payments


class GenerateCommissionsPeriod(models.Model):
    _name = 'ad_comisiones.ad_generacomisiones'
    _description = 'Modelo para generacion de comisiones'

    initDate = fields.Date(string='Fecha inicial', required=True)
    endDate = fields.Date(string='Fecha final', required=True)
    team_id = fields.Many2one('crm.team', string='Equipo', required=True)
    logdate = fields.Datetime(string='Fecha', default=datetime.now(), readonly=True)
    logcomments = fields.Text(string='Comentarios')
    commision_status = fields.Boolean(string="Generada", readonly=True)
    promotors = 0
    leaders = 0

    def button_generar(self):
        print('Generar Comisiones')
        self.commision_status = True
        sellers = []
        promotors = []
        leaders = []
        exist_promotor = False
        exist_seller = False
        exist_leader = False

        # Buscamos todas las ordenes con estatus de facturadas que no tengan comisione pagada y que sean de un equipo
        # de ventas en particular
        orders = self.env['sale.order'].search([('invoice_status', '=', 'invoiced'),
                                                ('commission_paid', '=', False),
                                                ('team_id', '=', self.team_id.id)])

        # Se recorren todas las ordenes para buscar los promotores y lideres
        for order in orders:
            print(order, order.amount_total)
            print('vendedor:', order.partner_id.id, order.partner_id.name)  # vendedor

            # si hay promotor
            if order.partner_id.guess_by.id:
                print('promotor:', order.partner_id.guess_by.id, order.partner_id.guess_by.name)
                if len(promotors) > 0:
                    for i in range(len(promotors)):
                        # for j in range(len(promotors[i])):
                        # si el promotor ya existe en arreglo le sumamos un vendedor
                        if order.partner_id.guess_by.id == promotors[i][0]:
                            # bucamos que el vendedor no se repita
                            for j in range(len(sellers)):
                                print(order.partner_id.id, sellers[j])
                                if order.partner_id.id == sellers[j]:
                                    exist_seller = True
                            # si el vencedor no existe, lo sumamos a la cuenta de vendedores del promotor
                            if not exist_seller:
                                promotors[i][1] = promotors[i][1] + 1
                                sellers.append(order.partner_id.id)
                            promotors[i][2] = promotors[i][2] + order.amount_total
                            exist_promotor = True
                            exist_seller = False

                    if not exist_promotor:
                        promotors.append([order.partner_id.guess_by.id, 1, order.amount_total,0.0])
                        sellers.append(order.partner_id.id)
                    exist_promotor = False
                else:
                    promotors.append([order.partner_id.guess_by.id, 1, order.amount_total,0.0])
                    sellers.append(order.partner_id.id)

             # si hay lider
            if order.partner_id.guess_by.guess_by.id:
                if len(leaders) > 0:
                    for i in range(len(leaders)):
                        # si el lider ya existe en arreglo
                        if order.partner_id.guess_by.guess_by.id == leaders[i][0]:
                            exist_leader = True
                            leaders[i][1] = leaders[i][1] + order.amount_total
                    if not exist_leader:
                        leaders.append([order.partner_id.guess_by.guess_by.id, order.amount_total,0.0])
                    exist_leader = False
                else:
                    leaders.append([order.partner_id.guess_by.guess_by.id, order.amount_total,0.0])
                # print(order.partner_id.guess_by.id)  # promotor
                # print(order.partner_id.guess_by.guess_by.id)  # lider
                # print(self.num_sellers_by_promotor(orders, order.partner_id.guess_by.id))

        print('Promotores - ventas')
        for i in range(len(promotors)):
            for j in range(len(promotors[i])):
                print(promotors[i][j], end=' ')
            print()

        print('Lider - ventas')
        for i in range(len(leaders)):
            for j in range(len(leaders[i])):
                print(leaders[i][j], end=' ')
            print()

        _commission_values_N1 = self.env['ad_comisiones.ad_comisiones'].search(
            [('sale_level', '=', 1), ('commision_status', '=', True)])

        _commission_values_N2_amount = self.env['ad_comisiones.ad_comisiones'].search(
            [('sale_level', '=', 2), ('sale_criteria_type','=','2'), ('commision_status', '=', True)])

        _commission_values_N2_num_per = self.env['ad_comisiones.ad_comisiones'].search(
            [('sale_level', '=', 2), ('sale_criteria_type', '=', 'I'), ('commision_status', '=', True)])

        for i in range(len(promotors)):

            for commisionN2_num_per in _commission_values_N2_num_per:
                if promotors[i][1] >= commisionN2_num_per.sale_min and promotors[i][1] <= commisionN2_num_per.sale_max:
                    promotors[i][3] = commisionN2_num_per.sale_commision

            for commisionN2_ammount in _commission_values_N2_amount:
                if promotors[i][2] >= commisionN2_ammount.sale_min:
                    promotors[i][3] = commisionN2_ammount.sale_commision

        for i in range(len(leaders)):
            leaders[i][2] = _commission_values_N1.sale_commision

        print('Promotores - ventas')
        for i in range(len(promotors)):
            for j in range(len(promotors[i])):
                print(promotors[i][j], end=' ')
            print()

        print('Lider - ventas')
        for i in range(len(leaders)):
            for j in range(len(leaders[i])):
                print(leaders[i][j], end=' ')
            print()


        for order in orders:
            print(order, order.id, order.amount_total)
            print('vendedor:', order.partner_id.id, order.partner_id.name)
            print('promotor:', order.partner_id.guess_by.id)
            print('lider:', order.partner_id.guess_by.guess_by.id)

            promotor = self.env['ad_commissions.commissions_to_pay'].search([('sale_id', '=', order.id),
                                                                             ('guess_by','=', order.partner_id.guess_by.id)])
            if not promotor:
                if order.partner_id.guess_by.id:
                    for i in range(len(promotors)):
                        if order.partner_id.guess_by.id == promotors[i][0]:
                            _commissions_to_pay = {
                                'sale_id': order.id,
                                'guess_by': order.partner_id.guess_by.id,
                                'seller_level': '2',
                                'sale_amount': order.amount_total,
                                'team_id': order.team_id.id,
                                'commission': promotors[i][3],
                                'commission_amount': (order.amount_total * promotors[i][3]) /100,
                                'sale_date': order.date_order,
                                'commission_paid': 0.0,
                                'commision_status': False
                            }
                            self.env['ad_commissions.commissions_to_pay'].create(_commissions_to_pay)

            lider = self.env['ad_commissions.commissions_to_pay'].search([('sale_id', '=', order.id),
                                                                ('guess_by', '=',order.partner_id.guess_by.guess_by.id)])
            if not lider:
                if order.partner_id.guess_by.guess_by.id:
                    for i in range(len(leaders)):
                        if order.partner_id.guess_by.guess_by.id == leaders[i][0]:
                            _commissions_to_pay = {
                                'sale_id': order.id,
                                'guess_by': order.partner_id.guess_by.guess_by.id,
                                'seller_level': '1',
                                'sale_amount': order.amount_total,
                                'team_id': order.team_id.id,
                                'commission': leaders[i][2],
                                'commission_amount': (order.amount_total * leaders[i][2]) /100,
                                'sale_date': order.date_order,
                                'commission_paid': 0.0,
                                'commision_status': False
                            }
                            self.env['ad_commissions.commissions_to_pay'].create(_commissions_to_pay)

    @api.constrains('endDate')
    def _check_endDate(self):
        for record in self:
            if record.endDate < record.initDate:
                raise ValidationError("Fecha final debe ser mayor a la fecha inicial")

class ad_commission_to_pay(models.Model):
     _name= 'ad_commissions.commissions_to_pay'
     _description = 'Registro de las comisiones a pagar'

     sale_id = fields.Many2one(string='Nota de Venta', comodel_name='sale.order', required=True, readonly=True)
     guess_by = fields.Many2one(string='Nombre', comodel_name='res.partner')
     seller_level = fields.Selection([('1', 'Lider'), ('2', 'Promotor')], string='Nivel', readonly=True)
     sale_amount = fields.Float(string="Monto de la Nota", store=True, readonly=True)
     team_id = fields.Many2one('crm.team', string='Equipo', required=True)
     commission = fields.Float(string="% comisión", store=True, readonly=True)
     commission_amount = fields.Float(string="Monto de comisión", store=True, readonly=True)     # compute="_commission_amount", store=True)
     sale_date = fields.Datetime(string='Fecha venta', readonly=True)
     commission_pay_date = fields.Datetime(string='Fecha pago de comisión', readonly=True)
     commission_paid = fields.Float(string="Comision pagada", readonly=True)
     commision_status = fields.Boolean(string="Pagada", readonly=True)

     # _sql_constraints = [
     #     ('record_uniq', 'unique(sale_id, guess_by)', 'Ya existe el registro de pago de comisión!'),
     # ]

     def pay_commissions(self):
        print ('boton header')
        for record in self:
            record.commision_status = True
            if record.commission_paid == 0.0:
                record.commission_pay_date = datetime.strftime(fields.Datetime.context_timestamp(record, datetime.now()), "%Y-%m-%d %H:%M:%S")
                record.commission_paid = record.commission_amount
                record.guess_by.commission_won += record.commission_amount

     #      order_paid = True
     #      for record in self:
     #           record.commision_status = True
     #           if record.commission_paid == 0.0:
     #                record.commission_pay_date = datetime.strftime(fields.Datetime.context_timestamp(record, datetime.now()), "%Y-%m-%d %H:%M:%S")
     #                record.commission_paid = record.commission_amount
     #                sellers = self.env['mss_commissions.commissions_to_pay'].search([('sale_id', '=', record.sale_id.id)])
     #                print(sellers)
     #                print('seller.comission_status')
     #                for seller in sellers:
     #                     print(seller)
     #                     if not seller.commision_status:
     #                          order_paid = False
     #                print(order_paid)
     #                if order_paid:
     #                     print(record.sale_id.id)
     #                     order = self.env['sale.order'].search([('id', '=', record.sale_id.id)])
     #                     order.write({
     #                          'commission_paid': True
     #                     })
     #                     print(order)
#
#
#
#
# class LogGetCommissions(models.Model):
#      _name = 'mss_commissions.loggetcommissions'
#      _description = 'Generación de registros para pago de comisiones'
#
#      logdate = fields.Datetime(string='Fecha', default=datetime.now(), readonly=True)
#      logcomments = fields.Text(string='Comentarios')
#      logstatus = fields.Boolean(string='Generados', readonly=True)
#
#
#      def button_generar(self):
#           print('hola desde el boton')
#           commission_value = 0
#           sale_sellers_to_pay = 0
#           saleorder_no_commission = 0
#           self.logstatus = True
#           orders = self.env['sale.order'].search([('invoice_status', '=', 'invoiced'), ('commission_paid', '=', False)])
#           for order in orders:
#                # Buscar que no exista ya la Orden en la tabla de pago de comisiones
#                registered_orders = self.env['mss_commissions.commissions_to_pay'].search_count([('sale_id', '=', order.id)])
#
#                # Si no existe la Orden
#                if registered_orders == 0:
#                     print('La orden a pagar no ha sido registrada anteriormente, numero de orden:')
#                     print(order.id)
#                     # Buscamos en el catálogo de comisiones el valor para calcular la comisión del nivel N1
#                     _commission_valuesN1 = self.env['ad_comisiones.ad_comisiones'].search([('sale_level', '=', 1), ('commision_status', '=', True)])
#                     for _commission_value in _commission_valuesN1:
#                          if order.amount_total >= _commission_value.sale_amount_min and order.amount_total <= _commission_value.sale_amount_max:
#                               commission_value = _commission_value.sale_commision
#                               break
#                          else:
#                               commission_value = 0.0
#                     # Guardamos el registro para el pago de la comision a nivel N1
#                     print('vendedor N1:')
#                     print(order.seller_id.id)
#                     sale_sellers_to_pay = sale_sellers_to_pay + 1
#                     _commissions_to_pay = {
#                          'sale_id': order.id,
#                          'seller_id': order.seller_id.id,
#                          'seller_level': '1',
#                          'sale_amount': order.amount_total,
#                          'commission_amount': commission_value,
#                          'sale_date': order.date_order,
#                          'commission_paid': 0.0,
#                          'commision_status': False
#                     }
#
#                     if commission_value > 0.0:
#                          self.env['mss_commissions.commissions_to_pay'].create(_commissions_to_pay)
#                          print(_commissions_to_pay)
#                     else:
#                          saleorder_no_commission = saleorder_no_commission + 1
#                          print('No hay comision a pagar')
#
#                     #Buscamos el empleado de nivel superior N2
#                     #print('search():', order, order.name, order.seller_id, order.seller_id.id)
#                     empleado = self.env['hr.employee'].search([('id', '=', order.seller_id.id)])
#                     #print('empleado:')
#                     #print(empleado)
#                     #print('empleado.parent_id.id:')
#                     #print(empleado.parent_id.id)
#
#                     if empleado.parent_id:
#                          _commission_valuesN2 = self.env['ad_comisiones.ad_comisiones'].search(
#                               [('sale_level', '=', 2), ('commision_status', '=', True)])
#                          for _commission_value in _commission_valuesN2:
#                               if order.amount_total >= _commission_value.sale_amount_min and order.amount_total <= _commission_value.sale_amount_max:
#                                    commission_value = _commission_value.sale_commision
#                                    break
#                               else:
#                                    commission_value = 0.0
#                          # Guardamos el registro para el pago de la comision a nivel N2
#
#                          print('vendedor N2:')
#                          print(empleado.parent_id.id)
#                          sale_sellers_to_pay = sale_sellers_to_pay + 1
#
#                          _commissions_to_pay = {
#                               'sale_id': order.id,
#                               'seller_id': empleado.parent_id.id,
#                               'seller_level': '2',
#                               'sale_amount': order.amount_total,
#                               'commission_amount': commission_value,
#                               'sale_date': order.date_order,
#                               'commission_paid': 0.0,
#                               'commision_status': False
#                          }
#                          if commission_value > 0.0:
#                               self.env['mss_commissions.commissions_to_pay'].create(_commissions_to_pay)
#                               print(_commissions_to_pay)
#                          else:
#                               saleorder_no_commission = saleorder_no_commission + 1
#                               print('No hay comision a pagar')
#
#                     # Buscamos el empleado de nivel superior N3
#                     #print('search():', order, order.name, order.seller_id, order.seller_id.id)
#                          empleado = self.env['hr.employee'].search([('id', '=', empleado.parent_id.id)])
#
#                          if empleado.parent_id:
#                               _commission_valuesN3 = self.env['ad_comisiones.ad_comisiones'].search(
#                                    [('sale_level', '=', 3), ('commision_status', '=', True)])
#                               for _commission_value in _commission_valuesN3:
#                                    if order.amount_total >= _commission_value.sale_amount_min and order.amount_total <= _commission_value.sale_amount_max:
#                                         commission_value = _commission_value.sale_commision
#                                         break
#                                    else:
#                                         commission_value = 0.0
#                               # Guardamos el registro para el pago de la comision a nivel N3
#                               print('vendedor N3:')
#                               print(empleado.parent_id.id)
#                               sale_sellers_to_pay = sale_sellers_to_pay + 1
#
#                               _commissions_to_pay = {
#                                    'sale_id': order.id,
#                                    'seller_id': empleado.parent_id.id,
#                                    'seller_level': '3',
#                                    'sale_amount': order.amount_total,
#                                    'commission_amount': commission_value,
#                                    'sale_date': order.date_order,
#                                    'commission_paid': 0.0,
#                                    'commision_status': False
#                               }
#                               if commission_value > 0.0:
#                                    self.env['mss_commissions.commissions_to_pay'].create(_commissions_to_pay)
#                                    print(_commissions_to_pay)
#                               else:
#                                    saleorder_no_commission = saleorder_no_commission + 1
#                                    print('No hay comision a pagar')
#
#                     #Si el numero de vendedores a pagar tienen comision 0.0 no se debe realizar ningun pago y se pone la orden como pagada
#                     print(sale_sellers_to_pay)
#                     print(saleorder_no_commission)
#                     if sale_sellers_to_pay == saleorder_no_commission:
#                          print ('No hay pago de comisiones, establecemos la orden como pagada')
#                          order.write({
#                               'commission_paid': True
#                          })


# print('search():', empleado, empleado.id, empleado.parent_id, empleado.name)
# print('search():', empleado.id, empleado.parent_id.name, empleado.name)


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
#      _name = 'ad_comisiones.mss_comisiones_registradas'
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


#    partner_type = fields.Selection('hr.employee', related='resource_id.name')

#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
