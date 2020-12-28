# Gradient Bank
Gradient bank is an online banking application which was developed over the course of 3 months as a class project. Gradient Bank was built using the Django Framework, and uses MySQL and Google Maps to support the features it provides.

## Description
### Customer Features
* External and Internal Transfers
* Check Deposit using Image
* Chase Bank ATM Searched - powered by google maps
### Employee Features
* Manager Dashboard
## Gallery 
<h3>Landing Page</h3>
<img src = "media/Screenshot - Landing.png"/>
<h3>User Dashboard</h3>
<img src = "media/Screenshot - Login Dashboard.png"/>
<h3>Account View</h3>
<img src = "media/Screenshot - Account View.png"/>
<h3>ATM Search Page</h3>
<img src = "media/Screenshot - ATM Lookup.png"/>
<h2>Setup Instructions</h2>

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

4.Collects the static files from all installed apps and copies them to the STATICFILES_STORAGE.
`python manage.py collectstatic`

5. Register the user who manages the system

`python manage.py createsuperuser`

input username, email, password


6. Start to run the system

`python manage.py runserver`

