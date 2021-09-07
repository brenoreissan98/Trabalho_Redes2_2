"""
Classe para tratar de uma lista de usuários
"""
class ListaDeUsuarios(list):
  def __init__(self):
    super().__init__([])

  def __str__(self):
    string_de_usuarios = ""
    for usuario in self:
      string_de_usuarios += "Usuário: {0.nome} IP: {0.ip} Porta: {0.porta}\n".format(usuario)
    return string_de_usuarios

  def adiciona_usuario(self, novo_usuario):
    self.append(novo_usuario)

  def remove_usuario(self, usuario_a_ser_removido):
    for usuario in self:
      if usuario == usuario_a_ser_removido:
        self.remove(usuario)
        break
        