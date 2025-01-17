import os

def create_directory_structure():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create main directories
    directories = [
        'backend/app',
        'backend/app/routes',
        'backend/app/models',
        'backend/app/utils',
        'frontend/src',
        'frontend/src/components',
        'frontend/src/views',
        'frontend/src/assets',
    ]
    
    for dir_path in directories:
        full_path = os.path.join(base_dir, dir_path)
        os.makedirs(full_path, exist_ok=True)
        
    # Create __init__.py files
    init_files = [
        'backend/app/__init__.py',
        'backend/app/routes/__init__.py',
        'backend/app/models/__init__.py',
        'backend/app/utils/__init__.py',
    ]
    
    for init_file in init_files:
        full_path = os.path.join(base_dir, init_file)
        with open(full_path, 'w') as f:
            pass

if __name__ == '__main__':
    create_directory_structure()
