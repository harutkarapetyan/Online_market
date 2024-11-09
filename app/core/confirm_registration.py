from services.service_email import send_email
import random
import string


def mail_body(email):

    URL = f"http://127.0.0.1:8000/auth/mail_verification"

    return f"""Dear user,
            Thank you for creating your account.
            Please confirm your email address. The confirmation code is:
            \n
            {URL}/{email}
            \n
            If you have not requested a verification code, you can safely ignore this email․
    """


subject = "Confirm Registration"
sender = "niddleproject@gmail.com"
password = "ngzr kwsw jvcs oiae"


def mail_verification_email(email):
    send_email(subject, mail_body(email), sender, email, password)
