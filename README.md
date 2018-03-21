CS 506 Project

<p>Python version 3.6.x</p>
<p>Django version 2.0.x</p>

Installation:
1. Use link below to configure Python and Django on your machine.  Your choice to use the Python in the main environment or setup a virtual environment (VE recommended).
<https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/development_environment>
2. Clone the GitHub repo from <https://github.com/trlee2/CryptoCounter>
3. Install PostgreSQL on your machine
<https://www.postgresql.org/download/>
4. Setup local instance of database and create user
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
6. Build the tables
```shell
$ python manage.py migrate
```
7. Start built-in Python Server
```shell
$ python manage.py runserver
```
