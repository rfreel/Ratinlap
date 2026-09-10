from __future__ import annotations

import unittest

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


def build_runtime() -> ReferenceRuntime:
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
        return "SHIPPED_ORDER_CANNOT_BE_CANCELLED" if order.properties["status"] == "shipped" else None

    def cancel_effects(rt: ReferenceRuntime, p: dict):
        rt.get("Order", p["order_id"])
        return [Edit("Order", p["order_id"], {"status": "cancelled"})]

    runtime.register_action(ActionDef(
        "cancelOrder", {"order_id": str, "reason": str}, effects=cancel_effects,
        domain_validator=validate_cancel, access=lambda actor: actor in {"planner", "admin"},
    ))
    runtime.register_function(FunctionDef(
        "customerTotal",
        lambda rt, p: rt.object_set("Customer").where("id", p["customer_id"]).traverse("customerOrders").sum("total"),
    ))
    return runtime


class ReferenceRuntimeTests(unittest.TestCase):
    def test_definition_and_instance_state_are_distinct(self):
        runtime = build_runtime()
        definition = runtime.object_types["Order"]
        instance = runtime.get("Order", "o1")
        self.assertEqual(definition.primary_key, "id")
        self.assertEqual(instance.primary_key, "o1")
        self.assertEqual(instance.type_name, definition.api_name)
        self.assertEqual(instance.properties["total"], 10)

    def test_objectset_is_compositional_before_materialization(self):
        runtime = build_runtime()
        base = runtime.object_set("Order")
        pending = base.where("status", "pending")
        shipped = base.where("status", "shipped")
        composed = pending.union(shipped).subtract(shipped)
        self.assertEqual(runtime.evaluation_count, 0)
        self.assertEqual(composed.expr[0], "subtract")
        self.assertEqual([o.primary_key for o in composed.fetch()], ["o1", "o3"])
        self.assertEqual(runtime.evaluation_count, 1)
        self.assertEqual(pending.sum("total"), 40.0)

    def test_link_traversal_and_cardinality_are_explicit(self):
        runtime = build_runtime()
        c1_orders = runtime.object_set("Customer").where("id", "c1").traverse("customerOrders")
        self.assertEqual({o.primary_key for o in c1_orders.fetch()}, {"o1", "o2"})
        with self.assertRaisesRegex(ValueError, "cardinality"):
            runtime.load_link("customerOrders", "c2", "o1")

    def test_validate_only_does_not_mutate_and_execute_emits_observation(self):
        runtime = build_runtime()
        observed = []
        runtime.subscribe("Order", observed.append)
        before = runtime.get("Order", "o1")
        validation = runtime.apply_action(
            "cancelOrder", {"order_id": "o1", "reason": "customer request"}, "planner",
            validate_only=True, return_edits=True,
        )
        self.assertTrue(validation.validation.valid)
        self.assertFalse(validation.executed)
        self.assertEqual(runtime.get("Order", "o1"), before)
        self.assertEqual(observed, [])
        result = runtime.apply_action(
            "cancelOrder", {"order_id": "o1", "reason": "customer request"}, "planner", return_edits=True,
        )
        self.assertTrue(result.executed)
        self.assertEqual(runtime.get("Order", "o1").properties["status"], "cancelled")
        self.assertEqual(result.edits[0].changes, {"status": "cancelled"})
        self.assertEqual(observed[0].kind, "object.updated")
        self.assertEqual(observed[0].primary_key, "o1")

    def test_access_parameter_and_domain_failures_are_not_collapsed(self):
        runtime = build_runtime()
        access = runtime.validate_action("cancelOrder", {"order_id": "o1", "reason": "x"}, "viewer")
        parameter = runtime.validate_action("cancelOrder", {"order_id": "o1"}, "planner")
        domain = runtime.validate_action("cancelOrder", {"order_id": "o2", "reason": "x"}, "planner")
        self.assertEqual(access.failure_kind, FailureKind.ACCESS)
        self.assertEqual(parameter.failure_kind, FailureKind.PARAMETER)
        self.assertEqual(domain.failure_kind, FailureKind.DOMAIN)
        self.assertEqual(domain.message, "SHIPPED_ORDER_CANNOT_BE_CANCELLED")

    def test_compute_operation_is_separate_from_action(self):
        runtime = build_runtime()
        self.assertEqual(runtime.execute_function("customerTotal", {"customer_id": "c1"}), 30.0)
        self.assertEqual(runtime.get("Order", "o1").properties["status"], "pending")

    def test_async_states_remain_distinct(self):
        self.assertEqual(AsyncValue.loading().state, AsyncState.LOADING)
        self.assertEqual(AsyncValue.succeeded(3).state, AsyncState.SUCCEEDED)
        self.assertEqual(AsyncValue.reloading(3).state, AsyncState.RELOADING)
        failed = AsyncValue.failed("network")
        self.assertEqual(failed.state, AsyncState.FAILED)
        self.assertEqual(failed.error, "network")

    def test_client_boundary_and_application_bridge_are_explicit(self):
        runtime = build_runtime()
        ontology = OntologyClient(runtime, "ri.ontology.main")
        platform = PlatformClient(runtime)
        self.assertEqual(ontology.kind, "ONTOLOGY_BOUND")
        self.assertEqual(ontology.ontology_id, "ri.ontology.main")
        self.assertEqual(platform.kind, "PLATFORM")
        self.assertFalse(hasattr(platform, "ontology_id"))
        self.assertEqual(platform.execute_function("customerTotal", {"customer_id": "c2"}), 30.0)
        bridge = ApplicationBridge()
        bridge.set_value("selection", AsyncValue.loading())
        bridge.set_value("selection", AsyncValue.succeeded("o1"))
        called = []
        bridge.register_event("openOrder", lambda: called.append("o1") or "ok")
        self.assertEqual(bridge.execute_event("openOrder"), "ok")
        self.assertEqual(called, ["o1"])


if __name__ == "__main__":
    unittest.main()
