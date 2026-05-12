# 🧠 MemForensics Framework — توثيق شامل ومفصل

---

## 📌 نظرة عامة على المشروع

**MemForensics** هو تطبيق Desktop مبني بـ Python + PyQt5، هدفه تحليل ملفات **Memory Dump** (صور الذاكرة العشوائية RAM) بشكل **أوتوماتيكي بالكامل** من غير ما المستخدم يحتاج يكتب أي أمر في الـ Terminal.

المستخدم بيعمل حاجة واحدة بس: **يحمّل ملف الـ Memory Dump** → والبرنامج بيشغل **5 عمليات تحليل متتالية (Pipeline)** في الخلفية ويعرض النتائج في Dashboard احترافي.

---

## 🎯 هدف المشروع

في مجال الـ Digital Forensics، الـ **Volatile Data** (البيانات المؤقتة) زي:
- العمليات الشغالة (Processes)
- الاتصالات النشطة (Network Connections)
- كلمات السر والـ Hashes
- الأكواد الخبيثة المحقونة (Injected Malware)

كل ده موجود **فقط في الـ RAM**. لما الجهاز يتقفل → البيانات دي **بتتمسح نهائياً**.

### المشكلة:
الأدوات التقليدية زي Volatility بتشتغل من الـ Command Line وبتحتاج خبرة كبيرة وتشغيل Plugin بـ Plugin يدوي.

### الحل:
MemForensics بيعمل **أتمتة كاملة** — بيشغل كل الـ Plugins المطلوبة تلقائياً ويعرض النتائج في واجهة رسومية جميلة.

---

## 🛠 التقنيات المستخدمة (Tech Stack)

| المكوّن | التقنية | الوظيفة |
|---------|---------|---------|
| لغة البرمجة | **Python 3.10+** | المنطق الأساسي للتطبيق |
| واجهة المستخدم | **PyQt5** | Dashboard بـ Dark Theme احترافي |
| محرك التحليل | **Volatility3** | تحليل ملفات الـ Memory Dump |
| كشف البرمجيات الخبيثة | **YARA-Python** | فحص الذاكرة بقواعد Signatures |
| التشفير | **PyCryptodome + Cryptography** | مطلوبين من Volatility لاستخراج الـ Credentials |

### ملف `requirements.txt`:
```
PyQt5>=5.15
volatility3>=2.0
yara-python>=4.0
pycryptodome>=3.0
cryptography>=3.0
```

---

## 📁 هيكل المشروع (Project Structure)

```
MemForensics_Framework/
│
├── main.py                          # نقطة البداية — بيشغل التطبيق
├── requirements.txt                 # المكتبات المطلوبة
├── run.bat                          # ملف تشغيل سريع بضغطة واحدة
├── .gitignore                       # الملفات المتجاهلة من Git
│
├── core/                            # المنطق الأساسي (Backend)
│   ├── __init__.py                  # تعريف الـ Package
│   ├── vol_wrapper.py               # Wrapper حوالين Volatility3
│   └── yara_scanner.py              # نظام فحص YARA
│
├── gui/                             # واجهة المستخدم (Frontend)
│   ├── __init__.py                  # تعريف الـ Package
│   └── main_window.py               # الواجهة الرئيسية الكاملة (778 سطر)
│
├── yara_rules/                      # قواعد YARA للكشف عن الـ Malware
│   ├── example.yar                  # قاعدة مثال بسيطة
│   ├── gen_suspicious_strings.yar   # كشف Strings مشبوهة (من النت)
│   ├── apt_cobaltstrike.yar         # كشف CobaltStrike (من النت)
│   ├── gen_mimikatz.yar             # كشف Mimikatz (من النت)
│   ├── all_rules.yar                # كل القواعد مدمجة (يتولّد أوتوماتيك)
│   └── _merged_rules.yar            # نسخة مدمجة تانية
│
├── package.json                     # (لتوليد العروض التقديمية — مش جزء من التطبيق)
├── pr.js                            # سكربت توليد Presentation
└── pr_tech.js                       # سكربت توليد Technical Presentation
```

---

## 📄 شرح كل ملف بالتفصيل

---

### 1️⃣ `main.py` — نقطة البداية (Entry Point)

**الوظيفة:** أول ملف بيتشغل — بيعمل 3 حاجات:

1. **`check_requirements()`** — بيتأكد إن كل المكتبات مثبتة:
   - بيدوّر على `pip.exe` في الـ Virtual Environment
   - لو لقاه → بيشغل `pip install -r requirements.txt` تلقائياً
   - لو ملقاهوش → بيستخدم الـ System pip

2. **`main()`** — بيشغل التطبيق:
   - بيعمل `QApplication` (التطبيق)
   - بيضبط الخط على **Segoe UI, size 10**
   - بيضبط الـ Style على **Fusion** (ده الـ Style اللي بيسمح بالتخصيص الكامل)
   - بيعمل `MainWindow()` ويعرضها

