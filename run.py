'''from elasticsearch import Elasticsearch
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
'''

from flask import Flask, redirect, render_template, request, url_for, jsonify
from elasticsearch import Elasticsearch
import os
import subprocess
import csv
from app import create_app



from flask import Flask, request, render_template
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")
# Create the Flask app via the factory function
app = create_app()

# Define the secret key for sessions
app.config['SECRET_KEY'] = os.urandom(24)

# Elasticsearch configuration
es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'csv'}

# Check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to process CSV files and index them into Elasticsearch
def index_to_elasticsearch(filepath):
    try:
        # Logic to parse the CSV file and index into Elasticsearch
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Create a document from CSV data and send to Elasticsearch
                es.index(index='customers_index', doc_type='_doc', body=row)
        print("Data successfully indexed into Elasticsearch.")
    except Exception as e:
        print(f"Error indexing data into Elasticsearch: {e}")

# Function to start Logstash processing
def start_logstash_processing(filepath):
    try:
        print(f"Starting Logstash processing for file: {filepath}")
        logstash_path = "/usr/share/logstash"  # Remplacer par le chemin réel de Logstash
        config_file = "/etc/logstash/conf.d/logstash_main.conf"  # Replace with the actual Logstash config path

        # Run Logstash via subprocess
        subprocess.run([f"{logstash_path}/bin/logstash", "-f", config_file], check=True)
        print(f"Logstash processing complete for file: {filepath}")

        # Logstash sends data to Elasticsearch
        index_to_elasticsearch(filepath)

    except subprocess.CalledProcessError as e:
        print(f"Error running Logstash: {e}")

# Upload file route
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        
        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Save the file
            file.save(filepath)
            
            # Start Logstash processing
            start_logstash_processing(filepath)
            
            return redirect(url_for('upload'))  # Redirect back to the upload page after upload
    
    return render_template('upload.html', title='Upload')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', title='Dashboard')


@app.route('/action', methods=['GET', 'POST'])
def action():
     return render_template("action.html")

    
@app.route("/customers", methods=['GET', 'POST'])
def customers_page():
    # Elasticsearch query setup
    customer_index = "customers_index"

    # Requête d'agrégation pour récupérer toutes les villes uniques
    city_aggregation_query = {
        "size": 0,
        "aggs": {
            "unique_cities": {
                "terms": {
                    "field": "City.keyword",  
                    "size": 100
                }
            }
        }
    }
    city_response = es.search(index=customer_index, body=city_aggregation_query)
    cities = [bucket['key'] for bucket in city_response['aggregations']['unique_cities']['buckets']]

    # Requête d'agrégation pour récupérer toutes les entreprises uniques
    company_aggregation_query = {
        "size": 0,
        "aggs": {
            "unique_companies": {
                "terms": {
                    "field": "Company.keyword",  
                    "size": 100
                }
            }
        }
    }
    company_response = es.search(index=customer_index, body=company_aggregation_query)
    companies = [bucket['key'] for bucket in company_response['aggregations']['unique_companies']['buckets']]

    # Handling filters from POST request
    selected_city = None
    selected_company = None
    customers = []

    if request.method == 'POST':
        selected_city = request.form.get('selected_city')
        selected_company = request.form.get('selected_company')

        # Build filtering query
        query = {
            "query": {
                "bool": {
                    "must": []
                }
            }
        }

        if selected_city:
            query['query']['bool']['must'].append({
                "match": {"City": selected_city}
            })

        if selected_company:
            query['query']['bool']['must'].append({
                "match": {"Company": selected_company}
            })

        # Execute the search with filters
        customer_response = es.search(index=customer_index, body=query)
        customers = [hit['_source'] for hit in customer_response['hits']['hits']]

        print(f"Filtered Customers: {customers}")  # Print to check data

    else:
        # If no filter, get all customers
        customer_response = es.search(index=customer_index, body={"size": 1000})
        customers = [hit['_source'] for hit in customer_response['hits']['hits']]

        print(f"All Customers: {customers}")  # Print to check data

    # Calculate total customers
    total_customers = len(customers)

    # Return to template with context
    return render_template(
        'customers.html',
        customers=customers,
        cities=cities,
        companies=companies,
        selected_city=selected_city,
        selected_company=selected_company,
        total_customers=total_customers
    )
'''@app.route("/sales", methods=['GET'])
def sales_page():
    sales_index = "logs-2024.11.16"
    selected_day = request.args.get('day')

    if selected_day:
        sales_query = {
            "query": {
                "bool": {
                    "filter": [
                        {
                            "term": {
                                "Order Date.keyword": f"4/{int(selected_day):02d}/2019"
                            }
                        }
                    ]
                }
            },
            "size": 0,
            "aggs": {
                "total_orders": {
                    "value_count": {
                        "field": "Order ID.keyword"
                    }
                }
            }
        }
        sales_response = es.search(index=sales_index, body=sales_query)
        total_orders = sales_response['aggregations']['total_orders']['value']
    else:
        total_orders = None
        selected_day = None

    return render_template('sales.html', total_orders=total_orders, selected_day=selected_day)
'''
@app.route("/sales", methods=['GET'])
def sales_page():
    sales_index = "logs-2024.11.16"
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    if min_price is not None and max_price is not None:
        # Construire la requête Elasticsearch pour filtrer les produits par plage de prix
        products_query = {
            "query": {
                "bool": {
                    "filter": [
                        {
                            "range": {
                                "Price Each": {
                                    "gte": min_price,
                                    "lte": max_price
                                }
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "products": {
                    "terms": {
                        "field": "Product.keyword",
                        "size": 10
                    }
                }
            }
        }

        # Exécuter la requête Elasticsearch
        products_response = es.search(index=sales_index, body=products_query)

        # Récupérer les produits trouvés
        products = [
            {
                "product": bucket["key"],
                "count": bucket["doc_count"]
            }
            for bucket in products_response["aggregations"]["products"]["buckets"]
        ]
    else:
        products = None

    return render_template('sales.html', products=products, min_price=min_price, max_price=max_price)


# Flask entry point
if __name__== "__main__":
    # Run the Flask application in debug mode
    app.run(debug=True, port=5003)