from __future__ import annotations

import http.client
import json
import threading
import unittest

from compat.server import CompatApp, make_server
from runtime.scenarios import build_demo_runtime


ONTOLOGY = "ri.ontology.main"


def base(type_name: str) -> dict:
    return {"type": "base", "objectType": type_name}


def eq(object_set: dict, field: str, value) -> dict:
    return {"type": "filter", "objectSet": object_set, "where": {"type": "eq", "field": field, "value": value}}


class DispatcherTests(unittest.TestCase):
    def setUp(self):
        self.app = CompatApp(build_demo_runtime(), ONTOLOGY)

    def test_object_type_list_and_get(self):
        response = self.app.dispatch("GET", f"/v2/ontologies/{ONTOLOGY}/objectTypes/Order")
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body["apiName"], "Order")
        self.assertEqual(response.body["primaryKey"], "id")

        response = self.app.dispatch("GET", f"/v2/ontologies/{ONTOLOGY}/objects/Order?select=id,status,total")
        self.assertEqual(response.status, 200)
        self.assertEqual([row["__primaryKey"] for row in response.body["data"]], ["o1", "o2", "o3"])
        self.assertEqual(response.body["data"][0]["__apiName"], "Order")

        response = self.app.dispatch("GET", f"/v2/ontologies/{ONTOLOGY}/objects/Order/o2?select=id,status")
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body["status"], "shipped")
        self.assertNotIn("total", response.body)

    def test_link_route(self):
        response = self.app.dispatch("GET", f"/v2/ontologies/{ONTOLOGY}/objects/Customer/c1/links/customerOrders?select=id,total")
        self.assertEqual(response.status, 200)
        self.assertEqual([row["__primaryKey"] for row in response.body["data"]], ["o1", "o2"])

    def test_all_supported_objectset_variants_use_existing_runtime(self):
        pending = eq(base("Order"), "status", "pending")
        shipped = eq(base("Order"), "status", "shipped")
        union = {"type": "union", "objectSets": [pending, shipped]}
        intersect = {"type": "intersect", "objectSets": [union, pending]}
        subtract = {"type": "subtract", "objectSets": [union, shipped]}
        around = {"type": "searchAround", "objectSet": eq(base("Customer"), "id", "c1"), "link": "customerOrders"}
        cases = [
            (base("Order"), ["o1", "o2", "o3"]),
            (pending, ["o1", "o3"]),
            (union, ["o1", "o2", "o3"]),
            (intersect, ["o1", "o3"]),
            (subtract, ["o1", "o3"]),
            (around, ["o1", "o2"]),
        ]
        for wire, expected in cases:
            with self.subTest(kind=wire["type"]):
                response = self.app.dispatch(
                    "POST",
                    f"/v2/ontologies/{ONTOLOGY}/objectSets/loadObjects",
                    {"objectSet": wire, "select": ["id"]},
                )
                self.assertEqual(response.status, 200)
                self.assertEqual([row["__primaryKey"] for row in response.body["data"]], expected)

    def test_page_size_never_silently_truncates_without_next_token(self):
        response = self.app.dispatch("GET", f"/v2/ontologies/{ONTOLOGY}/objects/Order?pageSize=1")
        self.assertEqual(response.status, 400)
        self.assertEqual(response.body["errorCode"], "UNSUPPORTED_PAGING")
        response = self.app.dispatch(
            "POST",
            f"/v2/ontologies/{ONTOLOGY}/objectSets/loadObjects",
            {"objectSet": base("Order"), "select": ["id"], "pageSize": 1},
        )
        self.assertEqual(response.status, 400)
        self.assertEqual(response.body["errorCode"], "UNSUPPORTED_PAGING")

    def test_load_rejects_paging_and_unsupported_query(self):
        response = self.app.dispatch(
            "POST",
            f"/v2/ontologies/{ONTOLOGY}/objectSets/loadObjects",
            {"objectSet": base("Order"), "select": ["id"], "pageToken": "next"},
        )
        self.assertEqual(response.status, 400)
        self.assertEqual(response.body["errorCode"], "UNSUPPORTED_PAGING")

        response = self.app.dispatch(
            "POST",
            f"/v2/ontologies/{ONTOLOGY}/objectSets/loadObjects",
            {"objectSet": {"type": "filter", "objectSet": base("Order"), "where": {"type": "gt", "field": "total", "value": 10}}, "select": ["id"]},
        )
        self.assertEqual(response.status, 400)
        self.assertEqual(response.body["errorCode"], "UNSUPPORTED_WIRE_VARIANT")

    def test_aggregate_count_and_sum(self):
        pending = eq(base("Order"), "status", "pending")
        count = self.app.dispatch(
            "POST",
            f"/v2/ontologies/{ONTOLOGY}/objectSets/aggregate",
            {"objectSet": pending, "aggregation": [{"type": "count", "name": "n"}], "groupBy": []},
        )
        self.assertEqual(count.body, {"accuracy": "ACCURATE", "data": [{"group": {}, "metrics": [{"name": "n", "value": 2}]}]})
        total = self.app.dispatch(
            "POST",
            f"/v2/ontologies/{ONTOLOGY}/objectSets/aggregate",
            {"objectSet": pending, "aggregation": [{"type": "sum", "name": "total", "field": "total"}], "groupBy": []},
        )
        self.assertEqual(total.body, {"accuracy": "ACCURATE", "data": [{"group": {}, "metrics": [{"name": "total", "value": 40.0}]}]})

    def test_action_validate_only_invalid_execute_and_edits(self):
        path = f"/v2/ontologies/{ONTOLOGY}/actions/cancelOrder/apply"
        headers = {"X-Ratinlap-Actor": "planner"}
        before = self.app.runtime.get("Order", "o1")
        validated = self.app.dispatch(
            "POST", path,
            {"parameters": {"order_id": "o1", "reason": "x"}, "options": {"mode": "VALIDATE_ONLY"}},
            headers,
        )
        self.assertEqual(validated.status, 200)
        self.assertEqual(validated.body["validation"]["result"], "VALID")
        self.assertEqual(self.app.runtime.get("Order", "o1"), before)

        invalid = self.app.dispatch(
            "POST", path,
            {"parameters": {"order_id": "o2", "reason": "x"}, "options": {"mode": "VALIDATE_AND_EXECUTE"}},
            headers,
        )
        self.assertEqual(invalid.status, 200)
        self.assertEqual(invalid.body["validation"]["result"], "INVALID")
        self.assertEqual(self.app.runtime.get("Order", "o2").properties["status"], "shipped")

        executed = self.app.dispatch(
            "POST", path,
            {"parameters": {"order_id": "o1", "reason": "x"}, "options": {"mode": "VALIDATE_AND_EXECUTE", "returnEdits": "ALL_V2_WITH_DELETIONS"}},
            headers,
        )
        self.assertEqual(executed.status, 200)
        self.assertEqual(executed.body["validation"]["result"], "VALID")
        self.assertEqual(executed.body["edits"]["type"], "edits")
        self.assertEqual(executed.body["edits"]["edits"][0]["type"], "modifyObject")
        self.assertEqual(self.app.runtime.get("Order", "o1").properties["status"], "cancelled")

    def test_access_and_transport_errors_remain_distinct(self):
        path = f"/v2/ontologies/{ONTOLOGY}/actions/cancelOrder/apply"
        forbidden = self.app.dispatch(
            "POST", path,
            {"parameters": {"order_id": "o1", "reason": "x"}},
            {"X-Ratinlap-Actor": "viewer"},
        )
        self.assertEqual(forbidden.status, 403)
        self.assertEqual(forbidden.body["errorCode"], "FORBIDDEN")

        not_found = self.app.dispatch("GET", "/v2/nothing")
        self.assertEqual(not_found.status, 404)
        self.assertEqual(not_found.body["errorCode"], "ROUTE_NOT_FOUND")

        wrong_method = self.app.dispatch("POST", f"/v2/ontologies/{ONTOLOGY}/objects/Order")
        self.assertEqual(wrong_method.status, 405)


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server(app=CompatApp(build_demo_runtime(), ONTOLOGY))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.host, cls.port = cls.server.server_address

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, method: str, path: str, body=None, headers=None):
        conn = http.client.HTTPConnection(self.host, self.port, timeout=3)
        payload = None if body is None else json.dumps(body)
        hdrs = dict(headers or {})
        if payload is not None:
            hdrs["Content-Type"] = "application/json"
        conn.request(method, path, body=payload, headers=hdrs)
        response = conn.getresponse()
        data = json.loads(response.read().decode())
        conn.close()
        return response.status, data

    def test_all_seven_routes_over_http(self):
        planner = {"X-Ratinlap-Actor": "planner"}
        checks = [
            ("GET", f"/v2/ontologies/{ONTOLOGY}/objectTypes/Order", None, None, 200),
            ("GET", f"/v2/ontologies/{ONTOLOGY}/objects/Order?select=id,status", None, None, 200),
            ("GET", f"/v2/ontologies/{ONTOLOGY}/objects/Order/o1?select=id,status", None, None, 200),
            ("GET", f"/v2/ontologies/{ONTOLOGY}/objects/Customer/c1/links/customerOrders?select=id", None, None, 200),
            ("POST", f"/v2/ontologies/{ONTOLOGY}/objectSets/loadObjects", {"objectSet": base("Order"), "select": ["id"]}, None, 200),
            ("POST", f"/v2/ontologies/{ONTOLOGY}/objectSets/aggregate", {"objectSet": base("Order"), "aggregation": [{"type": "count", "name": "n"}], "groupBy": []}, None, 200),
            ("POST", f"/v2/ontologies/{ONTOLOGY}/actions/cancelOrder/apply", {"parameters": {"order_id": "o1", "reason": "http"}, "options": {"mode": "VALIDATE_ONLY"}}, planner, 200),
        ]
        for method, path, body, headers, expected in checks:
            with self.subTest(path=path):
                status, _ = self.request(method, path, body, headers)
                self.assertEqual(status, expected)

    def test_invalid_json_is_transport_error(self):
        conn = http.client.HTTPConnection(self.host, self.port, timeout=3)
        conn.request("POST", f"/v2/ontologies/{ONTOLOGY}/objectSets/loadObjects", body="{bad", headers={"Content-Type": "application/json"})
        response = conn.getresponse()
        body = json.loads(response.read().decode())
        conn.close()
        self.assertEqual(response.status, 400)
        self.assertEqual(body["errorCode"], "INVALID_JSON")


if __name__ == "__main__":
    unittest.main()
