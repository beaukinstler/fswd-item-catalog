from google.oauth2 import id_token
from google.auth.transport import requests
import base64

class GoogleAuthorization:

    def __init__(self,google_id, request_response) -> None:

        self.google_id = google_id
        self.request_response = request_response
        
        # initializer functions
        self.set_reqeust_response(response=request_response)
        self.set_token()


    def get_token(self):
        """
        find the token in the response and return it to the caller
        There will only be a reponse avaialble if there was a valid repsonse
        """
        try:
            token = self.request_response.form.get("credential").encode("utf-8")
            return token
        except:
            return None

    def set_token(self):
        """
        if the token can be validated with google's library,
        set it the the id_token ot the the returned value
        """
        try:
            token = self.get_token()
            self.id_token = id_token.verify_oauth2_token(
                            token, 
                            requests.Request(), 
                            self.google_id)
        except:
            self.id_token = None
            
            pass

    def set_reqeust_response(self, response):
        """
        set and validate the response.
        
        Response should only be available if valid
        """

        self.request_response = response
        self.validate_response()
        if self.error_response is not None:
            self.request_response = None

    # def get_id_from_response(self,request):


        
    #     csrf_token_cookie = request.cookies.get('g_csrf_token')
    #     if not csrf_token_cookie:
    #         return (400, 'No CSRF token in Cookie.')
    #     csrf_token_body = request.form.get('g_csrf_token')
    #     if not csrf_token_body:
    #         return (400, 'No CSRF token in post body.')
    #     if csrf_token_cookie != csrf_token_body:
    #         return (400, 'Failed to verify double submit cookie.')

    #     token = request.form.get("credential").encode("utf-8")

    #     return id_token.verify_oauth2_token(token, requests.Request(), client_id)
    
    def validate_response(self):

        self.error_response = None
        
        csrf_token_cookie = self.request_response.cookies.get('g_csrf_token')
        if not csrf_token_cookie:
            self.error_response =  (400, 'No CSRF token in Cookie.')
        
        csrf_token_body = self.request.form.get('g_csrf_token')
        if not csrf_token_body:
            self.error_response = (400, 'No CSRF token in post body.')
        
        if csrf_token_cookie != csrf_token_body:
            self.error_response = (400, 'Failed to verify double submit cookie.')

        

    def validate_user(self, user):
        """
        expect a user with dict-like keys that match the keys, and the values
        of our token keys.

        return true if valid
        """
        token = self.get_token()
        valid = True
        keys = ("email","sub")

        for key in keys:

            valid = user.get(key) == token.get(key) and valid

        valid = valid and token.get("email_verified") 

        return valid
