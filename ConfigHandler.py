import configparser
import os

class ConfigHandler:
    def __init__(self):
        self.enabled_folders =  []
        self.enabled_files = []
        self.enabled_deployable = []
        self.config = configparser.ConfigParser()
        self.home_folder = os.path.expanduser("~")
        #self.home_folder = ""
        self.config.read(self.home_folder + "/.op/op.conf")
        #self.ssh_key_folder_path = "/Users/elprofesor/dev/github/operation.repo/ssh/"
        ### db for deployable scripts (where they are stored)
        self.opsdb_folder_path = self.home_folder + "/.op/opsdb/"
        ### remove script path is on auditserver or where auditserver is located
        #self.remove_script_path = "/home/audit/utils.sh"
        self.sections = self.config.sections()
        self.custom_template_sections = []
        self.custom_template_sections_length = 3

    def getHomeFolder(self):
        return self.home_folder

    def getDbFolderPath(self):
        return self.opsdb_folder_path

    def getRemoveScriptPath(self):
        return self.remove_script_path

         
    def readFolderStructure(self):
        if "FOLDER" in self.sections:
            folder_section_contents = self.config["FOLDER"]
            for folder, enabled in folder_section_contents.items():
                #print(folder, enabled)
                if enabled == "on":
                    self.enabled_folders.append(folder)
            return self.enabled_folders

    def readFileStructure(self):
        if "FILE" in self.sections:
            file_section_contents = self.config["FILE"]
            for file, enabled in file_section_contents.items():
                #print(file, enabled)
                if enabled == "on":
                    self.enabled_files.append(file)
            return self.enabled_files

    def readDbStructure(self):
        if "DB" in self.sections:
            db_section_contents = self.config["DB"]
            for db, enabled in db_section_contents.items():
                #print(db, enabled)
                if enabled == "on":
                    self.enabled_deployable.append(db)
            return self.enabled_deployable
        

    def readServerConfig(self):
        if "SERVER" in self.sections:
            audit_server_ip = self.config["SERVER"]["opsserver_ip"]
            ssh_key = self.config["SERVER"]["ssh_key"]
        return audit_server_ip, ssh_key
        
    def check_custom_template(self, template):
        ### a custom template should have all 3 sections: file, folder, deployable
        for section in self.sections:
            if template in section.lower():
                self.custom_template_sections.append(section)
        if len(self.custom_template_sections) is self.custom_template_sections_length:
            return True
        else:
            print()
            print("[-] Custom template init is not configured properly")
            print("[-] Please update ~/.op/op.conf")
            exit()

    def readCustomFolderStructure(self):
        for folder in self.config[self.custom_template_sections[0]]:
            enabled = self.config[self.custom_template_sections[0]][folder]
            #print(folder, enabled)
            if enabled == "True":
                self.enabled_folders.append(folder)
        return self.enabled_folders

    def readCustomFileStructure(self):
        for file in self.config[self.custom_template_sections[1]]:
            enabled = self.config[self.custom_template_sections[1]][file]
            #print(folder, enabled)
            if enabled == "True":
                self.enabled_files.append(file)
        return self.enabled_files

    def readCustomDeployableStructure(self):
        for deploy in self.config[self.custom_template_sections[2]]:
            enabled = self.config[self.custom_template_sections[2]][deploy]
            #print(folder, enabled)
            if enabled == "True":
                self.enabled_deployable.append(deploy)
        return self.enabled_deployable