    #############
    # FINAL SCRIPT
    ############
def AR_FINAL_script():

    import pandas as pd
    import numpy as np
    import LendemDS as ds
    import logging
    import sys
    import os
    import gc
    from joblib import load
    from datetime import datetime
    import datetime
    import pandas as pd
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    import numpy as np
    import LendemDS as ds

    import time
    from datetime import date
    from datetime import datetime
    from datetime import timedelta
    

    import os
    import gc

    ###########
    # Reading in the data from 2nd pull
    ###########
    from datetime import datetime, timedelta
    today = date.today().strftime("%Y-%m-%d")
    yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    query_from_2nd_pull = f'''SELECT * FROM ndl.AR_ClarityBatchData_pull2 where date_of_batch_run = '{today}';'''

    df = ds.mysql_query(query = query_from_2nd_pull,
    user = 'nishant',
    password = 'fai6ieMu',
    mode='pull',
    db ='db6')
    
    logging.info("Line 45")
    logging.info(datetime.today())
   

    # query_from_TDC_pull = f'''SELECT * FROM ndl.AR_ClarityBatchData_pull1 where date_of_batch_run > '2023-03-29';'''
    # df = ds.mysql_query(query = query_from_TDC_pull,
    # user = 'nishant',
    # password = 'fai6ieMu',
    # mode='pull',
    # db ='db6')


    df = df.drop_duplicates()
    print(df.shape)

    ###########
    # Creating a customer list on customerid and portfolio from 1st pull to find there records on core_infinity.cutomers
    ###########
    customer_list = df[['customerid', 'portfolio']].values.tolist()

    # join the tuples with commas and surround the portfolio value with quotes
    customer_conditions = ', '.join([f"({cid}, '{portfolio}')" for cid, portfolio in customer_list])

    q1 = f""" 
        SELECT CustomerID as customerid, portfolio, xid, FirstName as first_name, LastName as last_name, MiddleName as middle_initial, SSN as social_security_number, DOB as date_of_birth, 
        HomeAddress as street_address_1, HomeCity as city, HomeState as state, HomeZip as zip_code, ABANumber as bank_routing_number, AccountNumber as bank_account_number, 
        HomePhone as home_phone, CellPhone as cell_phone, WorkPhone as work_phone, Email as email_address, MonthlyIncome as net_monthly_income 
        FROM core_infinity.customers 
        WHERE (customerid, portfolio) IN ({customer_conditions})
    """

    df1 = ds.mysql_query(query = q1,
    user = 'nishant',
    password = 'fai6ieMu',
    mode='pull',
    db ='db6')
    
    logging.info("Line 82")
    logging.info(datetime.today())
   
    print(df1.shape)


    #########
    # Performing left join to append those customers information
    #########
    merge_loanid_1 = pd.merge(df,df1,on=['customerid','portfolio'],how='left')
    print(merge_loanid_1.shape)

    #########
    # Dropping null xids from dataframe
    #########
    #     merge_loanid_1.dropna(subset=['xid'], inplace=True)
    #     print('dropping null xids: ',merge_loanid_1.shape)
    ##########
    # Creating a list of xids from the dataframe to get more information on them from lead inbox
    ##########
    merge_loanid_1_xid_list = merge_loanid_1[merge_loanid_1['xid'].notnull()]['xid'].tolist()
    #     merge_loanid_1 = merge_loanid_1_xid_list
    merge_loanid_1['xid'] = merge_loanid_1['xid'].astype('Int64')
    fill_value = -1
    merge_loanid_1['xid'] = merge_loanid_1['xid'].fillna(fill_value)
    ##########
    # Creating a list of xids from the dataframe to get more information on them from lead inbox
    ##########
    #     merge_loanid_1_xid_list = merge_loanid_1['xid'].tolist()

    ##########
    # Reading in data from leadInboxdb7
    #########
    # Define the batch size
    BATCH_SIZE = 1000  # Adjust this value based on your needs and database capabilities

    # Function to split the list into chunks
    def batch_list(data, batch_size):

        for i in range(0, len(data), batch_size):
            yield data[i:i + batch_size]
            

    # SQL query template
    query_template = '''SELECT id as xid, ipaddress, addressmonths, empmonths FROM leadinbox.LeadInbox WHERE id IN ({ids});'''

    # Initialize an empty DataFrame to store results
    all_data = []


    # Iterate through batches of merge_loanid_1_xid_list
    for batch in batch_list(merge_loanid_1_xid_list, BATCH_SIZE):
        # Join the batch list into a string of IDs
        ids = ','.join(str(item) for item in batch)
        
        # Create the SQL query for the current batch
        lead_inbox_db7 = query_template.format(ids=ids)
        
        try:
            # Execute the query
            lead_inboxdb7 = ds.mysql_query(query=lead_inbox_db7, user='nishant', password='fai6ieMu', mode='pull', db='db7')
            
            if len(lead_inboxdb7) > 0:
                print("Batch query successful!")
                logging.info('Batch query to db7 successful!')
                
                # Append the batch result to the all_data list
                all_data.append(lead_inboxdb7)
            else:
                raise Exception("Failed to retrieve data for the current batch")
        
        except Exception as e:
            # Handle exceptions
            print(f"Error: {e}")
            logging.error(f"Error during batch query: {e}")

    # Concatenate all the batches into a single DataFrame
    if all_data:
        final_data = pd.concat(all_data, ignore_index=True)
        print("Data retrieval successful!")
        logging.info('Data retrieval from db7 successful!')
    else:
        final_data = pd.DataFrame()
        print("No data retrieved.")
        logging.warning('No data retrieved from db7.')

    # Continue with the remaining code
    print("Continuing with the remaining code...")

