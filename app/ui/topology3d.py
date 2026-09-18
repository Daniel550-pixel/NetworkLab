from __future__ import annotations

import json
import streamlit.components.v1 as components


def render_topology(data: dict, height: int = 680) -> None:
    """Render the current NetworkLab state as an interactive WebGL topology."""
    payload = json.dumps(data, ensure_ascii=True).replace("</", "<\\/")

    html = f"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
html,body,#scene{{margin:0;width:100%;height:100%;overflow:hidden;background:#071019;font-family:ui-monospace,SFMono-Regular,Consolas,monospace}}
#scene{{position:relative}}
#hud{{position:absolute;left:18px;top:16px;z-index:5;color:#e7eef4;pointer-events:none}}
#hud .title{{font-size:13px;font-weight:800;letter-spacing:.14em}}
#hud .sub{{font-size:10px;color:#8095a5;margin-top:5px}}
#legend{{position:absolute;right:18px;top:16px;z-index:5;color:#8095a5;font-size:10px;line-height:1.8;text-align:right;pointer-events:none}}
#inspect{{position:absolute;right:18px;bottom:18px;width:270px;z-index:5;background:rgba(13,25,35,.94);border:1px solid #1c3342;border-radius:8px;padding:12px;color:#e7eef4;display:none;box-sizing:border-box}}
#inspect .k{{font-size:9px;color:#4bb8ff;letter-spacing:.12em;margin-bottom:5px}}
#inspect .v{{font-size:13px;font-weight:700}}
#inspect .row{{font-size:10px;color:#8095a5;margin-top:7px;white-space:pre-wrap}}
#hint{{position:absolute;left:18px;bottom:16px;color:#5f7484;font-size:9px;z-index:5;pointer-events:none}}
</style>
</head>
<body>
<div id="scene">
  <div id="hud"><div class="title">NETWORKLAB / 3D TOPOLOGY</div><div class="sub">LIVE LOGICAL NETWORK MODEL · READ-ONLY</div></div>
  <div id="legend">DRAG · ORBIT<br>WHEEL · ZOOM<br>CLICK · INSPECT</div>
  <div id="inspect"><div class="k" id="ik"></div><div class="v" id="iv"></div><div class="row" id="ir"></div></div>
  <div id="hint">Telemetry snapshot: {data.get("timestamp","unknown")}</div>
</div>
<script type="module">
import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js";
import {{OrbitControls}} from "https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/controls/OrbitControls.js";

const state = {payload};
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x071019);

const camera = new THREE.PerspectiveCamera(48, innerWidth/innerHeight, .1, 200);
camera.position.set(0, 7, 15);

const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight);
document.getElementById("scene").appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.minDistance = 6;
controls.maxDistance = 35;

scene.add(new THREE.AmbientLight(0x8fb6cc, 1.6));
const key = new THREE.DirectionalLight(0xffffff, 2.2);
key.position.set(4,10,8); scene.add(key);

const grid = new THREE.GridHelper(28,28,0x173244,0x102532);
grid.position.y = -3.2; scene.add(grid);

const nodes = [];
const edges = [];
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();

function material(ok=true, active=false) {{
  return new THREE.MeshStandardMaterial({{
    color: ok ? (active ? 0x4bb8ff : 0x45d39a) : 0xff7070,
    emissive: ok ? (active ? 0x123d5c : 0x103a2a) : 0x4a1212,
    emissiveIntensity: .8,
    metalness:.35, roughness:.42
  }});
}}

function node(name, kind, position, ok=true, detail="") {{
  const group = new THREE.Group();
  const geometry = kind === "HOST"
    ? new THREE.BoxGeometry(2.2,1.15,1.15)
    : new THREE.IcosahedronGeometry(.72,1);
  const mesh = new THREE.Mesh(geometry, material(ok, kind==="HOST"));
  group.add(mesh);
  group.position.set(...position);
  group.userData = {{name,kind,detail,mesh}};
  scene.add(group);
  nodes.push(group);

  const glow = new THREE.PointLight(ok ? 0x45d39a : 0xff7070, .9, 5);
  glow.position.set(0,0,0); group.add(glow);
  return group;
}}

