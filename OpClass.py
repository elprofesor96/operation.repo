import os
from pathlib import Path
from datetime import datetime
import zipfile
import shutil
import random

class OpClass:
    def __init__(self):
        self.counter = 1
        self.total_default = 5
            
    def create_auditignore(self):
        pwd = os.getcwd()
        if os.path.isfile(pwd+"/.auditignore"):
            print("[-] Audit repo is already initialized!")
            exit()
        else:
            Path(pwd+"/.auditignore").touch()
            print("[+] [2/{}] Created default ".format(self.total_default), pwd+"/.auditignore")

    def create_auditfolder(self):
        pwd = os.getcwd()
        if os.path.isdir(pwd+"/.audit"):
            print("[-] Audit repo is already initialized!")
            exit()
        else:
            os.mkdir(pwd+"/.audit")
            print("[+] [1/{}] Created default ".format(self.total_default), pwd+"/.audit")

    def create_readme(self):
        pwd = os.getcwd()
        if os.path.isfile(pwd+"/README.md"):
            print("[-] Audit repo is already initialized!")
            exit()
        else:
            Path(pwd+"/README.md").touch()
            print("[+] [3/{}] Created default ".format(self.total_default), pwd+"/README.md")

    def create_deployable(self):
        pwd = os.getcwd()
        if os.path.isdir(pwd+"/deployable"):
            print("[-] Audit repo is already initialized!")
            exit()
        else:
            os.mkdir(pwd+"/deployable")
            print("[+] [4/{}] Created default ".format(self.total_default), pwd+"/deployable")
            Path(pwd+"/deployable/index.html").touch()
            print("[+] [5/{}] Created default ".format(self.total_default), pwd+"/deployable/index.html")

    def create_default(self):
        self.create_auditfolder()
        self.create_auditignore()
        pwd = os.getcwd()
        self.write_to_auditignore(".audit")
        self.create_readme()
        self.create_deployable()

    def create_to_deployable(self, enabled_deploy_list, deployable_db):
        pwd = os.getcwd()
        counter = 1
        #print(enabled_deploy_list)
        #deployable_db_path = config
        for deploy in enabled_deploy_list:
            try:
                if os.path.isfile(deployable_db+"/"+deploy):
                    #print(deployable_db+"/"+deploy)
                    ### if copy like aws/script.sh ... cannot copy into aws/script.sh because aws folder does NOT exist
                    ### will implement to copy from aws/script.sh into script.sh on default folder deployable
                    if "/" in deploy:
                        shutil.copy(deployable_db+"/"+deploy, pwd+"/deployable/"+deploy.split(sep="/")[-1])
                        print("[+] [{}/{}] Created deployable {}".format(counter,len(enabled_deploy_list),pwd+"/deployable/"+deploy.split(sep="/")[-1]))
                        counter += 1
                    else:
                        shutil.copy(deployable_db+"/"+deploy, pwd+"/deployable/"+deploy)
                        print("[+] [{}/{}] Created deployable {}".format(counter,len(enabled_deploy_list),pwd+"/deployable/"+deploy))
                        counter += 1
                else:
                    shutil.copytree(deployable_db+"/"+deploy, pwd+"/deployable/"+deploy)
                    print("[+] [{}/{}] Created deployable {}".format(counter,len(enabled_deploy_list),pwd+"/deployable/"+deploy))
                    counter += 1
                    #for script in os.listdir(deployable_db + deploy):
                    #    print("[+] [{}/{}] Created deployable {}".format(counter,len(enabled_deploy_list),pwd+"/deployable/"+deploy+"/"+script))
                    #    counter += 1
                   
            except:
                pass

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
        return name

    def write_to_auditignore(self,line_to_write):
        pwd = os.getcwd()
        with open(pwd+"/.auditignore", "a") as auditignore:
            auditignore.write(line_to_write+"\n")
        auditignore.close()

    def read_auditignore(self):
        pwd = os.getcwd()
        try:
            with open('{}/.auditignore'.format(pwd), "r") as f:
                names_list = [line.strip() for line in f if line.strip()]
            return names_list
        except:
            print("\n[-] Audit repo is not initialized!")
            exit()

    def process_auditignore(self,lines):
        results = []
        pwd = os.getcwd()
        for i in lines:
            results.append(pwd+"/"+i.split(sep="\n")[0])
        return results

    def remove(self):
        ### delete all files from repo except the ones from .auditignore
        pwd = os.getcwd()
        auditignore_lines = self.read_auditignore()
        parsed_lines = self.process_auditignore(auditignore_lines)
        print("\n[*] Remove audit repo.")
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
        if len(os.listdir(".audit")) == 0:
            #shutil.rmtree(".audit")
            remove_list.append(".audit")
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
        #if len(os.listdir(".audit")) == 0:
        #    shutil.rmtree(".audit")
        print("\n[*] Removed audit repo successfuly!")
        return True

    def backup(self):
        ### backing up into .zip file except for files in .auditignore
        pwd = os.getcwd()
        zip__output_name = self.generate_zipout_name()
        auditignore_lines = self.read_auditignore()
        parsed_lines = self.process_auditignore(auditignore_lines)
        print("\n[*] Backing up audit repo.")
        backup_zip = zipfile.ZipFile(pwd+"/.audit/"+zip__output_name, 'w')
        all_files = []
        for p in Path(pwd).rglob("*"):
            all_files.append(p)
        restricted_files = parsed_lines
        zip_list = []
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
            if zip != pwd+"/.audit/"+zip__output_name:
                #if zip != pwd+"/"+".auditignore":
                len_pwd_parsed = len(pwd + "/")
                parsed_zip_path = zip[len_pwd_parsed:]
                backup_zip.write(parsed_zip_path)
                counter += 1
                print("[+] [{}/{}] Zipping {}".format(counter, len(zip_list), parsed_zip_path))
        backup_zip.close()
        print("\n[*] Output saved at ", pwd+"/.audit/"+zip__output_name)
        #self.write_to_auditignore(".audit/"+zip__output_name)
        return pwd+"/.audit/"+zip__output_name

    def init(self, confighandler):
        pwd = os.getcwd()
        print()
        print("[*] Init audit repo.\n")
        ## create audit default files
        self.create_default()
        enabled_folders = confighandler.readFolderStructure()
        self.create_folders(enabled_folders)
        enabled_files = confighandler.readFileStructure()
        self.create_files(enabled_files)
        enabled_deploys = confighandler.readDeployableStructure()
        deployable_db = confighandler.getDeployableFolderPath()
        self.create_to_deployable(enabled_deploys, deployable_db)
        print("\n[*] Audit repo is initialized successfuly!")
        return True

    def init_template(self, confighandler, template):
        #print(template)
        pwd = os.getcwd()
        confighandler.check_custom_template(template)
        print()
        print("[*] Init audit repo with custom template.\n")
        self.create_default()
        enabled_folders = confighandler.readCustomFolderStructure()
        self.create_folders(enabled_folders)
        enabled_files = confighandler.readCustomFileStructure()
        self.create_files(enabled_files)
        enabled_deploys = confighandler.readCustomDeployableStructure()
        deployable_db = confighandler.getDeployableFolderPath()
        self.create_to_deployable(enabled_deploys, deployable_db)
        print("\n[*] Audit repo is initialized successfuly!")
        return True

    def view(readme):
        ### maybe cat file.md | grip -b
        ## cat and save file in memory then grip -b file.md
        #number_list = []
        #for number in range(10000, 15000):
        #    number_list.append(number)
        #port = random.choice(number_list)
        os.system("grip -b {}".format(readme))