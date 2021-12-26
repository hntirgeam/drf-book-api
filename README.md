<h3 align="center">Django DRF API для авторов, которые могут выкладывать книги и комментировать их</h3>

## Функционал
* Регистрация с обязательными кастомными полями (ФИО, день рождения) 
* Добавление, редактирование и удаление книг, комментариев к книгам, библиотек
* Кастомные (и не очень) пермишенны 
* Заполнение БД осмысленными фейковыми данными при помощи `manage.py createusers`


## Setup
```
git clone git@github.com:hntirgeam/drf-book-api.git
cd drf-book-api
python3 -m venv env
source env/bin/activate 
pip install -r requirements.txt
```

## Примените миграции и запустите сервер
```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Тесты
```
pytest book_review_app/tests
pytest book_review_app/tests_live (требуется runserver перед запуском)
```

## manage.py 
### Базу можно заполнить псевдо-реальными значениями (использовалась библиотека Faker):
```
manage.py createusers --users <кол-во юзеров> --books <кол-во книг> --comments <кол-во комментариев>
```
Будет создано X авторов с Y книгами у каждого. Для каждой книги от каждого автора (кроме самого создателя книги) будет создано по Z комментариев. 

Процесс ожидания скрасит ascii графика :) 

## Endpoints
| URL                               | Method                    | Accepts                                                   | Returns                          | 
|:---------------------------------:|:-------------------------:|:---------------------------------------------------------:|:--------------------------------:|
|`api/v1/register`                  | POST                      | `"username", "password", "name", "last_name", "birthday"` |  `HTTP_200_OK`                   |
|`api/v1/api-token-auth/`           | POST                      | `"username", "password"`                                  |  Token                           |
|`api/v1/api-token-deauth/`         | POST                      |  HEAD `{'Authorization': 'Token <token>'}`                |  `HTTP_200_OK`                   |
|`api/authors`                      | GET, PATCH                |  Data + Headers                                           |  Авторов или созданные данные    |
|`api/books`                        | GET, POST                 |  Data + Headers                                           |  Книги или созданные данные      |
|`api/books/<pk>/`                  | GET, PATCH, DELETE        |  Data + Headers                                           |  Книгу, ред. данные, 204         |
|`api/books/<pk>/comments/`         | GET, POST                 |  Data + Headers                                           |  Комментарии или созданные данные|
|`api/books/<pk>/comments/<pk>/`    | GET, PATCH, DELETE        |  Data + Headers                                           |  Комментарий, ред. данные, 204   |
|`api/genres/`                      | GET                       |  Headers                                                  |  Жанры                           |
|`api/libraries/`                   | GET, POST                 |  Data + Headers                                           |  Библиотеки или созданные данные |
|`api/libraries/<pk>/`              | GET, PATCH, DELETE        |  Data + Headers                                           |  Библиотеку, ред. данные, 204    |
