from __future__ import annotations

import json
import re
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, unquote, urlsplit

from compat.wire import (
    CompatError,
    access_failure,
    compat_error_to_wire,
    edit_results_to_wire,
    object_to_wire,
    object_type_to_wire,
    require_list,
    require_object,
    translate_object_set,
    validation_to_wire,
)
from runtime.reference import ReferenceRuntime
from runtime.scenarios import build_demo_runtime


@dataclass(frozen=True)
class Response:
    status: int
    body: dict[str, Any]


ROUTES = {
    "object_type": re.compile(r"^/v2/ontologies/([^/]+)/objectTypes/([^/]+)$"),
    "objects": re.compile(r"^/v2/ontologies/([^/]+)/objects/([^/]+)$"),
    "object": re.compile(r"^/v2/ontologies/([^/]+)/objects/([^/]+)/([^/]+)$"),
    "links": re.compile(r"^/v2/ontologies/([^/]+)/objects/([^/]+)/([^/]+)/links/([^/]+)$"),
    "load": re.compile(r"^/v2/ontologies/([^/]+)/objectSets/loadObjects$"),
    "aggregate": re.compile(r"^/v2/ontologies/([^/]+)/objectSets/aggregate$"),
    "apply": re.compile(r"^/v2/ontologies/([^/]+)/actions/([^/]+)/apply$"),
}


