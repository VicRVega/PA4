import subprocess


# Prompt for common name and passphrase (should be tpa4.chat.test)
common_name = input("Enter your chat server's common name: ")
pass_phrase = "CST311"

# Write common name in a text file for later reference
with open("common_name.txt", "w") as f:
    f.write(common_name)

# Add IP address and common name to /etc/hosts
def modify_hosts_file(ip_address, common_name):
    hosts_entry = f"{ip_address} {common_name}\n"
    
    try:
        # Use subprocess to run the command with sudo and echo the new entry into /etc/hosts
        command = f"echo '{hosts_entry.strip()}' | sudo tee -a /etc/hosts"
        subprocess.run(command, shell=True, check=True, text=True)
        print(f"Successfully added {common_name} to /etc/hosts")
    
    except subprocess.CalledProcessError as e:
        print(f"Failed to modify /etc/hosts: {e}")
        exit(1)

modify_hosts_file("10.0.0.4", common_name)


# Generate private key for server
def generate_private_key(common_name):
    key_file = f"{common_name}-key.pem"
    
    try:
        # Construct the command to generate the private key
        command = ["sudo", "openssl", "genrsa", "-out", key_file, "2048"]
        
        # Run the command
        subprocess.run(command, check=True)
        
        print(f"Private key generated: {key_file}")
    
    except subprocess.CalledProcessError as e:
        print(f"Error generating private key: {e}")
        exit(1)

generate_private_key(common_name)


def generate_csr(common_name):
    key_file = f"{common_name}-key.pem"
    csr_file = f"{common_name}.csr"
    config_file = "/etc/ssl/openssl.cnf"
    
    try:
        # Construct the command to generate the CSR
        command = [
            "sudo", "openssl", "req", "-nodes", "-new", 
            "-config", config_file, "-key", key_file, "-out", csr_file
        ]
        
        # Run the command
        subprocess.run(command, check=True)
        
        print(f"CSR generated: {csr_file}")
    
    except subprocess.CalledProcessError as e:
        print(f"Error generating CSR: {e}")
        exit(1)

generate_csr(common_name)


