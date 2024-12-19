===============================
Shopping Cart Backend API
===============================

This project is a FastAPI-based application that provides functionality for managing products and shopping carts. It includes features such as user authentication, product management (CRUD), and cart management. It also integrates role-based access control (admin, user), rate limiting, and file uploads (for product images).

Features
--------

- **User Management and Authentication**: CRUD operations for User, JWT token-based authentication.
- **Product Management**: CRUD operations for products, including product images.
- **Shopping Cart**: Users can add, update, and delete products from their shopping cart.
- **Role-based Access Control**: Admins can perform certain actions (e.g., create/update/delete products).
- **Rate Limiting**: Uses SlowAPI middleware for rate limiting requests.
- **File Uploads**: Supports uploading product images (JPEG, PNG, GIF).
- **CORS Middleware**: Configured to allow cross-origin requests.

Hosting
-------
This application was hosted using **AWS** for infrastructure and **NGINX** as a reverse proxy to manage requests.

Steps:
1. **AWS Deployment**:
   - Deployed the application on an AWS EC2 instance.
   - Configured security groups to allow traffic from the internet.

2. **NGINX Configuration**:
   - NGINX was set up as a reverse proxy to route requests from the server's domain or IP address to the FastAPI application.

Visit http://ec2-3-80-180-137.compute-1.amazonaws.com to access the live application.

Requirements
------------

- Python 3.8+
- PostgreSQL
- FastAPI
- SQLAlchemy
- Pydantic
- SlowAPI (for rate limiting)

Installation
------------

1. **Clone the repository**:

   .. code-block:: bash

      git clone https://github.com/quantum-ernest/backend-azubi-assessment.git
      cd your-repository

2. **Install dependencies**:

   .. code-block:: bash

      pip install -r requirements.txt

3. **Set up environment variables**:
   Create a `.env` file in the root directory and define the following variables:

   .. code-block:: ini

      POSTGRES_USER=
      POSTGRES_PASSWORD=
      POSTGRES_DB_NAME=
      POSTGRES_HOST=
      POSTGRES_PORT=
      AUTH_SECRETE_KEY=
      AUTH_ALGORITHM=
      ADMIN_DEFAULT_EMAIL=
      ADMIN_DEFAULT_NAME=
      ADMIN_DEFAULT_PASSWORD=

4. **Run the application**:

   .. code-block:: bash

      uvicorn main:app --reload

      The application will be running at `http://127.0.0.1:8000`.

Setup with Docker
=================

To set up the project with Docker, follow these steps:

1. Clone the repository.
2. Run the `docker-compose up -d` command.
3. The API will be accessible at: `http://localhost:8000` or `http://0.0.0.0:8000`.
4. Make sure to configure the environment variables in the `.env` file.

Endpoints
---------

### Authentication

- **POST /auth/login**: Login with email and password to get an access token.
- **POST /auth/change-password**: Change password.

### Products

- **GET /products**: Get a list of products. Supports filtering by name, category, and price.
- **GET /products/{id}**: Get a product by ID.
- **POST /products**: Create a new product (Admin only).
- **PUT /products/{id}**: Update an existing product (Admin only).
- **DELETE /products/{id}**: Delete a product (Admin only).
- **GET /products/images/{filename}**: Get an image of a product.

### Shopping Cart

- **GET /cart**: Get a list of items in the user's shopping cart.
- **POST /cart**: Add an item to the cart.
- **PUT /cart/{id}**: Update the quantity of an item in the cart.
- **DELETE /cart/{product_id}**: Remove an item from the cart.

### Roles

- **GET /roles**: Get all roles (Admin only).

### Users

- **GET /users**: Get all users (Admin only).
- **GET /users/profile**: Get user profile (Admin only).
- **POST /users**: Create a user.

Rate Limiting
-------------

The application uses SlowAPI to limit requests to 50 requests per minute. If the limit is exceeded, a `429 Too Many Requests` error will be returned.

File Uploads
------------

The following types of image files are supported for upload:

- **JPEG**
- **PNG**
- **GIF**

Images are stored in the `assets/images/` directory and are linked to products during creation or update.

Default Data
------------

The application will automatically create default roles (`user`, `admin`) and a default admin user based on values in the `.env` file.

Database
--------

The application uses PostgreSQL for storing user, product, cart, and role data. Ensure that the PostgreSQL database is set up and running, and that the credentials in the `.env` file are correct.

Testing
-------

This project includes automated tests for the API endpoints. The tests are written using `pytest` and FastAPI's `TestClient`.
