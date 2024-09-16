def AR_second_pull():
    import pandas as pd
    import numpy as np
  
    import LendemDS as ds
  
    
    import logging
    import sys
    import os
    import gc
    import time
    import subprocess
    from datetime import datetime

    from joblib import load

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
    ## query for every succesful payment (option1)
    q1 = f'''
    SELECT a.customerid, a.portfolio, a.loanid, a.ls_status, a.pmtnumber, a.cust_pmtnumber, 
    a.payment_status, a.origdt as origination_date,
    a.aged_pmt, a.scheduleddate, a.loanseriesdt as loan_series_date, a.loan_cycle_start_date, 
    a.customer_cycle_start_date,
    a.loanseries_cycle_start_date,
    a.fpd, a.start_date, a.loantype
    FROM rmg.payment_cycle_summary a
    inner join core.loan_performance_info b 
    on a.portfolio = b.portfolio and
    a.loanid = b.loanid and b.status like '%Active%'
    WHERE
    a.ls_status not like '%Delinquent%' 
    AND a.ls_status not like '%Not Aged%' 
    AND a.ls_status not like '%PIF%' 
    AND a.payment_status IN ('Good Payment','Forgiven Payment',
    'Paid Off - Transfered - With Payment', 'Discounted Payment')
    order by a.portfolio, a.customerid, a.loanid, a.cust_pmtnumber desc;
    '''

    logging.info("Line 54")
    logging.info(datetime.today())
   
    # ######################
    # ######################
    # Executing the query

    df = ds.mysql_query(query = q1,
    user = 'nishant',
    password = 'fai6ieMu',
    mode='pull',
    db ='db6')


    ####################
    #Deduping df
    df = df[['customerid', 'portfolio', 'loanid', 'loan_series_date','loantype']].drop_duplicates(keep='first')

    # ###################
    # ###################
    df["loan_series_date"] = pd.to_datetime(df["loan_series_date"])

    df["loan_series_age"] = (pd.Timestamp.now() - df["loan_series_date"]).dt.days

    logging.info("Line 76")
    logging.info(datetime.today())
   
    # #####################
    # # Query for reloan
    # #####################

    reloan_origination = f'''SELECT 
    customerid, portfolio, loanid, ls_status, pmtnumber,cust_pmtnumber, payment_status,origdt as origination_date,
    aged_pmt, scheduleddate,loanseriesdt as loan_series_date, loan_cycle_start_date,customer_cycle_start_date,
    loanseries_cycle_start_date, fpd,start_date,loantype
    FROM rmg.payment_cycle_summary
    WHERE loantype="Reloan"
    AND origdt BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 DAY) AND CURDATE();
     '''
    # ###############
    # ###############
    # # Executing the query

    df1 = ds.mysql_query(query = reloan_origination,
    user = 'nishant',
    password = 'fai6ieMu',
    mode='pull',
    db ='db6')


    df1['origination_date'] = pd.to_datetime(df1['origination_date'])
    df1['loan_series_age'] = (pd.Timestamp.now() - df1['origination_date']).dt.days
    df_new = df1[['customerid','portfolio','loanid','loan_series_age','loantype']].drop_duplicates()
    df_new = df_new.reset_index(drop=True)


    ##################
    ##45 days cadence
    ##################
    df_temp = df[(df["loan_series_age"] >= 45) & (df["loan_series_age"] % 45 >= 0) & (df["loan_series_age"] % 45 <= 1)]

    #################
    ##Consecutive payments
    #################
    
    logging.info("Line 117")
    logging.info(datetime.today())
   
    
    # This function calculates the number of consecutive payments
    query1 = '''

            SELECT
            `portfolio`,`loanid`,`customerid`,`loanseriesid`,`pmtnumber`,`scheduledamount`,`start_date`,`scheduleddate`,`principalpaid`,
            `origdt`,`cust_origdt`,`loanseriesdt`,`loantype`,`principal`,`fundedamt`, payment_status, ls_status, totalcashin
            FROM
            rmg.payment_cycle_summary
            WHERE
            origdt >= '2022-10-30'
            AND aged_pmt = 1
            AND dummy_record_flag = 0

            '''

    pmt_df = ds.mysql_query(query = query1,
    user = 'nishant',
    password = 'fai6ieMu',
    mode='pull',
    db ='db6')

    pmt_df['scheduleddate'] = pd.to_datetime(pmt_df['scheduleddate'])
    pmt_df['start_date'] = pd.to_datetime(pmt_df['start_date'])
    pmt_df['origdt'] = pd.to_datetime(pmt_df['origdt'])
    pmt_df['cust_origdt'] = pd.to_datetime(pmt_df['cust_origdt'])
    pmt_df['loanseriesdt'] = pd.to_datetime(pmt_df['loanseriesdt'])

    pmt_df['scheduleddate'] = pmt_df['scheduleddate'] + timedelta(days=-4)
    pmt_df['start_date'] = pmt_df['start_date'] + timedelta(days=-4)

    pmt_df['pmtind'] = np.where(pmt_df['payment_status']=='Good Payment', 1, 0)
    pmt_df['nopmtind'] = np.where(pmt_df['payment_status']=='Good Payment', 0, 1)

    pmt_df['consecgrps'] = pmt_df.groupby(['portfolio','loanid'])['nopmtind'].cumsum()

    pmt_df.shape
    pmt_df['pmtind'] = np.where(pmt_df['payment_status']=='Good Payment', 1, 0)
    pmt_df['nopmtind'] = np.where(pmt_df['payment_status']=='Good Payment', 0, 1)

    pmt_df['consecgrps'] = pmt_df.groupby(['portfolio','loanid'],group_keys=True)['nopmtind'].cumsum()

    pmt_df.shape

    def calculate_consecutive_payments(group):
        group['consecutive_payments'] = group.groupby(['consecgrps'], group_keys=True)['pmtind'].cumsum()#.cumcount()
        return group

    # Apply the function to each group
    pmt_df = pmt_df.sort_values(['portfolio', 'loanid', 'pmtnumber']).groupby(['portfolio', 'loanid'], group_keys=True).apply(calculate_consecutive_payments)

    # Define a custom function to get the last but one value within each group
    def get_last_but_one(group):
        if len(group) >= 2:
            return group.iloc[-2]
        else:
            return None

    query = '''

            SELECT dt AS scheduleddate, cureDate AS cure_date
            FROM calendar.calendar_table
            WHERE dt >= '2022-10-30'

            '''

    cured_df = ds.mysql_query(query=query, user = 'nishant',
    password = 'fai6ieMu',
    mode='pull',
    db ='db6')
    cured_df['scheduleddate'] = pd.to_datetime(cured_df['scheduleddate'])
    cured_df['cure_date'] = pd.to_datetime(cured_df['cure_date'])
    cured_df.shape    

    pmt_df = pd.merge(pmt_df, cured_df, on='scheduleddate', how='left')
    pmt_df.shape    

    pmt_df['cure_date'] = pd.to_datetime(pmt_df['cure_date'], format='%Y-%m-%d')
    
