# DB_Project
## Before you start ##
- After setup the project, make sure you python is higher than 3.6 to have 'operator' package if not please install python 3.6 and change to python 3 as default by:
```
    alias python=python3
```
## Code structure ##
```
DB_Project

├── DB_Project
    ├── __init__.py
    ├── __pycache__
    │   ├── __init__.cpython-36.pyc
    │   ├── settings.cpython-36.pyc
    │   ├── urls.cpython-36.pyc
    │   └── wsgi.cpython-36.pyc
    ├── settings.py
    ├── urls.py
    └── wsgi.py
├── bookstore
├── db.sqlite3
├── manage.py
├── pics
├── sql_script
    ├── Django_Bookstore_Arrival_history.sql
    ├── Django_Bookstore_Comment.sql
    ├── Django_Bookstore_Order.sql
    ├── Django_Bookstore_User.sql
    └── Django_Bookstore_book.sql
├── static
├── staticfiles
└── templates
```

## Before you run the project, please create related database ##
- a. Our database is simply the mysql. Before you start the server it is required for you to have a schema and better with a related dataset. To do this: run all scripts under ```sql_script``` folder in your mysql server.
- All five mysql scripts under ```sql_script``` folder:
```
    Django_Bookstore_Arrival_history.sql
    Django_Bookstore_Comment.sql
    Django_Bookstore_Order.sql
    Django_Bookstore_User.sql
    Django_Bookstore_book.sql
```
- b. You may need to install ```mysqlclient``` package to use ```MySQLDB``` module to fetch data from db. If not installed, please:
```
    pip3 install mysqlclient
```

## How to run the code ##
- a. Direct to ```.../DB_Project/bookstore/models.py``` and configure your database info over ```DB_Connection``` class:
```
from django.db import 
...
...
class DB_Connection(models.Model):
    host = "localhost"
    user = "root"
    pwd = "your_password_here"
    db = "Django_Bookstore"
    charset = "utf8"
...
```
- b. Direct to ```.../DB_Project/``` and execute:

```
    python manage.py runserver
```
- c. Go to below url and start browsing!

```
    http://127.0.0.1/8000/
```
## Related ERD ##
<p align="center">
<img src="https://github.com/Joe627487136/DB_Project/blob/master/pics/ERD.png" width="800" align="center">
</p>
