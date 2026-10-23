# АльфаДент Mini App — пакет обновления без перезаписи Telegram-бота

Этот архив содержит изменённые файлы Mini App/API и 19 подписанных фото-ассетов. Он не содержит `bot_telegram.py`, `.env` или токенов, чтобы не перезаписать рабочий бот с уже добавленным SOCKS5-прокси/демо-авторизацией.

## Как применить
1. Сделайте резервную копию текущего GitHub-репозитория.
2. Распакуйте архив в корень репозитория `alfadent-miniapp`, сохраняя структуру каталогов (`web/`, `webapp_api.py`, `requirements.txt`).
3. Не заменяйте текущий `bot_telegram.py` и не меняйте `.env` / Render Environment Variables.
4. Опубликуйте изменения и дождитесь деплоя Render.
5. Проверьте `GET /health`, затем откройте Mini App из Telegram.

## Что внутри
- `web/miniapp.html` — обновлённый UI.
- `web/assets/doctors/doctor-01-...jpg` … `doctor-19-...jpg` — фото, названные по ФИО из файлов клиента.
- `webapp_api.py` — существующие заявки в Bitrix24; для экстренных обращений телефон обязателен, время обращения записывается.
- `requirements.txt` — зависимости API.
- `IMPLEMENTATION_TRACKER.md`, `DOCTOR_PHOTO_MAPPING.csv`, `doctor-photo-contact-sheet.jpg`, `LIMITATIONS_AND_CLIENT_INPUTS.md`, `SOURCES_AND_DATA_REVIEW.md`, `UPDATE_AND_TEST.md` — трекер, таблица фото и требования к приёмке.

## Ограничения
- МИС «Инфоклиника» не интегрирована: реальные свободные слоты, визиты, перенос и отмена требуют API/доступов МИС.
- 19 фото сопоставлены с ФИО по названиям файлов клиента. Один ранее использованный портрет сохранён как `doctor-20-unassigned.jpg`, но не отображается в каталоге, пока клиент не подтвердит ФИО. Для профилей без подтверждённых сведений о специализации/стаже/ценах эти поля не придумывались; заполнить их нужно по утверждённым данным клиники. Проверьте отмеченное в CSV расхождение в написании отчества Мамеян Джульетты.
- `node --check` JS and `py_compile` for API/bot passed locally; real deployment/CRM/Telegram requests must be verified after deploy.
