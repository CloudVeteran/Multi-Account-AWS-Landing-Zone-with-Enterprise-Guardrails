"""Render docs/architecture.png for the landing zone README.

The picture shows only what this Terraform configuration creates: a management
account with GuardDuty and Security Hub in one Region, an organization root
with two service control policies, three organizational units, and six member
accounts. It does not draw Control Tower, CloudTrail, or centralized logging.

The current AWS architecture icon set has no separate service-control-policy
glyph. The guardrail nodes use the official IAM permissions icon, which is the
policy document (allow and deny marks), and the text states the real effect.

Labels are HTML tables so the caption sits below the icon with real padding.
Graphviz's default icon node draws that caption across the bottom of the image.

Regenerate with Graphviz on PATH:

    pip install diagrams
    python docs/diagram.py
"""

import html
from pathlib import Path

import diagrams
from diagrams import Cluster, Diagram, Edge
from diagrams.aws.management import (
    Organizations,
    OrganizationsAccount,
    OrganizationsOrganizationalUnit,
)
from diagrams.aws.security import Guardduty, IAMPermissions, SecurityHub

OUT = Path(__file__).resolve().parent / "architecture"
ICON_ROOT = Path(diagrams.__file__).resolve().parent.parent

FONT = "Liberation Sans"
INK = "#232F3E"
MUTED = "#545B64"
LINE = "#687078"

# Plain-English labels. The wording stays inside what the guardrails table
# says the JSON does.
SCP_PRINCIPAL_TYPE_ROOT = "Blocks actions by\nprincipal type Root\n(SCP)"
SCP_S3_NON_TLS = "Blocks S3 ACL/policy\nchanges over non-TLS\n(SCP)"


def cluster_style(fill: str, border: str, fontsize: str = "18") -> dict:
    return {
        "bgcolor": fill,
        "pencolor": border,
        "penwidth": "1.8",
        "style": "rounded,filled",
        "fontname": FONT,
        "fontsize": fontsize,
        "fontcolor": INK,
        # Points. Large enough that the cluster title sits above the icons.
        "margin": "28",
        "labeljust": "c",
    }


def same_rank(cluster: Cluster, *nodes) -> None:
    ids = " ".join(f'"{node.nodeid}"' for node in nodes)
    cluster.dot.body.append(f"{{rank=same; {ids};}}")


def order_row(cluster: Cluster, *nodes) -> None:
    """Place nodes left to right on one rank, with no visible arrows."""
    same_rank(cluster, *nodes)
    for left, right in zip(nodes, nodes[1:]):
        left >> Edge(style="invis") >> right


def icon_file(cls) -> Path:
    return ICON_ROOT / cls._icon_dir / cls._icon


def html_label(src: Path, text: str) -> str:
    """Icon with a gap, then the caption. The gap is what keeps text off the art."""
    rows = "".join(
        "<TR><TD ALIGN=\"CENTER\">"
        f'<FONT FACE="{FONT}" POINT-SIZE="16" COLOR="{INK}">{html.escape(line)}</FONT>'
        "</TD></TR>"
        for line in text.split("\n")
    )
    return (
        '<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0">'
        '<TR><TD FIXEDSIZE="TRUE" WIDTH="78" HEIGHT="78" ALIGN="CENTER">'
        f'<IMG SRC="{src}" SCALE="TRUE"/></TD></TR>'
        '<TR><TD HEIGHT="12"></TD></TR>'
        f"{rows}</TABLE>>"
    )


def aws_icon(cls, text: str):
    """Diagrams node whose caption is padded below the official icon."""

    class _Icon(cls):
        # Skip the library image attribute. The HTML label draws the icon.
        _icon = None

    # fixedsize/width/height on the graph would crush the HTML table into a
    # 1.4 inch box and paint the icon on top of the caption.
    return _Icon(
        html_label(icon_file(cls), text),
        shape="plaintext",
        fixedsize="false",
        width="0",
        height="0",
        margin="0.02",
        fontname=FONT,
        fontsize="16",
        fontcolor=INK,
    )


