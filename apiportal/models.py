from django.db import models


class ClientScopesGet(models.Model):
    client_id = models.CharField(max_length=50)
    client_secret = models.CharField(max_length=100)
    scopes = models.TextField()
    is_active = models.IntegerField()

    def __str__(self):
        return self.client_id

    class Meta:
        db_table = "client_scopes_get"


class ClientEndpointsAccess(models.Model):
    client_id = models.CharField(max_length=50)
    endpoint = models.TextField()
    allow_access = models.TextField()
    extra_constrains = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.client_id} - {self.endpoint}"

    class Meta:
        db_table = "client_endpoints_access"


class ScopesGet(models.Model):
    endpoint = models.CharField(max_length=180)
    scope = models.CharField(max_length=1000)
    column_access = models.TextField()

    def __str__(self):
        return self.endpoint

    class Meta:
        db_table = "scopes_get"
