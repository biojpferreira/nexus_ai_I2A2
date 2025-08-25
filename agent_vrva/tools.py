import pandas as pd
from langchain.tools import tool
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
import sys
from sqlalchemy import create_engine, select,desc, func
from sqlalchemy.orm import Session
from typing import Type, ClassVar

from migrations import *


def _calcular_vr_com_dataframe(row):
    # A lógica que o pandas irá aplicar por linha
    vr = 0
    dias_a_pagar = row['dias_uteis']

    if row['tipo_evento'] == "Trabalhando":
        vr = dias_a_pagar * row['valor']
    elif row['tipo_evento'] == "Férias":
        # Assumindo que você tem a coluna 'observacao' no seu df
        if dias_a_pagar - float(row['observacao']) >= 1:
            vr = (dias_a_pagar - float(row['observacao'])) * row['valor']
    elif row['tipo_evento'] == "Desligamento":
        # Assumindo que você tem a coluna 'data_evento' no seu df
        if row['data_evento'].day > 15:
            vr = dias_a_pagar * row['valor']
    
    return vr

def _calcular_vr_logica_interna(id_funcionario, session):
    query_completa = (
        select(Funcionario, Evento, Sindicato, DiasUteis, SindicatoValorBase)
        .join(Evento)
        .join(Sindicato)
        .join(DiasUteis)
        .join(SindicatoValorBase)
        .where(Funcionario.matricula == id_funcionario)
        .order_by(desc(Evento.id))
    )
    resultado = session.execute(query_completa).first()

    if resultado:
        funcionario, evento, sindicato, dias_uteis, valor_base = resultado
        vr = float(0)
        dias_a_pagar = dias_uteis.dias_uteis
        
        # 4. A lógica de cálculo
        if evento.tipo_evento == "Trabalhando":
            vr = dias_a_pagar * valor_base.valor

        elif evento.tipo_evento == "Férias":
            dias_a_pagar = dias_a_pagar - float(evento.observacao)
            
            if dias_a_pagar >= 1:
                vr = dias_a_pagar * valor_base.valor


        #Se o funcionario foi desligado antes do dia 15 nao pagar
        elif evento.tipo_evento == "Desligamento":
            if evento.data_evento.day > 15:
                vr = dias_uteis.dias_uteis * valor_base.valor
                
        # Retorna um dicionário, que é muito mais fácil de ser manipulado pelo pandas
        return {
            'vr_calculado': vr,
            'dias_a_pagar': dias_a_pagar
        }
    else:
        # Retorna um dicionário com valores padrão para facilitar o processamento
        return {
            'vr_calculado': 0,
            'dias_a_pagar': 0
        }

class VRVAAutomationTools:
    @tool
    def calcular_vr(id_funcionario):
        """Ferramenta para calcular VR de um funcionário."""
        engine = create_engine("sqlite:///meu_banco.db")
        with Session(engine) as session:
            return _calcular_vr_logica_interna(id_funcionario, session)
        
# Define o Pydantic Model para os argumentos da ferramenta
class ProcessarTudoInput(BaseModel):
    """Input para a ferramenta de processamento de todos os funcionários."""
    caminho_saida: str = Field(description="O caminho completo onde o arquivo de saída será salvo.")
    mes_referencia: Optional[str] = Field(
        None,
        description="O mês de referência para o cálculo, no formato 'MM-AAAA' (ex: '05-2025'). Se não fornecido, o mês atual será usado."
    )

# Define a nova ferramenta
class ProcessarTodosFuncionariosTool(BaseTool):
    """
    Ferramenta para buscar todos os funcionários no banco de dados,
    calcular o VR para cada um e gerar uma nova planilha com os resultados.
    """
    name: str  = "processar_todos_funcionarios"
    description: str = "Útil para calcular o VR de todos os funcionários presentes no banco de dados e salvar o resultado em um novo arquivo XLSX. Recebe apenas o caminho do arquivo de saída."
    args_schema: Type[BaseModel] = ProcessarTudoInput
    
    def _run(self, caminho_saida: str, mes_referencia: Optional[str] = None) -> str:
        try:
            vrva_tools_instance = VRVAAutomationTools()
            engine = create_engine("sqlite:///meu_banco.db")
            
            with Session(engine) as session:
                # Subquery para encontrar a data do primeiro e último evento por funcionário
                subquery_eventos_extremos = (
                    select(
                        Evento.funcionario_id,
                        func.min(Evento.data_evento).label('primeiro_evento'),
                        func.max(Evento.data_evento).label('ultimo_evento')
                    )
                    .group_by(Evento.funcionario_id)
                    .subquery()
                )

                # Query principal que junta tudo em uma única chamada
                query_final = (
                    select(
                        Funcionario.matricula,
                        Evento.data_evento,
                        Evento.tipo_evento,
                        Evento.observacao,
                        Sindicato.nome,
                        DiasUteis.dias_uteis,
                        SindicatoValorBase.valor,
                        subquery_eventos_extremos.c.primeiro_evento,
                        subquery_eventos_extremos.c.ultimo_evento
                    )
                    .join(Evento)
                    .join(Sindicato)
                    .join(DiasUteis)
                    .join(SindicatoValorBase)
                    .join(subquery_eventos_extremos, Evento.funcionario_id == subquery_eventos_extremos.c.funcionario_id)
                    .order_by(desc(Evento.id))
                )
                
                # Executa a query e cria o DataFrame em uma única linha, como deve ser
                df_final = pd.DataFrame(session.execute(query_final).all(), columns=session.execute(query_final).keys())
                df_final = df_final.drop_duplicates(subset="matricula", keep='first')

            df_final['VR_Calculado'] = df_final.apply(
                _calcular_vr_com_dataframe, axis=1
            )

            df_final['Custo empresa'] = df_final['VR_Calculado']*0.8
            df_final['Desconto profissional'] = df_final['VR_Calculado']*0.2
            df_final['OBS'] = ""
            df_final['Competencia'] = mes_referencia

            # As renomeações de colunas e remoção devem ser feitas APÓS o cálculo
            df_final.drop(columns=['tipo_evento', 'data_evento', 'observacao','ultimo_evento'], inplace=True)
            
            ordem=['matricula','primeiro_evento','nome','Competencia',
                   'dias_uteis','valor','VR_Calculado','Custo empresa',
                   'Desconto profissional','OBS']
            df_final = df_final[ordem]
            df_final.rename(columns={
                'matricula': 'Matricula', 
                'nome': "Sindicato do Colaborador",
                'dias_uteis': "Dias", 
                'valor': "VALOR DIÁRIO VR",
                'primeiro_evento':'Admissao',
                "VR_Calculado":"TOTAL"
            }, inplace=True)


            # Salva o DataFrame final em um novo arquivo XLSX
            df_final.to_excel(caminho_saida, index=False)
            
            return f"Processamento concluído para todos os funcionários. O arquivo final está em: {caminho_saida}"
            
        except Exception as e:
            return f"Ocorreu um erro: {e}"
