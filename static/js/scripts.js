document.addEventListener("DOMContentLoaded", function() {

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value
    }

    function showToast(message) {
        const el = document.getElementById("cartToast");
        el.querySelector(".toast-body").innerText = message;
        new bootstrap.Toast(el).show();
    }


    function showBanner(message) {
        const el = document.getElementById("globalBanner");
        el.innerText = message;
        el.classList.remove("d-none");

        setTimeout (() => {
            el.classList.add("d-none");
        }, 4000)
    }

    function notify(type, message) {
        if (type == "success") {
            showToast(message);
        }
        else{
            showBanner(message);
        }
    }

    function updateCartBadge(delta = 1) {
        const el = document.getElementById("cart-count");
        if (!el) return;

        let current = parseInt(el.innerText || "0");
        el.innerText = current + delta;
    }

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

    document.addEventListener("change", function(e) {
        const input = e.target.closest(".update-cart-input");
        if (!input) return;

        const quantity = parseInt(input.value);
        const productId = input.dataset.productId;

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

            notify(data.type, data.message);

            if(data.adjusted_quantity !== undefined) {
                input.value = data.adjusted_quantity;
            }
            if (data.ok) {

                if(data.deleted){

                    const card = input.closest("[data-cart-item]");

                    if(card) {
                        card.remove();
                    }

                    const badge = document.getElementById("cart-count");
                    if (badge) {
                        badge.innerText = data.cart_count;
                    }

                    const summaryCount = document.getElementById("cart-summary-count");
                    if(summaryCount) {
                        summaryCount.innerText = data.cart_count;
                    }

                    const summaryTotal= document.getElementById("cart-summary-total");
                    if (summaryTotal) {
                        summaryTotal.innerText = `${data.cart_total} €`;
                    }

                    if(typeof UpdateMiniCart === "function") {
                        UpdateMiniCart();
                    }
                    return;
                }

                const card = input.closest("[data-cart-item]");

                if (card) {
                    const itemTotal = card.querySelector(".item-total");

                    if (itemTotal) {
                        itemTotal.innerText = 
                        `Total: ${data.item_total} €`;
                    }
                }

                const summaryTotal= document.getElementById("cart-summary-total");
                if (summaryTotal) {
                    summaryTotal.innerText = `${data.cart_total} €`;
                }

                const badge = document.getElementById("cart-count");
                if (badge) {
                    badge.innerText = data.cart_count;
                }

                const summaryCount = document.getElementById("cart-summary-count");
                if(summaryCount) {
                    summaryCount.innerText = data.cart_count;
                }

                if(typeof UpdateMiniCart === "function") {
                    UpdateMiniCart();
                }
            }        
        });
    });

    document.addEventListener("click", function(e) {
        const input = e.target.closest(".update-cart-input");
        if (!input) return;

        const max = parseInt(input.max)
        
        if(parseInt(input.value) >= max){
            notify("warning", `Only ${max} units available.`)
        }
    });

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
})