#!/usr/bin/python3

import argparse
import ConfigHandler
import AuditClass
import AuditClassToServer

def args_init():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,prog="audit",description="""Init audit repo to stay organised. 
Change audit.conf file to have a more custom audit repo init.
audit.conf is found in /etc/audit/audit.conf

Credits:
    https://elprofesor.io
    https://github.com/elprofesor96/audit.repo""", epilog="Example: audit init")
    parser.add_argument("init", help="initialize audit repo",nargs='*', action="store")
    parser.add_argument("-c", metavar='custom_init', type=str, nargs='?', help="audit init with custom template from audit.conf. Example: audit init -c web" , action="store")
    parser.add_argument("backup", help="backing up audit repo into .zip, except for .auditignore files",nargs='*', action="store")
    parser.add_argument("remove", help="remove audit repo files except .zip backup and .auditignore files.",nargs='*', action="store")
    parser.add_argument("list", help="list all repos from auditserver",nargs='*', action="store")
    parser.add_argument("push", help="push current repo to auditserver",nargs='*', action="store")
    parser.add_argument("clone", help="clone repo from auditserver. Example: audit clone repo1",nargs='*', action="store")
    parser.add_argument("view", help="view readme.md from auditserver repo. Example: audit view repo1",nargs='*', action="store")
    args = parser.parse_args()
    return args, parser

def init():
    confighandler = ConfigHandler.ConfigHandler()
    AuditClass.AuditClass().init(confighandler)

def init_template(template):
    confighandler = ConfigHandler.ConfigHandler()
    AuditClass.AuditClass().init_template(confighandler, template)

def backup():
    AuditClass.AuditClass().backup()

def remove():
    AuditClass.AuditClass().remove()

def list_repos():
    confighandler = ConfigHandler.ConfigHandler()
    ip, key = confighandler.readServerConfig()
    user = key.split(sep="_")[0]
    AuditClassToServer.AuditClassToServer().list_repos_from_server(ip, key, user)

def push():
    confighandler = ConfigHandler.ConfigHandler()
    ip, key = confighandler.readServerConfig()
    user = key.split(sep="_")[0]
    AuditClassToServer.AuditClassToServer().push_repo(ip, key, user)

def clone(repo):
    confighandler = ConfigHandler.ConfigHandler()
    ip, key = confighandler.readServerConfig()
    user = key.split(sep="_")[0]
    AuditClassToServer.AuditClassToServer().clone_repo(ip, key, user, repo)

def view(repo):
    confighandler = ConfigHandler.ConfigHandler()
    ip, key = confighandler.readServerConfig()
    user = key.split(sep="_")[0]
    readme = AuditClassToServer.AuditClassToServer().cat_readme_from_auditserver(key, user, ip, repo)
    AuditClass.AuditClass.view(readme)

def main():
    args, parser = args_init()
    try:
        if args.init[0] == 'init':
            if args.c is None:
                init()
                exit()
            else:
                init_template(args.c)
                exit()
        elif args.init[0] == 'remove':
            remove()
            exit()
        elif args.init[0] == 'backup':
            backup()
            exit()
        elif args.init[0] == 'list':
            list_repos()
            exit()
        elif args.init[0] == 'push':
            push()
            exit()
        elif args.init[0] == 'clone' and args.init[1]:
            clone(args.init[1])
            exit()
        elif args.init[0] == 'view' and args.init[1]:
            view(args.init[1])
            exit()
        else:
            parser.print_help()
    except IndexError:
        parser.print_help()

if __name__ == '__main__':
    main()