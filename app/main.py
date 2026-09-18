from __future__ import annotations

import json
from datetime import datetime

import streamlit as st

from app.core.config import CONFIG
from app.services.evidence_service import get_evidence
from app.services.health_service import get_health
from app.services.network_service import get_state

st.set_page_config(
    page_title="NetworkLab",
    page_icon="⌘",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Lab console theme
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --nl-bg: #071018;
        --nl-panel: #0c1721;
        --nl-panel-2: #101e2a;
        --nl-border: #1d3444;
        --nl-text: #e6eef5;
        --nl-muted: #7f96a8;
        --nl-accent: #37b6ff;
        --nl-green: #3ddc97;
        --nl-yellow: #f4c95d;
        --nl-red: #ff6b6b;
    }

    .stApp { background: var(--nl-bg); color: var(--nl-text); }
    [data-testid="stSidebar"] { background: #09131c; border-right: 1px solid var(--nl-border); }
    [data-testid="stSidebar"] .block-container { padding-top: 1.25rem; }
    .block-container { max-width: 1540px; padding-top: 1.5rem; padding-bottom: 3rem; }

    h1, h2, h3 { letter-spacing: -0.02em; }
    h1 { font-size: 2.15rem !important; }
    h2 { font-size: 1.35rem !important; margin-top: 1.2rem !important; }
    h3 { font-size: 1.02rem !important; }

    .nl-brand {
        font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
        font-size: 1.25rem;
        font-weight: 800;
        letter-spacing: .12em;
    }
    .nl-kicker {
        color: var(--nl-accent);
        font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
        font-size: .72rem;
        letter-spacing: .14em;
        text-transform: uppercase;
    }
    .nl-subtitle { color: var(--nl-muted); margin-top: -.45rem; margin-bottom: 1.1rem; }
    .nl-panel {
        background: linear-gradient(180deg, var(--nl-panel), #0a141d);
        border: 1px solid var(--nl-border);
        border-radius: 10px;
        padding: 16px 18px;
        min-height: 108px;
    }
    .nl-panel-title {
        color: var(--nl-muted);
        font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
        font-size: .68rem;
        letter-spacing: .11em;
        text-transform: uppercase;
    }
    .nl-value { font-size: 1.65rem; font-weight: 750; margin-top: 6px; }
    .nl-ok { color: var(--nl-green); }
    .nl-warn { color: var(--nl-yellow); }
    .nl-bad { color: var(--nl-red); }

    .nl-topology {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        padding: 24px 8px;
        background: #09141e;
        border: 1px solid var(--nl-border);
        border-radius: 10px;
        overflow-x: auto;
    }
    .nl-node {
        min-width: 150px;
        text-align: center;
        padding: 14px 12px;
        border: 1px solid #29485b;
        border-radius: 8px;
        background: #0e1d29;
    }
    .nl-node strong { display: block; }
    .nl-node small { color: var(--nl-muted); }
    .nl-link { color: var(--nl-accent); font-family: monospace; font-size: 1.1rem; }

    .nl-status {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 999px;
        font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
        font-size: .68rem;
        letter-spacing: .06em;
        border: 1px solid currentColor;
    }
    .nl-footer {
        color: #62798b;
        border-top: 1px solid var(--nl-border);
        margin-top: 2rem;
        padding-top: .8rem;
        font-size: .76rem;
        font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Data layer
# ---------------------------------------------------------------------------
@st.cache_data(ttl=10)
def state() -> dict:
    return get_state()


@st.cache_data(ttl=10)
def health() -> dict:
    return get_health()


@st.cache_data(ttl=30)
def evidence() -> dict:
    return get_evidence()


def status_text(ok: bool) -> str:
    return "OPERATIONAL" if ok else "ATTENTION"


def metric_card(label: str, value: str, state_class: str = "") -> None:
    st.markdown(
        f"""
        <div class="nl-panel">
            <div class="nl-panel-title">{label}</div>
            <div class="nl-value {state_class}">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def header(title: str, subtitle: str) -> None:
    st.markdown('<div class="nl-kicker">NETWORKLAB / SOFTWARE NETWORK LABORATORY</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<div class="nl-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def safe_rows(value):
    return value if isinstance(value, list) else []


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------
st.sidebar.markdown('<div class="nl-brand">NETWORKLAB</div>', unsafe_allow_html=True)
st.sidebar.caption("Software-only / stage laboratory")

st.sidebar.markdown("### Laboratory")
page = st.sidebar.radio(
    "Laboratory workspace",
    [
        "Command Center",
        "Topology",
        "Interfaces",
        "Addressing & DNS",
        "Connectivity",
        "Services",
        "Diagnostics",
        "Evidence",
    ],
    label_visibility="collapsed",
)

st.sidebar.divider()
st.sidebar.markdown("### Controls")

if st.sidebar.button("Refresh laboratory", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption("Automatic data cache: 10s · Evidence cache: 30s")

st.sidebar.divider()
st.sidebar.markdown("### Laboratory scope")
st.sidebar.success("READ-ONLY")
st.sidebar.caption("Software-only stage environment")
st.sidebar.caption("Physical hardware: not required")
st.sidebar.caption("Production configuration: disabled")

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
try:
    data = state()
    h = health()

    adapters = safe_rows(data.get("adapters"))
    ip_config = safe_rows(data.get("ip"))
    connectivity = safe_rows(data.get("connectivity"))
    services = safe_rows(data.get("services"))

    connectivity_ok = bool(h.get("connectivity_ok"))
    services_ok = bool(h.get("services_ok"))
    overall_ok = connectivity_ok and services_ok

    if page == "Command Center":
        header(
            "Command Center",
            "Primary operating view for the local Windows network laboratory.",
        )

        cols = st.columns(5)
        with cols[0]:
            metric_card("LAB STATUS", status_text(overall_ok), "nl-ok" if overall_ok else "nl-bad")
        with cols[1]:
            metric_card("ADAPTERS", str(len(adapters)))
        with cols[2]:
            metric_card("IP INTERFACES", str(len(ip_config)))
        with cols[3]:
            metric_card(
                "CONNECTIVITY",
                "PASS" if connectivity_ok else "FAIL",
                "nl-ok" if connectivity_ok else "nl-bad",
            )
        with cols[4]:
            running = int(h.get("services_running", 0))
            total = int(h.get("services_total", 0))
            metric_card("SERVICES", f"{running}/{total}", "nl-ok" if services_ok else "nl-warn")

        st.subheader("Laboratory state")

        left, right = st.columns([1.35, 1])

        with left:
            st.markdown("#### Logical network path")
            st.markdown(
                """
                <div class="nl-topology">
                    <div class="nl-node"><strong>WORKSTATION</strong><small>Windows host</small></div>
                    <div class="nl-link">━━▶</div>
                    <div class="nl-node"><strong>NETWORK STACK</strong><small>Adapters / TCP-IP</small></div>
                    <div class="nl-link">━━▶</div>
                    <div class="nl-node"><strong>LOOPBACK</strong><small>127.0.0.1</small></div>
                    <div class="nl-link">━━▶</div>
                    <div class="nl-node"><strong>LAB SERVICES</strong><small>DNS / DHCP / NLA</small></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with right:
            st.markdown("#### Environment")
            st.json(
                {
                    "project": CONFIG.get("project"),
                    "environment": CONFIG.get("environment"),
                    "model": CONFIG.get("scope", {}).get("model"),
                    "production_allowed": CONFIG.get("scope", {}).get("production_network_allowed"),
                    "configuration_enabled": CONFIG.get("safety", {}).get("configuration_enabled"),
                }
            )

        st.subheader("Active observations")

        if connectivity:
            conn_rows = []
            for item in connectivity:
                conn_rows.append(
                    {
                        "Target": item.get("target", "—"),
                        "Status": "PASS" if item.get("ok") else "FAIL",
                        "Latency": item.get("latency", "—"),
                    }
                )
            st.dataframe(conn_rows, use_container_width=True, hide_index=True)

        if services:
            service_rows = []
            for item in services:
                running = item.get("status") == "Running"
                service_rows.append(
                    {
                        "Service": item.get("name", "—"),
                        "State": "RUNNING" if running else str(item.get("status", "—")).upper(),
                        "Start type": item.get("startType", "—"),
                    }
                )
            st.dataframe(service_rows, use_container_width=True, hide_index=True)

    elif page == "Topology":
        header(
            "Topology",
            "Logical topology of the software-only laboratory. No physical network changes are performed.",
        )

        st.markdown(
            """
            <div class="nl-topology">
                <div class="nl-node"><strong>HOST</strong><small>Windows 11</small></div>
                <div class="nl-link">━━▶</div>
                <div class="nl-node"><strong>NIC LAYER</strong><small>Network adapters</small></div>
                <div class="nl-link">━━▶</div>
                <div class="nl-node"><strong>IP LAYER</strong><small>IPv4 / gateway / DNS</small></div>
                <div class="nl-link">━━▶</div>
                <div class="nl-node"><strong>TEST TARGET</strong><small>127.0.0.1</small></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.subheader("Topology inventory")
        st.dataframe(
            [
                {"Layer": "Host", "Component": "Windows workstation", "Mode": "Observed"},
                {"Layer": "Link", "Component": "Network adapters", "Mode": "Observed"},
                {"Layer": "Network", "Component": "IPv4 configuration", "Mode": "Observed"},
                {"Layer": "Transport/Test", "Component": "Loopback 127.0.0.1", "Mode": "Tested"},
                {"Layer": "Services", "Component": "DNS Cache / DHCP / NLA", "Mode": "Observed"},
            ],
            use_container_width=True,
            hide_index=True,
        )

    elif page == "Interfaces":
        header("Interfaces", "Adapter inventory and link state reported by Windows.")

        if adapters:
            rows = []
            for item in adapters:
                rows.append(
                    {
                        "Interface": item.get("Name", "—"),
                        "State": item.get("Status", "—"),
                        "Link speed": item.get("LinkSpeed", "—"),
                        "MAC address": item.get("MacAddress", "—"),
                    }
                )
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info("No network adapters were returned by the Windows diagnostic layer.")

    elif page == "Addressing & DNS":
        header("Addressing & DNS", "IPv4 addressing, default gateways and DNS servers.")

        if ip_config:
            rows = []
            for item in ip_config:
                rows.append(
                    {
                        "Interface": item.get("interface", "—"),
                        "IPv4": item.get("ipv4", "—"),
                        "Gateway": item.get("gateway", "—"),
                        "DNS": item.get("dns", "—"),
                    }
                )
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info("No IPv4 configuration was returned by the Windows diagnostic layer.")

    elif page == "Connectivity":
        header("Connectivity Tests", "Read-only connectivity probes against configured laboratory targets.")

        if connectivity:
            for item in connectivity:
                ok = bool(item.get("ok"))
                label = "PASS" if ok else "FAIL"
                with st.container(border=True):
                    a, b, c = st.columns([2, 1, 1])
                    a.markdown(f"**{item.get('target', 'Unknown target')}**")
                    b.markdown(f'<span class="nl-status {"nl-ok" if ok else "nl-bad"}">{label}</span>', unsafe_allow_html=True)
                    c.write(item.get("latency", "—"))
        else:
            st.warning("No connectivity targets are currently configured.")

        st.caption("Connectivity testing is observational. Network configuration remains disabled.")

    elif page == "Services":
        header("Infrastructure Services", "Windows services monitored by the laboratory.")

        rows = []
        for item in services:
            running = item.get("status") == "Running"
            rows.append(
                {
                    "Service": item.get("name", "—"),
                    "State": "RUNNING" if running else str(item.get("status", "—")).upper(),
                    "Start type": item.get("startType", "—"),
                    "Health": "OK" if running else "ATTENTION",
                }
            )

        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.warning("No monitored services were returned.")

    elif page == "Diagnostics":
        header("Diagnostics", "Runtime and network health checks used to validate the laboratory.")

        cols = st.columns(4)
        with cols[0]:
            metric_card("CONNECTIVITY", "PASS" if connectivity_ok else "FAIL", "nl-ok" if connectivity_ok else "nl-bad")
        with cols[1]:
            metric_card("SERVICES", "PASS" if services_ok else "FAIL", "nl-ok" if services_ok else "nl-bad")
        with cols[2]:
            metric_card("POWERSHELL", str(h.get("powershell", "—")))
        with cols[3]:
            metric_card("PYTHON", "AVAILABLE" if h.get("python_available") else "MISSING", "nl-ok" if h.get("python_available") else "nl-bad")

        st.subheader("Diagnostic output")
        st.json(h)

    elif page == "Evidence":
        header(
            "Evidence & Reporting",
            "Machine-readable evidence for stage documentation, troubleshooting and GitHub traceability.",
        )

        e = evidence()

        c1, c2 = st.columns([1, 3])
        with c1:
            st.download_button(
                "Download JSON evidence",
                data=json.dumps(e, indent=2),
                file_name="networklab-evidence.json",
                mime="application/json",
                use_container_width=True,
            )
        with c2:
            st.caption("Evidence is generated from the same read-only PowerShell diagnostic layer used by the laboratory UI.")

        st.json(e)

    st.markdown(
        f'<div class="nl-footer">NETWORKLAB · {CONFIG.get("environment", "stage-lab")} · READ-ONLY · '
        f'Last UI refresh {datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")}</div>',
        unsafe_allow_html=True,
    )

except Exception as exc:
    st.error("NetworkLab diagnostic layer error")
    st.code(str(exc))
    st.caption("The UI is running, but a Windows diagnostic service returned an error.")
