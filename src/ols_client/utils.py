# -*- coding: utf-8 -*-

from requests.compat import quote_plus


def get_user_ols_search_url(name):
    """Gets the URL of the page a user should check when they're not sure about an entity's name

    :param str name: The name to search
    :return: The url to link users to
    :rtype: str
    """
    return 'http://www.ebi.ac.uk/ols/search/?q={}'.format(quote_plus(name))
