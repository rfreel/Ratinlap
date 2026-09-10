from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any, Callable, Iterable


class Effect(str, Enum):
    READ = "READ"
    COMPUTE = "COMPUTE"
    VALIDATE = "VALIDATE"
    WRITE = "WRITE"
    OBSERVE = "OBSERVE"
    APPLICATION_INTERACTION = "APPLICATION_INTERACTION"


class FailureKind(str, Enum):
    ACCESS = "ACCESS"
    PARAMETER = "PARAMETER"
    DOMAIN = "DOMAIN"


class Cardinality(str, Enum):
    ONE_TO_ONE = "ONE_TO_ONE"
    ONE_TO_MANY = "ONE_TO_MANY"
    MANY_TO_ONE = "MANY_TO_ONE"
    MANY_TO_MANY = "MANY_TO_MANY"


class AsyncState(str, Enum):
    LOADING = "LOADING"
    SUCCEEDED = "SUCCEEDED"
    RELOADING = "RELOADING"
    FAILED = "FAILED"


@dataclass(frozen=True)
class AsyncValue:
    state: AsyncState
    value: Any = None
    error: str | None = None

    @staticmethod
    def loading() -> "AsyncValue":
        return AsyncValue(AsyncState.LOADING)

    @staticmethod
    def succeeded(value: Any) -> "AsyncValue":
        return AsyncValue(AsyncState.SUCCEEDED, value=value)

    @staticmethod
    def reloading(value: Any) -> "AsyncValue":
        return AsyncValue(AsyncState.RELOADING, value=value)

    @staticmethod
    def failed(error: str) -> "AsyncValue":
        return AsyncValue(AsyncState.FAILED, error=error)


@dataclass(frozen=True)
class ObjectTypeDef:
    api_name: str
    primary_key: str
    properties: dict[str, type]


@dataclass(frozen=True)
class LinkTypeDef:
    api_name: str
    source_type: str
    target_type: str
    cardinality: Cardinality = Cardinality.MANY_TO_MANY


@dataclass(frozen=True)
class ObjectRecord:
    type_name: str
    primary_key: Any
    properties: dict[str, Any]


@dataclass(frozen=True)
class LinkRecord:
    link_type: str
    source_key: Any
    target_key: Any


@dataclass(frozen=True)
class EventRecord:
    sequence: int
    kind: str
    object_type: str | None = None
    primary_key: Any = None
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    failure_kind: FailureKind | None = None
    message: str | None = None


@dataclass(frozen=True)
class Edit:
    object_type: str
    primary_key: Any
    changes: dict[str, Any]


@dataclass(frozen=True)
class ActionResult:
    validation: ValidationResult
    executed: bool
    edits: tuple[Edit, ...] = ()
    events: tuple[EventRecord, ...] = ()


DomainValidator = Callable[["ReferenceRuntime", dict[str, Any]], str | None]
EffectBuilder = Callable[["ReferenceRuntime", dict[str, Any]], Iterable[Edit]]
AccessPredicate = Callable[[str], bool]
FunctionHandler = Callable[["ReferenceRuntime", dict[str, Any]], Any]


@dataclass(frozen=True)
class ActionDef:
    api_name: str
    parameters: dict[str, type]
    effects: EffectBuilder
    domain_validator: DomainValidator | None = None
    access: AccessPredicate = lambda actor: True


@dataclass(frozen=True)
class FunctionDef:
    api_name: str
    handler: FunctionHandler


Expr = tuple[Any, ...]


