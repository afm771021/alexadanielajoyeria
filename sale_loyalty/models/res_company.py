# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    loyalty_id = fields.Many2one('sale.loyalty.program', string='Loyalty Program', copy=True)
