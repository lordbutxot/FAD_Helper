from app import app
import os

print(f'Database URI: {app.config["SQLALCHEMY_DATABASE_URI"]}')
print(f'Current dir: {os.getcwd()}')
print(f'App root: {app.root_path}')

# Try to find the db file
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.db'):
            print(f'Found DB: {os.path.join(root, file)}')
