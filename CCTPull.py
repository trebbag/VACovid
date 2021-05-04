import pandas as pd 
import numpy as np

def CCTPull(CountyVACOVID):
    VAMC = pd.read_csv('data_folder/CleanVAMC.csv',dtype={'VISN':'int','VAMC':'str','FIPS':'str','COUNTY':'str','STATE':'str'})
    UScovid = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us.csv')

    #Formatting of NYTimes COVID-19 Data - Country Level
    UScovid[['cases','deaths']] = UScovid[['cases','deaths']].fillna(0).astype(int)
    UScovid['date'] = pd.to_datetime(UScovid['date'])
    UScovid = UScovid.rename(columns={'date':'DATE','cases':'CASES','deaths':'DEATHS'})

    USCasesToday = UScovid.loc[ UScovid.DATE == UScovid.DATE.max(),'CASES'].values[0]
    USCasesYesterday = UScovid.loc[ UScovid.DATE == UScovid.DATE.max() - pd.to_timedelta(1, unit='D'),'CASES'].values[0]
    USNewCases = USCasesToday - USCasesYesterday
    TodayDate = CountyVACOVID['DATE'][0]
    #State level Pulls
    OH_Cases = CountyVACOVID[CountyVACOVID.STATE == 'Ohio']['CASES'].sum()
    IN_Cases = CountyVACOVID[CountyVACOVID.STATE == 'Indiana']['CASES'].sum()
    MI_Cases = CountyVACOVID[CountyVACOVID.STATE == 'Michigan']['CASES'].sum()
    IL_Cases = CountyVACOVID[CountyVACOVID.STATE == 'Illinois']['CASES'].sum()
    WI_Cases = CountyVACOVID[CountyVACOVID.STATE == 'Wisconsin']['CASES'].sum()

    WA_Cases = CountyVACOVID[CountyVACOVID.STATE == 'Washington']['CASES'].sum()
    ID_Cases = CountyVACOVID[CountyVACOVID.STATE == 'Idaho']['CASES'].sum()
    OR_Cases = CountyVACOVID[CountyVACOVID.STATE == 'Oregon']['CASES'].sum()
    AK_Cases = CountyVACOVID[CountyVACOVID.STATE == 'Alaska']['CASES'].sum()


    OH_VACases = CountyVACOVID[CountyVACOVID.STATE == 'Ohio']['VET_CASES'].sum()
    IN_VACases = CountyVACOVID[CountyVACOVID.STATE == 'Indiana']['VET_CASES'].sum()
    MI_VACases = CountyVACOVID[CountyVACOVID.STATE == 'Michigan']['VET_CASES'].sum()
    IL_VACases = CountyVACOVID[CountyVACOVID.STATE == 'Illinois']['VET_CASES'].sum()
    WI_VACases = CountyVACOVID[CountyVACOVID.STATE == 'Wisconsin']['VET_CASES'].sum()

    WA_VACases = CountyVACOVID[CountyVACOVID.STATE == 'Washington']['VET_CASES'].sum()
    ID_VACases = CountyVACOVID[CountyVACOVID.STATE == 'Idaho']['VET_CASES'].sum()
    OR_VACases = CountyVACOVID[CountyVACOVID.STATE == 'Oregon']['VET_CASES'].sum()
    AK_VACases = CountyVACOVID[CountyVACOVID.STATE == 'Alaska']['VET_CASES'].sum()

    #VISN 10 level Pulls
    VISN10List = VAMC[VAMC.VISN == 10]['FIPS']
    VISN10Data = CountyVACOVID[CountyVACOVID['FIPS'].isin(VISN10List)]

    VISN10Cases = VISN10Data['CASES'].sum()
    VISN10_VACases = VISN10Data['VET_CASES'].sum()

    #VISN 12 level Pulls
    VISN12List = VAMC[VAMC.VISN == 12]['FIPS']
    VISN12Data = CountyVACOVID[CountyVACOVID['FIPS'].isin(VISN12List)]

    VISN12Cases = VISN12Data['CASES'].sum()
    VISN12_VACases = VISN12Data['VET_CASES'].sum()

    #VISN 20 level Pulls
    VISN20List = VAMC[VAMC.VISN == 20]['FIPS']
    VISN20Data = CountyVACOVID[CountyVACOVID['FIPS'].isin(VISN20List)]

    VISN20Cases = VISN20Data['CASES'].sum()
    VISN20_VACases = VISN20Data['VET_CASES'].sum()

    #Facility level Pulls
    DataSet ={}
    VAMCList = [ "Anchorage VA Medical Center", 
    "Portland VA Medical Center",
    "North Las Vegas VA Medical Center",
    "Jonathan M. Wainwright Memorial VA Medical Center",
    "White City VA Medical Center",
    "Roseburg VA Medical Center",
    "Seattle VA Medical Center",
    "Mann-Grandstaff Department of Veterans Affairs Medical Center",
    "Boise VA Medical Center",
    "Jesse Brown Department of Veterans Affairs Medical Center",
    'William S. Middleton Memorial Veterans\' Hospital',
    'Clement J. Zablocki Veterans\' Administration Medical Center',
    "Oscar G. Johnson Department of Veterans Affairs Medical Facility",
    "Lieutenant Colonel Charles S. Kettles VA Medical Center",
    "Battle Creek VA Medical Center",
    "John D. Dingell Department of Veterans Affairs Medical Center"
    ]
    
    for vamc in VAMCList:
        FacilityList = VAMC[VAMC.VAMC == vamc]['FIPS']
        FacilityData = CountyVACOVID[CountyVACOVID['FIPS'].isin(FacilityList)]
    
        ECases = FacilityData['VET_CASES'].sum()
        HospLower = FacilityData['LOWER_Hospitalizations'].sum()
        HospUpper = FacilityData['UPPER_Hospitalizations'].sum()
        values = [ECases, HospLower, HospUpper]
        DataSet['%s' %vamc] = values
    
    #Establish a cyclical chart to add new rows for every date it is run
    CCTVAChart = pd.read_csv('CCTVAChart.csv')
    CCTVAChart = CCTVAChart.set_index('index').T.rename_axis('DATE').reset_index()
    CCTVAChart_newrow = pd.DataFrame({ 'DATE': TodayDate,
                            'US Cases': USCasesToday,
                            'New US Cases': USNewCases,
                            
                            'VISN10 Cases': VISN10Cases,
                            'OH Cases': OH_Cases,
                            'IN Cases': IN_Cases,
                            'MI Cases': MI_Cases,
                            'VISN12 Cases': VISN12Cases,
                            'IL Cases': IL_Cases,
                            'WI Cases': WI_Cases,
                            'MI Cases': MI_Cases,
                            'VISN20 Cases': VISN20Cases,
                            'WA Cases': WA_Cases,
                            'OR Cases': OR_Cases,
                            'ID Cases': ID_Cases,
                            'AK Cases': AK_Cases,
                            
                            'VISN10 VACases': VISN10_VACases,
                            'OH VACases': OH_VACases,
                            'IN VACases': IN_VACases,
                            'MI VACases': MI_VACases,

                            'VISN12 VACases': VISN12_VACases,
                            'IL VACases': IL_VACases,
                            'WI VACases': WI_VACases,
                            'MI VACases': MI_VACases,

                            'VISN20 VACases': VISN20_VACases,
                            'WA VACases': WA_VACases,
                            'OR VACases': OR_VACases,
                            'ID VACases': ID_VACases,
                            'AK VACases': AK_VACases,

                            #Anchorage (AN)
                            'AN ECases': DataSet["Anchorage VA Medical Center"][0],
                            'AN HospLower': DataSet["Anchorage VA Medical Center"][1],
                            'AN HospUpper': DataSet["Anchorage VA Medical Center"][2],
                            #Portland (PO)
                            'PO ECases': DataSet["Portland VA Medical Center"][0],
                            'PO HospLower': DataSet["Portland VA Medical Center"][1],
                            'PO HospUpper': DataSet["Portland VA Medical Center"][2],
                            #WCPAC (WC)
                            'WC ECases': DataSet["North Las Vegas VA Medical Center"][0],
                            'WC HospLower': DataSet["North Las Vegas VA Medical Center"][1],
                            'WC HospUpper': DataSet["North Las Vegas VA Medical Center"][2],
                            #Walla Walla (WW)
                            'WW ECases': DataSet["Jonathan M. Wainwright Memorial VA Medical Center"][0],
                            'WW HospLower': DataSet["Jonathan M. Wainwright Memorial VA Medical Center"][1],
                            'WW HospUpper': DataSet["Jonathan M. Wainwright Memorial VA Medical Center"][2],
                            #White City (WH)
                            'WH ECases': DataSet["White City VA Medical Center"][0],
                            'WH HospLower': DataSet["White City VA Medical Center"][1],
                            'WH HospUpper': DataSet["White City VA Medical Center"][2],
                            #Roseburg (RO)
                            'RO ECases': DataSet["Roseburg VA Medical Center"][0],
                            'RO HospLower': DataSet["Roseburg VA Medical Center"][1],
                            'RO HospUpper': DataSet["Roseburg VA Medical Center"][2],
                            #Puget Sound (PS)
                            'PS ECases': DataSet["Seattle VA Medical Center"][0],
                            'PS HospLower': DataSet["Seattle VA Medical Center"][1],
                            'PS HospUpper': DataSet["Seattle VA Medical Center"][2],
                            #Mann-Grandstaff (MG)
                            'MG ECases': DataSet["Mann-Grandstaff Department of Veterans Affairs Medical Center"][0],
                            'MG HospLower': DataSet["Mann-Grandstaff Department of Veterans Affairs Medical Center"][1],
                            'MG HospUpper': DataSet["Mann-Grandstaff Department of Veterans Affairs Medical Center"][2],
                            #Boise (BO)
                            'BO ECases': DataSet["Boise VA Medical Center"][0],
                            'BO HospLower': DataSet["Boise VA Medical Center"][1],
                            'BO HospUpper': DataSet["Boise VA Medical Center"][2],
                            #Jesse Brown (JE)
                            'JE ECases': DataSet["Jesse Brown Department of Veterans Affairs Medical Center"][0],
                            'JE HospLower': DataSet["Jesse Brown Department of Veterans Affairs Medical Center"][1],
                            'JE HospUpper': DataSet["Jesse Brown Department of Veterans Affairs Medical Center"][2],
                            #William S. Middleton Memorial (WM)
                            'WM ECases': DataSet['William S. Middleton Memorial Veterans\' Hospital'][0],
                            'WM HospLower': DataSet['William S. Middleton Memorial Veterans\' Hospital'][1],
                            'WM HospUpper': DataSet['William S. Middleton Memorial Veterans\' Hospital'][2],
                            #Clement J. Zablocki (CZ)
                            'CZ ECases': DataSet['Clement J. Zablocki Veterans\' Administration Medical Center'][0],
                            'CZ HospLower': DataSet['Clement J. Zablocki Veterans\' Administration Medical Center'][1],
                            'CZ HospUpper': DataSet['Clement J. Zablocki Veterans\' Administration Medical Center'][2],
                            #Oscar G. Johnson (OJ)
                            'OJ ECases': DataSet["Oscar G. Johnson Department of Veterans Affairs Medical Facility"][0],
                            'OJ HospLower': DataSet["Oscar G. Johnson Department of Veterans Affairs Medical Facility"][1],
                            'OJ HospUpper': DataSet["Oscar G. Johnson Department of Veterans Affairs Medical Facility"][2],
                            #Ann Arbor (AA)
                            'AA ECases': DataSet["Lieutenant Colonel Charles S. Kettles VA Medical Center"][0],
                            'AA HospLower': DataSet["Lieutenant Colonel Charles S. Kettles VA Medical Center"][1],
                            'AA HospUpper': DataSet["Lieutenant Colonel Charles S. Kettles VA Medical Center"][2],
                            #Saginaw (SA)
                            'SA ECases': DataSet["Battle Creek VA Medical Center"][0],
                            'SA HospLower': DataSet["Battle Creek VA Medical Center"][1],
                            'SA HospUpper': DataSet["Battle Creek VA Medical Center"][2],
                            #Detroit (DE)
                            'DE ECases': DataSet["John D. Dingell Department of Veterans Affairs Medical Center"][0],
                            'DE HospLower': DataSet["John D. Dingell Department of Veterans Affairs Medical Center"][1],
                            'DE HospUpper': DataSet["John D. Dingell Department of Veterans Affairs Medical Center"][2]}, index=[0])

    CCTVAChart = pd.concat([CCTVAChart_newrow, CCTVAChart]).reset_index(drop=True).drop_duplicates(subset='DATE',keep='first').round(2)
    CCTVAChart = CCTVAChart.set_index('DATE').T.reset_index()
    CCTVAChart.to_csv('CCTVAChart.csv',index=False)