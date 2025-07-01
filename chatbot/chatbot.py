import requests
import pandas as pd
import time

class ProjectSuccessChatbot:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
        self.current_user = None
        self.project_data = {}
        
    def print_welcome(self):
        print("🤖 " + "="*60)
        print("🎯 CHATBOT DE PREVISÃO DE SUCESSO DE PROJETOS")
        print("="*60)
        print("Olá! Vou te ajudar a prever o sucesso do seu projeto!")
        print("="*60 + "\n")
    
    def authenticate_user(self):
        print("🔐 IDENTIFICAÇÃO DO USUÁRIO")
        print("-" * 30)
        
        try:
            users_df = pd.read_csv('../ml_model/data/users_data.csv')
            
            print("Usuários disponíveis:")
            for _, user in users_df.iterrows():
                print(f"  {user['usuario_id']}. {user['nome']} ({user['cargo']})")
            
            while True:
                try:
                    user_id = int(input("\nDigite seu ID de usuário: "))
                    user = users_df[users_df['usuario_id'] == user_id]
                    
                    if not user.empty:
                        self.current_user = user.iloc[0].to_dict()
                        print(f"\n✅ Bem-vindo(a), {self.current_user['nome']}!")
                        print(f"📊 Cargo: {self.current_user['cargo']}")
                        print(f"📈 Histórico: {self.current_user['historico_projetos']} projetos")
                        print(f"🎯 Taxa de sucesso: {self.current_user['sucesso_medio']}%")
                        return True
                    else:
                        print("❌ Usuário não encontrado. Tente novamente.")
                        
                except ValueError:
                    print("❌ Digite um número válido.")
        except Exception as e:
            print(f"❌ Erro ao carregar usuários: {e}")
            return False
    
    def collect_project_data(self):
        print("\n📋 DADOS DO PROJETO")
        print("-" * 30)
        
        questions = [
            {
                'key': 'duracao_meses',
                'question': '📅 Duração do projeto em meses (3-36)?',
                'type': 'int',
                'validation': lambda x: 3 <= x <= 36
            },
            {
                'key': 'orcamento',
                'question': '💰 Orçamento total em R$ (ex: 1000000)?',
                'type': 'float',
                'validation': lambda x: x > 0
            },
            {
                'key': 'tamanho_equipe',
                'question': '👥 Quantas pessoas na equipe (3-50)?',
                'type': 'int',
                'validation': lambda x: 3 <= x <= 50
            },
            {
                'key': 'experiencia_gerente',
                'question': '🎓 Anos de experiência do gerente (0-30)?',
                'type': 'int',
                'validation': lambda x: 0 <= x <= 30
            }
        ]
        
        choices = [
            {
                'key': 'recursos_disponiveis',
                'question': '🔧 Recursos disponíveis?',
                'options': ['Baixo', 'Médio', 'Alto']
            },
            {
                'key': 'complexidade',
                'question': '🎯 Complexidade do projeto?',
                'options': ['Baixa', 'Média', 'Alta']
            },
            {
                'key': 'tipo_projeto',
                'question': '🏗️ Tipo do projeto?',
                'options': ['TI', 'Construção', 'Marketing', 'P&D']
            }
        ]
        
        # Perguntas numéricas
        for q in questions:
            while True:
                try:
                    if q['type'] == 'int':
                        value = int(input(f"\n{q['question']}: "))
                    else:
                        value = float(input(f"\n{q['question']}: "))
                    
                    if q['validation'](value):
                        self.project_data[q['key']] = value
                        break
                    else:
                        print("❌ Valor inválido!")
                except ValueError:
                    print("❌ Digite um número válido!")
        
        # Perguntas de escolha
        for q in choices:
            print(f"\n{q['question']}")
            for i, option in enumerate(q['options'], 1):
                print(f"  {i}. {option}")
            
            while True:
                try:
                    choice = int(input("Escolha uma opção: ")) - 1
                    if 0 <= choice < len(q['options']):
                        self.project_data[q['key']] = q['options'][choice]
                        break
                    else:
                        print("❌ Opção inválida!")
                except ValueError:
                    print("❌ Digite um número válido!")
        
        return True
    
    def get_prediction(self):
        print("\n🔮 ANALISANDO SEU PROJETO...")
        print("-" * 30)
        
        try:
            for i in range(3):
                print(".", end="", flush=True)
                time.sleep(0.5)
            print(" ✅")
            
            response = requests.post(
                f"{self.api_url}/predict",
                json=self.project_data
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro na API: {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("❌ Erro: API não está rodando!")
            print("Execute: cd api && python app.py")
            return None
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    def display_results(self, prediction):
        print("\n" + "="*60)
        print("📊 RESULTADO DA ANÁLISE")
        print("="*60)
        
        prob = prediction['probabilidade_sucesso']
        status = "SUCESSO" if prediction['sucesso_previsto'] else "RISCO"
        emoji = "🎉" if prediction['sucesso_previsto'] else "⚠️"
        
        print(f"\n{emoji} STATUS: {status}")
        print(f"📈 Probabilidade de Sucesso: {prob:.1%}")
        print(f"🎯 Confiança: {prediction['confianca']}")
        
        # Barra visual
        bar_length = 20
        filled = int(prob * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"📊 [{bar}] {prob:.1%}")
        
        # Recomendações
        if prediction['recomendacoes']:
            print(f"\n💡 RECOMENDAÇÕES:")
            for i, rec in enumerate(prediction['recomendacoes'], 1):
                print(f"{i}. {rec}")
        
        # Interpretação
        print(f"\n🔍 INTERPRETAÇÃO:")
        if prob >= 0.8:
            print("🎯 Excelente! Continue com o planejamento atual.")
        elif prob >= 0.6:
            print("👍 Bom! Considere as recomendações para melhorar.")
        elif prob >= 0.4:
            print("⚠️ Atenção! Revise o planejamento antes de prosseguir.")
        else:
            print("🚨 Alto risco! Reavaliar escopo e recursos.")
    
    def show_project_summary(self):
        print(f"\n📋 RESUMO DO PROJETO")
        print("-" * 30)
        print(f"⏱️  Duração: {self.project_data['duracao_meses']} meses")
        print(f"💰 Orçamento: R$ {self.project_data['orcamento']:,.2f}")
        print(f"👥 Equipe: {self.project_data['tamanho_equipe']} pessoas")
        print(f"🔧 Recursos: {self.project_data['recursos_disponiveis']}")
        print(f"🎯 Complexidade: {self.project_data['complexidade']}")
        print(f"🎓 Exp. Gerente: {self.project_data['experiencia_gerente']} anos")
        print(f"🏗️  Tipo: {self.project_data['tipo_projeto']}")
    
    def run(self):
        try:
            self.print_welcome()
            
            # Verificar API
            try:
                response = requests.get(f"{self.api_url}/health")
                if response.status_code != 200:
                    print("❌ API não está funcionando!")
                    return
            except:
                print("❌ API não está rodando!")
                print("Execute: cd api && python app.py")
                return
            
            if not self.authenticate_user():
                return
            
            while True:
                print(f"\n{'='*60}")
                print("🚀 NOVA ANÁLISE DE PROJETO")
                print("="*60)
                
                if not self.collect_project_data():
                    break
                
                self.show_project_summary()
                
                confirm = input(f"\n❓ Analisar este projeto? (s/n): ").lower().strip()
                
                if confirm == 's':
                    prediction = self.get_prediction()
                    if prediction:
                        self.display_results(prediction)
                    else:
                        print("❌ Não foi possível fazer a previsão.")
                
                continue_analysis = input(f"\n❓ Analisar outro projeto? (s/n): ").lower().strip()
                if continue_analysis != 's':
                    break
                
                self.project_data = {}
            
            print(f"\n👋 Obrigado por usar o Chatbot!")
            
        except KeyboardInterrupt:
            print(f"\n\n👋 Até logo!")
        except Exception as e:
            print(f"\n❌ Erro: {e}")

if __name__ == "__main__":
    chatbot = ProjectSuccessChatbot()
    chatbot.run()