class ObjectSet:
    """Immutable, composable query expression; materialization is explicit."""

    def __init__(self, runtime: "ReferenceRuntime", type_name: str, expr: Expr | None = None):
        self.runtime = runtime
        self.type_name = type_name
        self.expr: Expr = expr or ("base", type_name)

    def where(self, property_name: str, equals: Any) -> "ObjectSet":
        definition = self.runtime.object_types[self.type_name]
        if property_name not in definition.properties:
            raise ValueError(f"unknown property {self.type_name}.{property_name}")
        expected = definition.properties[property_name]
        if not isinstance(equals, expected):
            raise TypeError(f"predicate value for {property_name} must be {expected.__name__}")
        return ObjectSet(self.runtime, self.type_name, ("where", self.expr, property_name, equals))

    def union(self, *others: "ObjectSet") -> "ObjectSet":
        self._require_same_type(others)
        return ObjectSet(self.runtime, self.type_name, ("union", self.expr, *(o.expr for o in others)))

    def intersect(self, *others: "ObjectSet") -> "ObjectSet":
        self._require_same_type(others)
        return ObjectSet(self.runtime, self.type_name, ("intersect", self.expr, *(o.expr for o in others)))

    def subtract(self, *others: "ObjectSet") -> "ObjectSet":
        self._require_same_type(others)
        return ObjectSet(self.runtime, self.type_name, ("subtract", self.expr, *(o.expr for o in others)))

    def traverse(self, link_type: str) -> "ObjectSet":
        link = self.runtime.link_types[link_type]
        if link.source_type != self.type_name:
            raise ValueError(f"{link_type} starts at {link.source_type}, not {self.type_name}")
        return ObjectSet(self.runtime, link.target_type, ("traverse", self.expr, link_type))

    def fetch(self) -> list[ObjectRecord]:
        self.runtime.evaluation_count += 1
        keys = self.runtime._evaluate_expr(self.expr)
        return [self.runtime.objects[(self.type_name, key)] for key in sorted(keys, key=repr)]

    def count(self) -> int:
        return len(self.fetch())

    def sum(self, property_name: str) -> float:
        total = 0.0
        for obj in self.fetch():
            value = obj.properties[property_name]
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{property_name} is not numeric")
            total += float(value)
        return total

    def _require_same_type(self, others: Iterable["ObjectSet"]) -> None:
        for other in others:
            if other.runtime is not self.runtime or other.type_name != self.type_name:
                raise ValueError("ObjectSet composition requires the same runtime and object type")


