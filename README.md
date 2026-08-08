# 🚀 My Marketplace & Automation API

Welcome to the backend API powering the marketplace platform. This service handles product management with pagination, seller inventory control, user authentication, shopping cart operations, PayPal checkout processing, and PDF invoice generation.

---

## 🛠️ Tech Stack

* **Framework:** FastAPI (Python)
* **Authentication:** OAuth2 with Password Flow & Bearer Tokens


* **Database / ORM:** SQLModel / SQLAlchemy
* **Payment Integration:** PayPal REST SDK & Webhooks


* **Specification:** OpenAPI 3.1.0



---

## ✨ Key Features

* **🔐 Authentication System:** Secure registration and token-based login.


* **📦 Product Catalog:** Full CRUD capabilities, seller-specific inventory views (`my-products`), category filtering, and offset/limit pagination.


* **🛒 Shopping Cart:** Persistent shopping cart management per user (add, update quantities, delete).


* **💳 Order Processing & PayPal:** Checkout pipeline featuring local order tracking, PayPal order creation, capture handling, and webhook integration.


* **📄 Invoice Generation:** Endpoint dedicated to fetching order PDF invoices.



---

## 📌 API Endpoint Reference

### 🔐 Authentication (`/auth`)

| Method | Endpoint | Description | Auth Required |
| --- | --- | --- | --- |
| `POST` | `/auth/sign-up`<br> | Register a new user (`username`, `email`, `password`, `bio`)

 | No |
| `POST` | `/auth/token/login`<br> | Authenticate user and issue OAuth2 Bearer Access Token

 | No |

---

### 📦 Product Management (`/products`)

| Method | Endpoint | Description | Auth Required |
| --- | --- | --- | --- |
| `GET` | `/products/products`<br> | List products with pagination metadata (`offset`, `limit`, `category_id`)

 | No |
| `GET` | `/products/{id_product}`<br> | Fetch product details by ID

 | No |
| `GET` | `/products/my-products`<br> | Retrieve products owned by the authenticated seller

 | Yes |
| `POST` | `/products/add-product`<br> | Create a new product entry in stock

 | Yes |
| `PATCH` | `/products/update`<br> | Update specific attributes of a product

 | Yes |
| `DELETE` | `/products/delete-product`<br> | Delete a product from inventory

 | Yes |

---

### 🛒 Shopping Cart (`/cart`)

| Method | Endpoint | Description | Auth Required |
| --- | --- | --- | --- |
| `GET` | `/cart/get-items`<br> | View all items in the user's cart

 | Yes |
| `POST` | `/cart/add-item`<br> | Add a product to the cart with specified quantity

 | Yes |
| `PATCH` | `/cart/update-item`<br> | Modify item quantity in the cart

 | Yes |
| `DELETE` | `/cart/delete-item`<br> | Remove an item from the cart

 | Yes |

---

### 💳 Orders & Payments (`/orders` & `/webhooks`)

| Method | Endpoint | Description | Auth Required |
| --- | --- | --- | --- |
| `POST` | `/orders/checkout`<br> | Create local order and initialize PayPal payment

 | Yes |
| `POST` | `/orders/capture-paypal`<br> | Capture approved PayPal payment and sync order state

 | No |
| `GET` | `/orders/history`<br> | Fetch authenticated user's order history

 | Yes |
| `GET` | `/orders/details`<br> | View detailed breakdown of a specific order

 | Yes |
| `GET` | `/orders/{order_id}/invoice`<br> | Download PDF invoice for a completed order

 | No |
| `POST` | `/webhooks/paypal`<br> | Process asynchronous payment events from PayPal

 | No |

---

## ⚡ Quick Start

### Prerequisites

* Python 3.10+
* Virtual Environment (`venv` or `poetry`)

### 1. Clone the repository

```bash
git clone https://github.com/Us7rname/your-repo-name.git
cd your-repo-name

```

### 2. Set up virtual environment & install dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

```

### 3. Environment Variables (`.env`)

Create a `.env` file in the root directory:

```env
SECRET_KEY=your_super_secret_jwt_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

DATABASE_URL=sqlite:///./database.db  # or PostgreSQL connection string

PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
PAYPAL_MODE=sandbox  # or live

```

### 4. Run the API locally

```bash
uvicorn app.main:app --reload

```

The API will be running at `[http://127.0.0.1:8000](http://127.0.0.1:8000)`.

---

## 📑 Interactive API Documentation

Once the server is running, explore and test endpoints interactively via:

* **Swagger UI:** `[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)`
* **ReDoc:** `[http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)`

---

## 👤 Author

* **Developer:** Us7rname (Code Craft)


* **GitHub:** [@Us7rname](https://www.google.com/search?q=https://github.com/Us7rname)