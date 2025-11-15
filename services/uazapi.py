import requests
import os
import io
import openai
from collections import defaultdict
import time
import threading

class Uazapi:

    # Buffer compartilhado entre instâncias
    message_buffer = defaultdict(list)
    last_message_time = {}
    buffer_timers = {}
    BUFFER_TIMEOUT = 5  # segundos

    def __init__(self):
        self.__api_url = os.environ.get('UAZAPI_URL')
        self.__token = os.environ.get('UAZAPI_TOKEN')

    # Remove sufixo '@s.whatsapp.net'
    def clean_number(self, number: str) -> str:
        return number.replace('@s.whatsapp.net', '').strip()
    
    def buffer_management(self, chat_id: str, text: str, callback=None) -> None:
        """
        Gerencia o buffer de mensagens por chat_id.
        Acumula mensagens e executa callback após BUFFER_TIMEOUT segundos sem novas mensagens.
        """
        print(f"[BUFFER] 🚀 ENTROU no buffer_management - chat_id: {chat_id}, text: {text}")
        now = time.time()

        # Adiciona mensagem ao buffer
        self.message_buffer[chat_id].append(text)
        self.last_message_time[chat_id] = now

        print(f"[BUFFER] 📦 Buffer atual para {chat_id}: {self.message_buffer[chat_id]}")

        # Cancela o timer anterior se existir
        if chat_id in self.buffer_timers:
            print(f"[DEBUG] Cancelando timer anterior de {chat_id}")
            self.buffer_timers[chat_id].cancel()

        # Função que será executada após o timeout
        def process_buffer():
            full_message = ' '.join(self.message_buffer[chat_id])
            self.message_buffer.pop(chat_id, None)
            self.last_message_time.pop(chat_id, None)
            self.buffer_timers.pop(chat_id, None)
            print(f'[BUFFER] Processando mensagem completa de {chat_id}: {full_message}')

            if callback:
                callback(chat_id, full_message)
        
        # Cria novo timer
        timer = threading.Timer(self.BUFFER_TIMEOUT, process_buffer)
        timer.start()
        self.buffer_timers[chat_id] = timer

        print(f'[BUFFER] Mensagem adicionada ao buffer de {chat_id}. Timer de {self.BUFFER_TIMEOUT}s iniciado.')
        return None

    # Envia mensagem via uazapi
    def send_message(self, number, message):
        clean_number = self.clean_number(number)

        url = f'{self.__api_url}/send/text'
        headers = {
            'Accept': 'application/json',
            'token': self.__token,
            'Content-Type': 'application/json'
        }
        payload = {
            'number': clean_number,
            'text': message,
        }

        print(f'Enviando Mensagem para o Numero: {clean_number} | Message: {message}')

        response = requests.post(url, json=payload, headers=headers)

        print(f'Status: {response.status_code}, resposta: {response.text}')
        return response
    
    # Envia presença 'digitando...'
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

        response = requests.post(url, json=payload, headers=headers)

        print(f"Status: {response.status_code}, resposta: {response.text}")
        return response
    
    # Transcreve audio
    def transcribe_audio_openai(self, message_id: str, token: str) -> str:
        api_url = f'{self.__api_url}/message/download'
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
            response = requests.post(api_url, json=payload, headers=headers)
            
            file_url = response.json().get('fileURL')
            mimetype = response.json().get('mimetype', '')

            if not file_url:
                print('Erro: Arquivo de áudio não retornado pela Uazapi')
                return None

            audio_response = requests.get(file_url)
            audio_response.raise_for_status()
            audio_bytes = audio_response.content

            print(audio_response)

            audio_file = io.BytesIO(audio_bytes)

            # Define o nome do arquivo baseado no mimetype
            if 'ogg' in mimetype:
                audio_file.name = 'audio.ogg'
            elif 'mpeg' in mimetype or 'mp3' in mimetype:
                audio_file.name = 'audio.mp3'
            else:
                audio_file.name = 'audio.wav'

            # Transcreve usando OpenAI Whisper
            transcription = openai.audio.transcriptions.create(
                model='whisper-1',
                file=audio_file
            )
            print(f"Transcrição retornada: {getattr(transcription, 'text', 'sem texto retornado')}")

            return transcription.text

        except requests.exceptions.HTTPError as http_err:
            print(f"Erro HTTP: {http_err}")
            return None

        except Exception as e:
            print(f"Erro ao transcrever áudio: {e}")
            return None