# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import models, fields, api, exceptions, _


class course(models.Model):
    _name = 'open_academy.course'
    _description = 'course'

    title = fields.Char(string="title", required=True)
    description = fields.Text()

    responsible_id = fields.Many2one('res.users', ondelete='set null', string="Responsible", index=True)
    session_ids=fields.One2many('open_academy.session', 'course_id', string="sessions")


    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
             [('name', '=like', _(u"Copy of {}%").format(self.name))])
        if not copied_count:
             new_name = _(u"Copy of {}").format(self.name)
        else:
            new_name = _(u"Copy of {} ({})").format(self.name, copied_count)

        default['title'] = new_title
        return super(Course, self).copy(default)

    _sql_constraints = [
        ('title_description_check',
         'CHECK(title != description)',
         "El título del curso no debe ser la descripción."),

        ('title_unique',
         'unique(title)',
         "El título del curso debe ser único."),
    ]


class Session(models.Model):
    _name='open_academy.session'
    

    name= fields.Char(string="Nombre", required=True)
    start_date = fields.Date(default=fields.Date.today)
    duration = fields.Float(digits=(6, 2), help="Duration in days")
    seats= fields.Integer(string="Number of seats")
    active = fields.Boolean(default=True)
    color = fields.Integer()

    instructor_id = fields.Many2one('res.partner', string="Instructor")
    domain=['|', ('instructor', '=', True),('category_id.name', 'ilike', "Teacher")]
    course_id = fields.Many2one('open_academy.course',
        ondelete='cascade', string="Course", required=True)
    attendee_ids = fields.Many2many('res.partner', string="Attendees")



    taken_seats = fields.Float(string="Taken seats", compute='_taken_seats')
    end_date = fields.Date(string="End Date", store=True,
        compute='_get_end_date', inverse='_set_end_date')

    hours = fields.Float(string="Duration in hours",
                         compute='_get_hours', inverse='_set_hours')

    attendees_count = fields.Integer(
        string="Attendees count", compute='_get_attendees_count', store=True)


    @api.depends('seats', 'attendee_ids')
    def _taken_seats(self):
        for r in self:
            if not r.seats:
                r.taken_seats = 0.0
            else:
                r.taken_seats = 100.0 * len(r.attendee_ids) / r.seats

    @api.onchange('seats', 'attendee_ids')
    def _verify_valid_seats(self):
        if self.seats < 0:
            return {
                'warning': {
                    'title': _("Incorrect 'seats' valor"),
                    'message': _("The number of available seats may not be negative"),
                },
            }
        if self.seats < len(self.attendee_ids):
            return {
                'warning': {
                    'title': _("Too many attendees"),
                    'message': _("Increase seats or remove excess attendees"),
                },
            }

    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        for r in self:
            if not (r.start_date and r.duration):
                r.end_date = r.start_date
                continue

            start = fields.Datetime.from_string(r.start_date)
            duration = timedelta(days=r.duration, seconds=-1)
            r.end_date = start + duration

    def _set_end_date(self):
        for r in self:
            if not (r.start_date and r.end_date):
                continue

           
            start_date = fields.Datetime.from_string(r.start_date)
            end_date = fields.Datetime.from_string(r.end_date)
            r.duration = (end_date - start_date).days + 1

    
    @api.depends('duration')
    def _get_hours(self):
        for r in self:
            r.hours = r.duration * 24

    def _set_hours(self):
        for r in self:
            r.duration = r.hours / 24


    @api.depends('attendee_ids')
    def _get_attendees_count(self):
        for r in self:
            r.attendees_count = len(r.attendee_ids)

    

    @api.constrains('instructor_id', 'attendee_ids')
    def _check_instructor_not_in_attendees(self):
        for r in self:
            if r.instructor_id and r.instructor_id in r.attendee_ids:
                 raise exceptions.ValidationError(_("A session's instructor can't be an attendee"))