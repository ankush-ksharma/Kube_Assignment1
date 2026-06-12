# Amy Approach to the Solution

## PHASE 1
### Step 1 Creating the Database
Init.sql file will create dataabased with some data

Writing standard SQL to create a table and insert 10 rows of data.
The assignment strictly requires the Database Tier to "include one table with 5–10 records" immediately when it starts. We will tell Kubernetes to run this script later when it launches the database.

### Step 2 Creating the API Application
I created a Python BAsed applciation to show this data using flash and PostgresSQL adapter.
This has 
app.py with falsh code
requirements.txt - dependencies

Docker file - with steps to run it in a docker

### Step 3 Build and Push docker images
1. Build the container image using your exact Docker Hub tag
```docker build -t ankushshwork/api-service:v2 .```
2. Push it to your repository
```docker push ankushshwork/api-service:v2```

