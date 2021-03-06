import pandas as pd, numpy as np
from datetime import timedelta
import pyodbc 

conn = pyodbc.connect("Driver={SQL Server};"
                      "Server=CVOLPACCHIO-D-5;"
                      "Database=Analytics;"
                      "Trusted_Connection=yes;", autocommit = True)
cursor = conn.cursor()
cursor.execute("""SELECT * from 
[Analytics].[dbo].[PY_SCRIPTTBL_DVM] 
where update_dt_PY_SCRIPTTBL_DVM = (select max(update_dt_PY_SCRIPTTBL_DVM) 
from [Analytics].[dbo].[PY_SCRIPTTBL_DVM])""")

data = cursor.fetchall()
records = []
for record in data:
    records.append(list(record))
columns = [i[0] for i in cursor.description]
master = pd.DataFrame(records, columns=columns)

df_strings = [i for i in list(master.columns) if 'columns_' in i]
df_fields = []
for i in range(0,len(df_strings)):
    temp_clean = list(master[df_strings[i]].unique())
    for n in temp_clean:
        if n != None:
            df_fields.append(n.split(','))
        else:
            pass
df_names = [i[1] for i in [i.split('columns_') for i in df_strings]]
df_names=sorted(df_names)
df_fields=sorted(df_fields)
for i in range(0,len(df_names)):
    globals()[str(df_names[i])] = master[df_fields[i]]

dvm_wage.dropna(thresh=round(((len(list(dvm_wage.columns))/3)*2),0),
                axis=0, 
                inplace = True)
dvm_wage.drop_duplicates(inplace = True)
dvm_wage.reset_index(inplace=True)

dvm_revenue.dropna(thresh=round(((len(list(dvm_revenue.columns))/3)*2),0),
                axis=0, 
                inplace = True)
dvm_revenue.drop_duplicates(inplace = True)
dvm_revenue.reset_index(inplace=True)

dayforce_master.dropna(thresh=round(((len(list(dayforce_master.columns))/3)*2),0),
                axis=0, 
                inplace = True)
dayforce_master.drop_duplicates(inplace = True)
dayforce_master.reset_index(inplace=True)

FiscalCalendar.dropna(thresh=round(((len(list(FiscalCalendar.columns))/3)*2),0),
                axis=0, 
                inplace = True)
FiscalCalendar.drop_duplicates(inplace = True)
FiscalCalendar.reset_index(inplace=True)

archive_contractor_pay.dropna(thresh=round(((len(list(archive_contractor_pay.columns))/3)*2),0),
                axis=0, 
                inplace = True)
archive_contractor_pay.drop_duplicates(inplace = True)
archive_contractor_pay.reset_index(inplace=True)

revenue_by_week = dvm_revenue
revenue_by_week.rename(columns={'PeriodNumber_RevenueByRS_forRevDrWageRpt_v':'Fiscal Month',
                               'WeekofYear_RevenueByRS_forRevDrWageRpt_v':'Fiscal Week',
                               'Location_ID_DEF_Location':'Location_ID',
                               'PercentAmount':'stale_PercentAmount',
                               'hardcode_wage_perc':'PercentAmount',
                               'LocationNumber_locationinfo':'LocationNumber'},inplace = True)
revenue_by_week['Department'].value_counts()

wages = dvm_wage
new_vals = []
for i in wages['Employee_Number']:
    try:
        new_vals.append(int(float(i)))
    except:
        new_vals.append(str(i))

wages['Number_']=new_vals

location_num = []
for i in range(0,len(wages)):
    location_num.append(int(wages['Location_'].iloc[i].strip()[0:3]))
wages['Loc_Num'] = location_num
wages['Period_End']=pd.to_datetime(wages['Period_End'])
wages['Period_Start']=pd.to_datetime(wages['Period_Start'])
wages['Period_End'] = wages['Period_End'] + timedelta(days=-1)
wages['split wage'] = wages['Amount']/2
wages = wages[wages['Expense_Type']=='Normal']
wages.reset_index(inplace = True,drop=True)

