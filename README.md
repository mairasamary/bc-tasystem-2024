# TA Buzz

TA Buzz is a TA-Professor matching made for Boston College to streamline to process of matching student TAs with Professors.

## TA System Install on MacOS

Clone your TA System project.

Go to its git folder and create a virtual environment:

```bash
pip3 install virtualenv
python3 -m virtualenv venv
```

Activate your virtual environment:

```bash
source venv/bin/activate
```

Now you can install the required libraries for your TA System project:

```bash
pip3 install -r ./requirements.txt
```

To know who you are, just type on a terminal:

```bash
whoami
```

### Install postgres

Let's install PostgreSQL:

```bash
brew install postgresql@15
```

After installing postgres, we should proceed with configuring it. When we install postgres in the MacOS, the user who installed it is the admin user (i.e.: marquemo). But when running psql, we should still use the postgres database:

```bash
psql postgres
```

So now, you are authenticated with your user (i.e: marquemo) but using the database postgres. Now we need to create a new database for the TA System:

```SQL
CREATE DATABASE tasystem_db;
```

Next, we must create the service account (just a fancy name for a user used by another system) for the TA System:

```SQL
CREATE USER tasystem_service_account WITH PASSWORD 'secretpassword';
ALTER ROLE tasystem_service_account SET client_encoding TO 'utf8';
ALTER ROLE tasystem_service_account SET default_transaction_isolation TO 'read committed';
ALTER ROLE tasystem_service_account SET timezone TO 'UTC';
```

The additional ALTER ROLEs above are recommended by Django.

Next, we need to grant the service account the privilege to use that database:

```SQL
GRANT ALL PRIVILEGES ON DATABASE tasystem_db TO tasystem_service_account;
GRANT ALL PRIVILEGES ON SCHEMA public TO tasystem_service_account;
grant usage on schema public to tasystem_service_account;
```

### Deploying the DJango Tables on PostgreSQL

Now, let’s quit postgres and tell our Django project to deploy its tables in its brand new database. Go to the src folder of your Django project and:

```bash
cd ./src 
source ../.env
python manage.py makemigrations users
python manage.py migrate users
python manage.py makemigrations courses
python manage.py migrate courses
python manage.py makemigrations
python manage.py migrate
```

The command above applies the migrations of the users app first and then the migrations of the other Django apps. That is because Django can’t figure out the order of migrations itself. 

### Create DJango Super User

Now, let’s create our Django app’s super user:

```bash
python manage.py createsuperuser

Email: marquemo@bc.edu
First name: Maira
Last name: Marques Samary
Password: 
Password (again): 
The password is too similar to the last name.
Bypass password validation and create user anyway? [y/N]: y
Superuser created successfully.
```

### Starting the DJango App

To start the app, make sure you use the ./start.sh script. It set’s the environment variables that tells Django where postgres is, which database to use and the credentials. 

Start the app:

```bash
./start.sh
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
November 03, 2024 - 21:39:14
Django version 4.2.6, using settings 'bcta.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

## Connecting to your PostgreSQL database using DBEaver

You can connect to this database using DBeaver by creating a new PostgreSQL connection and using the following information to configure it:
* Host: localhost  
* Port: 5432
* Database: tasystem_db
* Username: tasystem_service_account
* Password: <your password>

## License

None
