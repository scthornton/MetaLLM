"""
MetaLLM Reporting Engine.

Generates professional security assessment reports from module execution
results. Supports JSON, Markdown, and self-contained HTML output.
"""

from __future__ import annotations

import json
import uuid
import html as html_lib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

from metallm.base.result import Result, ResultStatus

logger = structlog.get_logger()

# ======================================================================
# MITRE ATLAS Technique Mapping
# ======================================================================

ATLAS_TECHNIQUES: Dict[str, str] = {
    "AML.T0000": "ML Model Access",
    "AML.T0001": "ML Attack Staging",
    "AML.T0002": "Active Scanning",
    "AML.T0003": "Acquire Public ML Artifacts",
    "AML.T0004": "Obtain Capabilities",
    "AML.T0005": "Create Proxy ML Model",
    "AML.T0006": "Develop Adversarial ML Attack",
    "AML.T0007": "Discover ML Artifacts",
    "AML.T0008": "Initial Access via ML Supply Chain",
    "AML.T0009": "Exploit Public-Facing ML Application",
    "AML.T0010": "ML Supply Chain Compromise",
    "AML.T0011": "Compromise ML Artifacts",
    "AML.T0012": "Valid Accounts",
    "AML.T0013": "Discover ML Artifacts in Repositories",
    "AML.T0014": "Verify ML Artifacts",
    "AML.T0015": "Evade ML Model",
    "AML.T0016": "Obtain Adversarial Input",
    "AML.T0017": "Develop Adversarial Examples",
    "AML.T0018": "Backdoor ML Model",
    "AML.T0019": "Publish Poisoned ML Model",
    "AML.T0020": "Poison Training Data",
    "AML.T0021": "Establish Persistence via ML Model",
    "AML.T0022": "Discover ML Environment",
    "AML.T0023": "Extract ML Model",
    "AML.T0024": "Exfiltration via ML API",
    "AML.T0025": "Exfiltration via ML Inference API",
    "AML.T0026": "Craft Adversarial Data for ML-based System",
    "AML.T0029": "Denial of ML Service",
    "AML.T0031": "Erode ML Model Integrity",
    "AML.T0034": "Cost Harvesting",
    "AML.T0035": "ML Artifact Collection",
    "AML.T0036": "Data from ML Artifact",
    "AML.T0040": "ML Model Inference API Access",
    "AML.T0042": "Verify Attack",
    "AML.T0043": "Craft Adversarial Data",
    "AML.T0044": "Full ML Model Access",
    "AML.T0045": "Acquire Infrastructure",
    "AML.T0046": "Spearphishing via AI Generated Content",
    "AML.T0047": "ML-Enabled Product or Service",
    "AML.T0048": "Discover Model Ontology",
    "AML.T0049": "Exploit Vector DB",
    "AML.T0050": "Command Injection via Prompt",
    "AML.T0051": "LLM Jailbreak",
    "AML.T0052": "Phishing via AI Generated Content",
    "AML.T0053": "Data Poisoning via RAG",
    "AML.T0054": "LLM Prompt Injection",
    "AML.T0055": "Unsafe LLM Output Handling",
    "AML.T0056": "LLM Plugin Compromise",
    "AML.T0057": "LLM Data Leakage",
}

# ======================================================================
# OWASP LLM Top 10 (2025)
# ======================================================================

OWASP_LLM_2025: Dict[str, str] = {
    "LLM01": "Prompt Injection",
    "LLM02": "Sensitive Information Disclosure",
    "LLM03": "Supply Chain Vulnerabilities",
    "LLM04": "Data and Model Poisoning",
    "LLM05": "Improper Output Handling",
    "LLM06": "Excessive Agency",
    "LLM07": "System Prompt Leakage",
    "LLM08": "Vector and Embedding Weaknesses",
    "LLM09": "Misinformation",
    "LLM10": "Unbounded Consumption",
}

# Severity ordering for sorting and comparison
_SEVERITY_ORDER: Dict[str, int] = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "info": 4,
}

_SEVERITY_COLORS: Dict[str, str] = {
    "critical": "#ff1744",
    "high": "#ff5722",
    "medium": "#ff9800",
    "low": "#2196f3",
    "info": "#78909c",
}


