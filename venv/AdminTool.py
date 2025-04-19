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
        
        # Create directory for product and category images if it doesn't exist
        os.makedirs('static/images', exist_ok=True)
        
        # Selected image paths
        self.selected_image_path = None
        self.selected_category_image_path = None
        
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
        
        # Load categories for use in product form
        self.categories = []
        self.load_categories_list()
    
    def init_products_tab(self):
        # Create frames for products tab
        products_left_frame = ttk.Frame(self.products_tab)
        products_left_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)
        
        products_right_frame = ttk.Frame(self.products_tab)
        products_right_frame.pack(side=tk.RIGHT, fill="both", expand=True, padx=5, pady=5)
        
        # Create treeview for products
        columns = ("ID", "Name", "Price", "Description", "Category")
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
        ttk.Label(product_form_frame, text="Product Image:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        
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
        
        # Category Selection - Now a combobox
        ttk.Label(product_form_frame, text="Category:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        
        # Create a frame for category selection and management
        category_frame = ttk.Frame(product_form_frame)
        category_frame.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        
        # Category ComboBox
        self.product_category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(
            category_frame, 
            textvariable=self.product_category_var,
            state="readonly"
        )
        self.category_combobox.pack(side=tk.LEFT, padx=5, fill="x", expand=True)
        
        # Category management buttons
        ttk.Button(category_frame, text="Add Category", command=self.add_category_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(category_frame, text="Edit Category", command=self.edit_category_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(category_frame, text="Delete Category", command=self.delete_category_dialog).pack(side=tk.LEFT, padx=5)
        
        # Buttons for product management
        buttons_frame = ttk.Frame(products_right_frame)
        buttons_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="New", command=self.new_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Save", command=self.save_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete", command=self.delete_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Refresh", command=self.load_products).pack(side=tk.LEFT, padx=5)
        
        # Load products from database
        self.load_products()
        
        # Update category dropdown
        self.update_category_dropdown()
    
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
    
    def load_categories_list(self):
        """Load categories from database to be used in product form"""
        try:
            conn = sqlite3.connect('ecommerce.db')
            c = conn.cursor()
            
            # Check if the categories table exists
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categories'")
            if not c.fetchone():
                # Create categories table if it doesn't exist
                c.execute('''
                    CREATE TABLE categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        image_url TEXT
                    )
                ''')
                conn.commit()
            
            c.execute('SELECT id, name, image_url FROM categories')
            self.categories = c.fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not load categories: {str(e)}")
    
    def update_category_dropdown(self):
        """Update the category dropdown with current categories"""
        self.load_categories_list()
        # Extract category names for the dropdown
        category_names = [category[1] for category in self.categories]
        self.category_combobox['values'] = category_names
        
        # If there's a current selection and it's still valid, keep it
        current = self.product_category_var.get()
        if current and current in category_names:
            self.category_combobox.set(current)
        elif category_names:
            # Otherwise select the first category if available
            self.category_combobox.set(category_names[0])
        else:
            # Clear if no categories
            self.product_category_var.set('')
    
    def select_image(self):
        """Open file dialog to select an image file for a product"""
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
    
    def process_image(self, name, is_category=False):
        """Process the selected image, convert if necessary, and save to static/images"""
        # Determine which image path to use based on whether it's a category or product
        selected_path = self.selected_category_image_path if is_category else self.selected_image_path
        
        if not selected_path:
            return None
        
        try:
            # Create safe filename with prefix for category images
            prefix = "category_" if is_category else ""
            safe_name = "".join(c if c.isalnum() else "_" for c in name)
            target_path = os.path.join('static', 'images', f"{prefix}{safe_name}.jpg")
            
            # Open the image with PIL
            img = Image.open(selected_path)
            
            # Convert to RGB if it's not already (needed for PNG with transparency)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save as JPG
            img.save(target_path, 'JPEG', quality=90)
            
            return f"/static/images/{prefix}{safe_name}.jpg"
        except Exception as e:
            messagebox.showerror("Image Processing Error", f"Failed to process image: {str(e)}")
            return None
    
    def select_category_image(self):
        """Open file dialog to select a category image file"""
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff")
        ]
        file_path = filedialog.askopenfilename(title="Select Category Image", filetypes=filetypes)
        
        if file_path:
            self.selected_category_image_path = file_path
            return file_path
        return None
    
    def add_category_dialog(self):
        """Show dialog to add a new category"""
        # Create custom dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Category")
        dialog.geometry("400x200")
        dialog.transient(self.root)  # Make dialog modal
        dialog.grab_set()
        
        # Category Name
        ttk.Label(dialog, text="Category Name:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var, width=30).grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Category Image
        ttk.Label(dialog, text="Category Image:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        # Frame for image selection
        image_frame = ttk.Frame(dialog)
        image_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Image path label
        image_path_var = tk.StringVar(value="No image selected")
        ttk.Label(image_frame, textvariable=image_path_var).pack(side=tk.RIGHT, padx=5)
        
        # Browse button
        def browse_image():
            path = self.select_category_image()
            if path:
                image_path_var.set(os.path.basename(path))
        
        ttk.Button(image_frame, text="Browse...", command=browse_image).pack(side=tk.LEFT, padx=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Save button
        def save_category():
            name = name_var.get().strip()
            
            # Validate form
            if not name:
                messagebox.showerror("Validation Error", "Category name is required", parent=dialog)
                return
            
            # Process image if selected
            image_url = None
            if self.selected_category_image_path:
                image_url = self.process_image(name, is_category=True)
            
            try:
                conn = sqlite3.connect('ecommerce.db')
                c = conn.cursor()
                
                # Insert new category
                c.execute('''
                    INSERT INTO categories (name, image_url)
                    VALUES (?, ?)
                ''', (name, image_url))
                
                conn.commit()
                conn.close()
                
                # Reset selected image path
                self.selected_category_image_path = None
                
                # Refresh categories dropdown
                self.update_category_dropdown()
                
                messagebox.showinfo("Success", "Category added successfully", parent=dialog)
                dialog.destroy()
            except sqlite3.IntegrityError as e:
                if "UNIQUE constraint failed: categories.name" in str(e):
                    messagebox.showerror("Database Error", "This category name already exists", parent=dialog)
                else:
                    messagebox.showerror("Database Error", f"Could not save category: {str(e)}", parent=dialog)
            except Exception as e:
                messagebox.showerror("Database Error", f"Could not save category: {str(e)}", parent=dialog)
        
        ttk.Button(buttons_frame, text="Save", command=save_category).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=10)
    
    def delete_category_dialog(self):
        """Show confirmation dialog to delete a category"""
        # Get current category
        category_name = self.product_category_var.get()
        if not category_name:
            messagebox.showerror("Error", "No category selected")
            return
        
        # Find category in the list
        category_data = None
        for cat in self.categories:
            if cat[1] == category_name:
                category_data = cat
                break
        
        if not category_data:
            messagebox.showerror("Error", "Category not found")
            return
        
        category_id = category_data[0]
        
        try:
            conn = sqlite3.connect('ecommerce.db')
            c = conn.cursor()
            
            # Check if any products use this category
            c.execute('SELECT COUNT(*) FROM products WHERE category = ?', (category_name,))
            count = c.fetchone()[0]
            conn.close()
            
            warning = ""
            if count > 0:
                warning = f"\n\nWarning: This category is used by {count} products. Deleting it will leave those products with no category."
            
            # Confirm deletion
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the category '{category_name}'?{warning}"):
                self.delete_category(category_id, category_name)
        except Exception as e:
            messagebox.showerror("Error", f"Error checking category usage: {str(e)}")
    
    def delete_category(self, category_id, category_name):
        """Delete a category from the database"""
        try:
            conn = sqlite3.connect('ecommerce.db')
            c = conn.cursor()
            
            # Get image URL before deleting
            c.execute('SELECT image_url FROM categories WHERE id = ?', (category_id,))
            result = c.fetchone()
            image_url = result[0] if result else None
            
            # Delete category
            c.execute('DELETE FROM categories WHERE id = ?', (category_id,))
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
            
            messagebox.showinfo("Success", "Category deleted successfully")
            
            # Update category dropdown
            self.update_category_dropdown()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not delete category: {str(e)}")
    
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
    
    def on_category_select(self, event):
        # Get selected item
        selected_items = self.categories_tree.selection()
        if not selected_items:
            return
        
        # Get category ID
        item = selected_items[0]
        category_id = self.categories_tree.item(item, "values")[0]
        
        # Fetch category details from database
        try:
            conn = sqlite3.connect('ecommerce.db')
            c = conn.cursor()
            c.execute('SELECT id, name, image_url FROM categories WHERE id = ?', (category_id,))
            category = c.fetchone()
            conn.close()
            
            if category:
                # Update form fields
                self.category_id_var.set(category[0])
                self.category_name_var.set(category[1])
                
                # Set image URL and reset selected image
                self.category_image_var.set(category[2] if category[2] else "")
                self.selected_category_image_path = None
                self.category_image_preview_label.config(text=f"Current image: {os.path.basename(category[2])}" if category[2] else "No image")
                
                # Remove thumbnail if exists
                if hasattr(self, 'category_image_thumbnail'):
                    self.category_image_thumbnail.config(image='')
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not fetch category details: {str(e)}")
    
    def new_product(self):
        # Clear form fields
        self.product_id_var.set("")
        self.product_name_var.set("")
        self.product_price_var.set("")
        self.product_description_text.delete(1.0, tk.END)
        self.product_image_var.set("")
        self.product_category_var.set("")
        self.selected_image_path = None
        self.image_preview_label.config(text="No image selected")
        
        # Remove thumbnail if exists
        if hasattr(self, 'image_thumbnail'):
            self.image_thumbnail.config(image='')
    
    def new_category(self):
        # Clear form fields
        self.category_id_var.set("")
        self.category_name_var.set("")
        self.category_image_var.set("")
        self.selected_category_image_path = None
        self.category_image_preview_label.config(text="No image selected")
        
        # Remove thumbnail if exists
        if hasattr(self, 'category_image_thumbnail'):
            self.category_image_thumbnail.config(image='')
    
    def save_product(self):
        # Get form values
        product_id = self.product_id_var.get()
        name = self.product_name_var.get()
        price_str = self.product_price_var.get()
        description = self.product_description_text.get(1.0, tk.END).strip()
        category = self.product_category_var.get()
        
        # Validate form
        if not name:
            messagebox.showerror("Validation Error", "Product name is required")
            return
        
        if not category:
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
            
            # Get category image URL
            c.execute('SELECT image_url FROM categories WHERE name = ?', (category,))
            category_image_result = c.fetchone()
            category_image_url = category_image_result[0] if category_image_result else None
            
            if product_id:  # Update existing product
                c.execute('''
                    UPDATE products
                    SET name = ?, price = ?, description = ?, image_url = ?, category = ?, category_image_url = ?
                    WHERE id = ?
                ''', (name, price, description, image_url, category, category_image_url, product_id))
                messagebox.showinfo("Success", "Product updated successfully")
            else:  # Insert new product
                c.execute('''
                    INSERT INTO products (name, price, description, image_url, category, category_image_url)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, price, description, image_url, category, category_image_url))
                messagebox.showinfo("Success", "Product added successfully")
            
            conn.commit()
            conn.close()
            
            # Reset selected image path
            self.selected_image_path = None
            
            # Refresh products list
            self.load_products()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not save product: {str(e)}")
    
    def save_category(self):
        # Get form values
        category_id = self.category_id_var.get()
        name = self.category_name_var.get()
        
        # Validate form
        if not name:
            messagebox.showerror("Validation Error", "Category name is required")
            return
        
        # Process image if selected
        image_url = self.category_image_var.get()  # Get existing URL first
        if self.selected_category_image_path:
            new_image_url = self.process_category_image(name)
            if new_image_url:
                image_url = new_image_url
        
        try:
            conn = sqlite3.connect('ecommerce.db')
            c = conn.cursor()
            
            if category_id:  # Update existing category
                c.execute('''
                    UPDATE categories
                    SET name = ?, image_url = ?
                    WHERE id = ?
                ''', (name, image_url, category_id))
                messagebox.showinfo("Success", "Category updated successfully")
            else:  # Insert new category
                c.execute('''
                    INSERT INTO categories (name, image_url)
                    VALUES (?, ?)
                ''', (name, image_url))
                messagebox.showinfo("Success", "Category added successfully")
            
            conn.commit()
            conn.close()
            
            # Reset selected image path
            self.selected_category_image_path = None
            
            # Refresh categories list
            self.load_categories()
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: categories.name" in str(e):
                messagebox.showerror("Database Error", "This category name already exists")
            else:
                messagebox.showerror("Database Error", f"Could not save category: {str(e)}")
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not save category: {str(e)}")
    
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
            try:
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
            except sqlite3.OperationalError:
                # Cart table might not exist yet
                pass
            
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
    
    def delete_category(self):
        # Get selected category ID
        category_id = self.category_id_var.get()
        if not category_id:
            messagebox.showerror("Error", "No category selected")
            return
        
        # Get category name for checking products
        category_name = self.category_name_var.get()
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this category?"):
            return
        
        try:
            conn = sqlite3.connect('ecommerce.db')
            c = conn.cursor()
            
            # Get image URL before deleting
            c.execute('SELECT image_url FROM categories WHERE id = ?', (category_id,))
            result = c.fetchone()
            image_url = result[0] if result else None
            
            # Check if any products use this category
            c.execute('SELECT COUNT(*) FROM products WHERE category = ?', (category_name,))
            count = c.fetchone()[0]
            
            if count > 0:
                # Category is used by products, ask user what to do
                if messagebox.askyesno("Warning", f"This category is used by {count} products. Delete anyway? (This will leave products with an invalid category)"):
                    pass  # Proceed with deletion
                else:
                    conn.close()
                    return
            
            # Delete category
            c.execute('DELETE FROM categories WHERE id = ?', (category_id,))
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
            
            messagebox.showinfo("Success", "Category deleted successfully")
            
            # Clear form and refresh list
            self.new_category()
            self.load_categories()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not delete category: {str(e)}")
    
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
            try:
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
            except sqlite3.OperationalError:
                # Cart table might not exist yet
                pass
            
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
    
    def edit_category_dialog(self):
        """Show dialog to edit an existing category"""
        # Get current category
        category_name = self.product_category_var.get()
        if not category_name:
            messagebox.showerror("Error", "No category selected")
            return
        
        # Find category in the list
        category_data = None
        for cat in self.categories:
            if cat[1] == category_name:
                category_data = cat
                break
        
        if not category_data:
            messagebox.showerror("Error", "Category not found")
            return
        
        # Create custom dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Category: {category_name}")
        dialog.geometry("400x200")
        dialog.transient(self.root)  # Make dialog modal
        dialog.grab_set()
        
        # Category ID (hidden)
        category_id = category_data[0]
        
        # Category Name
        ttk.Label(dialog, text="Category Name:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        name_var = tk.StringVar(value=category_name)
        ttk.Entry(dialog, textvariable=name_var, width=30).grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Category Image
        ttk.Label(dialog, text="Category Image:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        # Frame for image selection
        image_frame = ttk.Frame(dialog)
        image_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Current image info
        current_image = category_data[2] if len(category_data) > 2 else None
        image_path_var = tk.StringVar(
            value=f"Current: {os.path.basename(current_image)}" if current_image else "No image"
        )
        
        ttk.Label(image_frame, textvariable=image_path_var).pack(side=tk.RIGHT, padx=5)
        
        # Browse button
        def browse_image():
            path = self.select_category_image()
            if path:
                image_path_var.set(f"New: {os.path.basename(path)}")
        
        ttk.Button(image_frame, text="Browse...", command=browse_image).pack(side=tk.LEFT, padx=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Save button
        def save_category():
            updated_name = name_var.get().strip()
            if not updated_name:
                messagebox.showerror("Error", "Category name is required", parent=dialog)
                return
            
            # Process image if a new one was selected
            image_url = current_image
            if self.selected_category_image_path:
                new_image_url = self.process_image(updated_name, is_category=True)
                if new_image_url:
                    image_url = new_image_url
            
            # Update database
            try:
                conn = sqlite3.connect('ecommerce.db')
                c = conn.cursor()
                
                # Update category
                c.execute('UPDATE categories SET name = ?, image_url = ? WHERE id = ?', 
                          (updated_name, image_url, category_id))
                
                # If name changed, update product references to this category
                if updated_name != category_name:
                    c.execute('UPDATE products SET category = ? WHERE category = ?',
                              (updated_name, category_name))
                
                conn.commit()
                conn.close()
                
                # Reset selected image path
                self.selected_category_image_path = None
                
                # Update category dropdown and product list
                self.update_category_dropdown()
                self.load_products()
                
                messagebox.showinfo("Success", "Category updated successfully", parent=dialog)
                dialog.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Category name already exists", parent=dialog)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update category: {str(e)}", parent=dialog)
        
        ttk.Button(buttons_frame, text="Save", command=save_category).pack(side=tk.LEFT, padx=10)
        ttk.Button(buttons_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=10)

    
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
    # Create the database tables if they don't exist
    conn = sqlite3.connect('ecommerce.db')
    c = conn.cursor()
    
    # Check if category_image_url column exists in products table, add it if not
    c.execute("PRAGMA table_info(products)")
    columns = [column[1] for column in c.fetchall()]
    if 'category_image_url' not in columns:
        c.execute('ALTER TABLE products ADD COLUMN category_image_url TEXT')
    
    # Create products table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            image_url TEXT,
            category TEXT,
            category_image_url TEXT
        )
    ''')
    
    # Create cart table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    # Create categories table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            image_url TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    
    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop()