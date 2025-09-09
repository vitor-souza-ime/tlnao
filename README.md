# 🤖 TLNAO – TinyLlama + NAO Robot Chat

Este projeto integra o robô humanoide **NAO** com o modelo de linguagem **TinyLlama** para criar um sistema de chat interativo em inglês.  
O código principal está no arquivo [`main.py`](main.py).

---

## 📌 Funcionalidades

- Conexão direta com o robô NAO via **NAOqi SDK** (`qi`).
- Reconhecimento de fala usando **ALSpeechRecognition**.
- Geração de respostas com **TinyLlama-1.1B-Chat** (Hugging Face Transformers).
- Respostas faladas pelo **ALTextToSpeech** do NAO.
- Suporte a comandos especiais:
  - **“bye”**, **“stop”**, **“quit”** → encerra a conversa.
  - **“clear history”** → limpa o histórico de contexto da IA.
  - **“test listen”** → executa um teste de escuta rápida.

---

## ⚙️ Requisitos

### Hardware
- Robô **NAO** com firmware compatível com NAOqi 2.1+.
- Conexão de rede entre o PC e o NAO.

### Software
- Python **3.8+** (Linux ou Windows).
- Bibliotecas necessárias:
  pip install torch transformers qi

⚠️ **Observação:** o modelo TinyLlama requer GPU (CUDA) para melhor desempenho. Em CPU, a execução pode ser lenta.

---

## 🚀 Como Executar

1. Clone este repositório:

   git clone https://github.com/vitor-souza-ime/tlnao.git
   cd tlnao

2. Configure o IP do seu NAO no arquivo [`main.py`](main.py), na função `main()`:

   NAO_IP = "172.15.1.29"  # altere para o IP do seu robô

3. Execute o programa:

   python main.py

4. O NAO dará uma saudação inicial e aguardará sua fala.
   Fale em inglês e aguarde a resposta.

## 🧪 Exemplo de Uso

* Usuário: *"Hello robot, how are you today?"*
* NAO (via TinyLlama): *"I'm doing great. How about you?"*

## 📂 Estrutura do Projeto

```
tlnao/
│
├── main.py        # Código principal do chat NAO + TinyLlama
└── README.md      # Este guia
```

---

## 📝 Notas

* O vocabulário reconhecido pelo NAO é limitado, mas foi expandido em `listen()` para conversação natural.
* O TinyLlama gera respostas em inglês, resumidas a **2 frases** para evitar falas muito longas.
* O projeto está em fase de testes e pode ser estendido para incluir controle de LEDs, gestos e integração multimodal.

---

## 📧 Contato

Autor: **Vitor Amadeu Souza**
Repositório: [tlnao](https://github.com/vitor-souza-ime/tlnao)
