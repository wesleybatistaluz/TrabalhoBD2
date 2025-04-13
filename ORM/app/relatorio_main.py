#teste
from reports import relatorio_pedido_completo, ranking_funcionarios

print("1 - Relatório de pedido")
print("2 - Ranking de funcionários")
op = input("Escolha: ")

if op == "1":
    id_pedido = int(input("Digite o ID do pedido: "))
    relatorio_pedido_completo(id_pedido)
elif op == "2":
    inicio = input("Data inicial (YYYY-MM-DD): ")
    fim = input("Data final (YYYY-MM-DD): ")
    ranking_funcionarios(inicio, fim)
