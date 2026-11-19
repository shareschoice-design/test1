<?php
// ===== Kitsu Oracle – settings. Fill these in on your server. =====
return [
  // Full address of this folder, without a trailing slash
  'site_url'      => 'https://ggfrog.com/kitsu',

  // PayPal app keys from developer.paypal.com → Apps & Credentials
  'paypal_mode'   => 'sandbox',            // 'sandbox' for testing, 'live' for real payments
  'paypal_client' => 'PASTE_CLIENT_ID',
  'paypal_secret' => 'PASTE_SECRET',

  // Price
  'price'         => '9.99',               // with a dot, two decimals
  'currency'      => 'EUR',
  'product_name'  => 'Kitsu Oracle – full access',
  'access_days'   => 0,                    // 0 = lifetime access, 30 = one month, …

  // E-mails (login links). The address should be on your domain.
  'mail_from'     => 'kitsu@ggfrog.com',
  'mail_name'     => 'Kitsu Oracle',
  'mail_log_only' => false,                // true = write e-mails to data/mail.log instead of sending (testing)

  // Long random text, used to name the database file. Change it once, then never again.
  'secret'        => 'CHANGE-THIS-TO-A-LONG-RANDOM-TEXT',

  // Only for local testing: a fake PayPal address. Leave empty on the server.
  'paypal_api_override' => '',
];
