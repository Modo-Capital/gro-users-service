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
    - /banking/transactions/
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

```
# Setting up virtual enviroment
$ virtualenv -p python3.6 env

# Activate the Virtual Enviroment
$ . env/bin/activate

# Install Dependencies
(env)$ pip install -r requirements.txt

# Setting APP_SETTINGS to DevelopmentConfig, Database and SecretKey
(env)$ export APP_SETTINGS=project.config.DevelopmentConfig DATABASE_URL=postgres://gro_admin:gradeALoan@users-db.cqpif3mugtce.us-east-1.rds.amazonaws.com:5432/users SECRET_KEY=gradeALoan PLAID_CLIENT_ID=5a9591e08d9239244b8063ad PLAID_SECRET=eee49e6a0701f60eea4319bbf96282 PLAID_ENV=development PLAID_PUBLIC_KEY=02e15ef6f47e6ecb5377f4e3f26d82

# Spin up a Local Server and check in browser at http://127.0.0.1:5000/ 
$ python manage.py runserver

```

** Setting up on new EC2 Instance

```
# SSH into new instance
$ ssh -i "gro-apis.pem" ec2-user@ec2-54-165-169-138.compute-1.amazonaws.com

# Install GIT
$ sudo yum install git

# Clone the sourcecode into the ec2 instance
$ git clone https://github.com/joectuan/gro-users-service

# Install python3 and other python packages
$ sudo yum install python3
$ sudo python3 -m pip install -r requirements.txt

# Test Run Gunicorn on Port 5000
$ gunicorn --bind 0.0.0.0:5000 wsgi:app

# Copy the groCapita.conf file to etc/init
$ sudo cp groCapital.conf /etc/init/groCapital.conf

# reload configuration files from /etc/init/*.conf
$ sudo initctl reload-configuration

# see if the new job is listed
$ sudo initctl list

# start the groCapital.conf script
$ sudo initctl start groCapital

```

** Deploy on NOW

```
$ now
$ now -e APP_SETTINGS=project.config.DevelopmentConfig -e DATABASE_URL=postgres://gro_admin:gradeALoan@users-db.cqpif3mugtce.us-east-1.rds.amazonaws.com:5432/users -e SECRET_KEY=gradeALoan -e PLAID_CLIENT_ID=5a9591e08d9239244b8063ad  -e PLAID_SECRET=eee49e6a0701f60eea4319bbf96282 -e PLAID_ENV=development -e PLAID_PUBLIC_KEY=02e15ef6f47e6ecb5377f4e3f26d82
```


* How to run tests
** Run test locally
# Setting localDB variable

```
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