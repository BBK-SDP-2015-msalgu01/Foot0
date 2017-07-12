# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 17:11:23 2017
+++++++++++++++++++++++++++++++++++
Botador de dados
+++++++++++++++++++++++++++++++++++
Descricao dos dados aqui:
    
    http://www.football-data.co.uk/notes.txt

@author: msalgueiro
"""
#%% imp

import glob
import pandas as pd
import re
import os
import urllib.request as urllib
#%% const

_PATH     =  r'c:/temp/fute/'

_FILE_LINK = 'http://www.football-data.co.uk/mmz4281/XXXX/P1.csv'
_ORG_COLS  = ['Div','Date','HomeTeam','AwayTeam','FTHG','FTAG',
              'FTR','HTAG','HTHG','HTR']
_YYYS      = ['9495','9596','9697','9798','9899','9900','0001','0102','0203',
              '0304','0405','0506','0708','0809','0910','1011','1112','1213',
              '1314','1415','1516','1617']
_URLLOGIC  = {'BASE':_FILE_LINK,'PATTERN':_YYYS}

#%% fxn

def loadFootieData(folderloc, fpats=False):
    ''
    if fpats==False:
        pass
    else:
        directory = os.path.dirname(folderloc)
        try:
            os.stat(directory)
        except: 
            os.mkdir(directory)
        
        pattern = fpats['PATTERN']
        base    = fpats['BASE']
        for y in pattern:
            url = re.sub('XXXX', y, base)
            response = urllib.urlopen(url)
            csv = response.read()
            with open(folderloc+'/'+y+'.csv', 'wb') as f:
                f.write(csv)
                
    filenames = glob.glob(folderloc + "/*.csv")
    dfs = pd.DataFrame()
    for filename in filenames:
        dfs = dfs.append(pd.read_csv(filename, error_bad_lines=False, sep=','
             ,header=0).dropna(axis=1,how='all').dropna(axis=0,how='all'))
    dfs['Date'] = pd.to_datetime(dfs['Date'], dayfirst=True)
    ord_columns = _ORG_COLS+[x for x in list(dfs.columns) if x not in _ORG_COLS]
    return dfs[ord_columns].sort_values(by='Date',ascending=True).reset_index(drop=True)

#%% main

def _main_():    
    #Agora, da para fazer varias merdas:
    out = pd.DataFrame()
    df            = loadFootieData(_PATH, _URLLOGIC)
    df            = df.set_index('Date')
    df['Matches'] = df['HomeTeam'].str.replace(' ','_')+'_'+df['AwayTeam'].str.replace(' ','_')
    
    #Tipo todos os jogos:
    matches       = df['Matches'].unique()

    for _year in sorted(list(set(df.index.year))):
        df_year    = df.copy()[df.index.year==_year]        
        df_season1 = df_year.copy()[df_year.index.month<8]
        df_season2 = df_year.copy()[df_year.index.month>=8]
        
        df_season1['Season'] = str(_year-1)[-2:]+'/'+str(_year+0)[-2:]
        df_season2['Season'] = str(_year+0)[-2:]+'/'+str(_year+1)[-2:]
        
        out = out.append(df_season1).append(df_season2)
    
    #Ou os golos por equipa por epoca:
    slbH = out[out['HomeTeam']=='Benfica'].groupby(by='Season').sum()[['FTHG','FTAG']]
    fcpH = out[out['HomeTeam']=='Porto'].groupby(by='Season').sum()[['FTHG','FTAG']]
    scpH = out[out['HomeTeam']=='Sp Lisbon'].groupby(by='Season').sum()[['FTHG','FTAG']]
    
    slbA = out[out['AwayTeam']=='Benfica'].groupby(by='Season').sum()[['FTHG','FTAG']]
    fcpA = out[out['AwayTeam']=='Porto'].groupby(by='Season').sum()[['FTHG','FTAG']]
    scpA = out[out['AwayTeam']=='Sp Lisbon'].groupby(by='Season').sum()[['FTHG','FTAG']]

if __name__ == "__main__":
    _main_()        
    
