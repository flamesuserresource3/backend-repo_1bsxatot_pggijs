import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict

from database import db, create_document, get_documents
from schemas import Lead

app = FastAPI(title="Dental Leads API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LeadIntakeRequest(BaseModel):
    nome: str
    email: Optional[str] = None
    telefone: Optional[str] = None

    motivo_principal: Optional[str] = None
    como_conheceu: Optional[str] = None
    preferencia_horario: Optional[str] = None

    teve_diagnostico_previo: Optional[bool] = None
    detalhes_diagnostico: Optional[str] = None

    pronto_para_fechar: Optional[int] = None
    orcamento_estimado: Optional[str] = None

    disc_respostas: Optional[List[str]] = None  # valores "A"/"B"/"C"/"D"

class LeadResponse(BaseModel):
    id: str
    disc_scores: Dict[str, int]
    disc_tipo: str


def calcular_disc(respostas: Optional[List[str]]) -> Dict[str, int]:
    # Mapeia alternativas A-D para D/I/S/C de forma discreta
    mapping = {
        "A": "D",  # Dominância
        "B": "I",  # Influência
        "C": "S",  # Estabilidade
        "D": "C",  # Conformidade
    }
    scores = {"D": 0, "I": 0, "S": 0, "C": 0}
    if not respostas:
        return scores
    for r in respostas:
        r = (r or "").strip().upper()
        if r in mapping:
            scores[mapping[r]] += 1
    return scores


def tipo_disc(scores: Dict[str, int]) -> str:
    if not scores:
        return "Indefinido"
    # Empate: retorna combinação ordenada
    max_val = max(scores.values()) if scores else 0
    dominantes = [k for k, v in scores.items() if v == max_val and v > 0]
    if not dominantes:
        return "Indefinido"
    return "+".join(sorted(dominantes))


@app.get("/")
def read_root():
    return {"message": "Dental Leads Backend"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or ""
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response


@app.post("/api/lead-intake", response_model=LeadResponse)
def create_lead(payload: LeadIntakeRequest):
    scores = calcular_disc(payload.disc_respostas)
    disc = tipo_disc(scores)

    lead_data = Lead(
        nome=payload.nome,
        email=payload.email,
        telefone=payload.telefone,
        motivo_principal=payload.motivo_principal,
        como_conheceu=payload.como_conheceu,
        preferencia_horario=payload.preferencia_horario,
        teve_diagnostico_previo=payload.teve_diagnostico_previo,
        detalhes_diagnostico=payload.detalhes_diagnostico,
        pronto_para_fechar=payload.pronto_para_fechar,
        orcamento_estimado=payload.orcamento_estimado,
        disc_respostas=payload.disc_respostas or [],
        disc_scores=scores,
        disc_tipo=disc,
    )

    try:
        inserted_id = create_document("lead", lead_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"id": inserted_id, "disc_scores": scores, "disc_tipo": disc}


@app.get("/api/leads")
def list_leads(limit: int = Query(20, ge=1, le=100)):
    try:
        docs = get_documents("lead", {}, limit)
        # Sanitizar ObjectId para string
        for d in docs:
            if "_id" in d:
                d["_id"] = str(d["_id"])
        return {"items": docs, "count": len(docs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
