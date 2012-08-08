from datetime import datetime
from collections import defaultdict

from django.utils.datastructures import SortedDict

from dimagi.utils.dates import months_between

from logistics.models import SupplyPoint
from logistics.util import config

from logistics_project.apps.malawi.util import get_country_sp,\
    get_district_supply_points, facility_supply_points_below, fmt_pct
from logistics_project.apps.malawi.warehouse.models import ReportingRate
from logistics_project.apps.malawi.warehouse.report_utils import get_reporting_rates_chart
from logistics_project.apps.malawi.warehouse import warehouse_view

class View(warehouse_view.DistrictOnlyView):

    def custom_context(self, request):
        shared_headers = ["% Reporting", "% Rep on time", "% Late Rep", "% No Rep", "% Complete"]
        shared_slugs = ["reported", "on_time", "late", "missing", "complete"]
        
        # reporting rates by month table
        sp = SupplyPoint.objects.get(location=request.location) \
            if request.location else get_country_sp()
        months = SortedDict()
        for year, month in months_between(request.datespan.startdate, 
                                          request.datespan.enddate):
            dt = datetime(year, month, 1)
            months[dt] = ReportingRate.objects.get(supply_point=sp, date=dt)
        
        month_data = [[dt.strftime("%B")] + [getattr(rr, "pct_%s" % k) for k in shared_slugs] \
                      for dt, rr in months.items()]
        
        month_table = {
            "id": "month-table",
            "is_datatable": False,
            "header": ["Months"] + shared_headers,
            "data": month_data,
        }

        def _avg_report_rate_table_data(queryset, startdate, enddate):
            datamap = SortedDict()
            for sp in queryset:
                spdata = defaultdict(lambda: 0)
                for year, month in months_between(startdate, 
                                                  enddate):
                    rr = ReportingRate.objects.get(supply_point=sp,
                                                   date=datetime(year, month, 1))
                    spdata['total'] += rr.total
                    for k in shared_slugs:
                        spdata[k] += getattr(rr, k)
                datamap[sp] = spdata
                        
            return [[sp.name] + [fmt_pct(data[k], data['total']) for k in shared_slugs] \
                    for sp, data in datamap.items()]
        
        # district breakdown
            
        district_table = {
            "title": "average-reporting-rate-districts",
            "is_datatable": False,
            "header": ["Districts"] + shared_headers,
            "data": _avg_report_rate_table_data(get_district_supply_points().order_by('name'), 
                                                request.datespan.startdate,
                                                request.datespan.enddate)
        }
        
        # facility breakdown
        facility_table = None
        if sp.type.code == config.SupplyPointCodes.DISTRICT:
            facility_table = {
                "title": "average-reporting-rate-facilities",
                "is_datatable": False,
                "header": ["Facilities"] + shared_headers,
                "data": _avg_report_rate_table_data\
                    (facility_supply_points_below(sp.location).order_by('name'),
                     request.datespan.startdate,
                     request.datespan.enddate)
            }
        
        return {"month_table": month_table,
                "district_table": district_table,
                "facility_table": facility_table,
                "graphdata" : get_reporting_rates_chart(request.location, 
                                                        request.datespan.startdate, 
                                                        request.datespan.enddate)
                }