#     from datetime import datetime, timedelta
#     today = pd.Timestamp.today().date()
#     yesterday = today - pd.DateOffset(days=1)
#     ten_days_ago = today - datetime.timedelta(days=10)
#     ten_days_ago_str = ten_days_ago.strftime('%Y-%m-%d')
    from datetime import datetime, timedelta

    # Get the current date
    today = datetime.today().date()
    yesterday = today - pd.DateOffset(days=1)
    # Calculate date range for the past 10 days
    ten_days_ago = today - timedelta(days=10)

    # Format dates as strings in 'YYYY-MM-DD' format
    today_str = today.strftime('%Y-%m-%d')
    ten_days_ago_str = ten_days_ago.strftime('%Y-%m-%d')

#     five_plus_pmts = pmt_df[(pmt_df['cure_date'] > ten_days_ago_str) & (pmt_df['consecutive_payments'] >= 5)]


    # five_to_ten_pmts = pmt_df[(pmt_df['cure_date'].dt.date.isin([today, yesterday]))
    #        & (pmt_df['consecutive_payments'] >= 5) 
    #        & (pmt_df['consecutive_payments'] < 10)]

    five_plus_pmts = pmt_df[(pmt_df['cure_date'].dt.date.isin([today, yesterday]))
           & (pmt_df['consecutive_payments'] >= 5)]
    