#     try:
#     #      Reading in db3   
#             lead_inboxdb3 = ds.mysql_query(query = lead_inbox_db3,
#                 user = 'nishant',
#                 password = 'fai6ieMu',
#                 mode='pull',
#                 db ='leads')
#             if len(lead_inboxdb3) > 0:
                
#                 print("Connection to SQL Server successful!")
#                 logging.info('Connection to db3 Successful!')

#             ##########
#             # Looking for xids which are present in db3 and not db7 and then concatenating them on db7
#             ########
#             else:
#                 raise Exception("Failed to connect to SQL Server")

#     except Exception as e:
#         # If an exception occurs during the connection attempt, handle it here
#             print(f"Error: {e}")

    if len(lead_inboxdb7) > 0 :
#     and len(lead_inboxdb3) > 0  

    # check for xids that are in dataframe2 but not in dataframe1

#             missing_xids = lead_inboxdb3[~lead_inboxdb3['xid'].isin(lead_inboxdb7['xid'])]
#             # concatenate missing_xids with dataframe1
#             lead_inboxdb7 = pd.concat([lead_inboxdb7, missing_xids], ignore_index=True)
#     #     changing the datatype of xid in both the dataframe
            
            lead_inboxdb7['xid'] = lead_inboxdb7['xid'].fillna(fill_value)

            final_dataframe = pd.merge(merge_loanid_1,lead_inboxdb7,on='xid',how='left')
            print('Final_dataframe_shape',final_dataframe.shape)

#     if len(lead_inboxdb3) > 0:
#             final_dataframe = pd.merge(merge_loanid_1,lead_inboxdb3,on='xid',how='left')

    if len(lead_inboxdb7) > 0:
            final_dataframe = pd.merge(merge_loanid_1,lead_inboxdb7,on='xid',how='left')