**يعني ببساطة:** المستخدم بيشغل `python main.py` → البرنامج بيثبّت أي حاجة ناقصة → بيفتح الواجهة.

---

### 2️⃣ `core/vol_wrapper.py` — غلاف Volatility3

**الوظيفة:** ده الملف اللي بيتكلم مع أداة **Volatility3** عن طريق الـ Command Line.

#### Class: `VolatilityManager`

**`__init__(self, dump_path)`**
- بياخد مسار ملف الـ Memory Dump
- بيدوّر على `vol.exe` (أداة Volatility) في 3 أماكن:
  1. الـ Virtual Environment (`venv/Scripts/vol.exe`)
  2. الـ System PATH (`shutil.which("vol")`)
  3. Fallback على الأمر `vol` مباشرة

**`run_command(self, plugin_name, extra_args=[])`**
- بيشغل أمر Volatility كـ subprocess:
  ```
  vol -f <dump_path> -r json <plugin_name> [extra_args]
  ```
- الـ `-r json` معناها الناتج يطلع JSON (بدل النص العادي)
- الـ Timeout: **300 ثانية** (5 دقايق)
- لو حصل Error → بيرجع قائمة فاضية `[]`

**`run_pslist()`** — بيشغل Plugin: `windows.pslist.PsList`
- بيرجع: PID, Name, PPID, Threads, Handles, Session, CreateTime, ExitTime
- **الهدف:** استخراج كل العمليات (الشغالة والمنتهية) من الذاكرة

**`run_netscan()`** — بيشغل Plugin: `windows.netscan.NetScan`
- بيرجع: Protocol, LocalAddr, LocalPort, ForeignAddr, ForeignPort, State, PID, Owner
- **الهدف:** استخراج كل الاتصالات الشبكية (TCP/UDP)

**`run_malfind()`** — بيشغل Plugin: `windows.malfind.Malfind`
- بيرجع: PID, Process, Start VPN, End VPN, Protection, Hexdump, Disasm
- **الهدف:** كشف الأكواد المحقونة — بيدوّر على مناطق ذاكرة بصلاحيات `PAGE_EXECUTE_READWRITE` (علامة على Code Injection)

**`run_hashdump()`** — بيشغل Plugin: `windows.hashdump`
- بيرجع: User, RID, LM Hash, NTLM Hash
- **الهدف:** استخراج الـ Password Hashes من الـ SAM Database في الذاكرة

**`run_yarascan(self, yara_file)`** — بيشغل Plugin: `windows.yarascan.YaraScan`
- بياخد ملف YARA إضافي كـ argument: `--yara-file <path>`
- بيرجع: Rule, PID, Process, Offset, Match
- **الهدف:** فحص الذاكرة بقواعد YARA للكشف عن Malware معروف

---

### 3️⃣ `core/yara_scanner.py` — نظام فحص YARA

**الوظيفة:** بيدير قواعد YARA — تحميل، دمج، وتشغيل.

#### Class: `YaraScanner`

**`__init__(self)`**
- بيعمل مجلد `yara_rules/` لو مش موجود
- بيحدد **3 URLs** لتحميل قواعد YARA من GitHub

#### 🌐 مصادر البيانات الخارجية (External Data Sources)

