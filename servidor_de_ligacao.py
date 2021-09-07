from lista_de_usuarios import ListaDeUsuarios
import socket
import select
import pickle

from usuario import Usuario

class ServidorDeLigacao:
  def __init__(self):
    self.usuarios_conectados = ListaDeUsuarios() # Registro de usuários
    self.porta = 5000
    self.ip = "localhost"
    self.inicializa_servidor()

  # Classe que inicializa o Socket com TCP, e com o IP e a PORTA
  def inicializa_servidor(self):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.socket.bind((self.ip, self.porta))
    self.read_list = [self.socket]
    #self.server_socket.listen(10)

  # Função que será chamada em run_server em um loop infinito que fará o servidor sempre escutar novas conexões e mensagens
  def listen(self):
    self.socket.listen(10)
    print(f"Listening on {self.ip}:{self.porta}")
    while True:
      readable, writable, errored = select.select(self.read_list, [], [])
      for s in readable:
        self.s = s
        if s is self.socket:
          self.client_socket, self.address = self.socket.accept()
          self.read_list.append(self.client_socket)
          print("Connection from", self.address)
        else:
          data = s.recv(1024)
          if data:
            self.trata_mensagem(data)
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
    if mensagem["operacao"] == "criar":
      self.conecta_um_usuario(mensagem["data"])
    elif mensagem["operacao"] == "desconectar":
      self.desconecta_um_usuario(mensagem["data"])
    elif mensagem["operacao"] == "consultar":
      self.busca_usuario(mensagem["data"])
    elif mensagem["operacao"] == "listar":
      self.lista_usuarios_conectados()

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