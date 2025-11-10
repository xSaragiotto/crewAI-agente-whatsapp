import time
import random
from flask import Flask, request, jsonify
from services.uazapi import Uazapi
from agent.agent_ai import BotVania

app = Flask(__name__) # Passa para o Flask o Arquivo principal

# Criação do endpoint
@app.route('/bot/vania/webhook/', methods=['POST'])
def webhook():
    data = request.json # Extrai a requisição HTTP que chegou na rota
    print(f"EVENTO RECEBIDO: {data}") # Log

    if data.get('EventType') != 'messages': # Verifica se é um evento de mensagem
        return jsonify({'status': 'ignored', 'reason': 'não é mensagem'})
    
    # Não há necessidade de tratar 'IsGroup' ou outros formatos recebidos no webhook, a API Uazapi já faz nativamente.
    # Tratando o 'FromMe'
    message_info = data.get('message', {}) # Pega o conteúdo da mensagem
    instance_token = data.get('token') # Pega o Token da instancia 

    if message_info.get('fromMe', False): # O 'if' faz somente valores 'true' acessarem o bloco.
        print('Mensagem From Me - IGNORANDO.')
        return jsonify({'status': 'ignored', 'reason': 'From Me'}), 200 # Ignora a mensagem e retorna resposta via HTTP.
    
    chat_id = message_info.get('chatid')
    text = message_info.get('text', '')

    uaz = Uazapi() # Instanciando a classe.
    ## clean_number = uaz.clean_number(chat_id) # Caso precise usar somente o numero tratado na main.

    cleaned = Uazapi().clean_number(chat_id)

    print(f"[DEBUG] cleaned: {cleaned} | type: {type(cleaned)}") # Log
    print(f"[DEBUG] cleaned repr: {repr(cleaned)}") # Log

    agent_ai = BotVania(user_id=cleaned) # Instanciando o agente.

    content = message_info.get('content')

    # Transcreve audio se necessário.
    if isinstance(content, dict) and content.get('mimetype') == 'audio/ogg; codecs=opus': # Verificar se é dicionario
        message_id = message_info.get('messageid')
        text = uaz.transcribe_audio_openai(message_id, instance_token)
    elif message_info.get('text'):
        text = message_info.get('text') # Verifica se é texto
    else:
        return jsonify({'error': 'Dados de mensagem incompletos.'}), 400 # Nenhum dado válido

    full_message = uaz.buffer_management(chat_id, text)
    if full_message is None:
        return jsonify({'status': 'buffering'}), 200

    time.sleep(random.randint(10, 20)) # Wait para resposta.

    uaz.start_typing(number=chat_id) # Enviando presença de 'digitando...' por 30000 ms

    response = agent_ai.kickoff(text) # Enviando o conteudo da mensagem para o agente

    print(f'Log: {response}') # Log

    # Retorna a mensagem para o usuário.
    uaz.send_message(         
        number=chat_id,
        message=response.raw
    )

    return jsonify({'status': 'success'}), 200

    # Inicia o servidor
    if __name__ == '__main__':
        main.run(host="0.0.0.0", port=5000, debug=True)
