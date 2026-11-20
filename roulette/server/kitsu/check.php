<?php
// Kitsu Oracle – setup check. Upload, open ggfrog.com/kitsu/check.php, then DELETE this file.
declare(strict_types=1);
$rows = [];
$add = function (string $what, bool $ok, string $info = '') use (&$rows) { $rows[] = [$what, $ok, $info]; };

$add('PHP version ' . PHP_VERSION, version_compare(PHP_VERSION, '7.4', '>='), 'needs 7.4 or newer');
$add('SQLite (pdo_sqlite)', extension_loaded('pdo_sqlite'), 'turn on PDO SQLite in the hosting PHP settings');
$add('cURL', extension_loaded('curl'), 'turn on cURL in the hosting PHP settings');
$add('data/ folder writable', is_dir(__DIR__ . '/data') && is_writable(__DIR__ . '/data'), 'set folder data to 755 (or 775)');
$add('data/.htaccess present', file_exists(__DIR__ . '/data/.htaccess'), 'upload data/.htaccess');
$add('.htaccess present', file_exists(__DIR__ . '/.htaccess'), 'upload .htaccess');

$cfg = @include __DIR__ . '/config.php';
$cfgOk = is_array($cfg);
$add('config.php readable', $cfgOk);
$client = $cfgOk ? trim((string)($cfg['paypal_client'] ?? '')) : '';
$secret = $cfgOk ? trim((string)($cfg['paypal_secret'] ?? '')) : '';
$mode = $cfgOk ? (string)($cfg['paypal_mode'] ?? '') : '';
$add('paypal_client filled', strlen($client) > 40 && $client !== 'PASTE_CLIENT_ID', 'length ' . strlen($client) . ', starts with "' . htmlspecialchars(substr($client, 0, 6)) . '…"');
$add('paypal_secret filled', strlen($secret) > 40 && $secret !== 'PASTE_SECRET', 'length ' . strlen($secret));
$add('paypal_mode = sandbox or live', in_array($mode, ['sandbox', 'live'], true), 'now: "' . htmlspecialchars($mode) . '"');
$add('Subscription plan set (plan_id)', !$cfgOk || ($cfg['sale_type'] ?? 'one_time') !== 'subscription' || preg_match('/^P-[A-Z0-9]+$/', (string)($cfg['plan_id'] ?? '')), 'open setup-plan.php?key=YOUR_SECRET and put the plan_id it shows into config.php');
$add('secret changed', $cfgOk && ($cfg['secret'] ?? '') !== 'CHANGE-THIS-TO-A-LONG-RANDOM-TEXT', 'change "secret" in config.php to any long random text');
$add('Spaces around the keys', $cfgOk && $client === (string)($cfg['paypal_client'] ?? '') && $secret === (string)($cfg['paypal_secret'] ?? ''), 'remove spaces/new lines inside the quotes');

// Do the keys work? Ask PayPal for a token (nothing is charged).
if (extension_loaded('curl') && $client && $secret) {
  $base = $mode === 'live' ? 'https://api-m.paypal.com' : 'https://api-m.sandbox.paypal.com';
  $ch = curl_init($base . '/v1/oauth2/token');
  curl_setopt_array($ch, [CURLOPT_USERPWD => $client . ':' . $secret, CURLOPT_POSTFIELDS => 'grant_type=client_credentials',
    CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 20, CURLOPT_HTTPHEADER => ['Accept: application/json']]);
  $res = curl_exec($ch); $code = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE); $err = curl_error($ch); curl_close($ch);
  $tok = json_decode((string)$res, true);
  $ok = $code === 200 && !empty($tok['access_token']);
  $why = $ok ? 'PayPal accepted the keys (' . $mode . ')' :
    ($err ? 'connection error: ' . htmlspecialchars($err) :
     'HTTP ' . $code . ' – ' . htmlspecialchars((string)($tok['error_description'] ?? $tok['error'] ?? 'unknown')) . '. Keys and mode must come from the same tab (Sandbox or Live).');
  $add('PayPal accepts the keys', $ok, $why);
}

// Database test
if (extension_loaded('pdo_sqlite') && is_writable(__DIR__ . '/data')) {
  try { $p = new PDO('sqlite:' . __DIR__ . '/data/_check.sqlite'); $p->exec('CREATE TABLE IF NOT EXISTS t(x)'); $p = null; @unlink(__DIR__ . '/data/_check.sqlite'); $add('Database works', true); }
  catch (Throwable $e) { $add('Database works', false, htmlspecialchars($e->getMessage())); }
}
$add('mail() available', function_exists('mail'), 'ask the hosting to allow PHP mail()');
?><!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Kitsu setup check</title>
<style>body{font:15px/1.5 system-ui,sans-serif;background:#120a24;color:#fff6fb;margin:0;padding:20px}
.w{max-width:720px;margin:0 auto}h1{font-size:22px}table{width:100%;border-collapse:collapse}td{padding:8px;border-bottom:1px solid #3b2470;vertical-align:top}
.ok{color:#3df0ff;font-weight:700}.no{color:#ff3d9a;font-weight:700}.i{color:#b9a8d9;font-size:13px}#pp{margin-top:12px;padding:12px;border:2px solid #3b2470;border-radius:10px}</style></head>
<body><div class="w"><h1>Kitsu Oracle – setup check</h1><table>
<?php foreach ($rows as [$w, $ok, $i]): ?><tr><td><?= $ok ? '<span class="ok">OK</span>' : '<span class="no">FIX</span>' ?></td><td><?= $w ?><div class="i"><?= $ok ? '' : $i ?><?= $ok && $i && strpos($i, 'PayPal accepted') !== false ? $i : '' ?></div></td></tr><?php endforeach; ?>
</table>
<div id="pp">Browser test: loading the PayPal button…</div>
<p class="i">Delete check.php from the server when everything is OK.</p></div>
<script>
const box=document.getElementById('pp');
const s=document.createElement('script');
s.src='https://www.paypal.com/sdk/js?client-id=<?= rawurlencode($client) ?>&currency=<?= rawurlencode((string)($cfg['currency'] ?? 'EUR')) ?>&intent=capture';
s.onload=()=>{ if(!window.paypal){box.innerHTML='<span class="no">FIX</span> PayPal script loaded but did not start.';return;}
  box.innerHTML='<span class="ok">OK</span> PayPal script loaded. Button below:<div id="b" style="margin-top:8px;max-width:320px"></div>';
  paypal.Buttons({createOrder:()=>Promise.reject('test only')}).render('#b').catch(e=>box.insertAdjacentHTML('beforeend','<div class="no">Button failed: '+e+'</div>'));};
s.onerror=()=>{box.innerHTML='<span class="no">FIX</span> The browser could not load PayPal. Either the Client ID is wrong (PayPal answers with an error), or an ad/privacy blocker in this browser blocks paypal.com. Try another browser or turn off the blocker for ggfrog.com.';};
document.head.appendChild(s);
</script></body></html>
