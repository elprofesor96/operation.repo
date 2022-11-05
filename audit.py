#!/usr/bin/python3

import argparse
import os
from pathlib import Path
import zipfile
import configparser

def config_init():
    return None

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
    
    ## create folderds
    os.mkdir(pwd+"/nmap")
    os.mkdir(pwd+"/buster")
    os.mkdir(pwd+"/osint")
    os.mkdir(pwd+"/c2")
    os.mkdir(pwd+"/proxies")
    os.mkdir(pwd+"/phish")
    os.mkdir(pwd+"/burp")
    os.mkdir(pwd+"/openvpn")
    os.mkdir(pwd+"/www")
    os.mkdir(pwd+"/smb")
    os.mkdir(pwd+"/obsidian")
    os.mkdir(pwd+"/webapps")
    os.mkdir(pwd+"/exploits")

    ## create files
    Path(pwd+"/.auditignore").touch()
    Path(pwd+"/ips.txt").touch()
    Path(pwd+"/www/index.html").touch()

    print("\n[*] Audit repo is initialized!")
    return True

def backup():
    pwd = os.getcwd()
    zip__output_name = pwd.split(sep="/")[-1] + "-backup.zip"
    auditignore_lines = read_auditignore()
    parsed_lines = process_auditignore(auditignore_lines)
    backup_zip = zipfile.ZipFile(zip__output_name, 'w')
    all_files = []
    for p in Path(pwd).rglob("*"):
        all_files.append(p)
    restricted_files = parsed_lines
    zip_list = []
    parsed_restricted_files = []
    for parsed in restricted_files:
        if os.path.isdir(parsed):
            #print("true", parsed)
            for p in Path(parsed).rglob("*"):
               # print(p)
                restricted_files.append(str(p))
        else:
            pass
    for fil in all_files:
        if str(fil) in restricted_files:
            ## restrict from .auditignore
            pass
        else:
            zip_list.append(str(fil))
    print()
    for zip in zip_list:
        print("[+] Zipping {}".format(zip))
        backup_zip.write(zip)
    backup_zip.close()
    print("[*] Output saved at ", pwd+"/"+zip__output_name)
    with open(pwd+"/.auditignore", "a") as auditignore:
        auditignore.write(zip__output_name)
    auditignore.close()


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

def process_auditignore(lines):
    results = []
    pwd = os.getcwd()
    for i in lines:
        results.append(pwd+"/"+i.split(sep="\n")[0])
    return results

def remove():
    ### delete all files from repo except the ones from .auditignore
    pwd = os.getcwd()
    auditignore_lines = read_auditignore()
    processed_lines = process_auditignore(auditignore_lines)
    print(processed_lines)
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