#   if     len(lead_inboxdb3) == 0 and 
    if len(lead_inboxdb7) == 0 :
            final_dataframe = merge_loanid_1
            final_dataframe['origination_ip_address'] = np.nan
            final_dataframe['months_at_current_employer'] = np.nan
            final_dataframe['months_at_address'] = np.nan

    ##########
    # Creating the final Dataframe
    ##########


    logging.info("Line 150")
    logging.info(datetime.today())


        # create a new datetime object using the current date and time
    dt = datetime.now()

    # convert the datetime object to a pandas Timestamp object
    ts = pd.Timestamp(dt)

    # assign the Timestamp object to the 'inquiry_received_at' column in final_dataframe
    final_dataframe['inquiry_received_at'] = ts


    final_dataframe['inquiry_tradeline_type']='C3'

    ###########
    # renaming few columns in final_dataframe as per the requirement by clarity
    ###########
    final_dataframe = final_dataframe.rename({'ipaddress':'origination_ip_address', 'empmonths':'months_at_current_employer', 'addressmonths': 'months_at_address' },axis=1)

    ###########
    # Creating the final_dataframe to send to clarity
    ###########
    final_dataframe['work_phone_extension'] = None
    final_dataframe1 = final_dataframe[['inquiry_received_at','inquiry_tradeline_type','first_name','last_name','middle_initial','social_security_number','date_of_birth','street_address_1','city','state','zip_code','bank_routing_number','bank_account_number','home_phone','cell_phone','work_phone','work_phone_extension','email_address','origination_ip_address','net_monthly_income','months_at_address','months_at_current_employer','customerid','loanid','portfolio']]
    final_dataframe1 = final_dataframe1.rename(columns={'customerid': 'pass_through_1', 'loanid': 'pass_through_2', 'portfolio': 'pass_through_3'})
    final_dataframe1['home_phone'] = final_dataframe1['home_phone'].str.replace('[-() ]', '')
    final_dataframe1['cell_phone'] = final_dataframe1['cell_phone'].str.replace('[-() ]', '')
    final_dataframe1['work_phone'] = final_dataframe1['work_phone'].str.replace('[-() ]', '')

    #     Check for duplicates and drop them

    from datetime import datetime, timedelta
    # today = date.today().strftime("%Y-%m-%d")
    # yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    # query_from_final_pull = f'''SELECT * FROM ndl.AR_ClarityBatchData_pull_files_sent where inquiry_received_at > '{yesterday}' and inquiry_received_at < '{today}';'''

    # Calculate date range for the past 10 days
    today = datetime.today().date()
    ten_days_ago = today - timedelta(days=10)

    # Format dates as strings in 'YYYY-MM-DD' format
    today_str = today.strftime('%Y-%m-%d')
    ten_days_ago_str = ten_days_ago.strftime('%Y-%m-%d')

    # Prepare the dynamic SQL query with placeholders
    query_from_final_pull = f'''SELECT * FROM ndl.AR_ClarityBatchData_pull_files_sent where inquiry_received_at > '{ten_days_ago_str}';'''

    ten_days_ago_data = ds.mysql_query(query = query_from_final_pull,
    user = 'nishant',
    password = 'fai6ieMu',
    mode='pull',
    db ='db6')

    # Assuming final_dataframe1 and ten_days_ago_data are already defined DataFrames

    # Create a temporary column in final_dataframe1
    final_dataframe1['Column_temp'] = final_dataframe1['pass_through_2'].astype(str) + '_' + final_dataframe1['pass_through_3'].astype(str)

    # Create a temporary column in ten_days_ago_data
    ten_days_ago_data['Column_temp'] = ten_days_ago_data['pass_through_2'].astype(str) + '_' + ten_days_ago_data['pass_through_3'].astype(str)

    # Filter final_dataframe1 based on the temporary column in ten_days_ago_data
    final_dataframe = final_dataframe1[~final_dataframe1['Column_temp'].isin(ten_days_ago_data['Column_temp'])].copy()

    # Drop the temporary column
    final_dataframe = final_dataframe.drop(columns=['Column_temp'])

    # Assign final_dataframe to final_dataframe1
    final_dataframe1 = final_dataframe

    
    # final_dataframe1['Column_temp'] = final_dataframe1['pass_through_2'].astype(str) + '_' + final_dataframe1['pass_through_3'].astype(str)
    # ten_days_ago_data['Column_temp'] = ten_days_ago_data['pass_through_2'].astype(str) + '_' + ten_days_ago_data['pass_through_3'].astype(str) 


    # final_dataframe = final_dataframe1[~final_dataframe1['Column_temp'].isin(ten_days_ago_data['Column_temp'])].copy()
    # final_dataframe = final_dataframe.drop(columns=['Column_temp'])
    # final_dataframe1 = final_dataframe 


    #     Deduping today's files
    final_dataframe_dedupe = final_dataframe1.drop_duplicates(subset=['pass_through_2', 'pass_through_3' , 'inquiry_received_at'])
    print('After Final Deduping',final_dataframe_dedupe.shape)
    final_dataframe1 = final_dataframe_dedupe
    ################
    ################
    # DIVIDING Customers as per Portfolio
    ################
    ################

    logging.info("Line 192")
    logging.info(today)


    CFN = final_dataframe1[final_dataframe1['pass_through_3']=='CFN']
    print('CFN_customer_count:',CFN.shape)
    
    BSC = final_dataframe1[final_dataframe1['pass_through_3']=='BSC']
    print('BSC_customer_count:',BSC.shape)

    TDC = final_dataframe1[final_dataframe1['pass_through_3']=='TDC']
    print('TDC_customer_count:',TDC.shape)

    STC = final_dataframe1[final_dataframe1['pass_through_3']=='STC']
    print('STC_customer_count:',STC.shape)

    MCC = final_dataframe1[final_dataframe1['pass_through_3']=='MCC']
    print('MCC_customer_count:',MCC.shape)

    CMX = final_dataframe1[final_dataframe1['pass_through_3']=='CMX']
    print('CMX_customer_count:',CMX.shape)

    
    # print('CMX_Cashmax_customer_count:',CashMax.shape)
    # print('CMX_Finance_customer_count:',CMX_Finance.shape)


    ########################
    ########################
    # Pulling in Will's table to check for active states
    # pulling wills table 

    W_table = f'''SELECT * FROM whp.tableau_suppressions;'''
    Wills_table = ds.mysql_query(query = W_table,
    user = 'nishant',
    password = 'fai6ieMu',
    mode='pull',
    db ='db6')

    ######################
    ######################


    # Checking for only active states and creating a final dataframe for them
    # will_table_Only_reloans = Wills_table[Wills_table['combokey'].isin(['CFNReloans','TDCReloans','STCReloans','MCCReloans','CMXReloans','BSCReloans'])]
    will_table_Only_reloans = Wills_table[Wills_table['combokey'].isin(['CFNReloans','TDCReloans','STCReloans','MCCReloans','CMXReloans'])]


    only_CFN_Reloans = will_table_Only_reloans[will_table_Only_reloans['combokey']=='CFNReloans']
    only_BSC_Reloans = will_table_Only_reloans[will_table_Only_reloans['combokey']=='BSCReloans']
    only_TDC_Reloans = will_table_Only_reloans[will_table_Only_reloans['combokey']=='TDCReloans']
    only_STC_Reloans = will_table_Only_reloans[will_table_Only_reloans['combokey']=='STCReloans']
    only_MCC_Reloans = will_table_Only_reloans[will_table_Only_reloans['combokey']=='MCCReloans']
    only_CMX_Reloans = will_table_Only_reloans[will_table_Only_reloans['combokey']=='CMXReloans']


    mask_CFN = (only_CFN_Reloans.iloc[:, 3:] == 0)
    result_CFN = only_CFN_Reloans[mask_CFN].dropna(axis=1)
    result_CFN = result_CFN.columns.tolist()

    mask_TDC = (only_TDC_Reloans.iloc[:, 3:] == 0)
    result_TDC = only_TDC_Reloans[mask_TDC].dropna(axis=1)
    result_TDC = result_TDC.columns.tolist()

    mask_STC = (only_STC_Reloans.iloc[:, 3:] == 0)
    result_STC = only_STC_Reloans[mask_STC].dropna(axis=1)
    result_STC = result_STC.columns.tolist()

    mask_MCC = (only_MCC_Reloans.iloc[:, 3:] == 0)
    result_MCC = only_MCC_Reloans[mask_MCC].dropna(axis=1)
    result_MCC = result_MCC.columns.tolist()

    mask_CMX = (only_CMX_Reloans.iloc[:, 3:] == 0)
    result_CMX = only_CMX_Reloans[mask_CMX].dropna(axis=1)
    result_CMX = result_CMX.columns.tolist()
    
    mask_BSC = (only_BSC_Reloans.iloc[:, 3:] == 0)
    result_BSC = only_BSC_Reloans[mask_BSC].dropna(axis=1)
    result_BSC = result_BSC.columns.tolist()


    CFN_only_active_states = CFN[CFN['state'].isin(result_CFN)]
    TDC_only_active_states = TDC[TDC['state'].isin(result_TDC)]
    STC_only_active_states = STC[STC['state'].isin(result_STC)]
    MCC_only_active_states = MCC[MCC['state'].isin(result_MCC)]
    CMX_only_active_states = CMX[CMX['state'].isin(result_CMX)]
    BSC_only_active_states = BSC[BSC['state'].isin(result_BSC)]


    logging.info("Line 268")
    logging.info(today)
   

    # Creating the csv files for different portfolios
    save_path = '/home/nishant/nishant/Files_to_send_to_Clarity/'
    CFN_only_active_states.to_csv(save_path + f'CFN_account_review_{today}.csv',index = False)
    print('CFN_Active_states_customer_count:', CFN_only_active_states.shape)

    BSC_only_active_states.to_csv(save_path + f'BSC_account_review_{today}.csv',index = False)
    print('BSC_Active_states_customer_count:', BSC_only_active_states.shape)

    TDC_only_active_states.to_csv(save_path + f'TDC_account_review_{today}.csv',index = False)
    print('TDC_Active_states_customer_count:', TDC_only_active_states.shape)

