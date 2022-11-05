import configparser

class ConfigHandler:
    def __init__(self):
        self.enabled_folders =  []
        self.enabled_files = []
        self.config = configparser.ConfigParser()
        self.config.read("audit.conf") 
        self.sections = self.config.sections()
         
    def readFolderStructure(self):
        for folder in self.config[self.sections[0]]:
            enabled = self.config[self.sections[0]][folder]
            #print(folder, enabled)
            if enabled == "True":
                self.enabled_folders.append(folder)
        return self.enabled_folders

    def readFileStructure(self):
        for file in self.config[self.sections[1]]:
            enabled = self.config[self.sections[1]][file]
            #print(folder, enabled)
            if enabled == "True":
                self.enabled_files.append(file)
        return self.enabled_files