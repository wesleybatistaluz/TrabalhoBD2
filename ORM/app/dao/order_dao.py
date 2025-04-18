from typing import List
from config.db_config import DBConnectionHandler
from models.model import Orders, OrderDetails

class OrderDAO:
    def inserir_pedido(self, pedido: Orders, detalhes: List[OrderDetails]) -> bool:
        try:
            with DBConnectionHandler() as db:
                last_id = db.session.query(Orders.orderid).order_by(Orders.orderid.desc()).first()
                if last_id:
                    next_id = (last_id[0] + 1)
                pedido.orderid = next_id
                db.session.add(pedido)
                db.session.flush()

                for detalhe in detalhes:
                    detalhe.orderid = pedido.orderid
                    db.session.add(detalhe)

                db.session.commit()
                return True
        except Exception as e:
            print(f"Erro ao inserir pedido: {e}")
            return False

