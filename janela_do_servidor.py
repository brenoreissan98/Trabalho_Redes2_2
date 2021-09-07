from usuario import Usuario
from lista_de_usuarios import ListaDeUsuarios
from interface_do_servidor import InterfaceDoServidor
from servidor import Servidor
import tkinter
from tkinter import *
import time

#Programa principal
def main():
  root = tkinter.Tk(screenName="Servidor")
  janela = InterfaceDoServidor(master=root)

  while True:
    janela.update()
    janela.update_idletasks()
    janela.atualiza_lista_de_usuarios()
    time.sleep(1)

# chamando programa principal
main()