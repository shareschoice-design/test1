<?php
declare(strict_types=1);
define('KITSU', 1);
$CFG = require __DIR__ . '/config.php';
date_default_timezone_set('UTC');

function cfg(string $k) { global $CFG; return $CFG[$k] ?? null; }
function h($s): string { return htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8'); }

function db(): PDO {
  static $pdo = null;
  if ($pdo) return $pdo;
  $dir = __DIR__ . '/data';
  if (!is_dir($dir)) mkdir($dir, 0700, true);
  $file = $dir . '/db_' . substr(hash('sha256', (string)cfg('secret')), 0, 24) . '.sqlite';
  $pdo = new PDO('sqlite:' . $file, null, null, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
  $pdo->exec('PRAGMA journal_mode=WAL');
  $pdo->exec('CREATE TABLE IF NOT EXISTS users(email TEXT PRIMARY KEY, paid_until INTEGER, created INTEGER)');
  $pdo->exec('CREATE TABLE IF NOT EXISTS payments(capture_id TEXT PRIMARY KEY, order_id TEXT, email TEXT, amount TEXT, currency TEXT, created INTEGER)');
  $pdo->exec('CREATE TABLE IF NOT EXISTS sessions(hash TEXT PRIMARY KEY, email TEXT, expires INTEGER)');
  $pdo->exec('CREATE TABLE IF NOT EXISTS login_tokens(hash TEXT PRIMARY KEY, email TEXT, expires INTEGER, used INTEGER DEFAULT 0, created INTEGER)');
  return $pdo;
}

function start_session(): void {
  if (session_status() !== PHP_SESSION_ACTIVE) {
    session_set_cookie_params(['httponly' => true, 'samesite' => 'Lax', 'secure' => is_https()]);
    session_start();
  }
}
function is_https(): bool { return (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') || (($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https'); }
function csrf(): string { start_session(); if (empty($_SESSION['csrf'])) $_SESSION['csrf'] = bin2hex(random_bytes(16)); return $_SESSION['csrf']; }
function csrf_ok(?string $t): bool { start_session(); return is_string($t) && !empty($_SESSION['csrf']) && hash_equals($_SESSION['csrf'], $t); }

// ---------- access ----------
function has_access(string $email): bool {
  $st = db()->prepare('SELECT paid_until FROM users WHERE email=?'); $st->execute([$email]);
  $r = $st->fetch(PDO::FETCH_ASSOC);
  if (!$r) return false;
  return $r['paid_until'] === null || (int)$r['paid_until'] > time();
}
function grant_access(string $email): void {
  $days = (int)cfg('access_days');
  $st = db()->prepare('SELECT paid_until FROM users WHERE email=?'); $st->execute([$email]);
  $r = $st->fetch(PDO::FETCH_ASSOC);
  if ($days <= 0) $until = null;
  else { $from = ($r && $r['paid_until'] !== null && (int)$r['paid_until'] > time()) ? (int)$r['paid_until'] : time(); $until = $from + $days * 86400; }
  if ($r && $r['paid_until'] === null) $until = null; // lifetime stays lifetime
  db()->prepare('INSERT INTO users(email,paid_until,created) VALUES(?,?,?) ON CONFLICT(email) DO UPDATE SET paid_until=excluded.paid_until')
      ->execute([$email, $until, time()]);
}
function current_user(): ?string {
  $t = $_COOKIE['kitsu_s'] ?? '';
  if (!is_string($t) || strlen($t) < 20) return null;
  $st = db()->prepare('SELECT email,expires FROM sessions WHERE hash=?'); $st->execute([hash('sha256', $t)]);
  $r = $st->fetch(PDO::FETCH_ASSOC);
  if (!$r || (int)$r['expires'] < time()) return null;
  return has_access($r['email']) ? $r['email'] : null;
}
function log_in(string $email): void {
  $t = bin2hex(random_bytes(32)); $exp = time() + 365 * 86400;
  db()->prepare('INSERT INTO sessions(hash,email,expires) VALUES(?,?,?)')->execute([hash('sha256', $t), $email, $exp]);
  setcookie('kitsu_s', $t, ['expires' => $exp, 'path' => '/', 'httponly' => true, 'secure' => is_https(), 'samesite' => 'Lax']);
}
function log_out(): void {
  $t = $_COOKIE['kitsu_s'] ?? '';
  if (is_string($t) && $t !== '') db()->prepare('DELETE FROM sessions WHERE hash=?')->execute([hash('sha256', $t)]);
  setcookie('kitsu_s', '', ['expires' => time() - 3600, 'path' => '/', 'httponly' => true, 'secure' => is_https(), 'samesite' => 'Lax']);
}

// ---------- login links ----------
function send_login_link(string $email): void {
  $n = db()->prepare('SELECT COUNT(*) FROM login_tokens WHERE email=? AND created>?'); $n->execute([$email, time() - 3600]);
  if ((int)$n->fetchColumn() >= 5) return; // at most 5 links an hour
  $t = bin2hex(random_bytes(32));
  db()->prepare('INSERT INTO login_tokens(hash,email,expires,created) VALUES(?,?,?,?)')->execute([hash('sha256', $t), $email, time() + 1800, time()]);
  $link = rtrim((string)cfg('site_url'), '/') . '/login.php?t=' . $t;
  send_mail($email, 'Your Kitsu Oracle login link',
    "Hi!\n\nTap this link to open Kitsu Oracle (valid for 30 minutes, works once):\n\n$link\n\nIf you didn't ask for it, just ignore this e-mail.\n\nKitsu 🦊");
}
function use_login_token(string $t): ?string {
  $st = db()->prepare('SELECT email,expires,used FROM login_tokens WHERE hash=?'); $st->execute([hash('sha256', $t)]);
  $r = $st->fetch(PDO::FETCH_ASSOC);
  if (!$r || (int)$r['used'] || (int)$r['expires'] < time()) return null;
  db()->prepare('UPDATE login_tokens SET used=1 WHERE hash=?')->execute([hash('sha256', $t)]);
  return $r['email'];
}
function send_mail(string $to, string $subject, string $body): bool {
  if (cfg('mail_log_only')) {
    file_put_contents(__DIR__ . '/data/mail.log', date('c') . " TO:$to\nSUBJECT:$subject\n$body\n-----\n", FILE_APPEND);
    return true;
  }
  $from = (string)cfg('mail_from'); $name = '=?UTF-8?B?' . base64_encode((string)cfg('mail_name')) . '?=';
  $headers = "From: $name <$from>\r\nReply-To: $from\r\nMIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: 8bit";
  return @mail($to, '=?UTF-8?B?' . base64_encode($subject) . '?=', $body, $headers, '-f' . $from);
}

// ---------- PayPal REST ----------
function paypal_base(): string {
  if (cfg('paypal_api_override')) return rtrim((string)cfg('paypal_api_override'), '/');
  return cfg('paypal_mode') === 'live' ? 'https://api-m.paypal.com' : 'https://api-m.sandbox.paypal.com';
}
function paypal_call(string $method, string $path, ?array $body = null, bool $auth = false): array {
  $ch = curl_init(paypal_base() . $path);
  $headers = ['Accept: application/json'];
  if ($auth) {
    curl_setopt($ch, CURLOPT_USERPWD, cfg('paypal_client') . ':' . cfg('paypal_secret'));
    curl_setopt($ch, CURLOPT_POSTFIELDS, 'grant_type=client_credentials');
  } else {
    $headers[] = 'Authorization: Bearer ' . paypal_token();
    $headers[] = 'Content-Type: application/json';
    if ($body !== null) curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($body === [] ? new stdClass() : $body));
  }
  curl_setopt_array($ch, [CURLOPT_CUSTOMREQUEST => $method, CURLOPT_RETURNTRANSFER => true, CURLOPT_HTTPHEADER => $headers, CURLOPT_TIMEOUT => 30]);
  $res = curl_exec($ch); $code = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE); curl_close($ch);
  $data = json_decode((string)$res, true);
  return ['code' => $code, 'data' => is_array($data) ? $data : []];
}
function paypal_token(): string {
  static $tok = null; if ($tok) return $tok;
  $r = paypal_call('POST', '/v1/oauth2/token', null, true);
  if (empty($r['data']['access_token'])) throw new RuntimeException('PayPal login failed – check paypal_client and paypal_secret in config.php');
  return $tok = $r['data']['access_token'];
}
