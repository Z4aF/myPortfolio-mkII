import json
from lambdas.counter import lambda_handler


class FakeVisitorsTable:
    def __init__(self, existing_item=None):
        self.existing_item = existing_item
        self.put_called = False
        self.update_called = False
        self.last_put_item = None
        self.last_update_kwargs = None

    def get_item(self, Key):
        if self.existing_item is not None:
            return {"Item": self.existing_item}
        return {}

    def put_item(self, Item):
        self.put_called = True
        self.last_put_item = Item
        self.existing_item = Item
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}

    def update_item(self, **kwargs):
        self.update_called = True
        self.last_update_kwargs = kwargs

        expr = kwargs.get("UpdateExpression", "")

        if "counted_visit_count" in expr:
            self.existing_item["counted_visit_count"] += 1

        return {"ResponseMetadata": {"HTTPStatusCode": 200}}

    def scan(self, **kwargs):
        if self.existing_item is None:
            return {"Items": []}

        return {
            "Items": [
                {
                    "counted_visit_count":
                        self.existing_item.get("counted_visit_count", 1)
                }
            ]
        }


def test_new_visitor_increments_global_counter(monkeypatch):
    visitors_table = FakeVisitorsTable(existing_item=None)

    monkeypatch.setattr("lambdas.counter.get_visitors_table", lambda: visitors_table)
    monkeypatch.setattr("lambdas.counter.time.time", lambda: 1700000000)

    event = {
        "headers": {},
        "requestContext": {
            "identity": {
                "sourceIp": "1.2.3.4"
            }
        }
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert visitors_table.put_called is True
    assert visitors_table.update_called is False
    assert body["count"] == 1


def test_existing_visitor_within_cooldown_does_not_increment_global_counter(monkeypatch):
    now = 1700000000

    visitors_table = FakeVisitorsTable(
        existing_item={
            "visitor_id": "abc123",
            "first_visit": now - 1000,
            "last_seen": now - 100,
            "last_counted_at": now - 100,
            "hit_count": 3,
            "counted_visit_count": 1
        }
    )

    monkeypatch.setattr("lambdas.counter.get_visitors_table", lambda: visitors_table)
    monkeypatch.setattr("lambdas.counter.time.time", lambda: now)

    event = {
        "headers": {
            "x-visitor-id": "abc123"
        },
        "requestContext": {
            "identity": {
                "sourceIp": "1.2.3.4"
            }
        }
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert visitors_table.put_called is False
    assert visitors_table.update_called is True
    assert body["count"] == 1


def test_existing_visitor_after_cooldown_increments_global_counter(monkeypatch):
    now = 1700000000

    visitors_table = FakeVisitorsTable(
        existing_item={
            "visitor_id": "abc123",
            "first_visit": now - 200000,
            "last_seen": now - 90000,
            "last_counted_at": now - 90000,
            "hit_count": 3,
            "counted_visit_count": 1
        }
    )

    monkeypatch.setattr("lambdas.counter.get_visitors_table", lambda: visitors_table)
    monkeypatch.setattr("lambdas.counter.time.time", lambda: now)

    event = {
        "headers": {
            "x-visitor-id": "abc123"
        },
        "requestContext": {
            "identity": {
                "sourceIp": "1.2.3.4"
            }
        }
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert visitors_table.update_called is True
    assert body["count"] == 1


def test_hash_ip_fallback_used_when_header_missing(monkeypatch):
    visitors_table = FakeVisitorsTable(existing_item=None)

    monkeypatch.setattr("lambdas.counter.get_visitors_table", lambda: visitors_table)
    monkeypatch.setattr("lambdas.counter.time.time", lambda: 1700000000)

    event = {
        "headers": {},
        "requestContext": {
            "identity": {
                "sourceIp": "9.9.9.9"
            }
        }
    }

    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    assert visitors_table.put_called is True
    assert visitors_table.last_put_item["visitor_id"] != "9.9.9.9"