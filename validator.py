from flask import flash
import re

def validateSignup(firstName, lastName, email, phone, pPass, cPass):
    if firstName == "" or lastName == "" or email == "" or phone == "" or pPass == "" or cPass == "":
        flash("Ensure that all fields are filled")
        return False
    
    # Regular expression for email validation

    email_regex = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')

    # Check email format
    if not email_regex.match(email):
        flash('Invalid email format.')
        return False

    # Check password length
    if len(pPass) < 8:
        flash('Password must be at least 8 characters long.')
        return False

    # Check if passwords match
    if pPass != cPass:
        flash('Passwords do not match.')
        return False

    return True