# grouped wage info for 1099 & contractors
contractors = archive_contractor_pay
# contractors = contractors[['Invoice Date','Request Total', 'Custom 1 - Code']]
contractors = contractors[:-2]
contractors.loc[contractors['Custom 1 - Code'] == 'A0045', 'Custom 1 - Code'] = 45
contractors['Custom 1 - Code'] = [int(float(x)) for x in contractors['Custom 1 - Code']]

dayforce = dayforce_master
dayforce = dayforce[['Number_','Last_Name','First_Name','Location_Ledger_Code']]
dayforce.loc[dayforce['Location_Ledger_Code'] == '300D', 'Location_Ledger_Code'] = 300
dayforce.loc[dayforce['Location_Ledger_Code'] == '299D', 'Location_Ledger_Code'] = 299
dayforce['Location_Ledger_Code'] = [int(float(x)) for x in dayforce['Location_Ledger_Code']]
dayforce['Last_Name'] = [str(x).lower() for x in dayforce['Last_Name']]
dayforce['First_Name'] = [str(x).lower() for x in dayforce['First_Name']]

# Merge w/ DF and anything outstanding is bucketed misc
contractors['Employee Last Name'] = [str(x).lower() for x in contractors['Employee Last Name']]
contractors['Employee First Name'] = [str(x).lower() for x in contractors['Employee First Name']]
contractors_df = contractors.merge(dayforce, how='left', left_on=['Employee Last Name',
       'Employee First Name'],
                 right_on=['Last_Name','First_Name'])
contractors_df = contractors_df[contractors_df['Number_'].notnull()]
contractors_df.rename(columns = {'department_':'Department',
                                'Location_':'Location'}, inplace = True)
misc_wages = contractors_df[contractors_df['Number_'].isnull()]

contractors_df.rename(columns = {'Request Total':'split wage',
                             'Number':'Number_',
                             'Location_Ledger_Code':'Loc_Num',
                             'Invoice Date':'Period_Start',
                                'department_':'Department',
                                'Location_':'Location'}, inplace = True)
contractors_df['Employee_Name'] = contractors_df['Employee Last Name'] + ', ' + contractors_df['Employee First Name'] 
contractors_df['Employee_Number'] = contractors_df['Number_']

contractors_df = contractors_df[[x for x in list(contractors_df.columns) if x in list(wages.columns)]]

contractors_df[[x for x in list(wages.columns) if x not in list(contractors_df.columns)]] = 0

wages.rename(columns={'department_':'Department',
                     'Location_':'Location'}, inplace = True)
first_week = wages[['Period_Start','Pay_Group_Name', 
                    'Register_History_Record_Type_Code_Name',
       'Legal_Entity', 'Employee_Name', 'Employee_Number', 'Pay_Type',
       'Expense_Type', 'Expense_Code', 'split wage', 'Pay_Date','Hours', 
        'PSID', 'Location', 'Position',
       'Department','Loc_Num','Number_']]
first_week.rename(columns={'Period_Start':'Date'},inplace=True)
second_week = wages[['Period_End','Pay_Group_Name', 
                    'Register_History_Record_Type_Code_Name',
       'Legal_Entity', 'Employee_Name', 'Employee_Number', 'Pay_Type',
       'Expense_Type', 'Expense_Code', 'split wage', 'Pay_Date','Hours', 
        'PSID', 'Location', 'Position',
       'Department','Loc_Num','Number_']]
second_week.rename(columns={'Period_End':'Date'},inplace=True)
fw_wages = first_week.append(second_week)

contractors_df.rename(columns={'Period_Start':'Date',
                              'department_':'Department',
                              'Location_':'Location'}, inplace = True)

fw_wages = fw_wages.append(contractors_df)

#fw_wages['Pay_Date']=pd.to_datetime(fw_wages['Pay_Date'])
fw_wages.drop_duplicates(inplace=True)
fw_wages['Date'] = pd.to_datetime(fw_wages['Date'])
wages_cal = fw_wages.merge(FiscalCalendar,how='left',left_on=['Date'],right_on=['RevenueDate'])
wages_cal = wages_cal[wages_cal['FiscalYear'].isnull()==False]
wages_cal['year'] = [int(str(x)[0:4]) for x in wages_cal['FiscalYear']]

wage_types = list(wages_cal['Expense_Code'].unique())
wage_types = [str(x).lower() for x in wage_types]

