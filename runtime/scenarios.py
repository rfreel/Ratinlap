from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from runtime.reference import (
    ActionDef,
    ApplicationBridge,
    AsyncState,
    AsyncValue,
    Cardinality,
    Edit,
    FailureKind,
    FunctionDef,
    LinkTypeDef,
    ObjectTypeDef,
    OntologyClient,
    PlatformClient,
    ReferenceRuntime,
)


@dataclass(frozen=True)
class Scenario:
    id: str
    scopes: tuple[str, ...]
    description: str
    run: Callable[[], None]


def build_demo_runtime() -> ReferenceRuntime:
    runtime = ReferenceRuntime()
    runtime.register_object_type(ObjectTypeDef("Customer", "id", {"id": str, "name": str, "region": str}))
    runtime.register_object_type(ObjectTypeDef("Order", "id", {"id": str, "status": str, "total": int}))
    runtime.register_link_type(LinkTypeDef("customerOrders", "Customer", "Order", Cardinality.ONE_TO_MANY))

    runtime.load_object("Customer", {"id": "c1", "name": "Alpha", "region": "west"})
    runtime.load_object("Customer", {"id": "c2", "name": "Beta", "region": "east"})
    runtime.load_object("Order", {"id": "o1", "status": "pending", "total": 10})
    runtime.load_object("Order", {"id": "o2", "status": "shipped", "total": 20})
    runtime.load_object("Order", {"id": "o3", "status": "pending", "total": 30})
    runtime.load_link("customerOrders", "c1", "o1")
    runtime.load_link("customerOrders", "c1", "o2")
    runtime.load_link("customerOrders", "c2", "o3")

    def validate_cancel(rt: ReferenceRuntime, p: dict) -> str | None:
        order = rt.get("Order", p["order_id"])
        if order.properties["status"] == "shipped":
            return "SHIPPED_ORDER_CANNOT_BE_CANCELLED"
        return None

    def cancel_effects(rt: ReferenceRuntime, p: dict):
        rt.get("Order", p["order_id"])
        return [Edit("Order", p["order_id"], {"status": "cancelled"})]

    runtime.register_action(ActionDef(
        "cancelOrder",
        {"order_id": str, "reason": str},
        effects=cancel_effects,
        domain_validator=validate_cancel,
        access=lambda actor: actor in {"planner", "admin"},
    ))
    runtime.register_function(FunctionDef(
        "customerTotal",
        lambda rt, p: rt.object_set("Customer")
            .where("id", p["customer_id"])
            .traverse("customerOrders")
            .sum("total"),
    ))
    return runtime


def scenario_definition_state() -> None:
    runtime = build_demo_runtime()
    definition = runtime.object_types["Order"]
    state = runtime.get("Order", "o1")
    assert definition.api_name == state.type_name
    assert definition.primary_key == "id"
    assert state.primary_key == "o1"
    assert state.properties["total"] == 10


def scenario_relation_traversal_cardinality() -> None:
    runtime = build_demo_runtime()
    result = runtime.object_set("Customer").where("id", "c1").traverse("customerOrders").fetch()
    assert {obj.primary_key for obj in result} == {"o1", "o2"}
    try:
        runtime.load_link("customerOrders", "c2", "o1")
    except ValueError as exc:
        assert "cardinality" in str(exc)
    else:
        raise AssertionError("ONE_TO_MANY cardinality did not reject a second source for o1")


def scenario_objectset_composition() -> None:
    runtime = build_demo_runtime()
    base = runtime.object_set("Order")
    pending = base.where("status", "pending")
    shipped = base.where("status", "shipped")
    composed = pending.union(shipped).intersect(base).subtract(shipped)
    assert runtime.evaluation_count == 0
    assert composed.expr[0] == "subtract"
    materialized = composed.fetch()
    assert [obj.primary_key for obj in materialized] == ["o1", "o3"]
    assert pending.sum("total") == 40.0


def scenario_action_modes_and_failures() -> None:
    runtime = build_demo_runtime()
    original = runtime.get("Order", "o1")
    validate_only = runtime.apply_action(
        "cancelOrder",
        {"order_id": "o1", "reason": "customer request"},
        "planner",
        validate_only=True,
        return_edits=True,
    )
    assert validate_only.validation.valid is True
    assert validate_only.executed is False
    assert runtime.get("Order", "o1") == original

    access = runtime.validate_action("cancelOrder", {"order_id": "o1", "reason": "x"}, "viewer")
    parameter = runtime.validate_action("cancelOrder", {"order_id": "o1"}, "planner")
    domain = runtime.validate_action("cancelOrder", {"order_id": "o2", "reason": "x"}, "planner")
    assert access.failure_kind == FailureKind.ACCESS
    assert parameter.failure_kind == FailureKind.PARAMETER
    assert domain.failure_kind == FailureKind.DOMAIN

    executed = runtime.apply_action(
        "cancelOrder",
        {"order_id": "o1", "reason": "customer request"},
        "planner",
        return_edits=True,
    )
    assert executed.executed is True
    assert executed.edits[0].changes == {"status": "cancelled"}
    assert runtime.get("Order", "o1").properties["status"] == "cancelled"


