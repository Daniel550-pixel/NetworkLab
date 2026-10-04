const state = { data:null, health:null, evidence:null, virtualNetwork:null, vms:null, storage:null, readiness:null, architecture:null, connectivity:null, lab:null, verification:null, view:"command" };

const meta = {
  command:["Dashboard","Operational view of the local software network laboratory."],
  topology:["Topology","Logical representation of the observed local network environment."],
  interfaces:["Interfaces","Windows network adapter inventory and state."],
  addressing:["Addressing","Observed IP configuration and addressing data."],
  connectivity:["Connectivity","Connectivity checks and reachability observations."],
  services:["Services","Infrastructure service state reported by the local host."],
  diagnostics:["Diagnostics","Health signals and diagnostic output from the laboratory."],
  evidence:["Evidence","Structured evidence output suitable for stage documentation."],
  "vm-lab":["VM Lab","VirtualBox runtime, storage and boot-state control for the isolated stage laboratory."],
  telemetry:["Telemetry","Continuous VirtualBox health monitoring, incident detection and controlled recovery."],
  architecture:["Architecture","Consolidated control plane, runtime, verification, recovery and evidence architecture."],
  "lab-control":["Lab Control","Provision the host-side lab, inspect roles, and verify the complete build state."],
  "guest-build":["Guest Build","OS-agnostic guest contracts and service validation boundaries for MGMT, INFRA and CLIENT."],
  "evidence-capture":["Evidence","Capture a complete lab snapshot after provisioning and guest validation."]
};

const $ = id => document.getElementById(id);
const arr = value => Array.isArray(value) ? value : [];
const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({ "&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;" }[c]));
const badge = (value, cls="") => '<span class="badge '+cls+'">'+esc(value)+'</span>';

async function post(path, body=null){
  const options={method:"POST",cache:"no-store"};
  if(body){ options.headers={"Content-Type":"application/json"}; options.body=JSON.stringify(body); }
  const response = await fetch(path,options);
  const payload = await response.json();
  if(!response.ok) throw new Error(payload.error || "Request failed");
  return payload;
}

async function get(path){
  const response = await fetch(path,{cache:"no-store"});
  const payload = await response.json();
  if(!response.ok) throw new Error(payload.error || "Request failed");
  return payload;
}

function setStatus(){
  const h = state.health || {};
  const d = state.data || {};
  const adapters = arr(d.adapters);
  const conn = !!h.connectivity_ok;
  const services = !!h.services_ok;
  const operational = conn && services;
  $("lab-status").textContent = operational ? "OPERATIONAL" : "ATTENTION";
  $("lab-status").className = operational ? "ok" : "bad";
  $("connectivity-status").textContent = conn ? "PASS" : "FAIL";
  $("connectivity-status").className = conn ? "ok" : "bad";
  $("services-status").textContent = services ? "HEALTHY" : "ATTENTION";
  $("services-status").className = services ? "ok" : "warn";
  $("interface-count").textContent = adapters.length;
  $("last-updated").textContent = "UPDATED " + new Date().toLocaleTimeString();
}

function table(items, columns){
  if(!items.length) return '<div class="empty">No data returned by the local telemetry layer.</div>';
  return '<div class="card" style="padding:7px"><table><thead><tr>'+columns.map(c=>'<th>'+esc(c.label)+'</th>').join("")+'</tr></thead><tbody>'+
    items.map(item=>'<tr>'+columns.map(c=>'<td>'+esc(typeof c.value==="function"?c.value(item):item[c.key])+'</td>').join("")+'</tr>').join("")+
    '</tbody></table></div>';
}

function topology(){
  return '<div class="topology"><svg viewBox="0 0 900 430" preserveAspectRatio="xMidYMid meet">'+
    '<defs><filter id="glow"><feGaussianBlur stdDeviation="5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'+
    '<line class="edge live" x1="145" y1="215" x2="350" y2="215"/><line class="edge" x1="350" y1="215" x2="550" y2="215"/><line class="edge live" x1="550" y1="215" x2="755" y2="215"/>'+
    '<circle cx="145" cy="215" r="34" fill="#102735" stroke="#55c7ff" filter="url(#glow)"/><circle cx="350" cy="215" r="34" fill="#102735" stroke="#55c7ff"/><circle cx="550" cy="215" r="34" fill="#102735" stroke="#55c7ff"/><circle cx="755" cy="215" r="34" fill="#102735" stroke="#46d7a0" filter="url(#glow)"/>'+
    '<text class="node-text" x="145" y="270" text-anchor="middle">HOST</text><text class="node-sub" x="145" y="287" text-anchor="middle">WINDOWS</text>'+
    '<text class="node-text" x="350" y="270" text-anchor="middle">INTERFACES</text><text class="node-sub" x="350" y="287" text-anchor="middle">NIC LAYER</text>'+
    '<text class="node-text" x="550" y="270" text-anchor="middle">TCP/IP</text><text class="node-sub" x="550" y="287" text-anchor="middle">ADDRESSING</text>'+
    '<text class="node-text" x="755" y="270" text-anchor="middle">LOOPBACK</text><text class="node-sub" x="755" y="287" text-anchor="middle">127.0.0.1</text>'+
    '</svg></div>';
}

