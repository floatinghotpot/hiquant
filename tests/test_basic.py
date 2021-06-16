
class A:
  a = None
  def func(self, b):
    a = b
  def func2(self, a):
    a = a
  def func3(self, a):
    self.a = a

def test_class():
  x = A()
  x.func(1)
  print(x.a)

  x.func2(2)
  print(x.a)

  x.func3(3)
  print(x.a)
