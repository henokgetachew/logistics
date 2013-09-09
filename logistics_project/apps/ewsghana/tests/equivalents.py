from rapidsms.conf import settings
from rapidsms.tests.scripted import TestScript
from logistics.models import SupplyPoint, \
    SupplyPointType, Product, ProductType, ProductStock
from logistics_project.apps.ewsghana.tests.util import load_test_data

class TestEquivalents(TestScript):
    def setUp(self):
        TestScript.setUp(self)
        load_test_data()
        settings.LOGISTICS_STOCKED_BY = 'user'

    def testLowStock(self):
        a = """
              123 > register stella dedh
              123 < Congratulations stella, you have successfully been registered for the Early Warning System. Your facility is Dangme East District Hospital
              123 > ov2.0
              123 < Dear stella, these items need to be reordered: ov. Please order 28 ov.
            """
        self.runScript(a)

    def testEquivalentStockout(self):
        a = """
              123 > register stella dedh
              123 < Congratulations stella, you have successfully been registered for the Early Warning System. Your facility is Dangme East District Hospital
              123 > ov0.0 ml1.0
              123 < Dear stella, these items are stocked out: ov. these items need to be reordered: ml. Please order 29 ml, 30 ov.
              123 > ov1.1 ml0.0
              123 < Dear stella, these items are stocked out: ml. these items need to be reordered: ov. Please order 30 ml, 29 ov.
              123 > ov0.0 ml20.20
              123 < Dear stella, thank you for reporting the commodities you have. You received ml 20.
              123 > ov20.20 ml0.0
              123 < Dear stella, thank you for reporting the commodities you have. You received ov 20.
            """
        self.runScript(a)

    def testEquivalentLowSupply(self):
        a = """
              123 > register stella dedh
              123 < Congratulations stella, you have successfully been registered for the Early Warning System. Your facility is Dangme East District Hospital
              123 > ov1.0 ml20.0
              123 < Dear stella, thank you for reporting the commodities you have in stock.
              123 > ov20 19 ml1.0
              123 < Dear stella, thank you for reporting the commodities you have. You received ov 19.
              123 > ml20 19 ov1.0
              123 < Dear stella, thank you for reporting the commodities you have. You received ml 19.
              123 > ml1.0 ov20 19
              123 < Dear stella, thank you for reporting the commodities you have. You received ov 19.
            """
        self.runScript(a)

    def testNoProductStock(self):
        ov = Product.objects.get(sms_code='ov')
        zz, created = Product.objects.get_or_create(sms_code='zz', name='Test',
                                                    type=ProductType.objects.all()[0], 
                                                    units='cycle')
        zz.equivalents.add(ov)
        a = """
              123 > register stella dedh
              123 < Congratulations stella, you have successfully been registered for the Early Warning System. Your facility is Dangme East District Hospital
              123 > ov1.0 zz20.0
              123 < Dear stella, these items need to be reordered: ov. Please order 29 ov.
              123 > ov20 19 zz1.0
              123 < Dear stella, thank you for reporting the commodities you have. You received ov 19.
              123 > zz20 19 ov1.0
              123 < Dear stella, these items need to be reordered: ov. Please order 29 ov.
              123 > zz1.0 ov20 19
              123 < Dear stella, thank you for reporting the commodities you have. You received ov 19.
            """
        self.runScript(a)

    def testNoConsumption(self):
        ov = Product.objects.get(sms_code='ov')
        dedh = SupplyPoint.objects.get(code='dedh')
        zz, created = Product.objects.get_or_create(sms_code='zz', name='Test',
                                                    type=ProductType.objects.all()[0], 
                                                    units='cycle')
        zz.equivalents.add(ov)
        ProductStock.objects.get_or_create(product=zz, supply_point=dedh)
        a = """
              123 > register stella dedh
              123 < Congratulations stella, you have successfully been registered for the Early Warning System. Your facility is Dangme East District Hospital
              123 > ov1.0 zz20.0
              123 < Dear stella, these items need to be reordered: ov. Please order 29 ov.
              123 > ov20 19 zz1.0
              123 < Dear stella, thank you for reporting the commodities you have. You received ov 19.
              123 > zz20 19 ov1.0
              123 < Dear stella, these items need to be reordered: ov. Please order 29 ov.
              123 > zz1.0 ov20 19
              123 < Dear stella, thank you for reporting the commodities you have. You received ov 19.
            """
        self.runScript(a)
