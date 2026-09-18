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
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background: #08111f; color: #e7eef8; }
    [data-testid="stSidebar"] { background: #0b1626; }
    .block-container { padding-top: 2rem; max-width: 1500px; }
    .nl-title { font-size: 2rem; font-weight: 700; }
    .nl-kicker { color: #62b0ff; font-size: .78rem; letter-spacing: .12em; }
    .nl-muted { color: #8ea4bb; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("## NETWORKLAB")
st.sidebar.caption("Software-only stage lab")

page = st.sidebar.radio(
    "Workspace",
    [
        "Overview",
        "Adapters",
        "IP Configuration",
        "Connectivity",
        "Services",
        "Diagnostics",
        "Evidence",
    ],
)

if st.sidebar.button("Refresh data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.divider()
st.sidebar.caption("Safety")
st.sidebar.success("READ-ONLY")
st.sidebar.caption("Production network configuration is disabled.")


@st.cache_data(ttl=10)
def state():
    return get_state()


@st.cache_data(ttl=10)
def health():
    return get_health()


@st.cache_data(ttl=30)
def evidence():
    return get_evidence()


def header(title: str, subtitle: str):
    st.markdown(
        f'<div class="nl-kicker">NETWORKLAB · STAGE LAB</div>'
        f'<div class="nl-title">{title}</div>'
        f'<div class="nl-muted">{subtitle}</div>',
        unsafe_allow_html=True,
    )
    st.write("")


try:
    data = state()

    if page == "Overview":
        header(
            "Network Operations Overview",
            "Local Windows network state exposed through the NetworkLab application layer.",
        )
        h = health()
        cols = st.columns(4)
        cols[0].metric("Adapters", len(data.get("adapters", [])))
        cols[1].metric("IPv4 Interfaces", len(data.get("ip", [])))
        cols[2].metric(
            "Connectivity", "PASS" if h.get("connectivity_ok") else "FAIL"
        )
        cols[3].metric(
            "Services",
            f'{h.get("services_running", 0)}/{h.get("services_total", 0)}',
        )

        st.subheader("Environment")
        st.json(
            {
                "project": CONFIG.get("project"),
                "environment": CONFIG.get("environment"),
                "scope": CONFIG.get("scope"),
                "safety": CONFIG.get("safety"),
                "last_refresh": datetime.now().astimezone().isoformat(
                    timespec="seconds"
                ),
            }
        )

    elif page == "Adapters":
        header("Network Adapters", "Current adapter state from Windows.")
        st.dataframe(
            data.get("adapters", []),
            use_container_width=True,
            hide_index=True,
        )

    elif page == "IP Configuration":
        header("IP Configuration", "IPv4, gateway and DNS information.")
        st.dataframe(
            data.get("ip", []),
            use_container_width=True,
            hide_index=True,
        )

    elif page == "Connectivity":
        header("Connectivity", "Configured stage-lab connectivity targets.")
        st.dataframe(
            data.get("connectivity", []),
            use_container_width=True,
            hide_index=True,
        )

    elif page == "Services":
        header("Infrastructure Services", "Windows services relevant to the lab.")
        st.dataframe(
            data.get("services", []),
            use_container_width=True,
            hide_index=True,
        )

    elif page == "Diagnostics":
        header("Diagnostics", "Health and runtime information.")
        h = health()
        st.json(h)
        if h.get("connectivity_ok") and h.get("services_ok"):
            st.success("NetworkLab health checks passed.")
        else:
            st.error("One or more health checks require attention.")

    elif page == "Evidence":
        header(
            "Evidence",
            "Structured read-only evidence generated from the local system.",
        )
        e = evidence()
        st.download_button(
            "Download evidence JSON",
            data=json.dumps(e, indent=2),
            file_name="networklab-evidence.json",
            mime="application/json",
        )
        st.json(e)

except Exception as exc:
    st.error("NetworkLab backend error")
    st.code(str(exc))
    st.caption(
        "The Streamlit application is running, but a Windows diagnostic service failed."
    )
