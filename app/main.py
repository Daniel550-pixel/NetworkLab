from __future__ import annotations

import json
from datetime import datetime

import streamlit as st

from app.core.config import CONFIG
from app.services.evidence_service import get_evidence
from app.services.health_service import get_health
from app.services.network_service import get_state
from app.ui.topology3d import render_topology

st.set_page_config(
    page_title="NetworkLab",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --bg: #071019;
        --sidebar: #09131c;
        --panel: #0d1923;
        --panel2: #101f2b;
        --border: #1c3342;
        --text: #e7eef4;
        --muted: #8095a5;
        --accent: #4bb8ff;
        --ok: #45d39a;
        --warn: #e8bd5c;
        --bad: #ff7070;
    }

    .stApp { background: var(--bg); color: var(--text); }
    [data-testid="stSidebar"] {
        background: var(--sidebar);
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] .block-container { padding: 1.25rem 1rem; }
    .block-container {
        max-width: 1380px;
        padding: 1.6rem 2.2rem 3rem;
    }

    /* Sidebar */
    .brand {
        font: 800 1.12rem/1 ui-monospace, SFMono-Regular, Consolas, monospace;
        letter-spacing: .14em;
        margin-bottom: .25rem;
    }
    .brand-sub {
        color: var(--muted);
        font-size: .72rem;
        margin-bottom: 1.25rem;
    }
    .side-section {
        color: #5f7788;
        font: 700 .63rem/1 ui-monospace, SFMono-Regular, Consolas, monospace;
        letter-spacing: .13em;
        text-transform: uppercase;
        margin: 1.1rem 0 .45rem;
    }

    /* Header */
    .eyebrow {
        color: var(--accent);
        font: 700 .65rem/1 ui-monospace, SFMono-Regular, Consolas, monospace;
        letter-spacing: .16em;
        text-transform: uppercase;
        margin-bottom: .35rem;
    }
    .page-subtitle {
        color: var(--muted);
        font-size: .86rem;
        margin-top: -.65rem;
        margin-bottom: 1.4rem;
    }

    /* Status strip */
    .status-strip {
        display: grid;
        grid-template-columns: 1.3fr 1fr 1fr 1fr;
        border: 1px solid var(--border);
        border-radius: 9px;
        background: var(--panel);
        overflow: hidden;
        margin-bottom: 1.35rem;
    }
    .status-cell {
        padding: 13px 16px;
        border-right: 1px solid var(--border);
    }
    .status-cell:last-child { border-right: 0; }
    .status-label {
        color: var(--muted);
        font: 700 .61rem/1 ui-monospace, SFMono-Regular, Consolas, monospace;
        letter-spacing: .1em;
        text-transform: uppercase;
    }
    .status-value { font-size: 1rem; font-weight: 700; margin-top: 6px; }
    .ok { color: var(--ok); }
    .warn { color: var(--warn); }
    .bad { color: var(--bad); }

    /* Cards */
    .card {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 9px;
        padding: 15px 17px;
    }
    .card-title {
        font-weight: 700;
        font-size: .88rem;
        margin-bottom: 3px;
    }
    .card-meta {
        color: var(--muted);
        font-size: .72rem;
        margin-bottom: 12px;
    }
    .metric-row {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
    }
    .metric {
        background: var(--panel2);
        border: 1px solid #1b3040;
        border-radius: 7px;
        padding: 11px;
    }
    .metric-label {
        color: var(--muted);
        font: 700 .59rem/1 ui-monospace, SFMono-Regular, Consolas, monospace;
        letter-spacing: .09em;
        text-transform: uppercase;
    }
    .metric-value { font-size: 1.25rem; font-weight: 750; margin-top: 5px; }

    /* Topology */
    .topology {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
        padding: 20px 12px;
        background: #09141d;
        border: 1px solid var(--border);
        border-radius: 9px;
    }
    .node {
        flex: 1;
        text-align: center;
        background: var(--panel);
        border: 1px solid #254455;
        border-radius: 7px;
        padding: 11px 7px;
    }
    .node strong { display: block; font-size: .78rem; }
    .node span { color: var(--muted); font-size: .62rem; }
    .arrow { color: var(--accent); font-family: monospace; }

    /* Section labels */
    .section-label {
        color: #6d8799;
        font: 700 .63rem/1 ui-monospace, SFMono-Regular, Consolas, monospace;
        letter-spacing: .13em;
        text-transform: uppercase;
        margin: 1.35rem 0 .55rem;
    }

    /* Footer */
    .footer {
        border-top: 1px solid var(--border);
        color: #5f7484;
        font: .66rem ui-monospace, SFMono-Regular, Consolas, monospace;
        margin-top: 2rem;
        padding-top: .75rem;
    }

    /* Reduce Streamlit chrome */
    [data-testid="stMetric"] { background: transparent; }
    div[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data(ttl=10)
def state() -> dict:
    return get_state()

@st.cache_data(ttl=10)
def health() -> dict:
    return get_health()

@st.cache_data(ttl=30)
def evidence() -> dict:
    return get_evidence()

def rows(value):
    return value if isinstance(value, list) else []

def header(kicker: str, title: str, subtitle: str):
    st.markdown(f'<div class="eyebrow">{kicker}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)

def status_strip(overall: bool, connectivity: bool, services: bool, adapters: int):
    overall_text = "OPERATIONAL" if overall else "ATTENTION"
    overall_class = "ok" if overall else "bad"
    conn_text = "PASS" if connectivity else "FAIL"
    conn_class = "ok" if connectivity else "bad"
    svc_text = "HEALTHY" if services else "ATTENTION"
    svc_class = "ok" if services else "warn"
    st.markdown(
        f"""
        <div class="status-strip">
            <div class="status-cell">
                <div class="status-label">Laboratory</div>
                <div class="status-value {overall_class}">{overall_text}</div>
            </div>
            <div class="status-cell">
                <div class="status-label">Connectivity</div>
                <div class="status-value {conn_class}">{conn_text}</div>
            </div>
            <div class="status-cell">
                <div class="status-label">Services</div>
                <div class="status-value {svc_class}">{svc_text}</div>
            </div>
            <div class="status-cell">
                <div class="status-label">Interfaces</div>
                <div class="status-value">{adapters}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def topology():
    st.markdown(
        """
        <div class="topology">
            <div class="node"><strong>HOST</strong><span>Windows</span></div>
            <div class="arrow">━━</div>
            <div class="node"><strong>INTERFACES</strong><span>NIC layer</span></div>
            <div class="arrow">━━</div>
            <div class="node"><strong>TCP/IP</strong><span>Addressing</span></div>
            <div class="arrow">━━</div>
            <div class="node"><strong>LOOPBACK</strong><span>127.0.0.1</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Sidebar
st.sidebar.markdown('<div class="brand">NETWORKLAB</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="brand-sub">SOFTWARE NETWORK LABORATORY</div>', unsafe_allow_html=True)

st.sidebar.markdown('<div class="side-section">Workspace</div>', unsafe_allow_html=True)
page = st.sidebar.radio(
    "Workspace",
    ["3D Lab", "Command Center", "Topology", "Interfaces", "Addressing", "Connectivity", "Services", "Diagnostics", "Evidence"],
    label_visibility="collapsed",
)

st.sidebar.markdown('<div class="side-section">System</div>', unsafe_allow_html=True)
if st.sidebar.button("Refresh", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown(
    '<div class="side-section">Scope</div>'
    '<div style="font-size:.72rem;color:#8095a5;line-height:1.65">'
    '<b style="color:#45d39a">READ-ONLY</b><br>'
    'Software-only laboratory<br>'
    'Production configuration disabled'
    '</div>',
    unsafe_allow_html=True,
)

try:
    data = state()
    health_data = health()

    adapters = rows(data.get("adapters"))
    ip_config = rows(data.get("ip"))
    connectivity = rows(data.get("connectivity"))
    services = rows(data.get("services"))

    conn_ok = bool(health_data.get("connectivity_ok"))
    svc_ok = bool(health_data.get("services_ok"))
    overall_ok = conn_ok and svc_ok

    # 3D LAB
    if page == "3D Lab":
        header(
            "LAB / VISUALIZATION",
            "3D Laboratory",
            "Live interactive reconstruction of the observed logical network environment.",
        )
        status_strip(overall_ok, conn_ok, svc_ok, len(adapters))

        @st.fragment(run_every="5s")
        def live_topology():
            current = state()
            render_topology(current, height=700)

        live_topology()

        st.markdown('<div class="section-label">Selected telemetry</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Interfaces", len(adapters))
        with c2:
            st.metric("IPv4 configurations", len(ip_config))
        with c3:
            st.metric("Connectivity tests", len(connectivity))
        with c4:
            st.metric("Services", f"{sum(1 for x in services if x.get('status') == 'Running')}/{len(services)}")

        with st.expander("Raw topology state"):
            st.json(data)

    # COMMAND CENTER
    if page == "Command Center":
        header(
            "LAB / OPERATIONS",
            "Command Center",
            "A quiet operational view of the local network environment.",
        )
        status_strip(overall_ok, conn_ok, svc_ok, len(adapters))

        left, right = st.columns([1.35, .9], gap="large")

        with left:
            st.markdown('<div class="section-label">Network path</div>', unsafe_allow_html=True)
            topology()

        with right:
            st.markdown('<div class="section-label">Environment</div>', unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="card">
                    <div class="card-title">Stage laboratory</div>
                    <div class="card-meta">Current execution boundary</div>
                    <div class="metric-row">
                        <div class="metric"><div class="metric-label">Model</div><div class="metric-value">Software</div></div>
                        <div class="metric"><div class="metric-label">Write access</div><div class="metric-value ok">OFF</div></div>
                        <div class="metric"><div class="metric-label">Production</div><div class="metric-value ok">OFF</div></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown('<div class="section-label">Inventory</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f'<div class="card"><div class="card-title">Interfaces</div><div class="card-meta">Windows adapter inventory</div><div class="metric-value">{len(adapters)}</div></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="card"><div class="card-title">Addressing</div><div class="card-meta">Observed IPv4 configurations</div><div class="metric-value">{len(ip_config)}</div></div>',
                unsafe_allow_html=True,
            )
        with c3:
            running = sum(1 for x in services if x.get("status") == "Running")
            st.markdown(
                f'<div class="card"><div class="card-title">Services</div><div class="card-meta">Monitored Windows services</div><div class="metric-value">{running}/{len(services)}</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="section-label">Recent state</div>', unsafe_allow_html=True)
        if connectivity:
            st.dataframe(
                [
                    {
                        "Target": x.get("target", "—"),
                        "Result": "PASS" if x.get("ok") else "FAIL",
                        "Latency": x.get("latency", "—"),
                    }
                    for x in connectivity
                ],
                use_container_width=True,
                hide_index=True,
            )

    # TOPOLOGY
    elif page == "Topology":
        header("LAB / TOPOLOGY", "Topology", "Logical structure of the software laboratory.")
        topology()
        st.markdown('<div class="section-label">Layers</div>', unsafe_allow_html=True)
        st.dataframe(
            [
                {"Layer": "Host", "Component": "Windows workstation", "State": "Observed"},
                {"Layer": "Link", "Component": "Network adapters", "State": "Observed"},
                {"Layer": "Network", "Component": "IPv4 / gateway / DNS", "State": "Observed"},
                {"Layer": "Test", "Component": "127.0.0.1", "State": "Tested"},
                {"Layer": "Services", "Component": "DNS Cache / DHCP / NLA", "State": "Observed"},
            ],
            use_container_width=True,
            hide_index=True,
        )

    # INTERFACES
    elif page == "Interfaces":
        header("LAB / INTERFACES", "Interfaces", "Network adapter inventory reported by Windows.")
        st.markdown('<div class="section-label">Adapter inventory</div>', unsafe_allow_html=True)
        st.dataframe(
            [
                {
                    "Interface": x.get("Name", "—"),
                    "State": x.get("Status", "—"),
                    "Link": x.get("LinkSpeed", "—"),
                    "MAC": x.get("MacAddress", "—"),
                }
                for x in adapters
            ],
            use_container_width=True,
            hide_index=True,
        )

    # ADDRESSING
    elif page == "Addressing":
        header("LAB / TCP-IP", "Addressing & DNS", "Observed IPv4 addressing, gateways and DNS configuration.")
        st.markdown('<div class="section-label">IPv4 configuration</div>', unsafe_allow_html=True)
        st.dataframe(
            [
                {
                    "Interface": x.get("interface", "—"),
                    "IPv4": x.get("ipv4", "—"),
                    "Gateway": x.get("gateway", "—"),
                    "DNS": x.get("dns", "—"),
                }
                for x in ip_config
            ],
            use_container_width=True,
            hide_index=True,
        )

    # CONNECTIVITY
    elif page == "Connectivity":
        header("LAB / TESTING", "Connectivity", "Controlled read-only probes against laboratory targets.")
        st.markdown('<div class="section-label">Test results</div>', unsafe_allow_html=True)
        for x in connectivity:
            ok = bool(x.get("ok"))
            with st.container(border=True):
                a, b, c = st.columns([2.2, 1, 1])
                a.markdown(f"**{x.get('target', 'Unknown')}**")
                b.markdown(
                    f'<span class="{"ok" if ok else "bad"}">{ "PASS" if ok else "FAIL"}</span>',
                    unsafe_allow_html=True,
                )
                c.write(x.get("latency", "—"))
        if not connectivity:
            st.info("No laboratory targets configured.")

    # SERVICES
    elif page == "Services":
        header("LAB / SERVICES", "Services", "Windows services relevant to the laboratory environment.")
        st.markdown('<div class="section-label">Service state</div>', unsafe_allow_html=True)
        st.dataframe(
            [
                {
                    "Service": x.get("name", "—"),
                    "State": x.get("status", "—"),
                    "Start type": x.get("startType", "—"),
                }
                for x in services
            ],
            use_container_width=True,
            hide_index=True,
        )

    # DIAGNOSTICS
    elif page == "Diagnostics":
        header("LAB / HEALTH", "Diagnostics", "Runtime and infrastructure health information.")
        status_strip(overall_ok, conn_ok, svc_ok, len(adapters))
        c1, c2 = st.columns(2, gap="large")
        with c1:
            st.markdown('<div class="section-label">Runtime</div>', unsafe_allow_html=True)
            st.json(
                {
                    "PowerShell": health_data.get("powershell"),
                    "Python available": health_data.get("python_available"),
                }
            )
        with c2:
            st.markdown('<div class="section-label">Health response</div>', unsafe_allow_html=True)
            st.json(health_data)

    # EVIDENCE
    elif page == "Evidence":
        header("LAB / EVIDENCE", "Evidence", "Exportable read-only evidence for documentation and troubleshooting.")
        st.markdown('<div class="section-label">Export</div>', unsafe_allow_html=True)
        evidence_data = evidence()
        st.download_button(
            "Download evidence JSON",
            data=json.dumps(evidence_data, indent=2),
            file_name="networklab-evidence.json",
            mime="application/json",
        )
        st.markdown('<div class="section-label">Payload</div>', unsafe_allow_html=True)
        st.json(evidence_data)

    st.markdown(
        f'<div class="footer">NETWORKLAB · {CONFIG.get("environment", "stage-lab")} · READ-ONLY · '
        f'{datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")}</div>',
        unsafe_allow_html=True,
    )

except Exception as exc:
    st.error("NetworkLab backend error")
    st.code(str(exc))
