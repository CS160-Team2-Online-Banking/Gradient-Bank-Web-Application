import re
from decimal import *

def is_email(string):
    lst = re.findall('\S+@\S+', string)
    if lst is None:
        return False;
    return True;


def email_cleanup(string):
    lst = re.findall('\S+@\S+', string)
    if lst is not None:
        return lst
    # Inputted string is poorly formatted or not an email
    return None


def is_address(string):
    # check for PO box, normal address format, and addess with number after (and number after with # included in front)
    # "PO BOX NUMBER", "NUMBER STRING STRING" "NUMBER STRING STRING NUMBER" and "NUMBER STRING STRING #NUMBER"
    # NUMBER signifies any length of numbers, white space should be checked

    # normal format: 12345 real street
    lst = re.findall('\d{1,10}\s\S+\s\S+', string)
    if lst is not None:
        return True

    # number following real format: 12345 real street 12345
    lst = re.findall('\d{1,10}\s\S+\s\S+\s\d{1,10}', string)
    if lst is not None:
        return True
    # 12345 real street #12345
    lst = re.findall('\d{1,10}\s\S+\s\S+\s#\d{1,10}', string)
    if lst is not None:
        return True
    # Assumes no periods in "PO" i.e. NOT "P.O."
    lst = re.findall('[P,p][O,o]\s[B,b][O,o][X,x]\s\d+', string)
    if lst is not None:
        return True

    # Case where there are periods
    lst = re.findall('[P,p].[O,o].\s[B,b][O,o][X,x]\s\d+', string)
    if lst is not None:
        return True
    return False


def clean_address(string):
    # check for PO box, normal address format, and addess with number after (and number after with # included in front)
    # "PO BOX NUMBER", "NUMBER STRING STRING" "NUMBER STRING STRING NUMBER" and "NUMBER STRING STRING #NUMBER"
    # NUMBER signifies any length of numbers, white space should be checked

    # normal format: 12345 real street
    lst = re.findall('\d{1,10}\s\S+\s\S+', string)
    if lst is not None:
        return lst

    # number following real format: 12345 real street 12345
    lst = re.findall('\d{1,10}\s\S+\s\S+\s\d{1,10}', string)
    if lst is not None:
        return lst
    # 12345 real street #12345
    lst = re.findall('\d{1,10}\s\S+\s\S+\s#\d{1,10}', string)
    if lst is not None:
        return lst
    # Assumes no periods in "PO" i.e. NOT "P.O."
    lst = re.findall('[P,p][O,o]\s[B,b][O,o][X,x]\s\d+', string)
    if lst is not None:
        return lst

    # Case where there are periods
    lst = re.findall('[P,p].[O,o].\s[B,b][O,o][X,x]\s\d+', string)
    if lst is not None:
        return lst
    # Not a properly formatted string
    return None


def is_social_security(string):
    lst = re.findall('\d{3}-\d{2}-\d{4}', string)
    if lst is not None:
        return True
    # no hyphen case
    lst = re.findall('\d{9}', string)
    if lst is not None:
        return True
    return False

def clean_social_security(string):
    lst = re.findall('\d{3}-\d{2}-\d{4}', string)
    if lst is not None:
        return lst
    # no hyphen case
    lst = re.findall('\d{9}', string)
    if lst is not None:
        return lst
    return None

def is_phone_number(string):
    #Parenthes is around area code
    lst = re.findall('[(]\d{3}[)]\d{3}-\d{4}', string)
    if lst is not None:
        return True

    # hyphen separating area code instead
    lst = re.findall('\d{3}-\d{3}-\d{4}', string)
    if lst is not None:
        return True

    # no special characters
    lst = re.findall('\d{10}', string)
    if lst is not None:
        return True
    return False


def clean_phone_number(string):
    # Parenthesis around area code
    lst = re.findall('[(]\d{3}[)]\d{3}-\d{4}', string)
    if lst is not None:
        return lst

    # hyphen separating area code instead
    lst = re.findall('\d{3}-\d{3}-\d{4}', string)
    if lst is not None:
        return lst

    # no special characters
    lst = re.findall('\d{10}', string)
    if lst is not None:
        return lst
    return None

def is_balance(string):
    #Only going to take care of this from a functional perspective
    #digits, ., 2 digits
    # Allows for values up to 1 trillion dollars but it should work for now
    lst = re.findall('\d{1,13}\.\d{2}', string)
    if lst is not None:
        return True

    TWOPLACES = Decimal(10) ** -2
    Decimal('3.214').quantize(TWOPLACES)

    return False


def clean_balance(string):
    #Only going to take care of this from a functional perspective
    #digits, ., 2 digits
    # Allows for values up to 1 trillion dollars but it should work for now
    lst = re.findall('\d{1,13}\.\d{2}', string)
    if lst is not None:
        TWOPLACES = Decimal(10) ** -2
        string = Decimal('string').quantize(TWOPLACES)
        return string

    return None