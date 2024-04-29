#!/usr/bin/python3

import opsserver.OpsServerClass as OpsServerClass
import argparse

def args_init():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,prog="opsserver",description="""Operation.repo server to host op repos. 

Credits:
    https://elprofesor.io
    https://github.com/elprofesor96/operation.repo""", epilog="Example: opsserver status")
    parser.add_argument("status", help="check status of opsserver", nargs='*', action="store")
    parser.add_argument("createuser", help="create opsserver user. Example: opsserver createuser user", nargs='*', action="store")
    parser.add_argument("deleteuser", help="delete opsserver user. Example: opsserver deleteuser user", nargs='*', action="store")
    parser.add_argument("users", help="list of opsserver users", nargs="*", action="store")
    args = parser.parse_args()
    return args, parser


def main():
    args, parser = args_init()
    try:
        if args.status[0] == 'status':
            OpsServerClass.OpsServerClass().checkSSHPort()
            exit()
        elif args.status[0] == 'createuser' and args.status[1]:
            user_arg = args.status[1]
            OpsServerClass.OpsServerClass().createUser(user_arg)
            exit()
        elif args.status[0] == 'deleteuser' and args.status[1]:
            user_arg = args.status[1]
            OpsServerClass.OpsServerClass().deleteUser(user_arg)
            exit()
        elif args.status[0] == 'users':
            OpsServerClass.OpsServerClass().users()
            exit()
        else:
            parser.print_help()
    except IndexError:
        parser.print_help()
        

    
if __name__ == '__main__':
    main()

