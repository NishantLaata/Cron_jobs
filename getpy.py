def getpy(today):
    
    import paramiko
    from datetime import date
    import logging

#     today = date.today().strftime("%Y_%m_%d")

    # Remote server details
    hostname = 'sftp.clarityservices.com'
    port = 22  # Default SSH port
    username = 'dmp'
    password = 'MEmfNSM@6/Ft)ett'

    # Remote directory path and files to be moved
    remote_directory = '/accountreview/outgoing/'

    # Local directory path where files will be moved
    local_directory = '/home/nishant/nishant/Files_from_Clarity/'

    # Establish SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port, username, password)

    sftp = ssh.open_sftp()
    files_to_move = sftp.listdir(remote_directory)
    files_to_move = [file for file in files_to_move if today in file]
    
    if len(files_to_move) == 0:
        logging.info("Clarity no response yet!!!")
        return 0

    logging.info(files_to_move)

    # Move files from remote directory to local directory
    for file_name in files_to_move:
        remote_path = remote_directory + '/' + file_name
        local_path = local_directory + '/' + file_name
        try:
            # Use SFTP to transfer the files
            sftp = ssh.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
            logging.info(f"File '{file_name}' moved successfully.")
        except Exception as e:
            logging.info(f"Failed to move file '{file_name}': {str(e)}")

    # Close the SSH connection
    ssh.close()
    
    return 1