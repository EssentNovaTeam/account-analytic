# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa - <antonio.espinosa@tecnativa.com>
# Copyright 2017 Vicent Cubells - <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_distribution_id = fields.Many2one(
        comodel_name='account.analytic.distribution',
        string='Analytic distribution',
    )

    @api.multi
    def _analytic_line_distributed_prepare(self, rule):
        res = self._prepare_analytic_line(self)
        amount = (res.get('amount') * rule.percent) / 100.0
        res['amount'] = amount
        res['account_id'] = rule.analytic_account_id.id
        return res

    @api.multi
    def create_analytic_lines(self):
        res = super(AccountMoveLine, self).create_analytic_lines()
        move_lines = self.search([
            ('id', 'in', self.ids), ('analytic_distribution_id', '!=', False)])
        if not move_lines:
            return res
        self.env['account.analytic.line'].search(
            [('move_id', 'in', move_lines.ids)]).unlink()
        for line in move_lines:
            for rule in line.analytic_distribution_id.rule_ids:
                values = line._analytic_line_distributed_prepare(rule)
                self.env['account.analytic.line'].create(values)
        return res
