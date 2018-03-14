#project/api/__init__.py

from flask_restplus import Api
from .accounting import api as accounting
from .banking import api as banking
from .users import api as users
# from auth import auth as auth

### Define API with restplus.api
api = Api (
    version='0.1',
    title='Gro Users API', 
    description="Gro User Restful API"
)

api.add_namespace(accounting)
api.add_namespace(banking)
api.add_namespace(users)
# api.add_namespace(auth)