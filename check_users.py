from app import app
from models import User

with app.app_context():
    users = User.query.all()
    print(f'Total users: {len(users)}')
    for u in users:
        print(f'  {u.id}: {u.username} (admin={getattr(u, "is_admin", None)})')
