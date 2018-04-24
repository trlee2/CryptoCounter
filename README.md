CS 506 Project

<p>Python version 3.6.x</p>
<p>Django version 2.0.x</p>

Installation:
1. Use link below to configure Python and Django on your machine.  Your choice to use the Python in the main environment or setup a virtual environment (VE recommended).
<https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/development_environment>
2. Clone the GitHub repo from <https://github.com/trlee2/CryptoCounter>
3. Install PostgreSQL on your machine
<https://www.postgresql.org/download/>
4. Setup local instance of database and create user. We used ccadmin as the database owner and we set the password for ccadmin to '1', this needs to be done within PostgreSQL. This reflects the setup in the settings.py file. If this isn't set up properly the django app will not be able to run at all.
```shell
$ createdb cryptoDB
$ psql cryptoDB
```
```shell
cryptoDB=# CREATE USER ccadmin;
cryptoDB=# GRANT ALL ON DATABASE "cryptoDB" TO ccadmin;
cryptoDB=# \q
```
5. Navigate to the CryptoSite directory and install PostgreSQL Python adapater
```shell
$ pip install psycopg2
```
5a. Install other libraries for the background tasks to run
```shell
$ pip install requests
$ pip install apscheduler
$ pip install TwitterAPI
$ pip install pytrends
$ pip install praw
```
6. Build the tables
```shell
$ python manage.py migrate
```
7. Start built-in Python Server and run cron
```shell
$ python manage.py runserver
$ python cron.py
```
8. Cron can also take arguments when ran
```shell
$ python cron.py -h
----------------------------------------------------------------------------
long argument   short argument  definition
----------------------------------------------------------------------------
--help             -h             Show this help message and exit
--cron             -c             Enable cron mode
--reset            -r             Truncate all tables that cron interacts with
--test             -t             Start xUnit tests
--history [days]   -p             Sets the number of days to go back in history
                                    Default: 184 days (6 months)
-----------------------------------------------------------------------------
```
