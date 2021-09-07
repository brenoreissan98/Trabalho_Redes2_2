"""
Classe que denota um tipo usuário
"""
class Usuario:
  def __init__(self, nome, ip, porta):
    self.nome = nome
    self.ip = ip
    self.porta = porta

  def __str__(self):
    return f"nome: {self.nome}, ip: {self.ip}, porta: {self.porta}"
  
  def dicionario(self):
    return {"nome":self.nome, "ip":self.ip, "porta":self.porta}
