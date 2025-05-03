import json
import secrets
import logging

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseNotFound, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import ClientScopesGet, ClientEndpointsAccess, ScopesGet
from .forms import ClientIDForm, ClientScopeForm
from .services import get_client_and_scopes, prepare_scopes_data, process_post_request

logger = logging.getLogger(__name__)


def index(request: HttpRequest) -> HttpResponse:
    active_clients_count = ClientScopesGet.objects.filter(is_active=1).count()
    available_endpoints_count = ScopesGet.objects.values("scope").distinct().count()
    data_sources_count = ScopesGet.objects.values("endpoint").distinct().count()

    return render(
        request,
        "apiportal/index.html",
        {
            "active_clients_count": active_clients_count,
            "available_endpoints_count": available_endpoints_count,
            "data_sources_count": data_sources_count,
        },
    )


def client_scopes(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ClientIDForm(request.POST)
        if form.is_valid():
            client_id = form.cleaned_data["client_id"]
            return redirect("client_scopes_detail", client_id=client_id)
    else:
        form = ClientIDForm()
    return render(request, "apiportal/client_scopes.html", {"form": form})


def client_scopes_detail(request: HttpRequest, client_id: str) -> HttpResponse:
    client_data = get_client_and_scopes(client_id)
    client = client_data["client"]
    current_scopes = client_data["current_scopes"]
    other_scopes = client_data["other_scopes"]

    if request.method == "POST":
        return process_post_request(request, client, current_scopes)

    scopes_data = prepare_scopes_data(current_scopes, client_id)

    return render(
        request,
        "apiportal/client_scopes_edit.html",
        {
            "client_id": client_id,
            "current_scopes": current_scopes,
            "other_scopes": other_scopes,
            "scopes_data": scopes_data,
        },
    )


def client_scopes_edit(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ClientScopeForm(request.POST)
        if form.is_valid():
            client_id = form.cleaned_data["client_id"]
            scopes = form.cleaned_data["scopes"]
            client = ClientScopesGet.objects.get(client_id=client_id)
            client.scopes = scopes
            client.save()
            endpoints = ClientEndpointsAccess.objects.filter(client_id=client_id)
            for endpoint in endpoints:
                endpoint.endpoint = scopes
                endpoint.save()
            return redirect("index")
    else:
        client_id = request.GET.get("client_id")
        form = ClientScopeForm(initial={"client_id": client_id})
    return render(request, "apiportal/client_scopes_edit.html", {"form": form})


def client_scopes_edit_success(request: HttpRequest) -> HttpResponse:
    client_id = request.GET.get("client_id")
    updated_scopes = ClientEndpointsAccess.objects.filter(client_id=client_id).values(
        "endpoint", "allow_access"
    )

    scopes_dict = {entry["endpoint"]: entry["allow_access"] for entry in updated_scopes}

    return render(
        request,
        "apiportal/client_scopes_edit_success.html",
        {
            "client_id": client_id,
            "updated_scopes": scopes_dict,
        },
    )


@csrf_exempt
def new_client(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        data = json.loads(request.body)
        endpoints = data.get("endpoints", "")
        columns = data.get("columns", "")

        client_id = secrets.token_urlsafe(16)
        client_secret = secrets.token_urlsafe(32)

        ClientScopesGet.objects.create(
            client_id=client_id,
            client_secret=client_secret,
            scopes=endpoints,
            is_active=1,
        )

        for endpoint in endpoints.split(", "):
            endpoint_columns = [
                col.split(": ")[1]
                for col in columns.split("; ")
                if col.startswith(endpoint)
            ]
            ClientEndpointsAccess.objects.create(
                client_id=client_id,
                endpoint=endpoint,
                allow_access=", ".join(endpoint_columns),
            )

        request.session["client_secret"] = client_secret

        return JsonResponse({"success": True, "client_id": client_id})

    scopes = ScopesGet.objects.all()
    scopes_data = [
        {"scope": scope.scope, "columns": scope.column_access.split(", ")}
        for scope in scopes
    ]
    return render(request, "apiportal/new_client.html", {"scopes_data": scopes_data})


def new_client_success(request: HttpRequest) -> HttpResponse:
    client_id = request.GET.get("client_id")
    client_secret = request.session.pop("client_secret", None)

    if not client_id:
        return HttpResponseNotFound("Client ID not provided.")

    granted_scopes = ClientEndpointsAccess.objects.filter(client_id=client_id).values(
        "endpoint", "allow_access"
    )

    scopes_dict = {entry["endpoint"]: entry["allow_access"] for entry in granted_scopes}

    return render(
        request,
        "apiportal/new_client_success.html",
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "granted_scopes": scopes_dict,
        },
    )
