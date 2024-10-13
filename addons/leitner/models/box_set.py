from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.fields import Command



class BoxSet(models.Model):
    _name = "leitner.box_set"
    _description = "A deck spread into a set of boxes ready for use"
    _check_company_auto = True

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    user_id = fields.Many2one("res.users", "Owner", default=lambda self: self.env.user)
    deck_id = fields.Many2one("leitner.deck", required=True, check_company=True)
    boxed_card_ids = fields.One2many("leitner.boxed_card", "box_set_id")
    number_of_boxes = fields.Integer(required=True, default=4)
    number_of_cards = fields.Integer(compute="_compute_number_of_cards")
    is_answer_back = fields.Boolean(required=True, default=True)

    @api.model_create_multi
    def create(self, vals_list):
        box_sets = super().create(vals_list)
        box_sets._compute_boxed_card_ids()
        return box_sets

    def _compute_boxed_card_ids(self):
        for box_set in self:
            boxed_cards = [
                Command.create({"card_id": c.id, "sequence": i})
                for i, c in enumerate(box_set.deck_id.card_ids, 1)
            ]
            box_set.boxed_card_ids = boxed_cards

    @api.depends("boxed_card_ids")
    def _compute_number_of_cards(self):
        for box_set in self:
            box_set.number_of_cards = len(box_set.boxed_card_ids)

    def action_start_session(self):
        def get_next_card():
            return self.env["leitner.boxed_card"].search(
                [
                    ("box_set_id", "=", self.id),
                    ("box_number", "<", self.number_of_boxes),
                ],
                limit=1,
            )

        next_card = get_next_card()
        if not next_card:
            self.boxed_card_ids.write({"box_number": 1})
            next_card = get_next_card()
        if not next_card:
            raise UserError(
                _("Nothing to do here. You should reset the box or pick another one")
            )
        return {
            "name": self.name,
            "res_model": "leitner.boxed_card",
            "view_mode": "form",
            "views": [(self.env.ref("leitner.leitner_boxed_card_session").id, "form")],
            "target": "main",
            "type": "ir.actions.act_window",
            "res_id": next_card.id,
        }


class BoxedCard(models.Model):
    _name = "leitner.boxed_card"
    _description = "A card as part of the box set."
    _order = "box_number ASC, sequence ASC, id ASC"

    company_id = fields.Many2one(related="box_set_id.company_id")
    user_id = fields.Many2one(related="box_set_id.user_id")
    name = fields.Char(related="card_id.name")
    box_set_id = fields.Many2one("leitner.box_set", required=True, ondelete="cascade")
    box_number = fields.Integer(default=1, required=True)
    card_id = fields.Many2one("leitner.card", check_company=True)
    front = fields.Html(related="card_id.front")
    back = fields.Html(related="card_id.back")
    sequence = fields.Integer(default=1, required=True)
    is_answer_back = fields.Boolean(related="box_set_id.is_answer_back", readonly=True)
    is_answer_visible = fields.Boolean(default=False, required=True)

    @api.constrains("box_number")
    def _check_box_number(self):
        for bc in self:
            if 0 == bc.box_set_id.number_of_boxes:
                continue
            if not 1 <= bc.box_number <= bc.box_set_id.number_of_boxes:
                raise ValidationError(
                    _("Invalid box number %d " % bc.box_set_id.number_of_boxes)
                )

    def get_next(self):
        """Get the next card if exists.

        If there are cards pending in the current box, then pick the
        first card from that box.

        If the current box is empty, then pick the first card overall.

        Never return cards from the last box (those are done already)
        or the current card (unless it's the only one).

        Return the the card an empty recordset if no card was found.

        """
        next_card_from_box = self.search(
            [
                ("box_set_id", "=", self.box_set_id.id),
                ("box_number", "=", self.box_number),
                ("box_number", "<", self.box_set_id.number_of_boxes),
                ("id", "!=", self.id),
            ],
            limit=1,
        )
        if next_card_from_box:
            return next_card_from_box
        next_card = self.search(
            [
                ("box_set_id", "=", self.box_set_id.id),
                ("box_number", "<", self.box_set_id.number_of_boxes),
                ("id", "!=", self.id),
            ],
            limit=1,
        )
        if next_card:
            return next_card
        if self.box_number < self.box_set_id.number_of_boxes:
            return self
        return self.env["leitner.boxed_card"]

    def move_up(self):
        if self.box_number == self.box_set_id.number_of_boxes:
            return
        self.move(1)

    def move_down(self):
        self.move(1 - self.box_number)

    def move(self, delta):
        next_box = self.box_number + delta
        last_in_next_box = self.search(
            [("box_set_id", "=", self.box_set_id.id), ("box_number", "=", next_box)],
            limit=1,
            order="sequence DESC",
        )
        self.box_number = next_box
        self.sequence = last_in_next_box.sequence + 1 if last_in_next_box else 1
        self.is_answer_visible = False

    def action_flip(self):
        self.is_answer_visible = not self.is_answer_visible

    def action_hit(self):
        """Move card to the next box and show the next."""
        next_card = self.get_next()
        self.move_up()
        if next_card:
            return {
                "name": self.name,
                "res_model": "leitner.boxed_card",
                "view_mode": "form",
                "views": [
                    (self.env.ref("leitner.leitner_boxed_card_session").id, "form")
                ],
                "target": "main",
                "type": "ir.actions.act_window",
                "res_id": next_card.id,
            }
        raise UserError(_("Congratulations! There are no more cards, you are done!"))

    def action_miss(self):
        """Move card to the first box and show the next"""
        next_card = self.get_next()
        assert next_card
        self.move_down()
        return {
            "name": self.name,
            "res_model": "leitner.boxed_card",
            "view_mode": "form",
            "views": [(self.env.ref("leitner.leitner_boxed_card_session").id, "form")],
            "target": "main",
            "type": "ir.actions.act_window",
            "res_id": next_card.id,
        }

    def action_leave(self):
        return self.sudo().env.ref("leitner.leitner_box_set_action").read()[0]
