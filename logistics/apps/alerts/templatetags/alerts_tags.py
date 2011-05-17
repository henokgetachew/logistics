from django import template
from logistics.apps.alerts.utils import get_alert_functions
import itertools
from django.template.loader import render_to_string
register = template.Library()

@register.simple_tag
def alerts():
    alerts = itertools.chain(*(f() for f in get_alert_functions()))
    return render_to_string("alerts/partials/alerts.html",
                            {"alerts": alerts})
    
