import requests
from quickbooks import Oauth2SessionManager
from flask_restplus import Namespace, Resource 

api = Namespace('accounting', description='Connect and Get Accounting Data')

session_manager = Oauth2SessionManager(
    sandbox=True,
    client_id='Q0LH8ItSo4cZCuka8OAiXdbdea5k5vzWRaytOSeplNroZ4jYQi',
    client_secret='E5FYXGrL85Xm0UqkqXntZQIMlU3hlP6fhvoUEJQ4',
    base_url='http://localhost:8000',
)


# urlpatterns = [
#     url(r'^$', views.index, name='index'),
#     url(r'^(?i)connectToQuickbooks/?$', views.connectToQuickbooks, name='connectToQuickbooks'),
#     url(r'^(?i)signInWithIntuit/?$', views.signInWithIntuit, name='signInWithIntuit'),
#     url(r'^(?i)getAppNow/?$', views.getAppNow, name='getAppNow'),
#     url(r'^(?i)authCodeHandler/?$', views.authCodeHandler, name='authCodeHandler'),
#     url(r'^(?i)disconnect/?$', views.disconnect, name='disconnect'),
#     url(r'^(?i)apiCall/?$', views.apiCall, name='apiCall'),
#     url(r'^(?i)connected/?$', views.connected, name='connected'),
#     url(r'^(?i)refreshTokenCall/?$', views.refreshTokenCall, name='refreshTokenCall')
# ]

@api.route('/connectToQuickbooks')
class Connecting(Resource):
    """ Connect to Quickbook """
    def get(self):
        return 'Connecting to Quickbook', 200

@api.route('/authCodeHandler')
class Authorization(Resource):
    """ Authorization Code Handler """
    def get(self):
        return "Handling Authorization Code", 200

@api.route('/connected')
class Connected(Resource):
    """ Display information after connected """
    def get(self):
        return "Connected Succesfully", 200

@api.route('/disconnect')
class Disconnect(Resource):
    """ Disconnect from Quick Book Online """
    def get(self):
        return "Disconnected from Quickbook", 200

@api.route('/apiCall')
class apiCall(Resource):
    """ List all available APIs """
    def get(self):
        return "Listing available APIs", 200

@api.route('/apiCall/<string:method>')
class makeApiCall(Resource):
    """ List all available APIs """
    def get(self, method):
        return "Making %s API call"%(method), 200













