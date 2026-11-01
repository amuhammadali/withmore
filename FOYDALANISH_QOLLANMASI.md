# 📖 DO‘KON EGASI VA MENEYJERLAR UCHUN FOYDALANISH YO‘RIQNOMASI

Ushbu yo‘riqnoma **Whitmore** CRM va Telegram Mini App platformasidan kundalik foydalanish, tovar qo‘shish, buyurtmalarni boshqarish va kargo logistikasini yuritish bo‘yicha to‘liq amaliy qo‘llanmadir.

---

## 📌 MUNDARIJA
1. [Tizimga kirish](#1-tizimga-kirish)
2. [Do‘kon sozlamalari (Brending, Valyuta, Kargo, Karta)](#2-dokon-sozlamalari)
3. [Katalog va Mahsulot qo‘shish](#3-katalog-va-mahsulot-qoshish)
4. [CRM va Buyurtmalarni boshqarish (Kanban)](#4-crm-va-buyurtmalarni-boshqarish-kanban)
5. [Xitoy/Turkiyadan xarid qilish (Ops moduli)](#5-xitoyturkiyadan-xarid-qilish-ops-moduli)
6. [Pochta orqali jo‘natish (BTS / EMU)](#6-pochta-orqali-jonatish-bts--emu)
7. [Mijozlar profili va o‘lchamlar tahlili](#7-mijozlar-profili-va-olchamlar-tahlili)
8. [Zaxira nusxa (Backup) va xavfsizlik](#8-zaxira-nusxa-backup-va-xavfsizlik)

---

## 1. TIZIMGA KIRISH

1. Kompyuteringizda **`run.bat`** faylini ikki marta bosing.
2. Brauzeringizda avtomatik ravishda ochiladi:
   * **Manzil:** `http://localhost:8000/admin`
3. Kirish ma’lumotlari:
   * **Login:** `owner`
   * **Parol:** `.env` faylida ko‘rsatilgan parol.
4. Tizimga kirgach, sizni asosiy **Dashboard (Statistika va Tahlil)** sahifasi kutib oladi.

---

## 2. DO‘KON SOZLAMALARI

Chap menyudan **"Sozlamalar" (Settings)** bo‘limiga kiring. Bu yerda 4 ta asosiy blok mavjud:

### A) Brending (Oq yorliq — White-label)
* **Brend nomi:** Masalan: *Sartorial Men Tashkent*
* **Shior (UZ/RU):** Masalan: *Premium erkaklar liboslari*
* **Brend asosiy ranglari:** Asosiy to‘q rang va oltin urg‘u rangi.
* **Aloqa telefoni va Instagram:** Masalan: `@sartorial_uz`

### B) Narx va Kargo kalkulyatori
* **Yuan kursi (UZS):** Masalan: `1750` so‘m (Xitoydan olingan narx shu kursda hisoblanadi).
* **Kargo tarifi (1 kg uchun):** Masalan: `65000` so‘m / kg.
* **Standart ustama (Marja %):** Masalan: `25%` yoki `30%`.
* **Kalkulyator qoidasi:** Siz mahsulot kiritayotganda faqat Xitoydagi narxini (masalan: 120 yuan) va og‘irligini (0.5 kg) kiritasiz. Tizim avtomatik tarzda O‘zbekistondagi sotish narxini chiqarib beradi!

### C) Logistika va To‘lov
* **To‘lov kartasi:** Uzcard yoki Humo karta raqamingiz hamda karta egasining Ism-Familiyasi.
* **Avans to‘lovi foizi:** Buyurtma berilganda qancha to‘lanishi kerak (masalan: `50%` avans yoki `100%`).
* **Pochta xizmatlari:** BTS Pochta va EMU Pochta (standart jo‘natish narxi: 25,000 so‘m).

### D) Telegram Bot integratsiyasi
* `@BotFather` dan olingan bot tokeni shu yerda ko‘rinadi va tekshiriladi.

---

## 3. KATALOG VA MAHSULOT QO‘SHISH

### A) Yangi mahsulot qo‘shish:
1. Menyudan **"Mahsulotlar" -> "+ Yangi mahsulot"** tugmasini bosing.
2. Quyidagi maydonlarni to‘ldiring:
   * **Nomi (O‘zbekcha va Ruscha):** Masalan: *Klassik Double-Breasted kostyum*.
   * **Kategoriya:** Kostyumlar, Poyabzallar, Shimlar va h.k.
   * **Mato tarkibi:** *70% jun, 30% ipak*.
   * **Sotuv turi:**
     * `Mavjud (In Stock)` — Toshkentdagi omboringizda bor tovarlar.
     * `Buyurtmaga (Preorder)` — Xorijdan buyurtma asosida keltiriladigan tovarlar.
   * **Narx parametrlari:** Xitoydagi narxi (Yuan) va og‘irligi (kg). Tizim soting narxini o‘zi chiqaradi.
   * **O‘lchamlar jadvali (Size Chart):** Ko‘krak, bel va uzunlik o‘lchovlari.
   * **Rasmlar:** Mahsulotning 1 yoki bir nechta sifatli fotosuratini yuklang.
3. **"Saqlash"** tugmasini bosing — mahsulot bir zumda Telegram Mini Appda paydo bo‘ladi!

### B) Tezkor qo‘shish (Quick Add):
* Bir vaqtning o‘zida 10-20 ta tovar rasmini sudrab tashlang (Drag-and-Drop). Tizim ularni qoralama (Draft) qilib yaratadi, siz faqat narxini kiritib faollashtirasiz.

---

## 4. CRM VA BUYURTMALARNI BOSHQARISH (KANBAN)

Menyudan **"CRM Pipeline"** bo‘limini oching. Bu yerda barcha tushgan buyurtmalar 7 ta qulay ustunda (doskada) turadi:

```
[1. Yangi] ──> [2. To'lov kutilmoqda] ──> [3. Xitoydan olindi] ──> [4. Xitoy ombori] ──> [5. Yo'lda] ──> [6. BTS Pochta] ──> [7. Yetkazildi]
```

### Amallar ketma-ketligi:
1. **Yangi buyurtma tushganda:**
   * Tizim xabar beradi. Siz buyurtma ustiga bosib mijoz kiritgan tana o‘lchamlari (bo‘yi, vazni) to‘g‘ri kelishini tekshirasiz.
2. **To‘lovni tasdiqlash:**
   * Mijoz chek yuklagan bo‘lsa, uni tekshirib kartochkani **"To‘lov qabul qilindi"** holatiga o‘tkazasiz.
   * 📲 **Telegram:** Xaridorga avtomatik: *"To‘lovingiz qabul qilindi! Buyurtmangiz Xitoy fabrikasidan xarid qilinmoqda."* degan xabar boradi.
3. **Kargo holatlarini o‘zgartirish:**
   * Tovarni Xitoy omboriga yetib kelganda kartochkani **"Xitoy ombori"** ustuniga surasiz.
   * Tovarlar samolyot/avto kargoga yuklanganda **"Yo‘lda: O‘zbekistonga"** ustuniga surasiz.
   * Har bir bosqichda mijozning botiga avtomatik xushxabar boradi — **mijoz sizni savollar bilan bezovta qilmaydi!**

---

## 5. XITOY/TURKIYADAN XARID QILISH (OPS MODULI)

Menyudan **"Xitoy xaridi (Ops)"** bo‘limiga kiring:
1. Bu yerda to‘lovi tasdiqlangan, lekin hali xarid qilinmagan barcha tovarlar bitta jadvalda chiqadi.
2. Har bir tovar qoshida ta'minotchi havolasi (1688, Taobao, Poizon yoki agent kontaktlari) saqlanadi.
3. Xarid qilib bo‘lgach, ta’minotchi bergan Xitoy ichki trek-kodini kiritib **"Xarid qilindi"** tugmasini bosing.

---

## 6. POCHTA ORQALI JO‘NATISH (BTS / EMU)

Buyurtmalar Toshkentga yetib kelgach:
1. Tovarlar saralanadi va har bir buyurtma kodiga qarab alohida qadoqlanadi.
2. BTS Pochta yoki EMU Pochta filialiga topshiriladi.
3. Pochta kvitansiyasidagi trek-kodni buyurtma kartasiga yozasiz va holatni **"BTS Pochtada"** qilib belgilaysiz.
4. 📲 Xaridorga uning pochta trek-kodi va qaysi filialdan olib ketishi mumkinligi haqida SMS/Telegram xabar boradi.

---

## 7. MIJOZLAR PROFILI VA O‘LCHAMLAR TAHLILI

Menyudan **"Mijozlar"** bo‘limiga kiring:
* Har bir xaridorning ustiga bossangiz, uning shaxsiy sartorial profili ochiladi:
  * Bo‘yi, vazni, odatiy kiyadigan o‘lchami.
  * Avval qaysi tovarlarni xarid qilgani.
  * Umumiy qancha summa savdo qilgani.
* Bu ma'lumotlar orqali keyingi safar mijoz murojaat qilganda unga ikkilanmasdan unga mos o‘lchamni tavsiya qila olasiz.

---

## 8. ZAXIRA NUSXA (BACKUP) VA XAVFSIZLIK

* Har hafta yoki har oyda **Sozlamalar -> Zaxira nusxa** bo‘limiga kirib, **"Ma'lumotlar bazasini yuklab olish"** tugmasini bosing.
* Kompyuteringizga `whitmore_backup.db` fayli yuklanadi. Bu sizning barcha tovarlaringiz, mijozlaringiz va buyurtmalaringizning xavfsiz kafolatidir.

