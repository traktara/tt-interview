import unittest
from unittest.mock import MagicMock, patch

import requests

import app
import pipeline


BRISTOL = {"code": "E06000023", "name": "Bristol, City of",
           "region_code": "E12000009", "region_name": "South West"}
READING = {"code": "E06000038", "name": "Reading",
           "region_code": "E12000008", "region_name": "South East"}


def page(rows, more=False):
    return {"features": [{"attributes": dict(zip(pipeline.FIELDS, (
        row["code"], row["name"], row["region_code"], row["region_name"])))
        } for row in rows], "exceededTransferLimit": more}


class ImportTests(unittest.TestCase):
    def test_fetches_all_pages_before_publishing_ons_counts(self):
        session = MagicMock()
        session.get.side_effect = [MagicMock(json=lambda: page([BRISTOL], True)),
                                   MagicMock(json=lambda: page([READING]))]
        with patch.object(pipeline.requests, "Session") as factory, \
                patch.object(pipeline, "publish") as publish:
            factory.return_value.__enter__.return_value = session
            report = pipeline.run()
        self.assertEqual(report["authority_count"], 2)
        self.assertEqual(report["region_count"], 2)
        self.assertEqual(report["geography_source"], "live")
        publish.assert_called_once_with([BRISTOL, READING], report)
        self.assertEqual([call.kwargs["params"]["resultOffset"]
                          for call in session.get.call_args_list], [0, 1])

    def test_failed_fetch_does_not_publish(self):
        with patch.object(pipeline, "load_geography", side_effect=requests.Timeout), \
                patch.object(pipeline, "publish") as publish:
            with self.assertRaises(requests.Timeout):
                pipeline.run()
        publish.assert_not_called()

    def test_empty_error_and_malformed_responses_are_rejected(self):
        for payload in (page([]), {"error": {"message": "Unavailable"}},
                        {"features": [{"attributes": {"LAD24CD": "E06000023"}}]}):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                pipeline.parse_geography(payload)

    def test_duplicate_codes_across_pages_are_rejected(self):
        session = MagicMock()
        session.get.side_effect = [MagicMock(json=lambda: page([BRISTOL], True)),
                                   MagicMock(json=lambda: page([BRISTOL]))]
        with self.assertRaises(ValueError):
            pipeline.fetch_geography(session)


class DashboardTests(unittest.TestCase):
    def dashboard(self, rows, query=""):
        regions = [{"code": "E12000009", "name": "South West"},
                   {"code": "E12000008", "name": "South East"}]
        report = {"authority_count": 2, "region_count": 2}
        conn = MagicMock()
        conn.execute.side_effect = [MagicMock(), MagicMock(fetchall=lambda: rows),
                                   MagicMock(fetchall=lambda: regions),
                                   MagicMock(fetchone=lambda: {"report": report})]
        with patch.object(app, "connect") as connect:
            connect.return_value.__enter__.return_value = conn
            response = app.create_app().test_client().get('/api/dashboard' + query)
        self.assertEqual(response.status_code, 200)
        return response.get_json(), conn

    def test_returns_authorities_and_filtered_counts(self):
        body, conn = self.dashboard([BRISTOL], '?region=E12000009&q=Bristol')
        self.assertEqual(body["authorities"], [BRISTOL])
        self.assertEqual(body["summary"], {"authority_count": 1, "region_count": 1})
        self.assertEqual(len(body["regions"]), 2)
        self.assertEqual(body["pipeline"]["authority_count"], 2)
        self.assertNotIn("projects", body)
        sql, params = conn.execute.call_args_list[1].args
        self.assertNotIn("JOIN projects", sql)
        self.assertEqual(params, ('E12000009', 'E12000009', 'Bristol', 'Bristol'))

    def test_no_matches_returns_zero_counts_and_keeps_region_options(self):
        body, _ = self.dashboard([], '?q=unmatched')
        self.assertEqual(body["authorities"], [])
        self.assertEqual(body["summary"], {"authority_count": 0, "region_count": 0})
        self.assertEqual(len(body["regions"]), 2)


if __name__ == "__main__":
    unittest.main()
