import pandas as pd
pd.set_option('future.no_silent_downcasting', True)
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from tabulate import tabulate
from datetime import datetime
import sys
sys.path.insert(1, '/home/jferreira/devcry/nexusai/agent_vrva/')


from migrations import *

    
engine = create_engine("sqlite:///meu_banco.db")
Base.metadata.create_all(engine)

def read_file(file_path, sheetName=0,skiprows=0):
        try:
            df = pd.read_excel(file_path, sheet_name=sheetName,skiprows=skiprows)
            df.columns = [col.strip() for col in df.columns]
            if "MATRICULA" in df.columns:
                df.rename(columns={"MATRICULA":"matricula"}, inplace=True)
                
            return df
        except FileNotFoundError:
            print("Arquivo não encontrado. Cheque o caminho. Ou o universo está contra você.")
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
  
def merge_df(df1,df2,method,key):
    return pd.merge(df1,df2, on=key, how=method)
 
df_quadro_funcionarios = pd.DataFrame(columns=["matricula",'situacao','sindicato','cargo','obs','data_contratacao','data_desligamento','valor_devido'])

df_ativos = read_file(os.path.abspath("./data/ATIVOS.xlsx"))
df_ativos.rename(columns={"DESC. SITUACAO":"situacao","Sindicato":"sindicato","TITULO DO CARGO":"cargo"}, inplace=True)

df_admissao = read_file(os.path.abspath("./data/ADMISSÃO ABRIL.xlsx"))
df_admissao.rename(columns={"Unnamed: 3":"obs","MATRICULA":"matricula"}, inplace=True)

df_demissao = read_file(os.path.abspath("./data/DESLIGADOS.xlsx"))
df_estagio = read_file(os.path.abspath("./data/ESTÁGIO.xlsx"))
df_aprendiz = read_file(os.path.abspath("./data/APRENDIZ.xlsx"))
df_afastados = read_file(os.path.abspath("./data/AFASTAMENTOS.xlsx"))
df_afastados.rename(columns={"Unnamed: 3":"OBS"}, inplace=True)

df_exterior = read_file(os.path.abspath("./data/EXTERIOR.xlsx"))
df_exterior.rename(columns={"Cadastro":"matricula","Unnamed: 2":"OBS"}, inplace=True)

df_ferias = read_file(os.path.abspath("./data/FÉRIAS.xlsx"))

#MERGE SECTION
df_quadro_funcionarios = pd.concat([df_quadro_funcionarios, df_ativos[["matricula",'situacao','sindicato','cargo']]], ignore_index=True)
df_quadro_funcionarios.astype(str)

#Adicona a data de contrataçao caso necessário
df_quadro_funcionarios = pd.merge(
    df_quadro_funcionarios, 
    df_admissao, 
    on="matricula", 
    how='left', 
    suffixes=('_existente', '_admissao')
)
df_quadro_funcionarios['obs'] = df_quadro_funcionarios['obs_existente'].fillna(df_quadro_funcionarios['obs_admissao']).infer_objects(copy=False)
df_quadro_funcionarios.drop(columns=['obs_existente', 'obs_admissao','Admissão','Cargo'], inplace=True)


#Adiciona demissao
df_quadro_funcionarios = pd.merge(
    df_quadro_funcionarios,
    df_demissao,
    on="matricula",
    how='left',
    suffixes=['_existente','_demitidos']
)
df_quadro_funcionarios['data_desligamento'] = df_quadro_funcionarios['data_desligamento'].fillna(df_quadro_funcionarios['DATA DEMISSÃO']).infer_objects(copy=False)
df_quadro_funcionarios.drop(columns=['DATA DEMISSÃO', 'COMUNICADO DE DESLIGAMENTO'], inplace=True)


#Adiciona os estagiarios
df_quadro_funcionarios = merge_df(df1=df_quadro_funcionarios, df2=df_estagio, key="matricula",method="outer")
df_quadro_funcionarios['cargo'] = df_quadro_funcionarios['cargo'].fillna(df_quadro_funcionarios['TITULO DO CARGO']).infer_objects(copy=False)
df_quadro_funcionarios.drop(columns=['TITULO DO CARGO', 'na compra?'], inplace=True)


#Adiciona os apredizes
df_quadro_funcionarios = merge_df(df1=df_quadro_funcionarios, df2=df_aprendiz, key="matricula",method="outer")
df_quadro_funcionarios['cargo'] = df_quadro_funcionarios['cargo'].fillna(df_quadro_funcionarios['TITULO DO CARGO']).infer_objects(copy=False)
df_quadro_funcionarios.drop(columns=['TITULO DO CARGO'], inplace=True)

