#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import torch
from transformers import pipeline
import time
import qi

class NAOTinyLlamaChat:
    def __init__(self, nao_ip="172.15.1.80", nao_port=9559):
        """
        Chat NAO + TinyLlama usando o método de escuta que funciona
        """
        try:
            print(f"🔗 Conectando ao NAO em {nao_ip}:{nao_port}...")
            
            # Conecta ao NAO
            self.session = qi.Session()
            self.session.connect(f"tcp://{nao_ip}:{nao_port}")
            print("✅ Conectado ao NAO!")
            
            # Inicializa serviços
            self.asr = self.session.service("ALSpeechRecognition")
            self.memory = self.session.service("ALMemory")
            self.tts = self.session.service("ALTextToSpeech")
            
            # Configura idioma
            self.tts.setLanguage("English")
            self.asr.setLanguage("English")
            
            print("✅ Serviços NAO inicializados!")
            
        except Exception as e:
            print(f"❌ Erro ao conectar com NAO: {e}")
            raise

    def load_tinyllama(self):
        """Carrega o modelo TinyLlama"""
        try:
            print("🧠 Carregando TinyLlama...")
            
            self.pipe = pipeline(
                "text-generation",
                model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                torch_dtype=torch.bfloat16,
                device_map="auto",
                trust_remote_code=True
            )
            
            # Histórico da conversa
            self.messages = [
                {"role": "system", "content": ""}
            ]
            
            print("✅ TinyLlama carregado!")
            
        except Exception as e:
            print(f"❌ Erro ao carregar TinyLlama: {e}")
            raise

    def speak(self, text):
        """Faz o NAO falar"""
        try:
            print(f"🤖 NAO: {text}")
            self.tts.say(text)
            time.sleep(0.2)  # Pequena pausa
        except Exception as e:
            print(f"❌ Erro na fala: {e}")

    def listen(self, duration=8.0, extra_vocabulary=None):
        """
        Método baseado no seu código que funciona - adaptado com vocabulário expandido
        """
        try:
            # Vocabulário base expandido para conversação natural
            vocabulary = [
                # Cumprimentos e cortesia
                "hello", "hi", "hey", "good", "morning", "afternoon", "evening",
                "please", "thank", "you", "thanks", "welcome", "sorry",
                
                # Perguntas básicas
                "what", "how", "where", "when", "why", "who", "which", "can", "do", 
                "are", "is", "will", "would", "could", "should",
                
                # Respostas
                "yes", "no", "maybe", "sure", "okay", "right", "wrong", "true", "false",
                
                # Ações e comandos
                "tell", "me", "about", "talk", "speak", "listen", "look", "see",
                "move", "walk", "turn", "stop", "go", "come", "help", "show",
                
                # Objetos e lugares
                "robot", "nao", "computer", "table", "chair", "room", "house", "outside",
                "ball", "red", "blue", "green", "yellow", "black", "white",
                
                # Pessoas e relacionamentos
                "you", "i", "we", "they", "he", "she", "friend", "family", "people",
                
                # Tempo
                "time", "today", "yesterday", "tomorrow", "now", "later", "before", "after",
                "day", "night", "week", "month", "year",
                
                # Números
                "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
                
                # Sentimentos e estados
                "happy", "sad", "good", "bad", "great", "fine", "tired", "hungry", "cold", "hot",
                
                # Tópicos de conversa
                "weather", "music", "book", "movie", "food", "game", "sport", "news",
                "work", "school", "learn", "teach", "study", "read", "write",
                
                # Conectores e palavras funcionais
                "and", "or", "but", "because", "if", "then", "also", "too", "very",
                "really", "quite", "just", "only", "all", "some", "many", "few",
                "the", "a", "an", "this", "that", "these", "those",
                
                # Despedidas
                "bye", "goodbye", "see", "later", "stop", "quit", "exit", "end",
                
                # Teste
                "test", "check", "try", "start", "begin"
            ]
            
            # Adiciona vocabulário extra se fornecido
            if extra_vocabulary:
                vocabulary.extend(extra_vocabulary)
                print(f"   Vocabulário expandido: +{len(extra_vocabulary)} palavras")
            
            print(f"🎤 Escutando por {duration} segundos... (Vocabulário: {len(vocabulary)} palavras)")
            
            # Configura ASR (sem parâmetros que causam erro)
            self.asr.pause(True)
            self.asr.setVocabulary(vocabulary, False)
            self.asr.pause(False)
            
            # Limpa memória
            self.memory.insertData("WordRecognized", [])
            
            # Subscreve ao ASR
            self.asr.subscribe("TinyLlama_Chat")
            
            print("   🟢 PODE FALAR AGORA!")
            
            start_time = time.time()
            recognized_words = []
            last_word_time = start_time
            
            try:
                while time.time() - start_time < duration:
                    time.sleep(0.1)
                    
                    # Verifica palavras reconhecidas
                    words_data = self.memory.getData("WordRecognized")
                    
                    if words_data and len(words_data) >= 2:
                        word = words_data[0]
                        confidence = words_data[1] if len(words_data) > 1 else 0.0
                        
                        # Filtra palavras válidas
                        if (word and word not in recognized_words and 
                            confidence > 0.3 and word != "<...>"):
                            
                            recognized_words.append(word)
                            last_word_time = time.time()
                            print(f"   ✅ '{word}' (conf: {confidence:.2f})")
                            
                            # Para se detectar palavras de saída
                            if word.lower() in ["bye", "goodbye", "stop", "quit", "exit", "end"]:
                                print("   🛑 Comando de saída detectado!")
                                break
                    
                    # Para se passou tempo suficiente sem novas palavras
                    if recognized_words and (time.time() - last_word_time) > 3.0:
                        print("   ⏸️ Silêncio detectado, processando...")
                        break
                        
            except KeyboardInterrupt:
                print("\n   ⛔ Interrompido pelo usuário")
                
            finally:
                # Para o reconhecimento
                try:
                    self.asr.unsubscribe("TinyLlama_Chat")
                except:
                    pass
            
            if recognized_words:
                sentence = " ".join(recognized_words)
                print(f"   📝 Frase reconhecida: '{sentence}'")
                return sentence
            else:
                print("   ❌ Nenhuma palavra reconhecida")
                return None
                
        except Exception as e:
            print(f"❌ Erro na escuta: {e}")
            # Limpa em caso de erro
            try:
                self.asr.unsubscribe("TinyLlama_Chat")
            except:
                pass
            return None

    def ask_tinyllama(self, question: str):
        """Processa pergunta com TinyLlama"""
        try:
            print(f"🧠 TinyLlama processando: '{question}'")

            # Cria prompt no formato esperado pelo modelo
            self.messages = [
                {"role": "system", "content": "You are a helpful robot assistant. Reply clearly and concisely."},
                {"role": "user", "content": question}
            ]

            # Monta prompt formatado
            prompt = self.pipe.tokenizer.apply_chat_template(
                self.messages,
                tokenize=False,
                add_generation_prompt=True
            )

            # Gera resposta
            output = self.pipe(
                prompt,
                max_new_tokens=80,
                do_sample=True,
                temperature=0.6,   # Menos aleatório
                top_p=0.9,
                pad_token_id=self.pipe.tokenizer.eos_token_id
            )

            # Extrai a resposta do modelo
            resposta = output[0]["generated_text"]
            if resposta.startswith(prompt):
                resposta = resposta[len(prompt):].strip()
            else:
                resposta = resposta.strip()

            # Limpa tokens especiais e quebras
            resposta = resposta.replace("<|im_end|>", "").replace("<|im_start|>", "").strip()

            # Separa em frases e limita a duas para o NAO
            sentences = [s.strip() for s in resposta.split('.') if s.strip()]
            if len(sentences) >= 2:
                resposta = sentences[0] + ". " + sentences[1] + "."
            elif len(sentences) == 1:
                resposta = sentences[0] + "."

            # Garante que não devolve vazio
            if not resposta:
                resposta = "I'm not sure how to respond to that."

            print(f"🤖 TinyLlama respondeu: '{resposta}'")
            return resposta

        except Exception as e:
            print(f"❌ Erro com TinyLlama: {e}")
            return "I'm having trouble thinking right now."


    def test_listening(self):
        return False
        """Teste básico de escuta"""
        print("\n🧪 TESTE DE ESCUTA")
        self.speak("Testing speech recognition. Please say hello robot.")
        
        result = self.listen(duration=5.0, extra_vocabulary=["hello", "robot"])
        
        if result:
            self.speak(f"Great! I heard: {result}")
            return True
        else:
            self.speak("I didn't hear anything. Let me check the system.")
            return False

    def run_chat(self):
        """Loop principal do chat"""
        print("\n🚀 INICIANDO CHAT NAO + TINYLLAMA")
        
        # Carrega TinyLlama
        self.load_tinyllama()
         
        # Teste inicial
        print("\n📡 Testando sistema de escuta...")
        if not self.test_listening():
            print("⚠️ Problemas detectados, mas continuando...")
        
        # Saudação
        self.speak("Hello! I'm NAO with TinyLlama AI. I'm ready to chat with you in English. Please speak clearly.")
        
        conversation_count = 0
        consecutive_failures = 0
        
        while True:
            try:
                print(f"\n--- Conversa #{conversation_count + 1} ---")
                
                # Escuta o usuário
                print("🎤 Aguardando sua fala...")
                user_input = self.listen(duration=10.0)
                
                # DEBUG: Mostra exatamente o que foi capturado
                print(f"\n🔍 DEBUG - Entrada capturada:")
                print(f"   Tipo: {type(user_input)}")
                print(f"   Valor: '{user_input}'")
                print(f"   É None? {user_input is None}")
                print(f"   Está vazia? {user_input == '' if user_input else 'N/A'}")
                
                if user_input is None or user_input.strip() == "":
                    consecutive_failures += 1
                    print(f"❌ Falha #{consecutive_failures}")
                    
                    if consecutive_failures >= 3:
                        self.speak("I'm having trouble hearing you. Let me reset the speech system.")
                        print("🔄 Resetando sistema de fala...")
                        time.sleep(1)
                        consecutive_failures = 0
                    else:
                        feedback_messages = [
                            "I didn't catch that. Please speak louder and more clearly.",
                            "Could you repeat that? I'm listening.",
                            "Please try speaking one more time."
                        ]
                        self.speak(feedback_messages[consecutive_failures - 1])
                    continue
                
                # Reset contador de falhas
                consecutive_failures = 0
                
                print(f"👤 USUÁRIO DISSE: '{user_input}' (tamanho: {len(user_input)})")
                
                # Verifica comandos de saída
                exit_commands = ["bye", "goodbye", "stop", "quit", "exit", "end"]
                if any(cmd in user_input.lower() for cmd in exit_commands):
                    self.speak("Goodbye! It was wonderful chatting with you. Have a great day!")
                    break
                
                # Comandos especiais
                if "clear history" in user_input.lower():
                    self.messages = self.messages[0:1]
                    self.speak("Chat history cleared. Let's start fresh!")
                    continue
                
                if "test" in user_input.lower() and ("listen" in user_input.lower() or "hear" in user_input.lower()):
                    self.test_listening()
                    continue
                
                # Processa com TinyLlama
                print("🤖 Processando com TinyLlama...")
                self.speak("Let me think about that.")
                print(user_input)
                response = self.ask_tinyllama(user_input)
                
                # Responde
                if response and response.strip():
                    print(f"🤖 RESPOSTA SERÁ FALADA: '{response}'")
                    self.speak(response)
                else:
                    print("❌ Resposta vazia ou inválida!")
                    self.speak("I'm not sure how to respond to that.")
                
                conversation_count += 1
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n⛔ Chat interrompido pelo usuário")
                self.speak("Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Erro no chat: {e}")
                self.speak("Sorry, I encountered an error. Let's continue.")
                time.sleep(1)

def main():
    """Função principal"""
    try:
        print("=" * 60)
        print("🤖 NAO + TinyLlama Chat com Reconhecimento Funcional")
        print("=" * 60)
        
        # IP do NAO
        NAO_IP = "172.15.1.29"  # ALTERE PARA SEU IP# ALTERE PARA SEU IP
        
        # Cria e executa o chat
        chat = NAOTinyLlamaChat(NAO_IP)
        chat.run_chat()
        
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        print("\nVerifique:")
        print("1. NAO está ligado e conectado")
        print("2. IP do NAO está correto")
        print("3. pip install qi transformers torch")

if __name__ == "__main__":
    main()
