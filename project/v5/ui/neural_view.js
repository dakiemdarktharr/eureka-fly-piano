import * as THREE from 'three';
import {OrbitControls} from './vendor/OrbitControls.js';
const $=id=>document.getElementById(id);
const palette={DN:0xf6b65d,CPG:0xb49aff,MN:0x62cbed};
export class NeuralView{
 constructor(data,brainData){
  this.data=data;this.selected=0;this.lastFrame=-1;this.lines=[];this.points=[];this.rates=[];
  const el=$('neuralView');this.scene=new THREE.Scene();this.vnc=new THREE.Group();this.scene.add(this.vnc);this.mode="vnc";this.renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,preserveDrawingBuffer:true});this.renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));el.appendChild(this.renderer.domElement);
  const vertices=data.vertices.flat();const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));geo.setIndex(data.faces.flat());geo.computeVertexNormals();geo.computeBoundingBox();const box=geo.boundingBox,size=box.getSize(new THREE.Vector3()),extent=Math.max(size.x,size.y,size.z);
  this.camera=new THREE.PerspectiveCamera(35,1,.1,10000);this.camera.up.set(0,0,1);this.camera.position.set(0,-extent*1.65,extent*.35);this.controls=new OrbitControls(this.camera,this.renderer.domElement);this.controls.enableDamping=true;
  this.surface=new THREE.Mesh(geo,new THREE.MeshBasicMaterial({color:0x7083a9,transparent:true,opacity:.035,side:THREE.DoubleSide,depthWrite:false}));this.vnc.add(this.surface);
  data.neurons.forEach((n,i)=>{const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(n.segments.flat(),3));const line=new THREE.LineSegments(g,new THREE.LineBasicMaterial({color:palette[n.kind],transparent:true,opacity:.12,depthWrite:false}));line.userData.index=i;this.vnc.add(line);this.lines.push(line);
   const dots=new THREE.Points(g,new THREE.PointsMaterial({color:palette[n.kind],size:1.25,sizeAttenuation:true,transparent:true,opacity:.05,depthWrite:false,blending:THREE.AdditiveBlending}));this.vnc.add(dots);this.points.push(dots);
  });
  this.vncCamera=[0,-extent*1.65,extent*.35];this.buildBrain(brainData);
  const resize=()=>{this.renderer.setSize(el.clientWidth,el.clientHeight);this.camera.aspect=el.clientWidth/el.clientHeight;this.camera.updateProjectionMatrix()};new ResizeObserver(resize).observe(el);resize();
  this.ray=new THREE.Raycaster();this.ray.params.Line.threshold=1.5;this.pointer=new THREE.Vector2();
  this.renderer.domElement.addEventListener('click',e=>{const r=el.getBoundingClientRect();this.pointer.set((e.clientX-r.left)/r.width*2-1,1-(e.clientY-r.top)/r.height*2);this.ray.setFromCamera(this.pointer,this.camera);const hit=this.ray.intersectObjects((this.mode==='brain'?this.brainLines:this.lines).filter(l=>l.visible))[0];if(hit){this.select(hit.object.userData.index,false)}});
  for(const id of ['neuralRegion','activeOnly'])$(id).onchange=()=>this.lastFrame=-1;
  $('neuralSurface').onchange=()=>{this.surface.visible=this.brainSurface.visible=$('neuralSurface').checked};
  $('atlasMode').onchange=()=>this.setAtlas($('atlasMode').value);
  data.neurons.forEach((n,i)=>{const o=document.createElement('option');o.value=i;o.textContent=`${n.id} · ${n.type} · ${n.region}`;$('neuronSelect').appendChild(o)});$('neuronSelect').onchange=()=>this.select(Number($('neuronSelect').value),true);this.setAtlas('vnc');
  for(const region of ['neck connective','T1','T2','T3']){const row=document.createElement('div');row.className='regionRow';row.innerHTML=`<span>${region==='neck connective'?'DN / cổ':region}</span><div class="regionTrack"><i></i></div><span class="value">—</span>`;row.dataset.region=region;$('regionRates').appendChild(row)}
 }
 buildBrain(data){
  this.brainGroup=new THREE.Group();this.scene.add(this.brainGroup);this.brainLines=[];const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(data.vertices.flat(),3));g.setIndex(data.faces.flat());
  this.brainSurface=new THREE.Mesh(g,new THREE.MeshBasicMaterial({color:0x748ab7,transparent:true,opacity:.045,side:THREE.DoubleSide,depthWrite:false}));this.brainGroup.add(this.brainSurface);
  const inds=this.data.neurons.map((n,i)=>n.kind==='DN'?i:-1).filter(i=>i>=0);
  data.neurons.forEach((n,i)=>{const positions=[];for(const [a,b] of n.edges)positions.push(...n.vertices[a],...n.vertices[b]);const geom=new THREE.BufferGeometry();geom.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));const line=new THREE.LineSegments(geom,new THREE.LineBasicMaterial({color:i?0xf49bbe:0x65d6fa,transparent:true,opacity:.2,depthWrite:false}));line.userData.index=this.data.neurons.findIndex(x=>x.id===String(n.manc_id));if(line.userData.index<0)throw Error('Missing MANC homolog ID');this.brainGroup.add(line);this.brainLines.push(line)});
 }
 setAtlas(mode){this.mode=mode;$('neuralView').querySelector('.viewhint').textContent=mode==='brain'?'2 DNg100 đồng dạng · kéo xoay · chạm nhánh để chọn neuron':'410 hình thái VNC đã kiểm tra · kéo xoay · chạm nhánh để chọn neuron';if(mode==='brain'&&this.data.neurons[this.selected].kind!=='DN'){this.selected=this.brainLines[0].userData.index;$('neuronSelect').value=this.selected;this.trace();}$('neuralRegion').disabled=mode==='brain';this.vnc.visible=mode==='vnc';this.brainGroup.visible=mode==='brain';this.camera.position.fromArray(mode==='vnc'?this.vncCamera:[0,-660,430]);this.controls.target.set(0,0,0);this.controls.update();this.lastFrame=-1;$('atlasMode').value=mode;$('atlasScope').textContent=mode==='vnc'?'MANC · 410 hình thái ghép đúng bodyId, 412 kênh rate. Hai DN không vẽ do hệ tọa độ nguồn không tương thích.':'FlyWire · bối cảnh toàn não và 2 DNg100 đồng dạng. Tín hiệu chiếu từ MANC khác cá thể và giới tính; các vùng ngoài mô hình không được gán hoạt động.';}
 select(index,switchAtlas){this.selected=index;$('neuronSelect').value=index;if(switchAtlas)this.setAtlas(this.data.neurons[index].kind==='DN'?'brain':'vnc');this.lastFrame=-1;this.trace();}
 bind(replay,frames){
  this.replay=replay;this.frames=frames;const ids=new Map((replay.neuron_ids||[]).map((id,i)=>[String(id),i]));this.mapping=this.data.neurons.map(n=>ids.get(n.id));this.valid=!!replay.layout.neuron_rates&&this.mapping.every(i=>i!==undefined)&&ids.size===this.data.neurons.length;this.lastFrame=-1;
  if(!this.valid){$('activeCount').textContent='Replay thiếu tín hiệu từng neuron';return}
  const canvas=$('neuralHeatmap'),w=Math.min(1000,replay.frame_count),h=this.data.neurons.length;canvas.width=w;canvas.height=h;const ctx=canvas.getContext('2d'),img=ctx.createImageData(w,h),off=replay.layout.neuron_rates[0];
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){const f=Math.round(x/(w-1)*(replay.frame_count-1)),v=Math.min(1,Math.max(0,frames[f*replay.stride+off+this.mapping[y]]/50)),k=(y*w+x)*4;img.data[k]=12+220*v*v;img.data[k+1]=23+218*v;img.data[k+2]=40+180*v;img.data[k+3]=255}ctx.putImageData(img,0,0);this.trace();
 }
 trace(){if(!this.valid)return;const r=this.replay,c=$('neuralTrace'),w=c.clientWidth||300,h=110;c.width=w;c.height=h;const ctx=c.getContext('2d');ctx.fillStyle='#091321';ctx.fillRect(0,0,w,h);ctx.strokeStyle='#77ead3';ctx.beginPath();for(let x=0;x<w;x++){const f=Math.round(x/(w-1)*(r.frame_count-1)),v=this.frames[f*r.stride+r.layout.neuron_rates[0]+this.mapping[this.selected]],y=85-Math.min(1,v/50)*70;x?ctx.lineTo(x,y):ctx.moveTo(x,y)}ctx.stroke();ctx.fillStyle='#9aabc0';ctx.font='10px Segoe UI';ctx.fillText('0',0,104);ctx.fillText(`${r.duration.toFixed(1)} s`,w-48,104);ctx.fillText('50 rate',0,12);}
 update(replay,frames,frame){
  if(this.replay!==replay)this.bind(replay,frames);
  if(this.lastFrame!==frame&&this.valid){this.lastFrame=frame;const off=frame*replay.stride+replay.layout.neuron_rates[0],filter=$('neuralRegion').value,only=$('activeOnly').checked;let active=0,visibleActive=0;const regions={};
   this.data.neurons.forEach((n,i)=>{const value=frames[off+this.mapping[i]],v=Math.max(0,Math.min(1,value/50));this.rates[i]=value;const on=value>replay.activity_threshold,visible=n.coordinate_valid&&(filter==='all'||n.region===filter)&&(!only||on);if(on)active++;if(visible&&on)visibleActive++;this.lines[i].visible=this.points[i].visible=visible;this.lines[i].material.opacity=.035+.75*v;this.points[i].material.opacity=.02+.85*v;this.lines[i].material.color.setHex(i===this.selected?0xffffff:palette[n.kind]);this.points[i].material.size=i===this.selected?2:1.25;const b=regions[n.region]||(regions[n.region]={sum:0,n:0,active:0});b.sum+=value;b.n++;b.active+=on?1:0;
   });
   if(this.mode==='brain')visibleActive=this.brainLines.filter(l=>this.rates[l.userData.index]>1).length;this.brainLines.forEach(l=>{const v=Math.min(1,Math.max(0,this.rates[l.userData.index]/50));l.material.opacity=.04+.96*v;l.visible=!only||this.rates[l.userData.index]>1});
   this.active=active;$('activeCount').textContent=`${active} / ${this.data.neurons.length} active · ${visibleActive} trong view`;
   document.querySelectorAll('.regionRow').forEach(row=>{const b=regions[row.dataset.region];if(!b)return;row.querySelector('i').style.width=`${Math.min(100,b.sum/b.n/50*100)}%`;row.querySelector('.value').textContent=`${b.active}/${b.n} · ${(b.sum/b.n).toFixed(1)}`});
   const n=this.data.neurons[this.selected],v=this.rates[this.selected];$('selectedNeuron').textContent=`${n.type||n.kind} · ${n.id}`;$('neuralValue').textContent=`${n.region} · ${n.side} · ${v.toFixed(3)} đơn vị rate`;$('neuralHover').textContent=`bodyId ${n.id} · ${n.kind} · ${(n.coordinate_valid?n.shown_edges:0).toLocaleString()} / ${n.original_edges.toLocaleString()} nhánh SWC hiển thị · t=${(frame/replay.fps).toFixed(2)} s`;
  }
  if(!this.valid)this.lines.forEach((l,i)=>{l.material.opacity=.06;this.points[i].material.opacity=0});this.controls.update();this.renderer.render(this.scene,this.camera);
 }
}
