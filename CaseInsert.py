import pandas as pd 
import numpy as np

#Daily updated NYTimes COVID-19 Data 
covid = pd.read_csv('https://github.com/nytimes/covid-19-data/blob/master/us-counties.csv?raw=true',dtype={'fips':'str'})

#Formatting of NYTimes COVID-19 Data
covid[['cases','deaths']] = covid[['cases','deaths']].fillna(0).astype(int)
covid['date'] = pd.to_datetime(covid['date'])
covid = covid[['date','fips','county','state','cases','deaths']]
covid = covid.rename(columns={'date':'DATE','fips':'FIPS','county':'COUNTY','state':'STATE','cases':'CASES','deaths':'DEATHS'})

#Creation of 2 dataframes isolating the latest days-worth of COVID-19 data by county and the day prior
covid_today = covid[covid['DATE'] == covid['DATE'].max()].reset_index(drop=True)
covid_yesterday = covid[covid['DATE'] == covid['DATE'].max()- pd.to_timedelta(1, unit='D')].reset_index(drop=True)

AGKEY = ['FIPS','STATE']

#Creation of merged dataframe for latest days-worth of data and day prior
covid_today2 = covid_today.drop(['DATE'],axis=1)
covid_yesterday2 = covid_yesterday.drop(['DATE'],axis=1).rename(columns={'CASES':'YESTER_CASES','DEATHS':'YESTER_DEATHS'})
covid_lately = pd.merge(covid_today2, covid_yesterday2, how='left', on=AGKEY, suffixes=('','_drop'))
covid_lately.drop([col for col in covid_lately.columns if 'drop' in col],axis=1,inplace=True)

#Add in columns for today and yesterday's cases as well as the veteran share by population percentage
totpop_withvet = pd.read_csv('data_folder/totpop_withvet.csv',dtype={'FIPS':'str','COUNTY':'str','STATE':'str','POP':'float','VETS':'float','VET_PERCENT':'float'})
covid_lately2 = covid_lately.drop(['DEATHS','YESTER_DEATHS'], axis=1).astype({'FIPS':'str','COUNTY':'str','STATE':'str','CASES':'int','YESTER_CASES':'int'})
VAPopCases = pd.merge(totpop_withvet,covid_lately2,on=AGKEY, how='left',suffixes=('','_drop'))
VAPopCases.drop([col for col in VAPopCases.columns if 'drop' in col],axis=1,inplace=True)
VAPopCases['VET_CASES'] = VAPopCases['CASES'] * VAPopCases['VET_PERCENT']
VAPopCases['VET_YESTER'] = VAPopCases['YESTER_CASES'] * VAPopCases['VET_PERCENT']

#Processing for breakdown of cases by age groups for Hospitalization counting
#Bring in cleaned CDC case aggregations and calculate age-group proportions
CDC = pd.read_csv('data_folder/CDC.csv',dtype={'FIPS':'str','COUNTY':'str','STATE':'str','AG1CASES':'int','AG2CASES':'int','AG3CASES':'float','AG4CASES':'float','TOTALCASES':'float','AG1AR':'float','AG2AR':'float','AG3AR':'float','AG4AR':'float'})
AGProportions = pd.read_csv('data_folder/AGProportions.csv',dtype={'FIPS':'str','COUNTY':'str','STATE':'str','Vet1Perc':'float','Vet2Perc':'float','Vet3Perc':'float','Vet4Perc':'float'})
AgeFactor = VAPopCases.drop(['POP','VETS','VET_PERCENT','YESTER_CASES','VET_CASES','VET_YESTER'], axis=1)
AgeFactor = AgeFactor.merge(CDC, on=AGKEY,how='left',suffixes=('','_drop')).drop(['AG1CASES','AG2CASES','AG3CASES','AG4CASES','TOTALCASES'],axis=1)
AgeFactor.drop([col for col in AgeFactor.columns if 'drop' in col],axis=1,inplace=True)

#"Attack Rates" or just proportional percentages of cases by age group
AgeFactor['AG1AR'].fillna(value=AgeFactor['AG1AR'].mean(), inplace=True)
AgeFactor['AG2AR'].fillna(value=AgeFactor['AG2AR'].mean(), inplace=True)
AgeFactor['AG3AR'].fillna(value=AgeFactor['AG3AR'].mean(), inplace=True)
AgeFactor['AG4AR'].fillna(value=AgeFactor['AG4AR'].mean(), inplace=True)

