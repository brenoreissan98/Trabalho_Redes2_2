from lista_de_usuarios import ListaDeUsuarios
import socket
import select
import pickle
import pyaudio

from usuario import Usuario

class ServidorDeLigacao:
  def __init__(self, ip, porta):
    # Variáveis para o PyAudio processar e enviar o audio
    self.FORMAT = pyaudio.paInt16
    self.CHANNELS = 1
    self.RATE = 44100
    self.CHUNK = 8192

    self.ip = ip
    self.porta = porta
    self.inicializa_servidor()

    # variáveis auxiliares para controlar os estados do servidor de ligação
    self.usuario_em_ligacao = None
    self.recebendo_ligacao = False
    self.em_ligacao = False
    self.tratando_ligacao = False

  # Classe que inicializa o Socket UDP com o IP e a PORTA enviados no contrutor
  def inicializa_servidor(self):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.socket.bind((self.ip, self.porta))
    self.socket.setblocking(0)
    self.read_list = [self.socket]

  # Função que será chamada dentro da interface do usuário em um loop infinito que fará o servidor sempre escutar novas e mensagens
  def listen(self):
    try:
      recebido = self.socket.recvfrom(16384)
      mensagem = recebido[0]
      endereco_origem = recebido[1]

      """
      Caso o usuário esteja em uma ligação, então ele terá uma instancia de stream_output
      que será responsável por decodificar o audio e transformar em voz, então é necessário enviar
      a mensagem recebida pelo socket para ele
      """
      if self.em_ligacao:
        self.stream_output.write(mensagem)
      # Caso seja um objeto do tipo dict, então é uma mensagem com o padrão de mensagem estabelecido e deve ser tratado
      if isinstance(pickle.loads(mensagem), dict):
        self.trata_mensagem(mensagem)
    except Exception as e:
      pass

  # Função que ao receber uma mensagem verificará a operação que foi pedida e enviará os dados, se necessários, para a função que trata dessa operação
  def trata_mensagem(self, mensagem):
    mensagem = pickle.loads(mensagem)
    print(mensagem)
    if mensagem["operacao"] == "convite":
      self.trata_convite(mensagem["data"])
    elif mensagem["operacao"] == "resposta_ao_convite":
      self.trata_resposta(mensagem["data"])
    elif mensagem["operacao"] == "encerrar_ligacao":
      self.encerra_ligacao(mensagem["data"])

  # trata um convite de ligação recebido recebido
  def trata_convite(self, usuario_ligando):
    print(f"Recebendo ligação de {usuario_ligando.nome}")
    if not self.em_ligacao and not self.recebendo_ligacao:
      self.recebendo_ligacao = True
      self.tratando_ligacao = True
      self.usuario_destino = usuario_ligando # Guarda qual é o usuário que está ligando
    else:
      print(f"OCUPADO")
      mensagem = {"operacao": "resposta_ao_convite", "data": False}
      self.envia_mensagem(pickle.dumps(mensagem), (usuario_ligando.ip, usuario_ligando.porta))

  # Envia uma mensagem para o usuário consultado
  def envia_mensagem(self, mensagem, endereco):
    self.socket.sendto(mensagem, endereco)

  # função auxiliar que fará o PyAudio enviar a voz para o usuário de destino
  def grava_audio_e_envia(self, in_data, frame_count, time_info, status):
    try:
      #print(f"Enviando audio para {self.usuario_destino.nome} ip: {self.usuario_destino.ip} porta: {self.usuario_destino.porta}")
      #print(in_data)
      self.envia_mensagem(in_data, (self.usuario_destino.ip, self.usuario_destino.porta))
      return (None, pyaudio.paContinue)
    except:
      pass

  """
  Trata da resposta de um usuário
  se o usuário aceitar da interface do usuário, deve-se utilizar a flag de "enviar_resposta" para poder mandar uma mensagem
  para o usuário de origem que a ligação foi aceita.
  Quando um usuário de origem receber a mensagem de aceitação como resposta, ela não terá o flag para aceitar a resposta,
  somente criará e estabelecerá a chamada de voz
  """
  def trata_resposta(self, resposta, enviar_resposta=False):
    if resposta == True:
      if enviar_resposta:
        mensagem = {"operacao": "resposta_ao_convite", "data":True}
        self.envia_mensagem(pickle.dumps(mensagem), (self.usuario_destino.ip, self.usuario_destino.porta))

      print(f"Em ligação com {self.usuario_destino.nome}")
      self.em_ligacao = True
      self.recebendo_ligacao = False
      self.tratando_ligacao = False
      self.audio_input = pyaudio.PyAudio()
      self.stream_input = self.audio_input.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK, stream_callback=self.grava_audio_e_envia)
      self.audio_output = pyaudio.PyAudio()
      self.stream_output = self.audio_output.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, output=True, frames_per_buffer=self.CHUNK)
    else:
      if enviar_resposta:
        mensagem = {"operacao": "resposta_ao_convite", "data":False}
        self.envia_mensagem(pickle.dumps(mensagem), (self.usuario_destino.ip, self.usuario_destino.porta))

      print(f"ligação de {self.usuario_destino.nome} recusada")
      self.recebendo_ligacao = False
      self.usuario_destino = None
      self.tratando_ligacao = False

  # Encerra a ligação em andamento
  def encerra_ligacao(self, deve_encerrar):
    if deve_encerrar:
      print(f"Encerrando ligação")
      self.em_ligacao = False
      
      self.stream_input.stop_stream()
      self.stream_input.close()
      self.audio_input.terminate()

      self.stream_output.close()
      self.audio_output.terminate()

  def liga_para_usuario(self, usuario_ligando, usuario_a_ligar):
    print(f"Ligando para {usuario_a_ligar.nome}")
    self.usuario_destino = usuario_a_ligar

    self.tratando_ligacao = True

    endereco = (usuario_a_ligar.ip, usuario_a_ligar.porta)
    mensagem = {"operacao":"convite", "data": usuario_ligando}
    self.envia_mensagem(pickle.dumps(mensagem), endereco)
    self.tratando_ligacao = True