function line(a,b,ok=true) {{
  const geometry = new THREE.BufferGeometry().setFromPoints([a.position,b.position]);
  const material = new THREE.LineBasicMaterial({{color:ok?0x24516b:0x632d35,transparent:true,opacity:.9}});
  const l = new THREE.Line(geometry,material);
  scene.add(l); edges.push({{line:l,a,b,material}});
}}

const adapters = Array.isArray(state.adapters) ? state.adapters : [];
const ip = Array.isArray(state.ip) ? state.ip : [];
const connectivity = Array.isArray(state.connectivity) ? state.connectivity : [];
const services = Array.isArray(state.services) ? state.services : [];

const host = node("Windows Host","HOST",[0,0,0],true,"Environment: "+(state.environment||"stage-lab"));
const interfaceNodes = [];
const radius = 4.3;

adapters.slice(0,8).forEach((a,i) => {{
  const angle = (i/Math.max(adapters.length,1))*Math.PI*2;
  const ok = String(a.Status||"").toLowerCase()==="up";
  const n = node(a.Name||"Interface","INTERFACE",[Math.cos(angle)*radius,0,Math.sin(angle)*radius],ok,
    "Status: "+(a.Status||"unknown")+"\nLink: "+(a.LinkSpeed||"unknown")+"\nMAC: "+(a.MacAddress||"unknown"));
  interfaceNodes.push(n); line(host,n,ok);
}});

const testY = 3.1;
connectivity.slice(0,6).forEach((c,i) => {{
  const x = (i-(Math.min(connectivity.length,6)-1)/2)*3.2;
  const ok = !!c.ok;
  const n = node(c.target||"Target","TEST",[x,testY,0],ok,
    "Result: "+(ok?"PASS":"FAIL")+"\nLatency: "+(c.latency||"unknown"));
  line(host,n,ok);
}});

services.slice(0,6).forEach((s,i) => {{
  const x = (i-(Math.min(services.length,6)-1)/2)*2.5;
  const z = -4.2;
  const ok = String(s.status||"").toLowerCase()==="running";
  const n = node(s.name||"Service","SERVICE",[x,-.2,z],ok,
    "State: "+(s.status||"unknown")+"\nStart type: "+(s.startType||"unknown"));
  line(host,n,ok);
}});

function select(obj) {{
  const d=obj.userData;
  document.getElementById("ik").textContent=d.kind;
  document.getElementById("iv").textContent=d.name;
  document.getElementById("ir").textContent=d.detail || "No additional telemetry.";
  document.getElementById("inspect").style.display="block";
}}

renderer.domElement.addEventListener("pointerdown",(event)=>{{
  const rect=renderer.domElement.getBoundingClientRect();
  pointer.x=((event.clientX-rect.left)/rect.width)*2-1;
  pointer.y=-((event.clientY-rect.top)/rect.height)*2+1;
  raycaster.setFromCamera(pointer,camera);
  const hit=raycaster.intersectObjects(nodes.flatMap(n=>n.children.filter(c=>c.isMesh)),false)[0];
  if(hit) select(hit.object.parent);
}});

function animate(t) {{
  requestAnimationFrame(animate);
  const pulse=(Math.sin(t*.002)+1)/2;
  nodes.forEach(n=>{{ if(n.userData.kind!=="HOST") n.rotation.y += .0015; }});
  edges.forEach(e=>{{ e.material.opacity=.55+pulse*.35; }});
  controls.update();
  renderer.render(scene,camera);
}}
animate(0);

addEventListener("resize",()=>{{
  camera.aspect=innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
}});
</script>
</body>
</html>
"""
    components.html(html, height=height, scrolling=False)
