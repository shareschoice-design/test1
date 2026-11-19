<?php
require __DIR__ . '/lib.php';
$user = current_user();
if (!$user) { header('Location: index.php'); exit; }
header('Cache-Control: private, no-store');
require __DIR__ . '/app_html.php';
