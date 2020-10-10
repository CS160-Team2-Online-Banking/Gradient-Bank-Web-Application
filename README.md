# Online-Banking-App

## `How to set up`

1. Set up Virtual Environment

`python3 -m venv venv`

`cd venv`

【Windows＆command prompt】activate virtual env

`Scripts/activate.bat`

【Windows＆GitBash】activate virtual env

`source Scripts/activate`

※ if you got an error,

`source bin/activate`

【Macの場合】activate virtual env

`source Scripts/activate`

※ if you got an error,

`source bin/activate`

2. Install libraries

`pip3 install -r requirements.txt`

`cd ..`

3. Database migration

`python manage.py makemigrations`

`python manage.py migrate`

4. Register the user who manages the system

`python manage.py createsuperuser`

input username, email, password



5. Start to run the system

`python manage.py runserver`