AGCases = AgeFactor.merge(AGProportions, on=AGKEY, how='left',suffixes=('','_drop'))
AGCases.drop([col for col in AGCases.columns if 'drop' in col],axis=1,inplace=True)

#Application of "Attack Rates" on total cases to break into age group 
AGCases['TOTALCASES1'] = AGCases['CASES']*AGCases['AG1AR']
AGCases['TOTALCASES2'] = AGCases['CASES']*AGCases['AG2AR']
AGCases['TOTALCASES3'] = AGCases['CASES']*AGCases['AG3AR']
AGCases['TOTALCASES4'] = AGCases['CASES']*AGCases['AG4AR']
AGCases = AGCases.drop(['CASES','AG1AR','AG2AR','AG3AR','AG4AR'],axis=1)

#Subdivide cases by age group into same weight of veterans per age group
AGCases['VETCASES1'] = AGCases['TOTALCASES1']*AGCases['Vet1Perc']
AGCases['VETCASES2'] = AGCases['TOTALCASES2']*AGCases['Vet2Perc']
AGCases['VETCASES3'] = AGCases['TOTALCASES3']*AGCases['Vet3Perc']
AGCases['VETCASES4'] = AGCases['TOTALCASES4']*AGCases['Vet4Perc']
AGCases = AGCases.drop(['Vet1Perc','Vet2Perc','Vet3Perc','Vet4Perc'],axis=1)

#Apply hospitalization risk percentages to each age group for cumulative estimates of hospitalization
VetHospital = AGCases.drop(['TOTALCASES1','TOTALCASES2','TOTALCASES3','TOTALCASES4'],axis=1)
VetHospital['LOWER_Hospitalizations'] = 0.006*VetHospital['VETCASES1'] + 0.0545*VetHospital['VETCASES2'] + 0.159*VetHospital['VETCASES3'] + 0.2625*VetHospital['VETCASES4']
VetHospital['UPPER_Hospitalizations'] = 0.051*VetHospital['VETCASES1'] + 0.148*VetHospital['VETCASES2'] + 0.2625*VetHospital['VETCASES3'] + 0.45*VetHospital['VETCASES4']

VetHospital = VetHospital.drop(['VETCASES1','VETCASES2','VETCASES3','VETCASES4'],axis=1)

CountyVACOVID = VAPopCases.merge(VetHospital,on=AGKEY,how='left',suffixes=('','_drop'))
CountyVACOVID.drop([col for col in CountyVACOVID.columns if 'drop' in col],axis=1,inplace=True)
TodayDate = covid['DATE'].max()
CountyVACOVID['DATE'] = ""
CountyVACOVID.loc[0,'DATE'] = '%s-%s-%s' % (TodayDate.month, TodayDate.day, TodayDate.year)
CountyVACOVID.to_csv('CountyVACOVID.csv' ,index=False)

#Final Step - Route all date to a final sheet for direct copying to placemat
VAMC = pd.read_csv('data_folder/CleanVAMC.csv',dtype={'VISN':'int','VAMC':'str','FIPS':'str','COUNTY':'str','STATE':'str'})
UScovid = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us.csv')

#Formatting of NYTimes COVID-19 Data - Country Level
UScovid[['cases','deaths']] = UScovid[['cases','deaths']].fillna(0).astype(int)
UScovid['date'] = pd.to_datetime(UScovid['date'])
UScovid = UScovid.rename(columns={'date':'DATE','cases':'CASES','deaths':'DEATHS'})

USCasesToday = UScovid.loc[ UScovid.DATE == UScovid.DATE.max(),'CASES'].values[0]
USCasesYesterday = UScovid.loc[ UScovid.DATE == UScovid.DATE.max() - pd.to_timedelta(1, unit='D'),'CASES'].values[0]
USNewCases = USCasesToday - USCasesYesterday

#State level Pulls
WA_Cases = CountyVACOVID[CountyVACOVID.STATE == 'Washington']['CASES'].sum()
OR_Cases = CountyVACOVID[CountyVACOVID.STATE == 'Oregon']['CASES'].sum()
ID_Cases = CountyVACOVID[CountyVACOVID.STATE == 'Idaho']['CASES'].sum()
OH_Cases = CountyVACOVID[CountyVACOVID.STATE == 'Ohio']['CASES'].sum()
OH_VACases = CountyVACOVID[CountyVACOVID.STATE == 'Ohio']['VET_CASES'].sum()

