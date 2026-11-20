<?php
// Mail test. Open: https://ggfrog.com/kitsu/mailtest.php?key=<secret from config.php>&to=you@example.com   — then DELETE this file.
require __DIR__ . '/lib.php';
header('Content-Type: text/html; charset=utf-8');
if (!hash_equals((string)cfg('secret'), (string)($_GET['key'] ?? ''))) { http_response_code(403); exit('Add ?key=… (the "secret" from config.php) and &to=your e-mail to the address.'); }
$to = strtolower(trim((string)($_GET['to'] ?? '')));
$line = function (string $t, bool $ok) { echo '<p style="font:16px system-ui;color:' . ($ok ? '#0a7' : '#c22') . '">' . ($ok ? 'OK – ' : 'PROBLEM – ') . $t . '</p>'; };
if (!filter_var($to, FILTER_VALIDATE_EMAIL)) { $line('add &to=your@email to the address', false); exit; }
$line('lib.php is the new version (free_emails supported)', strpos((string)file_get_contents(__DIR__ . '/lib.php'), 'free_emails') !== false);
$line("$to has access (paid or in free_emails)", has_access($to));
$line('mail_log_only is ' . (cfg('mail_log_only') ? 'ON – e-mails go to data/mail.log, not to the inbox' : 'off'), !cfg('mail_log_only'));
$n = db()->prepare('SELECT COUNT(*) FROM login_tokens WHERE email=? AND created>?'); $n->execute([$to, time() - 3600]); $cnt = (int)$n->fetchColumn();
$line('login links asked in the last hour: ' . $cnt . ' (max 5)', $cnt < 5);
$sent = send_mail($to, 'Kitsu Oracle – mail test', "If you can read this, PHP mail() works on ggfrog.com.\n\nKitsu 🦊");
$line('PHP mail() accepted the test e-mail to ' . h($to) . ' from ' . h(cfg('mail_from')) . ' (check inbox and spam in 1–2 minutes)', $sent);
echo '<p style="font:14px system-ui;color:#666">Delete mailtest.php when done.</p>';
