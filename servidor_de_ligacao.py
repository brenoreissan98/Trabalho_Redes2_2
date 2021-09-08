from lista_de_usuarios import ListaDeUsuarios
import socket
import select
import pickle
import pyaudio

from usuario import Usuario

class ServidorDeLigacao:
  def __init__(self, ip, porta):
    self.FORMAT = pyaudio.paInt16
    self.CHANNELS = 1
    self.RATE = 44100
    self.CHUNK = 4096

    self.usuarios_conectados = ListaDeUsuarios() # Registro de usuários
    self.ip = ip
    self.porta = porta
    self.inicializa_servidor()

    self.usuario_em_ligacao = None

    self.recebendo_ligacao = False
    self.em_ligacao = False

  # Classe que inicializa o Socket com TCP, e com o IP e a PORTA
  def inicializa_servidor(self):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.socket.bind((self.ip, self.porta))
    self.socket.setblocking(0)
    self.read_list = [self.socket]

  # Função que será chamada dentro da interface do usuário em um loop infinito que fará o servidor sempre escutar novas conexões e mensagens
  def listen(self):
    try:
      recebido = self.socket.recvfrom(1024)
      mensagem = recebido[0]
      endereco_origem = recebido[1]
      print(f"from {endereco_origem[0]}:{endereco_origem[1]}")
      if mensagem:
        self.trata_mensagem(mensagem)
    except:
      pass
    """
    self.socket.listen(10)
    self.conexao, self.end_origem = self.socket.accept()
    with self.conexao:
      print(f"Conectado por: {self.end_origem}")
      while True:
        mensagem_recebida = self.conexao.recv(1024)
        if not mensagem_recebida:
          break
        self.trata_mensagem(mensagem_recebida)
    """

  # Função que, ao receber uma mensagem, o servidor verificará a operação que foi pedida e enviará os dados, se necessários, para a função que trata dessa operação
  def trata_mensagem(self, mensagem):
    mensagem = pickle.loads(mensagem)
    print(mensagem)
    if mensagem["operacao"] == "convite":
      self.trata_convite(mensagem["data"])
    elif mensagem["operacao"] == "resposta_ao_convite":
      self.trata_resposta(mensagem["data"])
    elif mensagem["operacao"] == "encerrar_ligacao":
      pass

  def trata_convite(self, usuario_ligando):
    print()
    self.usuario_ligando = usuario_ligando
    if not self.em_ligacao:
      self.recebendo_ligacao = True
    else:
      mensagem = {"operacao": "resposta_ao_convite", "data": False}
      self.envia_mensagem(mensagem, (self.usuario_ligando.ip, self.usuario_ligando.porta))

  # Envia uma mensagem para o usuário consultado
  def envia_mensagem(self, mensagem, endereco):
    self.socket.sendto(mensagem, endereco)

  def grava_audio_e_envia(self, in_data, frame_count, time_info, status):
    try:
      self.socket.sendto(in_data, (self.usuario_ligando.ip, self.usuario_ligando.porta))
    except:
      pass

  def trata_resposta(self, resposta):
    if resposta == True:
      self.em_ligacao = True
      self.recebendo_ligacao = False
      self.audio_input = pyaudio.PyAudio()
      self.stream_input = self.audio_input.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK, stream_callback=self.grava_audio_e_envia)
      self.audio_output = pyaudio.PyAudio()
      self.stream_output = self.audio_output.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, output=True, frames_per_buffer=self.CHUNK)
    else:
      self.recebendo_ligacao = False
      self.usuario_ligando = None

  def encerra_ligacao(self, deve_encerrar):
    if deve_encerrar:
      self.em_ligacao = False
      
      self.stream_input.stop_stream()
      self.stream_input.close()
      self.audio_input.terminate()

      self.stream_output.close()
      self.audio_output.terminate()

  # Registra um usuário novo, caso esse ainda não exista no servidor
  def conecta_um_usuario(self, nome_do_novo_usuario):
    for usuario in self.usuarios_conectados:
      if (usuario.nome == nome_do_novo_usuario):
        msg = pickle.dumps({"data": None})
        self.s.sendall(msg)
        return
    novo_usuario = Usuario(nome_do_novo_usuario, self.address[0], self.address[1])
    self.usuarios_conectados.append(novo_usuario)
    print(f"Conexão com novo usuário: {novo_usuario}")
    msg = pickle.dumps({"data": novo_usuario})
    self.s.sendall(msg)
  
  # Retira o cadastro de um usuário do registo de usuários
  def desconecta_um_usuario(self, usuario_a_excluir):
    usuario_a_excluir = self.busca_usuario_local(usuario_a_excluir)
    print(f"Excluindo: {usuario_a_excluir}")
    self.usuarios_conectados.remove_usuario(usuario_a_excluir)
    msg = pickle.dumps({"data": True})
    self.s.sendall(msg)
    self.s.close()
    self.read_list.remove(self.s)

  # Busca local auxiliar 
  def busca_usuario_local(self, nome):
    for usuario in self.usuarios_conectados:
      if nome == usuario.nome:
        return usuario
    return None

  # Busca um usuário pelo nome e retorna o usuário via socket
  def busca_usuario(self, nome):
    print(self.read_list)
    print(self.s)
    for usuario in self.usuarios_conectados:
      if nome == usuario.nome:
        msg = pickle.dumps({"data": usuario})
        self.s.sendall(msg)
        return
    msg = pickle.dumps({"data": None})
    self.s.sendall(msg)

  # Retorna a lista de usuários via socket
  def lista_usuarios_conectados(self):
    lista_de_usuarios = self.usuarios_conectados.copy()
    lista_de_usuarios = pickle.dumps({"data": lista_de_usuarios})
    self.s.sendall(lista_de_usuarios)