from google.oauth2 import id_token
from google.auth.transport import requests
import base64



def get_id_from_response(request, client_id):
    csrf_token_cookie = request.cookies.get('g_csrf_token')
    if not csrf_token_cookie:
        return (400, 'No CSRF token in Cookie.')
    csrf_token_body = request.form.get('g_csrf_token')
    if not csrf_token_body:
        return (400, 'No CSRF token in post body.')
    if csrf_token_cookie != csrf_token_body:
        return (400, 'Failed to verify double submit cookie.')

    token = request.form.get("credential").encode("utf-8")

    return id_token.verify_oauth2_token(token, requests.Request(), client_id)

def validate_user(token, user):
    emails_match = user.get("email") == token.get("email")

    return emails_match
