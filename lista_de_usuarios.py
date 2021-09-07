"""
Classe para tratar de uma lista de usuários
"""
class ListaDeUsuarios(list):
  def __init__(self):
    super().__init__([])

  def __str__(self):
    string_de_usuarios = ""
    for usuario in self:
      string_de_usuarios += "Usuário: " + usuario.nome + " IP: " + usuario.ip + " Porta: " + str(usuario.porta) + "\n"
    return string_de_usuarios

  def adiciona_usuario(self, novo_usuario):
    self.append(novo_usuario)

  def remove_usuario(self, usuario_a_ser_removido):
    for usuario in self:
      if usuario.nome == usuario_a_ser_removido.nome and usuario.ip == usuario_a_ser_removido.ip and usuario.porta == usuario_a_ser_removido.porta:
        self.remove(usuario)