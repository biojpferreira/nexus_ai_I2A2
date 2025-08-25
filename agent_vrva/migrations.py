from typing import Optional
from datetime import datetime, date
from sqlalchemy import String, ForeignKey, UniqueConstraint, create_engine
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from typing import Optional



class Base(DeclarativeBase):
    pass

class Sindicato(Base):
    __tablename__ = 'sindicatos'
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(200), unique=True)
    estado: Mapped[str] = mapped_column(String(2))
    
    funcionarios: Mapped[list["Funcionario"]] = relationship(back_populates="sindicato")
    valores_base: Mapped[list["SindicatoValorBase"]] = relationship(back_populates="sindicato")
    dias_uteis: Mapped[list["DiasUteis"]] = relationship(back_populates="sindicato")

class SindicatoValorBase(Base):
    __tablename__ = 'sindicatos_valores_base'
    id: Mapped[int] = mapped_column(primary_key=True)
    sindicato_id: Mapped[int] = mapped_column(ForeignKey("sindicatos.id"))
    valor: Mapped[float] = mapped_column()  
    data_vigencia: Mapped[date] = mapped_column()
    
    sindicato: Mapped["Sindicato"] = relationship(back_populates="valores_base")
    __table_args__ = (UniqueConstraint('sindicato_id', 'data_vigencia', name='_sindicato_data_uc'),)


class Funcionario(Base):
    __tablename__ = 'funcionarios'
    id: Mapped[int] = mapped_column(primary_key=True)
    sindicato_id: Mapped[int] = mapped_column(ForeignKey("sindicatos.id"))
    matricula: Mapped[str] = mapped_column(String(20), unique=True)
    cargo: Mapped[str] = mapped_column(String(50))
    
    sindicato: Mapped["Sindicato"] = relationship(back_populates="funcionarios")
    pagamentos: Mapped[list["Pagamento"]] = relationship(back_populates="funcionario")
    eventos: Mapped[list["Evento"]] = relationship(back_populates="funcionario")

class Pagamento(Base):
    __tablename__ = 'pagamentos'
    id: Mapped[int] = mapped_column(primary_key=True)
    funcionario_id: Mapped[int] = mapped_column(ForeignKey("funcionarios.id"))
    valor: Mapped[float] = mapped_column() 
    tipo: Mapped[str] = mapped_column(String(50))
    data_pagamento: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    funcionario: Mapped["Funcionario"] = relationship(back_populates="pagamentos")
    eventos: Mapped[list["Evento"]] = relationship(back_populates="pagamento")

class Evento(Base):
    __tablename__ = 'eventos'
    id: Mapped[int] = mapped_column(primary_key=True)
    funcionario_id: Mapped[int] = mapped_column(ForeignKey("funcionarios.id"))
    pagamento_id: Mapped[Optional[int]] = mapped_column(ForeignKey("pagamentos.id"))
    tipo_evento: Mapped[str] = mapped_column(String(50))
    data_evento: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    observacao: Mapped[Optional[str]] = mapped_column(String(300))
    
    funcionario: Mapped["Funcionario"] = relationship(back_populates="eventos")
    pagamento: Mapped[Optional["Pagamento"]] = relationship(back_populates="eventos")

class DiasUteis(Base):
    __tablename__ = 'dias_uteis'
    id: Mapped[int] = mapped_column(primary_key=True)
    sindicato_id: Mapped[int] = mapped_column(ForeignKey("sindicatos.id"))
    mes: Mapped[int] = mapped_column()
    ano: Mapped[int] = mapped_column()
    dias_uteis: Mapped[int] = mapped_column()
    
    sindicato: Mapped["Sindicato"] = relationship(back_populates="dias_uteis")
    __table_args__ = (UniqueConstraint('sindicato_id', 'mes', 'ano', name='_sindicato_mes_ano_uc'),)
    
    
def create_database():
    print("Criando tabelas no banco de dados...")
    engine = create_engine("sqlite:///meu_banco.db")
    Base.metadata.create_all(engine)
    
    print("Tabelas criadas com sucesso.")

if __name__ == '__main__':
    create_database()