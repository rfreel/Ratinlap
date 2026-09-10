from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.reference import FailureKind, ObjectRecord, ObjectSet, ReferenceRuntime, ValidationResult


@dataclass(frozen=True)
class CompatError(Exception):
    status: int
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


def require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CompatError(400, "INVALID_ARGUMENT", f"{label} must be an object")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise CompatError(400, "INVALID_ARGUMENT", f"{label} must be an array")
    return value


def translate_object_set(runtime: ReferenceRuntime, value: Any) -> ObjectSet:
    wire = require_object(value, "objectSet")
    kind = wire.get("type")
    try:
        if kind == "base":
            object_type = wire.get("objectType")
            if not isinstance(object_type, str):
                raise CompatError(400, "INVALID_ARGUMENT", "base.objectType must be a string")
            return runtime.object_set(object_type)
        if kind == "filter":
            parent = translate_object_set(runtime, wire.get("objectSet"))
            query = require_object(wire.get("where"), "filter.where")
            if query.get("type") != "eq":
                raise CompatError(400, "UNSUPPORTED_WIRE_VARIANT", f"SearchJsonQueryV2 type {query.get('type')!r} is not supported")
            field = query.get("field")
            if not isinstance(field, str):
                raise CompatError(400, "INVALID_ARGUMENT", "eq.field must be a string")
            return parent.where(field, query.get("value"))
        if kind in {"union", "intersect", "subtract"}:
            parts_wire = require_list(wire.get("objectSets"), f"{kind}.objectSets")
            if not parts_wire:
                raise CompatError(400, "INVALID_ARGUMENT", f"{kind}.objectSets must not be empty")
            parts = [translate_object_set(runtime, item) for item in parts_wire]
            head, tail = parts[0], parts[1:]
            if kind == "union":
                return head.union(*tail)
            if kind == "intersect":
                return head.intersect(*tail)
            return head.subtract(*tail)
        if kind == "searchAround":
            parent = translate_object_set(runtime, wire.get("objectSet"))
            link = wire.get("link")
            if not isinstance(link, str):
                raise CompatError(400, "INVALID_ARGUMENT", "searchAround.link must be a string")
            return parent.traverse(link)
    except CompatError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise CompatError(400, "INVALID_ARGUMENT", str(exc)) from exc
    raise CompatError(400, "UNSUPPORTED_WIRE_VARIANT", f"ObjectSet type {kind!r} is not supported")


def object_to_wire(record: ObjectRecord, select: list[str] | None = None) -> dict[str, Any]:
    properties = record.properties
    if select is None:
        selected = list(properties)
    else:
        selected = select
        unknown = set(selected) - set(properties)
        if unknown:
            raise CompatError(400, "INVALID_ARGUMENT", f"unknown selected properties: {sorted(unknown)}")
    out: dict[str, Any] = {
        "__apiName": record.type_name,
        "__primaryKey": record.primary_key,
    }
    for name in selected:
        value = properties[name]
        if value is not None:
            out[name] = value
    return out


def object_type_to_wire(runtime: ReferenceRuntime, object_type: str) -> dict[str, Any]:
    try:
        definition = runtime.object_types[object_type]
    except KeyError as exc:
        raise CompatError(404, "NOT_FOUND", f"object type {object_type!r} not found") from exc
    return {
        "apiName": definition.api_name,
        "primaryKey": definition.primary_key,
        "properties": {
            name: {"apiName": name, "type": python_type_to_wire(py_type)}
            for name, py_type in definition.properties.items()
        },
    }


def python_type_to_wire(py_type: type) -> str:
    return {str: "string", int: "integer", float: "double", bool: "boolean"}.get(py_type, "unknown")


def validation_to_wire(validation: ValidationResult) -> dict[str, Any]:
    return {
        "result": "VALID" if validation.valid else "INVALID",
        "submissionCriteria": [],
        "parameters": {},
    }


def edit_results_to_wire(edits: tuple[Any, ...]) -> dict[str, Any]:
    return {
        "type": "edits",
        "edits": [
            {
                "type": "modifyObject",
                "objectType": edit.object_type,
                "primaryKey": edit.primary_key,
            }
            for edit in edits
        ],
        "deletedObjectsCount": 0,
        "deletedLinksCount": 0,
    }


def compat_error_to_wire(error: CompatError) -> dict[str, Any]:
    return {
        "errorCode": error.code,
        "errorName": error.code,
        "errorDescription": error.message,
        "statusCode": error.status,
    }


def access_failure(validation: ValidationResult) -> bool:
    return (not validation.valid) and validation.failure_kind == FailureKind.ACCESS
