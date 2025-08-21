import os
from datetime import datetime
from langchain_core.tools import tool

# For PDF
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


@tool
def report_generator_tool(findings: dict, format: str = "markdown") -> str:
    """
    Generates a pentest report from the collected findings.

    Args:
        findings (dict): A dictionary with the vulnerabilities found.
            Example:
            {
                "target": "example.com",
                "findings": [
                    {"title": "SQL Injection", "severity": "High", "details": "'id' parameter is injectable"},
                    {"title": "Weak TLS", "severity": "Medium", "details": "Supports TLS 1.0"}
                ],
                "recommendations": [
                    "Use prepared statements",
                    "Disable TLS 1.0"
                ]
            }
        format (str): "markdown" or "pdf".

    Returns:
        str: Path to the generated file.
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"pentest_report_{timestamp}"

    if format == "markdown":
        filepath = f"reports/{filename}.md" #### TODO Modify this path as needed
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Pentest Report - {findings['target']}\n\n")
            f.write("## Findings\n")
            for fnd in findings.get("findings", []):
                f.write(f"### {fnd['title']} ({fnd['severity']})\n")
                f.write(f"{fnd['details']}\n\n")

            if "recommendations" in findings:
                f.write("## Recommendations\n")
                for rec in findings["recommendations"]:
                    f.write(f"- {rec}\n")
        return filepath

    elif format == "pdf":
        filepath = f"reports/{filename}.pdf" #### TODO Modify this path as needed
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph(f"Pentest Report - {findings['target']}", styles['Title']))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Findings", styles['Heading2']))
        for fnd in findings.get("findings", []):
            story.append(Paragraph(f"{fnd['title']} ({fnd['severity']})", styles['Heading3']))
            story.append(Paragraph(fnd['details'], styles['Normal']))
            story.append(Spacer(1, 12))

        if "recommendations" in findings:
            story.append(Paragraph("Recommendations", styles['Heading2']))
            for rec in findings["recommendations"]:
                story.append(Paragraph(f"- {rec}", styles['Normal']))
                story.append(Spacer(1, 6))

        doc.build(story)
        return filepath

    else:
        return "❌ Unsupported format. Choose 'markdown' or 'pdf'."


# test_findings = {
#     "target": "example.com",
#     "findings": [
#         {"title": "SQL Injection", "severity": "High", "details": "Paramètre 'id' injectable"},
#         {"title": "Weak TLS", "severity": "Medium", "details": "Supporte TLS 1.0"}
#     ],
#     "recommendations": [
#         "Utiliser des requêtes préparées",
#         "Désactiver TLS 1.0"
#     ]
# }

# print(report_generator_tool.invoke({"findings": test_findings, "format": "pdf"}))