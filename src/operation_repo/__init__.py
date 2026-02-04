"""
Operation Repo - A Git-like CLI tool for organizing operations.

Stay organized during pentests, HTB, and dev work.
"""

__version__ = "3.0.0"
__author__ = "elprofesor96"

from operation_repo.core import OpClass
from operation_repo.config import ConfigHandler
from operation_repo.server import OpClassToServer
from operation_repo.commits import CommitManager
from operation_repo.notes import NotesManager
from operation_repo.templates import TemplateManager

__all__ = [
    "OpClass",
    "ConfigHandler", 
    "OpClassToServer",
    "CommitManager",
    "NotesManager",
    "TemplateManager",
]
