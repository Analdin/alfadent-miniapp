# AlfaDent — приватная конфигурация Python

Этот репозиторий содержит старую копию Mini App/бота, которую больше нельзя запускать в production.

**Единственное назначение репозитория в текущей схеме:** хранение закрытого файла `alfadent_config.py` с действующими настройками Telegram, MAX, Bitrix24, прокси, внутренним секретом API и путями к данным.

Рабочие исходники находятся в:
- [Mini App + FastAPI + Telegram](https://github.com/Analdin/mini-app_main)
- [MAX bot](https://github.com/Analdin/alfa-dent_max)

## Правила

- Репозиторий должен оставаться **private**.
- Не переводите его в public.
- Не копируйте `alfadent_config.py` в публичные репозитории, Pull Request, issues, логи и тесты.
- На VPS конфигурация устанавливается в `/etc/alfadent/alfadent_config.py` с правами `root:alfadent 0640` и подключается к рабочим проектам символическими ссылками.
- `.env` и `EnvironmentFile` не используются.
- Не запускайте старые `bot_telegram.py` или `webapp_api.py` из этого репозитория.

Более ранние коммиты этого приватного репозитория содержат старые credentials. Не раскрывайте историю репозитория наружу.
