class Customer:
    def __init__(self, customerid=None, companyname=None, contactname=None):
        self.customerid = customerid
        self.companyname = companyname
        self.contactname = contactname

class Employee:
    def __init__(self, employeeid=None, firstname=None, lastname=None):
        self.employeeid = employeeid
        self.firstname = firstname
        self.lastname = lastname

class Product:
    def __init__(self, productid=None, productname=None, unitprice=None):
        self.productid = productid
        self.productname = productname
        self.unitprice = unitprice

class Order:
    def __init__(self, orderid=None, customerid=None, employeeid=None, orderdate=None):
        self.orderid = orderid
        self.customerid = customerid
        self.employeeid = employeeid
        self.orderdate = orderdate
        self.order_details = []  # Lista para armazenar os itens do pedido

class OrderDetail:
    def __init__(self, orderid=None, productid=None, unitprice=None, quantity=None, discount=None):
        self.orderid = orderid
        self.productid = productid
        self.unitprice = unitprice
        self.quantity = quantity
        self.discount = discount if discount is not None else 0