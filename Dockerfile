FROM python:3.6.0

EXPOSE 5000

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add requirements (to leverage Docker cache)
ADD ./requirements.txt /usr/src/app/requirements.txt

# install requirements
RUN pip install -r requirements.txt

# add app
ADD . /usr/src/app

# set enviroments
ENV APP_SETTINGS=project.config.DevelopmentConfig 
ENV DATABASE_URL=postgres://gro_admin:gradeALoan@users-db.cqpif3mugtce.us-east-1.rds.amazonaws.com:5432/users 
ENV SECRET_KEY=gradeALoan 
ENV PLAID_CLIENT_ID=5a9591e08d9239244b8063ad PLAID_SECRET=eee49e6a0701f60eea4319bbf96282 
ENV PLAID_ENV=development 
ENV PLAID_PUBLIC_KEY=02e15ef6f47e6ecb5377f4e3f26d82 
ENV REDIRECT_URI=https://apis.gro.capital/accounting/authCodeHandler

# run server
CMD python manage.py runserver -h 0.0.0.0