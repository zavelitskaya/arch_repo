import os
import shutil

# Удаляем старые миграции
migrations_dir = 'repository/migrations'
if os.path.exists(migrations_dir):
    shutil.rmtree(migrations_dir)
os.makedirs(migrations_dir)

with open(os.path.join(migrations_dir, '__init__.py'), 'w') as f:
    f.write('')

print("✅ Папка migrations создана")