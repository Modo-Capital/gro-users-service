# project/api/models.py
import datetime
import jwt

import enum
# from enum import Enum
from project import db, bcrypt
from flask import current_app
from flask_security import UserMixin, RoleMixin
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as sa_text
import uuid

# Create Client Application Model for API Keys in Database
# class ClientApp(db.Model):
#     # name of the client application detail
#     name = db.Column(db.String(40))
#     description = db.Column(db.String(400))
#     user_uid = db.Column(db.ForeignKey('users.uid'))
#     user = db.relationship('User')
#     client_id = db.Column(db.String(40), primary_key=True)
#     client_secret = db.Column(db.String)

# Create Token Model in Database
class Token(db.Model):
    __tablename__ = "access token"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vendor = db.Column(db.String(256), nullable=False)
    tokenType = db.Column(db.String(256), nullable=False)
    refreshExpiry = db.Column(db.DateTime, nullable=False)
    accessTokenExpiry = db.Column(db.DateTime, nullable=False)
    accessToken = db.Column(db.String(256), nullable=False)
    refreshToken = db.Column(db.String(256), nullable=False)
    idToken = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, vendor, tokenType, refreshExpiry, accessTokenExpiry, accessToken, refreshToken, idToken, created_at=datetime.datetime.utcnow()):
        self.vendor = vendor
        self.tokenType = tokenType
        self.refreshExpiry = refreshExpiry
        self.accessTokenExpiry = accessTokenExpiry
        self.accessToken = accessToken
        self.refreshToken = refreshToken
        self.idToken = idToken
        self.created_at = created_at

# Define Company Structure Type
class StructureType(enum.Enum):
    S = "Sole Proprietorship"
    GP = "General Partnership"
    C = "C-Corporation"
    LLC = "Limited Liability Corporation"
    SLLC = "S-Corporation"

# Define Company Industry Type
# class IndustryType(enum.Enum):
#     Agri = "Agriculture, Forestry, Fishing & Hunting"
#     Manu = "Manufacturing"

# Create Company Model in Database
class Company(db.Model):
    __tablename__="companies"
    id = db.Column(db.Integer, autoincrement=True)
    uid = db.Column(db.String(), primary_key=True, nullable=False)
    company_name = db.Column(db.String(256), nullable=True)
    address = db.Column(db.String(), nullable=True)
    email_address = db.Column(db.String(), nullable=True)
    company_phone = db.Column(db.Integer, nullable=True)
    password = db.Column(db.String(), nullable=True)
    city = db.Column(db.String(), nullable=True)
    state = db.Column(db.String(), nullable=True)
    zipcode = db.Column(db.Integer, nullable=True)
    structure = db.Column(db.String(), nullable=True)
    industry = db.Column(db.String(), nullable=True)
    established_date = db.Column(db.Date, nullable=True)
    annual_revenue = db.Column(db.Integer, nullable=True)
    loan_amount_applied = db.Column(db.Integer, nullable=True)
    loan_type = db.Column(db.String(), nullable=True)
    loan_reason = db.Column(db.String(), nullable=True)
    ein = db.Column(db.Integer, nullable=True)
    duns = db.Column(db.Integer, nullable=True)
    bank_account = db.Column(db.String, nullable=True)
    accounting_account = db.Column(db.String, nullable=True)
    loan_approved = db.Column(db.Integer, nullable=True)
    ml_inputs = db.relationship("Input", backref="company_inputs", cascade="all, delete-orphan", lazy='dynamic')
    gro_scores = db.relationship("Gro_Score", backref="company_score", cascade="all, delete-orphan", lazy='dynamic')
    active = db.Column(db.Boolean(), default=True, nullable=False)
    admin = db.Column(db.Boolean(),default=False, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)


    def __init__(self, company_name, address, city, state, zipcode):
        self.company_name = company_name
        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.uid = str(uuid.uuid4())
        self.created_at = datetime.datetime.utcnow()

# Create ML Input
class Input(db.Model):
    __tablename__ = "inputs"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_uid =  db.Column(db.String, db.ForeignKey('companies.uid'))
    company =  db.relationship('Company')
    created_at = db.Column(db.DateTime, nullable=False)
    annual_inc = db.Column(db.Integer, nullable=True)
    collections_12_mths_zero = db.Column(db.Integer, nullable=True)
    dti = db.Column(db.Float, nullable=True)
    deling_2yrs = db.Column(db.Integer, nullable=True, default=0)
    delinq_2yrs_zero = db.Column(db.Boolean, nullable=True)
    emp_length_num = db.Column(db.Integer, nullable=True, default=0)
    home_ownership = db.Column(db.String, nullable=True)
    inq_last_6mths = db.Column(db.Integer, nullable=True)
    last_deling_none = db.Column(db.Boolean, nullable=True)
    last_major_derog_none = db.Column(db.Boolean, nullable=True)
    mths_since_last_delinq = db.Column(db.Integer, nullable=True)
    mths_since_last_record = db.Column(db.Integer, nullable=True)
    mths_since_last_major_derog = db.Column(db.Integer, nullable=True)
    open_acc = db.Column(db.Integer, nullable=True, default=0)
    payment_inc_ratio = db.Column(db.Float, nullable=True, default=0)
    pub_rec = db.Column(db.Integer, nullable=True)
    pub_rec_zero = db.Column(db.Boolean, nullable=True)
    revolBal = db.Column(db.Float, nullable=True, default=0)
    revolUtil = db.Column(db.Float, nullable=True, default=0)
    total_acc = db.Column(db.Integer, nullable=True)

    def __init__(self, company, created_at=datetime.datetime.utcnow()):
        self.company = company
        self.created_at = created_at

