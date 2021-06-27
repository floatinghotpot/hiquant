
class A:
  a = None
  callbacks = []
  def func(self, b):
    a = b
  def func2(self, a):
    a = a
  def func3(self, a):
    self.a = a

  def func4(self):
    print(self, 'hi')
  def func5(self):
    self.callbacks.append([self.func4, self])
  def func6(self):
    func, obj = self.callbacks[0]
    print(obj, func)
    func()

def test_class():
  x = A()
  x.func(1)
  print(x.a)

  x.func2(2)
  print(x.a)

  x.func3(3)
  print(x.a)

  x.func5()
  x.func6()

if __name__ == "__main__":
  test_class()
