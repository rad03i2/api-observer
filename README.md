# API Observer

A small, local, dependency-free HTTP API health monitor for developers, homelabs, CI jobs, and lightweight operations. API Observer checks endpoints, evaluates useful assertions, records durable history in SQLite, and returns automation-friendly exit codes and JSON.

> **Author:** Radwan Abdulhadi Ahmed · رضوان عبدالهادي أحمد · [@rad03i2](https://github.com/rad03i2)

## Why it exists
Full monitoring platforms are excellent, but they can be excessive when you only need repeatable endpoint checks from a laptop, server, cron job, or CI runner. API Observer provides that narrow workflow with Python's standard library and data that stays on your machine.

## Features
- GET, HEAD, POST, PUT, PATCH, and DELETE checks.
- Expected HTTP status as one value or a list.
- Maximum latency assertions.
- Regular-expression response assertions.
- JSON dot/index path assertions such as `data.items.0.id` plus exact-value checks.
- Optional headers and JSON/text request bodies.
- Configurable timeout and response-size cap (1 MB by default).
- One-shot mode with exit code `0` when all checks pass and `1` when any check fails.
- Continuous watch mode with a validated interval.
- SQLite history using WAL mode, recent-history output, and retention pruning.
- Human-readable and JSON output.
- No telemetry, accounts, cloud backend, API keys, or runtime third-party packages.

## Requirements
Python 3.10 or newer.

## Installation
```bash
git clone https://github.com/rad03i2/api-observer.git
cd api-observer
python -m pip install -e .
```

For development/tests:
```bash
python -m pip install -e . pytest
python -m pytest -q
```

## Quick start
The repository includes `examples/checks.json` using a public endpoint and no credentials.

```bash
api-observer run examples/checks.json
api-observer run examples/checks.json --json
api-observer watch examples/checks.json --interval 60
api-observer history --limit 20
api-observer history --limit 20 --json
api-observer prune --keep-days 30
```

Use another history database when needed:
```bash
api-observer --db ./observer.db run checks.json
```

### Configuration
```json
{
  "checks": [
    {
      "name": "Health API",
      "url": "https://example.com/health",
      "method": "GET",
      "expected_status": [200, 204],
      "max_latency_ms": 1500,
      "body_regex": "healthy",
      "timeout": 5,
      "max_body_bytes": 250000
    },
    {
      "name": "JSON health",
      "url": "https://example.com/api/health",
      "json_path": "service.status",
      "json_equals": "ok"
    }
  ]
}
```

`headers` and `body` are also supported. Object/list bodies are JSON-encoded and receive `Content-Type: application/json` unless you set it yourself.

## Exit codes
| Code | Meaning |
|---|---|
| `0` | all checks passed / informational command succeeded |
| `1` | one or more checks failed |
| `2` | invalid configuration or CLI input |

## Project structure
```text
src/api_observer/core.py     HTTP engine, validation, assertions
src/api_observer/storage.py  SQLite history and retention
src/api_observer/cli.py      CLI, config loading, watch mode
examples/checks.json         safe example configuration
tests/                       mocked deterministic tests
.github/workflows/ci.yml     cross-platform test matrix
```

## Testing and validation
The test suite covers nested JSON paths, URL validation, JSON assertions, regex assertions, SQLite persistence/pruning, configuration loading, and failure exit codes. Network behavior is mocked so tests do not depend on external services. CI runs Python 3.10, 3.12, and 3.13 on Ubuntu, Windows, and macOS.

## Preview / screenshot guidance
This is intentionally a terminal-first project. For a portfolio screenshot, run `api-observer run examples/checks.json` and `api-observer history --limit 5` in a clean terminal. No screenshot is committed because terminal rendering varies by OS and theme.

## Security and privacy
API Observer has no telemetry and persists no response bodies. It stores check name, URL, pass/fail result, status, latency, timestamp, and diagnostic message locally. Configuration may contain authentication headers or request bodies; keep such files outside version control. Do not execute configuration supplied by an untrusted party because the tool intentionally makes network requests to configured URLs. See [SECURITY.md](SECURITY.md).

## Limitations
- No TLS-certificate expiry check, DNS metrics, distributed probes, alert delivery, or web dashboard.
- No OAuth/token refresh mechanism; static headers are sent exactly as configured.
- JSON paths support simple dot-separated dictionary keys and numeric list indexes, not JSONPath syntax.
- Watch mode is foreground-only and does not provide daemon/service management.
- History SQLite is not encrypted.

## Optional roadmap
Potential future additions include percentile summaries, TLS-expiry checks, JUnit output, and opt-in alert adapters. These are not implemented features today.

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). Keep tests deterministic and update both language sections for user-facing changes.

## License
MIT — see [LICENSE](LICENSE).

