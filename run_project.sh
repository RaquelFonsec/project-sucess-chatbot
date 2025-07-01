#!/bin/bash

echo "🚀 EXECUTANDO PROJETO COMPLETO"
echo "==============================="

# Verificar se modelo foi treinado
if [ ! -f "ml_model/data/trained_model.pkl" ]; then
    echo "📊 Treinando modelo..."
    cd ml_model
    python train_model.py
    cd ..
    echo ""
fi

echo "🌐 Iniciando API..."
cd api
python app.py &
API_PID=$!
cd ..

echo "⏱️  Aguardando API inicializar..."
sleep 5

echo "🤖 Iniciando Chatbot..."
echo "==============================="
cd chatbot
python chatbot.py

# Cleanup
echo "🧹 Finalizando API..."
kill $API_PID 2>/dev/null

echo "✅ Projeto finalizado!"
