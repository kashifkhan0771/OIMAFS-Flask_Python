# ========== Important Imports For Sending Mails And Checking Internet Connection ==========
import urllib.request
import urllib.error
from bootstrap import mail
# ========== Important Imports For Sending Mails And Checking Internet ==========


# ========== Function To Check Is You Are Connected To Internet ==========
def have_connection(host="http://google.com"):
    try:
        urllib.request.urlopen(host)
        return True
    except urllib.error.URLError:
        return False
# ========== Function To Check Is You Are Connected To Internet ==========


# ========= This Function Will Send Password As A Mail To User Who Forgot It's Password ==========
def send_forget_password(sender, receiver, password):
    if have_connection():
        mail.send_message(
            'Forget Password Of ' + str("Online Inventory Management System").upper(),
            sender=sender,
            recipients=[receiver],
            body="Your Password Is : " + password + " \n \n  Do Not Forget It Again"
        )
        return True
    else:
        return False