# Create Gro Score Model in Database
class Gro_Score(db.Model):
    __tablename__ = "gro score"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    data_score = db.Column(db.Integer, default=0)
    ml_score = db.Column(db.Integer, default=0)
    gro_score = db.Column(db.Integer, default=0)
    company_uid =  db.Column(db.String, db.ForeignKey('companies.uid'))
    company =  db.relationship('Company')
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, company, data_score, company_uid,created_at=datetime.datetime.utcnow()):
        self.company = company
        self.company_uid = company_uid
        self.data_score = data_score
        self.created_at = created_at

roles_users = db.Table('roles_users',
    db.Column('admin_user_id', db.Integer(), db.ForeignKey('admin_users.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    __tablename__ = "role"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

        
class AdminUser(db.Model, UserMixin):
    __tablename__ = "admin_users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('admin_roles', lazy='dynamic'))

    def __str__(self):
        return self.email

# Create User Model in Database
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(300), nullable=False)
    admin = db.Column(db.Boolean(),default=False, nullable=False) 
    status = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(128), nullable=True, unique=True)
    profile = db.Column(db.String(), nullable=True, default='https://avatars.io/static/default_128.jpg')
    first_name = db.Column(db.String(128), nullable=False, default="First Name")
    last_name = db.Column(db.String(128), nullable=False, default="Last Name")
    birthday = db.Column(db.Date, nullable=True, default="11-11-1111")
    driverLicense = db.Column(db.String(10), nullable=False, default="42424242AA")
    ssn = db.Column(db.Integer, nullable=False,default=42424242)
    company = db.Column(db.String, db.ForeignKey(Company.uid), nullable=True)
    facebook_uid = db.Column(db.String, nullable=True)
    facebook_access_token = db.Column(db.String(), nullable=True)
    linkedin_access_token = db.Column(db.String(), nullable=True)
    google_uid = db.Column(db.String, nullable=True)
    google_access_token = db.Column(db.String(), nullable=True)
    plaid_access_token = db.Column(db.String(), nullable=True)
    quickbook_access_token = db.Column(db.String(), nullable=True)
    quickbook_id = db.Column(db.String(), nullable=True)
    bank_accounts = db.relationship("Bank_Account", backref="business_bank", cascade="all, delete-orphan", lazy='dynamic')
    cash_flow_reports = db.relationship("Cash_Flow", backref="business_cash_flow", cascade="all, delete-orphan", lazy='dynamic')
    profit_loss_reports = db.relationship("Profit_Loss", backref="business_profit_loss", cascade="all, delete-orphan", lazy='dynamic')
    balance_sheet_reports = db.relationship("Balance_Sheet", backref="business_balance_sheet", cascade="all, delete-orphan", lazy='dynamic')
    documents = db.relationship("Document", backref="business_documents", cascade="all, delete-orphan", lazy='dynamic')
    created_at = db.Column(db.DateTime, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)
    
    def __init__(self, email, password, status, admin, first_name, last_name, birthday):
        self.email = email
        self.password = bcrypt.generate_password_hash(password, current_app.config.get('BCRYPT_LOG_ROUNDS')).decode('utf-8') 
        self.status = status
        self.admin = admin
        self.uid = str(uuid.uuid4())
        self.created_at = datetime.datetime.utcnow()
        self.first_name = first_name
        self.last_name = last_name
        self.birthday = birthday

    # Generate Auth Token
    def encode_auth_token(self, user_id):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(
                    days=current_app.config.get('TOKEN_EXPIRATION_DAYS'), 
                    seconds=current_app.config.get('TOKEN_EXPIRATION_SECONDS')
                ),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            } 

            return jwt.encode(
                payload, 
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e
    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_uid(self):
        return self.uid

    # Required for administrative interface
    def __str__(self):
        return self.email

    """Decodes the auth token - :param auth_token: - :return: integer|string"""
    @staticmethod
    def decode_auth_token(auth_token):      
        try:
            payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please login again.'
    def __repr__(self):
        return '<User %r>' % self.uid


# Create Documents
class Document(db.Model):
    __tablename__="documents"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    link = db.Column(db.String, nullable=False)
    user_id =  db.Column(db.Integer, db.ForeignKey('users.id'))
    user =  db.relationship('User')

    def __init__(self, name, link, user):
        self.user = user
        self.name = name
        self.link = link

    def __repr__(self):
        return '<Document %r>' % self.id

# Create Banking Accounts
class Bank_Account(db.Model):
    __tablename__ = "bank_accounts"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User')
    name = db.Column(db.String, nullable=False)
    account_type = db.Column(db.String, nullable=False)
    account_number = db.Column(db.Numeric, nullable=False)
    routing_number = db.Column(db.Numeric, nullable=False)
    balance = db.Column(db.Float, nullable=False)
    transactions = db.relationship("Transaction", backref="bank_transaction", cascade="all, delete-orphan", lazy='dynamic')

    def __init__(self, user, name, account_type, account_number, routing_number, balance):
        self.user = user
        self.name = name
        self.account_type = account_type
        self.account_number = account_number
        self.routing_number = routing_number
        self.balance = balance

class Balance_Sheet(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User')
    report_name = db.Column(db.String, nullable=False)
    startPeriod = db.Column(db.Date, nullable=True, default="11-11-1111")
    endPeriod = db.Column(db.Date, nullable=True, default="11-11-1111")
    current_asset = db.Column(db.Float, nullable=True)
    fixed_asset = db.Column(db.Float, nullable=True)
    current_liability = db.Column(db.Float, nullable=True)
    longterm_liability = db.Column(db.Float, nullable=True)
    equity = db.Column(db.Float,nullable=True)

    def __init__(self, user, report_name, startPeriod, endPeriod, current_asset, fixed_asset, current_liability, longterm_liability, equity):
        self.user = user
        self.report_name = report_name
        self.startPeriod = startPeriod
        self.endPeriod = endPeriod
        self.current_asset = current_asset
        self.fixed_asset = fixed_asset
        self.current_liability = current_liability
        self.longterm_liability = longterm_liability
        self.equity = equity

class Cash_Flow(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User')
    report_name = db.Column(db.String, nullable=False)
    startPeriod = db.Column(db.Date, nullable=True, default="11-11-1111")
    endPeriod = db.Column(db.Date, nullable=True, default="11-11-1111")
    beginningCash = db.Column(db.Float, nullable=True)
    endingCash = db.Column(db.Float, nullable=True)
    operatingNetCash = db.Column(db.Float, nullable=True)
    investingNetCash = db.Column(db.Float, nullable=True)
    financingNetCash = db.Column(db.Float, nullable=True)

    def __init__(self, user, report_name, startPeriod, endPeriod, beginningCash, endingCash, operatingNetCash, investingNetCash, financingNetCash):
        self.user = user
        self.report_name = report_name
        self.startPeriod = startPeriod
        self.endPeriod = endPeriod
        self.beginningCash = beginningCash
        self.endingCash = endingCash
        self.operatingNetCash = operatingNetCash
        self.investingNetCash = investingNetCash
        self.financingNetCash = financingNetCash


class Profit_Loss(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User')
    report_name = db.Column(db.String, nullable=False)
    startPeriod = db.Column(db.Date, nullable=True, default="11-11-1111")
    endPeriod = db.Column(db.Date, nullable=True, default="11-11-1111")
    income = db.Column(db.Float, nullable=True)
    COGS = db.Column(db.Float, nullable=True)
    grossProfit = db.Column(db.Float, nullable=True)
    expenses = db.Column(db.Float, nullable=True)
    netOperatingIncome = db.Column(db.Float, nullable=True)
    otherExpenses = db.Column(db.Float, nullable=True)
    netOtherIncome = db.Column(db.Float, nullable=True)
    netIncome = db.Column(db.Float, nullable=True)

    def __init__(self, user, report_name, startPeriod, endPeriod, income, COGS, grossProfit, expenses, netOperatingIncome, otherExpenses, netOtherIncome, netIncome):
        self.user = user
        self.report_name = report_name
        self.startPeriod = startPeriod
        self.endPeriod = endPeriod
        self.income = income
        self.COGS = COGS
        self.grossProfit = grossProfit
        self.expenses = expenses
        self.netOperatingIncome = netOperatingIncome
        self.otherExpenses = otherExpenses
        self.netOtherIncome = netOtherIncome
        self.netIncome = netIncome

# Create Banking Transaction
class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    amount = db.Column(db.Float, nullable=True)
    date = db.Column(db.Date, nullable=True, default="11-11-1111")
    bank_account_id =  db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=False)
    bank_account =  db.relationship('Bank_Account')

    def __init__(self,bank_account, name, amount, date):
        self.name = name
        self.bank_account = bank_account
        self.amount = amount
        self.date = date

# Create Daily Transactions
class DailyTransaction(db.Model):
    __tablename__ = "daily_transactions"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount = db.Column(db.Float, nullable=True)
    date = db.Column(db.Date, nullable=True, default="11-11-1111")
    bank_account_id =  db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=False)
    bank_account =  db.relationship('Bank_Account')

    def __init__(self,bank_account, amount, date):
        self.bank_account = bank_account
        self.amount = amount
        self.date = date 
        






