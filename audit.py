#!/usr/bin/python3

import argparse
import os
from pathlib import Path
import zipfile
import ConfigHandler
import Utils
import shutil


def args_init():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,prog="audit",description="""Init audit repo to stay organised. 
Change audit.conf file to have a more custom audit repo init.
audit.conf is found in /etc/audit/audit.conf

Credits:
    https://elprofesor.io
    https://github.com/elprofesor96/audit.repo""", epilog="Example: audit init")
    parser.add_argument("init", help="initialized audit repo",nargs='*', action="store")
    parser.add_argument("backup", help="backing up audit repo into .zip, except for .auditignore files",nargs='*', action="store")
    parser.add_argument("remove", help="remove audit repo files except .zip backup and .auditignore files.",nargs='*', action="store")
    args = parser.parse_args()
    return args, parser

def init():
    pwd = os.getcwd()
    confighandler = ConfigHandler.ConfigHandler()
    print()
    ## create .auditignore file which is always on by default
    Utils.Utils().create_auditignore()
    enabled_folders = confighandler.readFolderStructure()
    Utils.Utils().create_folders(enabled_folders)
    enabled_files = confighandler.readFileStructure()
    Utils.Utils().create_files(enabled_files)
    print("\n[*] Audit repo is initialized successfuly!")
    return True

def backup():
    ### backing up into .zip file except for files in .auditignore
    pwd = os.getcwd()
    zip__output_name = Utils.Utils().generate_zipout_name()
    auditignore_lines = Utils.Utils().read_auditignore()
    parsed_lines = Utils.Utils().process_auditignore(auditignore_lines)
    backup_zip = zipfile.ZipFile(zip__output_name, 'w')
    all_files = []
    for p in Path(pwd).rglob("*"):
        all_files.append(p)
    restricted_files = parsed_lines
    zip_list = []
    parsed_restricted_files = []
    for parsed in restricted_files:
        if os.path.isdir(parsed):
            for p in Path(parsed).rglob("*"):
                restricted_files.append(str(p))
        else:
            pass
    for fil in all_files:
        if str(fil) in restricted_files:
            pass
        else:
            zip_list.append(str(fil))
    print()
    counter = 0
    for zip in zip_list:
        if zip != pwd+"/"+zip__output_name:
            if zip != pwd+"/"+".auditignore":
                backup_zip.write(zip)
                counter += 1
                print("[+] [{}/{}] Zipping {}".format(counter, len(zip_list)-2, zip))
    backup_zip.close()
    print("\n[*] Output saved at ", pwd+"/"+zip__output_name)
    Utils.Utils().write_to_auditignore(zip__output_name)



def remove():
    ### delete all files from repo except the ones from .auditignore
    pwd = os.getcwd()
    auditignore_lines = Utils.Utils().read_auditignore()
    parsed_lines = Utils.Utils().process_auditignore(auditignore_lines)
    all_files = []
    for p in Path(pwd).rglob("*"):
        all_files.append(p)
    restricted_files = parsed_lines
    remove_list = []
    parsed_restricted_files = []
    for parsed in restricted_files:
        if os.path.isdir(parsed):
            for p in Path(parsed).rglob("*"):
                restricted_files.append(str(p))
        else:
            pass
    for fil in all_files:
        if str(fil) in restricted_files:
            pass
        else:
            remove_list.append(str(fil))
    print()
    counter = 1
    for removed in remove_list:
        try:
            if os.path.isfile(removed):
                print("[-] [{}/{}] Removed {}".format(counter, len(remove_list), removed))
                os.remove(removed)
            else:
                print("[-] [{}/{}] Removed {}".format(counter, len(remove_list), removed))
                shutil.rmtree(removed)
            counter += 1
        except FileNotFoundError:
            counter += 1
            pass
    print("\n[*] Removed audit repo successfuly!")
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