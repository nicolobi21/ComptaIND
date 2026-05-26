/* ============================================================
   app.js — Socle commun du cours de comptabilité 4e
   Navigation + moteurs interactifs (data-driven, auto-init)
   ============================================================ */
(function(){
"use strict";

/* ---------- Utilitaires ---------- */
const fmt = n => Number(n).toLocaleString('fr-FR',{maximumFractionDigits:2}).replace(/[\u202f\u00a0\s]/g,'\u00a0');
const num = v => { const s=String(v).replace(/\s/g,'').replace(',','.').replace(/[^\d.\-]/g,''); return s===''?NaN:parseFloat(s); };
const near = (a,b) => Math.abs(a-b) < 0.005;
const ICON = {
  ok:'<path d="M20 6 9 17l-5-5"/>',
  bad:'<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6M9 9l6 6"/>',
  info:'<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
  eye:'<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/>'
};

/* ---------- Plan du cours ---------- */
const FICHES = [
  {n:1, t:"Le bilan", f:"index.html"},
  {n:2, t:"Les comptes", f:"fiche-2.html"},
  {n:3, t:"La règle des signes", f:"fiche-3.html"},
  {n:4, t:"La démarche comptable", f:"fiche-4.html"},
  {n:5, t:"Les ressources de l'E.", f:"fiche-5.html"},
  {n:6, t:"La TVA", f:"fiche-6.html"},
  {n:7, t:"Constitution & capital", f:"fiche-7.html"},
  {n:8, t:"Variations de stock", f:"fiche-8.html"},
  {n:9, t:"Le calcul des résultats", f:"fiche-9.html"},
  {n:10, t:"La rémunération", f:"fiche-10.html"}
];

/* ---------- Injection sidebar + bouton menu + pager + fab ---------- */
function buildChrome(){
  const cur = parseInt(document.body.dataset.fiche || "1", 10);

  const menuBtn = document.createElement('button');
  menuBtn.className='menu-btn'; menuBtn.setAttribute('aria-label','Menu');
  menuBtn.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>';

  const sb = document.createElement('aside');
  sb.className='sidebar'; sb.id='sb';
  let nav = '';
  FICHES.forEach(fi=>{
    const active = fi.n===cur ? ' active':'';
    nav += `<a class="${active.trim()}" href="${fi.f}"><span class="num">${fi.n}</span> ${fi.t}</a>`;
  });
  sb.innerHTML = `
    <div class="brand">
      <div class="school">IND Loverval</div>
      <div class="course">Comptabilité</div>
      <div class="meta">Sciences économiques · 4ᵉ année<br>S. Molinari</div>
    </div>
    <div class="nav-label">Plan du cours</div>
    <nav class="nav">${nav}</nav>`;

  menuBtn.addEventListener('click', ()=>sb.classList.toggle('open'));

  // structure shell : sidebar + main(existant)
  const main = document.querySelector('.main');
  const shell = document.createElement('div'); shell.className='shell';
  document.body.insertBefore(shell, main);
  shell.appendChild(sb);
  shell.appendChild(main);
  document.body.insertBefore(menuBtn, shell);

  // pager
  const prev = FICHES.find(f=>f.n===cur-1);
  const next = FICHES.find(f=>f.n===cur+1);
  const pager = document.createElement('div'); pager.className='pager'; pager.style.maxWidth='860px'; pager.style.margin='48px auto 0'; pager.style.padding='26px 32px 0';
  pager.innerHTML =
    (prev?`<a class="prev" href="${prev.f}"><span class="dir">← Fiche ${prev.n}</span><span class="ttl">${prev.t}</span></a>`
         :`<a class="prev disabled"><span class="dir">←</span><span class="ttl">Début</span></a>`) +
    (next?`<a class="next" href="${next.f}"><span class="dir">Fiche ${next.n} →</span><span class="ttl">${next.t}</span></a>`
         :`<a class="next disabled"><span class="dir">Fin →</span><span class="ttl">Cours terminé</span></a>`);
  const footer = main.querySelector('footer');
  if(footer) main.insertBefore(pager, footer); else main.appendChild(pager);

  // fab imprimer
  const fab = document.createElement('div'); fab.className='fab';
  fab.innerHTML='<button type="button"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9V2h12v7M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8" rx="1"/></svg> Imprimer</button>';
  fab.querySelector('button').addEventListener('click', ()=>window.print());
  document.body.appendChild(fab);
}

/* ---------- Feedback helper ---------- */
function setFb(box, kind, html){
  if(!box) return;
  const ico = box.querySelector('.fb-ico'); const txt = box.querySelector('.fb-txt');
  box.className = 'feedback show ' + (kind==='win'?'win':kind==='lose'?'lose':'tip');
  if(ico) ico.innerHTML = kind==='win'?ICON.ok:kind==='lose'?ICON.bad:ICON.info;
  if(txt) txt.innerHTML = html;
}

/* ---------- Moteur : compte en T live ---------- */
function initTaccount(root){
  const inputs = root.querySelectorAll('input[data-side]');
  function recalc(){
    let d=0,c=0;
    inputs.forEach(i=>{ const v=num(i.value); if(!isNaN(v)){ i.dataset.side==='d'?d+=v:c+=v; } });
    const td=root.querySelector('[data-total="d"]'), tc=root.querySelector('[data-total="c"]'), sp=root.querySelector('[data-solde]');
    if(td) td.textContent=fmt(d); if(tc) tc.textContent=fmt(c);
    if(sp){ const s=d-c; sp.textContent = s>=0 ? fmt(s)+' € · débiteur' : fmt(-s)+' € · créditeur'; sp.classList.toggle('cred', s<0); }
  }
  inputs.forEach(i=>i.addEventListener('input', recalc));
  recalc();
}

/* ---------- Moteur : champs auto-corrigés (data-exp) ---------- */
function initFields(root){
  const inputs = root.querySelectorAll('input[data-exp]');
  const fb = root.querySelector('.feedback');
  const winMsg = root.dataset.win || "Bravo, tout est correct&nbsp;!";
  root.querySelectorAll('[data-act]').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      const a=btn.dataset.act;
      if(a==='check'){
        let filled=true, ok=true;
        inputs.forEach(i=>{
          i.classList.remove('ok','bad');
          const v=num(i.value), exp=parseFloat(i.dataset.exp);
          if(isNaN(v)){ filled=false; ok=false; return; }
          if(near(v,exp)) i.classList.add('ok'); else {i.classList.add('bad'); ok=false;}
        });
        if(!filled) setFb(fb,'tip','<b>Il manque des réponses.</b> Complète toutes les cases, puis vérifie.');
        else if(ok) setFb(fb,'win', winMsg);
        else setFb(fb,'lose','<b>Pas tout à fait.</b> Les cases en rouge sont à revoir.');
      } else if(a==='reveal'){
        inputs.forEach(i=>{ i.value=fmt(parseFloat(i.dataset.exp)); i.classList.remove('bad'); i.classList.add('ok'); });
        setFb(fb,'tip','<b>Correction affichée.</b>');
      } else if(a==='reset'){
        inputs.forEach(i=>{ i.value=''; i.classList.remove('ok','bad'); });
        if(fb) fb.className='feedback';
      }
    });
  });
}

