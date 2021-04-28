import pandas as pd 
import numpy as np
import requests

def stateNames(stateAbbreviation):
    states = {
            'AK': 'Alaska',
            'AL': 'Alabama',
            'AR': 'Arkansas',
            'AS': 'American Samoa',
            'AZ': 'Arizona',
            'CA': 'California',
            'CO': 'Colorado',
            'CT': 'Connecticut',
            'DC': 'District of Columbia',
            'DE': 'Delaware',
            'FL': 'Florida',
            'GA': 'Georgia',
            'GU': 'Guam',
            'HI': 'Hawaii',
            'IA': 'Iowa',
            'ID': 'Idaho',
            'IL': 'Illinois',
            'IN': 'Indiana',
            'KS': 'Kansas',
            'KY': 'Kentucky',
            'LA': 'Louisiana',
            'MA': 'Massachusetts',
            'MD': 'Maryland',
            'ME': 'Maine',
            'MI': 'Michigan',
            'MN': 'Minnesota',
            'MO': 'Missouri',
            'MP': 'Northern Mariana Islands',
            'MS': 'Mississippi',
            'MT': 'Montana',
            'NA': 'National',
            'NC': 'North Carolina',
            'ND': 'North Dakota',
            'NE': 'Nebraska',
            'NH': 'New Hampshire',
            'NJ': 'New Jersey',
            'NM': 'New Mexico',
            'NV': 'Nevada',
            'NY': 'New York',
            'OH': 'Ohio',
            'OK': 'Oklahoma',
            'OR': 'Oregon',
            'PA': 'Pennsylvania',
            'PR': 'Puerto Rico',
            'RI': 'Rhode Island',
            'SC': 'South Carolina',
            'SD': 'South Dakota',
            'TN': 'Tennessee',
            'TX': 'Texas',
            'UT': 'Utah',
            'VA': 'Virginia',
            'VI': 'Virgin Islands',
            'VT': 'Vermont',
            'WA': 'Washington',
            'WI': 'Wisconsin',
            'WV': 'West Virginia',
            'WY': 'Wyoming'
    }
    if stateAbbreviation is not None:
        if stateAbbreviation in states:
            return states[stateAbbreviation]
        else:
            return None
    else:
        return None

#Veteran Population Projection Estimates by County (Estimates span several decades; 2021 is selected out below)
veterans = pd.read_csv('data_folder/VetPop2018_County_Data__9L.csv',dtype={'FIPS':'str'})

veterans['Date'] = pd.to_datetime(veterans['Date'])
veterans2021 = veterans[veterans['Date'] == '2021-09-30'].reset_index(drop=True)
veterans2021['County'] = veterans2021['County, St'].str.split(',').str[0]
#Remove unneeded columns as well as Gender and then sum to remove Gender split of data
veterans2021 = veterans2021.drop(['County, St', 'Date', 'Gender'],axis=1)
veterans2021 = (veterans2021.groupby(['FIPS','Age Group','County'], sort=False, as_index=False)
                    .agg({'Veterans':'sum', 'State':'first'})
                    .reindex(columns=veterans2021.columns)) 
#Remove non-CONUS areas, reorder columns, and change column names for consistency
veterans2021.drop(veterans2021[veterans2021['State'] == 'Island Areas & Foreign'].index, inplace=True)
veterans2021.drop(veterans2021[veterans2021['State'] == 'Puerto Rico'].index, inplace=True)
veterans2021.loc[(veterans2021.FIPS == '11001'),'State'] = 'District of Columbia'
veterans2021 = veterans2021[['FIPS','County','State','Age Group','Veterans']]
veterans2021 = veterans2021.rename(columns={'County':'COUNTY','Age Group':'AGEGROUP','State':'STATE','Veterans':'VETS'})


#Create a dataframe without age column to get total counts of veterans by county
POPveterans2021 = veterans2021.drop(['AGEGROUP'],axis=1)
POPveterans2021 = (POPveterans2021.groupby(['FIPS','COUNTY'], sort=False, as_index=False)
                    .agg({'VETS':'sum', 'STATE':'first'})
                    .reindex(columns=POPveterans2021.columns))

API_KEY = 'eed39902208fc176e948f1dc4c8ecd60a81fd8d1'
AGEPOP_API_URL = 'https://api.census.gov/data/2019/pep/charagegroups?get=NAME,POP,AGEGROUP&for=county:*&in=state:*&key={}'.format(API_KEY)
POP_API_URL = 'https://api.census.gov/data/2019/pep/charagegroups?get=NAME,POP&for=county:*&in=state:*&key={}'.format(API_KEY)

#API Call for Census data by age groups 
results = requests.get(AGEPOP_API_URL).json()
agepop = pd.DataFrame(results[1:], columns=results[0])

