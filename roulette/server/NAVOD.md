# Kitsu Oracle na ggfrog.com – návod

Výsledek: **https://ggfrog.com/kitsu/** je prodejní stránka. Zákazník zaplatí přes PayPal (účtem nebo kartou), server platbu ověří přímo u PayPalu a hned ho pustí do aplikace. Na jiném zařízení zadá svůj PayPal e-mail a přijde mu přihlašovací odkaz. Tenhle odkaz dávej pod videa.

Potřeba: PHP 7.4 nebo novější s rozšířeními **pdo_sqlite** a **curl** (má je skoro každý hosting) a možnost posílat e-maily přes PHP `mail()`.

## 1. PayPal klíče (10 minut)
1. Přihlas se na **developer.paypal.com** svým PayPal Business účtem. Pokud máš osobní účet, převeď ho v PayPalu na Business (zdarma).
2. **Apps & Credentials → Create App**, typ *Merchant*. Nejdřív v záložce **Sandbox**.
3. Zkopíruj **Client ID** a **Secret**.

## 2. Nastavení
Otevři `kitsu/config.php` a vyplň:
- `paypal_client`, `paypal_secret`: klíče z kroku 1
- `paypal_mode`: nech `'sandbox'`, dokud netestuješ
- `price`: cena, třeba `'9.99'`; `access_days`: `0` = navždy, `30` = měsíc
- `mail_from`: adresa na tvé doméně, třeba `frog@ggfrog.com` (ať e-maily nepadají do spamu)
- `secret`: libovolný dlouhý náhodný text (vyplň jednou a už neměň)

## 3. Nahrání
Nahraj celou složku `kitsu` přes FTP nebo správce souborů do kořene webu, aby vznikla adresa `https://ggfrog.com/kitsu/`.
Složka `kitsu/data` musí být zapisovatelná pro PHP (práva 755 nebo 775). Vznikne v ní databáze.

## 4. Test v sandboxu
1. Na developer.paypal.com → **Sandbox accounts** je testovací kupující (Personal) s heslem.
2. Otevři `https://ggfrog.com/kitsu/`, klikni na PayPal a přihlas se tím testovacím kupujícím. Musí tě to pustit do aplikace.
3. V anonymním okně zkus „Send me a login link“ s e-mailem testovacího kupujícího. Musí přijít e-mail s odkazem.

## 5. Ostrý provoz
V PayPal developeru přepni na **Live**, vytvoř aplikaci, zkopíruj **Live** Client ID a Secret, vlož je do `config.php` a nastav `'paypal_mode' => 'live'`. Hotovo.

## Dobré vědět
- **Kdo zaplatil:** v PayPalu (Aktivita) a v databázi `data/db_….sqlite`, tabulky `users` a `payments`.
- **Vrácení peněz:** vrať platbu v PayPalu. Přístup člověku zrušíš smazáním jeho řádku v tabulce `users`.
- **Nginx místo Apache:** soubory `.htaccess` se ignorují. Data jsou i tak chráněná, protože soubor databáze má nepředvídatelný název. Pro jistotu ale v nginx zakaž přístup do `/kitsu/data/`.
- **E-maily nechodí:** zkontroluj u hostingu, že funguje PHP `mail()`, a nastav SPF záznam domény. Pro test můžeš v configu dát `'mail_log_only' => true`; e-maily se pak zapíšou do `data/mail.log`.
- **Obchodní podmínky** jsou v `terms.php`. Doplň do nich své údaje (jméno nebo firma, IČO).
- Stránka i podmínky říkají, že aplikace je zábava a ruletu nepředpovídá. Nech to tam, chrání tě to před reklamacemi a problémy s PayPalem.
