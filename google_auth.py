from google.oauth2 import id_token
from google.auth.transport import requests as google_requests


class GoogleAuthorization:

    def __init__(self,google_id, cookies, form_data) -> None:

        self.google_id = google_id
        self.cookies = cookies
        self.form_data = form_data
        self.google_info = None
        
        # initializer functions
        self.refresh_google_info()


    def get_form_token(self):
        """
        find the token in the response and return it to the caller
        There will only be a reponse avaialble if there was a valid repsonse
        """
        try:

            token = self.form_data.get("credential").encode("utf-8")
            return token
        except:
            return None

    def refresh_google_info(self,form_data=None, cookies=None):
        """
        if the token can be validated with google's library,
        set it in the id_token ot the the returned value

        if either of the form_data or cookies are passed to this 
        function, update them both.
        """
        try:
            if cookies or form_data:
                self.cookies,self.form_data = cookies,form_data
            self.validate_response()
            if self.error_response is None:
                token = self.get_form_token()
            self.google_info = id_token.verify_oauth2_token(
                            token, 
                            google_requests.Request(), 
                            self.google_id)
        except:
            self.google_info = None
            
            pass

    def validate_response(self):
        """
        Do some checks suggest by Google's Documentation
        https://developers.google.com/identity/gsi/web/guides/verify-google-id-token

        """

        self.error_response = None
        
        csrf_token_cookie = self.cookies.get('g_csrf_token')
        if not csrf_token_cookie:
            self.error_response =  (400, 'No CSRF token in Cookie.')
        
        csrf_token_body = self.form_data.get('g_csrf_token')
        if not csrf_token_body:
            self.error_response = (400, 'No CSRF token in post body.')
        
        if csrf_token_cookie != csrf_token_body:
            self.error_response = (400, 'Failed to verify double submit cookie.')

    def get_user_info(self,cookies=None,form_data=None):
        self.refresh_google_info(cookies=cookies, form_data=form_data)

        return self.google_info 

    def validate_user(self, user):
        """
        expect a user with dict-like keys that match the keys, and the values
        of our token keys.

        also check that google has verified the email address

        return true if valid
        """
        try:
            goolge_info = self.get_user_info()
            valid = True
            keys_to_check = ("email")

            for key in keys_to_check:

                valid = user.get(key) == goolge_info.get(key) and valid

            valid = valid and goolge_info.get("email_verified") 

            return valid
        except:
            return False