/* ---------- Moteur : classer par glisser-déposer ---------- */
function initClasser(root){
  const pool = root.querySelector('.pool');
  const zones = {}; root.querySelectorAll('[data-zone]').forEach(z=>{ if(z.dataset.zone!=='pool') zones[z.dataset.zone]=z; });
  const fb = root.querySelector('.feedback');
  const expectCap = root.dataset.cap ? parseFloat(root.dataset.cap) : null;
  const winMsg = root.dataset.win || "<b>Parfait, tout est bien classé&nbsp;!</b>";
  let drag={chip:null,moved:false,dx:0,dy:0,sx:0,sy:0,w:0}, selected=null;

  const capInput = c => c.querySelector('.cap-in');
  function syncCap(chip){
    if(!chip.dataset.calc) return;
    const slot=chip.querySelector('.cap-slot, .cap-in'); const inZone=chip.parentElement!==pool;
    if(inZone && slot && slot.classList.contains('cap-slot')){
      const inp=document.createElement('input'); inp.className='cap-in'; inp.type='text'; inp.inputMode='numeric'; inp.placeholder='montant €';
      inp.addEventListener('input', recalc); inp.addEventListener('pointerdown', e=>e.stopPropagation());
      slot.replaceWith(inp);
    } else if(!inZone && slot && slot.classList.contains('cap-in')){
      const span=document.createElement('span'); span.className='chip-amt cap-slot'; span.textContent='à calculer'; slot.replaceWith(span);
    }
  }
  function chipAmt(c){ if(c.dataset.calc){const i=capInput(c); return i?num(i.value):NaN;} return parseFloat(c.dataset.amount); }
  function recalc(){
    Object.keys(zones).forEach(k=>{
      const z=zones[k]; const out=root.querySelector(`[data-total="${k}"]`); if(!out) return;
      let s=0,ok=true; z.querySelectorAll('.chip').forEach(c=>{const v=chipAmt(c); isNaN(v)?ok=false:s+=v;});
      out.textContent = z.children.length===0?'—':(ok?fmt(s)+' €':'…');
    });
  }
  function place(chip,zone){ (zone||pool).appendChild(chip); chip.classList.remove('ok','bad','selected'); if(selected===chip)selected=null; syncCap(chip); recalc(); }
  function zoneAt(x,y){ const el=document.elementFromPoint(x,y); if(!el)return null; const z=el.closest('[data-zone]'); if(!z)return null; return z.dataset.zone==='pool'?pool:zones[z.dataset.zone]; }
  function hoverZone(x,y){ clearHover(); const z=zoneAt(x,y); if(z) z.classList.add('over'); }
  function clearHover(){ pool.classList.remove('over'); Object.values(zones).forEach(z=>z.classList.remove('over')); }
  function toggleSel(c){ if(selected===c)clearSel(); else{clearSel(); selected=c; c.classList.add('selected');} }
  function clearSel(){ if(selected){selected.classList.remove('selected'); selected=null;} }

  function onDown(e){ const chip=e.currentTarget; if(e.target.classList.contains('cap-in'))return;
    drag.chip=chip; drag.moved=false; drag.sx=e.clientX; drag.sy=e.clientY;
    const r=chip.getBoundingClientRect(); drag.dx=e.clientX-r.left; drag.dy=e.clientY-r.top; drag.w=r.width;
    window.addEventListener('pointermove',onMove); window.addEventListener('pointerup',onUp); }
  function onMove(e){ if(!drag.chip)return;
    if(!drag.moved && Math.hypot(e.clientX-drag.sx,e.clientY-drag.sy)>5){ drag.moved=true; drag.chip.classList.add('flying'); drag.chip.style.width=drag.w+'px'; clearSel(); }
    if(drag.moved){ e.preventDefault(); drag.chip.style.left=(e.clientX-drag.dx)+'px'; drag.chip.style.top=(e.clientY-drag.dy)+'px'; hoverZone(e.clientX,e.clientY); } }
  function onUp(e){ window.removeEventListener('pointermove',onMove); window.removeEventListener('pointerup',onUp);
    const chip=drag.chip; drag.chip=null; if(!chip)return;
    if(drag.moved){ chip.classList.remove('flying'); chip.style.left=chip.style.top=chip.style.width=''; const z=zoneAt(e.clientX,e.clientY); clearHover(); place(chip,z); }
    else toggleSel(chip); }

  root.querySelectorAll('.chip').forEach(c=>c.onpointerdown=onDown);
  Object.keys(zones).forEach(k=>zones[k].addEventListener('click',()=>{ if(selected) place(selected,zones[k]); }));
  pool.addEventListener('click', e=>{ if(e.target===pool && selected) place(selected,pool); });

  root.querySelectorAll('[data-act]').forEach(btn=>btn.addEventListener('click', ()=>{
    const a=btn.dataset.act;
    if(a==='check'){
      root.querySelectorAll('.chip').forEach(c=>c.classList.remove('ok','bad'));
      if(pool.querySelectorAll('.chip').length>0){ setFb(fb,'tip','<b>Il reste des étiquettes à classer.</b>'); return; }
      let classOk=true, capOk=true;
      Object.keys(zones).forEach(k=>zones[k].querySelectorAll('.chip').forEach(c=>{
        if(c.dataset.side===k) c.classList.add('ok'); else {c.classList.add('bad'); classOk=false;}
        if(c.dataset.calc && expectCap!=null && !near(chipAmt(c),expectCap)){ capOk=false; c.classList.remove('ok'); c.classList.add('bad'); }
      }));
      if(classOk&&capOk) setFb(fb,'win',winMsg);
      else if(!classOk) setFb(fb,'lose','<b>Attention au classement.</b> Les étiquettes en rouge ne sont pas du bon côté.');
      else setFb(fb,'lose','<b>Classement correct&nbsp;!</b> Mais revois le montant à calculer (en rouge).');
    } else if(a==='reveal'){
      root.querySelectorAll('.chip').forEach(c=>{ zones[c.dataset.side].appendChild(c); c.classList.remove('bad'); c.classList.add('ok'); syncCap(c);
        if(c.dataset.calc && expectCap!=null){ const i=capInput(c); if(i) i.value=fmt(expectCap); } });
      recalc(); setFb(fb,'tip','<b>Correction affichée.</b>');
    } else if(a==='reset'){
      root.querySelectorAll('.chip').forEach(c=>{ c.classList.remove('ok','bad','selected'); pool.appendChild(c); syncCap(c); });
      clearSel(); recalc(); if(fb) fb.className='feedback';
    }
  }));
  recalc();
}

