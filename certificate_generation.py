import subprocess


# Prompt for common name and passphrase (should be tpa4.chat.test)
common_name = input("Enter your chat server's common name: ")
challenge_password = input("Enter a challenge password for the server private key: ")

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
        command = [
            "sudo", "openssl", "genrsa", "-out", key_file,
            "-passout", f'pass:{challenge_password}', "2048"
        ]
        
        # Run the command
        subprocess.run(command, check=True, cwd="/etc/ssl/demoCA")
        
        print(f"Private key generated: {key_file}")
    
    except subprocess.CalledProcessError as e:
        print(f"Error generating private key: {e}")
        exit(1)

generate_private_key(common_name)


# Generate certificate signing requests (CSRs) for the server
def generate_csr(common_name):
    key_file = f"{common_name}-key.pem"
    csr_file = f"{common_name}.csr"
    config_file = "/etc/ssl/openssl.cnf"
    
    try:
        # Construct the command to generate the CSR
        command = [
            "sudo", "openssl", "req", "-nodes", "-new", 
            "-config", config_file, "-key", key_file, 
            "-passin", f'pass:{challenge_password}', "-out", csr_file,
            "-subj", "/C=US/ST=CA/L=Seaside/O=CST311/OU=Networking/CN=tpa4.chat.test"
        ]
        
        # Run the command
        subprocess.run(command, check=True, cwd="/etc/ssl/demoCA")
        
        print(f"CSR generated: {csr_file}")
    
    except subprocess.CalledProcessError as e:
        print(f"Error generating CSR: {e}")
        exit(1)

generate_csr(common_name)


# Generate server certificate
def generate_server_certificate(common_name):
    csr_file = f"{common_name}.csr"
    cert_file = f"{common_name}-cert.pem"
    
    try:
        # Construct the command to generate the server certificate
        command = [
            "sudo", "openssl", "x509", "-req", "-days", "365",
            "-in", csr_file,
            "-CA", "cacert.pem",
            "-CAkey", "./private/cakey.pem",
            "-CAcreateserial",
            "-out", cert_file
        ]
        
        # Run the command
        subprocess.run(command, check=True, cwd="/etc/ssl/demoCA")
        
        print(f"Server certificate generated: {cert_file}")
    
    except subprocess.CalledProcessError as e:
        print(f"Error generating server certificate: {e}")
        exit(1)

generate_server_certificate(common_name)

# Move key and certificate to folders as in Lab 6
def move_files(common_name):
    cert_file = f"{common_name}-cert.pem"
    key_file = f"{common_name}-key.pem"
    
    try:
        # Move the certificate to 'newcerts' directory
        move_cert_command = ["sudo", "mv", cert_file, "newcerts"]
        subprocess.run(move_cert_command, check=True, cwd="/etc/ssl/demoCA")
        print(f"Moved {cert_file} to newcerts")
        
        # Move the private key to 'private' directory
        move_key_command = ["sudo", "mv", key_file, "private"]
        subprocess.run(move_key_command, check=True, cwd="/etc/ssl/demoCA")
        print(f"Moved {key_file} to private")
    
    except subprocess.CalledProcessError as e:
        print(f"Error moving files: {e}")
        exit(1)

move_files(common_name)