function virtualNetworkCard(){
  const n=state.virtualNetwork||{};
  const exists=!!n.exists;
  return '<div class="kv"><b>Segment</b><span>'+esc(n.name||"NetworkLab-Lab")+'</span></div>'+
    '<div class="kv"><b>Subnet</b><span>'+esc(n.network||"192.168.77.0/24")+'</span></div>'+
    '<div class="kv"><b>Host endpoint</b><span>'+esc(n.host_ip||"192.168.77.1")+'</span></div>'+
    '<div class="kv"><b>DHCP</b><span>'+esc(n.dhcp?n.dhcp.lower+"–"+n.dhcp.upper:"192.168.77.100–192.168.77.200")+'</span></div>'+
    '<div class="kv"><b>Status</b><span>'+badge(exists?"READY":"NOT CREATED",exists?"ok":"warn")+'</span></div>'+
    '<button class="button primary" id="create-network">'+(exists?"Reconcile virtual network":"Create virtual network")+'</button>';
}

function vmTopologyCard(){
  const items=arr((state.vms||{}).vms);
  const rows=items.map(vm=>{
    const stateText=vm.exists?String(vm.state||"unknown").toUpperCase():"NOT CREATED";
    const cls=vm.exists && stateText==="RUNNING"?"ok":vm.exists?"warn":"";
    const actions=vm.exists ? '<button class="button" data-vm-action="start" data-vm="'+esc(vm.name)+'">Start</button><button class="button" data-vm-action="stop" data-vm="'+esc(vm.name)+'">Stop</button><button class="button" data-vm-runtime="'+esc(vm.name)+'">Runtime</button>' : '';
    return '<tr><td>'+esc(vm.name)+'</td><td>'+esc(vm.role)+'</td><td>'+badge(stateText,cls)+'</td><td>'+esc(vm.network||"")+'</td><td>'+actions+'</td></tr>';
  }).join("");
  return '<div class="card"><h2>Virtual machine topology</h2><div class="meta">Three lab nodes attached to NetworkLab-Lab</div><div style="overflow:auto"><table><thead><tr><th>VM</th><th>Role</th><th>State</th><th>Network</th><th>Actions</th></tr></thead><tbody>'+(rows||'<tr><td colspan="5">No VM definitions returned.</td></tr>')+'</tbody></table></div><button class="button primary" id="create-vms">Create / reconcile VM topology</button></div>';
}
function storageCard(){
  const items=arr((state.storage||{}).vms);
  const rows=items.map(vm=>{
    const disk=vm.disk ? "ATTACHED" : "NOT CREATED";
    const iso=vm.iso ? "CONFIGURED" : "NOT CONFIGURED";
    const action=vm.iso
      ? "<button class=\"button\" data-iso-eject=\""+esc(vm.name)+"\">Eject ISO</button>"
      : "<button class=\"button\" data-iso-attach=\""+esc(vm.name)+"\">Attach ISO</button>";
    return "<tr><td>"+esc(vm.name)+"</td><td>"+esc(vm.role)+"</td><td>"+badge(disk,disk==="ATTACHED"?"ok":"warn")+"</td><td>"+badge(iso,iso==="CONFIGURED"?"ok":"warn")+"</td><td>"+esc(vm.iso||vm.disk_path||"")+"</td><td>"+action+"</td></tr>";
  }).join("");
  return "<div class=\"card\"><h2>VM storage & OS media</h2><div class=\"meta\">20 GB local VDI storage plus explicit ISO assignment for boot/install preparation.</div><div style=\"overflow:auto\"><table><thead><tr><th>VM</th><th>Role</th><th>Disk</th><th>ISO</th><th>Path</th><th>Action</th></tr></thead><tbody>"+(rows||"<tr><td colspan=\"6\">No VM storage definitions returned.</td></tr>")+"</tbody></table></div><div class=\"storage-actions\"><button class=\"button primary\" id=\"create-storage\">Create / reconcile 20 GB VDI storage</button><div class=\"iso-help\">ISO attachment requires a local .iso path. NetworkLab does not download or select OS media automatically.</div></div></div>";
}
function render(){
  const d=state.data||{}, h=state.health||{}, e=state.evidence||{};
  const telemetry=state.telemetry||{};
  const adapters=arr(d.adapters), ip=arr(d.ip), conn=arr(d.connectivity), services=arr(d.services);
  const view=state.view;
  $("view-title").textContent=meta[view][0]; $("view-subtitle").textContent=meta[view][1];
  let html="";
  if(view==="command"){
    const running=services.filter(x=>String(x.status||"").toLowerCase()==="running").length;
    const vmItems=arr((state.vms||{}).vms);
    const runningVms=vmItems.filter(x=>String(x.state||"").toLowerCase()==="running").length;
    const readiness=state.readiness||{}; const t=state.telemetry||{};
    const verified=state.verification?.verified===true;
    const healthScore=[!!h.connectivity_ok,!!h.services_ok,!!t.healthy,!!readiness.ready,verified].filter(Boolean).length;
    html='<div class="dashboard-hero"><div><div class="eyebrow">NETWORKLAB CONTROL CENTER</div><h2>Laboratory operations</h2><p>Live host, virtualization, network and verification state from the local laboratory.</p></div><div class="hero-state">'+badge(healthScore>=4?"STABLE":healthScore>=2?"DEGRADED":"ATTENTION",healthScore>=4?"ok":healthScore>=2?"warn":"bad")+'<span>'+healthScore+'/5 control gates</span></div></div>'+
    '<div class="grid four dashboard-metrics">'+[['Lab health',healthScore+'/5'],['VM runtime',runningVms+'/'+vmItems.length],['Readiness',String(readiness.completed??0)+'/'+String(readiness.total??0)],['Services',running+'/'+services.length]].map(x=>'<div class="metric"><label>'+x[0]+'</label><strong>'+esc(x[1])+'</strong></div>').join("")+'</div>'+
    '<div class="dashboard-section"><div class="section-heading"><div><div class="eyebrow">OPERATIONS</div><h3>Current system state</h3></div><span class="section-note">AUTO REFRESH 10S</span></div><div class="grid three">'+
    '<div class="card state-card"><div class="state-icon">01</div><div><b>Connectivity</b><span>'+badge(h.connectivity_ok?"PASS":"FAIL",h.connectivity_ok?"ok":"bad")+'</span></div><p>Host reachability and local network checks.</p></div>'+
    '<div class="card state-card"><div class="state-icon">02</div><div><b>VirtualBox telemetry</b><span>'+badge(t.healthy?"HEALTHY":"ATTENTION",t.healthy?"ok":"warn")+'</span></div><p>'+esc(t.active_incident?"Active incident detected.":"No active incident.")+'</p></div>'+
    '<div class="card state-card"><div class="state-icon">03</div><div><b>Verification</b><span>'+badge(verified?"VERIFIED":"PENDING",verified?"ok":"warn")+'</span></div><p>Lab verification gate across infrastructure and runtime.</p></div></div></div>'+
    '<div class="grid two dashboard-section"><div class="card"><div class="eyebrow">VIRTUALIZATION</div><h2>Lab nodes</h2><div class="meta">Runtime state of the defined laboratory VMs.</div>'+vmTopologyCard()+'</div><div class="card"><div class="eyebrow">NETWORK</div><h2>NetworkLab-Lab</h2><div class="meta">Host-only segment and control path.</div>'+virtualNetworkCard()+'</div></div>'+
    '<div class="grid two dashboard-section"><div class="card"><div class="eyebrow">READINESS</div><h2>Build progression</h2><div class="readiness-mini">'+arr(readiness.steps).map((x,i)=>'<div class="'+(x.ready?"ready":"pending")+'"><span>0'+(i+1)+'</span><b>'+esc(x.label)+'</b></div>').join("")+'</div></div>'+
    '<div class="card"><div class="eyebrow">OPERATIONS</div><h2>Quick navigation</h2><div class="quick-actions"><button class="button primary" data-nav-view="vm-lab">Open VM Lab</button><button class="button" data-nav-view="guest-build">Guest Build</button><button class="button" data-nav-view="telemetry">Telemetry</button><button class="button" data-nav-view="evidence-capture">Capture Evidence</button></div></div></div>';
  } else if(view==="topology"){
    html='<div class="card"><h2>Network topology</h2><div class="meta">Pure SVG visualization — no external 3D or frontend service required</div>'+topology()+'</div>';
  } else if(view==="interfaces"){
    html='<div class="section">ADAPTER INVENTORY</div>'+table(adapters,[{label:"Name",key:"name"},{label:"Status",key:"status"},{label:"Description",key:"description"},{label:"MAC",key:"mac"}]);
  } else if(view==="addressing"){
    html='<div class="section">IP CONFIGURATION</div>'+table(ip,[{label:"Interface",key:"interface"},{label:"Address",key:"address"},{label:"Prefix",key:"prefix"},{label:"Gateway",key:"gateway"}]);
  } else if(view==="connectivity"){
    html='<div class="section">CONNECTIVITY OBSERVATIONS</div>'+table(conn,[{label:"Target",key:"target"},{label:"Status",value:x=>x.status||x.result||""},{label:"Latency",value:x=>x.latency_ms??x.latency??""},{label:"Details",value:x=>x.message||x.details||""}]);
  } else if(view==="services"){
    html='<div class="section">SERVICE INVENTORY</div>'+table(services,[{label:"Name",key:"name"},{label:"Status",value:x=>x.status||""},{label:"Start mode",value:x=>x.start_type||x.startMode||""},{label:"Details",value:x=>x.display_name||x.description||""}]);
  } else if(view==="diagnostics"){
    html='<div class="grid three">'+
      '<div class="metric"><label>Connectivity</label><strong class="'+(h.connectivity_ok?"ok":"bad")+'">'+(h.connectivity_ok?"PASS":"FAIL")+'</strong></div>'+
      '<div class="metric"><label>Services</label><strong class="'+(h.services_ok?"ok":"warn")+'">'+(h.services_ok?"HEALTHY":"ATTENTION")+'</strong></div>'+
      '<div class="metric"><label>Telemetry</label><strong class="ok">LIVE</strong></div></div>'+
      '<div class="card" style="margin-top:15px"><h2>Health payload</h2><div class="meta">Raw diagnostic result from PowerShell</div><pre>'+esc(JSON.stringify(h,null,2))+'</pre></div>';
  } else if(view==="evidence"){
    html='<div class="grid two"><div class="card"><h2>Evidence package</h2><div class="meta">Current structured evidence returned by the local evidence service</div><pre>'+esc(JSON.stringify(e,null,2))+'</pre></div>'+
      '<div class="card"><h2>Export</h2><div class="meta">Save the current evidence payload locally.</div><button class="button primary" id="download">Download JSON</button></div></div>';
  } else if(view==="lab-control"){
    const lab=state.lab||{};
    const def=lab.definition||{};
    const roles=arr(def.roles);
    const checks=arr((state.verification||{}).checks);
    html='<div class="grid four">'+
      [['Lab',def.lab_id||"—"],['Network',lab.network?.ready?"READY":"ATTENTION"],['VMs',String((lab.topology?.vms||[]).filter(x=>x.exists).length)+"/3"],['Storage',String((lab.storage?.vms||[]).filter(x=>x.disk).length)+"/3"]].map(x=>'<div class="metric"><label>'+esc(x[0])+'</label><strong>'+esc(x[1])+'</strong></div>').join("")+
      '</div><div class="grid two" style="margin-top:15px"><div class="card"><div class="eyebrow">HOST BUILD</div><h2>Lab provisioning</h2><div class="meta">Creates only the host-side network, VM topology and storage. OS media remains manual.</div><div class="vm-actions"><button class="button primary" id="prepare-lab">Prepare lab</button><button class="button" id="verify-lab">Verify lab</button></div><pre id="lab-result">'+esc(JSON.stringify(lab.readiness||{},null,2))+'</pre></div><div class="card"><div class="eyebrow">ROLE MAP</div><h2>Guest architecture</h2><table><thead><tr><th>VM</th><th>Role</th><th>Purpose</th><th>Recommended IP</th></tr></thead><tbody>'+roles.map(x=>'<tr><td>'+esc(x.hostname)+'</td><td>'+esc(x.role)+'</td><td>'+esc(x.purpose)+'</td><td>'+esc(x.recommended_ip)+'</td></tr>').join("")+'</tbody></table></div></div>'+
      '<div class="card" style="margin-top:15px"><div class="eyebrow">VERIFICATION GATES</div><h2>Build status</h2><table><thead><tr><th>Gate</th><th>Status</th></tr></thead><tbody>'+checks.map(x=>'<tr><td>'+esc(x.label)+'</td><td>'+badge(x.passed?"PASS":"ATTENTION",x.passed?"ok":"warn")+'</td></tr>').join("")+'</tbody></table></div>';
  } else if(view==="guest-build"){
    const contracts=arr((state.guestContracts||{}).contracts);
    const validation=state.guestValidation||{};
    const endpointRows=arr(validation.endpoints).map(x=>'<tr><td>'+esc(x.role)+'</td><td>'+esc(x.ip)+'</td><td>'+badge(x.icmp?.reachable?"REACHABLE":"NOT REACHABLE",x.icmp?.reachable?"ok":"warn")+'</td><td>'+esc(x.expected_services?.dns?.reachable===true?"DNS OPEN":x.expected_services?.dns?.skipped?"—":"DNS NOT OPEN")+'</td></tr>').join("");
    html='<div class="card"><div class="eyebrow">GUEST CONTRACTS</div><h2>OS-agnostic role definitions</h2><div class="meta">The host prepares the VM boundary; guest OS installation remains explicit and manual.</div><table><thead><tr><th>Role</th><th>VM</th><th>IP</th><th>Services</th><th>Validation</th></tr></thead><tbody>'+contracts.map(x=>'<tr><td>'+esc(x.role)+'</td><td>'+esc(x.vm)+'</td><td>'+esc(x.recommended_ip)+'</td><td>'+esc(x.services.join(", "))+'</td><td>'+esc(x.validation.join(", "))+'</td></tr>').join("")+'</tbody></table></div>'+
    '<div class="card" style="margin-top:15px"><div class="eyebrow">HOST-ASSISTED VALIDATION</div><h2>Guest endpoint probes</h2><div class="meta">ICMP and selected TCP probes are observational; guest-to-guest checks require installed/configured guests.</div><table><thead><tr><th>Role</th><th>IP</th><th>ICMP</th><th>DNS</th></tr></thead><tbody>'+endpointRows+'</tbody></table><button class="button primary" id="refresh-guest">Run guest validation</button></div>'+
    '<div class="card" style="margin-top:15px"><div class="eyebrow">BOUNDARY</div><h2>Manual guest configuration</h2><pre>'+esc(JSON.stringify({os_selection:"manual",next:["Install selected OS ISO","Apply role contract","Configure services","Run validation","Capture evidence"]},null,2))+'</pre></div>';
  } else if(view==="evidence-capture"){
    html='<div class="card"><div class="eyebrow">EVIDENCE PIPELINE</div><h2>Capture complete laboratory snapshot</h2><div class="meta">Stores verification, guest contracts, connectivity and VirtualBox telemetry as a timestamped JSON artifact.</div><button class="button primary" id="capture-evidence">Capture evidence</button><pre id="capture-result">Ready.</pre></div>';
  } else if(view==="architecture"){
    const a=state.architecture||{};
    const layers=arr(a.layers);
    const layerRows=layers.map(x=>"<tr><td>"+esc(x.name)+"</td><td>"+badge(String(x.status||"unknown").toUpperCase(),x.status==="ready"?"ok":"warn")+"</td><td>"+esc(x.purpose)+"</td></tr>").join("");
    const pipeline=arr(a.pipeline).map((x,i)=>"<div class=\"life-step done\"><span>0"+(i+1)+"</span><b>"+esc(x)+"</b><small>CONTROL PLANE</small></div>").join("");
    const conn=state.connectivity||{};
    html="<div class=\"grid four\">"+
      [["Mode",a.mode||"—"],["Network",a.network?.ready?"READY":"ATTENTION"],["Readiness",a.readiness?.ready?"READY":"ATTENTION"],["Telemetry",a.telemetry?.healthy?"HEALTHY":"ATTENTION"]].map(x=>"<div class=\"metric\"><label>"+esc(x[0])+"</label><strong>"+esc(x[1])+"</strong></div>").join("")+
      "</div><div class=\"card\" style=\"margin-top:15px\"><div class=\"eyebrow\">SYSTEM ARCHITECTURE</div><h2>NetworkLab control plane</h2><div class=\"meta\">"+esc(a.principle||"observe -> decide -> safely execute -> verify -> record")+"</div><table><thead><tr><th>Layer</th><th>Status</th><th>Purpose</th></tr></thead><tbody>"+(layerRows||"<tr><td colspan=\"3\">No architecture state returned.</td></tr>")+"</tbody></table></div>"+
      "<div class=\"card\" style=\"margin-top:15px\"><div class=\"eyebrow\">EXECUTION PIPELINE</div><h2>Operational sequence</h2><div class=\"lifecycle\">"+pipeline+"</div><div class=\"vm-actions\"><button class=\"button primary\" id=\"run-audit\">Run full architecture audit</button></div></div>"+
      "<div class=\"grid two\" style=\"margin-top:15px\"><div class=\"card\"><div class=\"eyebrow\">CONNECTIVITY GATE</div><h2>Read-only reachability</h2><div class=\"kv\"><b>Status</b><span>"+badge(conn.reachable?"PASS":"ATTENTION",conn.reachable?"ok":"warn")+"</span></div><pre>"+esc(JSON.stringify(conn.targets||[],null,2))+"</pre></div><div class=\"card\"><div class=\"eyebrow\">VM RECOVERY</div><h2>Autonomous boundary</h2><pre>"+esc(JSON.stringify(a.telemetry||{},null,2))+"</pre></div></div>";
  } else if(view==="telemetry"){
    const t=telemetry;
    const recommendation=t.recommendation||{};
    const healthy=!!t.healthy;
    const history=arr(t.history);
    const failures=arr(t.last_error);
    const processRows=Object.entries(t.processes||{}).map(([name,item])=>`<tr><td>${esc(name)}</td><td>${item.running?badge("RUNNING","ok"):badge("NOT RUNNING")}</td></tr>`).join("");
    const historyRows=history.slice(0,12).map(item=>`<tr><td>${esc(new Date(item.timestamp).toLocaleTimeString())}</td><td>${esc(item.event)}</td><td>${esc(item.classification||item.message||item.stage||"")}</td></tr>`).join("");
    html=`<div class="grid four">
      <div class="metric"><label>Engine</label><strong class="${healthy?"ok":"bad"}">${healthy?"HEALTHY":"ATTENTION"}</strong></div>
      <div class="metric"><label>Failures</label><strong>${esc(t.consecutive_failures||0)}</strong></div>
      <div class="metric"><label>Repairs</label><strong>${esc(t.repair_count||0)}</strong></div>
      <div class="metric"><label>Incident</label><strong class="${t.active_incident?"warn":"ok"}">${t.active_incident?"ACTIVE":"CLEAR"}</strong></div>
    </div>
    <div class="grid two" style="margin-top:15px">
      <div class="card"><div class="eyebrow">AUTONOMOUS RECOVERY</div><h2>VirtualBox control plane</h2><div class="meta">Safe recovery only: running VMs are never terminated by the repair engine.</div>
        <div class="kv"><b>Status</b><span>${badge(t.status||"UNKNOWN",healthy?"ok":t.status==="degraded"?"warn":"bad")}</span></div>
        <div class="kv"><b>Classification</b><span>${esc((t.probe||{}).classification||"—")}</span></div>
        <div class="kv"><b>Last check</b><span>${esc(t.last_check||"—")}</span></div>
        <div class="kv"><b>Last repair</b><span>${esc(t.last_repair||"—")}</span></div>
        <div class="kv"><b>Repair threshold</b><span>${esc(t.policy?.repair_threshold??"—")} failures</span></div><div class="kv"><b>Cooldown</b><span>${esc(t.policy?.repair_cooldown_seconds??"—")} seconds</span></div>
        <div class="vm-actions"><button class="button primary" id="telemetry-repair">Run controlled repair</button><button class="button" id="telemetry-refresh">Probe now</button></div>
      </div>
      <div class="card"><div class="eyebrow">RECOVERY INTELLIGENCE</div><h2>Next action</h2><div class="meta">Generated from the detected failure class and the safe recovery boundary.</div>\n        <div class="kv"><b>Priority</b><span>${esc(recommendation?.priority||"—")}</span></div>\n        <div class="kv"><b>Action</b><span>${esc(recommendation?.action||"No active recommendation.")}</span></div>\n        <div class="kv"><b>Reason</b><span>${esc(recommendation?.reason||"—")}</span></div>\n        <div class="kv"><b>Persistent ledger</b><span>${esc(t.incident_log_path||"—")}</span></div>\n      </div>\n      <div class="card"><div class="eyebrow">PROCESS SAFETY</div><h2>VirtualBox process state</h2><div class="meta">Diagnostic snapshot used before automatic recovery.</div><table><thead><tr><th>Process</th><th>State</th></tr></thead><tbody>${processRows||"<tr><td colspan=\"2\">No process snapshot yet.</td></tr>"}</tbody></table></div>
    </div>
    <div class="grid two" style="margin-top:15px">
      <div class="card"><div class="eyebrow">ACTIVE INCIDENT</div><h2>Latest fault</h2><pre>${esc(JSON.stringify(failures||t.last_error||"No active error",null,2))}</pre></div>
      <div class="card"><div class="eyebrow">EVENT LEDGER</div><h2>Recovery history</h2><div style="overflow:auto"><table><thead><tr><th>Time</th><th>Event</th><th>Detail</th></tr></thead><tbody>${historyRows||"<tr><td colspan=\"3\">No events recorded.</td></tr>"}</tbody></table></div></div>
    </div>`;
  } else if(view==="vm-lab"){
    const vmItems=arr((state.vms||{}).vms);
    const storageItems=arr((state.storage||{}).vms);
    const readiness=state.readiness||{};
    const steps=arr(readiness.steps);
    const readinessClass=readiness.ready?"ok":readiness.completed>0?"warn":"bad";
    const readinessLabel=readiness.ready?"LAB READY":readiness.completed+"/"+readiness.total+" READY";
    const readinessSteps=steps.map((step,index)=>{
      const cls=step.ready?"done":"pending";
      const status=step.ready?"READY":"PENDING";
      return '<div class="readiness-step '+cls+'"><span class="readiness-index">0'+(index+1)+'</span><div><b>'+esc(step.label)+'</b><small>'+status+'</small></div></div>';
    }).join("");
    const nextLabel=readiness.next_step ? (steps.find(x=>x.id===readiness.next_step)||{}).label : "None";
    html='<div class="card readiness-card"><div class="readiness-head"><div><div class="eyebrow">INSTALLATION / READINESS CONTROL</div><h2>Lab readiness</h2><div class="meta">Live validation of the required NetworkLab provisioning chain.</div></div>'+badge(readinessLabel,readinessClass)+'</div>'+
      '<div class="readiness-track">'+readinessSteps+'</div>'+
      '<div class="readiness-footer"><span><b>Next required:</b> '+esc(nextLabel)+'</span><span><b>OS media:</b> explicit ISO selection only</span></div></div>'+
    '<div class="grid three">'+vmItems.map(vm=>{
      const storage=storageItems.find(x=>x.name===vm.name)||{};
      const runtimeState=String(vm.state||"unknown").toUpperCase();
      const runtimeClass=runtimeState==="RUNNING"?"ok":runtimeState==="POWERED OFF"?"warn":"";
      return '<div class="card vm-card"><div class="vm-head"><div><div class="eyebrow">'+esc(vm.role)+'</div><h2>'+esc(vm.name)+'</h2></div>'+badge(runtimeState,runtimeClass)+'</div>'+
        '<div class="kv"><b>CPU / RAM</b><span>'+esc(vm.cpus)+' vCPU / '+esc(vm.memory)+' MB</span></div>'+
        '<div class="kv"><b>NIC</b><span>'+esc(vm.nic1||"—")+'</span></div>'+
        '<div class="kv"><b>Host-only</b><span>'+esc(vm.host_only_adapter||"—")+'</span></div>'+
        '<div class="kv"><b>Disk</b><span>'+esc(storage.disk_path||"Not provisioned")+'</span></div>'+
        '<div class="kv"><b>ISO</b><span>'+esc(storage.iso||"None attached")+'</span></div>'+
        '<div class="vm-actions"><button class="button" data-vm-action="start" data-vm="'+esc(vm.name)+'">Start</button><button class="button" data-vm-action="stop" data-vm="'+esc(vm.name)+'">Stop</button><button class="button danger" data-vm-action="poweroff" data-vm="'+esc(vm.name)+'">Power off</button><button class="button primary" data-vm-runtime="'+esc(vm.name)+'">Inspect runtime</button></div></div>';
    }).join('')+'</div>'+
    '<div class="card" style="margin-top:15px"><h2>Lab lifecycle</h2><div class="meta">Provision in order: virtual network → VM topology → 20 GB storage → OS ISO → boot → runtime inspection.</div>'+
    '<div class="lifecycle"><div class="life-step '+(steps.find(x=>x.id==="network")?.ready?"done":"")+'"><span>01</span><b>Host-only network</b><small>'+esc((state.virtualNetwork||{}).name||"NetworkLab-Lab")+'</small></div>'+
    '<div class="life-step '+(steps.find(x=>x.id==="vms")?.ready?"done":"")+'"><span>02</span><b>VM topology</b><small>'+vmItems.filter(x=>x.exists).length+'/3 registered</small></div>'+
    '<div class="life-step '+(steps.find(x=>x.id==="storage")?.ready?"done":"")+'"><span>03</span><b>Storage</b><small>'+storageItems.filter(x=>x.disk).length+'/3 disks</small></div>'+
    '<div class="life-step '+(steps.find(x=>x.id==="media")?.ready?"done":"")+'"><span>04</span><b>OS media</b><small>'+storageItems.filter(x=>x.iso).length+'/3 ISO mounts</small></div></div></div>';
  }
  $("content").innerHTML=html;
  bindLabControl();
  const runAudit=$("run-audit");
  if(runAudit) runAudit.onclick=async()=>{
    runAudit.disabled=true; runAudit.textContent="AUDITING...";
    try { const audit=await get("/api/orchestrator/audit"); state.architecture=audit.architecture; state.connectivity=audit.connectivity; state.readiness=audit.readiness; state.telemetry=audit.telemetry; render(); }
    catch(error){ $("alert").textContent="ARCHITECTURE AUDIT ERROR: "+error.message; $("alert").classList.remove("hidden"); }
    finally { runAudit.disabled=false; runAudit.textContent="Run full architecture audit"; }
  };
  const telemetryRepair=$("telemetry-repair");
  if(telemetryRepair) telemetryRepair.onclick=async()=>{
    telemetryRepair.disabled=true; telemetryRepair.textContent="REPAIRING...";
    try { state.telemetry=await post("/api/vm/telemetry/repair"); render(); }
    catch(error){ $("alert").textContent="VIRTUALBOX REPAIR ERROR: "+error.message; $("alert").classList.remove("hidden"); telemetryRepair.disabled=false; telemetryRepair.textContent="Retry"; }
  };
  const telemetryRefresh=$("telemetry-refresh");
  if(telemetryRefresh) telemetryRefresh.onclick=loadTelemetry;
  const createStorage=$("create-storage");
  if(createStorage) createStorage.onclick=async()=>{
    createStorage.disabled=true; createStorage.textContent="PROVISIONING...";
    try{ state.storage=await post("/api/vms/storage/create"); render(); }
    catch(error){ $("alert").textContent="VM STORAGE ERROR: "+error.message; $("alert").classList.remove("hidden"); createStorage.disabled=false; createStorage.textContent="Retry"; }
  };
  document.querySelectorAll("[data-iso-attach]").forEach(button=>button.onclick=async()=>{
    const name=button.dataset.isoAttach;
    const path=window.prompt("Local ISO path for "+name+":");
    if(!path) return;
    button.disabled=true; button.textContent="ATTACHING...";
    try{ state.storage=await post("/api/vms/"+encodeURIComponent(name)+"/iso",{path}); render(); }
    catch(error){ $("alert").textContent="ISO ATTACH ERROR: "+error.message; $("alert").classList.remove("hidden"); button.disabled=false; button.textContent="Retry"; }
  });
  document.querySelectorAll("[data-iso-eject]").forEach(button=>button.onclick=async()=>{
    const name=button.dataset.isoEject;
    button.disabled=true; button.textContent="EJECTING...";
    try{ state.storage=await post("/api/vms/"+encodeURIComponent(name)+"/iso",{action:"eject"}); render(); }
    catch(error){ $("alert").textContent="ISO EJECT ERROR: "+error.message; $("alert").classList.remove("hidden"); button.disabled=false; button.textContent="Retry"; }
  });
  const createVMs=$("create-vms");
  if(createVMs) createVMs.onclick=async()=>{
    createVMs.disabled=true; createVMs.textContent="BUILDING...";
    try{ state.vms=await post("/api/vms/create"); render(); }
    catch(error){ $("alert").textContent="VM TOPOLOGY ERROR: "+error.message; $("alert").classList.remove("hidden"); createVMs.disabled=false; createVMs.textContent="Retry"; }
  };
  document.querySelectorAll("[data-vm-runtime]").forEach(button=>button.onclick=async()=>{
    const name=button.dataset.vmRuntime;
    try{
      const runtime=await get("/api/vms/"+encodeURIComponent(name)+"/runtime");
      const boot=runtime.boot_order.join(" > ").toUpperCase();
      $("alert").textContent=name+" | STATE: "+runtime.state.toUpperCase()+" | BOOT: "+boot+" | NIC: "+runtime.nic1;
      $("alert").classList.remove("hidden");
    }catch(error){
      $("alert").textContent="VM RUNTIME ERROR: "+error.message;
      $("alert").classList.remove("hidden");
    }
  });
  document.querySelectorAll("[data-vm-action]").forEach(button=>button.onclick=async()=>{
    button.disabled=true;
    try{ state.vms=await post("/api/vms/"+encodeURIComponent(button.dataset.vm)+"/"+button.dataset.vmAction); render(); }
    catch(error){ $("alert").textContent="VM ACTION ERROR: "+error.message; $("alert").classList.remove("hidden"); button.disabled=false; }
  });
  const createNetwork=$("create-network");
  if(createNetwork) createNetwork.onclick=async()=>{
    createNetwork.disabled=true; createNetwork.textContent="BUILDING...";
    try{ state.virtualNetwork=await post("/api/virtual-network/create"); render(); }
    catch(error){ $("alert").textContent="VIRTUAL NETWORK ERROR: "+error.message; $("alert").classList.remove("hidden"); createNetwork.disabled=false; createNetwork.textContent="Retry"; }
  };
  const refreshGuest=$("refresh-guest");
  if(refreshGuest) refreshGuest.onclick=async()=>{ refreshGuest.disabled=true; refreshGuest.textContent="VALIDATING..."; try{ state.guestValidation=await get("/api/guest/validation"); render(); } catch(error){ $("alert").textContent="GUEST VALIDATION ERROR: "+error.message; $("alert").classList.remove("hidden"); refreshGuest.disabled=false; refreshGuest.textContent="Retry"; } };
  const captureEvidence=$("capture-evidence");
  if(captureEvidence) captureEvidence.onclick=async()=>{ captureEvidence.disabled=true; captureEvidence.textContent="CAPTURING..."; try{ const x=await post("/api/evidence/capture",{}); const result=$("capture-result"); if(result) result.textContent=JSON.stringify({captured:x.captured,path:x.path},null,2); } catch(error){ const result=$("capture-result"); if(result) result.textContent="ERROR: "+error.message; } finally { captureEvidence.disabled=false; captureEvidence.textContent="Capture evidence"; } };
  const download=$("download");
  if(download) download.onclick=()=>{const blob=new Blob([JSON.stringify(state.evidence,null,2)],{type:"application/json"});const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="networklab-evidence.json";a.click();URL.revokeObjectURL(a.href)};
}

