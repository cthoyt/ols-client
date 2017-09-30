# -*- coding: utf-8 -*-

"""

Interact with the EBI Ontology Lookup Service. Currently, the use case is tog et all terms from an ontology by name.

"""

from . import api
from . import client
from . import constants
from .api import *
from .client import *
from .constants import *

__all__ = (
    constants.__all__ +
    client.__all__ +
    api.__all__
)

__version__ = '0.0.7'

__title__ = 'ols_client'
__description__ = 'A Python client for the EBI Ontology Lookup Service RESTful API'
__url__ = 'https://github.com/cthoyt/ols-client'

__author__ = 'Charles Tapley Hoyt'
__email__ = 'charles.hoyt@scai.fraunhofer.de'

__license__ = 'Apache 2.0 License'
__copyright__ = 'Copyright (c) 2017 Charles Tapley Hoyt'
