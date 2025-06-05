
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Campos para representantes legales
    is_legal_representative = fields.Boolean(
        string='Es Representante Legal',
        default=False,
        help='Marcar si este contacto es un representante legal'
    )

    legal_position = fields.Char(
        string='Puesto/Cargo Legal',
        help='Puesto o cargo en la empresa (ej: Gerente General, Presidente)'
    )

    legal_hierarchy = fields.Selection([
        ('president', 'Presidente'),
        ('vp', 'Vicepresidente'),
        ('general_manager', 'Gerente General'),
        ('manager', 'Gerente'),
        ('legal_rep', 'Representante Legal'),
        ('attorney', 'Apoderado Generalísimo'),
        ('attorney_special', 'Apoderado Especial'),
        ('other', 'Otro')
    ], string='Jerarquía Legal')

    legal_id_number = fields.Char(
        string='Cédula/ID Legal',
        help='Número de identificación para efectos legales'
    )

    # Campos para empresas con contratos
    company_legal_name = fields.Char(
        string='Razón Social Completa',
        help='Nombre legal completo de la empresa'
    )

    company_registration = fields.Char(
        string='Número de Registro',
        help='Número de registro en el Registro Nacional (Costa Rica)'
    )

    company_tax_id = fields.Char(
        string='Cédula Jurídica',
        help='Cédula jurídica de la empresa'
    )

    # Relación con contratos
    contract_ids = fields.One2many(
        'contract.general',
        'partner_id',
        string='Contratos como Empresa'
    )

    legal_contract_ids = fields.One2many(
        'contract.general',
        'legal_contact_id',
        string='Contratos como Representante'
    )

    contract_count = fields.Integer(
        string='Número de Contratos',
        compute='_compute_contract_count'
    )

    @api.depends('contract_ids', 'legal_contract_ids')
    def _compute_contract_count(self):
        for partner in self:
            partner.contract_count = len(partner.contract_ids) + len(partner.legal_contract_ids)

    def action_view_contracts(self):
        """Ver contratos relacionados con este contacto"""
        self.ensure_one()
        contracts = self.contract_ids + self.legal_contract_ids
        return {
            'name': _('Contratos de %s') % self.name,
            'view_mode': 'tree,form',
            'res_model': 'contract.general',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', contracts.ids)],
            'context': {'default_partner_id': self.id if self.is_company else False,
                       'default_legal_contact_id': self.id if not self.is_company else False}
        }

    def sync_from_contract(self, contract_data):
        """Sincronizar datos del contacto desde un contrato"""
        self.ensure_one()
        
        # Actualizar datos básicos si han cambiado
        update_vals = {}
        
        if contract_data.get('email') and contract_data['email'] != self.email:
            update_vals['email'] = contract_data['email']
            
        if contract_data.get('phone') and contract_data['phone'] != self.phone:
            update_vals['phone'] = contract_data['phone']
            
        if contract_data.get('name') and contract_data['name'] != self.name:
            update_vals['name'] = contract_data['name']
        
        # Actualizar campos específicos de representante legal
        if contract_data.get('is_legal_representative'):
            update_vals.update({
                'is_legal_representative': True,
                'legal_position': contract_data.get('legal_position'),
                'legal_hierarchy': contract_data.get('legal_hierarchy'),
                'legal_id_number': contract_data.get('legal_id_number'),
            })
        
        # Actualizar campos de empresa si es compañía
        if self.is_company:
            if contract_data.get('company_legal_name'):
                update_vals['company_legal_name'] = contract_data['company_legal_name']
            if contract_data.get('company_tax_id'):
                update_vals['company_tax_id'] = contract_data['company_tax_id']
            if contract_data.get('company_registration'):
                update_vals['company_registration'] = contract_data['company_registration']
        
        if update_vals:
            self.write(update_vals)
            
        return True

    @api.model
    def create_from_contract(self, contract_data):
        """Crear un nuevo contacto desde datos de contrato"""
        vals = {
            'name': contract_data.get('name', 'Nuevo Contacto'),
            'email': contract_data.get('email'),
            'phone': contract_data.get('phone'),
            'is_company': contract_data.get('is_company', False),
            'customer_rank': 1,  # Marcar como cliente
        }
        
        # Agregar campos específicos según el tipo
        if contract_data.get('is_legal_representative'):
            vals.update({
                'is_legal_representative': True,
                'legal_position': contract_data.get('legal_position'),
                'legal_hierarchy': contract_data.get('legal_hierarchy'),
                'legal_id_number': contract_data.get('legal_id_number'),
            })
        
        if vals['is_company']:
            vals.update({
                'company_legal_name': contract_data.get('company_legal_name'),
                'company_tax_id': contract_data.get('company_tax_id'),
                'company_registration': contract_data.get('company_registration'),
            })
        
        return self.create(vals)