#Cleaning of Population by Age Group data
agepop['FIPS'] = agepop.state + agepop.county
agepop = agepop.astype(dtype={'NAME': 'str', 'POP':'float','AGEGROUP':'int64','state':'str','county':'str'})
agepop = agepop.sort_values(by=['NAME','AGEGROUP'])
agepop[['COUNTY','STATE']] = agepop['NAME'].str.split(', ', expand=True)
agepop['COUNTY'] = agepop['COUNTY'].str.replace(' County', '')
agepop['COUNTY'] = agepop['COUNTY'].str.replace(' Parish', '')
agepop = agepop[['FIPS','COUNTY','STATE','AGEGROUP','POP']].reset_index(drop=True)
agepop.drop(agepop[agepop['STATE'].str.contains('Puerto Rico')].index, inplace=True)
agepop = agepop.sort_values(by=['FIPS','AGEGROUP']).reset_index(drop=True)

AG1 = agepop[agepop['AGEGROUP'] == 30].rename(columns={'POP':'TOTPOP1'}).drop(['AGEGROUP'], axis=1).reset_index(drop=True)
AG2 = agepop[agepop['AGEGROUP'] == 25].rename(columns={'POP':'TOTPOP2'}).drop(['AGEGROUP'], axis=1).reset_index(drop=True)

AG3 = agepop[agepop['AGEGROUP'].isin([14,15,16,17])].rename(columns={'POP':'TOTPOP3'}).drop(['AGEGROUP'], axis=1).reset_index(drop=True)
AG3 = (AG3.groupby(['FIPS','COUNTY','STATE'], sort=False, as_index=False).agg({'TOTPOP3':'sum'}))

AG4 = agepop[agepop['AGEGROUP'] == 18].rename(columns={'POP':'TOTPOP4'}).drop(['AGEGROUP'], axis=1).reset_index(drop=True)

AGKEY = ['FIPS','STATE']

AG = AG1.merge(AG2,on=AGKEY,how='left',suffixes=('','_drop')).merge(AG3,on=AGKEY,how='left',suffixes=('','_drop')).merge(AG4,on=AGKEY,how='left',suffixes=('','_drop'))
AG.drop([col for col in AG.columns if 'drop' in col],axis=1,inplace=True)

AGVet1 = veterans2021[veterans2021['AGEGROUP'] == '17-44'].rename(columns={'VETS':'VETPOP1'}).drop(['AGEGROUP'],axis=1).reset_index(drop=True)
AGVet2 = veterans2021[veterans2021['AGEGROUP'] == '45-64'].rename(columns={'VETS':'VETPOP2'}).drop(['AGEGROUP'],axis=1).reset_index(drop=True)
AGVet3 = veterans2021[veterans2021['AGEGROUP'] == '65-84'].rename(columns={'VETS':'VETPOP3'}).drop(['AGEGROUP'],axis=1).reset_index(drop=True)
AGVet4 = veterans2021[veterans2021['AGEGROUP'] == '85+'].rename(columns={'VETS':'VETPOP4'}).drop(['AGEGROUP'],axis=1).reset_index(drop=True)

AGVet = AGVet1.merge(AGVet2,on=AGKEY,how='left',suffixes=('','_drop')).merge(AGVet3,on=AGKEY,how='left',suffixes=('','_drop')).merge(AGVet4,on=AGKEY,how='left',suffixes=('','_drop'))
AGVet.drop([col for col in AGVet.columns if 'drop' in col],axis=1,inplace=True)

AGProportions = AG.merge(AGVet,on=AGKEY,how='left',suffixes=('','_drop'))
AGProportions.drop([col for col in AGProportions.columns if 'drop' in col],axis=1,inplace=True)

AGProportions['Vet1Perc'] = AGProportions['VETPOP1']/AGProportions['TOTPOP1']
AGProportions['Vet2Perc'] = AGProportions['VETPOP2']/AGProportions['TOTPOP2']
AGProportions['Vet3Perc'] = AGProportions['VETPOP3']/AGProportions['TOTPOP3']
AGProportions['Vet4Perc'] = AGProportions['VETPOP4']/AGProportions['TOTPOP4']
AGProportions = AGProportions[['FIPS','COUNTY','STATE','Vet1Perc','Vet2Perc','Vet3Perc','Vet4Perc']]

AGProportions.to_csv('data_folder/AGProportions.csv',index=False)

#API Call for total population counts not split by age groups
results2 = requests.get(POP_API_URL).json()
pop = pd.DataFrame(results2[1:], columns=results2[0])

#Cleaning of total population counts
pop['FIPS'] = pop.state + pop.county
pop = pop.astype(dtype={'NAME': 'str', 'POP':'float','state':'str','county':'str'})
pop[['COUNTY','STATE']] = pop['NAME'].str.split(', ', expand=True)
pop['COUNTY'] = pop['COUNTY'].str.replace(' County', '')
pop['COUNTY'] = pop['COUNTY'].str.replace(' Parish', '')
pop = pop[['FIPS','COUNTY','STATE','POP']].reset_index(drop=True)
pop.drop(pop[pop['STATE'].str.contains('Puerto Rico')].index, inplace=True)
pop = pop.sort_values(by='FIPS')

