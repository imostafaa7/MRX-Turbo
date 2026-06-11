⚡ MRX Turbo - Ultra-Fast Automated Recon Framework






























أداة MRX Turbo هي النسخة المتطورة والخارقة من إطار عمل MRX، تم إعادة تصميمها بالكامل لتعتمد على محرك فحص متوازي فائق السرعة. هذه الأداة ليست مجرد سكربت، بل هي نظام أتمتة ذكي يقوم بتهيئة بيئة العمل بالكامل وفحص الأهداف بسرعة البرق.




🚀 لماذا MRX Turbo؟

تم بناء هذه النسخة لكسر حاجز الوقت في عمليات الاستطلاع الأمني. بينما تستغرق الأدوات الأخرى ساعات، تقوم MRX Turbo بإنهاء المهمة في دقائق بفضل تقنية Parallel Attack Engine.

💎 المميزات الحصرية في نسخة Turbo:

•
Parallel Execution Engine: تشغيل ما يصل إلى 20 أداة فحص في وقت واحد، مما يرفع الكفاءة بنسبة 1000%.

•
Auto-Provisioning System: نظام تثبيت ذكي يقوم بتهيئة (Go, Python, Pip, Wordlists, Tools) تلقائياً من أول تشغيل.

•
Rich Interactive CLI: واجهة مستخدم تفاعلية تحتوي على أشرطة تقدم (Progress Bars) حقيقية وجداول نتائج ملونة بدقة عالية.

•
Thread Control: مرونة كاملة في التحكم في عدد المهام المتوازية لتناسب موارد جهازك.

•
Deep JS & Parameter Mining: استخراج وتحليل متقدم للمسارات من ملفات الجافا سكريبت وتصنيف المعاملات لثغرات SQLi و XSS و SSRF.




🛠️ هيكلية العمل (Turbo Phases)

تعمل الأداة عبر 4 مراحل رئيسية مدمجة:

1.
Phase 1: Smart Recon: اكتشاف النطاقات والتحقق من المواقع النشطة (تتابعي لضمان الدقة).

2.
Phase 2: Heavy Scanning (Parallel): إطلاق أدوات (Nmap, FFUF, GAU, Subzy, Nikto) معاً في نفس اللحظة.

3.
Phase 3: Intelligence Mining: استخراج الروابط من JS وفلترة المعاملات الذكية.

4.
Phase 4: Vulnerability Assault (Parallel): إطلاق فاحصات الثغرات (Nuclei, Dalfox, SQLMap, SSRF Test) بشكل متوازي.




📥 التشغيل السريع

لا حاجة لإعداد أي شيء يدوياً، فقط قم بتشغيل السكربت:

Bash


# التشغيل الافتراضي (Turbo Mode)
python3 mrx_turbo.py -d target.com

# التشغيل الفائق (زيادة عدد المهام المتوازية)
python3 mrx_turbo.py -d target.com -t 20






📂 تنظيم النتائج (Turbo Output)

يتم تنظيم النتائج في مجلد ذكي يحتوي على:

•
live.txt: المواقع النشطة المكتشفة.

•
nuclei_results.txt: الثغرات الأمنية الحرجة.

•
params_*.txt: روابط مفلترة وجاهزة للحقن.

•
endpoints.txt: مسارات مكتشفة من ملفات JS.

•
sqlmap_results/: تقارير كاملة عن ثغرات قواعد البيانات.




📜 كلمة من المطور imostafaa9


"في عالم الأمن السيبراني، السرعة هي كل شيء. MRX Turbo صُممت لتمنحك الأفضلية، فهي تجمع بين قوة الأدوات العالمية وسرعة الأتمتة الحديثة. استخدمها بحكمة واحترافية."




MRX Turbo - Breaking the Limits of Security Automation.
Built for imostafaa9

