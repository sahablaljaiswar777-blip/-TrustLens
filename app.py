"""Flask application for local, offline TrustLens analysis."""

import re
from typing import Any, Dict
from urllib.parse import urlsplit, urlunsplit

from flask import Flask, abort, flash, redirect, render_template, request, url_for

from config import Config
from database.db import add_analysis, dashboard_stats, get_analysis, initialize_database, list_analyses
from engine.report_engine import analyze_submission

ALLOWED_FIELDS = {
    "message": 4000,
    "email_context": 4000,
    "sender": 320,
    "claimed_organization": 160,
    "url": 2048,
    "qr_url": 2048,
}
RISK_BANDS = ("TRUST", "LOW", "CAUTION", "SUSPICIOUS", "HIGH RISK", "CRITICAL")


def safe_preview(value: str, limit: int = 240) -> str:
    """Create a short history label while removing common secrets and URL parameters."""
    compact = " ".join(value.split())
    compact = re.sub(
        r"\b(password|passcode|one[- ]time code|otp|token|secret)\s*[:=]\s*[^\s,;]+",
        r"\1: [redacted]",
        compact,
        flags=re.IGNORECASE,
    )
    compact = re.sub(
        r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
        "[email address]",
        compact,
    )

    def remove_url_parameters(match: re.Match[str]) -> str:
        raw_url = match.group(0).rstrip(".,;)")
        suffix = match.group(0)[len(raw_url):]
        try:
            parsed = urlsplit(raw_url)
            hostname = parsed.hostname or ""
            if parsed.port:
                hostname += ":" + str(parsed.port)
            return urlunsplit((parsed.scheme, hostname, parsed.path, "", "")) + suffix
        except ValueError:
            return raw_url + suffix

    compact = re.sub(r"https?://[^\s<>]+", remove_url_parameters, compact, flags=re.IGNORECASE)
    return compact[:limit]

SIMULATIONS = {
    "delivery": {
        "title": "Package delivery notice",
        "sender": "notices@parcel-update.test",
        "claimed_organization": "Example Parcel",
        "message": "Urgent: your package is held. Click this link immediately to pay the delivery fee.",
        "url": "https://example-parcel.test/track",
        "email_context": "This fictional message uses urgency and a payment request.",
    },
    "workplace": {
        "title": "Fictional executive request",
        "sender": "director@company-help.test",
        "claimed_organization": "Example Company",
        "message": "This is an emergency. Keep this confidential and bypass the usual approval process. Send a gift card now.",
        "url": "",
        "email_context": "Training-only scenario; no action should be taken.",
    },
    "account": {
        "title": "Fictional account warning",
        "sender": "support@secure-example.test",
        "claimed_organization": "Example Bank",
        "message": "Your account will be suspended. Verify your password and one-time code immediately.",
        "url": "http://bank.example.test.account-check.test/login",
        "email_context": "All domains in this scenario are reserved example/test names.",
    },
}


def create_app(test_config: Dict[str, Any] | None = None) -> Flask:
    """Create the app and initialize its database."""
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    initialize_database(app.config["DATABASE_PATH"])

    @app.context_processor
    def inject_globals() -> Dict[str, Any]:
        return {"risk_bands": ["TRUST", "LOW", "CAUTION", "SUSPICIOUS", "HIGH RISK", "CRITICAL"]}

    @app.get("/")
    def index():
        return render_template("index.html", stats=dashboard_stats(app.config["DATABASE_PATH"]))

    @app.route("/analyze", methods=["GET", "POST"])
    def analyze():
        if request.method == "GET":
            return render_template("analyze.html", values={})
        values: Dict[str, str] = {}
        for field, limit in ALLOWED_FIELDS.items():
            value = request.form.get(field, "").strip()
            if len(value) > limit:
                flash(f"{field.replace('_', ' ').title()} exceeds the {limit}-character limit.", "error")
                return render_template("analyze.html", values=request.form), 400
            values[field] = value
        if not any(values.values()):
            flash("Enter a message, URL, email context, sender, or QR destination to analyze.", "error")
            return render_template("analyze.html", values=values), 400

        result = analyze_submission(**values)
        title_source = values["message"] or values["email_context"] or values["url"] or values["qr_url"] or values["sender"]
        title = safe_preview(title_source, 72) or "Offline analysis"
        preview = safe_preview(values["message"] or values["email_context"] or values["url"] or values["qr_url"])
        analysis_id = add_analysis(app.config["DATABASE_PATH"], title, preview or "Sender-only analysis", result)
        return redirect(url_for("result", analysis_id=analysis_id))

    @app.get("/result/<int:analysis_id>")
    def result(analysis_id: int):
        analysis = get_analysis(app.config["DATABASE_PATH"], analysis_id)
        if analysis is None:
            abort(404)
        return render_template("result.html", analysis=analysis, report_mode=False)

    @app.get("/history")
    def history():
        query = request.args.get("q", "")[:80]
        band = request.args.get("band", "")
        if band and band not in RISK_BANDS:
            band = ""
        analyses = list_analyses(app.config["DATABASE_PATH"], query, band)
        return render_template("history.html", analyses=analyses, query=query, selected_band=band)

    @app.get("/reports")
    def reports():
        analyses = list_analyses(app.config["DATABASE_PATH"])
        return render_template("reports.html", analyses=analyses)

    @app.get("/reports/<int:analysis_id>")
    def report(analysis_id: int):
        analysis = get_analysis(app.config["DATABASE_PATH"], analysis_id)
        if analysis is None:
            abort(404)
        return render_template("result.html", analysis=analysis, report_mode=True)

    @app.route("/simulation", methods=["GET", "POST"])
    def simulation():
        if request.method == "POST":
            scenario_key = request.form.get("scenario", "")
            scenario = SIMULATIONS.get(scenario_key)
            if scenario is None:
                abort(400)
            result = analyze_submission(
                message=scenario["message"],
                url=scenario["url"],
                email_context=scenario["email_context"],
                sender=scenario["sender"],
                claimed_organization=scenario["claimed_organization"],
            )
            preview = (scenario["message"] + " " + scenario["url"]).strip()[:240]
            analysis_id = add_analysis(
                app.config["DATABASE_PATH"], "Simulation: " + scenario["title"], preview, result
            )
            return redirect(url_for("result", analysis_id=analysis_id))
        return render_template("simulation.html", simulations=SIMULATIONS)

    @app.get("/about")
    def about():
        return render_template("about.html")

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("error.html", code=404, message="That page or analysis could not be found."), 404

    @app.errorhandler(400)
    def bad_request(_error):
        return render_template("error.html", code=400, message="The request could not be processed."), 400

    @app.errorhandler(413)
    def too_large(_error):
        return render_template("error.html", code=413, message="The request is larger than the allowed limit."), 413

    @app.errorhandler(500)
    def server_error(_error):
        app.logger.exception("Unhandled application error")
        return render_template("error.html", code=500, message="An unexpected error occurred. No diagnostic details are shown."), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
