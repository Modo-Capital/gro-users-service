# GROWTH CAPITAL - Users Services 

### What is this repository for? ###
* Deployment triggering endpoint:
    - /deployment (Pass in App name and Password)
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
* Running inside AWS Instance
```
# Running from inside AWS Instance
$ nohup python manage.py runserver -h 0.0.0.0 -p 8000
```

* How to run and deploy with Docker

```
$ docker image build --tag $DOCKERID/gro-api-prod:1.1 .
$ docker container run --detach --publish 8000:8000 --name gro-api-prod $DOCKERID/gro-api-prod:1.1
```

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
$ python manage.py runserver -h 0.0.0.0 -p 8000

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

# Using nodup to running app in the background and restart automatically
$ nohup python manage.py runserver -h 0.0.0.0 -p 8000

```

Now we can access the app from port 5000 of the aws instance. We need to use reverse proxy on CloudFlare to point http and https to this aws instance. 
This is a little hacky and I am working on moving to Gunicorn and Nginx.

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

```
Username: jack@topflightapps.com
Password: Th1$is@Password
``` 

### Who do I talk to? ###
* Troy Do - troy@topflightapps.com