#Start central frame with Vet count and Veteran Percentage of Total Population
totpop_withvet = pd.merge(pop,POPveterans2021, on=AGKEY, how='left',suffixes=('','_drop'))
totpop_withvet.drop([col for col in totpop_withvet.columns if 'drop' in col],axis=1,inplace=True)
totpop_withvet['VET_PERCENT'] = totpop_withvet['VETS']/totpop_withvet['POP']
totpop_withvet.to_csv('data_folder/totpop_withvet.csv',index=False)

#CDC Megadata File
CDCcovid = pd.read_csv('data_folder/CDCcovid.csv', dtype={'FIPS':'str','COUNTY':'str','STATE':'str','AGEGROUP':'str','CASES':'int'})

#Processing the CDC data to obtain columns for cases by county by age group and total cases by county
Cases1 = CDCcovid[CDCcovid['AGEGROUP'] == '18 to 49 years'].rename(columns={'CASES':'AG1CASES'}).drop(['AGEGROUP'],axis=1).reset_index(drop=True)
Cases2 = CDCcovid[CDCcovid['AGEGROUP'] == '50 to 64 years'].rename(columns={'CASES':'AG2CASES'}).drop(['AGEGROUP'],axis=1).reset_index(drop=True)
Cases3 = CDCcovid[CDCcovid['AGEGROUP'] == '65+ years'].rename(columns={'CASES':'AG3CASES'}).drop(['AGEGROUP'],axis=1).reset_index(drop=True)

Cases3 = Cases3.merge(AG3,on=AGKEY,how='left',suffixes=('','_drop')).merge(AG4,on=AGKEY,how='left',suffixes=('','_drop'))
Cases3.drop([col for col in Cases3.columns if 'drop' in col],axis=1,inplace=True)
Cases3['AG3CASES'] = Cases3['AG3CASES'] * (Cases3['TOTPOP3'] / (Cases3['TOTPOP3'] +Cases3['TOTPOP4']))
Cases3 = Cases3.drop(['TOTPOP3','TOTPOP4'], axis=1)

Cases4 = CDCcovid[CDCcovid['AGEGROUP'] == '65+ years'].rename(columns={'CASES':'AG4CASES'}).drop(['AGEGROUP'],axis=1).reset_index(drop=True)

Cases4 = Cases4.merge(AG3,on=AGKEY,how='left',suffixes=('','_drop')).merge(AG4,on=AGKEY,how='left',suffixes=('','_drop'))
Cases4.drop([col for col in Cases4.columns if 'drop' in col],axis=1,inplace=True)
Cases4['AG4CASES'] = Cases4['AG4CASES'] * (Cases4['TOTPOP4'] / (Cases4['TOTPOP3'] +Cases4['TOTPOP4']))
Cases4 = Cases4.drop(['TOTPOP3','TOTPOP4'], axis=1)

CDC = Cases1.merge(Cases2,on=AGKEY,how='left',suffixes=('','_drop')).merge(Cases3,on=AGKEY,how='left',suffixes=('','_drop')).merge(Cases4,on=AGKEY,how='left',suffixes=('','_drop'))
CDC.drop([col for col in CDC.columns if 'drop' in col],axis=1,inplace=True)

CDC['TOTALCASES'] = CDC['AG1CASES']+CDC['AG2CASES']+CDC['AG3CASES']+CDC['AG4CASES']

#Processing of these values to create county-level age-group percentage of cases
CDC['AG1AR'] = CDC['AG1CASES']/CDC['TOTALCASES']
CDC['AG2AR'] = CDC['AG2CASES']/CDC['TOTALCASES']
CDC['AG3AR'] = CDC['AG3CASES']/CDC['TOTALCASES']
CDC['AG4AR'] = CDC['AG4CASES']/CDC['TOTALCASES']

CDC.to_csv('data_folder/CDC.csv',index=False)

VAMC = pd.read_csv('data_folder/VAMC.csv', usecols=['NAME','STATE','STATEFP','COUNTYFP','CountyName','VISN'], converters={'STATEFP': '{:0>2}'.format,'COUNTYFP': '{:0>3}'.format}) \
    .dropna(subset=['VISN']) \
    .astype(dtype={'NAME': 'str', 'VISN':'int','STATEFP':'str','COUNTYFP':'str'}) 
    
VAMC['STATE'] = VAMC.apply(lambda x: stateNames(x['STATE']), axis=1)
VAMC['FIPS'] = VAMC.STATEFP + VAMC.COUNTYFP
VAMC = VAMC[['VISN','NAME','FIPS','CountyName','STATE']].rename(columns={'CountyName':'COUNTY','NAME':'VAMC'}).sort_values(by=['VISN','VAMC'])
VAMC.to_csv('data_folder/CleanVAMC.csv',index=False)