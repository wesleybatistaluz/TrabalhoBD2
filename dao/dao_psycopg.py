# dao/dao_psycopg.py
import psycopg2
from psycopg2 import Error
from config import DB_CONFIG

class OrderDAOPsycopg:
    def __init__(self):
        self.conn = None
        self.cur = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cur = self.conn.cursor()
        except Error as e:
            print(f"Erro ao conectar ao PostgreSQL: {e}")
            if self.conn:
                self.conn.close()
            raise e

    def disconnect(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def get_customers(self):
        self.connect()
        try:
            self.cur.execute("SELECT customerid, companyname, contactname FROM northwind.customers")
            return self.cur.fetchall()
        finally:
            self.disconnect()

    def get_customer_by_name(self, customer_name):
        self.connect()
        try:
            self.cur.execute(
                "SELECT customerid, companyname FROM northwind.customers WHERE contactname LIKE %s",
                (f"%{customer_name}%",)
            )
            results = self.cur.fetchall()
            converted_results = []
            for row in results:
                converted_row = [item.encode('latin1').decode('utf-8') if isinstance(item, str) else item for item in row]
                converted_results.append(tuple(converted_row))
            return converted_results
        finally:
            self.disconnect()

    def get_customer_by_name_unsafe(self, customer_name):
        """Versão vulnerável a SQL Injection para fins de demonstração"""
        self.connect()
        try:
            self.cur.execute(
                f"SELECT customerid, companyname FROM northwind.customers WHERE contactname LIKE '%{customer_name}%'"
            )
            results = self.cur.fetchall()
            converted_results = []
            for row in results:
                converted_row = [item.encode('latin1').decode('utf-8') if isinstance(item, str) else item for item in row]
                converted_results.append(tuple(converted_row))
            return converted_results
        finally:
            self.disconnect()

    def get_employees(self):
        self.connect()
        try:
            self.cur.execute("SELECT employeeid, firstname, lastname FROM northwind.employees")
            return self.cur.fetchall()
        finally:
            self.disconnect()

    def get_employee_by_name(self, employee_name):
        self.connect()
        try:
            self.cur.execute(
                "SELECT employeeid, firstname, lastname FROM northwind.employees WHERE firstname ILIKE %s OR lastname ILIKE %s",
                (f"%{employee_name}%", f"%{employee_name}%")
            )
            return self.cur.fetchall()
        finally:
            self.disconnect()

    def get_employee_by_name_unsafe(self, employee_name):
        """Versão vulnerável a SQL Injection para fins de demonstração"""
        self.connect()
        try:
            self.cur.execute(
                f"SELECT employeeid, firstname, lastname FROM northwind.employees WHERE firstname ILIKE '%{employee_name}%' OR lastname ILIKE '%{employee_name}%'"
            )
            return self.cur.fetchall()
        finally:
            self.disconnect()

    def get_products(self):
        self.connect()
        try:
            self.cur.execute("SELECT productid, productname, unitprice FROM northwind.products")
            return self.cur.fetchall()
        finally:
            self.disconnect()

    def get_product_by_name(self, product_name):
        self.connect()
        try:
            self.cur.execute(
                "SELECT productid, productname, unitprice FROM northwind.products WHERE productname ILIKE %s",
                (f"%{product_name}%",)
            )
            return self.cur.fetchall()
        finally:
            self.disconnect()

    def get_product_by_name_unsafe(self, product_name):
        """Versão vulnerável a SQL Injection para fins de demonstração"""
        self.connect()
        try:
            self.cur.execute(
                f"SELECT productid, productname, unitprice FROM northwind.products WHERE productname ILIKE '%{product_name}%'"
            )
            return self.cur.fetchall()
        finally:
            self.disconnect()

    def create_order_safe(self, order):
        self.connect()
        try:
            self.cur.execute("SELECT MAX(orderid) + 1 FROM northwind.orders")
            next_id = self.cur.fetchone()[0] or 1

            self.cur.execute(
                """
                INSERT INTO northwind.orders (orderid, customerid, employeeid, orderdate)
                VALUES (%s, %s, %s, %s)
                """,
                (next_id, order.customerid, order.employeeid, order.orderdate)
            )

            for item in order.order_details:
                self.cur.execute(
                    """
                    INSERT INTO northwind.order_details (orderid, productid, unitprice, quantity, discount)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (next_id, item.productid, item.unitprice, item.quantity, item.discount)
                )

            self.conn.commit()
            return next_id

        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            self.disconnect()

    def create_order_unsafe(self, order):
        """Versão vulnerável a SQL Injection para fins de demonstração"""
        self.connect()
        try:
            self.cur.execute("SELECT MAX(orderid) + 1 FROM northwind.orders")
            next_id = self.cur.fetchone()[0] or 1

            self.cur.execute(
                f"""
                INSERT INTO northwind.orders (orderid, customerid, employeeid, orderdate)
                VALUES ({next_id}, '{order.customerid}', '{order.employeeid}', '{order.orderdate}')
                """
            )

            for item in order.order_details:
                self.cur.execute(
                    f"""
                    INSERT INTO northwind.order_details (orderid, productid, unitprice, quantity, discount)
                    VALUES ({next_id}, {item.productid}, {item.unitprice}, {item.quantity}, {item.discount})
                    """
                )

            self.conn.commit()
            return next_id

        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            self.disconnect()

    def get_order_details(self, order_id):
        self.connect()
        try:
            self.cur.execute(
                """
                SELECT o.orderid, o.orderdate, c.companyname, c.contactname, 
                       e.firstname || ' ' || e.lastname AS employee_name
                FROM northwind.orders o
                JOIN northwind.customers c ON o.customerid = c.customerid
                JOIN northwind.employees e ON o.employeeid = e.employeeid
                WHERE o.orderid = %s
                """,
                (order_id,)
            )
            order_info = self.cur.fetchone()

            if not order_info:
                return None

            self.cur.execute(
                """
                SELECT p.productname, od.quantity, od.unitprice, 
                       (od.quantity * od.unitprice * (1 - od.discount)) AS subtotal
                FROM northwind.order_details od
                JOIN northwind.products p ON od.productid = p.productid
                WHERE od.orderid = %s
                """,
                (order_id,)
            )
            order_items = self.cur.fetchall()

            return {
                'order_info': order_info,
                'order_items': order_items
            }
        finally:
            self.disconnect()

    def get_order_details_unsafe(self, order_id):
        """Versão vulnerável a SQL Injection para fins de demonstração"""
        self.connect()
        try:
            self.cur.execute(
                f"""
                SELECT o.orderid, o.orderdate, c.companyname, c.contactname, 
                       e.firstname || ' ' || e.lastname AS employee_name
                FROM northwind.orders o
                JOIN northwind.customers c ON o.customerid = c.customerid
                JOIN northwind.employees e ON o.employeeid = e.employeeid
                WHERE o.orderid = {order_id}
                """
            )
            order_info = self.cur.fetchone()

            if not order_info:
                return None

            self.cur.execute(
                f"""
                SELECT p.productname, od.quantity, od.unitprice, 
                       (od.quantity * od.unitprice * (1 - od.discount)) AS subtotal
                FROM northwind.order_details od
                JOIN northwind.products p ON od.productid = p.productid
                WHERE od.orderid = {order_id}
                """
            )
            order_items = self.cur.fetchall()

            return {
                'order_info': order_info,
                'order_items': order_items
            }
        finally:
            self.disconnect()

    def get_employee_ranking(self, start_date, end_date):
        """Gera ranking dos funcionários por período e retorna os dados em formato exportável."""
        self.connect()
        try:
            self.cur.execute(
                """
                SELECT 
                    e.employeeid, 
                    e.firstname || ' ' || e.lastname AS employee_name,
                    COUNT(DISTINCT o.orderid) AS total_orders,
                    COALESCE(SUM(od.quantity * od.unitprice * (1 - od.discount)), 0) AS total_sales
                FROM northwind.employees e
                LEFT JOIN northwind.orders o ON e.employeeid = o.employeeid 
                                              AND o.orderdate BETWEEN %s AND %s
                LEFT JOIN northwind.order_details od ON o.orderid = od.orderid
                GROUP BY e.employeeid, employee_name
                ORDER BY total_sales DESC
                """,
                (start_date, end_date)
            )
            return self.cur.fetchall()
        finally:
            self.disconnect()

    def get_employee_ranking_unsafe(self, start_date, end_date):
        """Versão vulnerável a SQL Injection para fins de demonstração"""
        self.connect()
        try:
            self.cur.execute(
                f"""
                SELECT 
                    e.employeeid, 
                    e.firstname || ' ' || e.lastname AS employee_name,
                    COUNT(DISTINCT o.orderid) AS total_orders,
                    COALESCE(SUM(od.quantity * od.unitprice * (1 - od.discount)), 0) AS total_sales
                FROM northwind.employees e
                LEFT JOIN northwind.orders o ON e.employeeid = o.employeeid 
                                              AND o.orderdate BETWEEN '{start_date}' AND '{end_date}'
                LEFT JOIN northwind.order_details od ON o.orderid = od.orderid
                GROUP BY e.employeeid, employee_name
                ORDER BY total_sales DESC
                """
            )
            return self.cur.fetchall()
        finally:
            self.disconnect()

    def list_orders(self):
        self.connect()
        try:
            self.cur.execute(
                """
                SELECT o.orderid, o.orderdate, c.companyname, 
                       e.firstname || ' ' || e.lastname AS employee_name
                FROM northwind.orders o
                JOIN northwind.customers c ON o.customerid = c.customerid
                JOIN northwind.employees e ON o.employeeid = e.employeeid
                ORDER BY o.orderid DESC
                """
            )
            return self.cur.fetchall()
        finally:
            self.disconnect()

    def list_orders_unsafe(self):
        """Versão vulnerável a SQL Injection para fins de demonstração"""
        self.connect()
        try:
            self.cur.execute(
                """
                SELECT o.orderid, o.orderdate, c.companyname, 
                       e.firstname || ' ' || e.lastname AS employee_name
                FROM northwind.orders o
                JOIN northwind.customers c ON o.customerid = c.customerid
                JOIN northwind.employees e ON o.employeeid = e.employeeid
                ORDER BY o.orderid DESC
                """
            )
            return self.cur.fetchall()
        finally:
            self.disconnect()

    def search_orders(self, order_id=None):
        self.connect()
        try:
            if order_id and order_id.strip():
                self.cur.execute("""
                    SELECT o.orderid, o.orderdate, c.companyname
                    FROM northwind.orders o
                    JOIN northwind.customers c ON o.customerid = c.customerid
                    WHERE o.orderid::text LIKE %s
                    ORDER BY o.orderid
                    LIMIT 10
                """, (f"%{order_id}%",))
            else:
                self.cur.execute("""
                    SELECT o.orderid, o.orderdate, c.companyname
                    FROM northwind.orders o
                    JOIN northwind.customers c ON o.customerid = c.customerid
                    ORDER BY o.orderid DESC
                    LIMIT 10
                """)
            return self.cur.fetchall()
        finally:
            self.disconnect()

    def get_employee_sales_ranking(self, start_date, end_date):
        """Gera ranking de vendas por funcionário com método seguro."""
        self.connect()
        try:
            self.cur.execute(
                """
                SELECT 
                    e.employeeid, 
                    e.firstname || ' ' || e.lastname AS employee_name,
                    COALESCE(SUM(od.quantity * od.unitprice * (1 - od.discount)), 0) AS total_sales,
                    COUNT(DISTINCT o.orderid) AS order_count,
                    CASE 
                        WHEN COUNT(DISTINCT o.orderid) > 0 
                        THEN COALESCE(SUM(od.quantity * od.unitprice * (1 - od.discount)), 0) / COUNT(DISTINCT o.orderid) 
                        ELSE 0 
                    END AS average_per_order
                FROM northwind.employees e
                LEFT JOIN northwind.orders o ON e.employeeid = o.employeeid 
                                             AND o.orderdate BETWEEN %s AND %s
                LEFT JOIN northwind.order_details od ON o.orderid = od.orderid
                GROUP BY e.employeeid, employee_name
                ORDER BY total_sales DESC
                """,
                (start_date, end_date)
            )
            return self.cur.fetchall()
        finally:
            self.disconnect()

    def get_employee_sales_ranking_unsafe(self, start_date, end_date):
        """Versão vulnerável a SQL Injection para fins de demonstração"""
        self.connect()
        try:
            self.cur.execute(
                f"""
                SELECT 
                    e.employeeid, 
                    e.firstname || ' ' || e.lastname AS employee_name,
                    COALESCE(SUM(od.quantity * od.unitprice * (1 - od.discount)), 0) AS total_sales,
                    COUNT(DISTINCT o.orderid) AS order_count,
                    CASE 
                        WHEN COUNT(DISTINCT o.orderid) > 0 
                        THEN COALESCE(SUM(od.quantity * od.unitprice * (1 - od.discount)), 0) / COUNT(DISTINCT o.orderid) 
                        ELSE 0 
                    END AS average_per_order
                FROM northwind.employees e
                LEFT JOIN northwind.orders o ON e.employeeid = o.employeeid 
                                             AND o.orderdate BETWEEN '{start_date}' AND '{end_date}'
                LEFT JOIN northwind.order_details od ON o.orderid = od.orderid
                GROUP BY e.employeeid, employee_name
                ORDER BY total_sales DESC
                """
            )
            return self.cur.fetchall()
        finally:
            self.disconnect()