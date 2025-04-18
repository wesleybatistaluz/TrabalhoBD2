from config.db_config import DBConnectionHandler
from models.model import Orders, OrderDetails, Employees, Customers, Products
from sqlalchemy import func

def relatorio_pedido_completo(order_id: int):
    with DBConnectionHandler() as db:
        pedido = db.session.query(Orders).filter_by(orderid=order_id).first()

        if not pedido:
            print("Pedido não encontrado.")
            return

        print(f"\nPedido #{pedido.orderid}")
        print(f"Data: {pedido.orderdate}")
        print(f"Cliente: {pedido.customers.companyname}")
        print(f"Funcionário: {pedido.employees.firstname} {pedido.employees.lastname}")

        print("\nItens do Pedido:")
        for item in pedido.order_details:
            produto = db.session.query(Products).filter_by(productid=item.productid).first()
            print(f"- {produto.productname}: {item.quantity} x R${item.unitprice:.2f}")


def ranking_funcionarios(inicio: str, fim: str):
    with DBConnectionHandler() as db:
        print(f"\nRanking de Funcionários entre {inicio} e {fim}:")

        resultados = (
            db.session.query(
                Employees.firstname,
                Employees.lastname,
                func.count(Orders.orderid).label("total_pedidos"),
                func.sum(OrderDetails.unitprice * OrderDetails.quantity).label("total_vendido")
            )
            .join(Orders, Orders.employeeid == Employees.employeeid)
            .join(OrderDetails, OrderDetails.orderid == Orders.orderid)
            .filter(Orders.orderdate.between(inicio, fim))
            .group_by(Employees.employeeid)
            .order_by(func.count(Orders.orderid).desc())
            .all()
        )

        for i, (nome, sobrenome, total, vendido) in enumerate(resultados, start=1):
            print(f"{i}. {nome} {sobrenome} - {total} pedidos - R${vendido:.2f}")
