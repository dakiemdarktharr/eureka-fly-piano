"""Build the v4 viewer from the preserved v3 rendering primitives."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent;old=ROOT.parent/'v3/ui/viewer';ui=ROOT/'ui';ui.mkdir(exist_ok=True)
h=(old/'index.html').read_text(encoding='utf8')
h=h.replace('V3 · LOCAL','V4 · LEARNING LAB').replace('Quan sát một chuỗi vận động.','Học tiếp xúc. Đo từng nốt.').replace('Cơ thể NeuroMechFly, phím đàn vật lý và hoạt động mạng 412 neuron.','49 tham số được tối ưu, gồm 24 hệ số synapse và 6 hệ số kích thích MN. Bộ lập lịch và IK vẫn là hỗ trợ kỹ thuật.')
h=h.replace('<div class="songtabs">','<div class="songtabs"><button data-song="skill" class="song selected">00 <span>Kiểm tra kỹ năng</span></button>')
h=h.replace('class="song selected">01','class="song">01')
a=h.index('<label>Điều khiển <select');b=h.index('</label>',a)+len('</label>')
h=h[:a]+'<select id="variant" hidden><option value="adaptive">V4 adaptive</option></select>'+h[b:]
h=h.replace('Nốt mục tiêu <span','Nốt rơi: mục tiêu <span')
h=h.replace('Mạng thần kinh điều biến độ ấn.','Mạng thần kinh điều biến độ ấn. Các hệ số dương của synapse được CEM học từ phần thưởng ở cấp episode; đây không phải luật dopamine hay plasticity đã được kiểm chứng ở ruồi.')
h=h.replace('<main>','''<main>
<section class="campaign panel">
<div class="campaignHead"><div><span class="eyebrow">THÍ NGHIỆM CÓ NGÂN SÁCH</span><h1>Luyện hai bài. Đo từng nốt.</h1></div><span id="jobState" class="pill">Đang đọc…</span></div>
<p id="jobMessage">Tốc độ phát video không làm tăng thời gian huấn luyện.</p>
<div class="statRow"><div><b id="realTime">—</b><span>Thời gian thực / ngân sách</span></div><div><b id="simTime">—</b><span>Toàn chiến dịch · tổng bước train + đánh giá</span></div><div><b id="rtf">—</b><span>Giây mô phỏng / giây thực</span></div><div><b>8.766×</b><span>Mục tiêu 1 năm / 1 giờ</span></div></div>
<div class="progress"><i id="progressFill"></i></div>
<div class="experimentGrid"><div><canvas id="learningChart" height="190" aria-label="F1 validation theo thời gian"></canvas><p class="smallText">F1 trên các đoạn theo dõi; các đoạn này có thể đã được luyện. Trục X: thời gian chiến dịch chung.</p></div><div><table id="resultsTable"><thead><tr><th>Mạng / seed</th><th>P</th><th>R</th><th>F1</th><th>Thế hệ</th><th>Trải nghiệm học</th></tr></thead><tbody></tbody></table></div></div>
<div class="jobControls"><label>Ngân sách mỗi bài <select id="minutes"><option value="60">60 phút</option><option value="15">15 phút</option><option value="5">5 phút</option></select></label><button id="startTraining" class="primary">Luyện hai bài piano</button><button id="stopTraining">Dừng và đánh giá</button><a href="/api/export" target="_blank">Nhật ký JSON ↗</a><a href="/paper/manuscript.pdf" target="_blank">Paper v4 ↗</a><a href="/paper/reviewer.pdf" target="_blank">Giới hạn & phương án ↗</a></div>
<p id="demoGate" class="gateNotice">Không có ngưỡng precision. Replay từng bài xuất sau khi luyện xong.</p>
</section>''')
h=h.replace('<script type="module" src="/ui/app.js"></script>','<script type="module" src="/ui/app.js"></script><script src="/ui/dashboard.js"></script>')
h=h.replace('</article></section>\n<section class="transport panel"','<div class="cpgPanel"><span>VNC: 18 CPG · sơ đồ tín hiệu, không phải vị trí giải phẫu</span><div class="cpgGrid">'+''.join(f'<i id="cpg{i}" title="CPG {i}">{i+1}</i>' for i in range(18))+'</div></div></article></section>\n<section class="transport panel"')
(ui/'index.html').write_text(h,encoding='utf8')
css=(old/'style.css').read_text(encoding='utf8')+'''
.campaign{padding:26px;margin-bottom:30px;background:linear-gradient(125deg,#162d32,#121b27 65%)}.campaignHead{display:flex;justify-content:space-between;align-items:center}.campaignHead h1{font-size:28px}.pill{border:1px solid #3a635c;border-radius:20px;padding:8px 14px;color:var(--mint);font-size:12px}.statRow{display:grid;grid-template-columns:repeat(4,1fr);gap:24px;margin:25px 0}.statRow b{font-size:27px;font-weight:500;display:block;color:var(--mint)}.statRow span{font-size:11px;color:var(--muted);display:block;margin-top:8px}.progress{height:4px;background:#263f49;margin-bottom:22px}.progress i{display:block;height:100%;background:var(--mint);width:0}.experimentGrid{display:grid;grid-template-columns:1fr 1fr;gap:28px}#learningChart{width:100%;height:190px}.smallText{font-size:10px}table{width:100%;border-collapse:collapse;font-size:11px}th,td{text-align:right;padding:5px 8px;border-bottom:1px solid #2b3c47}th:first-child,td:first-child{text-align:left}.jobControls{display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-top:24px;font-size:12px}.gateNotice{margin-top:17px;padding-top:15px;border-top:1px solid #344653;color:var(--amber);font-size:12px}.campaign button:disabled{cursor:default}.webgl{height:410px}@media(max-width:950px){.statRow{grid-template-columns:1fr 1fr}.experimentGrid{grid-template-columns:1fr}.campaign{padding:18px}.campaignHead{align-items:flex-start;gap:10px}.campaignHead h1{font-size:24px}.statRow b{font-size:23px}}
'''
css+='\n.cpgPanel{padding:10px 20px 14px;font-size:9px;color:var(--muted);border-top:1px solid var(--line)}.cpgGrid{display:grid;grid-template-columns:repeat(18,1fr);gap:3px;margin-top:8px}.cpgGrid i{font-style:normal;text-align:center;padding:5px 0;background:#69e6c2;color:#092019;font-size:8px}\n'
(ui/'style.css').write_text(css,encoding='utf8')
js=(old/'app.js').read_text(encoding='utf8').replace("song:'merry',variant:'full'","song:'skill',variant:'adaptive'")
js=js.replace('const matrix=new THREE.Matrix4();','''const matrix=new THREE.Matrix4();
let falling=[];const cueHorizon=.15;
function buildFalling(){for(const mesh of falling){body.scene.remove(mesh);mesh.geometry.dispose();mesh.material.dispose()}falling=[];for(let i=0;i<48;i++){const mesh=new THREE.Mesh(new THREE.BoxGeometry(.5,sceneData.key_spacing*.65,1),new THREE.MeshBasicMaterial({color:0xedb76a,transparent:true,opacity:.65,depthWrite:false}));mesh.visible=false;body.scene.add(mesh);falling.push(mesh)}}
function updateFalling(){const t=state.time;const notes=score.notes.filter(n=>n.start<=t+cueHorizon&&n.end>=t).slice(0,48);falling.forEach((mesh,i)=>{const n=notes[i];mesh.visible=!!n;if(!n)return;const head=Math.max(0,n.start-t)*8,tail=Math.min(cueHorizon,Math.max(0,n.end-t))*8;mesh.scale.z=Math.max(.015,tail-head);mesh.position.set(-1.65,(n.pitch-64)*sceneData.key_spacing,sceneData.key_z+.05+(head+tail)/2);mesh.material.color.setHex(n.start<=t?0xf8d29c:0xedb76a)})}
''')
js=js.replace("'Kết thúc';drawRoll()","(state.song==='skill'?'Chuỗi tổng hợp':'Kết thúc');drawRoll()")
js=js.replace('drawRoll();body.renderer.render','drawRoll();updateFalling();body.renderer.render')
js=js.replace('const dn=base+replay.layout.DN[0];',"const cp=base+replay.layout.CPG[0];for(let i=0;i<18;i++){const el=$('cpg'+i);el.style.opacity=.15+.85*Math.min(1,frames[cp+i]/50);el.title='CPG '+i+': '+frames[cp+i].toFixed(2)+' đơn vị rate; thang 0–50'}const dn=base+replay.layout.DN[0];")
a=js.index('async function load(');b=js.index('\nfunction animate',a)
js=js[:a]+'''async function load(song,variant='adaptive'){
 const token=++state.loading;state.playing=false;state.ready=false;$('play').disabled=true;$('play').textContent='Đang tải…';
 try{const r=await json(`/replay/${song}.json`);const s=song==='skill'?{title:r.preview?'Kiểm tra trước huấn luyện':'Kiểm tra kỹ năng · replay chẩn đoán',notes:r.notes,bars:[],pages:0,warnings:[]}:await json(`/data/${song}_score.json`);
 const response=await fetch(`/replay/${song}.bin`);if(!response.ok)throw Error('Replay chưa sẵn sàng');const array=new Float32Array(await response.arrayBuffer());if(token!==state.loading)return;if(array.length!==r.frame_count*r.stride)throw Error('Sai kích thước replay');
 if(song!=='skill' && r.notes)s.notes=r.notes;score=s;replay=r;frames=array;state.song=song;state.variant=variant;state.ready=true;state.time=0;audioCursor=0;$('seek').max=r.duration;$('sheet').hidden=song==='skill';$('midi').hidden=song==='skill';if(song!=='skill'){$('sheet').href=s.source_pdf;$('midi').href=`/data/${song}_reference.mid`}
 $('songTitle').textContent=s.title;$('brainScope').textContent='Chiếu rate DN mô phỏng lên 2 DNg100 đồng dạng FlyWire; khác cá thể/giới tính. Không phải hoạt động não đo được. Thang cố định 0–50. Synapse học nằm trong mô hình VNC; không suy từ độ sáng DN rằng vùng này đã học.';
 $('scoreStatus').textContent=song==='skill'?'Chuỗi tổng hợp, có cao độ và thời gian xác định. Nốt rơi chỉ hiển thị 150 ms phía trước. Replay chẩn đoán không đồng nghĩa vượt chuẩn.':`${s.notes.length} nốt toàn bài · OMR chưa được kiểm tra độc lập từng nốt · ${s.warnings.length} cảnh báo ô nhịp.`;
 const m=r.metrics.find(m=>m.tolerance_s===.1);$('recall').textContent=percent(m.recall);$('precision').textContent=percent(m.precision);$('f1').textContent=percent(m.f1);$('counts').textContent=`${m.matched}/${m.target_notes} nốt đúng · ${m.missed} thiếu · ${m.extra} thừa. Ghép một-một từ tiếp xúc vật lý, ±100 ms.`;
 $('loadState').textContent=`${r.preview?'Chưa học · ':''}${r.physics_steps.toLocaleString('vi')} bước vật lý · ${r.solver_warnings} cảnh báo`;buildFalling();$('play').disabled=false;$('play').textContent='▶ Phát mô phỏng';document.querySelectorAll('.song').forEach(b=>b.classList.toggle('selected',b.dataset.song===song));update()
 }catch(e){$('loadState').textContent=e.message;$('play').textContent='Chưa có replay';console.error(e)}
}'''+js[b:]
a=js.index("try{const availability=await json('/api/state')")
js=js[:a]+'''try{const [s,b]=await Promise.all([json('/assets/scene.json'),json('/assets/brain.json')]);sceneData=s;buildBody(s);buildBrain(b);await load('skill');requestAnimationFrame(animate)}catch(e){$('loadState').textContent=e.message;console.error(e)}
'''
(ui/'app.js').write_text(js,encoding='utf8')