bonus_payment = []
for i in wage_types:
    if 'bonus' in str(i):
        bonus_payment.append(1)
    else:
        bonus_payment.append(0)

bonus_df = pd.DataFrame(wage_types)
bonus_df['isBonus'] = bonus_payment
bonus_df['Expense_Code'] = list(wages_cal['Expense_Code'].unique())

# fro twb joining purposes
wages_omitbonus=wages_cal.merge(bonus_df,
               how = 'left',
               left_on='Expense_Code',
               right_on='Expense_Code')
#
bonus_dta = wages_omitbonus[wages_omitbonus['isBonus']==1]
#

wages_omitbonus=wages_omitbonus[wages_omitbonus['isBonus']==0]
wages_omitbonus['year'] = [int(str(x)[0:4]) for x in wages_omitbonus['FiscalYear']]

"""
Bonus Omit from Aggregated wage
""";
# # weeklywagecodes will be used to bake in expense codes to dig

# weekly_wage_docs = wages_omitbonus.groupby(['WeekofYear',
#                 'PeriodNumber',
#                     'year',
#                 'Number_',
#               'Employee_Name',
#                 'Loc_Num',
#               'Location',
#             'Position',
#                 'Department',
#              ]).agg({'split wage':sum})
# weekly_wage_docs.reset_index(inplace = True)
# weekly_wage_codes = wages_omitbonus.groupby(['Number_',
#               'Employee_Name',
#                 'Loc_Num',
#               'Location',
#             'Position',
#                 'Department',
#               'Expense_Code',
#              'WeekofYear',
#             'PeriodNumber',
#                     'year']).agg({'split wage':sum})
# weekly_wage_codes.reset_index(inplace = True)
# print(len(weekly_wage_docs),len(weekly_wage_codes), sum(weekly_wage_docs['split wage']),sum(weekly_wage_codes['split wage']))#,sum(weekly_wage_codes))

# weekly_wage_docs=weekly_wage_docs[weekly_wage_docs['year']==2021]
# weekly_wage_codes=weekly_wage_codes[weekly_wage_codes['year']==2021]

# weeklywagecodes will be used to bake in expense codes to dig

weekly_wage_docs = wages_omitbonus.groupby(['WeekofYear',
                'PeriodNumber',
                    'year',
                'Number_',
              'Employee_Name',
                'Loc_Num',
              'Location',
            'Position',
                'Department',
             ]).agg({'split wage':sum})
weekly_wage_docs.reset_index(inplace = True)
weekly_wage_docs['split wage'] = [float(x) for x in weekly_wage_docs['split wage']]
weekly_wage_docs.drop_duplicates(inplace = True)

weekly_wage_codes = wages_cal.groupby(['Number_',
              'Employee_Name',
                'Loc_Num',
              'Location',
            'Position',
                'Department',
              'Expense_Code',
             'WeekofYear',
            'PeriodNumber',
                    'year']).agg({'split wage':sum})
weekly_wage_codes.reset_index(inplace = True)
weekly_wage_codes['split wage'] = [float(x) for x in weekly_wage_codes['split wage']]
weekly_wage_codes.drop_duplicates(inplace = True)
weekly_wage_docs=weekly_wage_docs[weekly_wage_docs['year']==2021]
weekly_wage_codes=weekly_wage_codes[weekly_wage_codes['year']==2021]

"""
Fix type casting for tb join!!

""";

#to avoid annoying tableau naming convention friction
weekly_wage_codes['Loc_Num'] = [int(float(x)) for x in weekly_wage_codes['Loc_Num']]
weekly_wage_codes['Number_'] = [int(float(x)) for x in weekly_wage_codes['Number_']]
weekly_wage_codes['WeekofYear'] = [int(float(x)) for x in weekly_wage_codes['WeekofYear']]

code_cols = list(weekly_wage_codes.columns)
new_cols = []
for i in range(0,len(code_cols)):
    new_cols.append('code_'+code_cols[i])
weekly_wage_codes.columns = new_cols

#Eventually write out sep tbl in SQLSERVER with itemized wage?
weekly_wage_codes.to_csv('C:/Users/CVolpacchio/Documents/wage_expense_codes.csv')
types = []
for i in revenue_by_week['Number']:
    types.append(type(i))

