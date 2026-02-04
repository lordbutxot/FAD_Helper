from app import app, login_manager
from models import User

with app.app_context():
    # Test user_loader
    user = User.query.get(1)
    print(f'Direct query: {user.username if user else "NOT FOUND"}')
    
    # Test what user_loader returns
    @login_manager.user_loader
    def test_loader(user_id):
        u = User.query.get(int(user_id))
        print(f'Loader called with {user_id}, returned: {u.username if u else "None"}')
        return u
    
    result = test_loader('1')
    print(f'Final result: {result}')