/* ---------- Moteur : QCM ---------- */
function initQuiz(root){
  const qs = root.querySelectorAll('.q'); let answered=0, good=0;
  const scoreBox = root.querySelector('.quiz-score');
  qs.forEach(q=>{
    const opts=q.querySelectorAll('.opt'); const fb=q.querySelector('.q-fb');
    opts.forEach(opt=>opt.addEventListener('click', ()=>{
      if(q.dataset.done) return; q.dataset.done="1"; answered++;
      const correct = opt.dataset.correct==="1";
      if(correct){ opt.classList.add('correct'); const m=opt.querySelector('.mk'); if(m)m.innerHTML=ICON.ok; good++; }
      else { opt.classList.add('wrong'); const m=opt.querySelector('.mk'); if(m)m.innerHTML=ICON.bad;
        opts.forEach(o=>{ if(o.dataset.correct==="1"){o.classList.add('correct'); const mm=o.querySelector('.mk'); if(mm)mm.innerHTML=ICON.ok;} }); }
      opts.forEach(o=>o.classList.add('locked'));
      if(fb){ fb.className='q-fb show '+(correct?'good':'bad'); fb.innerHTML=(correct?'<b>Correct&nbsp;!</b> ':'<b>Raté.</b> ')+(fb.dataset.explain||''); }
      if(answered===qs.length && scoreBox){ scoreBox.className='quiz-score show'; scoreBox.textContent=`Score : ${good} / ${qs.length}`; }
    }));
  });
}

