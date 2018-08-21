from django.conf import settings
from django.core.mail import EmailMessage

def email(subject, user_name, email_address):
    print("Sending email to ==>", email_address, " for user: ", user_name)
    message = 'Your handwritten is learned again!'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email_address]
    email = EmailMessage(subject, message, to=recipient_list)
    email.send()