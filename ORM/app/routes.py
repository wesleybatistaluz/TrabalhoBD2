from flask import Blueprint, request, jsonify
from controllers.controller import OrderController
from models.model import Orders, OrderDetails
import datetime

routes = Blueprint("routes", __name__)
controller = OrderController()

@routes.route("/api/pedidos", methods=["POST"])
def criar_pedido():
    try:
        data = request.get_json()

        pedido = Orders(
            customerid=data["customer_id"],
            employeeid=data["employee_id"],
            orderdate=datetime.datetime.strptime(data["order_date"], "%Y-%m-%d")
        )

        detalhes = []
        for item in data["items"]:
            detalhe = OrderDetails(
                productid=item["product_id"],
                quantity=item["quantity"],
                unitprice=item["unit_price"],
                discount=0
            )
            detalhes.append(detalhe)

        sucesso = controller.criar_pedido(pedido, detalhes)
        if sucesso:
            return jsonify({"mensagem": "Pedido criado com sucesso!"}), 201
        else:
            return jsonify({"erro": "Falha ao criar pedido"}), 400

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
