<?php
// One-time setup: creates the PayPal product and the monthly plan, then shows the plan_id for config.php.
// Open: https://ggfrog.com/kitsu/setup-plan.php?key=<your "secret" from config.php>   — then DELETE this file.
require __DIR__ . '/lib.php';
header('Content-Type: text/html; charset=utf-8');
if (!hash_equals((string)cfg('secret'), (string)($_GET['key'] ?? ''))) { http_response_code(403); exit('Add ?key=… with the "secret" from config.php to the address.'); }
$out = function (string $t, bool $ok = true) { echo '<p style="font:16px system-ui;color:' . ($ok ? '#0a7' : '#c22') . '">' . $t . '</p>'; };
try {
  $p = paypal_call('POST', '/v1/catalogs/products', ['name' => 'Kitsu Oracle', 'description' => 'Anime roulette companion web app', 'type' => 'SERVICE', 'category' => 'SOFTWARE']);
  if (empty($p['data']['id'])) { $out('Could not create the product (HTTP ' . $p['code'] . '): ' . h(json_encode($p['data'])), false); exit; }
  $plan = paypal_call('POST', '/v1/billing/plans', [
    'product_id' => $p['data']['id'], 'name' => cfg('product_name'), 'status' => 'ACTIVE',
    'billing_cycles' => [[ 'frequency' => ['interval_unit' => 'MONTH', 'interval_count' => 1], 'tenure_type' => 'REGULAR', 'sequence' => 1, 'total_cycles' => 0,
      'pricing_scheme' => ['fixed_price' => ['value' => cfg('price'), 'currency_code' => cfg('currency')]] ]],
    'payment_preferences' => ['auto_bill_outstanding' => true, 'payment_failure_threshold' => 1],
  ]);
  if (empty($plan['data']['id'])) { $out('Could not create the plan (HTTP ' . $plan['code'] . '): ' . h(json_encode($plan['data'])), false); exit; }
  $out('Done! Monthly plan for €' . h(cfg('price')) . ' (' . h(cfg('paypal_mode')) . ') created.');
  $out("Put this into config.php:  'plan_id' => '<b>" . h($plan['data']['id']) . "</b>',");
  $out('Then delete setup-plan.php from the server.', false);
} catch (Throwable $e) { $out('Error: ' . h($e->getMessage()), false); }
