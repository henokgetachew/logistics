#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from datetime import datetime
from logistics.apps.logistics.models import StockRequest
from logistics.apps.malawi.const import Messages
from logistics.apps.malawi.handlers.abstract.orderresponse import OrderResponseBaseHandler

class OrderReadyHandler(OrderResponseBaseHandler):
    """
    When a supply has been ordered, it is confirmed "ready" by the person
    providing supplies with this handler.
    """

    keyword = "ready"

    def help(self):
        self.respond(Messages.ORDERREADY_HELP_MESSAGE)
        
    def handle(self, text):
        if self.handle_preconditions(text):
            return
        
        now = datetime.utcnow()
        pending_reqs = StockRequest.pending_requests().filter(supply_point=self.hsa.supply_point)
        for req in pending_reqs:
            req.approve(self.msg.logistics_contact, req.amount_requested, now)
        
        products = ", ".join(req.sms_format() for req in pending_reqs)
        self.respond(Messages.APPROVAL_RESPONSE, hsa=self.hsa.name,
                     products=products)
        self.hsa.message(Messages.APPROVAL_NOTICE, hsa=self.hsa.name, 
                    products=products)
    
                