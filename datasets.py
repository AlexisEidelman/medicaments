# -*- coding:cp1252 -*-
'''
Created on 28 sept. 2014

@author: alexis
'''

import os
import re
import numpy as np
from pandas import read_csv

from CONFIG import working_path

import load_data.medic_gouv as mg
import load_data.bdm_cnamts as cnamts
from load_data.bdm_cnamts_prix import load_cnamts_prix_harmonise
from load_data.sniiram import load_sniiram

maj_gouv = 'maj_20140915122241'


def create_dataset_brut(from_gouv, maj_gouv, from_cnamts):
    # Chargement des données médicaments.gouv et cnamts
    print 'Loading medic.gouv'
    gouv = mg.load_medic_gouv(maj_gouv, var_to_keep=from_gouv, CIP_not_null=True)
    print 'Loading cnamts'
    cnam = cnamts.bdm_cnamts(from_cnamts)
    print 'Loading Sniiram extract'
    # Chargement de la base Sniiram
    sniiram = load_sniiram()
    # Chargement des prix dynamiques
    prix_dynamiques = load_cnamts_prix_harmonise()
    # On merge les bases
    base_brute = gouv.merge(cnam, left_on = 'CIP13', right_on='CIP', how='outer')
    base_brute = base_brute.merge(sniiram, left_on='CIP13', right_index=True, how='outer')
    base_brute = base_brute.merge(prix_dynamiques, left_on = 'CIP13', right_on='CIP', how='outer')
    # On remplace les nan des periodes par 0
    # J'ai enlev� la ligne ci dessous car je ne vois pas l'int�r�t de conserver les lignes si on ne connait pas le dosage
    #base_brute.fillna(0, inplace=True)
    return base_brute


def create_dataset_plus(from_gouv, maj_gouv, from_cnamts, force=False):
    table = dataset_brut(from_gouv, maj_gouv, from_cnamts, force)
    # code ATC de niveau 4
    table['CODE_ATC'].fillna('inconnu', inplace=True)
    table['CODE_ATC_4'] = table['CODE_ATC'].apply(lambda x: x[:5])
    # dosage_par_prestation_cnamts
    table['dosage_par_prestation_cnamts'] = table['DOSAGE_SA']*table['NB_UNITES']
    # dosage_par_prestation de medic.gouv
    table.loc[table['Dosage'] == 'qs', 'Dosage'] = 0  # Cas particulier
    # TODO: voir si �a marche
    table['Dosage_num'] = table['Dosage'].str.findall('\d*\.?\d+').str.get(0)
    table['Dosage_num'] = table['Dosage_num'].astype(float)
    table['dosage_par_prestation_medic_gouv'] = table['Dosage_num']*table['nb_ref_in_label_medic_gouv']
    table['dosage_par_prestation_medic_gouv'].replace(0, np.nan, inplace=True)
    return table

def dataset_brut(from_gouv, maj_gouv, from_cnamts, force=False):
    file = os.path.join(working_path, 'dataset_brut.csv')
    try:
        assert not force

        # TODO: check we have dataset_brut.csv was generated with maj_gouv
        table = read_csv(file, sep=',')
        for var in from_gouv + from_cnamts:
            if var != 'CIP':
                assert var in table.columns
        # On rend les colonnes compatibles avec 'period'
        table.columns = ['CIP'] + ['prix_' + x for x in table.columns[1:]]
        return table
    except:
        table = create_dataset_brut(from_gouv, maj_gouv, from_cnamts)
        table.to_csv(file, sep=',')
        return table

def dataset_plus(from_gouv, maj_gouv, from_cnamts, force=False):
    file = os.path.join(working_path, 'dataset_plus.csv')
    try:
        assert not force
        # TODO: check we have dataset_brut.csv was generated with maj_gouv
        table = read_csv(file, sep=',')
        for var in from_gouv + from_cnamts:
            assert var in table.columns
        # On rend les colonnes compatibles avec 'period'
        table.columns = ['CIP'] + ['prix_' + x for x in table.columns[1:]]
        return table
    except:
        table = create_dataset_plus(from_gouv, maj_gouv, from_cnamts)
        import pdb
        pdb.set_trace()
        table.to_csv(file, sep=',')
        return table


if __name__ == '__main__':
    info_utiles_from_gouv = ['CIP7', 'CIP13', 'Nom', 'Id_Groupe', 'Prix', 'Titulaires', 'Num_Europe',
                         'Code_Substance', 'Nom_Substance', 'Libelle_ASMR', 'Type',
                         'Date_declar_commerc', 'Date_AMM', 'Taux_rembours',
                         'indic_droit_rembours', 'Statu_admin_presta',
                         'Ref_Dosage', 'Dosage', 'Label_presta','Valeur_ASMR',
                         'nb_ref_in_label_medic_gouv', 'Prescription',
                         'premiere_vente', 'derniere_vente']
    info_utiles_from_cnamts = ['CIP', 'CODE_ATC', 'LABO', 'DOSAGE_SA', 'UNITE_SA', 'NB_UNITES'] #LABO
    test = dataset_plus(info_utiles_from_gouv, maj_gouv, info_utiles_from_cnamts)