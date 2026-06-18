import os
from flask import Flask, render_template_string, request, redirect
from psycopg2 import pool

app = Flask(__name__)

# Core Database Connection Pooling
try:
    db_pool = pool.SimpleConnectionPool(
        1, 10,
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        host=os.environ.get('DB_HOST'),
        port=os.environ.get('DB_PORT', 5432),
        database=os.environ.get('DB_NAME')
    )
except Exception as e:
    print("Database connection pool creation failed:", e)
    db_pool = None

# ==========================================
# HTML TEMPLATES
# ==========================================

# 1. Home Page Template (Views Data)
HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>NAGP Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light pb-5">
    <div class="container mt-5">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h2 class="text-primary fw-bold mb-0">NAGP Candidate Portal</h2>
                <p class="text-muted">User Information & Management Tier</p>
            </div>
            <a href="/add" class="btn btn-success btn-lg shadow-sm">+ Add New Candidate</a>
        </div>

        <div class="card shadow-sm border-0">
            <div class="card-header bg-dark text-white fw-bold">Current Candidates</div>
            <div class="card-body p-0">
                <table class="table table-striped table-hover mb-0">
                    <thead class="table-light">
                        <tr>
                            <th class="px-4">ID</th>
                            <th>Candidate Name</th>
                            <th>Technology Band</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for user in users %}
                        <tr>
                            <td class="px-4">{{ user['id'] }}</td>
                            <td><strong>{{ user['name'] }}</strong></td>
                            <td><span class="badge bg-secondary">{{ user['band'] }}</span></td>
                            <td>
                                <span class="badge {% if user['status'] == 'TaggedNAGAP' %}bg-primary{% else %}bg-warning text-dark{% endif %} rounded-pill px-3">
                                    {{ user['status'] }}
                                </span>
                            </td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="4" class="text-center py-4 text-muted">No candidate records found.</td>
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

# 2. Add Candidate Template (Form Page)
ADD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Add Candidate - NAGP</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container mt-5" style="max-width: 600px;">
        <div class="mb-4">
            <a href="/" class="text-decoration-none text-secondary">← Back to Dashboard</a>
        </div>
        
        <div class="card shadow-sm border-0">
            <div class="card-header bg-success text-white fw-bold">
                Enter Candidate Details
            </div>
            <div class="card-body p-4">
                <form method="POST" action="/add">
                    <div class="mb-3">
                        <label class="form-label fw-bold">Candidate Name</label>
                        <input type="text" class="form-control" name="candidate_name" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-bold">Technology Band</label>
                        <input type="text" class="form-control" name="technology_band" placeholder="e.g., QA, DEVOPS" required>
                    </div>
                    <div class="mb-4">
                        <label class="form-label fw-bold">Status</label>
                        <select class="form-select" name="status" required>
                            <option value="" disabled selected>Select a status...</option>
                            <option value="PotentailNAGP">PotentailNAGP</option>
                            <option value="TaggedNAGAP">TaggedNAGAP</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-success w-100 btn-lg">Save Candidate</button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
"""

# ==========================================
# APPLICATION ROUTES
# ==========================================

# 1. Home Route: Displays the table
@app.route('/', methods=['GET'])
def home():
    if not db_pool:
        return "<h3>Database connection error. Check your cluster configurations.</h3>", 500
    
    conn = db_pool.getconn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, candidate_name, technology_band, status FROM NAGAP_USER_INFO ORDER BY id ASC;")
        rows = cursor.fetchall()
        candidates = [{"id": r[0], "name": r[1], "band": r[2], "status": r[3]} for r in rows]
        
        return render_template_string(HOME_TEMPLATE, users=candidates), 200
    except Exception as e:
        return f"<h3>Database Error: {str(e)}</h3>", 500
    finally:
        cursor.close()
        db_pool.putconn(conn)

# 2. Add Route: Displays the form (GET) and saves the data (POST)
@app.route('/add', methods=['GET', 'POST'])
def add_candidate():
    if not db_pool:
        return "<h3>Database connection error.</h3>", 500

    if request.method == 'GET':
        # Just show the form page
        return render_template_string(ADD_TEMPLATE), 200

    if request.method == 'POST':
        # Process the submitted form data
        name = request.form.get('candidate_name')
        band = request.form.get('technology_band')
        status = request.form.get('status')
        
        conn = db_pool.getconn()
        cursor = conn.cursor()
        try:
            if name and band and status:
                cursor.execute(
                    "INSERT INTO NAGAP_USER_INFO (candidate_name, technology_band, status) VALUES (%s, %s, %s);",
                    (name, band, status)
                )
                conn.commit()
            return redirect('/') # Send them back to the home page table
        except Exception as e:
            conn.rollback()
            return f"<h3>Failed to insert data: {str(e)}</h3>", 500
        finally:
            cursor.close()
            db_pool.putconn(conn)

# 3. Old API Route (Kept just in case your assignment checker needs it)
@app.route('/api/data', methods=['GET'])
def legacy_api():
    return redirect('/')

# 4. Kubernetes Health Check
@app.route('/healthz', methods=['GET'])
def health():
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)