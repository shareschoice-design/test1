<?php
// PayPal checkout: the server creates the order with a fixed price and verifies the capture itself.
require __DIR__ . '/lib.php';
header('Content-Type: application/json');
start_session();
$a = $_GET['a'] ?? '';
try {
  if ($a === 'create' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $r = paypal_call('POST', '/v2/checkout/orders', [
      'intent' => 'CAPTURE',
      'purchase_units' => [[ 'description' => cfg('product_name'), 'amount' => ['currency_code' => cfg('currency'), 'value' => cfg('price')] ]],
      'application_context' => ['brand_name' => cfg('mail_name'), 'shipping_preference' => 'NO_SHIPPING', 'user_action' => 'PAY_NOW'],
    ]);
    if (empty($r['data']['id'])) { http_response_code(502); echo json_encode(['ok' => false, 'error' => 'PayPal did not create the order.']); exit; }
    $_SESSION['order'] = $r['data']['id'];
    echo json_encode(['ok' => true, 'id' => $r['data']['id']]); exit;
  }
  if ($a === 'capture' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $in = json_decode((string)file_get_contents('php://input'), true);
    $id = is_array($in) ? (string)($in['id'] ?? '') : '';
    if ($id === '' || ($_SESSION['order'] ?? '') !== $id || !preg_match('/^[A-Z0-9]+$/', $id)) { http_response_code(400); echo json_encode(['ok' => false, 'error' => 'Unknown order.']); exit; }
    $r = paypal_call('POST', '/v2/checkout/orders/' . $id . '/capture', []);
    $d = $r['data'];
    $cap = $d['purchase_units'][0]['payments']['captures'][0] ?? null;
    $email = strtolower(trim((string)($d['payer']['email_address'] ?? '')));
    $ok = ($d['status'] ?? '') === 'COMPLETED' && $cap && ($cap['status'] ?? '') === 'COMPLETED'
       && ($cap['amount']['value'] ?? '') === cfg('price') && ($cap['amount']['currency_code'] ?? '') === cfg('currency')
       && filter_var($email, FILTER_VALIDATE_EMAIL);
    if (!$ok) { http_response_code(402); echo json_encode(['ok' => false, 'error' => 'The payment was not completed.']); exit; }
    $ins = db()->prepare('INSERT OR IGNORE INTO payments(capture_id,order_id,email,amount,currency,created) VALUES(?,?,?,?,?,?)');
    $ins->execute([$cap['id'], $id, $email, $cap['amount']['value'], $cap['amount']['currency_code'], time()]);
    if ($ins->rowCount() === 1) grant_access($email);
    unset($_SESSION['order']);
    log_in($email);
    send_mail($email, 'Welcome to Kitsu Oracle 🦊',
      "Thank you for your purchase!\n\nOpen Kitsu Oracle any time here:\n" . rtrim((string)cfg('site_url'), '/') . "/\n\nOn a new phone or computer, enter this e-mail ($email) and you'll get a login link.\n\nKitsu 🦊");
    echo json_encode(['ok' => true, 'email' => $email]); exit;
  }
  if ($a === 'subscribe' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $in = json_decode((string)file_get_contents('php://input'), true);
    $id = is_array($in) ? (string)($in['id'] ?? '') : '';
    if (!preg_match('/^I-[A-Z0-9]+$/', $id)) { http_response_code(400); echo json_encode(['ok' => false, 'error' => 'Unknown subscription.']); exit; }
    $r = paypal_call('GET', '/v1/billing/subscriptions/' . $id);
    $d = $r['data']; $status = (string)($d['status'] ?? '');
    $email = strtolower(trim((string)($d['subscriber']['email_address'] ?? '')));
    $ok = $r['code'] === 200 && in_array($status, ['ACTIVE', 'APPROVED'], true) && ($d['plan_id'] ?? '') === cfg('plan_id') && filter_var($email, FILTER_VALIDATE_EMAIL);
    if (!$ok) { http_response_code(402); echo json_encode(['ok' => false, 'error' => 'The subscription is not active.']); exit; }
    $taken = db()->prepare('SELECT email FROM users WHERE sub_id=? AND email<>?'); $taken->execute([$id, $email]);
    if ($taken->fetchColumn()) { http_response_code(409); echo json_encode(['ok' => false, 'error' => 'This subscription belongs to another account.']); exit; }
    $next = strtotime((string)($d['billing_info']['next_billing_time'] ?? '')) ?: (time() + 31 * 86400);
    start_sub($email, $id, $next + 2 * 86400, $status);
    log_in($email);
    send_mail($email, 'Welcome to Kitsu Oracle 🦊',
      "Thank you for subscribing!\n\nOpen Kitsu Oracle any time here:\n" . rtrim((string)cfg('site_url'), '/') . "/index.php\n\nOn a new phone or computer, enter this e-mail ($email) and you'll get a login link.\n\nYour subscription renews every month. Cancel any time in PayPal: Settings → Payments → Manage automatic payments.\n\nKitsu 🦊");
    echo json_encode(['ok' => true, 'email' => $email]); exit;
  }
  http_response_code(404); echo json_encode(['ok' => false]);
} catch (Throwable $e) {
  error_log('kitsu api: ' . $e->getMessage());
  http_response_code(500); echo json_encode(['ok' => false, 'error' => 'Server error. Please try again.']);
}
