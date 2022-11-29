import socket
import os

class AuditServerClass:
    def __init__(self):
        self.ssh_port = 22
        self.audit_user = ''

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
    
    def checkIfUserExists(self, audit_user):
        data = []
        with open("/etc/passwd", 'r') as file:
            data = file.readlines()
        file.close()
        print()
        print("[*] Checking if user exists.")
        for user in data:
            parsed_user = user.strip().split(sep=":")[0]
            if parsed_user == audit_user:
                print("[-] User {} is already created!".format(audit_user))
                return True
        print("[+] User {} is not found.".format(audit_user, audit_user))
        return False

    def createUser(self, audit_user):
        if os.geteuid() != 0:
            exit("\n[-] You need to have root privileges to create new auditserver users.\n[-] Please try again using sudo.")
        response = self.checkIfUserExists(audit_user)
        if response is False:
            print("[+] Created user: {}".format(audit_user))
            os.system("useradd -m {}".format(audit_user))
            self.createSSHKey(audit_user)
            self.createAuditFile(audit_user)

    def checkIfUserIsAuditUser(self, audit_user):
        audit_file = "/home/" + audit_user + "/.audit"
        if os.path.exists(audit_file):
            return True
        else:
            return False

    def deleteUser(self, audit_user):
        if os.geteuid() != 0:
            exit("\n[-] You need to have root privileges to create new auditserver users.\n[-] Please try again using sudo.")
        if self.checkIfUserIsAuditUser(audit_user):
            os.system("userdel -r {}".format(audit_user))
            print("\n[+] User {} deleted successfully".format(audit_user))
        else:
            print("\n[-] User {} is not an audit user.".format(audit_user))
        
    def createSSHKey(self, audit_user):
        print("[+] Create .ssh folder for user: {}".format(audit_user))
        ssh_folder = "/home/" + audit_user + "/.ssh"
        os.mkdir(ssh_folder)
        print("[+] Create SSH key pair for user: ", audit_user)
        os.system("ssh-keygen -f {} -N ''".format(ssh_folder + "/" + audit_user))
        public_key_path = ssh_folder + "/" + audit_user + ".pub"
        public_key = ''
        with open(public_key_path, 'r') as file:
            public_key = file.read()
        file.close()
        with open(ssh_folder + "/authorized_keys", 'w') as file:
            file.write(public_key)
        file.close()
        os.system("chmod 600 {}".format(ssh_folder + "/authorized_keys"))
        os.system("chown -R {}:{} {}".format(audit_user, audit_user, ssh_folder))

    def createAuditFile(self, audit_user):
        with open("/home/" + audit_user + "/.audit", 'w') as file:
            file.write("audit user")
        file.close()
        os.system("chown -R {}:{} {}".format(audit_user, audit_user, "/home/" + audit_user + "/.audit"))

    def users(self):
        if os.geteuid() != 0:
            exit("\n[-] You need to have root privileges to create new auditserver users.\n[-] Please try again using sudo.")
        all_users = os.listdir("/home")
        audit_users = []
        for user in all_users:
            user_files = os.listdir("/home/" + user)
            if ".audit" in user_files:
                audit_users.append(user)
        length_audit_users = len(audit_users)
        counter = 1
        print()
        print("[*] List of audit users.\n")
        if len(audit_users) == 0:
            print("[-] No audit users found.")
        for audit_user in audit_users:
            print("[*] [{}/{}] User: {}".format(counter, length_audit_users, audit_user))
            counter += 1
        