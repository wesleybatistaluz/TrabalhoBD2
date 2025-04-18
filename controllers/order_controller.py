from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file
from dao.dao_psycopg import OrderDAOPsycopg
from models.models import Order, OrderDetail
from datetime import date
import csv
import os
import time
from pathlib import Path


# Instancia os DAOs corretamente
psycopg_dao = OrderDAOPsycopg()

order_bp = Blueprint('orders', __name__, url_prefix='/orders')

# Instancia o DAO
dao = OrderDAOPsycopg()

# Diretório para salvar os arquivos CSV
CSV_DIRECTORY = Path('reports/csv')
# Criar diretório se não existir
os.makedirs(CSV_DIRECTORY, exist_ok=True)

@order_bp.route('/new', methods=['GET'])
def new_order_form():
    """Exibe o formulário para novo pedido."""
    return render_template('new_order.html')

@order_bp.route('/search_customer', methods=['GET'])
def search_customer():
    """Busca clientes pelo nome."""
    name = request.args.get('name', '')
    safe = request.args.get('safe', 'true') == 'true'
    
    try:
        if safe:
            # Versão segura
            customers = dao.get_customer_by_name(name)
        else:
            # Versão vulnerável a SQL Injection
            customers = dao.get_customer_by_name_unsafe(name)
        
        return jsonify({'success': True, 'customers': customers})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@order_bp.route('/search_employee', methods=['GET'])
def search_employee():
    """Busca funcionários pelo nome."""
    name = request.args.get('name', '')
    safe = request.args.get('safe', 'true') == 'true'
    
    try:
        if safe:
            # Versão segura
            employees = dao.get_employee_by_name(name)
        else:
            # Versão vulnerável a SQL Injection
            employees = dao.get_employee_by_name_unsafe(name)
        
        return jsonify({'success': True, 'employees': employees})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@order_bp.route('/search_product', methods=['GET'])
def search_product():
    """Busca produtos pelo nome."""
    name = request.args.get('name', '')
    safe = request.args.get('safe', 'true') == 'true'
    
    try:
        if safe:
            # Versão segura
            products = dao.get_product_by_name(name)
        else:
            # Versão vulnerável a SQL Injection
            products = dao.get_product_by_name_unsafe(name)
        
        return jsonify({'success': True, 'products': products})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@order_bp.route('/create', methods=['POST'])
