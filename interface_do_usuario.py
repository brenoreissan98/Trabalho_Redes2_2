import tkinter
from tkinter import *
from tkinter import font
from usuario import Usuario
from servidor import Servidor
import socket
import pickle
import selectors
import types
from servidor_de_ligacao import ServidorDeLigacao

sel = selectors.DefaultSelector()

class InterfaceDoUsuario(tkinter.Frame):
  def __init__(self, master=None):

    self.em_ligacao = False
    self.servidor_de_ligacao = None

    self.tratando_ligacao = False

    self.ligando = False

    super().__init__(master)
    self.fonte = ("Verdana", "8")
    self.master = master
    self.pack()

    self.ip_host = "localhost"
    self.porta_host = 5000

    self.conectado = False
    self.mostrando_consulta = False # variável auxiliar para saber se o frame de consulta está sendo mostrado

    self.cria_container_do_form_do_usuario()

  # Cria o frame e inicializa o formulário de conexão de um cliente
  def cria_container_do_form_do_usuario(self):
    self.container_do_formulario = Frame(self.master)
    self.container_do_formulario.pack()

    self.container_nome_usuario = Frame(self.container_do_formulario)
    self.container_nome_usuario.pack()
    self.label_nome_usuario = Label(self.container_nome_usuario, text="Nome", font=self.fonte)
    self.label_nome_usuario.pack(side=LEFT)
    self.formulario_nome_usuario = Entry(self.container_nome_usuario)
    self.formulario_nome_usuario["font"] = self.fonte
    self.formulario_nome_usuario.pack(side=LEFT)

    self.container_botao_submit = Frame(self.container_do_formulario)
    self.container_botao_submit.pack()
    self.botar_de_submeter_form = Button(self.container_botao_submit, text="CONECTAR", fg="white", bg="green" , command=self.conectar_usuario)
    self.botar_de_submeter_form.pack(side=BOTTOM)

  """
  Ao clicar em conectar, essa função executará e mandará uma mensagem ao servidor para estabelecer uma nova conexão.
  Após a conexão ser bem sucedida, o fomulário será destruído e o frame de usuário conectado, formulário de busca é criado e o botão de desconectar
  """
  def conectar_usuario(self):
    self.nome = self.formulario_nome_usuario.get()
    if (self.nome == ""):
      return

    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.connect((self.ip_host, self.porta_host))
    mensagem = pickle.dumps({"operacao": "criar", "data": self.nome})
    self.socket.sendall(mensagem)
    data = self.socket.recv(1024)
    usuario = pickle.loads(data)["data"]
    if usuario:
      self.usuario_conectado = usuario
      self.ip = usuario.ip
      self.porta = usuario.porta

      self.servidor_de_ligacao = ServidorDeLigacao(self.ip, self.porta)

      self.label_nome_usuario["fg"] = "black"

      self.cria_label_para_usuario_conectado()
      self.container_do_formulario.destroy()
      self.cria_formulario_de_consulta_de_usuario()
      self.cria_botao_de_desconectar()
    else:
      self.label_nome_usuario["fg"] = "red"

  # Cria label para o usuário conectado
  def cria_label_para_usuario_conectado(self):
    self.container_para_label_do_nome_do_usuario_conectado = Frame(self.master)
    self.container_para_label_do_nome_do_usuario_conectado.pack(side=TOP)
    self.label_nome_do_usuario_conectado = Label(self.container_para_label_do_nome_do_usuario_conectado, text=f"BEM VINDO!\n {self.nome} ({self.ip}:{self.porta}))")
    self.label_nome_do_usuario_conectado.pack(side=TOP)

  # Cria formulário para consulta de usuário
  def cria_formulario_de_consulta_de_usuario(self):
    self.container_do_formulario_de_consulta_de_usuario = Frame(self.master)
    self.container_do_formulario_de_consulta_de_usuario.pack(side=BOTTOM)
    self.label_formulario_de_consulta = Label(self.container_do_formulario_de_consulta_de_usuario, text="Consulta: ", font=self.fonte)
    self.label_formulario_de_consulta.pack(side=LEFT)
    self.formulario_de_consulta = Entry(self.container_do_formulario_de_consulta_de_usuario)
    self.formulario_de_consulta.pack(side=LEFT)
    self.botao_de_consultar = Button(self.container_do_formulario_de_consulta_de_usuario, text="CONSULTAR", bg="blue", fg="white", font=self.fonte, command=self.cria_tela_de_usuario_consultado)
    self.botao_de_consultar.pack(side=LEFT)

  # Checa e atualiza todas as variáveis do servidor de ligação
  def atualiza_servidor_de_ligacao(self):
    self.servidor_de_ligacao.listen()

    if self.servidor_de_ligacao.recebendo_ligacao and not self.servidor_de_ligacao.em_ligacao and not self.tratando_ligacao:
      self.tratando_ligacao = True
      self.cria_botoes_de_tratar_ligacao()

    if self.ligando and not self.tratando_ligacao:
      self.ligando = False
      self.destroi_botao_desligar_ligacao()
      self.cria_botao_de_ligar()

  # Cria os botoes quando estiver recebendo uma ligacao
  def cria_botoes_de_tratar_ligacao(self):
    if self.mostrando_consulta:
      self.container_botao_de_ligar.destroy()
      self.botao_de_ligar.destroy()

    usuario_ligando = self.servidor_de_ligacao.usuario_destino

    self.container_tratar_ligacao = Frame(self.master)
    self.container_tratar_ligacao.pack(side=BOTTOM)
    self.usuario_ligando_label = Label(self.container_tratar_ligacao, text=f"Recebendo ligação de : {usuario_ligando.nome}")
    self.usuario_ligando_label.pack(side=TOP)
    self.botao_de_aceitar_ligacao = Button(self.container_tratar_ligacao, text="ACEITAR", fg="white", bg="green", command=self.aceitar_ligacao)
    self.botao_de_aceitar_ligacao.pack(side=LEFT)
    self.botao_de_recusar_ligacao = Button(self.container_tratar_ligacao, text="RECUSAR", fg="white", bg="red", command=self.recusar_ligacao)
    self.botao_de_recusar_ligacao.pack(side=LEFT)

  # Aceita uma ligação
  def aceitar_ligacao(self):
    self.tratando_ligacao = False

    self.destroi_botoes_de_tratar_ligacao()
    self.cria_botao_de_encerrar_ligacao()
    """
    mensagem = {"operacao": "resposta_ao_convite", "data":True}
    self.servidor_de_ligacao.envia_mensagem(pickle.dumps(mensagem), (self.usuario_consultado.ip, self.usuario_consultado.porta))
    """
    self.servidor_de_ligacao.trata_resposta(True)

  def cria_botao_de_encerrar_ligacao(self):
    self.container_botao_encerrar_ligacao = Frame(self.master)
    self.container_botao_encerrar_ligacao.pack(side=BOTTOM)
    self.botao_encerrar_ligacao = Button(self.container_botao_encerrar_ligacao, text="ENCERRAR", fg="white", bg="red", command=self.encerra_ligacao)
    self.botao_encerrar_ligacao.pack(side=BOTTOM)

  def encerra_ligacao(self):
    self.container_botao_encerrar_ligacao.destroy()
    self.botao_encerrar_ligacao.destroy()

    mensagem = {"operacao": "encerrar_ligacao", "data": None}
    self.servidor_de_ligacao.envia_mensagem(pickle.dumps(mensagem), (self.usuario_consultado.ip, self.usuario_consultado.porta))

  # Recusa uma Ligação
  def recusar_ligacao(self):
    self.tratando_ligacao = False
    self.destroi_botoes_de_tratar_ligacao()
    self.cria_botao_de_ligar()

    """
    mensagem = {"operacao": "resposta_ao_convite", "data":False}
    self.servidor_de_ligacao.envia_mensagem(pickle.dumps(mensagem), (self.usuario_consultado.ip, self.usuario_consultado.porta))
    """

    self.servidor_de_ligacao.trata_resposta(False)

    print("Recusei")

  # Destroi os botões de tratar ligação
  def destroi_botoes_de_tratar_ligacao(self):
    self.container_tratar_ligacao.destroy()
    self.botao_de_aceitar_ligacao.destroy()
    self.botao_de_recusar_ligacao.destroy()

  """
  Ao clicar em consultar um usuário é enviada uma mensagem para o servidor para consultar um usuário.
  Se o servidor retornar um usuário, é mostrado uma tela para mostrar a consulta
  """
  def cria_tela_de_usuario_consultado(self):

    self.nome_consultado = self.formulario_de_consulta.get()

    mensagem = pickle.dumps({"operacao": "consultar", "data": self.nome_consultado})
    self.socket.sendall(mensagem)
    data = self.socket.recv(1024)
    usuario_consultado = pickle.loads(data)["data"]
    self.usuario_consultado = usuario_consultado

    print(f"Consultado usuário: {usuario_consultado}")

    if self.mostrando_consulta:
      self.container_tela_de_usuario_consultado.destroy()
      self.label_usuario_consultado.destroy()
      self.container_botao_de_ligar.destroy()
      self.botao_de_ligar.destroy()

    if not self.tratando_ligacao:
      self.cria_botao_de_ligar()
    self.container_tela_de_usuario_consultado = Frame(self.master)
    self.container_tela_de_usuario_consultado.pack(side=TOP)
    self.label_usuario_consultado = Label(self.container_tela_de_usuario_consultado, text=f"NOME: {usuario_consultado.nome}\nIP: {usuario_consultado.ip}\nPORTA: {usuario_consultado.porta}")
    self.label_usuario_consultado.pack(side=BOTTOM)
    self.mostrando_consulta = True

  # Cria o botão de desconectar
  def cria_botao_de_desconectar(self):
    self.container_do_botao_de_desconectar = Frame(self.master)
    self.container_do_botao_de_desconectar.pack(side=TOP)
    self.botao_de_desconectar = Button(self.container_do_botao_de_desconectar, text="DESCONECTAR", fg="white", bg="red", command=self.desconecta)
    self.botao_de_desconectar.pack(side=TOP)

  def cria_botao_de_ligar(self):
    self.container_botao_de_ligar = Frame(self.master)
    self.container_botao_de_ligar.pack(side=BOTTOM)
    self.botao_de_ligar = Button(self.container_do_botao_de_desconectar, text="LIGAR", fg="white", bg="green", command=self.ligar)
    self.botao_de_ligar.pack(side=BOTTOM)

  def destroi_botao_de_ligar(self):
    self.container_botao_de_ligar.destroy()
    self.botao_de_ligar.destroy()

  def ligar(self):
    self.ligando = True
    self.tratando_ligacao = True
    self.destroi_botao_de_ligar()

    """
    mensagem = {"operacao": "convite", "data": self.usuario_consultado}
    self.servidor_de_ligacao.envia_mensagem(pickle.dumps(mensagem), (self.usuario_consultado.ip, self.usuario_consultado.porta))
    """
    
    self.servidor_de_ligacao.liga_para_usuario(self.usuario_conectado, self.usuario_consultado)
    self.cria_botao_desligar_ligacao()

  def cria_botao_desligar_ligacao(self):
    self.container_botao_de_desligar = Frame(self.master)
    self.container_botao_de_desligar.pack(side=BOTTOM)
    self.botao_de_desligar = Button(self.container_botao_de_desligar, text="DESISTIR DA LIGAÇÃO", fg="white", bg="red", command=self.desligar_ligacao)
    self.botao_de_desligar.pack(side=BOTTOM)

  def destroi_botao_desligar_ligacao(self):
    self.container_botao_de_desligar.destroy()
    self.botao_de_desligar.destroy()

  def desligar_ligacao(self):
    self.ligando = False
    self.tratando_ligacao = False
    mensagem = {"operacao": "resposta_ao_convite", "data": False}
    endereco = (self.usuario_consultado.ip, self.usuario_consultado.porta)
    self.servidor_de_ligacao.envia_mensagem(mensagem, endereco)
    self.destroi_botao_desligar_ligacao()
    self.cria_botao_de_ligar()

  """
  Manda uma mensagem de desconexão para o servidor.
  Em caso de sucesso, todas as janelas para o usuário conectado são destruídas e o formulário de conexão é criado novamente
  """
  def desconecta(self):
    mensagem = pickle.dumps({"operacao": "desconectar", "data": self.nome})
    self.socket.sendall(mensagem)
    data = self.socket.recv(1024)
    resultado = pickle.loads(data)["data"]

    if (resultado):
      self.container_para_label_do_nome_do_usuario_conectado.destroy()
      self.container_do_formulario_de_consulta_de_usuario.destroy()
      self.container_do_botao_de_desconectar.destroy()
      self.cria_container_do_form_do_usuario()

      if self.mostrando_consulta:
        self.container_tela_de_usuario_consultado.destroy()
        self.label_usuario_consultado.destroy()

      self.nome = ""
      self.ip = ""
      self.porta = ""

      self.socket.close()
      