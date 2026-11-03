# STWE - Smart Warehouse Enterprise 🏢📦

یک سیستم مدیریت انبار دسکتاپ حرفه‌ای با رابط کاربری مدرن، مبتنی بر **PySide6** و **SQLite**، با پشتیبانی از دو زبان (فارسی و انگلیسی).

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![PySide6](https://img.shields.io/badge/PySide6-6.5%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

## ✨ ویژگی‌های کلیدی

- 🔐 **سیستم احراز هویت** با دو نقش (مدیر ( admin ) / انباردار( worker )) و رمزنگاری SHA-256
- 📊 **داشبورد مدیریتی** با آمار لحظه‌ ای (تعداد محصولات، موجودی، ارزش سرمایه، کالاهای کم‌موجود)
- 📦 **مدیریت کامل محصولات** با جستجوی پیشرفته و فیلتر کالا های کم‌ موجودی
- 📥 **ورود و خروج کالا** با ثبت خودکار تراکنش‌ها
- 🏷️ **مدیریت دسته‌بندی‌ها** و **تامین‌کنندگان**
- 📜 **تاریخچه کامل تراکنش‌ها**
- 📄 **خروجی PDF** برای گزارش محصولات و تراکنش‌ ها
- 📊 **خروجی Excel** از انبار
- 📈 **نمودار گرافیکی** موجودی با matplotlib
- 💾 **پشتیبان‌گیری و بازیابی** پایگاه داده
- 🌐 **رابط کاربری چندزبانه** (فارسی / انگلیسی) با RTL/LTR خودکار

## 🖥️ پیش‌نیازها

- Python 3.10 یا بالاتر
- pip

## 🚀 نصب و راه‌اندازی

### 1. کلون کردن مخزن
```bash
git clone https://github.com/MohammadAriyaAllahdadi/stwe-warehouse.git
cd stwe-warehouse
