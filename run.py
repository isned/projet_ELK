from elasticsearch import Elasticsearch
from flask import redirect, render_template, request, url_for
from app import create_app
import os

# Create the Flask app via the factory function
app = create_app()

# Define the secret key for sessions
app.config['SECRET_KEY'] = os.urandom(24)

# Register blueprint (if using blueprints)
# app.register_blueprint(main_blueprint)

@app.route('/')
def index():
    return render_template('index.html', title='Accueil')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        # Handle the uploaded file
        return redirect(url_for('upload'))  # Redirect back to the upload page after upload
    return render_template('upload.html', title='Upload')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', title='Dashboard')

# Configurez la clé secrète pour les sessions
app.config['SECRET_KEY'] = os.urandom(24)

@app.route('/action', methods=['GET', 'POST'])
def action():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

    if request.method == 'POST':
        filter_by = request.form.get('filter_by')
        
        # Default query to match all documents
        query = {
            "query": {
                "match_all": {}
            }
        }
        
        # Adjust the query based on the selected filter
        if filter_by:
            query = {
                "query": {
                    "term": {
                        filter_by: "active"  # This can be modified based on your exact filter condition
                    }
                }
            }

        response = es.search(index="customers_index", body=query)
    else:
        # Default fetch all data if no filter is applied
        response = es.search(index="customers_index", body={
            "query": {
                "match_all": {}
            }
        })
    
    customers = response['hits']['hits']
    
    customer_data = []
    for customer in customers:
        source = customer['_source']
        customer_data.append({
            'Index': customer['_id'],
            'Customer Id': source.get('customer_id', ''),
            'First Name': source.get('first_name', ''),
            'Last Name': source.get('last_name', ''),
            'Company': source.get('company', ''),
            'City': source.get('city', ''),
            'Country': source.get('country', ''),
            'Phone 1': source.get('phone1', ''),
            'Phone 2': source.get('phone2', ''),
            'Email': source.get('email', ''),
            'Subscription Date': source.get('subscription_date', ''),
            'Website': source.get('website', '')
        })

    return render_template('action.html', customers=customer_data)

@app.route('/action/filter', methods=['POST'])
def filter_customers():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

    filter_by = request.form.get('filter_by')

    query = {
        "query": {
            "term": {
                filter_by: "active"  # Modify this to match the correct value or condition for filtering
            }
        }
    }

    response = es.search(index="customers_index", body=query)

    customers = response['hits']['hits']
    
    customer_data = []
    for customer in customers:
        source = customer['_source']
        customer_data.append({
            'Index': customer['_id'],
            'Customer Id': source.get('customer_id', ''),
            'First Name': source.get('first_name', ''),
            'Last Name': source.get('last_name', ''),
            'Company': source.get('company', ''),
            'City': source.get('city', ''),
            'Country': source.get('country', ''),
            'Phone 1': source.get('phone1', ''),
            'Phone 2': source.get('phone2', ''),
            'Email': source.get('email', ''),
            'Subscription Date': source.get('subscription_date', ''),
            'Website': source.get('website', '')
        })

    return render_template('action.html', customers=customer_data)
if __name__ == "__main__":
    # Run the Flask application in debug mode
    app.run(debug=True, port=5003)