new_vals = []
for i in revenue_by_week['Number']:
    try:
        new_vals.append(int(float(i)))
    except:
        new_vals.append(str(i))

revenue_by_week['Number_'] = new_vals
fw_revenue = revenue_by_week.groupby(['LocationNumber',
                         'Location',
                                      'AcquisitionDate',
                                'PercentAmount',
                                      'City', 
                          'State', 
                           'Zip',       
                            'LocationType',
                         'Number_',
                         'FullName',
                              'primary',
                                      'Fiscal Week',
                          'Fiscal Month',
                          'Quarter', 
                          'Year'
                         ]).agg({'Revenue':sum})
fw_revenue.reset_index(inplace=True)

types = []
for i in fw_revenue['Number_']:
    types.append(type(i))
    
new_vals = []
for i in fw_revenue['Number_']:
    try:
        new_vals.append(int(float(i)))
    except:
        new_vals.append(str(i))

fw_revenue['Number_']=new_vals

# Worth looking into Rev Goals & Baking into future iterations
doc_dtls = revenue_by_week.groupby(['Number_',
                                    #'Annual_Revenue_Goal',
                                    'Job',
                          'Position_Description',                                      
                                      'Pay_Type_Description']).agg({'Location':'nunique'})
doc_dtls.reset_index(inplace=True)

weekly_wage_docs['WeekofYear'] = [int(x) for x in weekly_wage_docs['WeekofYear']]
wage_group = weekly_wage_docs.groupby(['Number_','WeekofYear','PeriodNumber']).agg({'split wage':sum})
wage_group.reset_index(inplace=True)

# this nmbr will be much less since is coming from a view with pre-baked filters
revenue_group = fw_revenue.groupby(['Number_','Fiscal Week','Fiscal Month']).agg({'Revenue':sum})
revenue_group.reset_index(inplace=True)
revenue_group['Fiscal Week'] = [int(float(x)) for x in revenue_group['Fiscal Week']]
revenue_group['Fiscal Month'] = [int(float(x)) for x in revenue_group['Fiscal Month']]

wage_group['WeekofYear'] = [int(float(x)) for x in wage_group['WeekofYear']]
wage_group['PeriodNumber'] = [int(float(x)) for x in wage_group['PeriodNumber']]

## Now will merge max vals from both groupings should be left outer
max_rev_wages = (revenue_group.merge(wage_group, 
                    how = 'inner', 
                    left_on=['Number_','Fiscal Week', 'Fiscal Month'],
                   right_on=['Number_', 'WeekofYear', 'PeriodNumber'], 
                    indicator=True)).groupby(['Number_',
                                              'WeekofYear',
                                              'PeriodNumber'
                                             ]).agg({'Revenue':sum,
                                              'split wage':sum})#.query('_merge=="left_only"')
max_rev_wages.reset_index(inplace = True)
max_rev_wages.rename(columns={'Revenue':'ttl_rev',
                               'split wage': 'ttl_wage'}
                       , inplace=True)

# Grabbing total revenue by Employee/FW to use for wage calc.
master = fw_revenue.merge(max_rev_wages, 
                          how='left',
                          left_on=['Number_', 
                                    'Fiscal Week'], 
                          right_on=['Number_', 
                                    'WeekofYear'],indicator=True)

master.loc[master.WeekofYear.isnull() , 'WeekofYear'] = master['Fiscal Week']
master.loc[master.PeriodNumber.isnull() , 'PeriodNumber'] = master['Fiscal Month']
master.loc[master.ttl_rev.isnull() , 'ttl_rev'] = master['Revenue']
master.loc[master.ttl_wage.isnull() , 'ttl_wage'] = 0


non_docs = []
for i in master['Number_']:
    try:
        int(float(i))
        non_docs.append(0)
    except:
        non_docs.append(1)
master['non_doc'] = non_docs

cleanmaster = master[master['non_doc']==0]

loc_wages = []
for i in range(0,len(cleanmaster)):
    perc = cleanmaster['Revenue'].iloc[i]/cleanmaster['ttl_rev'].iloc[i]
    loc_wages.append(perc*float(cleanmaster['ttl_wage'].iloc[i]))
cleanmaster['location_wage'] = loc_wages

