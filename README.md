Python Telegram bot - PT.START

Телеграм-бот:
мониторит удаленную машину Linux
сохраняет/извлекает данные Postgresql
получает логи реплики бд-мастера

Для запуска необходим .env, где указаны креды DB и RM

### Docker
------------------------------
docker compose up --build -d
------------------------------
### Ansible
------------------------------
Для плейбука необходимо 3 машины Linux:
1. Сервер для бота 
2. Сервер для db-master
3. Сервер для db-slave
