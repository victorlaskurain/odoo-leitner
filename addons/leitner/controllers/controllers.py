# -*- coding: utf-8 -*-
# from odoo import http


# class Leitner(http.Controller):
#     @http.route('/leitner/leitner', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/leitner/leitner/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('leitner.listing', {
#             'root': '/leitner/leitner',
#             'objects': http.request.env['leitner.leitner'].search([]),
#         })

#     @http.route('/leitner/leitner/objects/<model("leitner.leitner"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('leitner.object', {
#             'object': obj
#         })