class ReferenceRuntime:
    """Small executable semantic model. It is not a Palantir implementation claim."""

    def __init__(self) -> None:
        self.object_types: dict[str, ObjectTypeDef] = {}
        self.link_types: dict[str, LinkTypeDef] = {}
        self.objects: dict[tuple[str, Any], ObjectRecord] = {}
        self.links: list[LinkRecord] = []
        self.actions: dict[str, ActionDef] = {}
        self.functions: dict[str, FunctionDef] = {}
        self.subscribers: dict[str, list[Callable[[EventRecord], None]]] = {}
        self.events: list[EventRecord] = []
        self.evaluation_count = 0
        self._event_sequence = 0

    def register_object_type(self, definition: ObjectTypeDef) -> None:
        if definition.primary_key not in definition.properties:
            raise ValueError("primary key must be a declared property")
        self.object_types[definition.api_name] = definition

    def register_link_type(self, definition: LinkTypeDef) -> None:
        if definition.source_type not in self.object_types or definition.target_type not in self.object_types:
            raise ValueError("link endpoints must reference registered object types")
        self.link_types[definition.api_name] = definition

    def load_object(self, type_name: str, properties: dict[str, Any]) -> ObjectRecord:
        definition = self.object_types[type_name]
        self._validate_properties(definition, properties)
        pk = properties[definition.primary_key]
        record = ObjectRecord(type_name, pk, dict(properties))
        self.objects[(type_name, pk)] = record
        return record

    def load_link(self, link_type: str, source_key: Any, target_key: Any) -> LinkRecord:
        definition = self.link_types[link_type]
        self._require_object(definition.source_type, source_key)
        self._require_object(definition.target_type, target_key)
        candidate = LinkRecord(link_type, source_key, target_key)
        self._enforce_cardinality(definition, candidate)
        if candidate not in self.links:
            self.links.append(candidate)
        return candidate

    def object_set(self, type_name: str) -> ObjectSet:
        if type_name not in self.object_types:
            raise KeyError(type_name)
        return ObjectSet(self, type_name)

    def get(self, type_name: str, primary_key: Any) -> ObjectRecord:
        return self._require_object(type_name, primary_key)

    def register_function(self, definition: FunctionDef) -> None:
        self.functions[definition.api_name] = definition

    def execute_function(self, api_name: str, parameters: dict[str, Any]) -> Any:
        return self.functions[api_name].handler(self, dict(parameters))

    def register_action(self, definition: ActionDef) -> None:
        self.actions[definition.api_name] = definition

    def validate_action(self, api_name: str, parameters: dict[str, Any], actor: str) -> ValidationResult:
        action = self.actions[api_name]
        if not action.access(actor):
            return ValidationResult(False, FailureKind.ACCESS, f"actor {actor!r} may not execute {api_name}")
        for name, expected in action.parameters.items():
            if name not in parameters:
                return ValidationResult(False, FailureKind.PARAMETER, f"missing parameter: {name}")
            value = parameters[name]
            if not isinstance(value, expected):
                return ValidationResult(False, FailureKind.PARAMETER, f"parameter {name} must be {expected.__name__}")
        unknown = set(parameters) - set(action.parameters)
        if unknown:
            return ValidationResult(False, FailureKind.PARAMETER, f"unknown parameters: {sorted(unknown)}")
        if action.domain_validator is not None:
            message = action.domain_validator(self, dict(parameters))
            if message is not None:
                return ValidationResult(False, FailureKind.DOMAIN, message)
        return ValidationResult(True)

    def apply_action(
        self,
        api_name: str,
        parameters: dict[str, Any],
        actor: str,
        *,
        validate_only: bool = False,
        return_edits: bool = False,
    ) -> ActionResult:
        validation = self.validate_action(api_name, parameters, actor)
        if not validation.valid or validate_only:
            return ActionResult(validation=validation, executed=False)

        action = self.actions[api_name]
        edits = tuple(action.effects(self, dict(parameters)))
        staged = dict(self.objects)
        for edit in edits:
            current = staged[(edit.object_type, edit.primary_key)]
            updated_properties = dict(current.properties)
            updated_properties.update(edit.changes)
            self._validate_properties(self.object_types[edit.object_type], updated_properties)
            staged[(edit.object_type, edit.primary_key)] = replace(current, properties=updated_properties)

        self.objects = staged
        emitted: list[EventRecord] = []
        for edit in edits:
            event = self._emit(
                kind="object.updated",
                object_type=edit.object_type,
                primary_key=edit.primary_key,
                payload={"changes": dict(edit.changes), "action": api_name},
            )
            emitted.append(event)
        return ActionResult(
            validation=validation,
            executed=True,
            edits=edits if return_edits else (),
            events=tuple(emitted),
        )

    def subscribe(self, object_type: str, listener: Callable[[EventRecord], None]) -> Callable[[], None]:
        listeners = self.subscribers.setdefault(object_type, [])
        listeners.append(listener)

        def unsubscribe() -> None:
            if listener in listeners:
                listeners.remove(listener)

        return unsubscribe

    def _emit(self, kind: str, object_type: str | None, primary_key: Any, payload: dict[str, Any]) -> EventRecord:
        self._event_sequence += 1
        event = EventRecord(self._event_sequence, kind, object_type, primary_key, dict(payload))
        self.events.append(event)
        if object_type is not None:
            for listener in tuple(self.subscribers.get(object_type, ())):
                listener(event)
        return event

    def _evaluate_expr(self, expr: Expr) -> set[Any]:
        kind = expr[0]
        if kind == "base":
            type_name = expr[1]
            return {pk for (t, pk) in self.objects if t == type_name}
        if kind == "where":
            parent, prop, expected = expr[1], expr[2], expr[3]
            base = self._evaluate_expr(parent)
            type_name = self._expr_type(parent)
            return {pk for pk in base if self.objects[(type_name, pk)].properties.get(prop) == expected}
        if kind in {"union", "intersect", "subtract"}:
            parts = [self._evaluate_expr(part) for part in expr[1:]]
            if kind == "union":
                result: set[Any] = set()
                for part in parts:
                    result |= part
                return result
            if kind == "intersect":
                result = set(parts[0])
                for part in parts[1:]:
                    result &= part
                return result
            result = set(parts[0])
            for part in parts[1:]:
                result -= part
            return result
        if kind == "traverse":
            parent, link_type = expr[1], expr[2]
            source_keys = self._evaluate_expr(parent)
            return {link.target_key for link in self.links if link.link_type == link_type and link.source_key in source_keys}
        raise ValueError(f"unknown ObjectSet expression: {kind}")

    def _expr_type(self, expr: Expr) -> str:
        kind = expr[0]
        if kind == "base":
            return expr[1]
        if kind in {"where", "union", "intersect", "subtract"}:
            return self._expr_type(expr[1])
        if kind == "traverse":
            return self.link_types[expr[2]].target_type
        raise ValueError(kind)

    def _validate_properties(self, definition: ObjectTypeDef, properties: dict[str, Any]) -> None:
        missing = set(definition.properties) - set(properties)
        unknown = set(properties) - set(definition.properties)
        if missing:
            raise ValueError(f"missing properties for {definition.api_name}: {sorted(missing)}")
        if unknown:
            raise ValueError(f"unknown properties for {definition.api_name}: {sorted(unknown)}")
        for name, expected in definition.properties.items():
            if not isinstance(properties[name], expected):
                raise TypeError(f"{definition.api_name}.{name} must be {expected.__name__}")

    def _require_object(self, type_name: str, primary_key: Any) -> ObjectRecord:
        key = (type_name, primary_key)
        if key not in self.objects:
            raise KeyError(key)
        return self.objects[key]

    def _enforce_cardinality(self, definition: LinkTypeDef, candidate: LinkRecord) -> None:
        same_type = [link for link in self.links if link.link_type == candidate.link_type]
        if definition.cardinality in {Cardinality.ONE_TO_ONE, Cardinality.MANY_TO_ONE}:
            if any(link.source_key == candidate.source_key and link.target_key != candidate.target_key for link in same_type):
                raise ValueError(f"{definition.api_name} cardinality forbids another target for source {candidate.source_key!r}")
        if definition.cardinality in {Cardinality.ONE_TO_ONE, Cardinality.ONE_TO_MANY}:
            if any(link.target_key == candidate.target_key and link.source_key != candidate.source_key for link in same_type):
                raise ValueError(f"{definition.api_name} cardinality forbids another source for target {candidate.target_key!r}")


