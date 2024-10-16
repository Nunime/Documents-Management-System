# Documents Management System

## Общее описание задачи
Разработка системы управления документами, их расположением и правами доступа к документам и папкам с документами.

1. Сущность Документ представляет собой файл (может быть люого типа), его наименование и описание/комментарий (необязательно), дата/время создания и создателя, дата/время последнего изменения и пользователя, осуществившего изменения
2. Сущность Папка содержит имя, комментарий (необязательно), дата/время создания и создателя, дата/время последнего изменения и пользователя, осуществившего изменения
3. Каждая папка может содержать в себе другие папки
4. В каждой папке может быть несколько документов
5. Права доступа настраиваются на каждую папку индивидуально, но применяются ко всем дочерним элементам (папкам и документам)
6. Спискок возможных прав доступа:
    - Чтение
    - Запись


## Задание на разработку
1. Разработка Backend части приложения согласно представленному описанию
2. Разработка Frontend приложения для отображения структуры папок и докуметов в них, создания / изменения / удаления папок, функций настройки прав доступа по папкам, загрузки докуметов
3. Документирование разрабтанного решения в GitLab

## Дополнительные задачи (будет плюсом)
1. Контейнеразция (написать Dockerfile и docker-compose)
2. Добавить возможность скачивания файлов
3. Добавить функции копирования и перемещения каталогов и файлов


## Стек для выполнения задачи
1. Backend: ``FastAPI`` + ``SQLAlchemy``
2. Frontend: ``React``
3. Database: ``PostgreSQL``

> Примечание
>
> Для хранения файлов докуметов достаточно использовать файловую систему





