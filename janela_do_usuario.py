from usuario import Usuario
from lista_de_usuarios import ListaDeUsuarios
from servidor import Servidor
from interface_do_usuario import InterfaceDoUsuario
import socket
import tkinter
from tkinter import *

# Programa principal
def main():
  root = tkinter.Tk(screenName="Trabalho Redes II")
  janela = InterfaceDoUsuario(master=root)
  janela.mainloop()
  janela.desconecta()

# chamando programa principal
main()