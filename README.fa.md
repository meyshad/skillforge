<div align="center">

# ⚒️ SkillForge

**مجموعه‌ی Agent Skill برای مهندسی نرم‌افزار حرفه‌ای**<br/>
۱۸ اسکیل تست‌شده که ایجنت برنامه‌نویسی هوش مصنوعی شما را به یک مهندس ارشد منظم تبدیل می‌کند

[English](README.md) · **فارسی**

</div>

<div dir="rtl">

## چرا SkillForge؟

ایجنت‌های برنامه‌نویسی سریع‌اند، اما وقتی راهنما نداشته باشند حدس می‌زنند: کامیت‌های مبهم می‌نویسند، به‌جای علت، علامت باگ را «درست» می‌کنند، PR را بدون خواندن کدهای وابسته تأیید می‌کنند و Dockerfile با کاربر root می‌سازند.

**اسکیل‌ها این مشکل را حل می‌کنند.** هر اسکیل یک پوشه با فایل `SKILL.md` (و در صورت نیاز اسکریپت) است که ایجنت هر وقت کار مرتبطی پیش بیاید، خودکار آن را بارگذاری می‌کند.

- 🎯 **دقیق و مشخص:** مراحل، دستورها، چک‌لیست‌ها و قالب خروجی واقعی
- ✅ **اول اثبات:** هر اسکیل با «ثابتش کن» تمام می‌شود: تست، اندازه‌گیری، ردیابی جریان داده
- 🛠️ **ابزار واقعی:** اسکنر رازها (Secrets) و الگوهای خطرناک کد و تولیدکننده‌ی Changelog، بدون هیچ وابستگی و با تست واحد
- 🔌 **قابل حمل:** فرمت باز `SKILL.md`؛ نصب با یک دستور برای Claude Code، Codex CLI یا هر ایجنتی که پوشه‌ی اسکیل می‌خواند
- 🧩 **ماژولار:** ۵ پلاگین؛ فقط همان را نصب کنید که لازم دارید

## 📦 پلاگین‌ها

| پلاگین | اسکیل‌ها |
|---|---|
| `dev-workflow` | commit-craft · pr-description · code-review · systematic-debugging · tdd-workflow · safe-refactor |
| `security` | security-audit · secret-scanner · dependency-audit |
| `docs` | readme-architect · changelog-keeper · adr-writer · api-docs |
| `devops` | dockerize · github-actions · incident-postmortem |
| `frontend` | accessibility-audit · web-performance |

توضیح کامل هر اسکیل در [README انگلیسی](README.md#-skill-catalog) آمده است.

## ⚡ نصب سریع

**روش ۱: مارکت‌پلیس پلاگین Claude Code**

</div>

```text
/plugin marketplace add meyshad/skillforge
/plugin install dev-workflow@skillforge
```

<div dir="rtl">

**روش ۲: نصب‌کننده‌ی یک‌خطی**

</div>

```bash
curl -fsSL https://raw.githubusercontent.com/meyshad/skillforge/main/scripts/install.sh | bash
```

```bash
./scripts/install.sh --target codex --plugin security
./scripts/install.sh --project --skill code-review
./scripts/install.sh --list
```

<div dir="rtl">

**روش ۳: دستی** — هر پوشه از `plugins/*/skills/` را در پوشه‌ی skills ایجنت خود کپی کنید.

## 🤝 مشارکت

از مشارکت شما استقبال می‌کنیم. از [`template/SKILL.md`](template/SKILL.md) شروع کنید، [راهنمای نوشتن اسکیل](docs/writing-skills.md) را بخوانید و قبل از ارسال PR این دستور را اجرا کنید:

</div>

```bash
python3 scripts/validate.py && python3 -m unittest discover tests
```

<div dir="rtl">

اگر SkillForge به کارتان آمد، با دادن ⭐ به دیگران کمک کنید پیدایش کنند.

مجوز: [MIT](LICENSE)

</div>
