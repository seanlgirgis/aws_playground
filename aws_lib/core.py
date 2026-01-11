import boto3  # The Main AWS Library for Python
import os     # Library to read Environment Variables (like AWS_PROFILE)
import sys
from botocore.exceptions import ProfileNotFound, ClientError

class SessionManager:
    """
    This class handles 'Logging In'. 
    It doesn't do any real work; it just gets us the 'Security Badge' (Session) 
    that we need to do work.
    """
    
    @staticmethod
    def get_session(profile_name=None):
        """
        Creates and returns a logical login session to AWS.
        
        Args:
            profile_name: The specific name of the user profile in ~/.aws/config.
                          If None, it tries to find a default from your environment.
        """
        # 1. Determine which Profile to use
        # If the user didn't specify one, we look for the 'AWS_PROFILE' setting
        # in the computer's environment. If that's missing, we default to 'study'.
        if not profile_name:
            profile_name = os.environ.get('AWS_PROFILE', 'study')
            
        try:
            # 2. Try to Create the Session
            # boto3 will look at your ~/.aws/credentials file.
            # If your profile needs MFA, it might pause here and wait for you 
            # to handle that (though usually that's handled by the 'env_setter' script beforehand).
            return boto3.Session(profile_name=profile_name)
            
        except ProfileNotFound:
            print(f"Error: Profile '{profile_name}' not found.")
            print("Please check your .aws/config file or run 'aws configure'.")
            sys.exit(1) # Stop the program immediately
        except Exception as e:
            print(f"Error creating session: {e}")
            sys.exit(1)