#Adicona afastados
df_quadro_funcionarios = merge_df(df1=df_quadro_funcionarios, df2=df_afastados, key="matricula",method="outer")
df_quadro_funcionarios['situacao'] = df_quadro_funcionarios['situacao'].fillna(df_quadro_funcionarios['DESC. SITUACAO']).infer_objects(copy=False)
df_quadro_funcionarios['obs'] = df_quadro_funcionarios['obs'].fillna(df_quadro_funcionarios['OBS']).infer_objects(copy=False)
df_quadro_funcionarios.drop(columns=['OBS','DESC. SITUACAO','na compra?'], inplace=True)

#adiciona funcionarios exterior
df_quadro_funcionarios = merge_df(df1=df_quadro_funcionarios, df2=df_exterior, key="matricula",method="outer")
df_quadro_funcionarios['obs'] = df_quadro_funcionarios['obs'].fillna(df_quadro_funcionarios['OBS']).infer_objects(copy=False)
df_quadro_funcionarios['valor_devido'] = df_quadro_funcionarios['valor_devido'].fillna(df_quadro_funcionarios['Valor']).infer_objects(copy=False)
df_quadro_funcionarios.drop(columns=['OBS','Valor'], inplace=True)


#adiciona ferias
df_quadro_funcionarios = merge_df(df1=df_quadro_funcionarios, df2=df_ferias, key="matricula",method="outer")
df_quadro_funcionarios['situacao'] = df_quadro_funcionarios['situacao'].fillna(df_quadro_funcionarios['DESC. SITUACAO']).infer_objects(copy=False)
df_quadro_funcionarios['obs'] = df_quadro_funcionarios['obs'].fillna(df_quadro_funcionarios['DIAS DE FÉRIAS']).infer_objects(copy=False)
df_quadro_funcionarios.drop(columns=['DESC. SITUACAO','DIAS DE FÉRIAS'], inplace=True)


#correcoes para insercao
df_quadro_funcionarios['valor_devido'] = df_quadro_funcionarios['valor_devido'].fillna(0)
df_quadro_funcionarios['sindicato'] = df_quadro_funcionarios['sindicato'].fillna("nao_filiado")
df_quadro_funcionarios['situacao'] = df_quadro_funcionarios['situacao'].fillna("Trabalhando")
df_quadro_funcionarios['cargo'] = df_quadro_funcionarios['cargo'].fillna("nao_definido")
df_quadro_funcionarios['data_contratacao'] = df_quadro_funcionarios['data_contratacao'].fillna(pd.to_datetime('1900-01-01'))


with Session(engine) as session:
    all_cols=['matricula', 'situacao', 'sindicato', 'cargo', 'data_contratacao',
       'data_desligamento', 'valor_devido', 'obs']
    for idx,row in df_quadro_funcionarios.iterrows():
        sindicato_objeto = session.query(Sindicato).filter_by(nome=row['sindicato']).first()
        funcionario_objeto = session.query(Funcionario).filter_by(matricula=row['matricula']).first()
        if sindicato_objeto and not funcionario_objeto:
            novo_funcionario = Funcionario(
            matricula=row['matricula'],
            cargo=row['cargo'],
            sindicato_id=sindicato_objeto.id)
            
            session.add(novo_funcionario)
            session.commit()
            
            novo_evento = Evento(funcionario_id=novo_funcionario.id,
                                 tipo_evento="contratacao",
                                 data_evento=datetime.strptime("2020-01-01","%Y-%M-%d")
                                 )
            
            session.add(novo_evento)
            session.commit()
            
            #Adicionando novos eventos
            novo_evento = Evento(funcionario_id=novo_funcionario.id,
                                 tipo_evento=row['situacao'],
                                 data_evento=datetime.strptime("2020-01-02","%Y-%M-%d"),
                                 observacao=row['obs']
                                 )
            
            session.add(novo_evento)
            session.commit()
            
        else:
            funcionario_objeto = session.query(Funcionario).filter_by(matricula=row['matricula']).first()
            if row['data_desligamento'].day >= 1:
                novo_evento = Evento(funcionario_id=funcionario_objeto.id,
                                    tipo_evento="Desligamento",
                                    data_evento=row['data_desligamento'],
                                    observacao=row['obs']
                                    )
                session.add(novo_evento)
                session.commit()
    