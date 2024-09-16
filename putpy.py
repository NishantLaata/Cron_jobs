# import paramiko

# def upload_file(host = 'sftp.clarityservices.com', port = 22, user = 'dmp', password = 'MEmfNSM@6/Ft)ett', local_path = sys.argv[1]
# portfolio_dir = sys.argv[2]
# remote_path = f"{portfolio_dir}/{local_path}" ):
    
    
#     try:
#         transport = paramiko.Transport((host, port))
#         transport.connect(username=username, password=password)
        
#         sftp = paramiko.SFTPClient.from_transport(transport)
#         sftp.put(local_path, remote_path)
        
#         sftp.close()
#         transport.close()
        
#         print(f"File '{local_path}' uploaded to '{remote_path}' successfully.")
#     except Exception as e:
#         print(f"Error uploading file: {e}")

# # # Replace with your actual server details and file paths
# # host = 'your_server_address'
# # port = 22  # SFTP port
# # username = 'your_username'
# # password = 'your_password'
# # local_path = 'path_to_local_file/file.txt'  # Path to your local file
# # remote_path = '/remote/directory/file.txt'  # Destination path on the remote server

# # upload_file(host, port, username, password, local_path, remote_path)


# #!/bin/bash

# username="dmp"
# password="MEmfNSM@6/Ft)ett"
# portfolio_dir="/remote/directory"

# # List of local files to upload
# files_to_upload=("file1.txt" "file2.txt" "file3.txt")

# for local_file in "${files_to_upload[@]}"; do
#     ./your_expect_script.exp "$local_file" "$portfolio_dir" "$username" "$password" &
# done

# # Wait for all background processes to finish
# wait