#     STC_only_active_states.to_csv(save_path + f'STC_account_review_{today}.csv',index = False)
#     print('STC_Active_states_customer_count:', STC_only_active_states.shape)

    # MCC_only_active_states.to_csv(save_path + f'MCC_account_review_{today}.csv',index = False)
    # print('MCC_Active_states_customer_count:', MCC_only_active_states.shape)

    # CMX_only_active_states.to_csv(f'CMX_account_review_{today}.csv',index = False)
    # print('CMX_Active_states_customer_count:', CMX_only_active_states.shape)


    # CMX_Finance = CMX[CMX['state'].isin(['CA','MS','SC'])]
    # CMX_Finance.to_csv(save_path + f'CMX_Finance_account_review_{today}.csv',index = False)
    # print('CMX_FINANCE_Active_states_customer_count:', CMX_Finance.shape)

    # CashMax = CMX[CMX['state'].isin(['DE','ID','MO','UT','WI','LA'])]
    # CashMax.to_csv(save_path + f'CMX_Cashmax_account_review_{today}.csv',index = False)
    # print('CashMax_Active_states_customer_count:', CashMax.shape)

    dataframes = [CFN_only_active_states,TDC_only_active_states,BSC_only_active_states]
    # dataframes = [CFN_only_active_states,TDC_only_active_states,STC_only_active_states,MCC_only_active_states,CMX_only_active_states,BSC_only_active_states]
    # dataframes = [CFN_only_active_states,TDC_only_active_states,STC_only_active_states,MCC_only_active_states,CMX_only_active_states]

