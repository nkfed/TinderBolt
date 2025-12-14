# Шаблон структури документації для Python‑проєктів

Цей шаблон описує рекомендовані документи та їхній зміст. Замініть плейсхолдери у форматі <...> і видаліть підказки після заповнення.

## 1) README.md
- Опис проєкту, функціонал, архітектура (коротко), швидкий старт (локально), Docker (за потреби), приклади, структура, TODO, ліцензія.

## 2) docs/PROJECT_MAP.md
- Детальна карта файлів і папок, ролі, зв’язки, безпека, подальший розвиток.

## 3) docs/ARCHITECTURE.md
- Підхід/патерни, модулі/шари, точки входу, діаграми (Mermaid), потоки даних/стан, обмеження, безпека, поліпшення.

## 4) docs/AI_<DOMAIN>_APP.md (або «How it works»)
- Сценарії/команди/ендпоїнти, логіка станів/діалогів, інтеграції із зовнішніми API/LLM, приклади, помилки.

## 5) docs/modules/*
- На модуль: призначення, класи, функції/методи (параметри/типи/повернення), приклади, залежності, edge cases.

## 6) docs/DEVELOPER_GUIDE.md
- Передумови, локальний запуск (pip/venv), Docker Compose, додавання функціоналу, інтеграція моделей/провайдерів, оновлення залежностей, логування, деплой (за потреби), troubleshooting.

## 7) docs/USER_GUIDE.md
- Як почати, команди/можливості, приклади діалогів, діаграма короткого сценарію (Mermaid), обмеження, приватність/зберігання даних, FAQ.

## 8) docs/TEST_PLAN.md
- Таблиці тест‑кейсів за модулями: «Сценарій | Вхідні дані | Очікуваний результат | Тип тесту». Unit/Integration/Resource/Edge cases.

## 9) REVISION.md
- Інвентар документів, дублікати, неузгодженості, пропуски, пропозиції структури (single‑source), quick‑wins, дорожня карта.

## 10) docs/index.md
- TOC навігація з анотаціями до ключових документів.

## 11) docs/reference/* (single‑source)
- commands.md — єдиний список команд/режимів.
- ai_config.md — параметри моделей/LLM (model, temperature, max_tokens, base_url).

## 12) Файли кореня
- LICENSE, CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, CHANGELOG.md, .env.example (без секретів).

Приклад .env.example:
TELEGRAM_BOT_TOKEN=<your_token>
OPENAI_API_KEY=<your_key>
OPENAI_BASE_URL=https://api.openai.com/v1

## 13) Узгодження стилю
- Мова: українська (або інша) — консистентність термінів; Markdown; діаграми — Mermaid; приклади — позначайте як «псевдокод» за потреби; Python версії — узгоджено в усіх файлах.

## 14) Політика підтримки docs
- Оновлюйте single‑source при будь‑яких змінах; PR‑чекліст у CONTRIBUTING.md: README, index, reference, діаграми, TEST_PLAN.

## 15) Додатково (опційно)
- docs/security/SECURITY.md, docs/OPERATIONS.md, docs/DEPLOYMENT.md, docs/MIGRATIONS.md.

## 16) Чек‑ліст запуску
1) README.md
2) docs/index.md, PROJECT_MAP.md, ARCHITECTURE.md
3) docs/modules/*
4) DEVELOPER_GUIDE.md, USER_GUIDE.md
5) TEST_PLAN.md
6) docs/reference/commands.md, ai_config.md
7) LICENSE, CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, CHANGELOG.md, .env.example
8) REVISION.md