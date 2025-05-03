from typing import List, Dict, Any
import logging

from django.db import transaction
from django.urls import reverse

from django.shortcuts import redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse

from .models import ClientScopesGet, ClientEndpointsAccess, ScopesGet

logger = logging.getLogger(__name__)


def get_client_and_scopes(client_id: str) -> Dict[str, Any]:
    client = get_object_or_404(ClientScopesGet, client_id=client_id)
    logger.info(f"Client ID: {client_id}")

    current_scopes = client.scopes.split(", ") if client.scopes else []
    logger.info(f"Current scopes: {current_scopes}")

    other_scopes = ScopesGet.objects.exclude(scope__in=current_scopes).values_list(
        "scope", flat=True
    )
    logger.info(f"Other scopes: {other_scopes}")

    return {
        "client": client,
        "current_scopes": current_scopes,
        "other_scopes": other_scopes,
    }


def prepare_scopes_data(
    current_scopes: List[str], client_id: str
) -> List[Dict[str, Any]]:
    scopes_data = []
    for scope in current_scopes:
        scope_data = ScopesGet.objects.filter(scope=scope).first()
        logger.info(f"Scope data: {scope_data}")

        if scope_data:
            allow_access = (
                ClientEndpointsAccess.objects.filter(
                    client_id=client_id, endpoint=scope
                )
                .values_list("allow_access", flat=True)
                .first()
            )
            logger.info(f"Allow access: {allow_access}")

            current_access = allow_access.split(", ") if allow_access else []
            logger.info(f"Current access: {current_access}")

            columns = [
                {"name": column, "access": column in current_access}
                for column in scope_data.column_access.split(", ")
            ]
            logger.info(f"Columns: {columns}")

            scopes_data.append({"scope": scope, "columns": columns})
            logger.info(f"Scopes data: {scopes_data}")

    return scopes_data


def process_post_request(
    request: HttpRequest, client: ClientScopesGet, current_scopes: List[str]
) -> HttpResponse:
    new_scopes = request.POST.get("scopes", "").strip()

    column_access_input = request.POST.get("column_access", "").strip()

    removed_columns_input = request.POST.get("removed_columns", "").strip()

    removed_scopes_input = request.POST.get("removed_scopes", "").strip()

    if new_scopes:
        client.scopes = new_scopes
        client.save()

    removed_scopes_list = (
        removed_scopes_input.split(", ") if removed_scopes_input else []
    )

    column_access_dict: Dict[str, Any] = parse_input(column_access_input)
    removed_columns_dict: Dict[str, Any] = parse_input(removed_columns_input)

    with transaction.atomic():
        delete_removed_scopes(client.client_id, removed_scopes_list)
        update_scopes_access(
            client.client_id,
            current_scopes,
            removed_scopes_list,
            column_access_dict,
            removed_columns_dict,
        )

    return redirect(
        reverse("client_scopes_edit_success") + f"?client_id={client.client_id}"
    )


def parse_input(input_data: str) -> Dict[str, List[str]]:
    parsed_data = {}
    if input_data:
        for item in input_data.split("; "):
            if ": " in item:
                scope, columns = item.split(": ")
                parsed_data[scope] = columns.split(", ")
    logger.info(f"Parsed input data: {parsed_data}")
    return parsed_data


def delete_removed_scopes(client_id: str, removed_scopes_list: List[str]) -> None:
    for scope in removed_scopes_list:
        ClientEndpointsAccess.objects.filter(
            client_id=client_id, endpoint=scope
        ).delete()


def update_scopes_access(
    client_id: str,
    current_scopes: List[str],
    removed_scopes_list: List[str],
    column_access_dict: Dict[str, List[str]],
    removed_columns_dict: Dict[str, List[str]],
) -> None:
    for scope in current_scopes:
        logger.info(f"Scope: {scope}")

        if scope in removed_scopes_list:
            continue

        existing_access = ClientEndpointsAccess.objects.filter(
            client_id=client_id, endpoint=scope
        ).first()
        logger.info(f"Existing access: {existing_access}")

        existing_columns = (
            existing_access.allow_access.split(", ")
            if existing_access and existing_access.allow_access
            else []
        )
        logger.info(f"Existing columns: {existing_columns}")

        new_columns = column_access_dict.get(scope, [])
        logger.info(f"New columns: {new_columns}")

        columns_to_remove = removed_columns_dict.get(scope, [])
        logger.info(f"Columns to remove: {columns_to_remove}")

        final_columns = [
            col
            for col in set(existing_columns + new_columns)
            if col not in columns_to_remove
        ]

        logger.info(f"Final columns: {final_columns}")

        if existing_access:
            existing_access.allow_access = ", ".join(final_columns)
            existing_access.save()
        elif new_columns:
            ClientEndpointsAccess.objects.create(
                client_id=client_id,
                endpoint=scope,
                allow_access=", ".join(new_columns),
            )
