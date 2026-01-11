# This file makes the "aws_lib" folder act like a package.
# It allows us to import our tools easily in other files.
#
# For example, instead of typing:
#   from aws_lib.core import SessionManager
# We can just type:
#   from aws_lib import SessionManager

from .core import SessionManager    # Import the Authentication tool
from .stacks import StackManager    # Import the Infrastructure Builder tool
from .audit import CostAuditor      # Import the Cost Inspector tool
