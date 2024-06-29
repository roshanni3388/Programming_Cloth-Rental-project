class test:
    def __init__(self,first,last,salary):
        self.first=first
        self.last=last
        self.salary=salary

    def calculate_salary(self,basic):
        total_pay=0
        total_pay = basic -.3*basic
        return total_pay
t1=test('roshani','naik',50000)
t1.calculate_salary(50000)