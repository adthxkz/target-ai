#!/usr/bin/env python3
"""
Анализ файлов проекта для оптимизации
"""

import os
import glob

def analyze_project_files():
    """Анализирует файлы проекта"""
    
    # Основные категории файлов
    categories = {
        'main_code': [],
        'test_files': [],
        'documentation': [],
        'config_files': [],
        'deprecated': [],
        'temp_files': []
    }
    
    # Анализируем все файлы
    all_files = glob.glob('**/*', recursive=True)
    
    for file_path in all_files:
        if os.path.isfile(file_path):
            filename = os.path.basename(file_path)
            
            # Тестовые файлы
            if filename.startswith('test_') or '/tests/' in file_path:
                categories['test_files'].append(file_path)
            
            # Документация
            elif filename.endswith('.md'):
                categories['documentation'].append(file_path)
            
            # Конфигурационные файлы
            elif filename in ['requirements.txt', '.env', '.env.example', '.gitignore', 'render.yaml', 'pyproject.toml']:
                categories['config_files'].append(file_path)
            
            # Временные файлы
            elif '/tmp/' in file_path or filename.endswith('.tmp'):
                categories['temp_files'].append(file_path)
            
            # Устаревшие файлы (по именам)
            elif any(keyword in filename.lower() for keyword in ['old', 'backup', 'copy', '_v1', 'deprecated']):
                categories['deprecated'].append(file_path)
            
            # Основной код
            elif filename.endswith(('.py', '.yaml', '.yml', '.json')):
                categories['main_code'].append(file_path)
    
    return categories

def find_duplicates():
    """Находит потенциальные дубликаты"""
    
    duplicates = {
        'telegram_bots': ['telegram_bot.py', 'telegram_bot_v2.py', 'bot.py'],
        'apis': ['target_ai_api.py', 'flask_app.py', 'app/main.py'],
        'requirements': ['requirements.txt', 'requirements.txt.new'],
        'readmes': ['README.md', 'README_NEW.md']
    }
    
    return duplicates

def recommend_cleanup():
    """Рекомендации по очистке"""
    
    recommendations = {
        'delete': [
            # Множественные тестовые файлы
            'test_bot_integration.py',  # дублирует test_telegram_bot.py
            'test_simple_bot.py',       # простая версия
            'test_fixed_integration.py', # временный тест
            'test_bot_production.py',   # дублирует check_after_setup.py
            
            # Устаревшие файлы
            'telegram_bot.py',          # старая версия, есть v2
            'bot.py',                   # еще одна старая версия
            'target_ai_api.py',         # дублирует app/main.py
            'flask_app.py',             # fallback, не нужен
            'requirements.txt.new',     # дубликат
            'README_NEW.md',            # дубликат
            
            # Временные файлы
            'tmp/*',                    # все временные медиа файлы
            '__main__.py',              # пустой файл
            'setup.py',                 # не используется
        ],
        
        'move_to_folder': [
            # Тестовые файлы в папку tests/
            ('test_*.py', 'tests/'),
            ('check_*.py', 'tests/'),
            
            # Документация в docs/
            ('*.md', 'docs/'),
        ],
        
        'rename': [
            ('telegram_bot_v2.py', 'telegram_bot.py'),  # убрать v2 из названия
        ],
        
        'keep': [
            'app/',                     # основной код приложения
            'requirements.txt',         # основные зависимости
            '.env.example',            # шаблон переменных
            '.gitignore',              # правила Git
            'render.yaml',             # конфигурация деплоя
        ]
    }
    
    return recommendations

if __name__ == "__main__":
    print("🔍 Анализ файлов проекта Target AI")
    print("=" * 50)
    
    # Анализируем категории
    categories = analyze_project_files()
    
    print("\n📊 СТАТИСТИКА ФАЙЛОВ:")
    for category, files in categories.items():
        print(f"   {category}: {len(files)} файлов")
    
    # Показываем дубликаты
    duplicates = find_duplicates()
    print("\n🔄 НАЙДЕННЫЕ ДУБЛИКАТЫ:")
    for group, files in duplicates.items():
        existing_files = [f for f in files if os.path.exists(f)]
        if len(existing_files) > 1:
            print(f"   {group}: {existing_files}")
    
    # Рекомендации
    recommendations = recommend_cleanup()
    
    print("\n🗑️ РЕКОМЕНДАЦИИ К УДАЛЕНИЮ:")
    for file in recommendations['delete'][:10]:  # показываем первые 10
        if os.path.exists(file):
            size = os.path.getsize(file) if not file.endswith('*') else 0
            print(f"   ❌ {file} ({size} bytes)")
    
    print("\n📁 РЕКОМЕНДАЦИИ К РЕОРГАНИЗАЦИИ:")
    for pattern, folder in recommendations['move_to_folder']:
        print(f"   📂 {pattern} → {folder}")
    
    print("\n✂️ ПОТЕНЦИАЛЬНАЯ ЭКОНОМИЯ:")
    total_test_files = len(categories['test_files'])
    total_docs = len(categories['documentation'])
    print(f"   Тестовых файлов: {total_test_files}")
    print(f"   Документации: {total_docs}")
    print(f"   Временных файлов: {len(categories['temp_files'])}")
    
    print("\n💡 РЕКОМЕНДАЦИИ:")
    print("   1. Удалить устаревшие тестовые файлы")
    print("   2. Объединить дублирующуюся документацию")
    print("   3. Переместить тесты в папку tests/")
    print("   4. Удалить временные медиа файлы")
    print("   5. Оставить только основной telegram_bot_v2.py")
