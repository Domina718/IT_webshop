document.addEventListener("DOMContentLoaded", function() {

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value
    }

    function showToast(message) {
        const el = document.getElementById("cartToast");
        el.querySelector(".toast-body").innerText = message;
        new bootstrap.Toast(el).show();
    }

    function notify(type, message) {
        if (!message) return;
            
        showToast(message);
    }

    function updateCartBadge(delta = 1) {
        const el = document.getElementById("cart-count");
        if (!el) return;

        let current = parseInt(el.innerText || "0");
        el.innerText = current + delta;
    }

    function showEmptyCartIfNeeded(cartCount) {
        cartCount = parseInt(cartCount);

        if(cartCount > 0) return;

        const cartItems = document.getElementById("cart-items");
        const orderSummary = document.getElementById("order-summary");

        if(cartItems) {
            cartItems.innerHTML = `<p class="text-muted">Your cart is empty.</p>`;
        }

        if(orderSummary) {
            orderSummary.remove();
        }
    }

    function refreshCartBadge() {
        fetch("/cart/count/")
            .then(res => res.json())
            .then(data => {
                const badge = document.getElementById("cart-count");

                if(badge) {
                    badge.innerText = data.count;

                    if(data.count > 0) {
                        badge.classList.remove("d-none");
                    }
                    else {
                        badge.classList.add("d-none");
                    }
                }
            });
    }

    function UpdateMiniCart() {
        fetch("/cart/mini/")
        .then(res => res.json())
        .then(data => {
            const miniCart = document.getElementById("mini-cart-dropdown");
            if(!miniCart) return;

            if(data.count === 0) {
                miniCart.innerHTML = `
                <p class="text-muted mb-2">Your cart is empty.</p>
                <a href="/products/" class="btn btn-primary btn-sm w-100">
                    Browse products
                </a>
            `;
            return;
            }

            let html = "";

            data.items.forEach(item => {
                html += `
                    <div class="d-flex border-bottom pb-2 mb-2 mini-cart-item">
                        <div class="mini-cart-image-box">
                            <img src="${item.image}" class="rounded me-2 mini-cart-image">
                        </div>
                        <div class="flex-grow-1">
                            <div class="fw-semibold">${item.name}</div>

                            ${item.has_discount ? `
                                <small class="text-muted">
                                    ${item.quantity} x 
                                    <span class="text-decoration-line-through">
                                        ${item.original_price.toFixed(2)} €
                                    </span>
                                    <span class="text-danger fw-bold">
                                        ${item.price.toFixed(2)} €
                                    </span>
                                    <span class="badge bg-danger ms-1">
                                        -${item.discount_percent}%
                                    </span>
                                </small>
                            `:`
                                <small class="text-muted">
                                    ${item.quantity} x ${item.price.toFixed(2)} €
                                </small>                         
                            `}
                            <div class="fw-bold">
                                ${item.total_price.toFixed(2)} €
                            </div>
                        </div>
                    </div>
                `;
                });

                html += `
                    <div class="d-flex justify-content-between fw-bold mt-2">
                        <span>Total:</span>
                        <span>${data.total.toFixed(2)} € </span>
                    </div>
                    
                    <a href="/cart/" class="btn btn-success btn-sm w-100 mt-3">
                        View cart
                    </a>
                `;

                miniCart.innerHTML = html;         
            });
    }

    document.addEventListener("submit", function(e) {

        const form = e.target 
        if (!form.classList.contains("ajax-update-cart-form")){
           return;
        }

        e.preventDefault();
        const quantityInput = form.querySelector("[name='quantity']");
        const quantity = parseInt(quantityInput.value);

        const productId = form.action.split("/cart/update/")[1].split("/")[0];

        const visibleInput = document.querySelector(
            `.update-cart-input[data-product-id="${productId}"]`
        );

        if (visibleInput) {
            visibleInput.value = quantity;
            visibleInput.dispatchEvent(new Event("change", { bubbles: true}));
        }
    });

    document.addEventListener("click", function(e) {
        const btn = e.target.closest(".add-to-cart-btn");
        if (!btn) return;

        e.preventDefault();

        const form = btn.closest("form");
        const qtyInput = form?.querySelector(".qty-input");
        const quantity = qtyInput ? parseInt(qtyInput.value) : 1;

        fetch("/cart/add/" + btn.dataset.productId + "/", {
            method: "POST", 
            headers: {
                "X-CSRFToken": getCSRFToken()
            },
            body: new URLSearchParams({
                quantity: quantity
            })
        })
        .then(res => res.json())
        .then(data => {
            notify(data.type, data.message);

            if (data.ok) {
                refreshCartBadge();
                if(typeof UpdateMiniCart === "function") {
                    UpdateMiniCart();
                }
                
                if (qtyInput) {
                    qtyInput.value = "1";
                }
            }
        });
    });

    document.addEventListener("click", function(e) {
        const btn = e.target.closest(".confirm-remove-btn");
        if (!btn) return;

        e.preventDefault();

        const productId = btn.dataset.productId;

        fetch("/cart/remove/" + productId + "/", {
            method: "POST", 
            headers: {
                "X-CSRFToken": getCSRFToken()
            }
        })
        .then(res => res.json())
        .then(data => {
            notify(data.type, data.message);

            if (data.ok) {
                const itemEl = document.querySelector(
                    `[data-cart-item = "${data.product_id}"]`);
                if (itemEl) itemEl.remove();

                const badge = document.getElementById("cart-count");

                if (badge) {
                    badge.innerText = data.cart_count;

                    if(data.cart_count > 0) {
                        badge.classList.remove("d-none");
                    }
                    else {
                        badge.classList.add("d-none");
                    }
                }

                const summaryCount = document.getElementById("cart-summary-count");
                if(summaryCount) {
                    summaryCount.innerText = data.cart_count;
                }

                const summaryTotal= document.getElementById("cart-summary-total");
                if (summaryTotal) {
                    summaryTotal.innerText = `${data.cart_total} €`;
                }

                const summarySubtotal = document.getElementById("cart-summary-subtotal");
                if(summarySubtotal && data.original_cart_total !== undefined) {
                    summarySubtotal.innerText = `${data.original_cart_total.toFixed(2)} €`;
                }

                const summarySavings = document.getElementById("cart-summary-savings");
                if(summarySavings && data.total_savings !== undefined) {
                    summarySavings.innerText = `-${data.total_savings.toFixed(2)} €`;
                }

                const discountBlock = document.getElementById("discount-summary-block");
                if (discountBlock && data.total_savings !== undefined && data.total_savings <= 0) {
                    discountBlock.remove();
                }

                showEmptyCartIfNeeded(data.cart_count);

                const modalEl = btn.closest(".modal");
                if (modalEl) {
                    const modal = bootstrap.Modal.getInstance(modalEl);
                    modal?.hide();
                }

                if(typeof UpdateMiniCart === "function") {
                    UpdateMiniCart();
                }
            }
        });
    });

    function updateCartSummary(data) {
        const summaryTotal= document.getElementById("cart-summary-total");
        if (summaryTotal) {
            summaryTotal.innerText = `${data.cart_total} €`;
        }

        const summarySubtotal = document.getElementById("cart-summary-subtotal");
        if(summarySubtotal && data.original_cart_total !== undefined) {
            summarySubtotal.innerText = `${data.original_cart_total.toFixed(2)} €`;
        }

        const summarySavings = document.getElementById("cart-summary-savings");
        if(summarySavings && data.total_savings !== undefined) {
            summarySavings.innerText = `-${data.total_savings.toFixed(2)} €`;
        }

        const discountBlock = document.getElementById("discount-summary-block");
        if (discountBlock && data.total_savings !== undefined && data.total_savings <= 0) {
            discountBlock.remove();
        }

        const badge = document.getElementById("cart-count");
        if (badge && data.cart_count !== undefined) {
            badge.innerText = data.cart_count;
        }

        const summaryCount = document.getElementById("cart-summary-count");
        if(summaryCount && data.cart_count !== undefined) {
            summaryCount.innerText = data.cart_count;
        }

        if(typeof UpdateMiniCart === "function") {
            UpdateMiniCart();
        }
    }

    function updateItemTotal(card, data) {
        const itemTotal = card?.querySelector(".item-total");
        if (!itemTotal) return;

        if(data.has_discount) {
            itemTotal.innerHTML = `
            Total:
            <span class="text-muted text-decoration-line-through">
                ${data.original_item_total.toFixed(2)} €
            </span>
            <span class="text-danger fw-bold ms-2">
                ${data.item_total.toFixed(2)} €
            </span>
            <span class="badge bg-danger ms-1">
                -${data.discount_percent}%
            </span>`;
        }
        else{
            itemTotal.innerText = `Total: ${data.item_total.toFixed(2)} €`;
        }
    }

    function removeStockWarningIfFixed(card, input, data) {
        if(card && data.adjusted_quantity <= parseInt(input.max)) {
            const warningBlock = card.querySelector(".stock-warning-block");
            if (warningBlock) {
                warningBlock.remove();
            }

            const anyStockWarningsLeft = document.querySelector(".stock-warning-block");
            if(!anyStockWarningsLeft) {
                const disabledBlock = document.getElementById("checkout-disabled-block");

                if (disabledBlock) {
                    disabledBlock.innerHTML = `
                        <a href="/orders/checkout/" id="checkout-enabled-btn" class="btn btn-success btn-lg w-100 mb-2">
                            🛒 Proceed to Checkout
                        </a>
                    `;
                }
            }
        }

    }

    document.addEventListener("change", function(e) {
        const input = e.target.closest(".update-cart-input");
        if (!input) return;

        const quantity = parseInt(input.value);
        const productId = input.dataset.productId;
        const oldQuantity = parseInt(input.dataset.currentQuantity || input.defaultValue || "0")

        if(quantity <= 0) {
            input.value = 1;
        
            const modalEl = document.getElementById("removeModal" + productId);
            if(modalEl) {
                const modal = new bootstrap.Modal(modalEl);
                modal.show();
            }
            return;
        }

        fetch("/cart/update/" + productId + "/", {
            method: "POST", 
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": getCSRFToken()
            },
            body: new URLSearchParams({
                quantity: quantity
            })
        })
        .then(res => res.json())
        .then(data => {

            if(data.type === "warning") {
                notify(data.type, data.message);
            }
            else {
                const newQuantity = parseInt(data.adjusted_quantity);
                const diff = newQuantity - oldQuantity;
            
                if (diff > 0) {
                    notify("success", `${diff}x ${data.product_name} added to cart`);
                }
                else if (diff < 0) {
                    notify("success", `${Math.abs(diff)}x ${data.product_name} removed from cart`);
                }
                else {
                    notify(data.type, data.message);
                }
            }
        

            if(data.adjusted_quantity !== undefined) {
                input.value = data.adjusted_quantity;
            }
            if (data.ok) {
                input.dataset.currentQuantity = data.adjusted_quantity;

                const card = input.closest("[data-cart-item]");

                removeStockWarningIfFixed(card, input, data);
                updateItemTotal(card, data);
                updateCartSummary(data);                     
            }
        });        
    });

    document.addEventListener("click", function(e) {
        const input = e.target.closest(".update-cart-input");
        if (!input) return;

        const max = parseInt(input.max);
        const value = parseInt(input.value);
        const productName = input.dataset.productName;
        
        if(value >= max){
            notify("warning", `Only ${max} units of ${productName} are available.`)
        }
    });


    UpdateMiniCart();
})