# -*- coding: utf-8 -*-
"""
Created on Fri Aug 08 15:30:38 2014

@author: tvialette
"""
import pandas as pd
import re
import os
import numpy as np
from CONFIG import path_BDM

info_dispo = ['CIP', 'CIP7', 'CIP_UCD', 'NATURE', 'NOM_COURT', 'INDIC_COND',
              'DEBUT_REMB', 'FIN_REMB', 'CODE_LISTE', 'CODE_FORME', 'FORME',
              'CODE_CPLT', 'CPLT_FORME', 'DOSAGE_SA', 'UNITE_SA', 'NB_UNITES',
              'CODE_ATC', 'CLASSE_ATC', 'CODE_EPH', 'CLASSE_EPH', 'LABO',
              'NOM_LONG1', 'NOM_LONG2', 'SUIVI', 'DATE_EFFET', 'SEUIL_ALER',
              'SEUIL_REJE', 'PRESC_REST', 'EXCEPTIONS', 'TYPE', 'SEXE',
              'INTERACT', 'PIH', 'PECP']



def recode_dosage_isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
        
def recode_dosage_as_float(value):
    try:
        return float(value)
    except:
        return np.nan

def recode_dosage_sa(table):
    print('dosage ' + str(len(table)))
    #Supprimer le texte en particulier
    #table = table.loc[table['DOSAGE_SA'].apply(lambda x: x!='NON RENSEIGNE' and x!='NON RENSIGNE' and x!='NON RE' and x!='NR')]
    #Supprimer toutes les listes avec du texte
    table['DOSAGE_SA_ini'] = table['DOSAGE_SA'].copy()
    table['DOSAGE_SA'] = table['DOSAGE_SA'].str.replace(',','.')
#    table = table.loc[table['DOSAGE_SA'].apply(lambda x: recode_dosage_isfloat(str(x)))]
#    table = table.loc[table['DOSAGE_SA'].notnull(), :]
    table['DOSAGE_SA'] = table['DOSAGE_SA'].apply(recode_dosage_as_float)
    

    test_mui = table['UNITE_SA'].str.contains('MUI', na=False)
    table.loc[test_mui,'UNITE_SA'] = table.loc[test_mui,'UNITE_SA'].str.replace('MUI', 'U')
    table.loc[test_mui,'DOSAGE_SA'] = table.loc[test_mui,'DOSAGE_SA'].apply(lambda x: x*1000000)

    test_grammes = table['UNITE_SA'] == 'G'
    table.loc[test_grammes, 'UNITE_SA'] = table.loc[test_mui,'UNITE_SA'].str.replace('G', 'MG')
    table.loc[test_grammes,'DOSAGE_SA'] = table.loc[test_grammes,'DOSAGE_SA'].apply(lambda x: x*1000)
    
#    table['DOSAGE_SA'] = table['DOSAGE_SA'].str.replace('UI', 'U') # Sa place est à la fin (ici)

    return table


def recode_nb_unites(table):
    #print('nb_unites ' + str(len(table)))
    ''' recode les objets avec des slashs : 2/150 ---> 2'''
    selector = table['NB_UNITES'].notnull()
    table.loc[selector, 'NB_UNITES'] = table.loc[selector, 'NB_UNITES'].str.replace(',','.')
    table.loc[selector, 'NB_UNITES'] = table.loc[selector, 'NB_UNITES'].str.replace(' M','000000')
    table.loc[selector, 'NB_UNITES'] = table.loc[selector, 'NB_UNITES'].str.split('/').apply(lambda x: recode_nb_unites_split_func(x))
    table.loc[selector, 'NB_UNITES'] = table.loc[selector, 'NB_UNITES'].apply(lambda x: re.findall('\d*\.?\d+',str(x))[0])
    table.loc[selector, 'NB_UNITES'] = table.loc[selector, 'NB_UNITES'].astype(float)
    return table

def recode_nb_unites_split_func(x):
    assert(len(x)<=2)
    assert(len(x)>0)
    if len(x)==2:
        #Si lettre G est après le slash, on multiplie par la valeur avant le 'G'
        if len(re.findall('G', x[1])):
            val = re.findall('\d*\.?\d+',str(x[1]))[0]
            return (float(x[0])*float(val))
        else:
            return (x[0])
    else:
        return (x[0])

