const CART_KEY = "fox-shop-cart";

const readCart = () => JSON.parse(localStorage.getItem(CART_KEY) || "{}");

const addToCart = (id, quantity) => {
  const cart = readCart();
  cart[id] = (cart[id] || 0) + quantity;
  localStorage.setItem(CART_KEY, JSON.stringify(cart));
};

const toCents = (price) => Math.round(Number(price.replace("$", "")) * 100);

const formatCents = (cents) => `$${(cents / 100).toFixed(2)}`;
