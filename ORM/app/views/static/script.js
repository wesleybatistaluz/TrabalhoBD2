const form = document.getElementById("pedido-form");
const itensContainer = document.getElementById("itens-container");

function adicionarItem() {
    const div = document.createElement("div");
    div.classList.add("item");
  
    div.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <strong>Item</strong>
        <button type="button" class="remover-item" style="background: transparent; border: none; font-size: 18px; color: red; cursor: pointer;">❌</button>
      </div>
  
      <label>Produto ID</label>
      <input type="number" name="product_id" required>
  
      <label>Quantidade</label>
      <input type="number" name="quantity" required>
  
  
      <hr>
    `;
  
    // Botão "Remover item"
    div.querySelector(".remover-item").addEventListener("click", () => {
      div.remove();
    });
  
    itensContainer.appendChild(div);
  }
  

// Adiciona 1 item por padrão ao carregar
window.onload = () => adicionarItem();

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const customer_id = document.getElementById("customer_id").value;
  const employee_id = parseInt(document.getElementById("employee_id").value);
  const order_date = document.getElementById("order_date").value;

  const itemDivs = document.querySelectorAll("#itens-container .item");
  const items = [];

  for (const div of itemDivs) {
    const product_id = parseInt(div.querySelector('[name="product_id"]').value);
    const quantity = parseInt(div.querySelector('[name="quantity"]').value);

    if (!product_id || !quantity) {
      alert("Por favor, preencha todos os campos dos itens.");
      return;
    }

    items.push({ product_id, quantity});
  }

  const data = { customer_id, employee_id, order_date, items };

  

  try {
    const response = await fetch("http://localhost:5000/api/pedidos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    const result = await response.json();

    if (response.ok) {
      alert("✅ Pedido enviado com sucesso!");
      form.reset();
      itensContainer.innerHTML = "";
      adicionarItem(); // adiciona um novo item em branco
    } else {
      alert("❌ Erro: " + (result.erro || "Erro inesperado"));
    }
  } catch (err) {
    alert("Erro ao enviar: " + err.message);
  }
});