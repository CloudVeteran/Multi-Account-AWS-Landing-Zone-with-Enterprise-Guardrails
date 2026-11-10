"""Render docs/architecture.png for the landing zone README.

The picture shows only what this Terraform configuration creates: a management
account with GuardDuty and Security Hub in one Region, an organization root
with two service control policies, three organizational units, and six member
accounts. It does not draw Control Tower, CloudTrail, or centralized logging.

The current AWS architecture icon set has no separate service-control-policy
glyph. The guardrail nodes use the official IAM permissions icon, which is the
policy document (allow and deny marks), and the text states the real effect.

Regenerate with Graphviz on PATH:

    pip install diagrams
    python docs/diagram.py
"""

from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.management import (
    Organizations,
    OrganizationsAccount,
    OrganizationsOrganizationalUnit,
)
from diagrams.aws.security import Guardduty, IAMPermissions, SecurityHub

OUT = Path(__file__).resolve().parent / "architecture"

FONT = "Liberation Sans"
INK = "#232F3E"
MUTED = "#545B64"
LINE = "#687078"

# Plain-English labels. Line breaks keep each phrase under the icon; the
# wording stays inside what the guardrails table says the JSON does.
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
        "margin": "16",
        "labeljust": "c",
    }


def same_rank(cluster: Cluster, *nodes) -> None:
    ids = " ".join(f'"{node.nodeid}"' for node in nodes)
    cluster.dot.body.append(f"{{rank=same; {ids};}}")


def order_row(cluster: Cluster, *nodes, minlen: str = "1") -> None:
    """Place nodes left to right on one rank, with no visible arrows."""
    same_rank(cluster, *nodes)
    for left, right in zip(nodes, nodes[1:]):
        left >> Edge(style="invis", minlen=minlen) >> right


def policy(label: str) -> IAMPermissions:
    # The library's default height draws a three-line label across the icon.
    return IAMPermissions(label, height="3.6")


def main() -> None:
    graph_attr = {
        "bgcolor": "white",
        "pad": "0.35",
        "nodesep": "0.35",
        "ranksep": "0.42",
        "splines": "ortho",
        "fontname": FONT,
        "fontsize": "26",
        "fontcolor": INK,
        "labeljust": "c",
        "labelloc": "t",
        "dpi": "120",
        "forcelabels": "true",
    }
    node_attr = {
        "fontname": FONT,
        "fontsize": "16",
        "fontcolor": INK,
        "labelloc": "b",
    }
    edge_attr = {
        "color": LINE,
        "fontname": FONT,
        "fontsize": "15",
        "fontcolor": MUTED,
        "penwidth": "1.6",
        "arrowsize": "0.85",
    }

    with Diagram(
        "What this Terraform creates",
        filename=str(OUT),
        show=False,
        direction="TB",
        curvestyle="ortho",
        outformat="png",
        graph_attr=graph_attr,
        node_attr=node_attr,
        edge_attr=edge_attr,
    ):
        with Cluster(
            "Management account   ·   one Region",
            graph_attr=cluster_style("#FFF8F1", "#ED7100"),
        ) as management:
            guardduty = Guardduty("Threat detection\nGuardDuty")
            management_account = OrganizationsAccount("Management\naccount")
            security_hub = SecurityHub("Security Hub\nNIST 800-53 Rev. 5")
            order_row(management, guardduty, management_account, security_hub)

        with Cluster(
            "AWS Organization",
            graph_attr={
                **cluster_style("#FFFFFF", "#232F3E"),
                # Top-left, so the arrow from the management account misses it.
                "labeljust": "l",
            },
        ) as organization:
            root = Organizations("Organization root")

            with Cluster(
                "Guardrails on the organization root\n"
                "They do not apply to the management account",
                graph_attr=cluster_style("#FCF7F7", "#D13212", "16"),
            ) as guardrails:
                principal_type_root = policy(SCP_PRINCIPAL_TYPE_ROOT)
                s3_non_tls = policy(SCP_S3_NON_TLS)
                order_row(guardrails, principal_type_root, s3_non_tls, minlen="2")

            with Cluster(
                "Security",
                graph_attr=cluster_style("#F4F6F8", "#232F3E", "20"),
            ) as security:
                security_ou = OrganizationsOrganizationalUnit(
                    "Organizational\nunit"
                )
                security_account = OrganizationsAccount("Security\naccount")
                logging_account = OrganizationsAccount("Logging\naccount")
                audit_account = OrganizationsAccount("Audit\naccount")
                order_row(
                    security, security_account, logging_account, audit_account
                )
                security_ou >> Edge(style="invis") >> logging_account

            with Cluster(
                "Workloads",
                graph_attr=cluster_style("#F4F6F8", "#232F3E", "20"),
            ) as workloads:
                workloads_ou = OrganizationsOrganizationalUnit(
                    "Organizational\nunit"
                )
                production_account = OrganizationsAccount("Production\naccount")
                nonproduction_account = OrganizationsAccount(
                    "Non-production\naccount"
                )
                order_row(workloads, production_account, nonproduction_account)
                workloads_ou >> Edge(style="invis") >> production_account

            with Cluster(
                "Infrastructure",
                graph_attr=cluster_style("#F4F6F8", "#232F3E", "20"),
            ):
                infrastructure_ou = OrganizationsOrganizationalUnit(
                    "Organizational\nunit"
                )
                shared_services = OrganizationsAccount("Shared services\naccount")
                infrastructure_ou >> Edge(style="invis") >> shared_services

            # This rank keeps Security, Workloads, and Infrastructure in one
            # row. Graphviz draws these icons just above each box.
            order_row(organization, security_ou, workloads_ou, infrastructure_ou)
            root >> Edge(style="invis") >> principal_type_root
            root >> Edge(style="invis") >> s3_non_tls
            principal_type_root >> Edge(style="invis") >> workloads_ou
            s3_non_tls >> Edge(style="invis") >> workloads_ou

        management_account >> Edge(label="owns", minlen="2") >> root


if __name__ == "__main__":
    main()
