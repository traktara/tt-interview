"""Fetch and validate ONS geography, then atomically publish to Postgres."""

import argparse
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from psycopg.types.json import Jsonb
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from db import connect

API_URL = "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/LAD24_RGN24_EN_LU/FeatureServer/0/query"
FIELDS = ("LAD24CD", "LAD24NM", "RGN24CD", "RGN24NM")
LOG = logging.getLogger(__name__)


def parse_geography(payload):
    if not isinstance(payload, dict) or "error" in payload:
        raise ValueError("ONS API returned an error or invalid response")
    features = payload.get("features")
    if not isinstance(features, list) or not features:
        raise ValueError("ONS response contains no geography records")
    rows = []
    for feature in features:
        attrs = feature.get("attributes", {})
        if any(not isinstance(attrs.get(field), str) or not attrs[field].strip() for field in FIELDS):
            raise ValueError("ONS response is missing expected geography fields")
        rows.append(dict(zip(("code", "name", "region_code", "region_name"),
                             (attrs[field].strip() for field in FIELDS))))
    return rows


def validate_geography(rows):
    codes = [row["code"] for row in rows]
    if not rows or len(codes) != len(set(codes)):
        raise ValueError("Empty geography or duplicate authority codes")
    for row in rows:
        if not re.fullmatch(r"E\d{8}", row["code"]) or not re.fullmatch(r"E12\d{6}", row["region_code"]):
            raise ValueError("Invalid geography code")
    return rows


def fetch_geography(session):
    rows = []
    # A small page size deliberately exercises pagination on this 296-row lookup.
    for _ in range(100):
        response = session.get(API_URL, params={
            "where": "1=1", "outFields": ",".join(FIELDS),
            "returnGeometry": "false", "orderByFields": "LAD24CD",
            "resultOffset": len(rows), "resultRecordCount": 100, "f": "json",
        }, timeout=(5, 15))
        response.raise_for_status()
        payload = response.json()
        rows.extend(parse_geography(payload))
        if not payload.get("exceededTransferLimit", False):
            return validate_geography(rows)
    raise ValueError("ONS pagination exceeded its safety limit")


def load_geography():
    with requests.Session() as session:
        retry = Retry(total=2, backoff_factor=0.5,
                      status_forcelist=[429, 500, 502, 503, 504],
                      respect_retry_after_header=False)
        session.mount("https://", HTTPAdapter(max_retries=retry))
        return fetch_geography(session)


def publish(authorities, report):
    # One transaction keeps readers on the previous complete dataset until commit.
    with connect() as conn:
        conn.execute("SELECT pg_advisory_xact_lock(240924)")
        conn.execute(Path(__file__).with_name("schema.sql").read_text())
        conn.execute("DELETE FROM authorities")
        with conn.cursor() as cur:
            cur.executemany("INSERT INTO authorities VALUES (%(code)s, %(name)s, %(region_code)s, %(region_name)s)", authorities)
        conn.execute("INSERT INTO pipeline_status VALUES (1, %s) ON CONFLICT (id) DO UPDATE SET report = EXCLUDED.report", (Jsonb(report),))


def run():
    authorities = load_geography()
    report = {"loaded_at": datetime.now(timezone.utc).isoformat(),
              "geography_source": "live", "geography_vintage": "December 2024",
              "authority_count": len(authorities),
              "region_count": len({row["region_code"] for row in authorities})}
    publish(authorities, report)
    return report


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        print(json.dumps(run(), indent=2))
    except (ValueError, OSError, requests.RequestException) as exc:
        LOG.error("Pipeline failed: %s", exc)
        raise SystemExit(1) from exc
