# GROWTH CAPITAL - Users Services #

### What is this repository for? ###
* Auths Endpoints for Sign In, Sign Up, Sign Out and Status
    - /auth/signup
    - /auth/signin
    - /auth/signout
    - /auth/status

* Users Endpoints for Early Access
    - /users/
    - /users/{id}

* Companies Endpoints
    - /companies/
    - /companies/{id}
    
* Banking Endpoints
    - /banking/get_access_token
    - /banking/accounts
    - /banking/transactions
    - /banking/create_public_token

* Accounting Endpoints


* Social Media Endpoints


### How do I get set up? ###

* Summary of set up
** Run project locally

```bash
# Setting up virtual enviroment
$ virtualenv -p python3.6 env

# Activate the Virtual Enviroment
$ . env/bin/activate

# Install Dependencies
(env)$ pip install -r requirements.txt

# Setting APP_SETTINGS to DevelopmentConfig
(env)$ export APP_SETTINGS=project.config.DevelopmentConfig

# Setting DATABASE_URL to local postgres user_dev
(env)$ export DATABASE_URL=postgres://postgres:postgres@localhost:5432/users_dev

# Setting SERCRET_KEY 
(env)$ export SECRET_KEY=my_precious

# Initalize Postgres DB
(env)$ python manage.py db init

# Make migration
(env)$ python manage.py db migrate

# Upgrade DB
(env)$ python manage.py db upgrade

# Spin up a Local Server and check in browser at http://127.0.0.1:5000/ 
$ python manage.py runserver

```

* How to run tests

** Run test locally
```bash
# Setting localDB variable

# Activate local enviroment
$ . env/bin/activate

# Setting APP_SETTING  to TestingConfig
(env)$ export APP_SETTINGS=project.config.TestingConfig

# Setting DATABASE_URL to local postgres users_test
(env)$ export DATABASE_TEST_URL=postgres://postgres:postgres@localhost:5432/users_test

# Setting SERCRET_KEY 
(env)$ export SECRET_KEY=my_precious

# Run Test
$ python manage.py test
```


* How to run and deploy with Docker

** Docker Build and Run Locally
```
$ docker build -t troydo42/gro-users .
$ docker run -e APP_SETTINGS=project.config.ProductionConfig -e DATABASE_URL=postgres://gro_admin:gradeALoan@users-db.cqpif3mugtce.us-east-1.rds.amazonaws.com:5432/users -e SECRET_KEY=gradeALoan -d -p 8888:5000 troydo42/gro-users

```

** Docker Deploy on AWS

```
$ docker build -t troydo42/gro-users .
$ eb setenv APP_SETTINGS=project.config.ProductionConfig DATABASE_URL=postgres://gro_admin:gradeALoan@users-db.cqpif3mugtce.us-east-1.rds.amazonaws.com:5432/users SECRET_KEY=gradeALoan

```


### Who do I talk to? ###
* Troy Do - troy@topflightapps.com
