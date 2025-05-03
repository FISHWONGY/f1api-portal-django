# forms.py

from django import forms
from .models import ClientScopesGet


class ClientIDForm(forms.Form):
    client_id = forms.CharField(max_length=50, label="Client ID")


class ClientScopeForm(forms.ModelForm):
    class Meta:
        model = ClientScopesGet
        fields = ["client_id", "scopes"]


class NewClientForm(forms.ModelForm):
    class Meta:
        model = ClientScopesGet
        fields = ["client_id", "scopes"]