#     five_plus_pmts = pmt_df[(pmt_df['cure_date']>ten_days_ago_str)
#            & (pmt_df['consecutive_payments'] >= 5)]
    
    # Concatenating all the dataframes
    final_df = pd.concat([df_new, df_temp, five_plus_pmts])

    # Dropping the duplicates from the final dataframe
    final_df_drop_dups = final_df.drop_duplicates(subset=['customerid','portfolio'], keep='first')

    # print(final_df_drop_dups.shape)
    # final_df_drop_dups.head()

    # Adding in the date_of_batch_run column
    final_df_drop_dups['date_of_batch_run'] = pd.Timestamp.now()
    
    # Creating PortLOan column to check for Dupes in final_df_drop_dups
    
    final_df_drop_dups['portLoan'] = final_df_drop_dups['portfolio'] + final_df_drop_dups['loanid'].astype(str)

    # pulling in infinity data
    infinity = f'''Select * from spy.Infinity_ACH_Returns_Refresh'''
    infinity_data = ds.mysql_query(query = infinity,
    user = 'nishant',
    password = 'fai6ieMu',
    mode='pull',
    db ='db6')

    # renaming loan id
    infinity_data = infinity_data.rename(columns = {'loan #':'loanid'})
    
    
    # Creating PortLoan column in check_Infinity to check for columns present in final_df_drop_dups and drop the dupes
    infinity_data['portLoan'] = infinity_data['portfolio'] + infinity_data['loanid'].astype(str)

    # Checking infinity data to see for customers who defaulted
    check_infinity = final_df_drop_dups[~final_df_drop_dups['portLoan'].isin(infinity_data['portLoan'])].copy()
    
    # Final dataframe to upload to sql
    df_final = check_infinity
    
    # Final dataframe to upload to sql
    
    
    df_final = df_final[['customerid','portfolio','loanid','loan_series_age','loantype','date_of_batch_run']]
    df_final['date_of_batch_run'] = pd.to_datetime(df_final['date_of_batch_run']).dt.date

    logging.info("Line 245")
    logging.info(datetime.today())
   

    ##################
    # Uploading to mysql, creating a sql table
    ###################

    q2 = '''CREATE TABLE IF NOT EXISTS ndl.AR_ClarityBatchData_pull2 (
                customerid int,
                portfolio varchar(15),
                loanid int,
                loan_series_age int,
                loantype varchar(50),
                date_of_batch_run TIMESTAMP
                )
                ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 DEFAULT COLLATE=utf8mb4_0900_ai_ci;
               '''
    # # # # ds.mysql_query(query = q2,
    # # # # user = 'nishant',
    # # # # password = 'fai6ieMu',
    # # # # mode='push',
    # # # # db ='db6')

    # # ####################
    # # ## ADD in condition for reloan : for repeating customers include the latest(origination_date's loan_id)
    # # ####################

    # #####################
    # # Upload tables
    # #####################

    ds.mysql_upload(df_final, 'nishant', 'fai6ieMu', 'ndl', 'AR_ClarityBatchData_pull2', db='db6')
    logging.info("Clarity batch data second and so on pulls completed")






















   # # This will be the fourth file to kick off the script. 
   # /home/shyam/miniconda3/bin/python3 /home/shyam/CRON_jobs/LeadNet_BUPDT/v3/DEV/Production/driver.py  
   # > /home/shyam/CRON_jobs/LeadNet_BUPDT/v3/DEV/logs/cronjob1.log 2>&1

   # .sh extension
