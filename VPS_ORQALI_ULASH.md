# 🌐 VPS SERVERGA O‘RNATISH VA TELEGRAM MINI APPNI INTERNETGA CHIQARISH QO‘LLANMASI

Ushbu qo‘llanma orqali platformani **$3–$5 lik arzon VPS serverga** joylashtirib, o‘z domeningiz va avtomatik bepul **HTTPS (SSL)** sertifikat bilan internetga chiqarasiz. Natijada har qanday xaridor o‘z telefonida Telegram botingizga kirib, Mini Appdan to‘liq foydalana oladi.

---

## 📌 BOSQICHMA-BOSQICH REJA:
1. [1-Qadam: VPS Server sotib olish](#1-qadam-vps-server-sotib-olish)
2. [2-Qadam: Domenni VPS IP siga ulash (DNS)](#2-qadam-domenni-vps-ip-siga-ulash-dns)
3. [3-Qadam: Serverga ulanish va 1 klikda o‘rnatish](#3-qadam-serverga-ulanish-va-1-klikda-ornatish)
4. [4-Qadam: Telegram Botga Mini App tugmasini qo‘yish](#4-qadam-telegram-botga-mini-app-tugmasini-qoyish)
5. [5-Qadam: 10 ta do‘konga alohida subdomen ochish (Multi-Store)](#5-qadam-10-ta-dokonga-alohida-subdomen-ochish)

---

## 1-QADAM: VPS SERVER SOTIB OLISH

Tizim juda ixcham va resurslarni kam yeydi. Minimal parametrlar:
* **OS:** Ubuntu 22.04 LTS yoki Ubuntu 24.04 LTS
* **RAM:** 1 GB yoki 2 GB
* **CPU:** 1 Core
* **Disk:** 20 GB SSD

### Tavsiya etiladigan provayderlar:
| Provayder | Narxi | Afzalligi | Sayt |
| :--- | :--- | :--- | :--- |
| **Timeweb Cloud** | ~40,000 so‘m/oy ($3.5) | O‘zbekiston kartalari (Uzcard/Humo) bilan to‘lash mumkin, tezkor | timeweb.cloud |
| **Hetzner Cloud** | €3.79 / oy | Eng arzon va eng sifatli Yevropa serverlari | hetzner.com |
| **Vultr / DigitalOcean** | $4 - $6 / oy | Global standart | vultr.com |

> Server ochilganda sizga **IP manzil** (masalan: `185.196.21.45`) va **root paroli** beriladi.

---

## 2-QADAM: DOMENNI VPS IP SIGA ULASH (DNS)

Telegram Mini App ochilishi uchun albatta **HTTPS** (masalan: `https://shop.mydomain.uz`) kerak.

1. Domeningiz boshqaruv paneliga kiring (Eskiz, Cpanel, Regos, Cloudflare yoki Namecheap).
2. **DNS Records** bo‘limiga o‘ting.
3. Yangi **A-Record** qo‘shing:
   * **Type:** `A`
   * **Name / Host:** `@` (yoki `shop`, ya'ni subdomen)
   * **Value / IP:** Serveringizning IP manzili (masalan: `185.196.21.45`)
   * **TTL:** Auto yoki 300
4. Agar kelajakda boshqa do‘konlarga ham bermoqchi bo‘lsangiz, **Wildcard A-Record** qo‘shib qo‘ying:
   * **Type:** `A`
   * **Name / Host:** `*`
   * **Value:** Serveringiz IP manzili. *(Bu sizga `zara.mydomain.uz`, `dior.mydomain.uz` larni avtomat ishlatish imkonini beradi).*

---

## 3-QADAM: SERVERGA ULANISH VA 1 KLIKDA O‘RNATISH

1. Kompyuteringizda terminalni (yoki PowerShell / PuTTY) oching va serveringizga ulaning:
   ```bash
   ssh root@185.196.21.45
   ```
   *(Parolni so‘raydi, parolni kiritasiz).*

2. Loyihani yuklab oling yoki fayllarni serverga ko‘chiring:
   ```bash
   git clone <sizning_repo_url> /var/www/withmore
   cd /var/www/withmore
   ```
   *(Agar git bo‘lmasa, loyiha papkasini WinSCP orqali `/var/www/withmore` ga tashlashingiz mumkin).*

3. Tayyorlangan avtomatik o‘rnatish skriptini ishga tushiring:
   ```bash
   chmod +x deploy_vps.sh
   sudo bash deploy_vps.sh
   ```

4. Skript sizdan 3 ta narsani so‘raydi:
   * **Domen nomi:** `shop.mydomain.uz`
   * **Telegram Bot Token:** `@BotFather` dan olingan token
   * **Admin Paroli:** Kamida 10 ta belgidan iborat kuchli parol.

**Bo‘ldi!** Skript:
* Python, Caddy veb-server va barcha kutubxonalarni o‘rnatadi.
* Bepul **Let's Encrypt SSL (HTTPS)** sertifikatini oladi va avtomatik ulaydi.
* Tizimni **Systemd servisi** sifatida yoqadi (server o‘chib yonsa ham avtomatik qayta ishlab ketadi).

---

## 4-QADAM: TELEGRAM BOTGA MINI APP TUGMASINI QO‘YISH

1. Telegramda **`@BotFather`** ga kiring.
2. `/mybots` buyrug‘ini bering va botingizni tanlang.
3. **Bot Settings -> Menu Button -> Configure menu button** ga kiring.
4. Botingiz sizdan havola so‘raydi:
   * URL ga domeningizni kiriting:  
     `https://shop.mydomain.uz/miniapp`
5. Tugma nomini yozing:  
     `🛍️ Do'konni ochish` yoki `👔 Katalog`

Endi istalgan odam sizning botingizga kirib **/start** bossa, pastda chap burchakda **"Do'konni ochish"** tugmasi chiqadi va to‘g‘ridan-to‘g‘ri telefonida Mini App ochiladi!

---

## 5-QADAM: 10 TA DO‘KONGA ALOHIDA SUBDOMEN OCHISH (MULTI-STORE)

Agar yangi mijoz (masalan, "Zara Men" do‘koni) paydo bo‘lsa:

1. Serverda bitta buyruq berasiz:
   ```bash
   python setup_store.py --name "Zara Men" --bot_token "ZARA_BOT_TOKEN" --port 8001
   ```
2. `/etc/caddy/Caddyfile` fayliga 4 qator qo‘shasiz:
   ```caddy
   zara.mydomain.uz {
       reverse_proxy 127.0.0.1:8001
   }
   ```
3. Caddy ni yangilaysiz:
   ```bash
   caddy reload --config /etc/caddy/Caddyfile
   ```

Bir zumda `https://zara.mydomain.uz/miniapp` avtomatik HTTPS bilan ishga tushadi! Yangi do‘kon egasi o‘zining botida o‘z tovarlarini sotadi.

---

## 🛠️ FOYDALI BUYRUQLAR (SERVERNI NAZORAT QILISH)

* **Server holatini ko‘rish:**
  ```bash
  systemctl status whitmore
  ```
* **Loglarni real vaqtda ko‘rish (buyurtmalar va xatolar):**
  ```bash
  journalctl -u whitmore -f
  ```
* **Serverni qayta ishga tushirish (yangilanishlardan keyin):**
  ```bash
  systemctl restart whitmore
  ```

