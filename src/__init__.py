"""
Email Processing and Classification System
Core source code package
"""

__version__ = "1.0.0"
__author__ = "Your Team"
__description__ = "Email Processing and Classification System with AI-powered agents"

from . import agents
from . import extraction
from . import models
from . import services
from . import utils
from . import database

__all__ = [
    "agents",
    "extraction",
    "models",
    "services",
    "utils",
    "database",
]

