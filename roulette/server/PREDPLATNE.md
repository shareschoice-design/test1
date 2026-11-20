# Přechod na měsíční předplatné + skrytý systém

Co se mění: zákazník zaplatí **9,99 € měsíčně** a PayPal strhává platbu automaticky. Zákazník může kdykoli zrušit ve svém PayPalu a přístup mu zůstane do konce zaplaceného měsíce. Aplikace má nové názvy metod (Spirit Geometry, Fox Instinct) a vzorec už neukazuje.

## 1. Nahraj nové soubory (config.php NEPŘEPISUJ)
Z balíčku nahraj do `/www/kitsu/` a přepiš: `api.php`, `app_html.php`, `index.php`, `lib.php`, `terms.php`, `check.php`, `setup-plan.php`.
**`config.php` nenahrávej**, přišel bys o své klíče.

## 2. Doplň do config.php na serveru dva řádky
Otevři `config.php` na serveru a hned pod řádek `'currency' => 'EUR',` vlož:
```
  'sale_type'     => 'subscription',
  'plan_id'       => '',
```
Řádek `'price' => '9.99',` je teď měsíční cena.

## 3. Vytvoř předplatitelský plán v PayPalu
Otevři v prohlížeči tuhle adresu. Místo TVUJ_SECRET dej text z `'secret'` v config.php:
```
https://ggfrog.com/kitsu/setup-plan.php?key=TVUJ_SECRET
```
Stránka napíše `'plan_id' => 'P-…'`. Zkopíruj to do `config.php` místo `'plan_id' => '',`.
Pak **smaž `setup-plan.php`** ze serveru.

## 4. Zkontroluj a otestuj
- `ggfrog.com/kitsu/check.php`: všechno musí být OK, nově i „Subscription plan set“. Pak check.php zase smaž.
- `ggfrog.com/kitsu/index.php`: musí ukázat cenu „€9.99 / month“ a tlačítka PayPal.
- Zaplať testovací předplatné jiným PayPal účtem. Musí tě to pustit do aplikace.
- Předplatné zruš v PayPalu (Nastavení → Platby → Spravovat automatické platby) a platbu vrať (Aktivita → transakce → Vrátit).

## Dobré vědět
- Kdo už dřív zaplatil jednorázově, má přístup dál navždy.
- Server se PayPalu ptá na stav předplatného nejvýš jednou za 6 hodin na zákazníka. Obnovení přístup prodlouží. Zrušení ho nechá doběhnout do konce zaplaceného měsíce, s rezervou 2 dny.
- Změna ceny později: změň `'price'`, znovu spusť setup-plan.php (vytvoří nový plán) a nový `plan_id` dej do configu. Stávající předplatitelé zůstanou na staré ceně.
- **Úplné skrytí:** kód aplikace je teď zkomprimovaný a zamaskovaný. Zkušený programátor by ho ale v prohlížeči přečíst dokázal. Úplné skrytí by znamenalo počítat čísla na serveru. Dej vědět, jestli to chceš.