def scenario_compute() -> None:
    runtime = build_demo_runtime()
    before = runtime.get("Order", "o1")
    result = runtime.execute_function("customerTotal", {"customer_id": "c1"})
    assert result == 30.0
    assert runtime.get("Order", "o1") == before


def scenario_observe_and_async() -> None:
    runtime = build_demo_runtime()
    seen = []
    unsubscribe = runtime.subscribe("Order", seen.append)
    runtime.apply_action("cancelOrder", {"order_id": "o1", "reason": "x"}, "planner")
    unsubscribe()
    runtime.apply_action("cancelOrder", {"order_id": "o3", "reason": "x"}, "planner")
    assert len(seen) == 1
    assert seen[0].kind == "object.updated"
    assert seen[0].primary_key == "o1"
    states = [
        AsyncValue.loading(),
        AsyncValue.succeeded("o1"),
        AsyncValue.reloading("o1"),
        AsyncValue.failed("network"),
    ]
    assert [value.state for value in states] == [
        AsyncState.LOADING,
        AsyncState.SUCCEEDED,
        AsyncState.RELOADING,
        AsyncState.FAILED,
    ]


def scenario_client_boundary() -> None:
    runtime = build_demo_runtime()
    ontology = OntologyClient(runtime, "ri.ontology.main")
    platform = PlatformClient(runtime)
    assert ontology.kind == "ONTOLOGY_BOUND"
    assert ontology.ontology_id == "ri.ontology.main"
    assert platform.kind == "PLATFORM"
    assert not hasattr(platform, "ontology_id")
    assert ontology.object_set("Order").count() == 3
    assert platform.execute_function("customerTotal", {"customer_id": "c2"}) == 30.0


def scenario_application_bridge() -> None:
    bridge = ApplicationBridge()
    bridge.set_value("selection", AsyncValue.loading())
    assert bridge.values["selection"].state == AsyncState.LOADING
    bridge.set_value("selection", AsyncValue.succeeded("o1"))
    assert bridge.values["selection"].value == "o1"
    called: list[str] = []
    bridge.register_event("openOrder", lambda: called.append("o1") or "ok")
    assert bridge.execute_event("openOrder") == "ok"
    assert called == ["o1"]


SCENARIOS = (
    Scenario("definition-state", ("S01", "S02"), "Definition/instance identity and typed properties remain distinct.", scenario_definition_state),
    Scenario("relation-traversal", ("S03",), "Typed link traversal and cardinality are explicit.", scenario_relation_traversal_cardinality),
    Scenario("objectset-composition", ("S04",), "ObjectSet composes before explicit materialization and supports aggregation.", scenario_objectset_composition),
    Scenario("action-modes-failures", ("S05", "S07"), "Validate-only differs from execution; access, parameter, and domain failures do not collapse.", scenario_action_modes_and_failures),
    Scenario("compute", ("S06",), "Named computation is represented separately from action mutation.", scenario_compute),
    Scenario("observe-async", ("S08",), "Subscriptions and loading/reloading/failure states remain explicit.", scenario_observe_and_async),
    Scenario("client-boundary", ("S09",), "Ontology-bound and broader platform clients remain distinct facades.", scenario_client_boundary),
    Scenario("application-bridge", ("S10",), "Application bridge carries explicit async values and configured event execution.", scenario_application_bridge),
)


def run_scenarios() -> dict:
    rows = []
    covered: set[str] = set()
    for scenario in SCENARIOS:
        try:
            scenario.run()
        except Exception as exc:
            rows.append({
                "id": scenario.id,
                "scopes": list(scenario.scopes),
                "description": scenario.description,
                "status": "FAIL",
                "error": f"{type(exc).__name__}: {exc}",
            })
        else:
            covered.update(scenario.scopes)
            rows.append({
                "id": scenario.id,
                "scopes": list(scenario.scopes),
                "description": scenario.description,
                "status": "PASS",
            })
    required = {f"S{i:02d}" for i in range(1, 11)}
    missing = sorted(required - covered)
    all_pass = all(row["status"] == "PASS" for row in rows) and not missing
    return {
        "schema_version": "0.1",
        "target": "EXECUTABLE_CORE_READY",
        "status": "PASS" if all_pass else "FAIL",
        "summary": {
            "passed": sum(row["status"] == "PASS" for row in rows),
            "failed": sum(row["status"] == "FAIL" for row in rows),
            "required_scopes": 10,
            "covered_scopes": len(covered & required),
            "missing_scopes": missing,
        },
        "scenarios": rows,
    }
