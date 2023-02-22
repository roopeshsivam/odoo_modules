# -*- coding: utf-8 -*-
from odoo import api, fields, models, _  # type: ignore
from odoo.exceptions import UserError    # type: ignore
import json
import requests    # type: ignore
import base64, binascii

import datetime as dt

aftership_URL = "https://api.aftership.com/v4/last_checkpoint"
class DeliveryAftership(models.Model):
    _inherit = 'delivery.carrier'

    aftership_slug = fields.Char('Slug')
    aftership_id = fields.Many2one('aftership.account', string='Account')
    test_tracking_number = fields.Char('Test Tracking Number')


    def get_tracking_status(self, tracking_number):
        ''' Return Json data of tracking:
            To be implemented
            {
                "tag" : "Pending",
                "subtag" : "Pending_003",
                "message" : "Label created, no updates yet",
                "cp_tag" : "Tagged",
                "cp_message" : "TEST",
                "cp_country" : "UAE"
            }
        '''
        self.ensure_one()
        if hasattr(self, '%s_get_tracking_status' % self.delivery_type):
            return getattr(self, '%s_get_tracking_status' % self.delivery_type)(tracking_number)
        return self.get_aftership_tracking_message(tracking_number)
    

    def get_aftership_tracking_message(self, tracking_number):
        response = self._get_aftership_tracking(tracking_number)
        data = response.get('data', {})
        try :
            cp = data.get("checkpoint")
            return {
                    "tag" : data.get('tag'),
                    "subtag" : data.get('subtag'),
                    "message" : data.get('subtag_message'),
                    "cp_tag" : cp.get('tag'),
                    "cp_message" : cp.get('message'),
                    "cp_country" : cp.get('country_name')
                }
        except :
            return {
                    "tag" : "No Tracking Details Available",
                    "subtag" : "",
                    "message" : "",
                    "cp_tag" : "",
                    "cp_message" : "",
                    "cp_country" : ""
                }




    def test_tracking_status(self):
        resp = self._get_aftership_tracking(self.test_tracking_number)
        raise UserError(str(resp))


    def _get_aftership_tracking(self, tracking_number):
        def _get_aftership_headers():
            return {
                'as-api-key' : self.aftership_id.api_key
                }
        url = f"{aftership_URL}/{self.aftership_slug}/{tracking_number}"
        try :
            return requests.request('GET', url, headers=_get_aftership_headers()).json()
        except:
            return {}


class AftershipCarrier(models.Model):
    _name = 'aftership.account'
    _description = 'Aftership Account'

    name = fields.Char('Name')
    api_key = fields.Char('Api Key')


class AsSaleOrder(models.Model):
    _inherit = 'sale.order'

    def get_tracking_status(self):
        for record in self:
            picking_ids = record.env['stock.picking'].search([('sale_id', '=', record.id), ('state', 'in', ['done', 'assigned']), \
                ('picking_type_code', '=', 'outgoing'), ('carrier_tracking_ref', '!=', False), ('carrier_id', '!=', False)])
            picking_ids.get_tracking_status()
            record.write({
                'carrier_tracking_ref' : ",".join(picking_ids.mapped('carrier_tracking_ref'))
            })

    def write_tracking_data(self):
        return
    


    


    tracking_status_text = fields.Char('Tracking Status')
class AsPicking(models.Model):
    _inherit = 'stock.picking'

    def get_tracking_status(self):
        for record in self:
            message_json =  record.carrier_id.get_tracking_status(record.carrier_tracking_ref)
            tag = message_json.get('tag')
            subtag = message_json.get('subtag')
            message = message_json.get('message')
            cp_tag = message_json.get('cp_tag')
            cp_message = message_json.get('cp_message')
            cp_country = message_json.get('cp_country')
            body = f"""Tag : {subtag}
            Message : {message}
            Checkpoint Details
            Tag : {cp_tag}
            Message : {cp_message}
            Country : {cp_country}
            """
            summary = tag + ", "  + subtag
            record.message_post(body=f"{body}", subject=f"Tracking Details :: {tag}")
            record.sale_id.message_post(body=f"{body}", subject=f"Tracking Details :: {tag}")
            record.sale_id.update({
                'tracking_status_text' : summary
            })