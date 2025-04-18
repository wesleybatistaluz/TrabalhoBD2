from flask import Flask, render_template
from controllers.order_controller import order_bp

app = Flask(__name__)
app.config.from_object('config')

# Registrar blueprints
app.register_blueprint(order_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)