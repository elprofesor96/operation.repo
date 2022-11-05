import os
from pathlib import Path
from datetime import datetime


class Utils:
    def __init__(self):
        self.counter = 1

  
            
    def create_auditignore(self):
        pwd = os.getcwd()
        if os.path.isfile(pwd+"/.auditignore"):
            print("[-] Audit repo is already initialized!")
            exit()
        else:
            Path(pwd+"/.auditignore").touch()
            print("[+] Created ", pwd+"/.auditignore")

    def create_folders(self, enabled_folder_list):
        pwd = os.getcwd()
        counter = 1
        for folder in enabled_folder_list:
            try:
                os.mkdir(pwd+"/"+folder)
                print("[+] [{}/{}] Created folder {}".format(counter,len(enabled_folder_list),pwd+"/"+folder))
                counter += 1
            except:
                pass
    
    def create_files(self, enabled_file_list):
        pwd = os.getcwd()
        counter = 1
        for file in enabled_file_list:
            try:
                Path(pwd+"/"+file).touch()
                print("[+] [{}/{}] Created file {}".format(counter,len(enabled_file_list),pwd+"/"+file))
                counter += 1
            except:
                pass

    
    def generate_zipout_name(self):
        pwd = os.getcwd()
        pwd.split(sep="/")[-1] + "-backup.zip"
        name = pwd.split(sep="/")[-1] + "-" + datetime.now().strftime("%Y-%m-%d_%H%M%S") + "-backup.zip"
        #print(name)
        return name

    def write_to_auditignore(self,line_to_write):
        pwd = os.getcwd()
        with open(pwd+"/.auditignore", "a") as auditignore:
            auditignore.write(line_to_write+"\n")
        auditignore.close()

    def read_auditignore(self):
        pwd = os.getcwd()
        try:
            #f = open('{}/.auditignore'.format(pwd), 'r')
            #data = f.readlines()
            with open('{}/.auditignore'.format(pwd), "r") as f:
                names_list = [line.strip() for line in f if line.strip()]
            return names_list
        except:
            print("\n[-] Audit repo is not initialized!")
            exit()
            return False

    def process_auditignore(self,lines):
        results = []
        pwd = os.getcwd()
        for i in lines:
            results.append(pwd+"/"+i.split(sep="\n")[0])
        return results