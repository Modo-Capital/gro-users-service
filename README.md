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

* Deploy on AWS EC2

```
# CD into Location of gro-apis.pem key
$ cd .ssh

# SSH into EC2 Instance
$ ssh -i "gro-apis.pem" ec2-user@ec2-18-233-153-200.compute-1.amazonaws.com

# Stop Current Dockers
$ docker-compose down

# Pull New Image
$ docker pull registry.gitlab.com/troydo42/gro-api

# Restart Dockers
$ docker-compose up -d --build
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


### Who do I talk to? ###
* Troy Do - troy@topflightapps.com
