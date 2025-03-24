import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sqlite3
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import os
import shutil
from werkzeug.security import generate_password_hash

class AdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("E-commerce Admin Tool")
        self.root.geometry("1000x600")
        
        # Create directory for product images if it doesn't exist
        os.makedirs('static/images', exist_ok=True)
        
        # Selected image path
        self.selected_image_path = None
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create tabs
        self.products_tab = ttk.Frame(self.notebook)
        self.users_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.products_tab, text="Products")
        self.notebook.add(self.users_tab, text="Users")
        
        # Initialize the products tab
        self.init_products_tab()
        
        # Initialize the users tab
        self.init_users_tab()
    
    def init_products_tab(self):
        # Create frames for products tab
        products_left_frame = ttk.Frame(self.products_tab)
        products_left_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)
        
        products_right_frame = ttk.Frame(self.products_tab)
        products_right_frame.pack(side=tk.RIGHT, fill="both", expand=True, padx=5, pady=5)
        
        # Create treeview for products
        columns = ("ID", "Name", "Price", "Description", "Category")  # Added Category
        self.products_tree = ttk.Treeview(products_left_frame, columns=columns, show="headings")
        
        # Set column headings
        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=100)
        
        self.products_tree.column("Description", width=200)
        
        # Add scrollbar to treeview
        products_scrollbar = ttk.Scrollbar(products_left_frame, orient="vertical", command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=products_scrollbar.set)
        
        # Pack treeview and scrollbar
        self.products_tree.pack(side=tk.LEFT, fill="both", expand=True)
        products_scrollbar.pack(side=tk.RIGHT, fill="y")
        
        # Bind select event
        self.products_tree.bind("<<TreeviewSelect>>", self.on_product_select)
        
        # Create form for product details
        product_form_frame = ttk.LabelFrame(products_right_frame, text="Product Details")
        product_form_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Product ID (disabled for editing)
        ttk.Label(product_form_frame, text="ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.product_id_var = tk.StringVar()
        ttk.Entry(product_form_frame, textvariable=self.product_id_var, state="readonly").grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Product Name
        ttk.Label(product_form_frame, text="Name:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.product_name_var = tk.StringVar()
        ttk.Entry(product_form_frame, textvariable=self.product_name_var).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Product Price
        ttk.Label(product_form_frame, text="Price:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.product_price_var = tk.StringVar()
        ttk.Entry(product_form_frame, textvariable=self.product_price_var).grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Product Description
        ttk.Label(product_form_frame, text="Description:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.product_description_text = ScrolledText(product_form_frame, height=5, width=30)
        self.product_description_text.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        # Product Image
        ttk.Label(product_form_frame, text="Image:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        
        # Create a frame for the image selection and preview
        image_frame = ttk.Frame(product_form_frame)
        image_frame.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        
        # Image URL (hidden but retained for compatibility)
        self.product_image_var = tk.StringVar()
        
        # Image Selection Button
        self.select_image_button = ttk.Button(image_frame, text="Select Image", command=self.select_image)
        self.select_image_button.pack(side=tk.LEFT, padx=5)
        
        # Image Preview Label
        self.image_preview_label = ttk.Label(image_frame, text="No image selected")
        self.image_preview_label.pack(side=tk.LEFT, padx=5)
        
        # Product Category - Added
        ttk.Label(product_form_frame, text="Category:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.product_category_var = tk.StringVar()
        ttk.Entry(product_form_frame, textvariable=self.product_category_var).grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        
        # Buttons for product management
        buttons_frame = ttk.Frame(products_right_frame)
        buttons_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="New", command=self.new_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Save", command=self.save_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete", command=self.delete_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Refresh", command=self.load_products).pack(side=tk.LEFT, padx=5)
        
        # Load products from database
        self.load_products()
    
    def init_users_tab(self):
        # Create frames for users tab
        users_left_frame = ttk.Frame(self.users_tab)
        users_left_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)
        
        users_right_frame = ttk.Frame(self.users_tab)
        users_right_frame.pack(side=tk.RIGHT, fill="both", expand=True, padx=5, pady=5)
        
        # Create treeview for users
        columns = ("ID", "Username", "Email")
        self.users_tree = ttk.Treeview(users_left_frame, columns=columns, show="headings")
        
        # Set column headings
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=100)
        
        # Add scrollbar to treeview
        users_scrollbar = ttk.Scrollbar(users_left_frame, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=users_scrollbar.set)
        
        # Pack treeview and scrollbar
        self.users_tree.pack(side=tk.LEFT, fill="both", expand=True)
        users_scrollbar.pack(side=tk.RIGHT, fill="y")
        
        # Bind select event
        self.users_tree.bind("<<TreeviewSelect>>", self.on_user_select)
        
        # Create form for user details
        user_form_frame = ttk.LabelFrame(users_right_frame, text="User Details")
        user_form_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # User ID (disabled for editing)
        ttk.Label(user_form_frame, text="ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.user_id_var = tk.StringVar()
        ttk.Entry(user_form_frame, textvariable=self.user_id_var, state="readonly").grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Username
        ttk.Label(user_form_frame, text="Username:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.username_var = tk.StringVar()
        ttk.Entry(user_form_frame, textvariable=self.username_var).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Email
        ttk.Label(user_form_frame, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.email_var = tk.StringVar()
        ttk.Entry(user_form_frame, textvariable=self.email_var).grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Password (for new users or reset)
        ttk.Label(user_form_frame, text="New Password:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(user_form_frame, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        # Buttons for user management
        buttons_frame = ttk.Frame(users_right_frame)
        buttons_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="New", command=self.new_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Save", command=self.save_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete", command=self.delete_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Reset Password", command=self.reset_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Refresh", command=self.load_users).pack(side=tk.LEFT, padx=5)
        
        # Load users from database
        self.load_users()
    
    def select_image(self):
        """Open file dialog to select an image file"""
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff")
        ]
        file_path = filedialog.askopenfilename(title="Select Image", filetypes=filetypes)
        
        if file_path:
            self.selected_image_path = file_path
            # Update image preview label
            self.image_preview_label.config(text=os.path.basename(file_path))
            
            # Attempt to show a thumbnail if possible
            try:
                img = Image.open(file_path)
                img = img.resize((50, 50), Image.LANCZOS)  # Create a small thumbnail
                photo = ImageTk.PhotoImage(img)
                
                # Create a new label for the image if it doesn't exist
                if not hasattr(self, 'image_thumbnail'):
                    self.image_thumbnail = tk.Label(self.image_preview_label.master)
                    self.image_thumbnail.pack(side=tk.LEFT, padx=5)
                
                self.image_thumbnail.config(image=photo)
                self.image_thumbnail.image = photo  # Keep a reference to prevent garbage collection
            except Exception as e:
                print(f"Error displaying image thumbnail: {e}")
    
    def process_image(self, product_name):
        """Process the selected image, convert if necessary, and save to static/images"""
        if not self.selected_image_path:
            return None
        
        try:
            # Create safe filename from product name
            safe_name = "".join(c if c.isalnum() else "_" for c in product_name)
            target_path = os.path.join('static', 'images', f"{safe_name}.jpg")
            
            # Open the image with PIL
            img = Image.open(self.selected_image_path)
            
            # Convert to RGB if it's not already (needed for PNG with transparency)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save as JPG
            img.save(target_path, 'JPEG', quality=90)
            
            return f"/static/images/{safe_name}.jpg"
        except Exception as e:
            messagebox.showerror("Image Processing Error", f"Failed to process image: {str(e)}")
            return None
    
    def load_products(self):
        # Clear existing items
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Connect to database and fetch products
        try:
            conn = sqlite3.connect('ecommerce.db')
            c = conn.cursor()
            c.execute('SELECT id, name, price, description, category FROM products')
            products = c.fetchall()
            conn.close()
            
            # Insert products into treeview
            for product in products:
                self.products_tree.insert("", "end", values=product)
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not load products: {str(e)}")
    
    def load_users(self):
        # Clear existing items
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        # Connect to database and fetch users
        try:
            conn = sqlite3.connect('ecommerce.db')
            c = conn.cursor()
            c.execute('SELECT id, username, email FROM users')
            users = c.fetchall()
            conn.close()
            
            # Insert users into treeview
            for user in users:
                self.users_tree.insert("", "end", values=user)
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not load users: {str(e)}")
    
    def on_product_select(self, event):
        # Get selected item
        selected_items = self.products_tree.selection()
        if not selected_items:
            return
        
        # Get product ID
        item = selected_items[0]
        product_id = self.products_tree.item(item, "values")[0]
        
        # Fetch product details from database
        try:
            conn = sqlite3.connect('ecommerce.db')
            c = conn.cursor()
            c.execute('SELECT id, name, price, description, image_url, category FROM products WHERE id = ?', (product_id,))
            product = c.fetchone()
            conn.close()
            
            if product:
                # Update form fields
                self.product_id_var.set(product[0])
                self.product_name_var.set(product[1])
                self.product_price_var.set(product[2])
                
                # Clear and set description text
                self.product_description_text.delete(1.0, tk.END)
                self.product_description_text.insert(tk.END, product[3] if product[3] else "")
                
                # Set image URL and reset selected image
                self.product_image_var.set(product[4] if product[4] else "")
                self.selected_image_path = None
                self.image_preview_label.config(text=f"Current image: {os.path.basename(product[4])}" if product[4] else "No image")
                
                # Set category
                self.product_category_var.set(product[5] if product[5] else "")
                
                # Remove thumbnail if exists
                if hasattr(self, 'image_thumbnail'):
                    self.image_thumbnail.config(image='')
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not fetch product details: {str(e)}")
    
    def on_user_select(self, event):
        # Get selected item
        selected_items = self.users_tree.selection()
        if not selected_items:
            return
        
        # Get user ID
        item = selected_items[0]
        user_id = self.users_tree.item(item, "values")[0]
        
        # Fetch user details from database
        try:
            conn = sqlite3.connect('ecommerce.db')
            c = conn.cursor()
            c.execute('SELECT id, username, email FROM users WHERE id = ?', (user_id,))
            user = c.fetchone()
            conn.close()
            
            if user:
                # Update form fields
                self.user_id_var.set(user[0])
                self.username_var.set(user[1])
                self.email_var.set(user[2])
                
                # Clear password field
                self.password_var.set("")
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not fetch user details: {str(e)}")
    
    def new_product(self):
        # Clear form fields
        self.product_id_var.set("")
        self.product_name_var.set("")
        self.product_price_var.set("")
        self.product_description_text.delete(1.0, tk.END)
        self.product_image_var.set("")
        self.product_category_var.set("")  # Added
        self.selected_image_path = None
        self.image_preview_label.config(text="No image selected")
        
        # Remove thumbnail if exists
        if hasattr(self, 'image_thumbnail'):
            self.image_thumbnail.config(image='')
    
    def save_product(self):
        # Get form values
        product_id = self.product_id_var.get()
        name = self.product_name_var.get()
        price_str = self.product_price_var.get()
        description = self.product_description_text.get(1.0, tk.END).strip()
        category = self.product_category_var.get()  # Added
        
        # Validate form
        if not name:
            messagebox.showerror("Validation Error", "Product name is required")
            return
        
        if not category:  # Added
            messagebox.showerror("Validation Error", "Product category is required")
            return
        
        try:
            price = float(price_str)
            if price < 0:
                raise ValueError("Price must be positive")
        except ValueError:
            messagebox.showerror("Validation Error", "Invalid price format")
            return
        
        # Process image if selected
        image_url = self.product_image_var.get()  # Get existing URL first
        if self.selected_image_path:
            new_image_url = self.process_image(name)
            if new_image_url:
                image_url = new_image_url
        
        try:
            conn = sqlite3.connect('ecommerce.db')
            c = conn.cursor()
            
            if product_id:  # Update existing product
                c.execute('''
                    UPDATE products
                    SET name = ?, price = ?, description = ?, image_url = ?, category = ?
                    WHERE id = ?
                ''', (name, price, description, image_url, category, product_id))
                messagebox.showinfo("Success", "Product updated successfully")
            else:  # Insert new product
                c.execute('''
                    INSERT INTO products (name, price, description, image_url, category)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, price, description, image_url, category))
                messagebox.showinfo("Success", "Product added successfully")
            
            conn.commit()
            conn.close()
            
            # Reset selected image path
            self.selected_image_path = None
            
            # Refresh products list
            self.load_products()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not save product: {str(e)}")
    
    def delete_product(self):
        # Get selected product ID
        product_id = self.product_id_var.get()
        if not product_id:
            messagebox.showerror("Error", "No product selected")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this product?"):
            return
        
        try:
            conn = sqlite3.connect('ecommerce.db')
            c = conn.cursor()
            
            # Get image URL before deleting
            c.execute('SELECT image_url FROM products WHERE id = ?', (product_id,))
            result = c.fetchone()
            image_url = result[0] if result else None
            
            # Check if product is in any carts
            c.execute('SELECT COUNT(*) FROM cart WHERE product_id = ?', (product_id,))
            count = c.fetchone()[0]
            
            if count > 0:
                # Product is in carts, ask user what to do
                if messagebox.askyesno("Warning", "This product is in users' carts. Delete anyway and remove from all carts?"):
                    # Delete from cart first
                    c.execute('DELETE FROM cart WHERE product_id = ?', (product_id,))
                else:
                    conn.close()
                    return
            
            # Delete product
            c.execute('DELETE FROM products WHERE id = ?', (product_id,))
            conn.commit()
            conn.close()
            
            # Try to delete image file if it exists
            if image_url and image_url.startswith('/static/images/'):
                try:
                    file_path = os.path.join('.', image_url.lstrip('/'))
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Warning: Could not delete image file: {e}")
            
            messagebox.showinfo("Success", "Product deleted successfully")
            
            # Clear form and refresh list
            self.new_product()
            self.load_products()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not delete product: {str(e)}")
    
    def new_user(self):
        # Clear form fields
        self.user_id_var.set("")
        self.username_var.set("")
        self.email_var.set("")
        self.password_var.set("")
    
    def save_user(self):
        # Get form values
        user_id = self.user_id_var.get()
        username = self.username_var.get()
        email = self.email_var.get()
        password = self.password_var.get()
        
        # Validate form
        if not username:
            messagebox.showerror("Validation Error", "Username is required")
            return
        
        if not email:
            messagebox.showerror("Validation Error", "Email is required")
            return
        
        try:
            conn = sqlite3.connect('ecommerce.db')
            c = conn.cursor()
            
            if user_id:  # Update existing user
                if password:  # If password is provided, update it
                    hashed_password = generate_password_hash(password)
                    c.execute('''
                        UPDATE users
                        SET username = ?, email = ?, password = ?
                        WHERE id = ?
                    ''', (username, email, hashed_password, user_id))
                else:  # Otherwise, don't change password
                    c.execute('''
                        UPDATE users
                        SET username = ?, email = ?
                        WHERE id = ?
                    ''', (username, email, user_id))
                messagebox.showinfo("Success", "User updated successfully")
            else:  # Insert new user
                if not password:
                    messagebox.showerror("Validation Error", "Password is required for new users")
                    conn.close()
                    return
                
                hashed_password = generate_password_hash(password)
                c.execute('''
                    INSERT INTO users (username, password, email)
                    VALUES (?, ?, ?)
                ''', (username, hashed_password, email))
                messagebox.showinfo("Success", "User added successfully")
            
            conn.commit()
            conn.close()
            
            # Refresh users list
            self.load_users()
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: users.username" in str(e):
                messagebox.showerror("Database Error", "This username is already taken")
            elif "UNIQUE constraint failed: users.email" in str(e):
                messagebox.showerror("Database Error", "This email is already in use")
            else:
                messagebox.showerror("Database Error", f"Could not save user: {str(e)}")
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not save user: {str(e)}")
    
    def delete_user(self):
        # Get selected user ID
        user_id = self.user_id_var.get()
        if not user_id:
            messagebox.showerror("Error", "No user selected")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this user?"):
            return
        
        try:
            conn = sqlite3.connect('ecommerce.db')
            c = conn.cursor()
            
            # Check if user has items in cart
            c.execute('SELECT COUNT(*) FROM cart WHERE user_id = ?', (user_id,))
            count = c.fetchone()[0]
            
            if count > 0:
                # User has items in cart, ask user what to do
                if messagebox.askyesno("Warning", "This user has items in their cart. Delete anyway and remove their cart?"):
                    # Delete from cart first
                    c.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
                else:
                    conn.close()
                    return
            
            # Delete user
            c.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "User deleted successfully")
            
            # Clear form and refresh list
            self.new_user()
            self.load_users()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not delete user: {str(e)}")
    
    def reset_password(self):
        # Get selected user ID
        user_id = self.user_id_var.get()
        if not user_id:
            messagebox.showerror("Error", "No user selected")
            return
        
        # Ask for new password
        new_password = simpledialog.askstring("New Password", "Enter new password:", show="*")
        if not new_password:
            return
        
        try:
            conn = sqlite3.connect('ecommerce.db')
            c = conn.cursor()
            
            # Update password
            hashed_password = generate_password_hash(new_password)
            c.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_password, user_id))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Password reset successfully")
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not reset password: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop()