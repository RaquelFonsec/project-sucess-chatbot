from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sys
import os
import joblib
import numpy as np
import pandas as pd
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv('../.env')


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

sys.path.append("../ml_model")

app = FastAPI(
    title="Project Success Prediction API",
    description="API para prever sucesso de projetos com ML + LLM",
    version="1.0.0"
)

class ProjectData(BaseModel):
    duracao_meses: int
    orcamento: float
    tamanho_equipe: int
    recursos_disponiveis: str
    complexidade: str
    experiencia_gerente: int
    tipo_projeto: str

class PredictionResponse(BaseModel):
    sucesso_previsto: bool
    probabilidade_sucesso: float
    confianca: str
    recomendacoes: List[str]

class LLMAnalysisResponse(BaseModel):
    ml_prediction: dict
    llm_analysis: str
    combined_insights: str

# Carregar modelo
try:
    model = joblib.load("../ml_model/data/trained_model.pkl")
    le_recursos = joblib.load("../ml_model/data/le_recursos.pkl")
    le_complexidade = joblib.load("../ml_model/data/le_complexidade.pkl")
    le_tipo = joblib.load("../ml_model/data/le_tipo.pkl")
    
    with open("../ml_model/data/model_metadata.json", "r") as f:
        metadata = json.load(f)
    
    print("✅ Modelo carregado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao carregar modelo: {e}")
    model = None

@app.get("/")
async def root():
    return {
        "message": "Project Success Prediction API with LLM",
        "status": "running",
        "version": "1.0.0",
        "features": ["ML Prediction", "LLM Analysis", "Hybrid Intelligence"]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy" if model is not None else "unhealthy",
        "model_loaded": model is not None,
        "llm_available": bool(os.getenv("OPENAI_API_KEY"))
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict_project_success(project: ProjectData):
    if model is None:
        raise HTTPException(status_code=500, detail="Modelo não carregado")
    
    try:
        # Encoding
        recursos_encoded = le_recursos.transform([project.recursos_disponiveis])[0]
        complexidade_encoded = le_complexidade.transform([project.complexidade])[0]
        tipo_encoded = le_tipo.transform([project.tipo_projeto])[0]
        
        # Features
        features_dict = {
            "duracao_meses": project.duracao_meses,
            "orcamento": project.orcamento,
            "tamanho_equipe": project.tamanho_equipe,
            "recursos_encoded": recursos_encoded,
            "complexidade_encoded": complexidade_encoded,
            "experiencia_gerente": project.experiencia_gerente,
            "tipo_encoded": tipo_encoded
        }
        
        features = pd.DataFrame([features_dict])
        
        # Previsão
        probabilidade = model.predict_proba(features)[0][1]
        predicao = model.predict(features)[0]
        
        # Recomendações
        recomendacoes = []
        if probabilidade < 0.6:
            if project.duracao_meses > 18:
                recomendacoes.append("⏰ Considere reduzir duração para 12-15 meses")
            if project.orcamento < 500000:
                recomendacoes.append("💰 Orçamento pode estar baixo")
            if project.tamanho_equipe > 20:
                recomendacoes.append("👥 Equipe muito grande pode gerar overhead")
            if project.recursos_disponiveis == "Baixo":
                recomendacoes.append("🔧 Recursos insuficientes são críticos")
            if project.experiencia_gerente < 5:
                recomendacoes.append("🎓 Considere mentoria para o gerente")
        else:
            recomendacoes.append("🎉 Excelente! Projeto com alta probabilidade de sucesso")
        
        return PredictionResponse(
            sucesso_previsto=bool(predicao),
            probabilidade_sucesso=float(probabilidade),
            confianca="Alta" if abs(probabilidade - 0.5) > 0.3 else "Média",
            recomendacoes=recomendacoes
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na previsão: {str(e)}")

@app.post("/analyze-with-llm", response_model=LLMAnalysisResponse)
async def analyze_project_with_llm(project: ProjectData):
    """Endpoint que combina ML + LLM"""
    
    # Fazer predição com ML
    prediction = await predict_project_success(project)
    
    # Análise contextual com LLM
    llm_prompt = f"""
    Como especialista em gestão de projetos, analise este projeto:
    
    📊 DADOS DO PROJETO:
    - Duração: {project.duracao_meses} meses
    - Orçamento: R$ {project.orcamento:,.2f}
    - Equipe: {project.tamanho_equipe} pessoas
    - Recursos: {project.recursos_disponiveis}
    - Complexidade: {project.complexidade}
    - Experiência do gerente: {project.experiencia_gerente} anos
    - Tipo: {project.tipo_projeto}
    
    🤖 PREDIÇÃO ML: {prediction.probabilidade_sucesso:.1%} de sucesso
    
    Forneça uma análise detalhada incluindo:
    1. Principais fatores de risco/sucesso
    2. Recomendações específicas para melhorar
    3. Benchmarks da indústria para este tipo de projeto
    4. Próximos passos sugeridos
    
    Seja específico e prático.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": llm_prompt}],
            max_tokens=600,
            temperature=0.7
        )
        
        llm_analysis = response.choices[0].message.content
        
        return LLMAnalysisResponse(
            ml_prediction=prediction.dict(),
            llm_analysis=llm_analysis,
            combined_insights="✅ Análise híbrida ML + LLM concluída com sucesso"
        )
    except Exception as e:
        return LLMAnalysisResponse(
            ml_prediction=prediction.dict(),
            llm_analysis=f"⚠️ Análise LLM temporariamente indisponível: {str(e)}",
            combined_insights="📊 Usando apenas predição ML"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