/* ---------- Moteur : calculateur TVA ---------- */
function initTva(root){
  const base=root.querySelector('[data-tva-base]');
  const tauxBtns=root.querySelectorAll('[data-taux]');
  let taux = parseFloat(root.dataset.taux||"21");
  function recalc(){
    const h=num(base.value); const oH=root.querySelector('[data-out="htva"]'), oT=root.querySelector('[data-out="tva"]'), oC=root.querySelector('[data-out="tvac"]');
    if(isNaN(h)){ if(oH)oH.textContent='—'; if(oT)oT.textContent='—'; if(oC)oC.textContent='—'; return; }
    const tva=Math.round(h*taux)/100, tvac=h+tva;
    if(oH)oH.textContent=fmt(h)+' €'; if(oT)oT.textContent=fmt(tva)+' €'; if(oC)oC.textContent=fmt(tvac)+' €';
  }
  tauxBtns.forEach(b=>b.addEventListener('click', ()=>{ taux=parseFloat(b.dataset.taux); tauxBtns.forEach(x=>x.classList.toggle('on',x===b)); recalc(); }));
  base.addEventListener('input', recalc);
  recalc();
}

/* ---------- Init global ---------- */
document.addEventListener('DOMContentLoaded', ()=>{
  buildChrome();
  document.querySelectorAll('.js-taccount').forEach(initTaccount);
  document.querySelectorAll('.js-fields').forEach(initFields);
  document.querySelectorAll('.js-classer').forEach(initClasser);
  document.querySelectorAll('.js-quiz').forEach(initQuiz);
  document.querySelectorAll('.js-tva').forEach(initTva);
});

})();