async function loadTelemetry(){
  try { state.telemetry=await get("/api/vm/telemetry"); } catch(error) { state.telemetry={status:"failed",healthy:false,last_error:error.message}; }
  if(state.view==="telemetry") render();
}

async function load(){
  $("alert").classList.add("hidden");
  try{
    const [data,health,evidence,virtualNetwork,vms,storage,readiness,telemetry,architecture,connectivity,lab,verification,guestContracts,guestValidation]=await Promise.all([get("/api/state"),get("/api/health"),get("/api/evidence"),get("/api/virtual-network"),get("/api/vms"),get("/api/vms/storage"),get("/api/vm/readiness"),get("/api/vm/telemetry"),get("/api/architecture"),get("/api/connectivity"),get("/api/lab/state"),get("/api/lab/verify"),get("/api/guest/contracts"),get("/api/guest/validation")]);
    state.data=data; state.health=health; state.evidence=evidence; state.virtualNetwork=virtualNetwork; state.vms=vms; state.storage=storage; state.readiness=readiness; state.telemetry=telemetry; state.architecture=architecture; state.connectivity=connectivity; state.lab=lab; state.verification=verification; state.guestContracts=guestContracts; state.guestValidation=guestValidation; setStatus(); render();
  }catch(error){
    $("alert").textContent="LOCAL TELEMETRY ERROR: "+error.message;
    $("alert").classList.remove("hidden");
  }
}

document.querySelectorAll(".nav-item").forEach(button=>button.addEventListener("click",()=>{
  document.querySelectorAll(".nav-item").forEach(x=>x.classList.remove("active"));
  button.classList.add("active"); state.view=button.dataset.view; render();
}));
$("refresh").addEventListener("click",load);
load();
setInterval(load,10000);


async function bindLabControl(){
  const prepare=$("prepare-lab"), verify=$("verify-lab"), result=$("lab-result");
  if(prepare) prepare.onclick=async()=>{
    prepare.disabled=true; prepare.textContent="PREPARING...";
    try { const x=await post("/api/lab/prepare",{}); state.lab=x; state.readiness=x.readiness; result.textContent=JSON.stringify(x,null,2); }
    catch(error){ result.textContent="ERROR: "+error.message; }
    finally { prepare.disabled=false; prepare.textContent="Prepare lab"; }
  };
  if(verify) verify.onclick=async()=>{
    verify.disabled=true; verify.textContent="VERIFYING...";
    try { const x=await get("/api/lab/verify"); state.verification=x; result.textContent=JSON.stringify(x,null,2); }
    catch(error){ result.textContent="ERROR: "+error.message; }
    finally { verify.disabled=false; verify.textContent="Verify lab"; }
  };
}

