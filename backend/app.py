import psycopg
from flask import Flask, jsonify, request

from db import connect


def create_app():
    app = Flask(__name__)

    @app.errorhandler(psycopg.Error)
    def database_error(error):
        app.logger.exception("Database request failed")
        return jsonify(error="Database unavailable. Check the pipeline and database logs."), 503

    @app.get("/api/health")
    def health():
        with connect() as conn:
            ready = conn.execute("SELECT id FROM pipeline_status WHERE id = 1").fetchone()
        return jsonify(status="ok" if ready else "not_ready"), 200 if ready else 503

    @app.get("/api/dashboard")
    def dashboard():
        region = request.args.get("region", "").strip()
        search = request.args.get("q", "").strip()
        with connect() as conn:
            # Keep report and rows consistent even if the pipeline commits mid-request.
            conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            authorities = conn.execute("""
                SELECT a.code, a.name, a.region_code, a.region_name
                FROM authorities a
                WHERE (%s = '' OR a.region_code = %s)
                  AND (%s = '' OR strpos(lower(a.name || ' ' || a.code), lower(%s)) > 0)
                ORDER BY a.region_name, a.name
            """, (region, region, search, search)).fetchall()
            regions = conn.execute("SELECT DISTINCT region_code AS code, region_name AS name FROM authorities ORDER BY region_name").fetchall()
            status = conn.execute("SELECT report FROM pipeline_status WHERE id = 1").fetchone()
        return jsonify(authorities=authorities, regions=regions,
                       summary={"authority_count": len(authorities),
                                "region_count": len({a["region_code"] for a in authorities})},
                       pipeline=status["report"] if status else None)

    return app
