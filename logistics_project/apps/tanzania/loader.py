import os
from django.conf import settings
from rapidsms.contrib.locations.models import LocationType, Location, Point
from logistics.models import SupplyPoint, SupplyPointType, SupplyPointGroup

from logging import info
from logistics_project.loader.base import load_report_types, load_roles
from logistics.shortcuts import supply_point_from_location
import csv
from dimagi.utils.parsing import string_to_boolean
from logistics_project.apps.tanzania.config import SupplyPointCodes

def clear_supplypoints():
    Location.objects.all().delete()
    SupplyPoint.objects.all().delete()
    Point.objects.all().delete()
    LocationType.objects.all().delete()
    SupplyPointType.objects.all().delete()

def create_location_and_sp_types():
    types = (
        ("MOHSW", SupplyPointCodes.MOH),
        ("REGION", SupplyPointCodes.REGION),
        ("DISTRICT", SupplyPointCodes.DISTRICT),
        ("FACILITY", SupplyPointCodes.FACILITY)
    )
    count = 0
    for t in types:
        LocationType.objects.create(name=t[0], slug=t[1])
        SupplyPointType.objects.create(name=t[0],code=t[1])
        count += 1
    print "Created %d loc types." % count


def load_locations(path):
    info("Loading locations %s"  % (path))
    if not os.path.exists(path):
        raise Exception("no file found at %s" % path)

    count = 0
    with open(path, 'r') as f:
        reader = csv.reader(f, delimiter=',', quotechar='"')
        for row in reader:
            id, name, is_active, msd_code, parent_name, parent_type, lat, lon, group, type = row
            loc_type = LocationType.objects.get(name__iexact=type)
            
            
            parent = Location.objects.get(name__iexact=parent_name, 
                                          type__name__iexact=parent_type) \
                            if parent_name and parent_type else None
            
            point = Point.objects.create(longitude=lon, latitude=lat) \
                            if lat and lon else None
            
            kwargs = {}
            if parent: kwargs["parent"] = parent
            if point:  kwargs["point"] = point
            
            l = Location.objects.create(name=name,
                                        code=msd_code if msd_code else "%s-%s" % (type, name),
                                        type=loc_type,
                                        is_active=string_to_boolean(is_active),
                                        **kwargs)
            
            sp = supply_point_from_location\
                    (l, SupplyPointType.objects.get(name__iexact=type),
                     SupplyPoint.objects.get(location=parent) if parent else None)
            
            if group:
                group_obj = SupplyPointGroup.objects.get_or_create(code=group)[0]
                sp.groups.add(group_obj)
                sp.save()
            
            count += 1
    print "Processed %d locations"  % count


def init_static_data():
    clear_supplypoints()
    load_report_types()
    load_roles()
    create_location_and_sp_types()
    locations = getattr(settings, "STATIC_LOCATIONS")
    if locations:
        load_locations(locations)
    info("Success!")