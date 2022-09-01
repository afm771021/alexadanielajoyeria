from odoo import fields, models


class HrEmployeePrivate(models.Model):
    _inherit = 'hr.employee'

    identification_id = fields.Char(string='Identification No.', required=True, groups="hr.group_hr_user", tracking=True)
    _sql_constraints = [
        ('identification_id_unique', 'unique(identification_id)', 'Ya existe un usuario con esta identificación!')
    ]