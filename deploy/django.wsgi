import os
import sys

filedir = os.path.dirname(__file__)

filedir = os.path.join(filedir, "..", "logistics_project")     
sys.path.append(os.path.join(filedir))
sys.path.append(os.path.join(filedir,'..'))
sys.path.append(os.path.join(filedir,'..','rapidsms','lib'))
sys.path.append(os.path.join(filedir,'..','submodules','django-cpserver'))
sys.path.append(os.path.join(filedir,'..','submodules','dimagi-utils'))
sys.path.append(os.path.join(filedir,'..','submodules','django-tablib'))
sys.path.append(os.path.join(filedir,'..','submodules','tablib'))
sys.path.append(os.path.join(filedir,'..','submodules','auditcare'))
sys.path.append(os.path.join(filedir,'..','submodules','couchlog'))
sys.path.append(os.path.join(filedir,'..','submodules','django-scheduler'))
sys.path.append(os.path.join(filedir,'..','submodules','rapidsms-alerts'))
sys.path.append(os.path.join(filedir,'..','submodules','email-reports'))
sys.path.append(os.path.join(filedir,'..','submodules','rapidsms-logistics'))
sys.path.append(os.path.join(filedir,'..','submodules','rapidsms-groupmessaging'))
sys.path.insert(0, os.path.join(filedir,'..','submodules','dimagi-djtables','lib'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
