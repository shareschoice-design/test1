<?php
require __DIR__ . '/lib.php'; require __DIR__ . '/page.php';
if (current_user()) { header('Location: app.php'); exit; }
$sent = isset($_GET['sent']); $bad = isset($_GET['expired']);
$tok = csrf(); // start the session before any output
page_head('Kitsu Oracle – anime roulette companion');
?>
<div><div class="jp">ルーレット予言</div><h1>KITSU ORACLE</h1></div>
<p class="lead">Your anime roulette companion 🦊<br>Tap the number that landed. Kitsu picks your next 4 numbers and tells you how much to bet.</p>

<?php if ($sent): ?><div class="msg ok">If this e-mail has access, a login link is on its way. Check your inbox (and spam).</div><?php endif; ?>
<?php if ($bad): ?><div class="msg err">That login link has expired or was already used. Ask for a new one below.</div><?php endif; ?>

<section class="box gold">
  <div class="price">€<?= h(cfg('price')) ?><?= is_sub() ? '<span style="font-size:22px"> / month</span>' : '' ?><small><?= is_sub() ? 'monthly subscription · cancel any time in PayPal' : ((int)cfg('access_days') > 0 ? (int)cfg('access_days') . ' days of access' : 'one payment · lifetime access') ?></small></div>
  <ul>
    <li><b>2 methods:</b> 📐 Pythagoras (c = √(a² + b²) and its wheel neighbours) and 🦊 Fox instinct (sleeping numbers)</li>
    <li><b>Series play:</b> keep the same 4 numbers for 1–20 spins</li>
    <li><b>Money management:</b> base bet, raise after a miss, max bet, all in whole 10-cent steps</li>
    <li><b>Session score:</b> hits, combos, profit and loss</li>
    <li>Works on your phone, right in the browser</li>
  </ul>
  <div id="pp-buttons" style="color-scheme:light;min-height:50px;max-width:420px;width:100%;justify-self:center"></div>
  <div id="payMsg"></div>
  <p class="fine">Pay with PayPal or card. Access opens right after payment on this device; on other devices log in with your PayPal e-mail.<?= is_sub() ? ' Renews monthly; cancel any time in PayPal → Settings → Payments → Manage automatic payments.' : '' ?></p>
</section>

<section class="box">
  <h2>Already bought it?</h2>
  <form method="post" action="login.php">
    <input type="hidden" name="csrf" value="<?= h($tok) ?>">
    <label for="email" class="fine">Your PayPal e-mail</label>
    <input id="email" name="email" type="email" required autocomplete="email" placeholder="you@example.com" style="margin:6px 0 10px">
    <button type="submit">Send me a login link</button>
  </form>
</section>

<script>
const msg=(t,ok)=>{document.getElementById('payMsg').innerHTML=`<div class="msg ${ok?'ok':'err'}">${t}</div>`;};
const SUB=<?= is_sub() ? 'true' : 'false' ?>, PLAN=<?= json_encode((string)cfg('plan_id')) ?>;
const SDK='https://www.paypal.com/sdk/js?client-id=<?= rawurlencode((string)cfg('paypal_client')) ?>&currency=<?= rawurlencode((string)cfg('currency')) ?>'+(SUB?'&vault=true&intent=subscription':'&intent=capture');
function startButtons(){
  if(!window.paypal||!paypal.Buttons){msg('PayPal could not start. Reload the page, or try another browser.',false);return;}
  const done=res=>{if(res.ok){msg('Payment complete! Opening Kitsu… 🦊',true);location.href='app.php';}else msg(res.error||'The payment did not go through.',false);};
  const opts=SUB?{
    createSubscription:(d,actions)=>actions.subscription.create({plan_id:PLAN}),
    onApprove:d=>fetch('api.php?a=subscribe',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:d.subscriptionID})}).then(r=>r.json()).then(done)
  }:{
    createOrder:()=>fetch('api.php?a=create',{method:'POST',credentials:'same-origin'}).then(r=>r.json()).then(d=>{if(!d.ok)throw new Error(d.error||'Could not start the payment.');return d.id;}),
    onApprove:d=>fetch('api.php?a=capture',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:d.orderID})})
      .then(r=>r.json()).then(done)
  };
  opts.onError=e=>{console.error(e);msg('PayPal reported an error. No money was taken; please try again.',false);};
  if(SUB&&!PLAN){msg('Subscriptions are not set up yet. (Site owner: run setup-plan.php and put plan_id in config.php.)',false);return;}
  paypal.Buttons(opts).render("#pp-buttons").catch(e=>{console.error(e);msg('The PayPal button could not be shown: '+(e&&e.message||e),false);});
}
const sdk=document.createElement('script');sdk.src=SDK;sdk.onload=startButtons;
sdk.onerror=()=>msg('PayPal could not load. If you use an ad or privacy blocker, allow paypal.com for this site, or try another browser.',false);
document.head.appendChild(sdk);
setTimeout(()=>{if(!document.querySelector('#pp-buttons iframe')&&!document.querySelector('#payMsg .msg'))msg('The PayPal button is taking long to appear. Reload the page, or try another browser.',false);},10000);
</script>
<?php page_foot();
