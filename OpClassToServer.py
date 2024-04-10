import ConfigHandler
import subprocess
import socket
import time
import os
import tqdm
import OpClass

class OpClassToServer:
    def __init__(self):
        pass
    
    def checkIfServerIsStarted(self, ip):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        response = sock.connect_ex((ip, 22))
        if response != 0:
            print("\n[-] Cannot connect to audit server.\n[-] Please check audit server and enable ssh port 22")
            exit()
        else:
            return True

    def checkIfUserCanConnect(self, ssh_key, ip, user):
        response = subprocess.run(["ssh", "-q", "-i", "{}".format(ssh_key), "{}@{}".format(user,ip), "-o", "StrictHostKeyChecking no", "-o" , "BatchMode=yes" , "whoami"], capture_output=True)
        parsed_stdout = response.stdout.decode()
        if len(parsed_stdout) < 2:
            print("[-] Check if Server is installed or User is created or SSH key is valid or audit.conf.")
            exit()

    def checkIfAuditRepo(self, repo, ssh_key, ip, user):
        audit_repos = []
        response = subprocess.run(["ssh", "-q", "-i", "{}".format(ssh_key), "{}@{}".format(user,ip), "-o", "StrictHostKeyChecking no", "file", "{}".format(repo + "/.auditignore")], capture_output=True)
        parsed_stdout = response.stdout.decode()
        #print(parsed_stdout)
        if "cannot open" in parsed_stdout:
            pass
        else:
            return True

    def list_repos_from_server(self, ip, ssh_key, user):
        self.checkIfServerIsStarted(ip)
        ssh_key_path = ConfigHandler.ConfigHandler().getSSHKeyFolderPath() + ssh_key
        self.checkIfUserCanConnect(ssh_key_path, ip, user)
        if len(ip) < 2:
            print("\n[-] Check /etc/audit/audit.conf for server configuration.")
            exit()
        print("\n[*] List all repos from audit server:\n")
        #os.system("ssh -q -i {} {}@{} -o 'StrictHostKeyChecking no' ls -1".format(ssh_key_path, user, ip))
        response = subprocess.run(["ssh", "-q", "-i", "{}".format(ssh_key_path), "{}@{}".format(user,ip), "-o", "StrictHostKeyChecking no", "ls", "-1"], capture_output=True)
        all_repos_from_server = response.stdout.decode().split(sep="\n")[:-1]
        for repo in all_repos_from_server:
            #if self.checkIfAuditRepo(repo, ssh_key_path, ip, user):
            #    print(repo)
            print(repo)

    def push_repo(self, ip, ssh_key, user):
        self.checkIfServerIsStarted(ip)
        ssh_key_path = ConfigHandler.ConfigHandler().getSSHKeyFolderPath() + ssh_key
        self.checkIfUserCanConnect(ssh_key_path, ip, user)
        if len(ip) < 2:
            print("\n[-] Check /etc/audit/audit.conf for server configuration.")
            exit()
        zip_name = AuditClass.AuditClass().backup()
        pwd = os.getcwd()
        print()
        dir_name = pwd.split(sep="/")[-1]
        print("[*] Pushing repo: {}".format(dir_name))
        print()
        response = subprocess.run(["ssh", "-q", "-i", "{}".format(ssh_key_path), "{}@{}".format(user,ip), "-o", 'StrictHostKeyChecking no', "mkdir", "-p" ,"{}/.audit".format(dir_name)], capture_output=True)
        os.system("scp -q -i {} -o 'StrictHostKeyChecking no' {} {}@{}:~/{}/.audit/".format(ssh_key_path, zip_name, user, ip, dir_name))
        remove_script_path = ConfigHandler.ConfigHandler().getRemoveScriptPath()
        os.system("ssh -q -i {} -o 'StrictHostKeyChecking no' {}@{} {} /home/{}/{}".format(ssh_key_path, user, ip, remove_script_path , user, dir_name))
        for i in tqdm.tqdm(range(100), colour="green"):
            time.sleep(0.05)
        print()
        #os.system("ssh -q -i {} -o 'StrictHostKeyChecking no' {}@{} unzip -o /home/{}/{}/.audit/{} -d /home/{}/{}/".format(ssh_key_path, user, ip, user, dir_name, zip_name.split(sep="/")[-1], user, dir_name))
        unzip_response = subprocess.run(["ssh", "-q", "-i", "{}".format(ssh_key_path), "{}@{}".format(user, ip) , "-o", "StrictHostKeyChecking no", "unzip", "-o", "/home/{}/{}/.audit/{}".format(user, dir_name, zip_name.split(sep="/")[-1]), "-d", "/home/{}/{}/".format(user, dir_name)], capture_output=True)
        print("[*] Pushed audit repo successfuly!")

    def clone_repo(self, ip, ssh_key, user, repo):
        self.checkIfServerIsStarted(ip)
        ssh_key_path = ConfigHandler.ConfigHandler().getSSHKeyFolderPath() + ssh_key
        if len(ip) < 2:
            print("\n[-] Check /etc/audit/audit.conf for server configuration.")
            exit()
        print()
        print("[*] Cloning repo\n")
        os.system("scp -q -r -i {} {}@{}:~/{} .".format(ssh_key_path, user, ip, repo))
        for i in tqdm.tqdm(range(100), colour="green"):
            time.sleep(0.05)
        print("\n[+] Repo cloned successgully!")

    def cat_readme_from_auditserver(self, ssh_key, user, ip, repo):
        ssh_key_path = ConfigHandler.ConfigHandler().getSSHKeyFolderPath() + ssh_key
        output = subprocess.run(["ssh", "-q", "-i", "{}".format(ssh_key_path), "{}@{}".format(user, ip) , "-o", "StrictHostKeyChecking no", "cat", "/home/{}/{}/README.md".format(user, repo)], capture_output=True)
        return output.stdout.decode()