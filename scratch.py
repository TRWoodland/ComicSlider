class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def future_age(self):
        calc = Calculator(*args)
        print(calc.future_age(self.age, self.age))

class Calculator:
    def __init__(self, numberone, numbertwo):
        self.numberone = numberone
        self.numbertwo = numbertwo

    def future_age(self, numberone, numbertwo):
        return self.numberone * self.numbertwo
