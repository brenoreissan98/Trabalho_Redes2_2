from usuario import Usuario
from lista_de_usuarios import ListaDeUsuarios
from interface_do_servidor import InterfaceDoServidor
from servidor import Servidor
import socket
import tkinter
from tkinter import *
import multiprocessing

#Programa principal
def main():
  root = tkinter.Tk(screenName="Servidor")
  janela = InterfaceDoServidor(master=root)
  janela.mainloop()

# chamando programa principal
main()