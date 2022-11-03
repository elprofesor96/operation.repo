#!/usr/bin/python3

import argparse
import os

def args_init():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,prog="audit",description="""Init audit repo to stay organised. 
    
Credits:
    https://elprofesor.io
    https://github.com/elprofesor96""", epilog="Example: audit init")
    parser.add_argument("init", help="initialized audit repo",nargs='*', action="store")
    parser.add_argument("backup", help="backing up audit repo into .zip, except for .auditignore files",nargs='*', action="store")
    parser.add_argument("remove", help="remove audit repo files except .zip backup and .auditignore files.",nargs='*', action="store")
    args = parser.parse_args()
    return args, parser

def init():
    pwd = os.getcwd()
    os.system('mkdir {}/nmap'.format(pwd))
    os.system('mkdir {}/buster'.format(pwd))
    os.system('mkdir {}/osint'.format(pwd))
    os.system('mkdir {}/c2'.format(pwd))
    os.system('mkdir {}/proxies'.format(pwd))
    os.system('mkdir {}/phish'.format(pwd))
    os.system('mkdir {}/burp'.format(pwd))
    os.system('mkdir {}/openvpn'.format(pwd))
    os.system('mkdir {}/www'.format(pwd))
    os.system('touch {}/www/index.html'.format(pwd))
    os.system('mkdir {}/smb'.format(pwd))
    os.system('touch {}/ips.txt'.format(pwd))
    os.system('mkdir {}/obsidian'.format(pwd))
    os.system('touch {}/.auditignore'.format(pwd))
    os.system('mkdir {}/webapps'.format(pwd))

    print("\n[*] Audit repo is initialized!")
    return True

def backup():
    ### creates a .zip file from all files from repo except files from .auditignore
    pwd = os.getcwd()
    zip__output_name = pwd.split(sep="/")[-1] + "-backup.zip"
    #print(zip__output_name)
    ## exclude file with full path
    ## exclude_file = pwd+"/audit.py"
    exclude_file_cmd = "-x " + pwd + "/audit.py "
    exclude_file_cmd += "-x " + pwd + "/.auditignore "
    auditignore_lines = read_auditignore()
    for i in auditignore_lines:
        if '.' in i:
            exclude_file_cmd += " -x " + pwd + "/" +  i.split(sep="\n")[0]
        else:
            if os.path.isdir(i.split(sep="\n")[0]):
                exclude_file_cmd += " -x " + pwd + "/" +  i.split(sep="\n")[0] + "/"
            else:
                exclude_file_cmd += " -x " + pwd + "/" +  i.split(sep="\n")[0]
    #print(exclude_file_cmd)
    cmd = "zip -r {} {} {}".format(zip__output_name, pwd, exclude_file_cmd)
    os.system(cmd)
    os.system('echo {} >> .auditignore'.format(zip__output_name))
    return True

def read_auditignore():
    pwd = os.getcwd()
    try:
        f = open('{}/.auditignore'.format(pwd), 'r')
        data = f.readlines()
        f.close()
        return data
    except:
        print("\n[-] Audit repo is not initialized!")
        exit()
        return False

def remove():
    ### delete all files from repo except the ones from .auditignore
    pwd = os.getcwd()
    auditignore_lines = read_auditignore()
    find_cmd_args = ''
    for i in auditignore_lines:
        find_cmd_args += ' -not -name ' + i.split(sep="\n")[0]
    os.system('find {} {} -not -name audit.py -not -name {} -delete'.format(pwd, find_cmd_args, pwd.split(sep="/")[-1]))
    print("\n[*] Audit repo deleted!")
    return True

def main():
    args, parser = args_init()
    if args.init[0] == 'init':
        init()
        exit()
    elif args.init[0] == 'remove':
        remove()
        exit()
    elif args.init[0] == 'backup':
        backup()
        exit()
    else:
        parser.print_help()

    
    

if __name__ == '__main__':
    main()