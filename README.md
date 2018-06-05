# GROWTH CAPITAL - Users Services 


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
    - /banking/accounts/{uid}
    - /banking/transactions/{uid}
    - /banking/create_public_token

* Accounting Endpoints
    - /accounting/connectToQuickbooks
    - /accounting/authCodeHandler
    - /accounting/companyInfo
    - /accounting/BalanceSheet
    - /accounting/CashFlow
    - /accounting/ProfitAndLost

* Social Media Endpoints
    - /social_media/facebook_handler
    - /social_media/linkedin_handler
    - /social_media/google_handler

### How do I get set up? ###

* How to run and deploy with Docker
** Run Application on Local Host

```bash
# Setting up virtual enviroment
$ virtualenv -p python3.6 env

# Activate the Virtual Enviroment
$ . env/bin/activate

# Install Dependencies
(env)$ pip install -r requirements.txt

# Setting APP_SETTINGS to DevelopmentConfig, Database and SecretKey
```
(env)$ export APP_SETTINGS=project.config.DevelopmentConfig DATABASE_URL=postgres://gro_admin:gradeALoan@users-db.cqpif3mugtce.us-east-1.rds.amazonaws.com:5432/users SECRET_KEY=gradeALoan PLAID_CLIENT_ID=5a9591e08d9239244b8063ad PLAID_SECRET=eee49e6a0701f60eea4319bbf96282 PLAID_ENV=development PLAID_PUBLIC_KEY=02e15ef6f47e6ecb5377f4e3f26d82

# Spin up a Local Server and check in browser at http://127.0.0.1:5000/ 
$ python manage.py runserver

```
** Docker Build and Run Locally
```
$ docker build -t troydo42/gro-users .
$ docker run -e APP_SETTINGS=project.config.DevelopmentConfig -e DATABASE_URL=postgres://gro_admin:gradeALoan@users-db.cqpif3mugtce.us-east-1.rds.amazonaws.com:5432/users -e SECRET_KEY=gradeALoan -e PLAID_CLIENT_ID=5a9591e08d9239244b8063ad -e PLAID_SECRET=eee49e6a0701f60eea4319bbf96282 -e PLAID_ENV=sandbox -e PLAID_PUBLIC_KEY=02e15ef6f47e6ecb5377f4e3f26d82 -e REDIRECT_URI=https://apis.gro.capital/accounting/authCodeHandler -d -p 8888:5000 troydo42/gro-users

```
** Docker Deploy on AWS

```
$ docker build -t troydo42/gro-users .
$ docker push troydo42/gro-users
$ eb setenv APP_SETTINGS=project.config.DevelopmentConfig DATABASE_URL=postgres://gro_admin:gradeALoan@users-db.cqpif3mugtce.us-east-1.rds.amazonaws.com:5432/users SECRET_KEY=gradeALoan PLAID_CLIENT_ID=5a9591e08d9239244b8063ad PLAID_SECRET=eee49e6a0701f60eea4319bbf96282 PLAID_ENV=development PLAID_PUBLIC_KEY=02e15ef6f47e6ecb5377f4e3f26d82
REDIRECT_URI=https://apis.gro.capital/accounting/authCodeHandler
```

** Deploy on NOW

```
$ now
$ now -e APP_SETTINGS=project.config.DevelopmentConfig -e DATABASE_URL=postgres://gro_admin:gradeALoan@users-db.cqpif3mugtce.us-east-1.rds.amazonaws.com:5432/users -e SECRET_KEY=gradeALoan -e PLAID_CLIENT_ID=5a9591e08d9239244b8063ad -e PLAID_SECRET=eee49e6a0701f60eea4319bbf96282 -e PLAID_ENV=sandbox -e PLAID_PUBLIC_KEY=02e15ef6f47e6ecb5377f4e3f26d82 -e REDIRECT_URI=https://apis.gro.capital/accounting/authCodeHandler
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


### Who do I talk to? ###
* Troy Do - troy@topflightapps.com