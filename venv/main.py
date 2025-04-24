
# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import sqlite3
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

# Load environment variables
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Initialize LangChain with Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    google_api_key=os.getenv('GOOGLE_API_KEY'),
    temperature=0.7
)

# Initialize conversation chain with memory
conversation = ConversationChain(
    llm=llm,
    memory=ConversationBufferMemory()
)

def init_db():
    """Initialize the SQLite database and create products and users tables if they don't exist"""
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    
    # Create products table
    c.execute('''
        CREATE TABLE IF NOT EXISTS products
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         name TEXT NOT NULL,
         price REAL NOT NULL,
         description TEXT,
         image_url TEXT,
         category TEXT NOT NULL,
         category_image_url TEXT)
    ''')
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         username TEXT UNIQUE NOT NULL,
         password TEXT NOT NULL,
         email TEXT UNIQUE NOT NULL)
    ''')
    
    # Create cart table
    c.execute('''
        CREATE TABLE IF NOT EXISTS cart
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         user_id INTEGER NOT NULL,
         product_id INTEGER NOT NULL,
         quantity INTEGER NOT NULL DEFAULT 1,
         FOREIGN KEY (user_id) REFERENCES users (id),
         FOREIGN KEY (product_id) REFERENCES products (id))
    ''')
    
    # Insert sample products if the table is empty
    c.execute('SELECT COUNT(*) FROM products')
    count = c.fetchone()[0]
    
    if count == 0:
        sample_products = [
            ('Smartphone', 699.99, 'Latest model with high-resolution camera and all-day battery life', 'static/images/smartphone.jpg', 'Electronics', 'static/images/category_electronics.jpg'),
            ('Laptop', 1299.99, 'Powerful laptop for work and gaming with SSD storage', 'static/images/laptop.jpg', 'Electronics', 'static/images/category_electronics.jpg'),
            ('Wireless Headphones', 149.99, 'Noise-cancelling headphones with 30-hour battery life', 'static/images/headphones.jpg', 'Electronics', 'static/images/category_electronics.jpg'),
            ('Smartwatch', 249.99, 'Track your fitness and stay connected with this premium smartwatch', 'static/images/smartwatch.jpg', 'Electronics', 'static/images/category_electronics.jpg'),
            ('Tablet', 499.99, '10-inch display with fast processor and long battery life', 'static/images/tablet.jpg', 'Electronics', 'static/images/category_electronics.jpg'),
            ('earbuds', 100.00, 'earbuds for playing music', 'static/images/earbuds.jpg', 'Electronics', 'static/images/category_electronics.jpg'),
            ('Shirt', 49.99, 'meduim size white shirt', 'static/images/shirt.jpg', 'Clothes', 'static/images/category_clothes.jpg')
        ]
        c.executemany('INSERT INTO products (name, price, description, image_url, category, category_image_url) VALUES (?, ?, ?, ?, ?, ?)', sample_products)
    conn.commit()
    conn.close()

def get_products():
    """Retrieve all products from the database"""
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('SELECT * FROM products')
    products = c.fetchall()
    conn.close()
    return products

def get_product(product_id):
    """Retrieve a specific product from the database"""
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = c.fetchone()
    conn.close()
    return product

def get_cart_items(user_id):
    """Retrieve cart items for a specific user"""
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('''
        SELECT p.id, p.name, p.price, c.quantity, p.image_url
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    ''', (user_id,))
    cart_items = c.fetchall()
    conn.close()
    return cart_items

def get_cart_total(user_id):
    """Calculate the total price of items in the cart"""
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('''
        SELECT SUM(p.price * c.quantity)
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    ''', (user_id,))
    total = c.fetchone()[0]
    conn.close()
    return total if total else 0

@app.route('/')
def home():
    """Render the home page"""
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        # Hash the password
        hashed_password = generate_password_hash(password)
        
        # Insert the new user into the database
        conn = sqlite3.connect('ecommerce.db')
        c = conn.cursor()
        
        try:
            c.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                     (username, hashed_password, email))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists.', 'error')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = sqlite3.connect('ecommerce.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            # Create session for the user
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash('You are now logged in!', 'success')
            return redirect(url_for('products'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')

def logout():
    """Handle user logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/products')
def products():
    """Render the products page with all products"""
    category = request.args.get('category', 'All')
    products = search_products(category=category) if category != 'All' else get_products()
    categories = get_categories()
    return render_template('products.html', products=products, categories=categories, current_category=category)
    
    
    
@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat interactions with the LLM"""
    user_input = request.json.get('message', '')
    
    # Get product context from database
    products = get_products()
    product_context = "Available products:\n"
    for product in products:
        # Only include name and price, not description
        product_context += f"- {product[1]}: ${product[2]}\n"
    
    # Combine user input with product context
    full_prompt = f"Context: {product_context}\nUser question: {user_input}\nPlease help with product recommendations or questions based on this specific product catalog. Be brief and helpful."
    
    # Get response from LangChain conversation
    response = conversation.predict(input=full_prompt)
    
    return jsonify({'response': response})

@app.route('/about')
def about():
    """Render the about page"""
    print(os.path.join(app.template_folder, 'about.html'))


    return render_template('about.html')

@app.route('/contact')
def contact():
    """Render the contact us page"""
    return render_template('contact.html')

@app.route('/policy')
def policy():
    """Render the policy page"""
    return render_template('policy.html')    

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """Add a product to the user's cart"""
    if 'user_id' not in session:
        flash('Please log in to add items to your cart.', 'error')
        return redirect(url_for('login'))
    
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    
    # Check if the product is already in the cart
    c.execute('SELECT id, quantity FROM cart WHERE user_id = ? AND product_id = ?',
             (session['user_id'], product_id))
    existing_item = c.fetchone()
    
    if existing_item:
        # Update quantity if item already in cart
        c.execute('UPDATE cart SET quantity = quantity + ? WHERE id = ?',
                 (quantity, existing_item[0]))
    else:
        # Add new item to cart
        c.execute('INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)',
                 (session['user_id'], product_id, quantity))
    
    conn.commit()
    conn.close()
    
    flash('Product added to cart!', 'success')
    return redirect(url_for('products'))

@app.route('/cart')
def cart():
    """Render the cart page with the user's items"""
    if 'user_id' not in session:
        flash('Please log in to view your cart.', 'error')
        return redirect(url_for('login'))
    
    cart_items = get_cart_items(session['user_id'])
    cart_total = get_cart_total(session['user_id'])
    
    return render_template('cart.html', cart_items=cart_items, cart_total=cart_total)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    """Update quantities in the cart"""
    if 'user_id' not in session:
        flash('Please log in to update your cart.', 'error')
        return redirect(url_for('login'))
    
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity'))
    
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    
    if quantity > 0:
        c.execute('UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ?',
                 (quantity, session['user_id'], product_id))
    else:
        c.execute('DELETE FROM cart WHERE user_id = ? AND product_id = ?',
                 (session['user_id'], product_id))
    
    conn.commit()
    conn.close()
    
    flash('Cart updated!', 'success')
    return redirect(url_for('cart'))

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    """Remove an item from the cart"""
    if 'user_id' not in session:
        flash('Please log in to remove items from your cart.', 'error')
        return redirect(url_for('login'))
    
    product_id = request.form.get('product_id')
    
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('DELETE FROM cart WHERE user_id = ? AND product_id = ?',
             (session['user_id'], product_id))
    conn.commit()
    conn.close()
    
    flash('Item removed from cart!', 'success')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
def checkout():
    """Process the checkout"""
    if 'user_id' not in session:
        flash('Please log in to checkout.', 'error')
        return redirect(url_for('login'))
    
    # Generate order ID
    order_id = str(uuid.uuid4())
    
    # In a real app, you would process payment here
    
    # Clear the user's cart
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('DELETE FROM cart WHERE user_id = ?', (session['user_id'],))
    conn.commit()
    conn.close()
    
    flash(f'Order placed successfully! Your order ID is {order_id}', 'success')
    return redirect(url_for('products'))



def search_products(query=None, category=None):
    """Search for products based on a query and/or category"""
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    
    params = []
    sql = 'SELECT * FROM products WHERE 1=1'
    
    if query:
        # Use LIKE with wildcards for partial matches
        sql += ' AND (name LIKE ? OR description LIKE ?)'
        search_param = f"%{query}%"
        params.extend([search_param, search_param])
    
    if category and category != 'All':
        sql += ' AND category = ?'
        params.append(category)
    
    c.execute(sql, params)
    
    products = c.fetchall()
    conn.close()
    return products    


@app.route('/search', methods=['GET'])
def search():
    """Handle product search"""
    query = request.args.get('q', '')
    category = request.args.get('category', 'All')
    
    if query or category != 'All':
        products = search_products(query, category)
    else:
        products = get_products()
    
    categories = get_categories()
    return render_template('products.html', products=products, search_query=query, categories=categories, current_category=category)
    
    
    
def get_categories():
    """Retrieve all unique categories from the database"""
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    c.execute('SELECT DISTINCT category FROM products ORDER BY category')
    categories = [row[0] for row in c.fetchall()]
    conn.close()
    return categories    
    
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
