"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name.
"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, EmailStr

class Lead(BaseModel):
    """
    Leads da clínica odontológica
    Collection name: "lead"
    """
    nome: str = Field(..., description="Nome completo do lead")
    email: Optional[EmailStr] = Field(None, description="Email do lead")
    telefone: Optional[str] = Field(None, description="Telefone/WhatsApp")

    motivo_principal: Optional[str] = Field(None, description="Motivo principal da consulta")
    como_conheceu: Optional[str] = Field(None, description="Como conheceu a clínica")
    preferencia_horario: Optional[str] = Field(None, description="Preferência de horário")

    teve_diagnostico_previo: Optional[bool] = Field(None, description="Se já teve diagnóstico prévio")
    detalhes_diagnostico: Optional[str] = Field(None, description="Detalhes do diagnóstico, se houver")

    pronto_para_fechar: Optional[int] = Field(None, ge=1, le=5, description="Nível de prontidão para fechar (1-5)")
    orcamento_estimado: Optional[str] = Field(None, description="Faixa de orçamento estimada")

    disc_respostas: Optional[List[str]] = Field(None, description="Lista de respostas do questionário DISC (A/B/C/D)")
    disc_scores: Optional[Dict[str, int]] = Field(None, description="Pontuação por perfil: D, I, S, C")
    disc_tipo: Optional[str] = Field(None, description="Tipo DISC dominante")
