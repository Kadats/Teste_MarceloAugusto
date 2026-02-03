from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel
from .db import get_db

app = FastAPI(
    title="API Intuitive Care - Teste Marcelo",
    description="API para consulta de despesas de operadoras de saúde (ANS).",
    version="1.0.0"
)

# --- Schemas (Modelos de Resposta - O contrato da API) ---
class OperadoraStats(BaseModel):
    razao_social: str
    total_despesas: float
    uf: str

class TopOperadora(BaseModel):
    razao_social: str
    registro_ans: str
    total_despesas: float

# --- Rotas ---

@app.get("/")
def health_check():
    """Rota raiz para verificar se a API está online."""
    return {"status": "ok", "message": "API de Despesas ANS rodando!"}

@app.get("/operadoras", summary="Busca operadoras")
def listar_operadoras(
    busca: Optional[str] = None, 
    limit: int = 10, 
    db: Session = Depends(get_db)
):
    """
    Lista as operadoras com maiores despesas.
    Permite filtrar por nome (busca) e limitar a quantidade.
    """
    # Query segura usando parâmetros (:busca) para evitar SQL Injection
    query_sql = """
        SELECT razao_social, uf, total_despesas 
        FROM despesas_agregadas
        WHERE (:busca IS NULL OR lower(razao_social) LIKE lower('%' || :busca || '%'))
        ORDER BY total_despesas DESC
        LIMIT :limit
    """
    
    # Executa SQL puro
    results = db.execute(text(query_sql), {"busca": busca, "limit": limit}).fetchall()
    
    # Formata resposta
    lista_resposta = []
    for row in results:
        lista_resposta.append({
            "razao_social": row.razao_social,
            "uf": row.uf,
            "total_despesas": float(row.total_despesas)
        })
        
    return lista_resposta

@app.get("/dashboard/top-10", response_model=List[TopOperadora])
def top_10_despesas_anual(db: Session = Depends(get_db)):
    """
    Retorna o Top 10 operadoras que mais gastaram no último ano.
    """
    query = """
        SELECT 
            o.razao_social,
            o.registro_ans,
            SUM(d.valor_despesa) as total_despesas
        FROM despesas_detalhadas d
        JOIN operadoras o ON d.registro_ans = o.registro_ans
        GROUP BY o.razao_social, o.registro_ans
        ORDER BY total_despesas DESC
        LIMIT 10;
    """
    results = db.execute(text(query)).fetchall()
    
    return [
        {
            "razao_social": row.razao_social, 
            "registro_ans": row.registro_ans, 
            "total_despesas": row.total_despesas
        } 
        for row in results
    ]

@app.get("/dashboard/resumo")
def resumo_geral(db: Session = Depends(get_db)):
    """Retorna números gerais para o topo do Dashboard."""
    total_despesa = db.execute(text("SELECT SUM(valor_despesa) FROM despesas_detalhadas")).scalar()
    total_ops = db.execute(text("SELECT COUNT(*) FROM operadoras")).scalar()
    
    return {
        "total_gasto_geral": total_despesa,
        "total_operadoras_analisadas": total_ops
    }