def create_order():
    """Cria um novo pedido."""
    try:
        # Obtém os dados do pedido do formulário
        customer_id = request.form.get('customer_id')
        employee_id = request.form.get('employee_id')
        order_date = request.form.get('order_date', date.today().isoformat())
        
        # Cria o objeto do pedido
        new_order = Order(
            customerid=customer_id,
            employeeid=employee_id, 
            orderdate=order_date
        )
        
        # Processa os itens do pedido
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('price[]')
        
        # Adiciona os itens do pedido
        for i in range(len(product_ids)):
            item = OrderDetail(
                productid=product_ids[i],
                quantity=quantities[i],
                unitprice=prices[i],
                discount=0  # Valor padrão para desconto
            )
            new_order.order_details.append(item)
        
        # Determina o método de inserção baseado nos parâmetros
        safe_mode = request.form.get('safe_mode', 'true') == 'true'
        
        # Usar Psycopg2
        if safe_mode:
            order_id = dao.create_order_safe(new_order)
        else:
            order_id = dao.create_order_unsafe(new_order)
        
        return jsonify({
            'success': True, 
            'message': f'Pedido {order_id} criado com sucesso!',
            'order_id': order_id
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@order_bp.route('/view/<int:order_id>', methods=['GET'])
def view_order(order_id):
    """Exibe detalhes completos de um pedido."""
    # Determina se deve usar o método seguro ou não
    safe_mode = request.args.get('safe', 'true') == 'true'
    
    try:
        if safe_mode:
            order_details = dao.get_order_details(order_id)
        else:
            order_details = dao.get_order_details_unsafe(order_id)
        
        if not order_details:
            flash('Pedido não encontrado!', 'danger')
            return redirect(url_for('index'))
            
        return render_template('view_order.html', 
                               order_info=order_details['order_info'], 
                               order_items=order_details['order_items'])
    except Exception as e:
        flash(f'Erro ao buscar detalhes do pedido: {str(e)}', 'danger')
        return redirect(url_for('index'))

@order_bp.route('/ranking', methods=['GET', 'POST'])
def employee_ranking_view():
    """Gera ranking de funcionários por vendas em formato CSV."""
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        safe_mode = request.form.get('safe_mode', 'true') == 'true'
        
        try:
            # Obtém o ranking
            if safe_mode:
                ranking = dao.get_employee_ranking(start_date, end_date)
            else:
                ranking = dao.get_employee_ranking_unsafe(start_date, end_date)
            
            # Verificar se o ranking está vazio
            if not ranking:
                flash('Nenhum dado encontrado para o período selecionado', 'warning')
                return render_template('employee_ranking_form.html')
            
            # Debug: imprimir informações sobre o ranking
            print(f"Dados do ranking: {ranking}")
            
            # Gera um nome de arquivo único baseado no timestamp
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"employee_ranking_{timestamp}.csv"
            filepath = CSV_DIRECTORY / filename
            
            # Escreve os dados no arquivo CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                csvwriter = csv.writer(csvfile)
                # Escreve o cabeçalho
                csvwriter.writerow(['ID', 'Nome', 'Total de Pedidos', 'Total de Vendas'])
                # Escreve os dados
                for employee in ranking:
                    # Acessa os valores como índices da tupla, não como dicionário
                    # Estrutura da tupla: (employeeid, employee_name, total_orders, total_sales)
                    csvwriter.writerow([
                        employee[0],  # employeeid
                        employee[1],  # employee_name
                        employee[2],  # total_orders
                        employee[3]   # total_sales
                    ])
            
            flash(f'Relatório CSV gerado com sucesso: {filename}', 'success')
            
            # Opção: retornar o arquivo para download
            return send_file(filepath, as_attachment=True, download_name=filename)
            
        except Exception as e:
            flash(f'Erro ao gerar ranking CSV: {str(e)}', 'danger')
            print(f"Erro detalhado: {e}")
    
    # Para requisições GET, apenas mostra o formulário de datas
    return render_template('employee_ranking_form.html')

@order_bp.route('/list', methods=['GET'])
def list_orders():
    """Lista todos os pedidos."""
    safe_mode = request.args.get('safe', 'true') == 'true'
    
    try:
        # Adicione um método ao DAO para listar pedidos
        if safe_mode:
            orders = dao.list_orders()
        else:
            orders = dao.list_orders_unsafe()
            
        return render_template('order_list.html', orders=orders)
    except Exception as e:
        flash(f'Erro ao listar pedidos: {str(e)}', 'danger')
        return redirect(url_for('index'))
    
@order_bp.route('/report/order/<int:order_id>')
def order_report(order_id):
    """Relatório com informações detalhadas de um pedido."""
    safe = request.args.get('safe', 'true') == 'true'
    
    try:
        order_data = psycopg_dao.get_order_details(order_id)
        if not order_data:
            return render_template('order_not_found.html', order_id=order_id)
            
        return render_template('order_report.html', order=order_data)
    except Exception as e:
        return render_template('error.html', error=str(e))

@order_bp.route('/report/employees', methods=['GET', 'POST'])
def employee_report():
    """Gera relatório CSV de ranking de funcionários por vendas."""
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        safe = request.form.get('safe', 'true') == 'true'
        
        try:
            # Busca os dados
            if safe:
                ranking = psycopg_dao.get_employee_sales_ranking(start_date, end_date)
            else:
                ranking = psycopg_dao.get_employee_sales_ranking_unsafe(start_date, end_date)
            
            # Verificar se o ranking está vazio
            if not ranking:
                flash('Nenhum dado encontrado para o período selecionado', 'warning')
                return render_template('employee_ranking_form.html')
                
            # Debug: imprimir informações sobre o ranking
            print(f"Dados do ranking: {ranking}")
            
            # Gera nome de arquivo com timestamp
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"employee_sales_report_{timestamp}.csv"
            filepath = CSV_DIRECTORY / filename
            
            # Escreve os dados para o CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                csvwriter = csv.writer(csvfile)
                # Cabeçalho
                csvwriter.writerow(['ID', 'Funcionário', 'Vendas Totais', 'Número de Pedidos', 'Média por Pedido'])
                # Dados
                for emp in ranking:
                    # Access tuple values by index instead of treating as dictionary
                    # Assumindo a estrutura: (employeeid, employeename, total_sales, order_count, average_per_order)
                    avg_per_order = emp[4] if len(emp) > 4 else (emp[2] / emp[3] if emp[3] > 0 else 0)
                    csvwriter.writerow([
                        emp[0],  # employeeid
                        emp[1],  # employeename
                        emp[2],  # total_sales
                        emp[3],  # order_count
                        avg_per_order  # average_per_order (calculado se não fornecido)
                    ])
            
            flash(f'Relatório CSV gerado com sucesso: {filename}', 'success')
            
            # Opção: Retornar arquivo para download
            return send_file(filepath, as_attachment=True, download_name=filename)
            
        except Exception as e:
            flash(f'Erro ao gerar relatório CSV: {str(e)}', 'danger')
            print(f"Erro detalhado: {e}")
            return render_template('error.html', error=str(e))
    else:
        return render_template('employee_ranking_form.html')

@order_bp.route('/search_orders', methods=['GET'])
def search_orders():
    """Busca pedidos para mostrar no relatório."""
    safe = request.args.get('safe', 'true') == 'true'
    order_id = request.args.get('order_id', '')
    
    try:
       
        orders = psycopg_dao.search_orders(order_id)
        return jsonify({'success': True, 'orders': orders})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})