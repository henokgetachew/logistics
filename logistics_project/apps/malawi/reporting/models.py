from django.db import models
from datetime import datetime
from logistics.models import SupplyPoint, Product

class UserAccess(models.Model):
	pass	

class ReportingModel(models.Model):
    organization = models.ForeignKey(SupplyPoint) # viewing organization
    date = models.DateTimeField() # viewing time period

    create_date = models.DateTimeField(editable=False)
    update_date = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.create_date = datetime.utcnow()
        self.update_date = datetime.utcnow()
        super(ReportingModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class OrganizationSummary(ReportingModel):
    total_orgs = models.PositiveIntegerField(default=0) # 176
    average_lead_time_in_days = models.FloatField(default=0) # 28

    def __unicode__(self):
        return "%s: %s/%s" % (self.organization, self.date.month, self.date.year)
    

class GroupSummary(models.Model):
    """
    Warehouse data related to a particular category of reporting 
    (e.g. stock on hand summary)
    """
    org_summary = models.ForeignKey('OrganizationSummary')
    title = models.CharField(max_length=50, blank=True, null=True) # SOH
    total = models.PositiveIntegerField(default=0)
    responded = models.PositiveIntegerField(default=0)
    on_time = models.PositiveIntegerField(default=0)
    complete = models.PositiveIntegerField(default=0) # "complete" = submitted or responded
    
    @property
    def late(self):
        return self.complete - self.on_time
    
    @property
    def not_responding(self):
        return self.total - self.responded
   
    
    def __unicode__(self):
        return "%s - %s" % (self.org_summary, self.title)
    

class ProductAvailabilityData(ReportingModel):
    product = models.ForeignKey(Product)
    total = models.PositiveIntegerField(default=0)
    with_stock = models.PositiveIntegerField(default=0)
    with_under_stock = models.PositiveIntegerField(default=0)
    with_over_stock = models.PositiveIntegerField(default=0)
    without_stock = models.PositiveIntegerField(default=0)
    without_data = models.PositiveIntegerField(default=0)

class Alert(ReportingModel):
    type = models.CharField(max_length=50, blank=True, null=True)
    number = models.PositiveIntegerField(default=0)
    text = models.TextField()
    url = models.CharField(max_length=100, blank=True, null=True)
    expires = models.DateTimeField()

class ReportRun(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    complete = models.BooleanField(default=False)
    has_error = models.BooleanField(default=False)

class OrganizationTree(models.Model):
    below = models.ForeignKey(SupplyPoint, related_name='child')
    above = models.ForeignKey(SupplyPoint, related_name='parent')
    is_facility = models.NullBooleanField(default=False)