القواعد بتتحمل من مستودع **[Neo23x0/signature-base](https://github.com/Neo23x0/signature-base)** على GitHub:

| الملف | بيكشف إيه |
|-------|-----------|
| `gen_suspicious_strings.yar` | Strings مشفرة ومشبوهة، أنماط Obfuscation |
| `apt_cobaltstrike.yar` | CobaltStrike Beacons و Shellcode |
| `gen_mimikatz.yar` | أداة Mimikatz لسرقة كلمات السر |

> **Neo23x0** هو Florian Roth — واحد من أشهر الباحثين في مجال Threat Intelligence.

**`download_missing_rules()`** — بيتشيك على كل ملف — لو مش موجود بيحمله. لو الانترنت مش شغال → بيتجاهل.

**`merge_all_rules()`** — بيجمع كل ملفات `.yar` في ملف واحد `all_rules.yar`. لو ملف فيه Error → بيتخطاه.

**`auto_scan(self, dump_path)`** — بيعمل كل الخطوات أوتوماتيك: تحميل → دمج → فحص.

---

### 4️⃣ `gui/main_window.py` — الواجهة الرئيسية (778 سطر)

**ده أكبر ملف في المشروع** — فيه كل الواجهة الرسومية والمنطق بتاع الـ Pipeline.

#### الألوان (Color Palette):
- `#0B0E14` — خلفية رئيسية (أسود غامق)
- `#111621` — خلفية الـ Sidebar
- `#00E5A0` — اللون الأساسي (أخضر نيون)
- `#FF6B6B` — أحمر للتحذيرات
- `#FFD93D` — أصفر للتنبيهات
- `#6CB4EE` — أزرق للمعلومات

#### المكونات:

**`VolWorker(QThread)`** — Background Thread لعمليات Volatility (الواجهة مبتتعلقش)

**`YaraWorker(QThread)`** — Background Thread لفحص YARA

**`NavButton`** — زرار تنقل في الـ Sidebar (4 أزرار: Processes, Network, Credentials, Malware Scan)

**`StatCard`** — كارت إحصائيات بـ Glow Effect

**`ForensicsPage`** — صفحة عرض بيانات فيها جدول + عنوان + Copy Support

**`MainWindow`** — النافذة الرئيسية: Sidebar + Top Bar + Stat Cards + 4 Pages + Status Bar

---

## 🔄 الـ Pipeline — خطوات التحليل الـ 5

```
📂 Load Memory Dump
    │
    ├──▶ [1/5] Process Extraction   (pslist)    → جدول العمليات + كارت العدد
    ├──▶ [2/5] Network Recovery     (netscan)   → جدول الشبكة + كارت العدد
    ├──▶ [3/5] Injection Detection  (malfind)   → جدول الـ Malware + كارت العدد
    ├──▶ [4/5] Credential Recovery  (hashdump)  → جدول الـ Credentials + كارت العدد
    └──▶ [5/5] YARA Signature Scan  (yarascan)  → يضيف النتائج لجدول الـ Malware
                                                   ✅ اكتمل التحليل
```

**كل خطوة:** بتشتغل في Background Thread | لو فشلت بيكمل | نتائج YARA بتتميز بـ `[YARA]` prefix.

---

## 🔄 طريقة الشغل الداخلية (Internal Flow)

```
المستخدم يضغط "Load Memory Dump"
    ▼
QFileDialog — اختيار ملف (.raw / .mem / .dmp / .vmem / .lime / .img)
    ▼
MainWindow._load_dump() — بيحفظ المسار + يعرض اسم الملف وحجمه
    ▼
_run_pslist() → VolWorker(Thread) → VolatilityManager.run_pslist()
    ▼
subprocess.run(["vol", "-f", dump, "-r", "json", "windows.pslist.PsList"])
    ▼
JSON → parse → rows → Signal(finished) → يملى الجدول → يشغل الخطوة التالية
    ▼
... نفس الباترن لكل خطوة ...
    ▼
_on_yarascan_done() → يضيف نتائج YARA لجدول Malware → ✅ Pipeline Complete
```

---

## 🔧 أدوات خارجية أساسية

### Volatility3
- **إيه هو:** أشهر أداة Open Source لتحليل Memory Dumps
- **بيشتغل ازاي:** من الـ Command Line — `vol -f <dump> <plugin>`
- **البرنامج بيستخدمه ازاي:** بيشغله كـ `subprocess` مع output بـ JSON
- **الـ Plugins المستخدمة:** `pslist`, `netscan`, `malfind`, `hashdump`, `yarascan`

### YARA
- **إيه هو:** أداة لكتابة قواعد لكشف الـ Malware بناءً على Patterns
- **البرنامج بيستخدمه ازاي:** `yara-python` للـ Compile Test + Volatility Plugin `yarascan` للفحص الفعلي

---

## 👥 فريق العمل

| الاسم | الدور |
|-------|-------|
| **Eslam Ebrahim** | Developer & Architect |
| **Ahmed Emad** | Developer & Testing |
| **Mohamed Wael** | Developer & Documentation |

**المشرف:** Dr. Maryam Adel | **المادة:** Advanced Digital Forensics

---

## 📊 إحصائيات الكود

| الملف | عدد الأسطر | الحجم |
|-------|-----------|-------|
| `main.py` | 41 | 1.1 KB |
| `core/vol_wrapper.py` | 117 | 4.3 KB |
| `core/yara_scanner.py` | 73 | 2.9 KB |
| `gui/main_window.py` | 778 | 33.8 KB |
| **المجموع** | **~1009** | **~42 KB** |

---

## ✅ ملخص سريع

| السؤال | الإجابة |
|--------|---------|
| المشروع بيعمل إيه؟ | تحليل Memory Dumps أوتوماتيكياً |
| مكتوب بإيه؟ | Python + PyQt5 |
| بيستخدم إيه في التحليل؟ | Volatility3 (subprocess) |
| بيكشف Malware ازاي؟ | malfind + YARA Rules |
| القواعد جاية منين؟ | Neo23x0/signature-base من GitHub |
| الواجهة إيه؟ | PyQt5 Dashboard بـ Dark Theme |
| بيشتغل ازاي؟ | `python main.py` أو `run.bat` |
| بيدعم أنهي ملفات؟ | `.raw`, `.mem`, `.dmp`, `.vmem`, `.lime`, `.img` |
