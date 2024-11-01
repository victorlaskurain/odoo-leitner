from odoo import models, fields, api, _
from odoo.fields import Command


class Deck(models.Model):
    _name = "leitner.deck"
    _inherit = ["mail.thread"]
    _description = "A Leitner System deck"
    _order = "name"
    _check_company_auto = True

    name = fields.Char(required=True, translate=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    card_ids = fields.Many2many(
        "leitner.card",
        "leitner_card_deck_rel",
        "deck_id",
        "card_id",
        check_company=True,
    )
    number_of_cards = fields.Integer(compute="_compute_number_of_cards")

    @api.depends("card_ids")
    def _compute_number_of_cards(self):
        for deck in self:
            deck.number_of_cards = len(deck.card_ids)

    def action_edit_form(self):
        return {
            "name": self.name,
            "res_model": "leitner.deck",
            "res_id": self.id,
            "views": [(self.env.ref("leitner.leitner_deck_view_form").id, "form")],
            "view_mode": "form",
            "type": "ir.actions.act_window",
        }

    def action_show_cards(self):
        return {
            "name": _("Cards of %s") % self.name,
            "res_model": "leitner.card",
            "view_mode": "kanban,list,form",
            "context": {"default_deck_ids": [(Command.LINK, self.id, 0)]},
            "domain": [("deck_ids", "=", self.id)],
            "target": "current",
            "type": "ir.actions.act_window",
        }

    def action_new_box(self):
        return {
            "name": self.name,
            "res_model": "leitner.box_set",
            "view_mode": "form",
            "context": {"default_deck_id": self.id},
            "type": "ir.actions.act_window",
        }
