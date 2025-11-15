import time
import random
from flask import Flask, request, jsonify
from services.uazapi import Uazapi
from agent.agent_ai import BotVania

app = Flask(__name__)
app.url_map.strict_slashes = False  # Aceita URLs com ou sem barra final

@app.route('/bot/vania/webhook/', methods=['POST'])
def webhook():
    data = request.json
    print(f"EVENTO RECEBIDO: {data}")

    if data.get('EventType') != 'messages':
        return jsonify({'status': 'ignored', 'reason': 'não é mensagem'})
    
    message_info = data.get('message', {})
    instance_token = data.get('token')

    if message_info.get('fromMe', False):
        print('Mensagem From Me - IGNORANDO.')
        return jsonify({'status': 'ignored', 'reason': 'From Me'}), 200
    
    chat_id = message_info.get('chatid')
    uaz = Uazapi()
    cleaned = uaz.clean_number(chat_id)

    print(f"[DEBUG] cleaned: {cleaned} | type: {type(cleaned)}")

    content = message_info.get('content')

    # Transcreve audio se necessário
    if isinstance(content, dict) and content.get('mimetype') == 'audio/ogg; codecs=opus':
        message_id = message_info.get('messageid')
        text = uaz.transcribe_audio_openai(message_id, instance_token)
    elif message_info.get('text'):
        text = message_info.get('text')
    else:
        return jsonify({'error': 'Dados de mensagem incompletos.'}), 400

    # Callback para processar a mensagem completa (executado após timeout)
    def process_complete_message(chat_id, full_message):
        time.sleep(random.randint(10, 20))
        uaz.start_typing(number=chat_id)
        
        agent_ai = BotVania(user_id=cleaned)
        response = agent_ai.kickoff(full_message)  # Usa full_message acumulada!
        
        print(f'Log: {response}')
        uaz.send_message(number=chat_id, message=response.raw)

    # Adiciona ao buffer - o callback será executado automaticamente após 5s
    uaz.buffer_management(chat_id, text, callback=process_complete_message)
    
    # Retorna imediatamente informando que está bufferizando
    return jsonify({'status': 'buffering'}), 200

if __name__ == '__main__':  
    app.run(host="0.0.0.0", port=5000, debug=True)