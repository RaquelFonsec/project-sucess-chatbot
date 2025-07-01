import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib
import json
import os

def create_project_data():
    """Cria dataset sintético de projetos"""
    np.random.seed(42)
    n_samples = 1000
    
    data = {
        'duracao_meses': np.random.randint(3, 24, n_samples),
        'orcamento': np.random.randint(100000, 5000000, n_samples),
        'tamanho_equipe': np.random.randint(3, 25, n_samples),
        'recursos_disponiveis': np.random.choice(['Baixo', 'Médio', 'Alto'], n_samples),
        'complexidade': np.random.choice(['Baixa', 'Média', 'Alta'], n_samples),
        'experiencia_gerente': np.random.randint(1, 20, n_samples),
        'tipo_projeto': np.random.choice(['TI', 'Construção', 'Marketing', 'P&D'], n_samples)
    }
    
    # Criar variável alvo com lógica
    sucessos = []
    for i in range(n_samples):
        score = 0
        
        # Duração ideal
        if 6 <= data['duracao_meses'][i] <= 15:
            score += 2
        elif data['duracao_meses'][i] > 18:
            score -= 1
            
        # Orçamento adequado
        if data['orcamento'][i] > 500000:
            score += 1
            
        # Tamanho de equipe
        if 5 <= data['tamanho_equipe'][i] <= 15:
            score += 2
        elif data['tamanho_equipe'][i] > 20:
            score -= 1
            
        # Recursos
        if data['recursos_disponiveis'][i] == 'Alto':
            score += 3
        elif data['recursos_disponiveis'][i] == 'Médio':
            score += 1
        else:
            score -= 1
            
        # Complexidade
        if data['complexidade'][i] == 'Baixa':
            score += 2
        elif data['complexidade'][i] == 'Alta':
            score -= 2
            
        # Experiência
        if data['experiencia_gerente'][i] > 10:
            score += 2
        elif data['experiencia_gerente'][i] > 5:
            score += 1
            
        # Ruído
        score += np.random.normal(0, 1)
        
        sucessos.append(1 if score > 2 else 0)
    
    data['sucesso'] = sucessos
    return pd.DataFrame(data)

def create_user_data():
    """Cria dataset de usuários"""
    users_data = {
        'usuario_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'nome': ['João Silva', 'Maria Santos', 'Pedro Costa', 'Ana Oliveira', 'Carlos Lima', 
                'Lucia Ferreira', 'Roberto Alves', 'Patricia Sousa', 'Fernando Rocha', 'Camila Dias'],
        'cargo': ['Gerente de TI', 'Analista de Projetos', 'Coordenador', 'Gerente Sênior', 
                 'Analista Júnior', 'Coordenadora', 'Gerente de TI', 'Analista Sênior', 
                 'Coordenador', 'Gerente de Projetos'],
        'historico_projetos': [15, 10, 25, 30, 5, 18, 22, 12, 20, 16],
        'experiencia_anos': [5, 3, 8, 12, 2, 6, 9, 4, 7, 5],
        'sucesso_medio': [80, 65, 90, 95, 45, 75, 85, 70, 88, 72]
    }
    return pd.DataFrame(users_data)

def train_model():
    """Função principal de treinamento"""
    print("🚀 Iniciando treinamento do modelo...")
    
    # Criar dados
    df_projects = create_project_data()
    df_users = create_user_data()
    
    # Salvar dados
    df_projects.to_csv('data/projects_data.csv', index=False)
    df_users.to_csv('data/users_data.csv', index=False)
    
    print(f"📊 Dados criados: {len(df_projects)} projetos")
    print(f"Distribuição: {df_projects['sucesso'].value_counts().to_dict()}")
    
    # Encoding
    le_recursos = LabelEncoder()
    le_complexidade = LabelEncoder()
    le_tipo = LabelEncoder()
    
    df_projects['recursos_encoded'] = le_recursos.fit_transform(df_projects['recursos_disponiveis'])
    df_projects['complexidade_encoded'] = le_complexidade.fit_transform(df_projects['complexidade'])
    df_projects['tipo_encoded'] = le_tipo.fit_transform(df_projects['tipo_projeto'])
    
    # Salvar encoders
    joblib.dump(le_recursos, 'data/le_recursos.pkl')
    joblib.dump(le_complexidade, 'data/le_complexidade.pkl')
    joblib.dump(le_tipo, 'data/le_tipo.pkl')
    
    # Features e target
    features = ['duracao_meses', 'orcamento', 'tamanho_equipe', 'recursos_encoded', 
               'complexidade_encoded', 'experiencia_gerente', 'tipo_encoded']
    X = df_projects[features]
    y = df_projects['sucesso']
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Treinar
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    
    # Avaliar
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"🎯 Acurácia: {accuracy:.3f}")
    print("\n📊 Relatório:")
    print(classification_report(y_test, y_pred))
    
    # Salvar modelo
    joblib.dump(model, 'data/trained_model.pkl')
    
    # Metadados
    metadata = {
        'accuracy': accuracy,
        'features': features,
        'classes': model.classes_.tolist()
    }
    
    with open('data/model_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("✅ Modelo treinado e salvo!")
    return model, accuracy

if __name__ == "__main__":
    model, accuracy = train_model()
    print(f"\n🎉 Concluído! Acurácia: {accuracy:.3f}")
