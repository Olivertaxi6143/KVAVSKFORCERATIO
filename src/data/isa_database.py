"""
Módulo de base de datos para Intelligent Strategy Advisor (ISA)
Implementa el esquema profesional y utilidades de acceso usando SQLAlchemy.
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
from typing import Optional
import os

# Definir base declarativa
Base = declarative_base()

# --- Tablas principales ---

class Strategy(Base):
    __tablename__ = 'strategies'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, unique=True)
    factor_k = Column(Float, nullable=False)
    predictability = Column(Float, nullable=False)
    sharpe = Column(Float, nullable=False)
    drawdown = Column(Float, nullable=False)
    cagr = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    # Relaciones
    analysis_results = relationship('AnalysisResult', back_populates='strategy')

class AnalysisResult(Base):
    __tablename__ = 'analysis_results'
    id = Column(Integer, primary_key=True)
    strategy_id = Column(Integer, ForeignKey('strategies.id'), nullable=False)
    result_json = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    # Relaciones
    strategy = relationship('Strategy', back_populates='analysis_results')

class Portfolio(Base):
    __tablename__ = 'portfolios'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class LogEntry(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    event_type = Column(String(64), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

# --- Utilidades de conexión y sesión ---

class ISADatabase:
    """Gestor profesional de la base de datos ISA."""
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'isa_database.sqlite3')
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False, future=True)
        self.Session = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
        self._init_db()

    def _init_db(self):
        """Crea las tablas si no existen."""
        Base.metadata.create_all(self.engine)

    def get_session(self):
        """Obtiene una nueva sesión de base de datos."""
        return self.Session()

# --- Ejemplo de uso ---
if __name__ == "__main__":
    db = ISADatabase()
    session = db.get_session()
    # Insertar ejemplo
    if not session.query(Strategy).filter_by(name="Estrategia Demo").first():
        s = Strategy(
            name="Estrategia Demo",
            factor_k=9.5,
            predictability=87.0,
            sharpe=2.1,
            drawdown=8.5,
            cagr=22.3
        )
        session.add(s)
        session.commit()
        print("Estrategia Demo insertada.")
    else:
        print("Estrategia Demo ya existe.")
    session.close() 