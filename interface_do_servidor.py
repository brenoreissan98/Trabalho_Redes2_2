import tkinter
from tkinter import *
from tkinter import font
from usuario import Usuario
from servidor import Servidor
import socket
import pickle
from lista_de_usuarios import ListaDeUsuarios

class InterfaceDoServidor(tkinter.Frame):
  def __init__(self, master=None):
    super().__init__(master)

    # Endereço do HOST
    self.ip_host = "127.0.0.1"
    self.porta_host = 5000

    # Inicializações da interface
    self.fonte = ("Verdana", "8")
    self.fonte_cabecalho = ("Verdana", "12")
    self.fonte_titulo = ("Verdana", "20")
    self.master = master
    self.pack()

    self.linhas_da_tabela = []
    self.width_da_tabela = 15
    # Botão de atualizar
    self.titulo = Label(self.master, text="SERVIDOR" ,font=self.fonte_titulo)
    self.titulo.pack(side=TOP)
    self.botao_teste = Button(self.master, text="ATUALIZAR" ,font=self.fonte, fg="blue", bg="white", command=self.atualiza_lista_de_usuarios)
    self.botao_teste.pack(side=TOP)

    self.lista_de_usuarios_conectados()

  def listen(self):
    self.servidor.listen()

  # Inicializa a tabela de usuários conectados
  def lista_de_usuarios_conectados(self):
    self.frame_da_tabela_de_usuarios_conectados = Frame(self.master, borderwidth=3)
    self.frame_da_tabela_de_usuarios_conectados.pack()
    self.cabecalho_da_tabela_de_usuarios()
    self.linhas_da_tabela_de_usuarios()

  # Cria um cabeçalho para a lista de usuários
  def cabecalho_da_tabela_de_usuarios(self):
    self.frame_do_cabecalho = Frame(self.frame_da_tabela_de_usuarios_conectados)
    self.frame_do_cabecalho.pack()
    self.coluna_de_nome = Label(self.frame_do_cabecalho, text="NOME", font=self.fonte, width=self.width_da_tabela-5)
    self.coluna_de_nome.pack(side=LEFT)
    self.coluna_de_ip = Label(self.frame_do_cabecalho, text="IP", font=self.fonte, width=self.width_da_tabela-5)
    self.coluna_de_ip.pack(side=LEFT)
    self.coluna_de_porta = Label(self.frame_do_cabecalho, text="PORTA", font=self.fonte, width=self.width_da_tabela-5)
    self.coluna_de_porta.pack(side=LEFT)

  def linhas_da_tabela_de_usuarios(self):
    self.frame_da_linha = Frame(self.frame_da_tabela_de_usuarios_conectados)
    self.frame_da_linha.pack()
  
  """
  Função executada após clicar no botão de atualizar a lista de usuário
  manda uma mensagem para o servidor requisitando a lista de usuários conectador
  """
  def atualiza_lista_de_usuarios(self):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
      s.connect((self.ip_host, self.porta_host))
      mensagem = pickle.dumps({"operacao": "listar"})
      s.sendall(mensagem)
      data = s.recv(1024)
      usuarios_conectados = pickle.loads(data)
      #print(usuarios_conectados)
      self.destroi_tabela_de_usuarios()
      for usuario in usuarios_conectados["data"]:
        self.cria_linha_da_tabela(usuario)

  # Recebe um usuário e cria uma linha para na tabela para esse.
  def cria_linha_da_tabela(self, usuario):
    frame = Frame(self.frame_da_tabela_de_usuarios_conectados)
    frame.pack(side=TOP)
    nome = Label(frame, text=usuario.nome, font=self.fonte, width=self.width_da_tabela)
    nome.pack(side=LEFT)
    ip = Label(frame, text=usuario.ip, font=self.fonte, width=self.width_da_tabela)
    ip.pack(side=LEFT)
    porta = Label(frame, text=usuario.porta, font=self.fonte, width=self.width_da_tabela)
    porta.pack(side=LEFT)

    self.linhas_da_tabela.append(
      {
        "frame": frame,
        "nome": nome,
        "ip": ip,
        "porta": porta
      }
    )

  # Destrói toda a tabela de usuários
  def destroi_tabela_de_usuarios(self):
    for linha in self.linhas_da_tabela:
      linha["frame"].destroy()
    self.linhas_da_tabela.clear()
