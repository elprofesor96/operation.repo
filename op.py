
import argparse
import ConfigHandler
import OpClass
import OpClassToServer
import os

def args_init():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,prog="op",description="""Init operation repo to stay organised. 
Change op.conf file to have a more custom op repo init.
op.conf is found in ~/.op/op.conf

Credits:
    https://elprofesor.io
    https://github.com/elprofesor96/operation.repo""", epilog="Example: op init")
    
    parser.add_argument("init", help="initialize op repo",nargs='*', action="store")
    parser.add_argument("-c", metavar='custom_init', type=str, nargs='?', help="op init with custom template from op.conf. Example: op init -c web" , action="store")
    parser.add_argument("backup", help="backing up op repo into .zip, except for .opignore files",nargs='*', action="store")
    parser.add_argument("remove", help="remove op repo files except .zip backup and .opignore files.",nargs='*', action="store")
    parser.add_argument("list", help="list all repos from opsserver",nargs='*', action="store")
    parser.add_argument("push", help="push current repo to opsserver",nargs='*', action="store")
    parser.add_argument("clone", help="clone repo from opsserver. Example: op clone repo1",nargs='*', action="store")
    parser.add_argument("view", help="view readme.md from opsserver repo. Example: op view repo1",nargs='*', action="store")
    args = parser.parse_args()
    return args, parser

def init():
    confighandler = ConfigHandler.ConfigHandler()
    OpClass.OpClass().init(confighandler)

def init_template(template):
    confighandler = ConfigHandler.ConfigHandler()
    OpClass.OpClass().init_template(confighandler, template)

def backup():
    OpClass.OpClass().backup()

def remove():
    OpClass.OpClass().remove()

def list_repos():
    confighandler = ConfigHandler.ConfigHandler()
    ip, key = confighandler.readServerConfig()
    user = key.split(sep="_")[0].split(sep="/")[-1]
    OpClassToServer.OpClassToServer().list_repos_from_server(ip, key, user)

def push():
    confighandler = ConfigHandler.ConfigHandler()
    ip, key = confighandler.readServerConfig()
    user = key.split(sep="_")[0].split(sep="/")[-1]
    OpClassToServer.OpClassToServer().push_repo(ip, key, user)

def clone(repo):
    confighandler = ConfigHandler.ConfigHandler()
    ip, key = confighandler.readServerConfig()
    user = key.split(sep="_")[0].split(sep="/")[-1]
    OpClassToServer.OpClassToServer().clone_repo(ip, key, user, repo)

def view(repo):
    confighandler = ConfigHandler.ConfigHandler()
    ip, key = confighandler.readServerConfig()
    user = key.split(sep="_")[0].split(sep="/")[-1]
    readme = OpClassToServer.OpClassToServer().cat_readme_from_opsserver(key, user, ip, repo)
    OpClass.OpClass.view(readme)

def default_op_config_init_first_run():
    home_folder = ConfigHandler.ConfigHandler().getHomeFolder()
    default_op_conf = [
        "[SERVER]",
        "opsserver_ip = [127.0.0.1]",
        "ssh_key = [example_key_path]",
        "[FOLDER]",
        "[FILE]",
        "[DB]",
    ]
    try:
        os.mkdir(home_folder + "/.op")
        os.mkdir(home_folder + "/.op/opsdb")
        with open(home_folder + "/.op/op.conf", 'w') as file:
            for line in default_op_conf:
                file.write(line + "\n")
        file.close()
    except:
        pass



def main():
    default_op_config_init_first_run()
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