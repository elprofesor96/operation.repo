#!/usr/bin/python3

import AuditServerClass
import argparse

def args_init():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,prog="auditserver",description="""Audit server to host audit repos. 

Credits:
    https://elprofesor.io
    https://github.com/elprofesor96/audit.repo""", epilog="Example: auditserver status")
    parser.add_argument("status", help="check status of auditserver", nargs='*', action="store")
    parser.add_argument("createuser", help="create auditserver user. Example: auditserver createuser user", nargs='*', action="store")
    parser.add_argument("deleteuser", help="delete auditserver user. Example: auditserver deleteuser user", nargs='*', action="store")
    parser.add_argument("users", help="list of auditserver users", nargs="*", action="store")
    args = parser.parse_args()
    return args, parser


def main():
    args, parser = args_init()
    try:
        if args.status[0] == 'status':
            AuditServerClass.AuditServerClass().checkSSHPort()
            exit()
        elif args.status[0] == 'createuser' and args.status[1]:
            user_arg = args.status[1]
            AuditServerClass.AuditServerClass().createUser(user_arg)
            exit()
        elif args.status[0] == 'deleteuser' and args.status[1]:
            user_arg = args.status[1]
            AuditServerClass.AuditServerClass().deleteUser(user_arg)
            exit()
        elif args.status[0] == 'users':
            AuditServerClass.AuditServerClass().users()
            exit()
        else:
            parser.print_help()
    except IndexError:
        parser.print_help()
        

    
if __name__ == '__main__':
    main()

