<?php
require __DIR__ . '/lib.php';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
  $email = strtolower(trim((string)($_POST['email'] ?? '')));
  if (csrf_ok($_POST['csrf'] ?? null) && filter_var($email, FILTER_VALIDATE_EMAIL) && has_access($email)) send_login_link($email);
  header('Location: index.php?sent=1'); exit; // same answer either way, so nobody can test which e-mails bought
}
$t = (string)($_GET['t'] ?? '');
$email = preg_match('/^[a-f0-9]{64}$/', $t) ? use_login_token($t) : null;
if ($email && has_access($email)) { log_in($email); header('Location: app.php'); exit; }
header('Location: index.php?expired=1');
