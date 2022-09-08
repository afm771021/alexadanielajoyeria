# -*- coding: utf-8 -*-
# from odoo import http


# class MssComisiones(http.Controller):
#     @http.route('/mss_comisiones/mss_comisiones', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mss_comisiones/mss_comisiones/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mss_comisiones.listing', {
#             'root': '/mss_comisiones/mss_comisiones',
#             'objects': http.request.env['mss_comisiones.mss_comisiones'].search([]),
#         })

#     @http.route('/mss_comisiones/mss_comisiones/objects/<model("mss_comisiones.mss_comisiones"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mss_comisiones.object', {
#             'object': obj
#         })
