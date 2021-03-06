from django.db import transaction
from logistics.util import config
from logistics_project.apps.malawi.handlers.abstract.base import RecordResponseHandler
from logistics.models import StockRequest
from logistics.decorators import logistics_contact_and_permission_required, managed_products_required
from logistics.shortcuts import create_stock_report


class StockReportBaseHandler(RecordResponseHandler):
    hsa = None
    requests = []
    
    
    def get_report_type(self):
        raise NotImplemented("This method must be overridden")
    
    def send_responses(self):
        raise NotImplemented("This method must be overridden")

    @transaction.commit_on_success
    @logistics_contact_and_permission_required(config.Operations.REPORT_STOCK)
    @managed_products_required()
    def handle(self, text):
        """
        Check some preconditions, based on shared assumptions of these handlers.
        Return true if there is a precondition that wasn't met. If all preconditions
        are met, the variables for facility and name will be set.
        
        This method will manage some replies as well.
        """
        # at some point we may want more granular permissions for these
        # operations, but for now we just share the one
        self.hsa = self.msg.logistics_contact
        
        stock_report = create_stock_report(self.get_report_type(),  
                                           self.hsa.supply_point,
                                           text, 
                                           self.msg.logger_msg)
        self.requests = StockRequest.create_from_report(stock_report, self.hsa)
        self.send_responses(stock_report)