class CompatApp:
    def __init__(self, runtime: ReferenceRuntime | None = None, ontology_id: str = "ri.ontology.main") -> None:
        self.runtime = runtime or build_demo_runtime()
        self.ontology_id = ontology_id

    def dispatch(
        self,
        method: str,
        target: str,
        body: Any = None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        headers = {k.lower(): v for k, v in (headers or {}).items()}
        split = urlsplit(target)
        path = split.path
        query = parse_qs(split.query)
        try:
            response = self._dispatch(method.upper(), path, query, body, headers)
        except CompatError as exc:
            return Response(exc.status, compat_error_to_wire(exc))
        except KeyError as exc:
            return Response(404, compat_error_to_wire(CompatError(404, "NOT_FOUND", str(exc))))
        return response

    def _dispatch(
        self,
        method: str,
        path: str,
        query: dict[str, list[str]],
        body: Any,
        headers: dict[str, str],
    ) -> Response:
        match = ROUTES["object_type"].match(path)
        if match and method == "GET":
            ontology, object_type = map(unquote, match.groups())
            self._require_ontology(ontology)
            return Response(200, object_type_to_wire(self.runtime, object_type))

        match = ROUTES["links"].match(path)
        if match and method == "GET":
            ontology, source_type, primary_key, link_type = map(unquote, match.groups())
            self._require_ontology(ontology)
            select = _select_from_query(query)
            return Response(200, self._linked_objects(source_type, primary_key, link_type, select))

        match = ROUTES["object"].match(path)
        if match and method == "GET":
            ontology, object_type, primary_key = map(unquote, match.groups())
            self._require_ontology(ontology)
            select = _select_from_query(query)
            record = self.runtime.get(object_type, primary_key)
            return Response(200, object_to_wire(record, select))

        match = ROUTES["objects"].match(path)
        if match and method == "GET":
            ontology, object_type = map(unquote, match.groups())
            self._require_ontology(ontology)
            select = _select_from_query(query)
            if "pageToken" in query:
                raise CompatError(400, "UNSUPPORTED_PAGING", "pageToken is not supported in this slice")
            records = self.runtime.object_set(object_type).fetch()
            page_size = _optional_positive_int(query, "pageSize")
            if page_size is not None and page_size < len(records):
                raise CompatError(400, "UNSUPPORTED_PAGING", "requested pageSize would require nextPageToken support")
            return Response(200, {"data": [object_to_wire(obj, select) for obj in records]})

        match = ROUTES["load"].match(path)
        if match and method == "POST":
            ontology = unquote(match.group(1))
            self._require_ontology(ontology)
            request = require_object(body, "body")
            if request.get("pageToken") is not None:
                raise CompatError(400, "UNSUPPORTED_PAGING", "pageToken is not supported in this slice")
            select = require_list(request.get("select"), "select")
            if not all(isinstance(item, str) for item in select):
                raise CompatError(400, "INVALID_ARGUMENT", "select entries must be strings")
            object_set = translate_object_set(self.runtime, request.get("objectSet"))
            records = object_set.fetch()
            page_size = request.get("pageSize")
            if page_size is not None:
                if not isinstance(page_size, int) or isinstance(page_size, bool) or page_size <= 0:
                    raise CompatError(400, "INVALID_ARGUMENT", "pageSize must be a positive integer")
                if page_size < len(records):
                    raise CompatError(400, "UNSUPPORTED_PAGING", "requested pageSize would require nextPageToken support")
            return Response(200, {"data": [object_to_wire(obj, select) for obj in records]})

        match = ROUTES["aggregate"].match(path)
        if match and method == "POST":
            ontology = unquote(match.group(1))
            self._require_ontology(ontology)
            request = require_object(body, "body")
            object_set = translate_object_set(self.runtime, request.get("objectSet"))
            group_by = require_list(request.get("groupBy"), "groupBy")
            if group_by:
                raise CompatError(400, "UNSUPPORTED_WIRE_VARIANT", "non-empty groupBy is not supported in this slice")
            metrics_wire = require_list(request.get("aggregation"), "aggregation")
            if not metrics_wire:
                raise CompatError(400, "INVALID_ARGUMENT", "aggregation must not be empty")
            metrics: list[dict[str, Any]] = []
            for index, item in enumerate(metrics_wire):
                metric = require_object(item, f"aggregation[{index}]")
                kind = metric.get("type")
                name = metric.get("name", kind)
                if not isinstance(name, str):
                    raise CompatError(400, "INVALID_ARGUMENT", "aggregation.name must be a string")
                if kind == "count":
                    value: int | float = object_set.count()
                elif kind == "sum":
                    field = metric.get("field")
                    if not isinstance(field, str):
                        raise CompatError(400, "INVALID_ARGUMENT", "sum.field must be a string")
                    try:
                        value = object_set.sum(field)
                    except (KeyError, TypeError, ValueError) as exc:
                        raise CompatError(400, "INVALID_ARGUMENT", str(exc)) from exc
                else:
                    raise CompatError(400, "UNSUPPORTED_WIRE_VARIANT", f"aggregation type {kind!r} is not supported")
                metrics.append({"name": name, "value": value})
            return Response(200, {"accuracy": "ACCURATE", "data": [{"group": {}, "metrics": metrics}]})

        match = ROUTES["apply"].match(path)
        if match and method == "POST":
            ontology, action_name = map(unquote, match.groups())
            self._require_ontology(ontology)
            request = require_object(body, "body")
            parameters = require_object(request.get("parameters"), "parameters")
            options = request.get("options") or {}
            options = require_object(options, "options")
            mode = options.get("mode", "VALIDATE_AND_EXECUTE")
            if mode not in {"VALIDATE_ONLY", "VALIDATE_AND_EXECUTE"}:
                raise CompatError(400, "UNSUPPORTED_WIRE_VARIANT", f"action mode {mode!r} is not supported")
            return_edits = options.get("returnEdits", "NONE")
            if return_edits not in {"NONE", "ALL_V2_WITH_DELETIONS"}:
                raise CompatError(400, "UNSUPPORTED_WIRE_VARIANT", f"returnEdits {return_edits!r} is not supported")
            actor = headers.get("x-ratinlap-actor", "viewer")
            validation = self.runtime.validate_action(action_name, parameters, actor)
            if access_failure(validation):
                raise CompatError(403, "FORBIDDEN", validation.message or "access denied")
            if not validation.valid:
                return Response(200, {"validation": validation_to_wire(validation)})
            result = self.runtime.apply_action(
                action_name,
                parameters,
                actor,
                validate_only=(mode == "VALIDATE_ONLY"),
                return_edits=(return_edits != "NONE"),
            )
            response_body: dict[str, Any] = {"validation": validation_to_wire(result.validation)}
            if return_edits != "NONE" and result.executed:
                response_body["edits"] = edit_results_to_wire(result.edits)
            return Response(200, response_body)

        if any(regex.match(path) for regex in ROUTES.values()):
            raise CompatError(405, "METHOD_NOT_ALLOWED", f"method {method} is not supported for {path}")
        raise CompatError(404, "ROUTE_NOT_FOUND", f"no supported route for {path}")

    def _require_ontology(self, ontology: str) -> None:
        if ontology != self.ontology_id:
            raise CompatError(404, "NOT_FOUND", f"ontology {ontology!r} not found")

    def _linked_objects(self, source_type: str, primary_key: str, link_type: str, select: list[str] | None) -> dict[str, Any]:
        self.runtime.get(source_type, primary_key)
        try:
            definition = self.runtime.link_types[link_type]
        except KeyError as exc:
            raise CompatError(404, "NOT_FOUND", f"link type {link_type!r} not found") from exc
        if definition.source_type != source_type:
            raise CompatError(400, "INVALID_ARGUMENT", f"{link_type} does not originate from {source_type}")
        target_keys = [
            link.target_key
            for link in self.runtime.links
            if link.link_type == link_type and link.source_key == primary_key
        ]
        records = [self.runtime.get(definition.target_type, key) for key in sorted(target_keys, key=repr)]
        return {"data": [object_to_wire(record, select) for record in records]}


def _select_from_query(query: dict[str, list[str]]) -> list[str] | None:
    if "select" not in query:
        return None
    values: list[str] = []
    for item in query["select"]:
        values.extend(part for part in item.split(",") if part)
    return values


def _optional_positive_int(query: dict[str, list[str]], key: str) -> int | None:
    if key not in query:
        return None
    raw = query[key][-1]
    try:
        value = int(raw)
    except ValueError as exc:
        raise CompatError(400, "INVALID_ARGUMENT", f"{key} must be a positive integer") from exc
    if value <= 0:
        raise CompatError(400, "INVALID_ARGUMENT", f"{key} must be a positive integer")
    return value


class CompatHandler(BaseHTTPRequestHandler):
    app: CompatApp = CompatApp()

    def do_GET(self) -> None:
        self._handle(None)

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        raw = self.rfile.read(length) if length else b""
        if raw:
            try:
                body = json.loads(raw)
            except json.JSONDecodeError:
                self._send(Response(400, compat_error_to_wire(CompatError(400, "INVALID_JSON", "request body is not valid JSON"))))
                return
        else:
            body = None
        self._handle(body)

    def _handle(self, body: Any) -> None:
        headers = {key: value for key, value in self.headers.items()}
        self._send(self.app.dispatch(self.command, self.path, body, headers))

    def _send(self, response: Response) -> None:
        encoded = json.dumps(response.body, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.send_response(response.status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args: Any) -> None:
        return


def make_server(host: str = "127.0.0.1", port: int = 0, app: CompatApp | None = None) -> ThreadingHTTPServer:
    handler = type("BoundCompatHandler", (CompatHandler,), {"app": app or CompatApp()})
    return ThreadingHTTPServer((host, port), handler)
