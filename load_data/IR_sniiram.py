# -*- coding:cp1252 -*-
"""
Created on Tue Sep 30 15:27:41 2014

@author: aeidelman
"""

import pandas as pd
import numpy as np
from CONFIG import path_sniiram
import os

def load_infos_sniiram(variables_interet = ['Nom court du m�dicament ', 'PHA_CIP_C13',
                                             'Dosage', 'Unit� du dosage', "Nombre d'unit�s par conditionnement"]):
    ''' Retourne les variables d'int�rets de dosage disponibles de la base sniiram '''

    file = os.path.join(path_sniiram, 'IR_PHA_R.csv')
    table = pd.read_csv(file , sep=';')

    # On renomme les colonnes dont on a les descriptifs (nouvelles versions)
    file_desc = os.path.join(path_sniiram, 'Referentiel PHARMACIE.csv')
    nom_variable = pd.read_csv(file_desc, sep=';')
    nom_variable.set_index('Donn�es', drop=True, inplace=True)
    table.rename(columns=nom_variable['Libell�'].to_dict(), inplace=True)
#     # 7 variables pr�sentes dans l�ancienne version du r�f�rentiel,
#     # c'est-�-dire avant sous ORAREF, ne sont plus restitu�es dans la nouvelle version
#     variables_old = ['PHA_ATC_CLA', 'PHA_ATC_LIB', 'PHA_EPH_CLA', 'PHA_EPH_LIB',
#                        'PHA_SUB_DOS', 'PHA_DOS_UNI', 'PHA_UPC_NBR']

    # Pour certains produits seules les anciennes variables nous informent du dosage,
    # on va donc prendre l'union des deux sources pour avoir le  moins de NaN possible :
    # ['Dosage'] avec ['PHA_SUB_DOS'] et ['Unit� du dosage'] avec ['PHA_DOS_UNI']
    table.loc[table['Dosage'].isnull(), 'Dosage'] = table.loc[table['Dosage'].isnull(), 'PHA_SUB_DOS']
    table.loc[table['Unit� du dosage'].isnull(), 'Unit� du dosage'] = table.loc[table['Unit� du dosage'].isnull(), 'PHA_DOS_UNI']

    table_int = table[variables_interet]
    is_nan = table_int['Dosage'].isnull() | table_int['Unit� du dosage'].isnull()

    print "Sur les " + str(len(table_int)) + " m�dicaments de la base, nous avons \
    des informations de dosage sur " + str(len(table_int) - sum(is_nan)) + " d'entre eux."
    table_int.drop(is_nan.index[is_nan], inplace=True)
    # Remplacemet des virgules par des points
    table_int.loc[:, 'Dosage'] = table_int['Dosage'].str.replace(',', '.')
    table_int.loc[:, 'Dosage'] = table_int['Dosage'].str.replace('0.50', '0.5')
    table_int.loc[:, "Nombre d'unit�s par conditionnement"] = table_int["Nombre d'unit�s par conditionnement"].str.replace(',', '.')
    table_int.loc[:, "Nombre d'unit�s par conditionnement"] = table_int["Nombre d'unit�s par conditionnement"].str.replace(' DOSES', '')
    table_int.loc[:, 'Unit� du dosage'] = table_int['Unit� du dosage'].str.replace(',', '.')
    table_int.loc[:, 'Unit� du dosage'] = table_int['Unit� du dosage'].str.replace('P. 100', '%')
    table_int.loc[:, 'Unit� du dosage'] = table_int['Unit� du dosage'].str.replace('MG/24 H', 'MG/24H')
    table_int.loc[:, 'Unit� du dosage'] = table_int['Unit� du dosage'].str.replace('G/100 G', '%')
    table_int.loc[:, 'Unit� du dosage'] = table_int['Unit� du dosage'].str.replace('M.UI', 'MUI')
    table_int.loc[:, 'Unit� du dosage'] = table_int['Unit� du dosage'].str.replace('MUI/ MG', 'MUI/MG')
    table_int.loc[:, 'Unit� du dosage'] = table_int['Unit� du dosage'].str.replace('MG/1 ML', 'MG/ML')
    return table_int