#     dataframes = [CFN_only_active_states,TDC_only_active_states,MCC_only_active_states,CMX_only_active_states]
#     Concatenate all the DataFrames in the list
    concatenated_df = pd.concat(dataframes, ignore_index=True)
    print('The total count of records sent to clarity :', concatenated_df.shape)

#        secs = 45
# #     time.sleep(secs)
#     from send_to_clarity_subprocess import put
   
#     logging.info("This is CFN at line 306")
#     put(local_file = save_path + f'CFN_account_review_{today}.csv' , portfolio_dir= '/accountreview/CraneLending/')
#     logging.info("This is CFN at line 308 and it's done")
#     time.sleep(secs)
    
#     put(local_file = save_path + f'TDC_account_review_{today}.csv' , portfolio_dir= '/accountreview/LoonLending/')
#     logging.info("Finished the TDC at line 310")
#     time.sleep(secs)
    
#     put(local_file = save_path + f'STC_account_review_{today}.csv' , portfolio_dir='/accountreview/Ningodwaaswi/')
#     logging.info("Finished the STC at line 312")
#     time.sleep(secs)
    
#     put(local_file = save_path + f'MCC_account_review_{today}.csv' , portfolio_dir='/accountreview/MyCashCenter/')
#     logging.info("Finished the MCC put at line 314")
#     time.sleep(secs)
    
# #     put(local_file = save_path + f'CMX_Finance_account_review_{today}.csv' , portfolio_dir='/accountreview/CMXFinance/')    
# #     logging.info("Finished the CMX_Finance put at line 316")
# #     time.sleep(secs)
    
#     put(local_file = save_path + f'CMX_Cashmax_account_review_{today}.csv' , portfolio_dir='/accountreview/CashMax/')    
#     logging.info("Finished the CMX_CAshmax at line 318")
#     time.sleep(secs)
   
    q2 = '''CREATE TABLE IF NOT EXISTS ndl.AR_ClarityBatchData_pull_files_sent (
                inquiry_received_at TIMESTAMP,
                inquiry_tradeline_type varchar(5),
                first_name varchar(15),
                last_name var(char(15),
                middle_initial varchar(15),
                social_security_number int,
                date_of_birth varchar(15),
                street_address_1 varchar(45),
                city varchar(35),
                state varchar(10),
                zip_code int,
                bank_routing_number int,
                bank_account_number int,
                home_phone int,
                cell_phone int, 
                work_phone int,
                work_phone_extension float,
                email_address varchar(50),
                origination_ip_address varchar(20),
                net_monthly_income float,
                months_at_address int,
                months_at_current_employer int,
                pass_through_1 int,
                pass_through_2 int,
                pass_through_3 int
                )
                ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 DEFAULT COLLATE=utf8mb4_0900_ai_ci;
               '''
    # # ds.mysql_query(query = q2,
    # # user = 'nishant',
    # # password = 'fai6ieMu',
    # # mode='push',
    # # db ='db6')


    logging.info("Line 338")
    logging.info(today)
   
    # #####################
    # # Upload tables
    # #####################

    ds.mysql_upload(concatenated_df, 'nishant', 'fai6ieMu', 'ndl', 'AR_ClarityBatchData_pull_files_sent', db='db6')
    # logging.info("Clarity batch data second and so on pulls completed")
    print('Uploaded the files to the SQL table in db6')