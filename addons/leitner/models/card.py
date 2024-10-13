from odoo import models, fields, api

from bs4 import BeautifulSoup


class Card(models.Model):
    _name = "leitner.card"
    _inherit = ["mail.thread"]
    _description = "A Leitner System card"
    _order = "name"
    _check_company_auto = True

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    front = fields.Html()
    front_txt = fields.Char(compute="_compute_front_txt", tracking=True)
    back = fields.Html()
    back_txt = fields.Char(compute="_compute_back_txt", tracking=True)
    deck_ids = fields.Many2many(
        "leitner.deck",
        "leitner_card_deck_rel",
        "card_id",
        "deck_id",
        check_company=True,
        tracking=True,
    )

    @api.depends("front")
    def _compute_front_txt(self):
        for c in self:
            c.front_txt = BeautifulSoup(c.front, features="lxml").get_text("\n")

    @api.depends("back")
    def _compute_back_txt(self):
        for c in self:
            c.back_txt = BeautifulSoup(c.back, features="lxml").get_text("\n")
