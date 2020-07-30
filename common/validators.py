"""
# @Author  wk
# @Time 2020/4/24 18:05

"""
import re


DOMAIN_RE = re.compile(
    r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
    r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
    r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
    r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
)


def is_valid_domain(value):
    """
    Return whether or not given value is a valid domain.
    If the value is valid domain name this function returns ``True``, otherwise False
    :param value: domain string to validate
    """
    return True if DOMAIN_RE.match(value) else False


def check_domain_valid(domains_str):
    domain_list = domains_str.split('|')
    for domain in domain_list:
        valid = is_valid_domain(domain)
        if valid is False:
            pass
            # raise ValidationError('invalid domain')
    return True


EMAIL_RE = re.compile(r"""^([a-zA-Z0-9_\-\.]+)@
                    ((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|
                    (([a-zA-Z0-9\-]+\.)+))
                    ([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$""", re.VERBOSE)


def check_email(email, field_name="Email"):
    if not EMAIL_RE.match(email):
        return "%s is non verified" % field_name


URL_RE = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def check_url(url, field_name="Url"):
    if len(url) > 1024:
        return "%s is too long" % field_name
    if not URL_RE.match(url):
        return "%s is illegal" % field_name


