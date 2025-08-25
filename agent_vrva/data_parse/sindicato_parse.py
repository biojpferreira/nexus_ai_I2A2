import pandas as pd
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from tabulate import tabulate
import sys
from datetime import datetime
import numpy as np

sys.path.insert(1, '/home/jferreira/devcry/nexusai/agent_vrva/')


from migrations import *
    
engine = create_engine("sqlite:///meu_banco.db")
Base.metadata.create_all(engine)


def read_file(file_path, sheetName=0,skiprows=0):
        try:
            df = pd.read_excel(file_path, sheet_name=sheetName,skiprows=skiprows)
            return df
        except FileNotFoundError:
            print("Arquivo não encontrado. Cheque o caminho. Ou o universo está contra você.")
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")

def mesclar_dados_sindicato(df_sindicato: pd.DataFrame, df_valores: pd.DataFrame,df_dias) -> pd.DataFrame:
    """
    Mescla tres DataFrames com base nas informações de sindicato e estado.
    
    Argumentos:
        df_sindicato (pd.DataFrame): DataFrame com dados de sindicato.
        df_valores (pd.DataFrame): DataFrame com dados de estados e valores.
        df_dias (pd.DataFrame): Dataframe com a contagem de dias uteis considerada pelo sindicato
        
    Retorna:
        pd.DataFrame: DataFrame final com os dados mesclados.
    """
    
    # Mapeamento de sigla para nome completo do estado. Simples e direto.
    mapeamento_siglas = {
        'SP': 'São Paulo',
        'RS': 'Rio Grande do Sul',
        "RJ": 'Rio de Janeiro',
        "PR": "Paraná"
    }
    
    # 1. Extrair a sigla do estado da coluna 'Sindicato' usando regex.
    # O 'str.extract' é cirúrgico para isso.
    df_sindicato['SIGLA_ESTADO'] = df_sindicato['Sindicato'].str.extract(rf"({"|".join(mapeamento_siglas.keys())})")

    # 2. Criar a coluna 'ESTADO' no df_sindicato com os nomes completos.
    # Usamos o 'map' para aplicar o mapeamento.
    df_sindicato['ESTADO'] = df_sindicato['SIGLA_ESTADO'].map(mapeamento_siglas)

    # 3. Limpar a coluna 'ESTADO' do df_valores para evitar falhas na união.
    # Strip é seu amigo contra espaços extras.
    df_valores['ESTADO'] = df_valores['ESTADO'].str.strip()
    
    # 4. Mesclar os DataFrames. 'how=left' para manter todas as linhas do primeiro DF.
    df_tmp = pd.merge(df_sindicato, df_valores, on='ESTADO', how='left')
    df_final = pd.merge(df_tmp, df_dias, left_on="Sindicato", right_on="SINDICATO", how='left')

    # Limpeza final: dropa a coluna de sigla que não serve mais.
    df_final.drop(columns=['SIGLA_ESTADO'], inplace=True)
    df_final.drop(columns=['SINDICATO'], inplace=True)
    return df_final

df_ativos = read_file(os.path.abspath("./data/ATIVOS.xlsx"))
df_sindicatos = df_ativos.drop_duplicates(subset=['Sindicato'])[['Sindicato']]
df_sindicatos_valores = read_file(os.path.abspath("./data/Base sindicato x valor.xlsx"))
df_sindicato_dia_util = read_file(os.path.abspath("./data/Base dias uteis.xlsx"),skiprows=1)


df_mesclado = mesclar_dados_sindicato(df_sindicatos, df_sindicatos_valores,df_sindicato_dia_util)

nova_linha = pd.Series({"Sindicato":"nao_filiado", "ESTADO":"nao_filiado", "VALOR":"35", "DIAS UTEIS ":22}).to_frame().T

df_mesclado = pd.concat([df_mesclado, nova_linha], ignore_index=True)

with Session(engine) as session:
    
    for idx,sindicato in df_mesclado.iterrows():
        sindicato_objeto = session.query(Sindicato).filter_by(nome=sindicato['Sindicato']).first()
        if not sindicato_objeto:
            novo_sindicato = Sindicato(nome=sindicato["Sindicato"],
                                estado=sindicato["ESTADO"])
            session.add(novo_sindicato)
            session.commit()
            
            
            new_dia = DiasUteis(mes=5,ano=25,dias_uteis=int(sindicato['DIAS UTEIS ']),sindicato_id=novo_sindicato.id)
            session.add(new_dia)
            session.commit()
            
            new_valor = SindicatoValorBase(sindicato_id=novo_sindicato.id,
                                        valor=sindicato['VALOR'],
                                        data_vigencia=datetime.strptime("2025","%Y"))
            session.add(new_valor)
            session.commit()
            
        
        