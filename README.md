Запуск:
    - git clone https://github.com/LegendGaming0305/avito-backend-task.git
    - docker-compose build
    - docker-compose up (может выдать ошибку в django, тогда остановить и заново запустить docker-compose up)
    

Описание функций и взаимодействия с API:
    - Базовый маршрут http://http://0.0.0.0:8000/api/v1/
    - Запрос пользовательского баннера user_banner/ (в headers указать key=token value='user_token/admin_token') Method GET
![alt text](image.png)
    в параметрах нужно указывать tag_id и feature_id, use_last_revision - по желанию

    - Баннеры для админа хранятся в /banner/ Methods GET, POST
    - Взаимодействие с определенным баннером по id находится в /banner/{id}/ GET, PATCH, DELETE
    в методе GET можно получить активный баннер и три его предыдущие версии
    - Взаимодействие с определенной версией баннера в /banner/{id}/{uuid}/ Methods GET, PATCH
    параметры в PATCH идентичны входящим параметрам в /banner/{id}/ по спецификации API

Проблемы и решения:
    - Первая проблема была связана с оптимизацией получения баннера