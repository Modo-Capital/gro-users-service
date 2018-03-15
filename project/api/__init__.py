#project/api/__init__.py

from flask_restplus import Api


### Importing Namespaces
from .auth import api as auth
from .users import api as users
from .companies import api as companies
from .banking import api as banking
from .accounting import api as accounting

### Define API with restplus.api
api = Api (
    version='0.1',
    title='Gro Users API', 
    description="Gro User Restful API"
)


api.add_namespace(auth)
api.add_namespace(users)
api.add_namespace(companies)
api.add_namespace(accounting)
api.add_namespace(banking)
