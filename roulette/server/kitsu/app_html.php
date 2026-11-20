<?php if(!defined('KITSU')){http_response_code(403);exit;} ?>
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Kitsu Roulette Oracle</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Dela+Gothic+One&family=M+PLUS+Rounded+1c:wght@500;800&display=swap">
<style>
/* Layout: one neon column. Fox + bubble, today's 4 picks with the bet, the number table to tap, score, money settings. Single dark look on purpose. */
:root{
  --night:#120a24; --deep:#1d1038; --line:#3b2470; --pink:#ff3d9a; --cyan:#3df0ff; --gold:#ffd23d; --fox:#ff8a3d; --ink:#fff6fb; --dim:#b9a8d9;
  --red:#e8264a; --blk:#1a1426; --grn:#19b36b;
  --display:"Dela Gothic One","Arial Black",system-ui,sans-serif;
  --body:"M PLUS Rounded 1c",ui-rounded,system-ui,sans-serif;
  color-scheme:dark;
}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{background:var(--night)}
body{margin:0;color:var(--ink);font-family:var(--body);font-weight:500;
  background:radial-gradient(ellipse at 50% 18%,#3a1670 0%,var(--night) 62%),var(--night);
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:14px 40px;overflow-x:hidden}
body::after{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;opacity:.16;
  background:repeating-conic-gradient(from 0deg at 50% 22%,transparent 0 3deg,rgba(255,255,255,.35) 3deg 3.6deg,transparent 3.6deg 9deg)}
.stage{position:relative;z-index:1;max-width:520px;margin:0 auto;display:grid;gap:14px;justify-items:center;text-align:center}
.jp{font-family:var(--display);color:var(--cyan);font-size:13px;letter-spacing:.3em;opacity:.85}
.title{font-family:var(--display);font-size:clamp(28px,8vw,42px);line-height:1;margin:4px 0 0;
  background:linear-gradient(90deg,var(--pink),var(--gold),var(--cyan));-webkit-background-clip:text;background-clip:text;color:transparent;
  filter:drop-shadow(0 0 12px rgba(255,61,154,.55))}
.oracle{display:flex;align-items:flex-end;gap:10px;width:100%;justify-content:center}
.fox{width:112px;flex:none;filter:drop-shadow(0 0 14px rgba(255,138,61,.6))}
.fox.bounce{animation:bounce .5s}.fox.shake{animation:shake .45s}
@keyframes bounce{0%,100%{transform:translateY(0)}35%{transform:translateY(-16px) rotate(-4deg)}70%{transform:translateY(-4px)}}
@keyframes shake{0%,100%{transform:translateX(0)}25%{transform:translateX(-7px) rotate(-3deg)}75%{transform:translateX(7px) rotate(3deg)}}
.bubble{position:relative;background:var(--ink);color:#2a1440;border-radius:18px;padding:12px 14px;font-weight:800;font-size:15px;line-height:1.35;
  max-width:300px;min-height:64px;display:grid;place-items:center;box-shadow:0 0 0 3px var(--pink),0 0 22px rgba(255,61,154,.55)}
.bubble::before{content:"";position:absolute;left:-12px;bottom:18px;border:8px solid transparent;border-right:12px solid var(--ink)}
.seg{display:flex;gap:6px;flex-wrap:wrap;justify-content:center;align-items:center}
.seg button{border:2px solid var(--line);background:rgba(29,16,56,.85);color:var(--dim);border-radius:999px;padding:6px 12px;font-weight:800;font-size:13px}
.seg button.on{border-color:var(--gold);color:var(--gold);box-shadow:0 0 12px rgba(255,210,61,.45)}
.seg .lbl{color:var(--dim);font-size:12px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;width:100%}
.card{width:100%;border:3px solid var(--gold);border-radius:20px;padding:14px 12px;background:rgba(255,210,61,.07);box-shadow:0 0 22px rgba(255,210,61,.28);display:grid;gap:10px;justify-items:center}
.card .head{font-family:var(--display);color:var(--gold);letter-spacing:.14em;font-size:15px}
.picks{display:flex;gap:10px;justify-content:center;min-height:58px}
.chip{display:inline-grid;place-items:center;width:56px;height:56px;border-radius:50%;font-family:var(--display);font-size:22px;color:#fff;
  border:3px solid var(--gold);box-shadow:0 0 14px rgba(255,210,61,.7),inset 0 0 10px rgba(0,0,0,.35);animation:pop .4s backwards}
.chip:nth-child(2){animation-delay:.1s}.chip:nth-child(3){animation-delay:.2s}.chip:nth-child(4){animation-delay:.3s}
.chip.hit{border-color:var(--cyan);box-shadow:0 0 26px var(--cyan),0 0 6px #fff;transform:scale(1.15)}
.c-r{background:var(--red)} .c-b{background:var(--blk)} .c-g{background:var(--grn)}
@keyframes pop{from{transform:scale(0) rotate(-90deg);opacity:0}to{transform:scale(1);opacity:1}}
.formula{font-family:var(--display);font-size:clamp(16px,4.6vw,21px);color:var(--gold);text-shadow:0 0 12px rgba(255,210,61,.6)}
.rune{display:inline-block;animation:rune 2.4s linear infinite;color:var(--cyan)}
@keyframes rune{to{transform:rotate(360deg)}}
.formula small{display:block;font-family:var(--body);font-size:12px;color:var(--dim);text-shadow:none;margin-top:2px}
.stake{font-family:var(--display);font-size:30px;line-height:1}
.stake small{display:block;font-family:var(--body);font-size:13px;color:var(--dim);font-weight:800;margin-top:6px}
.series{display:grid;gap:6px;justify-items:center;font-weight:800;color:var(--dim);font-size:13px}
.dots{display:flex;gap:4px;flex-wrap:wrap;justify-content:center}
.dots i{width:12px;height:12px;border-radius:50%;background:#2b1a4d;border:2px solid var(--line)}
.dots i.miss{background:var(--pink);border-color:var(--pink)}
.dots i.now{background:var(--gold);border-color:var(--gold);box-shadow:0 0 10px var(--gold)}
.wait{color:var(--dim);font-weight:800;padding:8px 0}
.padlabel{font-family:var(--display);font-size:16px;color:var(--cyan);letter-spacing:.06em}
.table{display:grid;grid-template-columns:1.2fr repeat(12,minmax(0,1fr));grid-template-rows:repeat(3,44px);gap:3px;width:100%;padding:6px;border-radius:14px;background:#0f4a37;box-shadow:0 0 0 3px var(--gold),0 0 22px rgba(255,210,61,.25)}
.table button{border:0;border-radius:6px;color:#fff;font-family:var(--display);font-size:clamp(11px,3.2vw,15px);padding:0;transition:transform .06s}
.table button:active{transform:scale(.9)}
.table .z{grid-row:1/4;background:var(--grn)}
.table button.pick{box-shadow:inset 0 0 0 3px var(--gold),0 0 10px var(--gold)}
.strip{display:flex;gap:5px;justify-content:center;flex-wrap:wrap;min-height:30px}
.strip span{display:inline-grid;place-items:center;width:30px;height:30px;border-radius:50%;font-family:var(--display);font-size:12px;color:#fff}
.strip span.last{outline:2px solid var(--gold);outline-offset:2px}
.strip span.won{box-shadow:0 0 12px var(--cyan),0 0 0 2px var(--cyan)}
.row{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}
button{font:inherit;cursor:pointer}
.btn{font-family:var(--display);font-size:15px;border:2px solid var(--dim);border-radius:12px;padding:8px 14px;color:var(--dim);background:transparent}
.btn:disabled{opacity:.4;cursor:default}
:focus-visible{outline:3px solid var(--gold);outline-offset:3px}
.board{width:100%;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.board div{background:rgba(29,16,56,.85);border:2px solid var(--line);border-radius:12px;padding:8px 4px}
.board b{display:block;font-family:var(--display);font-size:clamp(14px,4.6vw,20px);font-variant-numeric:tabular-nums;white-space:nowrap}
.board small{font-size:11px;color:var(--dim);letter-spacing:.06em;text-transform:uppercase}
.mm{width:100%;background:rgba(29,16,56,.85);border:2px solid var(--line);border-radius:16px;padding:12px;display:grid;gap:12px}
.mm h2{font-family:var(--display);font-size:16px;margin:0;color:var(--pink);letter-spacing:.08em}
.burst{position:fixed;left:50%;top:38%;transform:translate(-50%,-50%) scale(0);font-family:var(--display);font-size:clamp(44px,14vw,84px);z-index:5;pointer-events:none;
  color:var(--gold);-webkit-text-stroke:3px #2a1440;text-shadow:0 0 30px var(--pink);white-space:nowrap}
.burst.go{animation:burst 1.1s ease-out}
@keyframes burst{0%{transform:translate(-50%,-50%) scale(0) rotate(-12deg);opacity:1}30%{transform:translate(-50%,-50%) scale(1.15) rotate(4deg)}80%{opacity:1}100%{transform:translate(-50%,-50%) scale(1);opacity:0}}
.foot{font-size:12px;color:var(--dim);max-width:46ch;line-height:1.5;margin:0}
@media (max-width:420px){.fox{width:92px}.bubble{font-size:14px}.chip{width:50px;height:50px;font-size:19px}}
@media (prefers-reduced-motion:reduce){.chip,.burst.go,.fox.bounce,.fox.shake,.rune{animation:none}}
</style>
</head>
<body><a href="logout.php" style="position:fixed;top:max(10px,env(safe-area-inset-top,0px));right:max(12px,env(safe-area-inset-right,0px));z-index:9;color:#b9a8d9;font:800 12px 'M PLUS Rounded 1c',sans-serif;text-decoration:none;border:2px solid #3b2470;border-radius:999px;padding:4px 10px;background:rgba(18,10,36,.85)">Log out</a>

<div class="stage">
  <div>
    <div class="jp">ルーレット予言</div>
    <h1 class="title">KITSU ORACLE</h1>
  </div>

  <div class="oracle">
    <svg class="fox" id="fox" viewBox="0 0 120 120" aria-label="Kitsu the fox oracle">
      <path d="M18 52 L26 6 L52 34 Z" fill="var(--fox)"/><path d="M26 40 L29 16 L44 33 Z" fill="#ffc2dd"/>
      <path d="M102 52 L94 6 L68 34 Z" fill="var(--fox)"/><path d="M94 40 L91 16 L76 33 Z" fill="#ffc2dd"/>
      <ellipse cx="60" cy="66" rx="44" ry="40" fill="var(--fox)"/>
      <path d="M20 74 Q60 120 100 74 Q86 104 60 106 Q34 104 20 74 Z" fill="#fff6fb"/>
      <path d="M48 30 Q60 44 72 30 Q66 50 60 52 Q54 50 48 30 Z" fill="#fff6fb" opacity=".9"/>
      <g id="eyes">
        <ellipse cx="42" cy="66" rx="10" ry="13" fill="#2a1440"/><ellipse cx="78" cy="66" rx="10" ry="13" fill="#2a1440"/>
        <ellipse cx="42" cy="70" rx="7" ry="8" fill="var(--pink)"/><ellipse cx="78" cy="70" rx="7" ry="8" fill="var(--pink)"/>
        <circle cx="38" cy="60" r="4" fill="#fff"/><circle cx="74" cy="60" r="4" fill="#fff"/>
        <circle cx="45" cy="73" r="2" fill="#fff"/><circle cx="81" cy="73" r="2" fill="#fff"/>
      </g>
      <g id="eyesHappy" hidden><path d="M32 68 Q42 56 52 68" stroke="#2a1440" stroke-width="4.5" fill="none" stroke-linecap="round"/><path d="M68 68 Q78 56 88 68" stroke="#2a1440" stroke-width="4.5" fill="none" stroke-linecap="round"/></g>
      <g id="eyesSad" hidden><path d="M32 62 L52 68 M33 70 L50 70" stroke="#2a1440" stroke-width="4" stroke-linecap="round"/><path d="M88 62 L68 68 M87 70 L70 70" stroke="#2a1440" stroke-width="4" stroke-linecap="round"/><circle cx="92" cy="80" r="3" fill="var(--cyan)"/></g>
      <ellipse cx="28" cy="84" rx="7" ry="4" fill="var(--pink)" opacity=".55"/><ellipse cx="92" cy="84" rx="7" ry="4" fill="var(--pink)" opacity=".55"/>
      <circle cx="60" cy="84" r="3" fill="#2a1440"/>
      <path id="mouth" d="M53 90 Q60 96 67 90" stroke="#2a1440" stroke-width="3" fill="none" stroke-linecap="round"/>
    </svg>
    <div class="bubble" id="say">Konnichiwa! Tap the last two numbers from your table and I'll read the wheel~</div>
  </div>

  <div class="seg" id="method" aria-label="Prediction method">
    <button data-m="pyth">🔮 Spirit Geometry</button><button data-m="fox">🦊 Fox Instinct</button>
  </div>

  <section class="card" aria-live="polite">
    <div class="head">NEXT SPIN · BET THESE 4</div>
    <div class="series" id="series"></div>
    <div class="picks" id="picks"></div>
    <div class="formula" id="formula"></div>
    <div class="stake" id="stake"></div>
  </section>

  <div class="padlabel">Tap the number that landed</div>
  <div class="table" id="table"></div>
  <div class="strip" id="strip" aria-label="Last numbers"></div>
  <div class="row">
    <button class="btn" id="bUndo">↶ Undo</button>
    <button class="btn" id="bDemo">🎲 Demo number</button>
  </div>

  <div class="board">
    <div><small>Spins</small><b id="sRounds">0</b></div>
    <div><small>Hits</small><b id="sHits">0</b></div>
    <div><small>Combo</small><b id="sCombo">0</b></div>
    <div><small>Session</small><b id="sPL">€0.00</b></div>
  </div>

  <section class="mm">
    <h2>MONEY MANAGEMENT</h2>
    <div class="seg" id="hold"><span class="lbl">Keep the same 4 numbers for</span><button data-v="1">1 spin</button><button data-v="5">5</button><button data-v="10">10</button><button data-v="15">15</button><button data-v="20">20 spins</button></div>
    <div class="seg" id="base"><span class="lbl">Base bet per number</span><button data-v="0.1">€0.10</button><button data-v="0.2">€0.20</button><button data-v="0.5">€0.50</button><button data-v="1">€1</button><button data-v="2">€2</button></div>
    <div class="seg" id="prog"><span class="lbl">After a miss, raise the bet by</span><button data-v="0">0%</button><button data-v="10">10%</button><button data-v="20">20%</button><button data-v="35">35%</button><button data-v="50">50%</button></div>
    <div class="seg" id="cap"><span class="lbl">Max bet per number</span><button data-v="1">€1</button><button data-v="2">€2</button><button data-v="5">€5</button><button data-v="10">€10</button></div>
    <button class="btn" id="bReset">New session</button>
  </section>

  <p class="foot">Entertainment only. Roulette spins are random and no method can predict them. Never bet money you can't afford to lose. 18+</p>
</div>
<div class="burst" id="burst"></div>

<script>(()=>{const t=[0,32,15,19,4,21,2,25,17,34,6,27,13,36,11,30,8,23,10,5,24,16,33,1,20,14,31,9,22,18,29,7,28,12,35,3,26],e=new Set([1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]),s=t=>document.getElementById(t),n=t=>0===t?"g":e.has(t)?"r":"b",o=t=>t[Math.floor(Math.random()*t.length)],a={pyth:["The spirits have spoken! ✨","The sacred geometry points here~","Spirit magic! Bet these four!","Geometry of fate… ✨"],fox:["The fox spirit whispers… these four!","My tails are tingling~","These numbers are sleeping… time to wake up!","I saw it in a dream!"],hit:["SUGOI!! I called it!","Yatta~! Fox powers!","Did you SEE that?!","Hehe, told you so ✨"],miss:["Ehh?! The wheel cheated!","Mou~ next one for sure!","Hmph. Lucky wheel.","That… was a test. Yes."]},i="kitsu-player-v2",l={hist:[],won:[],rounds:0,hits:0,combo:0,best:0,pl:0,step:0,cur:null,f:"",inS:0};let r={...l,method:"pyth",base:.2,prog:20,cap:2,hold:10},h=null;const c=[];try{const t=JSON.parse(localStorage.getItem(i)||"null");t&&(r={...r,...t})}catch(t){}const d=()=>{try{localStorage.setItem(i,JSON.stringify(r))}catch(t){}},u=t=>(t<0?"−":t>0?"+":"")+"€"+Math.abs(t).toFixed(2),p=t=>Math.min(r.cap,Math.max(r.base,Math.ceil(Math.round(r.base*Math.pow(1+r.prog/100,t)*1e6)/1e5-1e-9)/10)),m=()=>p(r.step),f=[];for(let t=0;t<3;t++)for(let e=0;e<12;e++)f.push(3*e+3-t);function g(t){s("eyes").hidden="idle"!==t,s("eyesHappy").hidden="happy"!==t,s("eyesSad").hidden="sad"!==t,s("mouth").setAttribute("d","happy"===t?"M50 88 Q60 102 70 88 Z":"sad"===t?"M53 94 Q60 88 67 94":"M53 90 Q60 96 67 90"),s("mouth").setAttribute("fill","happy"===t?"#ff6fb0":"none");const e=s("fox");e.classList.remove("bounce","shake"),e.offsetWidth,"happy"===t&&e.classList.add("bounce"),"sad"===t&&e.classList.add("shake")}s("table").innerHTML='<button class="z" data-n="0">0</button>'+f.map((t=>`<button style="background:var(--${e.has(t)?"red":"blk"})" data-n="${t}">${t}</button>`)).join("");const b=t=>s("say").textContent=t;function y(e=!0){const n=r.hist;if("pyth"===r.method){if(n.length<2)return h=r.cur=null,s("formula").innerHTML="",void(e&&b(n.length?`Got ${n[0]}! One more number and I can calculate~`:"Tap the last two numbers from your table and I'll calculate~"));const o=n[n.length-2],a=n[n.length-1],i=Math.sqrt(o*o+a*a),l=Math.round(i)%37,c=t.indexOf(l);h=[t[(c+36)%37],l,t[(c+1)%37],t[(c+2)%37]],s("formula").innerHTML='<span class="rune">✦</span> Spirit Geometry reading <span class="rune">✦</span><small>Kitsu read your last spins and drew these four</small>'}else{if(n.length<1)return h=r.cur=null,s("formula").innerHTML="",void(e&&b("Tap a few numbers from your table so I can sense the sleeping ones~"));const t=new Map;n.forEach(((e,s)=>t.set(e,s)));const o=Array.from({length:37},((e,s)=>({n:s,g:t.has(s)?n.length-t.get(s):1e3+(13*s+5)%37})));o.sort(((t,e)=>e.g-t.g||t.n-e.n)),h=o.slice(0,4).map((t=>t.n)).sort(((t,e)=>t-e)),s("formula").innerHTML='<span class="rune">✦</span> Fox Instinct reading <span class="rune">✦</span><small>Kitsu sniffed out these four</small>'}r.cur=h,r.f=s("formula").innerHTML,r.inS=0,r.step=0,r.sStart=r.pl,e&&(g("idle"),b(o(a[r.method])))}function M(){h=r.cur||null,s("formula").innerHTML=h?r.f:""}function S(t){s("picks").innerHTML=h?h.map((e=>`<span class="chip c-${n(e)} ${e===t?"hit":""}">${e}</span>`)).join(""):"";const e=m();let o=0;for(let t=r.step;t<r.step+Math.max(1,r.hold-r.inS);t++)o+=4*p(t);s("series").innerHTML=h&&r.hold>1?`Spin ${r.inS+1} of ${r.hold} with these numbers<div class="dots">${Array.from({length:r.hold},((t,e)=>`<i class="${e<r.inS?"miss":e===r.inS?"now":""}"></i>`)).join("")}</div>`:"",s("stake").innerHTML=h?`€${e.toFixed(2)} on each<small>total €${(4*e).toFixed(2)} · hit now: series ${u(Math.round(100*(r.pl-(r.sStart??r.pl)+32*e))/100)}${r.hold>1?`<br>rest of this series can cost up to €${o.toFixed(2)}`:""}</small>`:'<div class="wait">Waiting for your numbers…</div>';const a=new Set(h||[]);[...s("table").children].forEach((t=>t.classList.toggle("pick",a.has(+t.dataset.n)))),s("strip").innerHTML=r.hist.slice(-14).map(((t,e,s)=>`<span class="c-${n(t)} ${e===s.length-1?"last":""} ${r.won.includes(r.hist.length-s.length+e)?"won":""}">${t}</span>`)).join(""),s("sRounds").textContent=r.rounds,s("sHits").textContent=r.hits,s("sCombo").textContent=`${r.combo} / ${r.best}`,s("sPL").textContent=u(r.pl),s("sPL").style.color=r.pl>0?"var(--cyan)":r.pl<0?"var(--pink)":"";for(const[t,e]of[["method","method"],["hold","hold"],["base","base"],["prog","prog"],["cap","cap"]])[...s(t).querySelectorAll("button")].forEach((t=>t.classList.toggle("on",String(t.dataset.m??t.dataset.v)===String(r[e]))))}let w=!1;function T(t){if(w)return;c.push(JSON.stringify(r)),c.length>60&&c.shift();let e=null;if(h){const n=m(),i=h.includes(t);r.rounds++,i?(r.hits++,r.combo++,r.best=Math.max(r.best,r.combo),r.pl=Math.round(100*(r.pl+32*n))/100,r.step=0,r.won.push(r.hist.length),e=t,g("happy"),b(o(a.hit)),function(t){const e=s("burst");e.textContent=t,e.classList.remove("go"),e.offsetWidth,e.classList.add("go")}(r.combo>1?`COMBO ×${r.combo}!`:"SUGOI!")):(r.combo=0,r.pl=Math.round(100*(r.pl-4*n))/100,r.step++,g("sad"),b(o(a.miss))),r.inS++}if(r.hist.push(t),r.hist.length>400&&(r.hist.shift(),r.won=r.won.map((t=>t-1)).filter((t=>t>=0))),d(),null!==e)S(e),w=!0,setTimeout((()=>{w=!1,y(),d(),S()}),2e3);else if(!h||r.inS>=r.hold){const t=!!h;y(!t),d(),S(),t&&setTimeout((()=>{h&&b(r.hold>1?"Series over! New numbers~ "+o(a[r.method]):o(a[r.method])),g("idle")}),900)}else S(),setTimeout((()=>{b(o(["Same four, stay strong!","Keep going~ they're coming!","Don't give up on them!","Trust the fox. Again!"])),g("idle")}),900)}s("table").onclick=t=>{const e=t.target.closest("button[data-n]");e&&T(+e.dataset.n)},s("bDemo").onclick=()=>{const t=new Uint32Array(1);crypto.getRandomValues(t),T(t[0]%37)},s("bUndo").onclick=()=>{!w&&c.length&&(r=JSON.parse(c.pop()),d(),M(),S(),g("idle"),b("Undone! Tap the right number~"))};for(const t of["method","hold","base","prog","cap"])s(t).onclick=e=>{const s=e.target.closest("button");s&&!w&&("method"===t?(r.method=s.dataset.m,y()):(r[t]=+s.dataset.v,"hold"===t&&r.inS>=r.hold&&h&&y()),d(),S())};s("bReset").onclick=()=>{r={...r,...l,hist:[],won:[]},c.length=0,d(),y(),S(),g("idle")},r.cur?M():y(!1),d(),S()})();
</script>

</body>
</html>
