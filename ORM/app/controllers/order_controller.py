
from models.model import Orders, OrderDetails, Customers, Employees, Products
from dao.order_dao import OrderDAO
from config.db_config import DBConnectionHandler

class OrderController:

    def criar_pedido(self, pedido: Orders, detalhes: list[OrderDetails]) -> bool:
        with DBConnectionHandler() as db:
            customer = db.session.query(Customers).filter_by(customerid=pedido.customerid).first()
            if not customer:
                print(f"Cliente com ID {pedido.customerid} não encontrado.")
                return False

            employee = db.session.query(Employees).filter_by(employeeid=pedido.employeeid).first()
            if not employee:
                print(f"Funcionário com ID {pedido.employeeid} não encontrado.")
                return False

            for detalhe in detalhes:
                product = db.session.query(Products).filter_by(productid=detalhe.productid).first()
                if not product:
                    print(f"Produto com ID {detalhe.productid} não encontrado.")
                    return False
                detalhe.unitprice = product.unitprice

        dao = OrderDAO()
        sucesso = dao.inserir_pedido(pedido, detalhes)
        return sucesso