#VISN level Pulls
VISN20List = VAMC[VAMC.VISN == 20]['FIPS']
VISN20Data = CountyVACOVID[CountyVACOVID['FIPS'].isin(VISN20List)]

VISN20Cases = VISN20Data['CASES'].sum()
VISN20_VACases = VISN20Data['VET_CASES'].sum()

#Facility level Pulls
MGFacilityList = VAMC[VAMC.VAMC == 'Mann-Grandstaff Department of Veterans Affairs Medical Center']['FIPS']
MGFacilityData = CountyVACOVID[CountyVACOVID['FIPS'].isin(MGFacilityList)]

PSFacilityList = VAMC[VAMC.VAMC == 'Seattle VA Medical Center']['FIPS']
PSFacilityData = CountyVACOVID[CountyVACOVID['FIPS'].isin(PSFacilityList)]

#Hard-coded Columbus while VAMC list is broken/missing Columbus
ColumbusFacilityList = ['39159','39097', '39129','39049','39045','39089','39041','39117']
#ColumbusFacilityList = VAMC[VAMC.VAMC == '']['FIPS']
ColumbusFacilityData = CountyVACOVID[CountyVACOVID['FIPS'].isin(ColumbusFacilityList)]

ClevelandFacilityList = VAMC[VAMC.VAMC == 'Louis Stokes Cleveland Department of Veterans Affairs Medical Center']['FIPS']
ClevelandFacilityData = CountyVACOVID[CountyVACOVID['FIPS'].isin(ClevelandFacilityList)]

MG_ECases = MGFacilityData['VET_CASES'].sum()
MG_HospLower = MGFacilityData['LOWER_Hospitalizations'].sum()
MG_HospUpper = MGFacilityData['UPPER_Hospitalizations'].sum()

PS_ECases = PSFacilityData['VET_CASES'].sum()
PS_HospLower = PSFacilityData['LOWER_Hospitalizations'].sum()
PS_HospUpper = PSFacilityData['UPPER_Hospitalizations'].sum()

Columbus_ECases = ColumbusFacilityData['VET_CASES'].sum()
Columbus_HospLower = ColumbusFacilityData['LOWER_Hospitalizations'].sum()
Columbus_HospUpper = ColumbusFacilityData['UPPER_Hospitalizations'].sum()

Cleveland_ECases = ClevelandFacilityData['VET_CASES'].sum()
Cleveland_HospLower = ClevelandFacilityData['LOWER_Hospitalizations'].sum()
Cleveland_HospUpper = ClevelandFacilityData['UPPER_Hospitalizations'].sum()

#Establish a cyclical chart to add new rows for every date it is run
VAChart = pd.read_csv('VAChart.csv', parse_dates=['DATE'])

VAChart_newrow = pd.DataFrame({ 'DATE': TodayDate,
                           'US Cases': USCasesToday,
                           'New US Cases': USNewCases,
                           'VISN20 Cases': VISN20Cases,
                           'WA Cases': WA_Cases,
                           'OR Cases': OR_Cases,
                           'ID Cases': ID_Cases,
                           'VISN20 VACases': VISN20_VACases,
                           'OH Cases': OH_Cases,
                           'OH VACases': OH_VACases,
                           'MG ECases': MG_ECases,
                           'MG HospLower': MG_HospLower,
                           'MG HospUpper': MG_HospUpper,
                           'PS ECases': PS_ECases,
                           'PS HospLower': PS_HospLower,
                           'PS HospUpper': PS_HospUpper,
                           'Columbus ECases': Columbus_ECases,
                           'Columbus HospLower': Columbus_HospLower,
                           'Columbus HospUpper': Columbus_HospUpper,
                           'Cleveland ECases': Cleveland_ECases,
                           'Cleveland HospLower': Cleveland_HospLower,
                           'Cleveland HospUpper': Cleveland_HospUpper}, index=[0])

VAChart = pd.concat([VAChart_newrow, VAChart]).reset_index(drop=True).drop_duplicates(subset='DATE',keep='first').round(2)

VAChart.to_csv('VAChart.csv',index=False)