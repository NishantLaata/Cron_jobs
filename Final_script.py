##################
# Load libraries
##################

import logging
import os
import sys
from datetime import date

# Custom packages
from Upload_AR_to_SQL import Uploading_to_sql as upsql
from AR_Final_Pull import AR_FINAL_script as ARF
from AR_second_pull import AR_second_pull as ARS
from put_to_Clarity import upload_file_sftp as upsftp
from getpy import getpy
# Data science packages
import numpy as np

import pandas as pd
# Utility
import time
from datetime import datetime
from datetime import date
from datetime import timedelta

log_loc = "/home/nishant/nishant/Cron_jobs/AR_Clarity_log.log"

# Log file set up
logging.basicConfig(filename=log_loc, level=logging.INFO)
start = time.perf_counter()
logging.info("Execution Starts")

logging.info("Driver Setup complete")

logging.info("############################")
logging.info(datetime.today())
logging.info("Batch Update Starting")
logging.info("############################")


# # #############################################################################
# # #############################################################################

logging.info("AR Second Pull")

ARS()

logging.info("AR Second Pull completed")
end = time.perf_counter()
logging.info("Total time taken: {} seconds".format(round(end-start, 2)))

# ##############################################################################

logging.info("AR Final Script")

ARF()

logging.info("AR Final Script completed")
logging.info("AR Final Script Process completed")
end = time.perf_counter()
logging.info("Total time taken: {} seconds".format(round(end-start, 2)))


# ##############################################################################
logging.info("Uploading files to clarity")
logging.info("Total time taken: {} seconds".format(round(end-start, 2)))

# upsftp(hostname, username, password, local_file, remote_dir)
upsftp('sftp.clarityservices.com', 'dmp', 'MEmfNSM@6/Ft)ett')

# upsftp('sftp.clarityservices.com', 'dmp', 'MEmfNSM@6/Ft)ett', local_file, remote_dir)

logging.info("Files uploaded to Clarity")
end = time.perf_counter()
logging.info("Total time taken: {} seconds".format(round(end-start, 2)))

# Check if Clarity sent us the data back

today = date.today().strftime("%Y_%m_%d")
yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
secs = 900  # Number of seconds to sleep
remote_directory = '/accountreview/outgoing/'
local_directory = '/home/nishant/nishant/Files_from_Clarity/'
desired_string = today
counter = 0
ind=0
 # Specify the substrings to check
# substrings_to_check = ["CFN_account_review_" + today, "TDC_account_review_" + today, "MCC_account_review_" + today, "CMX_Cashmax_account_review_" + today]
substrings_to_check = ["CFN_account_review_" + today, "TDC_account_review_" + today, "BSC_account_review_" + today]
            
         
missing_files = substrings_to_check.copy()

while missing_files:
# while ind == 0: 
    
    
    logging.info(f"Waiting on files from Clarity: Attempt {counter}")
    
    print("Waiting on files from Clarity")

    logging.info(f"Sleeping for {int(secs/60)} minutes")
    print(f"Sleeping for {int(secs/60)} minutes")

    time.sleep(secs)
    counter += 1
    
   
    try:
        
        logging.info("Trying to Pull the files from CLarity Server")
        logging.info(datetime.today())
        ind = getpy(today)
    
    except Exception as e:
        
        logging.info(f'Error {e}')
        logging.info("Connection Timed Out, Unable to pull files")
        logging.info(datetime.today())

 
            
    file_names = os.listdir(local_directory)

   
    for sub in missing_files:
        for file_name in file_names:
            if sub in file_name:
                missing_files.remove(sub)
                logging.info("File found: " + file_name)
                break

    if missing_files:
        logging.info("Waiting for files to arrive...")
logging.info("All files have arrived.")
            
logging.info("Files from Clarity received")
end = time.perf_counter()
logging.info("Total time taken: {} seconds".format(round(end-start, 2)))

print("Files from Clarity received")
# ###############################################################################
# ##############################################################################

logging.info("Uplaoding clarity data to SQL")

upsql(today)

logging.info("Uplaoding clarity data to SQL completed")
logging.info("Uplaoding clarity data to SQL Process completed")
end = time.perf_counter()
logging.info("Total time taken: {} seconds".format(round(end-start, 2)))


# ##############################################################################

logging.info("AR Process completed")
end = time.perf_counter()
logging.info("Total time taken: {} seconds".format(round(end-start, 2)))