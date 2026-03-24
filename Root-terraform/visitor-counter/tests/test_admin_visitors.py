import json
from lambdas.admin_visitors import lambda_handler


class FakeVisitorsTableSinglePage:
    def scan(self, **kwargs):
        return {
            "Items": [
                {
                    "visitor_id": "abc",
                    "first_visit": 1700000000,
                    "last_seen": 1700001000,
                    "last_counted_at": 1700000500,
                    "hit_count": 3,
                    "counted_visit_count": 2
                }
            ]
        }


class FakeVisitorsTableMultiPage:
    def __init__(self):
        self.calls = 0

    def scan(self, **kwargs):
        self.calls += 1

        if self.calls == 1:
            return {
                "Items": [
                    {
                        "visitor_id": "first",
                        "first_visit": 1,
                        "last_seen": 2,
                        "last_counted_at": 2,
                        "hit_count": 3,
                        "counted_visit_count": 1
                    }
                ],
                "LastEvaluatedKey": {"visitor_id": "first"}
            }

        return {
            "Items": [
                {
                    "visitor_id": "second",
                    "first_visit": 4,
                    "last_seen": 5,
                    "last_counted_at": 5,
                    "hit_count": 6,
                    "counted_visit_count": 2
                }
            ]
        }


class FakeVisitorsTableError:
    def scan(self, **kwargs):
        raise Exception("scan failed")


def test_admin_visitors_returns_visitors_list(monkeypatch):
    fake_table = FakeVisitorsTableSinglePage()
    monkeypatch.setattr("lambdas.admin_visitors.get_visitors_table", lambda: fake_table)

    response = lambda_handler({}, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert "visitors" in body
    assert isinstance(body["visitors"], list)
    assert body["visitors"][0]["visitor_id"] == "abc"
    assert body["visitors"][0]["hit_count"] == 3
    assert body["visitors"][0]["counted_visit_count"] == 2
    assert isinstance(body["visitors"][0]["first_visit"], int)


def test_admin_visitors_handles_pagination(monkeypatch):
    fake_table = FakeVisitorsTableMultiPage()
    monkeypatch.setattr("lambdas.admin_visitors.get_visitors_table", lambda: fake_table)

    response = lambda_handler({}, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert len(body["visitors"]) == 2
    assert body["visitors"][0]["visitor_id"] == "first"
    assert body["visitors"][1]["visitor_id"] == "second"


def test_admin_visitors_returns_500_on_error(monkeypatch):
    fake_table = FakeVisitorsTableError()
    monkeypatch.setattr("lambdas.admin_visitors.get_visitors_table", lambda: fake_table)

    response = lambda_handler({}, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 500
    assert "error" in body
    assert body["error"] == "scan failed"