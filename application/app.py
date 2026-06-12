import os
from flask import Flask, render_template_string
from psycopg2 import pool

app = Flask(__name__)

# Core Database Connection Pooling
try:
    db_pool = pool.SimpleConnectionPool(
        1, 10,  # FinOps restriction: min 1, max 10 active connections
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        host=os.environ.get('DB_HOST'),
        port=os.environ.get('DB_PORT', 5432),
        database=os.environ.get('DB_NAME')
    )
except Exception as e:
    print("Database connection pool creation failed:", e)
    db_pool = None

# HTML Template for the User Interface (UI Dashboard)
HTML_UI_TEMPLATE = """
<!xltype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NAGP Candidate Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container mt-5">
        <div class="card shadow-sm">
            <div class="card-header bg-primary text-white">
                <h2 class="mb-0">NAGP Advance Portal - User Info Tier</h2>
            </div>
            <div class="card-body">
                <table class="table table-striped table-hover mt-3">
                    <thead class="table-dark">
                        <tr>
                            <th>ID</th>
                            <th>Candidate Name</th>
                            <th>Technology Band</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for user in users %}
                        <tr>
                            <td>{{ user.id }}</td>
                            <td><strong>{{ user.name }}</strong></td>
                            <td><span class="badge bg-secondary">{{ user.band }}</span></td>
                            <td>
                                <span class="badge {% if user.status == 'TaggedNAGAP' %}bg-success{% else %}bg-warning text-dark{% endif %}">
                                    {{ user.status }}
                                </span>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""

# The UI Dashboard Route
@app.route('/api/data', methods=['GET'])
def view_ui():
    if not db_pool:
        return "<h3>Database connection error. Check your cluster configurations.</h3>", 500
    
    conn = db_pool.getconn()
    try:
        cursor = conn.cursor()
        # Query your custom NAGAP_USER_INFO table
        cursor.execute("SELECT id, candidate_name, technology_band, status FROM NAGAP_USER_INFO;")
        rows = cursor.fetchall()
        
        # Structure the data entries dynamically for our UI template
        candidates = [{"id": r[0], "name": r[1], "band": r[2], "status": r[3]} for row in rows]
        
        # Inject data directly into the HTML UI layout
        return render_template_string(HTML_UI_TEMPLATE, users=candidates), 200
    except Exception as e:
        return f"<h3>An error occurred while fetching candidate records: {str(e)}</h3>", 500
    finally:
        cursor.close()
        db_pool.putconn(conn) # Return the connection to protect server memory

# Self-Healing Liveness probe endpoint required by Kubernetes
@app.route('/healthz', methods=['GET'])
def health():
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)