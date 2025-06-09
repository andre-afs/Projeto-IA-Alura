from flask import Flask,render_template, request, Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *
from selecionar_persona import selecionar_persona, personas
from selecionar_documento import selecionar_documento, selecionar_contexto, carrega
from assistente_ecomart import criar_assistente, criar_thread

load_dotenv()
api_key_env = os.getenv("OPENAI_API_KEY")

cliente = OpenAI(api_key=api_key_env)
modelo = "gpt-4"

assistente = criar_assistente()
thread = criar_thread()

app = Flask(__name__)
app.secret_key = 'alura'

def bot(prompt):
    maximo_tentativas = 1
    repeticao = 0

    while True:
        try:
            cliente.beta.threads.messages.create(
                thread=thread.id,
                role="user",
                content=prompt
            )

            run = cliente.beta.threads.runs.create(
                thread=thread.id,
                assistant=assistente.id,
                model=modelo
            )

            while run.status != "completed":
                run = cliente.beta.threads.runs.retrieve(
                    thread=thread.id,
                    run=run.id
                )

            historico = list(cliente.beta.threads.messages.list(thread=thread.id).data)
            resposta = historico[0]
            return resposta
        except Exception as erro:
            repeticao += 1
            if repeticao >= maximo_tentativas:
                    return "Erro no GPT: %s" % erro
            print('Erro de comunicação com OpenAI:', erro)
            sleep(1)


@app.route("/chat", methods=["POST"])
def chat():
    prompt = request.json['msg'] 
    resposta = bot(prompt)
    texto_resposta = resposta.content[0].text.value
    return texto_resposta

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug = True)

