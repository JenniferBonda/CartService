#Jennifer Bonda
import requests
from flask import Flask, jsonify, request
app = Flask(__name__)

carts = [
    {"user_id": 1, "cart": {}},
    {"user_id": 2, "cart": {}},
    {"user_id": 3, "cart": {}},
    {"user_id": 4, "cart": {}},
    {"user_id": 5, "cart": {}}
]

product_url = 'https://productservice-omnh.onrender.com'

def get_products_data():
    response = requests.get(product_url)
    data = response.json()
    return data

def get_all_products():
    response = requests.get(f'{product_url}/products')
    data = response.json()
    return data

def get_product(product_id):
    response = requests.get(f'{product_url}/products/{product_id}')
    data = response.json()
    return data

def create_product(name):
    new_product = {"name": name}
    response = requests.post(f'{product_url}/products', json=new_product)
    data = response.json()
    return data

# Endpoint 1: Retrieve contents of user's cart
@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    cart = next((cart for cart in carts if cart["user_id"] == user_id), None)
    return jsonify({f"User {user_id}'s Cart": cart})

@app.route('/products', methods=['GET'])
def get_products():
    response = requests.get(f'{product_url}/products')
    product_data = response.json()
    return jsonify({"products": product_data})

@app.route('/cart/<int:user_id>/add/<int:product_id>', methods=['POST'])
def add_to_cart(user_id, product_id):

    response = requests.get(f'{product_url}/products')
    if 'quantity' in request.json:
        quantity = request.json['quantity']

        user_cart = next((cart for cart in carts if cart["user_id"] == user_id), None)

        response = requests.get(f'{product_url}/products/nameandprice/{product_id}')

        #Retrieve product name and price
                
        data = response.json()
                
        product_name = data['name']
        product_price = data['price']

        if user_cart:
            # Check if the product is in cart already
            if product_name in user_cart['cart']:
                # Update the quantity of product
                user_cart['cart'][product_name]['quantity'] += quantity
                quantity = user_cart['cart'][product_name]['quantity']

                quantity1 = request.json['quantity']

                response = requests.put(f'{product_url}/products/quantity/{product_id}/{quantity1}', json={"quantity": quantity})

                if response.status_code == 400:
                    user_cart['cart'][product_name]['quantity'] -= quantity1
                    quantity = user_cart['cart'][product_name]['quantity']
                    return jsonify({"message": "Not enough stock to reduce"})

            
        
            elif product_name not in user_cart['cart']:
                quantity1 = request.json['quantity']
                response = requests.put(f'{product_url}/products/quantity/{product_id}/{quantity1}', json={"quantity": quantity})
                if response.status_code == 400:
                    return jsonify({"message": "Not enough stock to reduce"})


            total_item_price = quantity * product_price

            user_cart['cart'][product_name] = {
                "product_id": product_id,
                "unit price": product_price,
                "quantity": quantity,
                "total item price": total_item_price
            }

            
            return jsonify({"message": f"Added {request.json['quantity']} units of product {product_id} to user {user_id}'s cart"})

    else:
        return jsonify({"error": "Quantity not given"}), 400
    

@app.route('/cart/<int:user_id>/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(user_id, product_id):
    
    response = requests.get(f'{product_url}/products')
    if 'quantity' in request.json:
        quantity = request.json['quantity']

        user_cart = next((cart for cart in carts if cart["user_id"] == user_id), None)

        response = requests.get(f'{product_url}/products/nameandprice/{product_id}')

        #Retrieve product name and price
        data = response.json()
                
        product_name = data['name']
        product_price = data['price']

        if user_cart:
            # Check if the product already in cart
            if product_name in user_cart['cart']:

                product_amount_in_cart = user_cart['cart'][product_name]['quantity']
                if request.json['quantity'] <= product_amount_in_cart: 
                # Update the quantity of product (decreasing)
                    product_amount_in_cart = user_cart['cart'][product_name]['quantity']
                    user_cart['cart'][product_name]['quantity'] -= quantity
                    quantity = user_cart['cart'][product_name]['quantity']

                elif request.json['quantity'] > product_amount_in_cart:
                    #updates the quantity in cart
                    if product_amount_in_cart != 0:
                        user_cart['cart'][product_name]['quantity'] += request.json['quantity']
                    quantity = user_cart['cart'][product_name]['quantity']
                    return jsonify({"message": "Not enough products in cart to remove"})


                quantity1 = request.json['quantity']
        

                response = requests.put(f'{product_url}/products/addbackquantity/{product_id}/{quantity1}', json={"quantity": quantity})
                
                total_item_price = quantity * product_price

                user_cart['cart'][product_name] = {
                    "product_id": product_id,
                    "unit price": product_price,
                    "quantity": quantity,
                    "total item price": total_item_price
                }

        

                return jsonify({"message": f"Removed {request.json['quantity']} units of product {product_id} from user {user_id}'s cart"})
            
            else:
                return jsonify({"error": "Item is not in the cart"})

    else:
        return jsonify({"error": "Quantity not given"}), 400
    


if __name__ == '__main__':
    app.run(debug=True)

  
