

# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    contract_id = fields.Many2one(
        'contract.general',
        string='Contrato Relacionado',
        help='Contrato al que pertenece esta factura'
    )

    @api.model
    def create(self, vals):
        """Override to link invoices to contracts automatically"""
        move = super(AccountMove, self).create(vals)
        
        # Try to find and link contract automatically for customer invoices
        if (move.move_type in ['out_invoice', 'out_refund'] and 
            move.partner_id and 
            not move.contract_id):
            
            # Search for active contracts for this partner
            contract = self.env['contract.general'].search([
                ('partner_id', '=', move.partner_id.id),
                ('state', '=', 'valid')
            ], limit=1)
            
            if contract:
                move.contract_id = contract.id
        
        return move

    def write(self, vals):
        """Override to maintain contract linkage"""
        result = super(AccountMove, self).write(vals)
        
        # Auto-link contracts when partner changes
        if 'partner_id' in vals:
            for move in self:
                if (move.move_type in ['out_invoice', 'out_refund'] and 
                    move.partner_id and 
                    not move.contract_id):
                    
                    contract = self.env['contract.general'].search([
                        ('partner_id', '=', move.partner_id.id),
                        ('state', '=', 'valid')
                    ], limit=1)
                    
                    if contract:
                        move.contract_id = contract.id
        
        return result
