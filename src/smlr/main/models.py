from django.db import models
from django.conf import settings


class URL(models.Model):
    original_url = models.URLField()
    shortenings = models.IntegerField(default=0)
    created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    alias = models.CharField(max_length=8, null=True, blank=True)
    is_custom_alias = models.BooleanField(default=False)
    
    def get_short_url(self):
        return settings.BASE_URL + '/' + self.alias
        
    def __unicode__(self):
        return u'%s - %s' % (self.alias, self.original_url)


class Redirect(models.Model):
    url = models.ForeignKey(URL)
    created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    remote_host = models.CharField(max_length=255, blank=True, null=True)
    remote_ip = models.CharField(max_length=15, blank=True, null=True)
    remote_port = models.CharField(max_length=8, blank=True, null=True)
    request_method = models.CharField(max_length=8, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return u'For alias: %s' % (self.url.alias,)
    