def recode_labo(table):
    print('labo ' + str(len(table)))
    table['LABO'] = table['LABO'].str.replace('-','')
    table['LABO'] = table['LABO'].str.replace(' ','')  # On veut vraiment faire ça ?
    return table

#def recode_unites(table):
#    table = table[~table['UNITE_SA'].isnull()]
#    #On met les miligrammes en grammes
#    table.loc[table['UNITE_SA'].str.contains('MG'),'DOSAGE_SA']*=1000

#def recode_microgrammes_en_mg

def get_dose(obj):
    ''' permet d'extraire le nombre d'unités des cellules où il y a un slash,
    exemple : pour [1/10 ML] renvoie [1] '''
    obj = str(obj)
    if '/' in obj:
        idx = obj.index('/')
        value = obj[:idx]
    else:
        value = obj
    try:
        return float(value)
    except ValueError:
        return None


def bdm_cnamts(info_utiles, unites_par_boite=True):
    ''' charge les info_utiles et crée la variable unites_par_boite '''
    path = os.path.join(path_BDM, "BDM_CIP.xlsx")
    table_entiere = pd.read_excel(path, 0)
    table = table_entiere.loc[:, info_utiles]
    if 'DOSAGE_SA' in info_utiles:
        table = recode_dosage_sa(table)
    if 'NB_UNITES' in info_utiles:
        table = recode_nb_unites(table)
    if 'LABO' in info_utiles:
        table = recode_labo(table)
    if unites_par_boite:
        table['unites_par_boite_cnamts'] = table_entiere['NB_UNITES'].str.replace(',', '.')
        table['unites_par_boite_cnamts'] = table['unites_par_boite_cnamts'].apply(get_dose)
    if 'CODE_ATC' in info_utiles:
        table['CODE_ATC_4'] = table['CODE_ATC'].str[:5]
    if 'CIP' in info_utiles:
        table['CIP'] = table['CIP'].astype(str)
    return table




if __name__ == '__main__':
    info_utiles_from_cnamts = ['CIP', 'CIP7', 'CODE_ATC', 'FORME', 'NB_UNITES', 'DOSAGE_SA', 'UNITE_SA','LABO']
    info_utiles_from_cnamts = info_dispo

    test = bdm_cnamts(info_utiles_from_cnamts)
    
    deux_subst = test.NOM_LONG1.str.contains('MG/') & test.NOM_LONG1.str.contains(', ')
    deux_subst = (1 - test.NOM_LONG1.str.contains('24 H')) & (deux_subst)
    deux_subst = (1 - test.NOM_LONG1.str.contains('16 H')) & (deux_subst)

    deux_subst = (1 - test.NOM_LONG1.str.contains(' ML ')) & (deux_subst)
    
    prob = test[deux_subst]
    # 781 cas sur 1327
    HYDROCHLOROTHIAZIDE = prob.NOM_LONG1.str.contains('HYDROCHLOROTHIAZIDE')
    hydroturc = prob[HYDROCHLOROTHIAZIDE]
    #  HYDROCHLOROTHIAZIDE en deuxième position
    deuxieme = hydroturc[hydroturc.NOM_LONG1.str.contains('/HYDROCHLOROTHIAZIDE') | \
                         hydroturc.NOM_LONG1.str.contains(', HYDROCHLOROTHIAZIDE') | \
                         hydroturc.NOM_LONG1.str.contains('IL HYDROCHLOROTHIAZIDE') |
                         hydroturc.NOM_LONG1.str.contains('-HYDROCHLOROTHIAZIDE')] 
    #  HYDROCHLOROTHIAZIDE en deuxième position
    premiere = hydroturc[~hydroturc.CIP.isin(deuxieme.CIP)] # en ait premier aussi.
    # => tous les HYDROCHLOROTHIAZIDE sont en deuxième position
    
    autre = prob[~HYDROCHLOROTHIAZIDE]

    