class OntologyClient:
    """Ontology-bound facade; the bound identifier is part of the client contract."""

    kind = "ONTOLOGY_BOUND"

    def __init__(self, runtime: ReferenceRuntime, ontology_id: str):
        if not ontology_id:
            raise ValueError("ontology_id is required")
        self.runtime = runtime
        self.ontology_id = ontology_id

    def object_set(self, type_name: str) -> ObjectSet:
        return self.runtime.object_set(type_name)

    def apply_action(self, api_name: str, parameters: dict[str, Any], actor: str, **options: Any) -> ActionResult:
        return self.runtime.apply_action(api_name, parameters, actor, **options)

    def subscribe(self, object_type: str, listener: Callable[[EventRecord], None]) -> Callable[[], None]:
        return self.runtime.subscribe(object_type, listener)


class PlatformClient:
    """Broader facade deliberately not bound to one ontology identifier."""

    kind = "PLATFORM"

    def __init__(self, runtime: ReferenceRuntime):
        self.runtime = runtime

    def execute_function(self, api_name: str, parameters: dict[str, Any]) -> Any:
        return self.runtime.execute_function(api_name, parameters)


class ApplicationBridge:
    """Local reference for typed async values plus configured event execution."""

    def __init__(self) -> None:
        self.values: dict[str, AsyncValue] = {}
        self.events: dict[str, Callable[[], Any]] = {}

    def set_value(self, field_id: str, value: AsyncValue) -> None:
        self.values[field_id] = value

    def register_event(self, event_id: str, callback: Callable[[], Any]) -> None:
        self.events[event_id] = callback

    def execute_event(self, event_id: str) -> Any:
        if event_id not in self.events:
            raise KeyError(event_id)
        return self.events[event_id]()
