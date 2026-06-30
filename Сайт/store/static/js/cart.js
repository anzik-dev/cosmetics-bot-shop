document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.cart-form').forEach(form => {
    const pid   = form.dataset.productId;
    const token = form.querySelector('[name=csrfmiddlewaretoken]').value;

    form.addEventListener('click', async e => {
      const btn = e.target.closest('button');
      if (!btn) return;

      let action = null;
      if (btn.classList.contains('add-to-cart-btn')) action = 'add';
      if (btn.classList.contains('plus'))            action = 'increase';
      if (btn.classList.contains('minus'))           action = 'decrease';
      if (!action) return;

      const resp = await fetch(`/cart/ajax/update/${pid}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': token,
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `action=${action}`
      });

      if (!resp.ok) return console.error('Network error');
      const data = await resp.json();

      // обновляем кнопку прямо на месте
      if (data.quantity > 0) {
        form.innerHTML = `
          <input type="hidden" name="csrfmiddlewaretoken" value="${token}">
          <div class="in-cart">
            <button type="button" class="cart-btn minus">−</button>
            <span class="cart-quantity">В корзине: ${data.quantity}</span>
            <button type="button" class="cart-btn plus">+</button>
          </div>`;
      } else {
        form.innerHTML = `
          <input type="hidden" name="csrfmiddlewaretoken" value="${token}">
          <button type="button" class="add-to-cart-btn">Добавить в корзину</button>`;
      }
    });
  });
});
