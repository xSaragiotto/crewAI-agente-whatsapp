import requests
import os
import io
# import base64
import openai
from collections import defaultdict
import time

class Uazapi:

    # Buffer compartilhado entre instâncias
    message_buffer = defaultdict(list)
    last_message_time = {}
    BUFFER_TIMEOUT = 5  # segundos

    def __init__(self):
        self.__api_url = os.environ.get('UAZAPI_URL')  # DEIXAR O TOKEN DINAMICO
        self.__token = os.environ.get('UAZAPI_TOKEN')

    def clean_number(self, number:str) -> str: # Removemos o sufixo '@s.whatsapp.net' se existir
        return number.replace('@s.whatsapp.net', '').strip()
    
    # Buffer de mensagem
    def buffer_management(self, chat_id: str, text: str) -> str | None:
        now = time.time()
        self.message_buffer[chat_id].append(text)

        last_time = self.last_message_time.get(chat_id, 0)
        self.last_message_time[chat_id] = now

        if now - last_time < self.BUFFER_TIMEOUT:
            print(f'[BUFFER] Aguardando mais mensagens de {chat_id}')
            return None
        
        full_message = ''.join(self.message_buffer[chat_id])
        self.message_buffer.pop(chat_id, None)
        self.last_message_time.pop(chat_id, None)
        print(f'[BUFFER] Mensagem final de {chat_id}: {full_message}')
        return full_message

    # Envia mensagem de resposta
    def send_message(self, number, message): 

        clean_number = self.clean_number(number)

        url = f'{self.__api_url}/send/text' # Endpoint da uazpi para enviar mensagem
        headers = {
            'Accept': 'application/json',
            'token': self.__token,
            'Content-Type': 'application/json'
        }
        payload = {
            'number': clean_number,
            'text': message,
        }

        print(f'Enviando Mensagem para o Numero: {clean_number} | Message:{message}') # Console Log

        response = requests.post(url, json=payload, headers=headers)

        print(f'Status: {response.status_code}, resposta: {response.text}') # Console Log
        return response
    
    # Envia presença 'digitando...' via UazAPI.
    def start_typing(self, number): 
        
        clean_number = self.clean_number(number)

        url = f'{self.__api_url}/message/presence'
        headers = {
            "Accept": "application/json",
            "token": self.__token,
            "Content-Type": "application/json"
        }
        payload = {
            "number": clean_number,
            "presence": "composing",
            "delay": 30000,
        }

        # print(f"Enviando presença de 'digitando...' para: {clean_number}") # Console Log

        response = requests.post(url, json=payload, headers=headers)

        print(f"Status: {response.status_code}, resposta: {response.text}") # Console Log
        return response
    
    # Transcreve audio em texto
    def transcribe_audio_openai(self, message_id: str, token: str) -> str: 

        api_url = f'{self.__api_url}/message/download' # Endpoint para baixar audio
        payload = {
            'id': message_id,
            'return_base64': True,
            'return_link': False
        }
        headers = {
            'Accept': 'application/json',
            'token': self.__token,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(api_url, json=payload, headers=headers) # Faz a requisição para baixar o áudio
            # response.raise_for_status()
            # print('Resposta Uazapi:', response.json()) # Log
            # audio_base64 = response.json().get('base64Data') # Precisa adicionar um conversor para mp3 ou outros formatos.

            # if not audio_base64: # Log
                # print("Erro: áudio não disponível ou base64 vazio") 
                # return None

            # audio_bytes = base64.b64decode(audio_base64)
            # audio_file = io.BytesIO(audio_bytes)

            file_url = response.json().get('fileURL') # Pega o URL do audio para download
            mimetype = response.json().get('mimetype', '') # Pega o tipo do audio.

            if not file_url: # Log
                print('Erro: Arquivo de áudio não retornado pela Uazapi') 
                return None

            audio_response = requests.get(file_url)
            audio_response.raise_for_status()
            audio_bytes = audio_response.content

            print(audio_response) # Log

            audio_file = io.BytesIO(audio_bytes) # Cria o Arquivo em memória

            if 'ogg' in mimetype: # Define o nome do arquivo
                audio_file.name = 'audio.ogg'
            elif 'mpeg' in mimetype or 'mp3' in mimetype:
                audio_file.name = 'audio.mp3'
            else:
                audio_file.name = 'audio.wav'

            transcription = openai.audio.transcriptions.create(     # Faz a transcrição usando OpenAI
                model='whisper-1',
                file=audio_file
            )
            print(f"Transcrição retornada: {getattr(transcription, 'text', 'sem texto retornado')}") # Log

            return transcription.text

        except requests.exceptions.HTTPError as http_err: # Log
            print(f"Erro HTTP: {http_err}")
            return None

        except Exception as e:
            print(f"Erro ao transcrever áudio: {e}") # Log
            return None



            


