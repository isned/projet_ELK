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
    # Define two indices: one for customers and one for logs
    customer_index = "customers_index"
    logs_index = "logs-2024.11.16"

    # Récupérer toutes les villes uniques pour les clients
    city_aggregation_query = {
        "size": 0,
        "aggs": {
            "unique_cities": {
                "terms": {
                    "field": "City.keyword",  # Utiliser le champ exact pour une agrégation
                    "size": 100  # Nombre maximum de villes à récupérer
                }
            }
        }
    }
    city_response = es.search(index=customer_index, body=city_aggregation_query)
    cities = [bucket['key'] for bucket in city_response['aggregations']['unique_cities']['buckets']]

    # Récupérer toutes les entreprises uniques pour les clients
    company_aggregation_query = {
        "size": 0,
        "aggs": {
            "unique_companies": {
                "terms": {
                    "field": "Company.keyword",  # Utiliser le champ exact pour une agrégation
                    "size": 100  # Nombre maximum d'entreprises à récupérer
                }
            }
        }
    }
    company_response = es.search(index=customer_index, body=company_aggregation_query)
    companies = [bucket['key'] for bucket in company_response['aggregations']['unique_companies']['buckets']]

    # Initialiser la liste des clients et les variables sélectionnées
    customers = []
    selected_city = None
    selected_company = None

    if request.method == 'POST':
        # Récupérer la ville et l'entreprise sélectionnées
        selected_city = request.form.get('selected_city')
        selected_company = request.form.get('selected_company')

        # Construire la requête de filtrage pour les deux indices
        query = {
            "query": {
                "bool": {
                    "must": []
                }
            }
        }

        if selected_city:
            query['query']['bool']['must'].append({
                "match": {
                    "City": selected_city  # Rechercher sur le champ City
                }
            })

        if selected_company:
            query['query']['bool']['must'].append({
                "match": {
                    "Company": selected_company  # Rechercher sur le champ Company
                }
            })

        # Exécuter la recherche filtrée pour les deux indices
        customer_response = es.search(index=customer_index, body=query)
        log_response = es.search(index=logs_index, body=query)

        # Collecter les résultats des deux indices
        customers = [hit['_source'] for hit in customer_response['hits']['hits']]
        logs = [hit['_source'] for hit in log_response['hits']['hits']]

    else:
        # Si pas de filtrage, récupérer tous les clients et logs
        customer_response = es.search(index=customer_index, body={"size": 10})
        log_response = es.search(index=logs_index, body={"size": 10})
        customers = [hit['_source'] for hit in customer_response['hits']['hits']]
        logs = [hit['_source'] for hit in log_response['hits']['hits']]

    # Calculer le total des clients et logs, filtré ou non filtré
    if not selected_city and not selected_company:
        # Total de tous les clients et logs sans filtre
        total_customers = es.count(index=customer_index)['count']
        total_logs = es.count(index=logs_index)['count']
    else:
        # Total des clients et logs après filtrage
        total_customers = len(customers)
        total_logs = len(logs)

    # Passer les deux ensembles de résultats (clients et logs) à la template
    return render_template(
        'action.html',
        customers=customers,
        logs=logs,  # Passer aussi les logs filtrés
        cities=cities,
        companies=companies,
        selected_city=selected_city,
        selected_company=selected_company,
        total_customers=total_customers,
        total_logs=total_logs  # Passer le total des logs à la template
    )


# Flask entry point
if __name__== "__main__":
    # Run the Flask application in debug mode
    app.run(debug=True, port=5003)