def main() -> None:
    graph_attr = {
        "bgcolor": "white",
        "pad": "0.4",
        "nodesep": "0.55",
        "ranksep": "0.7",
        "splines": "true",
        "fontname": FONT,
        "fontsize": "26",
        "fontcolor": INK,
        "labeljust": "c",
        "labelloc": "t",
        "dpi": "100",
        "forcelabels": "true",
        "compound": "true",
    }
    node_attr = {
        "fontname": FONT,
        "fontsize": "16",
        "fontcolor": INK,
    }
    edge_attr = {
        "color": LINE,
        "fontname": FONT,
        "fontsize": "15",
        "fontcolor": MUTED,
        "penwidth": "1.6",
        "arrowsize": "0.9",
    }

    with Diagram(
        "What this Terraform creates",
        filename=str(OUT),
        show=False,
        direction="TB",
        curvestyle="curved",
        outformat="png",
        graph_attr=graph_attr,
        node_attr=node_attr,
        edge_attr=edge_attr,
    ):
        with Cluster(
            "Management account   ·   one Region",
            graph_attr=cluster_style("#FFF8F1", "#ED7100"),
        ) as management:
            guardduty = aws_icon(Guardduty, "Threat detection\nGuardDuty")
            management_account = aws_icon(OrganizationsAccount, "Management\naccount")
            security_hub = aws_icon(SecurityHub, "Security Hub\nNIST 800-53 Rev. 5")
            order_row(management, guardduty, management_account, security_hub)

        with Cluster(
            "AWS Organization",
            graph_attr={
                **cluster_style("#FFFFFF", "#232F3E"),
                # Top-left, so the arrow from the management account misses it.
                "labeljust": "l",
            },
        ):
            root = aws_icon(Organizations, "Organization root")

            with Cluster(
                "Guardrails on the organization root\n"
                "They do not apply to the management account",
                graph_attr={
                    **cluster_style("#FCF7F7", "#D13212", "16"),
                    # Bottom, so the "attached" arrow can enter the top of the box.
                    "labelloc": "b",
                },
            ) as guardrails:
                principal_type_root = aws_icon(IAMPermissions, SCP_PRINCIPAL_TYPE_ROOT)
                s3_non_tls = aws_icon(IAMPermissions, SCP_S3_NON_TLS)
                order_row(guardrails, principal_type_root, s3_non_tls)

            with Cluster(
                "Security",
                graph_attr=cluster_style("#F4F6F8", "#232F3E", "20"),
            ) as security:
                security_ou = aws_icon(OrganizationsOrganizationalUnit, "Security OU")
                security_account = aws_icon(OrganizationsAccount, "Security\naccount")
                logging_account = aws_icon(OrganizationsAccount, "Logging\naccount")
                audit_account = aws_icon(OrganizationsAccount, "Audit\naccount")
                order_row(
                    security, security_account, logging_account, audit_account
                )
                security_ou >> [security_account, logging_account, audit_account]

            with Cluster(
                "Workloads",
                graph_attr=cluster_style("#F4F6F8", "#232F3E", "20"),
            ) as workloads:
                workloads_ou = aws_icon(OrganizationsOrganizationalUnit, "Workloads OU")
                production_account = aws_icon(
                    OrganizationsAccount, "Production\naccount"
                )
                nonproduction_account = aws_icon(
                    OrganizationsAccount, "Non-production\naccount"
                )
                order_row(workloads, production_account, nonproduction_account)
                workloads_ou >> [production_account, nonproduction_account]

            with Cluster(
                "Infrastructure",
                graph_attr=cluster_style("#F4F6F8", "#232F3E", "20"),
            ):
                infrastructure_ou = aws_icon(
                    OrganizationsOrganizationalUnit, "Infrastructure OU"
                )
                shared_services = aws_icon(
                    OrganizationsAccount, "Shared services\naccount"
                )
                infrastructure_ou >> shared_services

            # One labeled edge into the guardrails box, then an edge to each OU.
            # The invisible edges only keep the three groups under that box.
            # Ranking the OU icons from the parent pulls them out of the boxes.
            root >> Edge(label="attached") >> principal_type_root
            root >> Edge(style="invis") >> s3_non_tls
            for ou in (security_ou, workloads_ou, infrastructure_ou):
                principal_type_root >> Edge(style="invis") >> ou
                root >> Edge(constraint="false") >> ou

        management_account >> Edge(label="owns", minlen="2") >> root


if __name__ == "__main__":
    main()
