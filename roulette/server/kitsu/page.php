<?php
// Shared look for the public pages
function page_head(string $title): void { ?>
<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title><?= h($title) ?></title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Dela+Gothic+One&family=M+PLUS+Rounded+1c:wght@500;800&display=swap">
<style>
:root{--night:#120a24;--deep:#1d1038;--line:#3b2470;--pink:#ff3d9a;--cyan:#3df0ff;--gold:#ffd23d;--fox:#ff8a3d;--ink:#fff6fb;--dim:#b9a8d9;
 --display:"Dela Gothic One","Arial Black",system-ui,sans-serif;--body:"M PLUS Rounded 1c",ui-rounded,system-ui,sans-serif;color-scheme:dark}
*{box-sizing:border-box}body{margin:0;color:var(--ink);font-family:var(--body);font-weight:500;line-height:1.5;
 background:radial-gradient(ellipse at 50% 10%,#3a1670 0%,var(--night) 60%),var(--night);min-height:100vh;
 padding:24px max(16px,env(safe-area-inset-right,0px)) 48px max(16px,env(safe-area-inset-left,0px))}
.wrap{max-width:560px;margin:0 auto;display:grid;gap:18px;text-align:center}
.jp{font-family:var(--display);color:var(--cyan);letter-spacing:.3em;font-size:13px}
h1{font-family:var(--display);font-size:clamp(34px,9vw,52px);line-height:1;margin:4px 0 0;background:linear-gradient(90deg,var(--pink),var(--gold),var(--cyan));-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 0 12px rgba(255,61,154,.5))}
h2{font-family:var(--display);font-size:20px;margin:0;color:var(--gold)}
.lead{font-size:18px;font-weight:800}
.box{background:rgba(29,16,56,.85);border:2px solid var(--line);border-radius:18px;padding:18px;display:grid;gap:12px;text-align:left}
.box.gold{border-color:var(--gold);box-shadow:0 0 24px rgba(255,210,61,.25)}
.price{font-family:var(--display);font-size:44px;color:var(--gold);text-align:center;line-height:1}
.price small{display:block;font-family:var(--body);font-size:14px;color:var(--dim);margin-top:6px}
ul{margin:0;padding-left:20px;display:grid;gap:6px}
input{font:inherit;width:100%;padding:12px;border-radius:12px;border:2px solid var(--line);background:var(--night);color:var(--ink)}
button{font-family:var(--display);font-size:16px;border:0;border-radius:12px;padding:12px 18px;background:var(--cyan);color:#2a1440;cursor:pointer}
:focus-visible{outline:3px solid var(--gold);outline-offset:3px}
.msg{border-radius:12px;padding:10px 14px;font-weight:800}
.ok{background:rgba(61,240,255,.12);border:2px solid var(--cyan)} .err{background:rgba(255,61,154,.12);border:2px solid var(--pink)}
.fine{font-size:12px;color:var(--dim)}
a{color:var(--cyan)}
img.shot{width:100%;border-radius:16px;border:2px solid var(--line)}
</style></head><body><div class="wrap">
<?php }
function page_foot(): void { ?>
<p class="fine">Entertainment only. Kitsu's picks are random choices and cannot predict roulette; nobody can. Never bet money you can't afford to lose. 18+ · <a href="terms.php">Terms</a></p>
</div></body></html>
<?php }
