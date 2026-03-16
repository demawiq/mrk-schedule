import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

User = get_user_model()

def create_superuser_from_file():
    try:
        with open('superuser_credentials.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if ':' not in line:
                    print(f"Ошибка в строке: {line}. Используйте формат username:password")
                    continue
                
                username, password = line.split(':', 1)
                
                if not User.objects.filter(username=username).exists():
                    User.objects.create_superuser(username=username, password=password, email='')
                    print(f"Суперпользователь '{username}' успешно создан!")
                else:
                    user = User.objects.get(username=username)
                    user.set_password(password)
                    user.is_superuser = True
                    user.is_staff = True
                    user.save()
                    print(f"Пароль для суперпользователя '{username}' обновлен.")
    except FileNotFoundError:
        print("Файл superuser_credentials.txt не найден.")

if __name__ == '__main__':
    create_superuser_from_file()
