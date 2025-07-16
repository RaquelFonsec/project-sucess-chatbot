import os
from openai import OpenAI
from dotenv import load_dotenv
import requests
import pandas as pd
import json
import time


load_dotenv('../.env')


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class LLMProjectChatbot:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
        self.current_user = None
        self.project_data = {}
        
    def get_llm_response(self, user_message, context=""):
        """Usar GPT-4o-mini para respostas inteligentes"""
        system_prompt = f"""
        Você é um assistente especialista em gestão de projetos chamado ProjectAI.
        Seu objetivo é ajudar gestores a avaliar o sucesso de projetos usando dados e IA.
        
        Contexto: {context}
        
        Seja conversacional, profissional e faça perguntas de forma natural.
        Quando coletar dados, explique brevemente por que cada informação é importante.
        Use emojis para tornar a conversa mais amigável.
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"🤖 Ops, estou com dificuldades técnicas, mas vamos continuar!"
    
    def intelligent_welcome(self):
        """Boas-vindas inteligentes com LLM"""
        print("🤖 " + "="*60)
        print("🎯 CHATBOT INTELIGENTE DE ANÁLISE DE PROJETOS")
        print("="*60)
        
        welcome_msg = """
        Seja bem-vindo! Sou o ProjectAI, seu assistente inteligente.
        
        Vou ajudar você a prever o sucesso do seu próximo projeto usando:
        • Machine Learning treinado com 1000 projetos
        • Análise de IA contextual
        • Recomendações personalizadas
        
        Primeiro, preciso te conhecer melhor! 😊
        """
        
        response = self.get_llm_response(welcome_msg)
        print(f"\n🤖: {response}")
    
    def authenticate_user(self):
        """Autenticação de usuário"""
        try:
            users_df = pd.read_csv('../ml_model/data/users_data.csv')
            
            print("\n👥 Usuários disponíveis:")
            for _, user in users_df.iterrows():
                print(f"  {user['usuario_id']}. {user['nome']} ({user['cargo']})")
            
            while True:
                try:
                    user_id = int(input("\n🔑 Digite seu ID de usuário: "))
                    user = users_df[users_df['usuario_id'] == user_id]
                    
                    if not user.empty:
                        self.current_user = user.iloc[0].to_dict()
                        
                        # Cumprimento personalizado
                        greeting_context = f"Usuário: {self.current_user['nome']}, {self.current_user['cargo']}, {self.current_user['experiencia_anos']} anos de experiência"
                        greeting_msg = f"O usuário {self.current_user['nome']} acabou de fazer login. Cumprimente-o e comente sobre sua experiência."
                        
                        greeting = self.get_llm_response(greeting_msg, greeting_context)
                        print(f"\n🤖: {greeting}")
                        return True
                    else:
                        print("❌ Usuário não encontrado. Tente novamente.")
                        
                except ValueError:
                    print("❌ Digite um número válido.")
        except Exception as e:
            print(f"❌ Erro ao carregar usuários: {e}")
            return False
    
    def collect_project_data(self):
        """Coleta dados do projeto com conversação natural"""
        print("\n" + "="*50)
        print("📋 COLETA DE DADOS DO PROJETO")
        print("="*50)
        
        # Mapeamento de campos - CORRIGIDO
        field_map = {
            'duracao_meses': {'question': 'Quantos meses o projeto vai durar?', 'type': 'int'},
            'orcamento': {'question': 'Qual o orçamento total do projeto em R$?', 'type': 'float'},
            'tamanho_equipe': {'question': 'Quantas pessoas vão trabalhar no projeto?', 'type': 'int'},
            'experiencia_gerente': {'question': 'Quantos anos de experiência tem o gerente?', 'type': 'int'},
            'recursos_disponiveis': {'question': 'Recursos disponíveis?', 'type': 'choice', 'options': ['Baixo', 'Médio', 'Alto']},
            'complexidade': {'question': 'Complexidade técnica?', 'type': 'choice', 'options': ['Baixa', 'Média', 'Alta']},
            'tipo_projeto': {'question': 'Tipo do projeto?', 'type': 'choice', 'options': ['TI', 'Construção', 'Marketing', 'P&D']}
        }
        
        for field, config in field_map.items():
            # Gerar pergunta inteligente
            context = f"Coletando {field} para análise de projeto. Usuário: {self.current_user['nome']}"
            question_prompt = f"Faça uma pergunta natural sobre: {config['question']}. Explique brevemente por que essa informação é importante para análise."
            
            question = self.get_llm_response(question_prompt, context)
            print(f"\n🤖: {question}")
            
            # Coletar resposta
            while True:
                try:
                    if config['type'] == 'choice':
                        print(f"   Opções: {', '.join(config['options'])}")
                    
                    user_input = input("👤: ").strip()
                    
                    # Processar resposta
                    if config['type'] == 'int':
                        value = int(user_input)
                        self.project_data[field] = value
                        break
                    elif config['type'] == 'float':
                        # Limpar formatação brasileira
                        clean_input = user_input.replace('R$', '').replace('.', '').replace(',', '.')
                        value = float(clean_input)
                        self.project_data[field] = value
                        break
                    elif config['type'] == 'choice':
                        # CORREÇÃO: Comparação case-insensitive
                        user_choice = user_input.strip().lower()
                        options_lower = [opt.lower() for opt in config['options']]
                        
                        if user_choice in options_lower:
                            # Encontrar a opção original
                            original_option = config['options'][options_lower.index(user_choice)]
                            self.project_data[field] = original_option
                            print(f"✅ Selecionado: {original_option}")
                            break
                        else:
                            print(f"❌ Escolha uma das opções: {', '.join(config['options'])}")
                            print(f"💡 Dica: Digite exatamente como mostrado ou use minúsculas")
                    
                except ValueError:
                    print("❌ Formato inválido. Tente novamente.")
        
        return True
    
    def display_project_summary(self):
        """Mostrar resumo do projeto"""
        print("\n" + "="*50)
        print("📋 RESUMO DO PROJETO")
        print("="*50)
        
        summary_context = f"Dados coletados: {self.project_data}"
        summary_prompt = "Faça um resumo amigável dos dados do projeto que coletamos. Seja positivo e mencione se algo chama atenção."
        
        summary = self.get_llm_response(summary_prompt, summary_context)
        print(f"\n🤖: {summary}")
        
        # Dados técnicos
        print(f"\n📊 DADOS TÉCNICOS:")
        print(f"   ⏱️  Duração: {self.project_data['duracao_meses']} meses")
        print(f"   💰 Orçamento: R$ {self.project_data['orcamento']:,.2f}")
        print(f"   👥 Equipe: {self.project_data['tamanho_equipe']} pessoas")
        print(f"   🔧 Recursos: {self.project_data['recursos_disponiveis']}")
        print(f"   🎯 Complexidade: {self.project_data['complexidade']}")
        print(f"   🎓 Exp. Gerente: {self.project_data['experiencia_gerente']} anos")
        print(f"   🏗️  Tipo: {self.project_data['tipo_projeto']}")
    
    def get_ai_analysis(self):
        """Obter análise completa ML + LLM"""
        print("\n🔮 ANALISANDO COM IA...")
        print("-" * 30)
        
        # Animação de loading
        for i in range(3):
            print("🤖 Processando", "." * (i+1), end="\r")
            time.sleep(0.8)
        print("🤖 Análise concluída! ✅    ")
        
        try:
            # Chamar endpoint híbrido
            response = requests.post(
                f"{self.api_url}/analyze-with-llm",
                json=self.project_data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro na API: {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("❌ Erro: API não está rodando!")
            print("💡 Execute: cd api && python app.py")
            return None
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    def display_results(self, analysis):
        """Exibir resultados da análise"""
        print("\n" + "="*60)
        print("📊 RESULTADO DA ANÁLISE INTELIGENTE")
        print("="*60)
        
        ml_pred = analysis['ml_prediction']
        prob = ml_pred['probabilidade_sucesso']
        
        # Status visual
        status = "SUCESSO ✅" if ml_pred['sucesso_previsto'] else "ATENÇÃO ⚠️"
        emoji = "🎉" if ml_pred['sucesso_previsto'] else "⚠️"
        
        print(f"\n{emoji} STATUS: {status}")
        print(f"📈 Probabilidade de Sucesso: {prob:.1%}")
        print(f"🎯 Confiança: {ml_pred['confianca']}")
        
        # Barra visual
        bar_length = 20
        filled = int(prob * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"📊 [{bar}] {prob:.1%}")
        
        # Análise LLM
        print(f"\n🤖 ANÁLISE ESPECIALISTA:")
        print("=" * 40)
        print(analysis['llm_analysis'])
        
        # Recomendações ML
        if ml_pred['recomendacoes']:
            print(f"\n💡 RECOMENDAÇÕES RÁPIDAS:")
            for i, rec in enumerate(ml_pred['recomendacoes'], 1):
                print(f"{i}. {rec}")
        
        print(f"\n✨ {analysis['combined_insights']}")
    
    def run(self):
        """Executar chatbot inteligente"""
        try:
            # Verificar API
            try:
                response = requests.get(f"{self.api_url}/health", timeout=5)
                if response.status_code != 200:
                    print("❌ API não está funcionando!")
                    return
            except:
                print("❌ API não está rodando!")
                print("💡 Execute: cd api && python app.py")
                return
            
            # Fluxo principal
            self.intelligent_welcome()
            
            if not self.authenticate_user():
                return
            
            while True:
                print(f"\n{'='*60}")
                print("🚀 NOVA ANÁLISE DE PROJETO")
                print("="*60)
                
                if not self.collect_project_data():
                    break
                
                self.display_project_summary()
                
                confirm = input(f"\n❓ Analisar este projeto com IA? (s/n): ").lower().strip()
                
                if confirm == 's':
                    analysis = self.get_ai_analysis()
                    if analysis:
                        self.display_results(analysis)
                    else:
                        print("❌ Não foi possível fazer a análise.")
                
                continue_analysis = input(f"\n❓ Analisar outro projeto? (s/n): ").lower().strip()
                if continue_analysis != 's':
                    break
                
                self.project_data = {}
            
            # Despedida inteligente
            goodbye_msg = "O usuário está encerrando a sessão. Faça uma despedida amigável e profissional."
            goodbye = self.get_llm_response(goodbye_msg)
            print(f"\n🤖: {goodbye}")
            
        except KeyboardInterrupt:
            print(f"\n\n👋 Até logo!")
        except Exception as e:
            print(f"\n❌ Erro: {e}")

if __name__ == "__main__":
    chatbot = LLMProjectChatbot()
    chatbot.run()
