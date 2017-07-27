# -*- coding: utf-8 -*-

"""

Interact with the EBI Ontology Lookup Service. Currently, the use case is tog et all terms from an ontology by name.

"""

from . import api
from .api import *

__all__ = api.__all__

__version__ = '0.0.2'

__title__ = 'ols_client'
__description__ = 'Interact with EBI Ontology Lookup Service'
__url__ = 'https://github.com/cthoyt/ols-client'

__author__ = 'Charles Tapley Hoyt'
__email__ = 'charles.hoyt@scai.fraunhofer.de'

__license__ = 'Apache 2.0 License'
__copyright__ = 'Copyright (c) 2017 Charles Tapley Hoyt'