## Author
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: [@rad03i2](https://github.com/rad03i2)

---

# API Observer — العربية

أداة محلية صغيرة لمراقبة صحة واجهات HTTP API، موجهة للمطورين والخوادم المنزلية ومهام CI والمراقبة الخفيفة. تفحص نقاط النهاية، وتتحقق من شروط عملية، وتحفظ السجل في SQLite، وتوفر مخرجات JSON ورموز خروج مناسبة للأتمتة، وكل ذلك بدون حزم تشغيل خارجية.

## لماذا هذا المشروع؟
منصات المراقبة الكبيرة ممتازة، لكنها قد تكون أكثر من المطلوب عندما تحتاج فقط إلى فحوصات HTTP قابلة للتكرار من حاسوب أو خادم أو مهمة مجدولة. يوفر API Observer هذا الاستخدام المحدد مع إبقاء البيانات محليًا.

## المميزات
- دعم GET وHEAD وPOST وPUT وPATCH وDELETE.
- التحقق من رمز HTTP المتوقع، كقيمة واحدة أو عدة قيم.
- حد أقصى اختياري لزمن الاستجابة.
- التحقق من نص الاستجابة بتعبير منتظم.
- فحص JSON بمسارات بسيطة مثل `data.items.0.id` مع مقارنة قيمة دقيقة.
- رؤوس HTTP وطلبات JSON أو نصية اختيارية.
- مهلة اتصال وحد أقصى لحجم الاستجابة؛ الافتراضي 1 ميغابايت.
- تشغيل مرة واحدة برمز خروج واضح للأتمتة.
- وضع مراقبة مستمرة بفاصل زمني متحقق منه.
- سجل SQLite مع WAL وعرض أحدث النتائج وحذف السجلات القديمة.
- مخرجات بشرية أو JSON.
- لا Telemetry ولا حسابات ولا Backend سحابي ولا مفاتيح API مطلوبة.

## المتطلبات والتثبيت
يتطلب Python 3.10 أو أحدث.

```bash
git clone https://github.com/rad03i2/api-observer.git
cd api-observer
python -m pip install -e .
```

للاختبارات:
```bash
python -m pip install -e . pytest
python -m pytest -q
```

## الاستخدام
```bash
api-observer run examples/checks.json
api-observer run examples/checks.json --json
api-observer watch examples/checks.json --interval 60
api-observer history --limit 20
api-observer prune --keep-days 30
```

ملف الإعداد يحتوي مصفوفة `checks`. لكل فحص يلزم `name` و`url`، ويمكن إضافة `method` و`expected_status` و`max_latency_ms` و`body_regex` و`json_path` و`json_equals` و`headers` و`body` و`timeout` و`max_body_bytes`.

## بنية المشروع
المحرك والتحقق في `src/api_observer/core.py`، وسجل SQLite في `storage.py`، وواجهة الأوامر في `cli.py`، مع مثال آمن في `examples/` واختبارات في `tests/` وCI متعدد الأنظمة في `.github/workflows/ci.yml`.

## الاختبارات
تغطي الاختبارات مسارات JSON والتحقق من الروابط وشروط JSON والتعبيرات المنتظمة وتخزين SQLite وحذف السجلات القديمة وتحميل الإعدادات ورمز الخروج عند الفشل. اتصالات الشبكة Mocked داخل الاختبارات حتى تبقى النتائج ثابتة. يشغّل CI الإصدارات 3.10 و3.12 و3.13 على Ubuntu وWindows وmacOS.

## المعاينة
المشروع موجه للطرفية. للحصول على صورة عرض للمشروع، شغّل فحص المثال ثم أمر `history` في طرفية نظيفة. لم تُضف صورة ثابتة لأن شكل الطرفية يختلف حسب النظام والثيم.

## الخصوصية والأمان
لا يرسل المشروع Telemetry ولا يحفظ أجسام الاستجابات. يحفظ محليًا الاسم والرابط والنتيجة ورمز HTTP والزمن والتوقيت ورسالة التشخيص. قد تحتوي ملفات الإعداد على رموز مصادقة، لذلك لا ترفعها إلى GitHub. لا تشغّل إعدادات من مصدر غير موثوق لأنها قد تطلب عناوين شبكة داخلية. راجع [SECURITY.md](SECURITY.md).

## القيود
لا توجد حاليًا تنبيهات أو لوحة ويب أو مجسات موزعة أو فحص لانتهاء شهادة TLS أو تحديث تلقائي لرموز OAuth. مسار JSON بسيط وليس JSONPath كاملًا. وضع `watch` يعمل في الواجهة الأمامية وليس كخدمة نظام، وقاعدة SQLite غير مشفرة.

## تطوير اختياري
يمكن مستقبلًا إضافة إحصاءات percentile وفحص TLS ومخرجات JUnit ومحولات تنبيه اختيارية. هذه ليست ميزات منفذة حاليًا.

## المساهمة والترخيص
راجع [CONTRIBUTING.md](CONTRIBUTING.md). المشروع مرخص برخصة MIT الموجودة في [LICENSE](LICENSE).

## المؤلف
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: [@rad03i2](https://github.com/rad03i2)
