# Copyright (C) 2018 Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMTeam(models.Model):
    _name = "fsm.team"
    _description = "Field Service Team"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _default_stages(self):
        return self.env["fsm.stage"].search([("is_default", "=", True)])


## Diego ## 26/07/2021 "stage_id", "=", 16
    def _compute_agendadas_count(self):
        order_data = self.env["fsm.order"].read_group(
            [("team_id", "in", self.ids), ("stage_id", "=", 16 )],
            ["team_id"],
            ["team_id"],
        )
        result = {data["team_id"][0]: int(data["team_id_count"]) for data in order_data}
        for team in self:
            team.agendadas_count = result.get(team.id, 0)

    def _compute_reagendadas_count(self):
        order_data = self.env["fsm.order"].read_group(
            [("team_id", "in", self.ids), ("stage_id", "=", 15 )],
            ["team_id"],
            ["team_id"],
        )
        result = {data["team_id"][0]: int(data["team_id_count"]) for data in order_data}
        for team in self:
            team.reagendadas_count = result.get(team.id, 0)
##


    def _compute_order_count(self):
        order_data = self.env["fsm.order"].read_group(
            [("team_id", "in", self.ids), ("stage_id.is_closed", "=", False)],
            ["team_id"],
            ["team_id"],
        )
        result = {data["team_id"][0]: int(data["team_id_count"]) for data in order_data}
        for team in self:
            team.order_count = result.get(team.id, 0)

    def _compute_order_need_assign_count(self):
        order_data = self.env["fsm.order"].read_group(
            [("team_id", "in", self.ids), ("person_id", "=", False)],
            ["team_id"],
            ["team_id"],
        )
        result = {data["team_id"][0]: int(data["team_id_count"]) for data in order_data}
        for team in self:
            team.order_need_assign_count = result.get(team.id, 0)

    def _compute_order_need_schedule_count(self):
        order_data = self.env["fsm.order"].read_group(
            [("team_id", "in", self.ids), ("scheduled_date_start", "=", False)],
            ["team_id"],
            ["team_id"],
        )
        result = {data["team_id"][0]: int(data["team_id_count"]) for data in order_data}
        for team in self:
            team.order_need_schedule_count = result.get(team.id, 0)

    name = fields.Char(required=True, translate=True, string="Código do Serviço")
    description = fields.Text(translate=True, string="Descrição do Serviço")
    type = fields.Many2one("fsm.order.type", string="Type")
    color = fields.Integer("Color Index")
    stage_ids = fields.Many2many(
        "fsm.stage",
        "order_team_stage_rel",
        "team_id",
        "stage_id",
        string="Stages",
        default=_default_stages,
    )
    order_ids = fields.One2many(
        "fsm.order",
        "team_id",
        string="Orders",
        domain=[("stage_id.is_closed", "=", False)],
    )

# Diego # 26/07/2021
    valor_servico = fields.Float(
        default=0.0,
        string="Valor do Serviço",
        store=True,
        help="O valor unitario do serviço")
# Adicionado contadores para ordens de serviços agendados, para agendar.
    agendadas_count = fields.Integer(compute="_compute_agendadas_count", string="Total OS Agendadas")
    reagendadas_count = fields.Integer(compute="_compute_reagendadas_count", string="Total OS Reagendadas")
    order_count = fields.Integer(compute="_compute_order_count", string="Total Ordens Abertas")
    order_need_assign_count = fields.Integer(
        compute="_compute_order_need_assign_count", string="Total OS para Atríbuir"
    )
    order_need_schedule_count = fields.Integer(
        compute="_compute_order_need_schedule_count", string="Total OS para Agendar"
    )
    sequence = fields.Integer(
        "Sequence", default=1, help="Used to sort teams. Lower is better."
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.user.company_id,
        help="Company related to this team",
    )

    _sql_constraints = [("name_uniq", "unique (name)", "Team name already exists!")]