# simply for doc mix
doc_dtls = revenue_by_week.groupby(['Number_', 
                                    'Job',
                          'Position_Description',
                        'Pay_Type_Description']).agg({'LocationNumber':'nunique'})
doc_dtls.reset_index(inplace=True)

master1 = cleanmaster.merge(doc_dtls, left_on=['Number_'],
             right_on=['Number_'],how='left')

master1.rename(columns={'Revenue_x':'Revenue'}, inplace=True)

master1.loc[master1.Pay_Type_Description == 'Contractor', 'primary'] = -1
misc_rev_group = master[master['non_doc']==1].groupby(['LocationNumber',
                    'Location',
                    'LocationType',
                    'AcquisitionDate',
                    'City',
                    'State',
                    'Zip',
                   'Fiscal Week',
                   'Fiscal Month',
                   'Quarter',
                   'Year']).agg({'Revenue':sum})
misc_rev_group.reset_index(inplace=True)
misc_rev_group.drop_duplicates(inplace=True)
misc_rev_group['LocationNumber'] = [int(float(x)) for x in misc_rev_group['LocationNumber']]

# master_misc = misc_rev_group.merge(misc_wage_master, 
#            how = 'left',
#           left_on=['LocationNumber',
#                   'Fiscal Week'],
#           right_on=['Custom 1 - Code', 
#                     'WeekofYear'])
# len(master_misc)# = master_misc[master_misc['WeekofYear_y'].notnull()]

# len(master_misc[master_misc['WeekofYear'].notnull()])

# master_misc['location_wage'] = master_misc['Request Total']
# master_misc.drop_duplicates(inplace=True)
# # print(master_misc['Number_'].value_counts())
# # print(master_misc['FullName'].value_counts())

# master_misc[master_misc['Request Total'].isnull()]

# master_misc.loc[master_misc['Request Total'].isnull(), 'location_wage'] = 0
# master_misc.loc[master_misc['Custom 1 - Code'].isnull(), 'Custom 1 - Code'] = master_misc['LocationNumber']
# master_misc.loc[master_misc['WeekofYear'].isnull(), 'WeekofYear'] = master_misc['Fiscal Week']
# master_misc.loc[master_misc['PeriodNumber'].isnull(), 'PeriodNumber'] = master_misc['Fiscal Month']
#master_misc.columns

# [x for x in list(master_misc.columns) if x not in (master1.columns)]

# [x for x in list(master1.columns) if x not in (master_misc.columns)]

#master_misc['location_wage'] = master_misc['Request Total']
master_misc.drop_duplicates(inplace=True)
master_misc.rename(columns={'Year_x':'Year',
 'Custom 1 - Code':'LocationNumber_x',
'LocationNumber':'LocationNumber_y'},
           inplace=True)
master_misc['primary'] =-2
master_misc['FullName']='misc'
master_misc[['PercentAmount',
 'Number_',
 'ttl_rev',
 'ttl_wage',
 '_merge',
 'Job',
 'Position_Description',
 'Pay_Type_Description']] = 0

master_misc['non_doc'] = 1
master_misc = master_misc[list(master1.columns)]

master1 = master1.append(master_misc)
master1.loc[master1.LocationType == 'Other', 'LocationType'] = 'Specialty'
master1.dropna(inplace=True)
master1['LocationNumber_x'] = [int(float(x)) for x in master1['LocationNumber_x']]

loomis = master1[master1.Number_ == 90058]
master1 = master1[master1.Number_ != 90058]

# Hard-coded anomolies
loomis['adjusted_wage'] = loomis['location_wage']*.6
loomis.rename(columns = {'location_wage':'drop',
                        'adjusted_wage':'location_wage'},
                         inplace=True)
loomis.drop('drop', axis = 1, inplace = True)
master1 = master1.append(loomis)

"""
this is where we write out to new tbl in sql server
""";
from sqlalchemy import create_engine
import urllib

quoted = urllib.parse.quote_plus("DRIVER={SQL Server};SERVER=CVOLPACCHIO-D-5;DATABASE=Analytics")
engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted))

master1.to_sql('ReportTable_DVMProd', schema='dbo', 
               con = engine, 
               chunksize=int(2100/len(list(master1.columns))), 
               method='multi', 
               index=False, if_exists='replace')

