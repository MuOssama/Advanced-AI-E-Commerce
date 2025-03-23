# Advanced-AI-E-Commerce
Advanced AI E-Commerce built by LLM API# Flask E-commerce Application with AI Chat Assistant

A modern e-commerce web application built with Flask, featuring an AI-powered shopping assistant using Google's Gemini 1.5 Pro model.

## Features

- **User Authentication**: Secure registration and login system
- **Product Catalog**: Browse products with category filtering
- **Shopping Cart**: Add, update, and remove items
- **AI Shopping Assistant**: Powered by Google's Gemini 1.5 Pro
- **Search Functionality**: Find products by name or description
- **Checkout Process**: Simple order placement
- **Admin Tools**: Dedicated utility for managing products and users

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **AI Model**: Google Gemini 1.5 Pro via LangChain
- **Authentication**: Werkzeug security for password hashing
- **Frontend**: HTML, CSS, JavaScript (templates not shown in repo)

## Prerequisites

- Python 3.7+
- Google API key for Gemini 1.5 Pro
- Flask and other dependencies

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/flask-ecommerce-ai.git
   cd flask-ecommerce-ai
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. open the `.env` file in the project root with your credentials:
   ```
   GOOGLE_API_KEY= copy_here_you_Gemini_API
   ```

## Running the Application

1. Initialize the database (happens automatically on first run)

2. Start the development server:
   ```
   python app.py
   ```

3. Open your browser and go to `http://127.0.0.1:5000/`

## Administration

The application includes an admin tool for database management:

1. Run the admin utility:
   ```
   python adminTool.py
   ```

2. Use the admin tool to:
   - Add new products to the catalog
   - Modify existing product details
   - Remove products from the database
   - Manage user accounts
   - Perform other database maintenance tasks

This utility is separate from the main application for security purposes and should only be accessible to administrators.

## Database Structure

The application uses SQLite with the following tables:

- **products**: Store product information (name, price, description, image, category)
- **users**: Store user account information
- **cart**: Track items in user shopping carts

## AI Chat Assistant

The application integrates Google's Gemini 1.5 Pro model through LangChain to provide:

- Product recommendations
- Answering questions about available products
- Shopping assistance

The AI assistant has access to the current product catalog to provide accurate information.

## Application Structure

- `app.py`: Main application file with all routes and database functions
- `adminTool.py`: Administrative utility for database management
- `templates/`: HTML templates for the web interface (not shown in repo)
- `static/`: Static files like images and CSS (not shown in repo)
- `ecommerce.db`: SQLite database (created on first run)

## Routes

- `/`: Home page
- `/register`: User registration
- `/login`: User login
- `/logout`: User logout
- `/products`: Product catalog
- `/search`: Product search
- `/chat`: AI assistant endpoint
- `/cart`: Shopping cart
- `/add_to_cart`: Add items to cart
- `/update_cart`: Update cart quantities
- `/remove_from_cart`: Remove items from cart
- `/checkout`: Process orders

## Future Enhancements

- Payment gateway integration
- Order history
- Product reviews and ratings
- Enhanced AI capabilities
- Web-based admin dashboard
- Responsive design improvements


## Acknowledgements

- Google for the Gemini API
- LangChain for simplified AI integration
- Flask and its ecosystem

## DEPLOYMENT
Running the Project on Windows

To run the project on Windows, follow these steps:

1. Open Command Prompt (cmd)

2. Create a Virtual Environment

python -m venv venv

3. Activate the Virtual Environment

venv\Scripts\activate

4. Clone the Repository and Place It Inside venv

Ensure that the project repository is inside the venv directory.

5. Install Dependencies

pip install -r venv/requirements.txt

6. Run the Project

python main.py

Now, your project should be running successfully!

Running the Project on Replit

To deploy the project on Replit, follow these steps:

1. Create a New Replit Project

Go to Replit

Click Create Repl and select Python as the template.

2. Clone the Repository

Open the Replit shell and run:

git clone <your-repo-url>
cd <your-repo-folder>

3. Install Dependencies

pip install -r requirements.txt

4. Run the Project

python main.py

5. Keep the Server Running (For Flask Apps)

If using Flask, modify main.py to include:

from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Replit!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

6. Enable Replit Web Hosting

Click on the Run button.

Copy the provided Replit URL to access your project online.
