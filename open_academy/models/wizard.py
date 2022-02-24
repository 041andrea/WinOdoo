# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Wizard(models.TransientModel):
    _name = 'open_academy.wizard'

    session_id = fields.Many2one('open_academy.session',
        string="Session", required=True)
    attendee_ids = fields.Many2many('res.partner', string="Attendees")