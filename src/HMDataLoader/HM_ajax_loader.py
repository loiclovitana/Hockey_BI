import sys
import argparse
from os import getenv

from HMDataLoader.constants import HM_DATABASE_URL_ENV_NAME, HM_USER_ENV_NAME, HM_PASSWORD_ENV_NAME, HM_URL

AJAX_URL = HM_URL + "ajaxrequest/"


def import_from_ajax(database_url, user, password):
    pass


if __name__ == '__main__':

    argument_parser = argparse.ArgumentParser(
        description="Load data from hockey manager using ajax queries into a database"
    )

    argument_parser.add_argument("-d", "--database-url", default=getenv(HM_DATABASE_URL_ENV_NAME)
                                 , help=f"""Connection string to connect to the database were to save the data.
                                 If not set, use environment variable {HM_DATABASE_URL_ENV_NAME}""")
    argument_parser.add_argument("-u", "--hm-user", default=getenv(HM_USER_ENV_NAME)
                                 , help=f"""User login to connect to Hockey Manager.
                                     If not set, use environment variable {HM_USER_ENV_NAME}""")
    argument_parser.add_argument("-p", "--hm-password", default=getenv(HM_PASSWORD_ENV_NAME)
                                 , help=f"""Password for login to HockeyManager.
                                     If not set, use environment variable {HM_PASSWORD_ENV_NAME}""")


    def check_exists(argument, name):
        if argument is None:
            print(f"Error: Missing argument {name}.")
            argument_parser.print_help()
            sys.exit(1)


    arguments = argument_parser.parse_args()
    check_exists(arguments.database_url, 'database-url')
    check_exists(arguments.hm_user, 'hm-user')
    check_exists(arguments.hm_password, 'hm-password')

    import_from_ajax(arguments.database_url, arguments.hm_user, arguments.hm_password)
