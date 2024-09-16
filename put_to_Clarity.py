import paramiko
import os
from datetime import date

def upload_file_sftp(hostname, username, password):
    # Create an SSH client
    ssh = paramiko.SSHClient()
    # Automatically add the server's host key (this disables key verification)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Replace these values with your server details
    hostname = "sftp.clarityservices.com"
    username = "dmp"
    password = "MEmfNSM@6/Ft)ett"
    base_local_dir = "/home/nishant/nishant/Files_to_send_to_Clarity/"
    base_remote_dir = "/accountreview/"
    today = date.today().strftime("%Y-%m-%d")

    # List of files to upload with their respective remote directories
    files_to_upload = [
        {"file": f'CFN_account_review_{today}.csv', "remote_dir": "CraneLending"},
        {"file": f'TDC_account_review_{today}.csv', "remote_dir": "LoonLending"},
#         {"file": f'STC_account_review_{today}.csv', "remote_dir": "Ningodwaaswi"},
        # {"file": f'MCC_account_review_{today}.csv', "remote_dir": "MyCashCenter"},
        # {"file": f'CMX_Cashmax_account_review_{today}.csv', "remote_dir": "CashMax"},
        {"file": f'BSC_account_review_{today}.csv', "remote_dir": "BisonBucks"}   
    ]

    try:
        # Connect to the server
        ssh.connect(hostname, username=username, password=password)

        # Open an SFTP session
        sftp = ssh.open_sftp()

        # Upload each file
        for file_info in files_to_upload:
            local_file_path = os.path.join(base_local_dir, file_info["file"])
            remote_dir = os.path.join(base_remote_dir, file_info["remote_dir"])

            # Extract the file name from the local file path
            file_name = os.path.basename(local_file_path)

            # Upload the local file to the remote directory
            sftp.put(local_file_path, f"{remote_dir}/{file_name}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the SFTP session and the SSH connection
        sftp.close()
        ssh.close()

# Replace these values with your server details
# base_local_dir = "/home/nishant/nishant/Files_to_send_to_Clarity/"
# base_remote_dir = "/accountreview/"

# Call the function
# upload_file_sftp(hostname, username, password, local_file_path, remote_dir)
