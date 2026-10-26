let featureChart, currentItems=[];
const fmt=n=>Number(n).toLocaleString(undefined,{maximumFractionDigits:2});
async function loadSummary(){
 const s=await fetch('/api/summary').then(r=>r.json());
 document.getElementById('participants').textContent=fmt(s.participants);
 document.getElementById('rate').textContent=s.positive_rate+'%';
 document.getElementById('accuracy').textContent=s.model_accuracy_training+'%';
 featureChart=new Chart(document.getElementById('featureChart'),{type:'bar',data:{labels:s.features.map(x=>x.name.replace('_',' ')),datasets:[{label:'Coefficient',data:s.features.map(x=>x.coefficient),backgroundColor:s.features.map(x=>x.coefficient>=0?'#23877f':'#df9b61'),borderRadius:5}]},options:{responsive:true,maintainAspectRatio:false,indexAxis:'y',plugins:{legend:{display:false}},scales:{x:{grid:{color:'#edf1f5'}},y:{grid:{display:false}}}}});
 const cm=s.confusion_matrix;
 document.getElementById('matrix').innerHTML=`<div class="head"></div><div class="head">Predicted 0</div><div class="head">Predicted 1</div><div class="head">Actual 0</div><div class="cell">${cm[0][0]}</div><div class="cell">${cm[0][1]}</div><div class="head">Actual 1</div><div class="cell">${cm[1][0]}</div><div class="cell">${cm[1][1]}</div>`;
}
async function loadRows(){
 const q=new URLSearchParams({q:document.getElementById('search').value,group:document.getElementById('group').value});
 const d=await fetch('/api/participants?'+q).then(r=>r.json());currentItems=d.items;
 document.getElementById('rows').innerHTML=d.items.length?d.items.map(x=>`<tr><td class="participant">${x.participant_code}</td><td>${x.study_group}</td><td>${x.collection_date}</td><td>${x.marker_alpha.toFixed(2)}</td><td>${x.marker_beta.toFixed(2)}</td><td>${x.marker_gamma.toFixed(2)}</td><td>${x.age_years}</td><td><span class="pill ${x.response_label?'positive':'negative'}">${x.response_label?'Positive':'Negative'}</span></td></tr>`).join(''):'<tr><td colspan="8">No matching participants found.</td></tr>';
 document.getElementById('tableFoot').textContent=`Showing ${d.count} records · Up to 250 results`;
}
document.getElementById('search').addEventListener('input',loadRows);document.getElementById('group').addEventListener('change',loadRows);
document.getElementById('predictForm').addEventListener('submit',async e=>{
 e.preventDefault();const data=Object.fromEntries(new FormData(e.target).entries());Object.keys(data).forEach(k=>data[k]=Number(data[k]));
 const box=document.getElementById('resultText');box.textContent='Calculating…';
 const r=await fetch('/api/predict',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
 const out=await r.json();if(!r.ok){box.textContent=out.detail||'Could not calculate score.';return}
 document.getElementById('probability').textContent=(out.illustrative_response_probability*100).toFixed(1)+'%';
 document.getElementById('predictionLabel').textContent=out.label;box.textContent=out.warning;
});
document.getElementById('exportBtn').addEventListener('click',()=>{const cols=['participant_code','study_group','collection_date','marker_alpha','marker_beta','marker_gamma','age_years','response_label'];const csv=[cols.join(','),...currentItems.map(r=>cols.map(k=>JSON.stringify(r[k]??'')).join(','))].join('\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8;'}));const a=document.createElement('a');a.href=url;a.download='biomarker-participants.csv';a.click();URL.revokeObjectURL(url)});
loadSummary().catch(console.error);loadRows().catch(console.error);