# ======================================================================
# Finding dataclass
# ======================================================================

@dataclass
class Finding:
    """A single vulnerability finding from a module execution."""

    id: str
    module_path: str
    module_name: str
    timestamp: datetime
    severity: str
    status: ResultStatus
    target_url: str
    owasp_category: str
    mitre_atlas: List[str]
    description: str
    evidence: List[str]
    remediation: str
    raw_result: Dict[str, Any]

    def severity_rank(self) -> int:
        """Return numeric severity for sorting (lower = more severe)."""
        return _SEVERITY_ORDER.get(self.severity.lower(), 99)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a JSON-friendly dictionary."""
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        d["status"] = self.status.value
        return d


# ======================================================================
# Reporting Engine
# ======================================================================

class ReportingEngine:
    """
    Collects findings from module executions and generates professional
    security assessment reports in JSON, Markdown, and HTML formats.
    """

    def __init__(
        self,
        assessment_name: str = "MetaLLM Security Assessment",
        assessor: str = "",
        organization: str = "",
    ) -> None:
        self.assessment_name = assessment_name
        self.assessor = assessor
        self.organization = organization
        self.started_at: datetime = datetime.now(timezone.utc)
        self._findings: List[Finding] = []
        logger.info(
            "reporting.init",
            assessment=assessment_name,
            assessor=assessor,
        )

    # ------------------------------------------------------------------
    # Finding management
    # ------------------------------------------------------------------

    def add_finding(
        self,
        result: Result,
        module_path: str,
        module_name: str,
        target_url: str,
    ) -> Finding:
        """
        Record a finding from a module execution result.

        Returns the created Finding instance.
        """
        finding = Finding(
            id=f"MLLM-{uuid.uuid4().hex[:8].upper()}",
            module_path=module_path,
            module_name=module_name,
            timestamp=datetime.now(timezone.utc),
            severity=result.severity.lower(),
            status=result.status,
            target_url=target_url,
            owasp_category=result.owasp_category,
            mitre_atlas=list(result.mitre_atlas),
            description=result.message,
            evidence=list(result.evidence),
            remediation=result.remediation,
            raw_result={
                "status": result.status.value,
                "message": result.message,
                "data": result.data,
                "loot": result.loot,
            },
        )
        self._findings.append(finding)
        logger.info(
            "reporting.finding_added",
            finding_id=finding.id,
            severity=finding.severity,
            module=module_name,
            owasp=finding.owasp_category,
        )
        return finding

    def get_findings(
        self,
        severity: Optional[str] = None,
    ) -> List[Finding]:
        """
        Return findings, optionally filtered by severity.

        Results are sorted by severity (critical first), then timestamp.
        """
        findings = self._findings
        if severity is not None:
            sev = severity.lower()
            findings = [f for f in findings if f.severity == sev]
        return sorted(findings, key=lambda f: (f.severity_rank(), f.timestamp))

    # ------------------------------------------------------------------
    # Summary statistics
    # ------------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """
        Return a summary of the current assessment state.

        Includes counts by severity, OWASP coverage, ATLAS techniques hit,
        status breakdown, and overall risk rating.
        """
        severity_counts: Dict[str, int] = {s: 0 for s in _SEVERITY_ORDER}
        status_counts: Dict[str, int] = {}
        owasp_hit: Dict[str, List[str]] = {}
        atlas_hit: Dict[str, List[str]] = {}

        for f in self._findings:
            # Severity
            severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1

            # Status
            sv = f.status.value
            status_counts[sv] = status_counts.get(sv, 0) + 1

            # OWASP
            if f.owasp_category:
                owasp_hit.setdefault(f.owasp_category, []).append(f.id)

            # ATLAS
            for tech in f.mitre_atlas:
                atlas_hit.setdefault(tech, []).append(f.id)

        # Overall risk rating
        if severity_counts.get("critical", 0) > 0:
            overall_risk = "CRITICAL"
        elif severity_counts.get("high", 0) > 0:
            overall_risk = "HIGH"
        elif severity_counts.get("medium", 0) > 0:
            overall_risk = "MEDIUM"
        elif severity_counts.get("low", 0) > 0:
            overall_risk = "LOW"
        elif self._findings:
            overall_risk = "INFORMATIONAL"
        else:
            overall_risk = "NONE"

        owasp_coverage: Dict[str, Any] = {}
        for cat_id, cat_name in OWASP_LLM_2025.items():
            finding_ids = owasp_hit.get(cat_id, [])
            owasp_coverage[cat_id] = {
                "name": cat_name,
                "tested": len(finding_ids) > 0,
                "finding_count": len(finding_ids),
                "finding_ids": finding_ids,
            }

        return {
            "assessment_name": self.assessment_name,
            "assessor": self.assessor,
            "organization": self.organization,
            "started_at": self.started_at.isoformat(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_findings": len(self._findings),
            "overall_risk": overall_risk,
            "severity_counts": severity_counts,
            "status_counts": status_counts,
            "owasp_coverage": owasp_coverage,
            "atlas_techniques": {
                tid: {
                    "name": ATLAS_TECHNIQUES.get(tid, "Unknown"),
                    "finding_ids": fids,
                }
                for tid, fids in atlas_hit.items()
            },
        }

    # ------------------------------------------------------------------
    # JSON export
    # ------------------------------------------------------------------

    def generate_json(self, filepath: str | Path) -> Path:
        """Export the full assessment as a JSON file."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        report = {
            "meta": self.summary(),
            "findings": [f.to_dict() for f in self.get_findings()],
        }

        filepath.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        logger.info("reporting.json_exported", path=str(filepath))
        return filepath

    # ------------------------------------------------------------------
    # Markdown export
    # ------------------------------------------------------------------

    def generate_markdown(self, filepath: str | Path) -> Path:
        """Export the assessment as a Markdown report suitable for pentesting deliverables."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        s = self.summary()
        findings = self.get_findings()
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        lines: List[str] = []
        _a = lines.append

        # Title
        _a(f"# {self.assessment_name}")
        _a("")
        _a(f"**Generated:** {now}  ")
        if self.assessor:
            _a(f"**Assessor:** {self.assessor}  ")
        if self.organization:
            _a(f"**Organization:** {self.organization}  ")
        _a(f"**Overall Risk Rating:** {s['overall_risk']}")
        _a("")

        # Executive summary
        _a("## Executive Summary")
        _a("")
        _a(f"This assessment identified **{s['total_findings']}** finding(s) "
           f"across the target environment.")
        _a("")
        _a("| Severity | Count |")
        _a("|----------|-------|")
        for sev in _SEVERITY_ORDER:
            count = s["severity_counts"].get(sev, 0)
            _a(f"| {sev.capitalize()} | {count} |")
        _a("")

        # OWASP coverage
        _a("## OWASP LLM Top 10 (2025) Coverage")
        _a("")
        _a("| ID | Category | Tested | Findings |")
        _a("|----|----------|--------|----------|")
        for cat_id in sorted(OWASP_LLM_2025.keys()):
            cov = s["owasp_coverage"][cat_id]
            tested = "Yes" if cov["tested"] else "No"
            _a(f"| {cat_id} | {cov['name']} | {tested} | {cov['finding_count']} |")
        _a("")

        # MITRE ATLAS techniques
        if s["atlas_techniques"]:
            _a("## MITRE ATLAS Techniques Observed")
            _a("")
            _a("| Technique | Name | Findings |")
            _a("|-----------|------|----------|")
            for tid, info in sorted(s["atlas_techniques"].items()):
                _a(f"| {tid} | {info['name']} | {len(info['finding_ids'])} |")
            _a("")

        # Detailed findings
        _a("## Detailed Findings")
        _a("")

        for i, f in enumerate(findings, 1):
            _a(f"### {i}. [{f.severity.upper()}] {f.module_name}")
            _a("")
            _a(f"**Finding ID:** `{f.id}`  ")
            _a(f"**Module:** `{f.module_path}`  ")
            _a(f"**Target:** `{f.target_url}`  ")
            _a(f"**Timestamp:** {f.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}  ")
            _a(f"**Status:** {f.status.value}  ")
            if f.owasp_category:
                owasp_name = OWASP_LLM_2025.get(f.owasp_category, "")
                _a(f"**OWASP:** {f.owasp_category} — {owasp_name}  ")
            if f.mitre_atlas:
                atlas_str = ", ".join(
                    f"{t} ({ATLAS_TECHNIQUES.get(t, 'Unknown')})"
                    for t in f.mitre_atlas
                )
                _a(f"**MITRE ATLAS:** {atlas_str}  ")
            _a("")

            _a("#### Description")
            _a("")
            _a(f"{f.description}")
            _a("")

            if f.evidence:
                _a("#### Evidence")
                _a("")
                for ev in f.evidence:
                    _a(f"- `{ev}`")
                _a("")

            if f.remediation:
                _a("#### Remediation")
                _a("")
                _a(f"{f.remediation}")
                _a("")

            _a("---")
            _a("")

        # Footer
        _a("*Report generated by MetaLLM — AI Security Assessment Framework*")

        filepath.write_text("\n".join(lines), encoding="utf-8")
        logger.info("reporting.markdown_exported", path=str(filepath))
        return filepath

    # ------------------------------------------------------------------
    # HTML export
    # ------------------------------------------------------------------

    def generate_html(self, filepath: str | Path) -> Path:
        """Export the assessment as a self-contained HTML report with inline CSS."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        s = self.summary()
        findings = self.get_findings()
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        esc = html_lib.escape

        # Build severity bar chart
        max_count = max((s["severity_counts"].get(sv, 0) for sv in _SEVERITY_ORDER), default=1)
        max_count = max(max_count, 1)  # avoid division by zero

        bar_rows = ""
        for sev in _SEVERITY_ORDER:
            count = s["severity_counts"].get(sev, 0)
            pct = int((count / max_count) * 100)
            color = _SEVERITY_COLORS.get(sev, "#999")
            bar_rows += (
                f'<div class="bar-row">'
                f'<span class="bar-label">{sev.capitalize()}</span>'
                f'<div class="bar-track">'
                f'<div class="bar-fill" style="width:{pct}%;background:{color};"></div>'
                f'</div>'
                f'<span class="bar-count">{count}</span>'
                f'</div>\n'
            )

        # Build OWASP coverage matrix
        owasp_rows = ""
        for cat_id in sorted(OWASP_LLM_2025.keys()):
            cov = s["owasp_coverage"][cat_id]
            tested_cls = "tested" if cov["tested"] else "not-tested"
            tested_txt = "YES" if cov["tested"] else "NO"
            owasp_rows += (
                f'<tr>'
                f'<td class="cat-id">{esc(cat_id)}</td>'
                f'<td>{esc(cov["name"])}</td>'
                f'<td class="{tested_cls}">{tested_txt}</td>'
                f'<td class="count">{cov["finding_count"]}</td>'
                f'</tr>\n'
            )

        # Build ATLAS table
        atlas_rows = ""
        for tid, info in sorted(s.get("atlas_techniques", {}).items()):
            atlas_rows += (
                f'<tr>'
                f'<td><code>{esc(tid)}</code></td>'
                f'<td>{esc(info["name"])}</td>'
                f'<td class="count">{len(info["finding_ids"])}</td>'
                f'</tr>\n'
            )

        # Build finding cards
        finding_cards = ""
        for i, f in enumerate(findings, 1):
            sev_cls = f.severity.lower()
            sev_color = _SEVERITY_COLORS.get(f.severity.lower(), "#999")

            evidence_html = ""
            if f.evidence:
                evidence_items = "".join(
                    f"<li><code>{esc(ev)}</code></li>" for ev in f.evidence
                )
                evidence_html = (
                    f'<div class="section"><h4>Evidence</h4>'
                    f'<ul class="evidence-list">{evidence_items}</ul></div>'
                )

            remediation_html = ""
            if f.remediation:
                remediation_html = (
                    f'<div class="section remediation"><h4>Remediation</h4>'
                    f'<p>{esc(f.remediation)}</p></div>'
                )

            owasp_label = ""
            if f.owasp_category:
                owasp_name = OWASP_LLM_2025.get(f.owasp_category, "")
                owasp_label = (
                    f'<span class="tag owasp">{esc(f.owasp_category)}'
                    f' &mdash; {esc(owasp_name)}</span>'
                )

            atlas_tags = ""
            if f.mitre_atlas:
                atlas_tags = " ".join(
                    f'<span class="tag atlas">{esc(t)}</span>'
                    for t in f.mitre_atlas
                )

            finding_cards += f"""
<div class="finding-card">
  <div class="finding-header" style="border-left:4px solid {sev_color};">
    <div class="finding-title">
      <span class="finding-num">#{i}</span>
      <span class="severity-badge {sev_cls}">{esc(f.severity.upper())}</span>
      <span class="finding-name">{esc(f.module_name)}</span>
    </div>
    <div class="finding-meta">
      <code>{esc(f.id)}</code> &middot;
      <code>{esc(f.module_path)}</code> &middot;
      Target: <code>{esc(f.target_url)}</code> &middot;
      {esc(f.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC'))} &middot;
      Status: <strong>{esc(f.status.value)}</strong>
    </div>
    <div class="finding-tags">{owasp_label} {atlas_tags}</div>
  </div>
  <div class="finding-body">
    <div class="section"><h4>Description</h4><p>{esc(f.description)}</p></div>
    {evidence_html}
    {remediation_html}
  </div>
</div>
"""

        # Assemble full HTML
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(self.assessment_name)}</title>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  background:#0d1117;color:#c9d1d9;line-height:1.6;padding:2rem;
}}
a{{color:#58a6ff;text-decoration:none}}
h1,h2,h3,h4{{color:#e6edf3}}
h1{{font-size:1.8rem;margin-bottom:.5rem}}
h2{{font-size:1.4rem;margin:2rem 0 1rem;padding-bottom:.5rem;border-bottom:1px solid #21262d}}
h3{{font-size:1.1rem;margin:1rem 0 .5rem}}
h4{{font-size:.95rem;margin-bottom:.4rem;color:#8b949e}}
.container{{max-width:1100px;margin:0 auto}}
.header{{margin-bottom:2rem}}
.header p{{color:#8b949e;margin:.2rem 0}}
.risk-badge{{
  display:inline-block;padding:.3rem .8rem;border-radius:4px;
  font-weight:700;font-size:.9rem;margin-top:.5rem;
}}
.risk-CRITICAL{{background:#ff1744;color:#fff}}
.risk-HIGH{{background:#ff5722;color:#fff}}
.risk-MEDIUM{{background:#ff9800;color:#000}}
.risk-LOW{{background:#2196f3;color:#fff}}
.risk-INFORMATIONAL{{background:#78909c;color:#fff}}
.risk-NONE{{background:#21262d;color:#8b949e}}
.summary-grid{{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin:1rem 0}}
@media(max-width:768px){{.summary-grid{{grid-template-columns:1fr}}}}
.panel{{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:1.2rem}}
.bar-row{{display:flex;align-items:center;margin:.4rem 0}}
.bar-label{{width:80px;font-size:.85rem;color:#8b949e;text-align:right;padding-right:.8rem}}
.bar-track{{flex:1;height:20px;background:#21262d;border-radius:4px;overflow:hidden}}
.bar-fill{{height:100%;border-radius:4px;transition:width .3s}}
.bar-count{{width:36px;text-align:right;font-weight:700;font-size:.85rem;padding-left:.5rem}}
table{{width:100%;border-collapse:collapse;margin:.5rem 0}}
th,td{{padding:.5rem .7rem;text-align:left;border-bottom:1px solid #21262d;font-size:.85rem}}
th{{color:#8b949e;font-weight:600;text-transform:uppercase;font-size:.75rem;letter-spacing:.05em}}
td.cat-id{{font-weight:700;color:#58a6ff}}
td.count{{text-align:center;font-weight:700}}
td.tested{{color:#3fb950;font-weight:700}}
td.not-tested{{color:#484f58}}
.finding-card{{background:#161b22;border:1px solid #21262d;border-radius:8px;margin:1rem 0;overflow:hidden}}
.finding-header{{padding:1rem 1.2rem;background:#0d1117}}
.finding-title{{display:flex;align-items:center;gap:.6rem;flex-wrap:wrap}}
.finding-num{{color:#484f58;font-weight:700}}
.severity-badge{{
  display:inline-block;padding:.15rem .5rem;border-radius:3px;
  font-weight:700;font-size:.75rem;text-transform:uppercase;
}}
.severity-badge.critical{{background:#ff1744;color:#fff}}
.severity-badge.high{{background:#ff5722;color:#fff}}
.severity-badge.medium{{background:#ff9800;color:#000}}
.severity-badge.low{{background:#2196f3;color:#fff}}
.severity-badge.info{{background:#78909c;color:#fff}}
.finding-name{{font-weight:600;font-size:1.05rem}}
.finding-meta{{margin-top:.4rem;font-size:.8rem;color:#8b949e}}
.finding-meta code{{background:#21262d;padding:.1rem .3rem;border-radius:3px;font-size:.78rem}}
.finding-tags{{margin-top:.5rem;display:flex;gap:.4rem;flex-wrap:wrap}}
.tag{{display:inline-block;padding:.15rem .5rem;border-radius:3px;font-size:.75rem;font-weight:600}}
.tag.owasp{{background:#1a3a5c;color:#58a6ff}}
.tag.atlas{{background:#2d1a3a;color:#bc8cff}}
.finding-body{{padding:1rem 1.2rem}}
.finding-body .section{{margin-bottom:1rem}}
.finding-body p{{color:#c9d1d9;font-size:.9rem}}
.evidence-list{{list-style:none;padding:0}}
.evidence-list li{{
  padding:.3rem .5rem;margin:.2rem 0;background:#0d1117;
  border-radius:4px;font-size:.85rem;
}}
.evidence-list li code{{color:#f0883e;background:none;padding:0}}
.remediation{{background:#0b2e13;border-radius:6px;padding:.8rem 1rem}}
.remediation p{{color:#3fb950}}
.footer{{margin-top:3rem;padding-top:1rem;border-top:1px solid #21262d;text-align:center;color:#484f58;font-size:.8rem}}
</style>
</head>
<body>
<div class="container">

<div class="header">
  <h1>{esc(self.assessment_name)}</h1>
  <p><strong>Generated:</strong> {now}</p>
  {"<p><strong>Assessor:</strong> " + esc(self.assessor) + "</p>" if self.assessor else ""}
  {"<p><strong>Organization:</strong> " + esc(self.organization) + "</p>" if self.organization else ""}
  <span class="risk-badge risk-{s['overall_risk']}">{s['overall_risk']} RISK</span>
</div>

<h2>Executive Summary</h2>
<p>This assessment identified <strong>{s['total_findings']}</strong> finding(s) across the target environment.</p>

<div class="summary-grid">
  <div class="panel">
    <h3>Severity Distribution</h3>
    {bar_rows}
  </div>
  <div class="panel">
    <h3>Status Breakdown</h3>
    <table>
      <tr><th>Status</th><th>Count</th></tr>
      {"".join(f'<tr><td>{esc(st)}</td><td class="count">{ct}</td></tr>' for st, ct in s["status_counts"].items())}
    </table>
  </div>
</div>

<h2>OWASP LLM Top 10 (2025) Coverage</h2>
<div class="panel">
  <table>
    <tr><th>ID</th><th>Category</th><th>Tested</th><th>Findings</th></tr>
    {owasp_rows}
  </table>
</div>

{"<h2>MITRE ATLAS Techniques Observed</h2><div class='panel'><table><tr><th>Technique</th><th>Name</th><th>Findings</th></tr>" + atlas_rows + "</table></div>" if atlas_rows else ""}

<h2>Detailed Findings</h2>
{finding_cards if finding_cards else '<p style="color:#8b949e;">No findings recorded.</p>'}

<div class="footer">
  <p>MetaLLM &mdash; AI Security Assessment Framework</p>
</div>

</div>
</body>
</html>"""

        filepath.write_text(html_content, encoding="utf-8")
        logger.info("reporting.html_exported", path=str(filepath))
        return filepath
