CS 506 Project

<p>Python version 3.6.x</p>
<p>Django version 2.0.x</p>

Installation:
1. Use link below to configure Python and Django on your machine.  Your choice to use the Python in the main environment or setup a virtual environment (VE recommended). All the commands with python and pip below have them set to default to python3 and pip3 if these are not the defaults on your machine you will need to use pip3 instead of pip or python3 instead of python in the terminal commands listed below.
<https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/development_environment>
2. Clone the GitHub repo from <https://github.com/trlee2/CryptoCounter>
3. Install PostgreSQL on your machine
<https://www.postgresql.org/download/>
4. Setup local instance of database and create user. We used ccadmin as the database owner and we set the password for ccadmin to '1', this needs to be done within PostgreSQL. This reflects the setup in the settings.py file. If this isn't set up properly the django app will not be able to run at all. (It is very important to have the user set up and have all permissions granted to that user in the database. Also having the user password in postgresql match the password in the settings.py file is necessary to get the django app to run). When you create a database in PostgreSQL it is not located in the current directory, and will need to be modified within the postgre terminal to get it configured properly. Setting up the database gave us a lot of issues early on so make sure the directions are followed carefully.
```shell
$ createdb cryptoDB
$ psql cryptoDB
```
```shell
cryptoDB=# CREATE USER ccadmin WITH PASSWORD '1';
cryptoDB=# GRANT ALL ON DATABASE "cryptoDB" TO ccadmin;
cryptoDB=# \q
```
5. Install PostgreSQL Python adapter
```shell
$ pip install psycopg2
```
5a. Install other libraries for the background tasks to run (in main directory)
```shell
$ pip install requests
$ pip install apscheduler
$ pip install TwitterAPI
$ pip install pytrends
$ pip install praw
```
6. Build the tables using the command:
```shell
$ python manage.py migrate
```
7. Start built-in Python Server and run cron (run cron with -p and a low number otherwise it will take a long time to scrap all the data this will result in fewer data points in the graphs but you won't have to have cron running for 24+ hours first before you can run the server)
```shell
$ python manage.py runserver
$ python cron.py
```
8. Cron can also take arguments when ran
```shell
$ python cron.py -h
$ python cron.py -d (use this for debugging)
----------------------------------------------------------------------------
long argument   short argument  definition
----------------------------------------------------------------------------
--help             -h             Show this help message and exit
--cron             -c             Enable cron mode
--reset            -r             Truncate all tables that cron interacts with
--test             -t             Start xUnit tests
--history [days]   -p             Sets the number of days to go back in history
                                    Default: 184 days (6 months)
--debug            -d             Debug mode of testing as we code                                    
-----------------------------------------------------------------------------
```
