const state = { data:null, health:null, evidence:null, virtualNetwork:null, vms:null, storage:null, readiness:null, view:"command" };

const meta = {
  command:["Command Center","Operational view of the local software network laboratory."],
  topology:["Topology","Logical representation of the observed local network environment."],
  interfaces:["Interfaces","Windows network adapter inventory and state."],
  addressing:["Addressing","Observed IP configuration and addressing data."],
  connectivity:["Connectivity","Connectivity checks and reachability observations."],
  services:["Services","Infrastructure service state reported by the local host."],
  diagnostics:["Diagnostics","Health signals and diagnostic output from the laboratory."],
  evidence:["Evidence","Structured evidence output suitable for stage documentation."],
  "vm-lab":["VM Lab","VirtualBox runtime, storage and boot-state control for the isolated stage laboratory."],
  telemetry:["Self-Healing Telemetry","Continuous VirtualBox health monitoring, incident detection and controlled recovery."]
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
    html='<div class="grid four">'+
      [['Interfaces',adapters.length],['IPv4 configurations',ip.length],['Connectivity tests',conn.length],['Running services',running+'/'+services.length]].map(x=>'<div class="metric"><label>'+x[0]+'</label><strong>'+esc(x[1])+'</strong></div>').join("")+
      '</div><div class="grid two" style="margin-top:15px"><div class="card"><h2>Virtual network</h2><div class="meta">Managed directly by the NetworkLab application</div>'+virtualNetworkCard()+'</div><div class="card"><h2>Logical network path</h2><div class="meta">Local telemetry model</div>'+topology()+'</div>'+
      '<div style="grid-column:1 / -1">'+vmTopologyCard()+'</div><div style="grid-column:1 / -1">'+storageCard()+'</div><div class="card"><h2>Execution boundary</h2><div class="meta">Current laboratory safety model</div>'+
      '<div class="kv"><b>Environment</b><span>Software laboratory</span></div><div class="kv"><b>Write operations</b><span>'+badge("DISABLED")+'</span></div><div class="kv"><b>Production assumptions</b><span>'+badge("NONE")+'</span></div><div class="kv"><b>Server</b><span>127.0.0.1:8501</span></div></div></div>';
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
  } else if(view==="telemetry"){
    const t=telemetry;
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
      <div class="card"><div class="eyebrow">PROCESS SAFETY</div><h2>VirtualBox process state</h2><div class="meta">Diagnostic snapshot used before automatic recovery.</div><table><thead><tr><th>Process</th><th>State</th></tr></thead><tbody>${processRows||"<tr><td colspan=\"2\">No process snapshot yet.</td></tr>"}</tbody></table></div>
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
    const [data,health,evidence,virtualNetwork,vms,storage,readiness,telemetry]=await Promise.all([get("/api/state"),get("/api/health"),get("/api/evidence"),get("/api/virtual-network"),get("/api/vms"),get("/api/vms/storage"),get("/api/vm/readiness"),get("/api/vm/telemetry")]);
    state.data=data; state.health=health; state.evidence=evidence; state.virtualNetwork=virtualNetwork; state.vms=vms; state.storage=storage; state.readiness=readiness; state.telemetry=telemetry; setStatus(); render();
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
