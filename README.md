# GROWTH CAPITAL - Users Services #

### What is this repository for? ###
* Users Endpoints for Early Access
    - /users/
    - /users/{id}

* Auths Endpoints for Sign In, Sign Up, Sign Out and Status
    - /auth/signup
    - /auth/signin
    - /auth/signout
    - /auth/status

* Companies Endpoints
    - /companies/
    - /companies/{id}
    
* Banking Endpoints
    - /banking/get_access_token
    - /banking/accounts
    - /banking/transactions
    - /banking/create_public_token

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

### Application Structure ###
```bash
├── env
├── migrations
├── project
│   ├── __init__.py
│   ├── config.py
│   ├── api
│   │   ├── __init__.py
│   ├── auth
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── parameters.py
│   │   ├── views.py
│   ├── users
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── parameters.py
│   │   ├── permissions.py
│   │   ├── resources.py
│   │   ├── schemas.py
│   ├── companies
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── parameters.py
│   │   ├── resources.py
│   │   ├── schemas.py
│   ├── banking
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── parameters.py
│   │   ├── resources.py
│   │   ├── schemas.py
│   ├── accounting
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── parameters.py
│   │   ├── resources.py
│   │   ├── schemas.py
│   ├── social_media
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── parameters.py
│   │   ├── resources.py
│   │   ├── schemas.py
│   ├── db
│   ├── templates
│   ├── tests
├── travis.yml
├── Dockerfile-local
├── manage.py
├── travis.yml
├── requirements.txt
└── .gitignore
```


### Who do I talk to? ###
* Troy Do - troy@topflightapps.com
