import socket
import os

class OpsServerClass:
    def __init__(self):
        self.ssh_port = 22
        self.op_user = ''

    def checkSSHPort(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1',22))
        print("\n[*] Checking if SSH is running.")
        if result == 0:
            print("[+] SSH port {} is open.".format(self.ssh_port))
            sock.close()
            return True
        else:
            print("[-] SSH port {} is closed.\n[-] Please start SSH Server on port {}.".format(self.ssh_port, self.ssh_port))
            sock.close()
            return False
    
    def checkIfUserExists(self, op_user):
        data = []
        with open("/etc/passwd", 'r') as file:
            data = file.readlines()
        file.close()
        print()
        print("[*] Checking if user exists.")
        for user in data:
            parsed_user = user.strip().split(sep=":")[0]
            if parsed_user == op_user:
                print("[-] User {} is already created!".format(op_user))
                return True
        print("[+] User {} is not found.".format(op_user, op_user))
        return False

    def createUser(self, op_user):
        if os.geteuid() != 0:
            exit("\n[-] You need to have root privileges to create new opsserver users.\n[-] Please try again using sudo.")
        response = self.checkIfUserExists(op_user)
        if response is False:
            print("[+] Created user: {}".format(op_user))
            os.system("useradd -m {}".format(op_user))
            self.createSSHKey(op_user)
            self.createOpUserFile(op_user)

    def checkIfUserIsOpUser(self, op_user):
        op_file = "/home/" + op_user + "/.opuser"
        if os.path.exists(op_file):
            return True
        else:
            return False

    def deleteUser(self, op_user):
        if os.geteuid() != 0:
            exit("\n[-] You need to have root privileges to create new opsserver users.\n[-] Please try again using sudo.")
        if self.checkIfUserIsOpUser(op_user):
            os.system("userdel -r {}".format(op_user))
            print("\n[+] User {} deleted successfully".format(op_user))
        else:
            print("\n[-] User {} is not an op user.".format(op_user))
        
    def createSSHKey(self, op_user):
        print("[+] Create .ssh folder for user: {}".format(op_user))
        ssh_folder = "/home/" + op_user + "/.ssh"
        os.mkdir(ssh_folder)
        print("[+] Create SSH key pair for user: ", op_user)
        os.system("ssh-keygen -f {} -N ''".format(ssh_folder + "/" + op_user + "_opsserver"))
        public_key_path = ssh_folder + "/" + op_user + "_opsserver" + ".pub"
        public_key = ''
        with open(public_key_path, 'r') as file:
            public_key = file.read()
        file.close()
        with open(ssh_folder + "/authorized_keys", 'w') as file:
            file.write(public_key)
        file.close()
        os.system("chmod 600 {}".format(ssh_folder + "/authorized_keys"))
        os.system("chown -R {}:{} {}".format(op_user, op_user, ssh_folder))

    def createOpUserFile(self, op_user):
        with open("/home/" + op_user + "/.opuser", 'w') as file:
            file.write("op user")
        file.close()
        os.system("chown -R {}:{} {}".format(op_user, op_user, "/home/" + op_user + "/.opuser"))

    def users(self):
        if os.geteuid() != 0:
            exit("\n[-] You need to have root privileges to create new opsserver users.\n[-] Please try again using sudo.")
        all_users = os.listdir("/home")
        op_users = []
        for user in all_users:
            user_files = os.listdir("/home/" + user)
            if ".opuser" in user_files:
                op_users.append(user)
        length_op_users = len(op_users)
        counter = 1
        print()
        print("[*] List of op users.\n")
        if len(op_users) == 0:
            print("[-] No op users found.")
        for op_user in op_users:
            print("[*] [{}/{}] User: {}".format(counter, length_op_users, op_user))
            counter += 1
        