from odoo import fields, models


class HrEmployeePrivate(models.Model):
    _inherit = 'hr.employee'

    identification_id = fields.Char(string='Identification No.', required=True, groups="hr.group_hr_user", tracking=True)
