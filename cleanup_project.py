#!/usr/bin/env python3
"""
Скрипт очистки проекта от ненужных файлов
"""

import os
import shutil
import glob

def cleanup_project():
    """Очищает проект от ненужных файлов"""
    
    print("🧹 Очистка проекта Target AI")
    print("=" * 40)
    
    # Файлы для удаления
    files_to_delete = [
        # Устаревшие тестовые файлы
        'test_bot_integration.py',
        'test_simple_bot.py', 
        'test_fixed_integration.py',
        'test_bot_production.py',
        'test_openai_connection.py',
        
        # Устаревшие боты
        'telegram_bot.py',  # есть v2
        'bot.py',           # старая версия
        
        # Устаревшие API
        'target_ai_api.py', # дублирует app/main.py
        'flask_app.py',     # fallback не нужен
        
        # Дублирующиеся файлы
        'requirements.txt.new',
        'README_NEW.md',
        
        # Пустые файлы
        '__main__.py',
        'setup.py',
    ]
    
    # Папки для очистки
    folders_to_clean = [
        'tmp/',  # временные медиа файлы
    ]
    
    deleted_count = 0
    saved_bytes = 0
    
    # Удаляем файлы
    print("\n🗑️ Удаление файлов:")
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            try:
                size = os.path.getsize(file_path)
                os.remove(file_path)
                print(f"   ✅ Удален: {file_path} ({size} bytes)")
                deleted_count += 1
                saved_bytes += size
            except Exception as e:
                print(f"   ❌ Ошибка удаления {file_path}: {e}")
        else:
            print(f"   ⚠️ Не найден: {file_path}")
    
    # Очищаем папки
    print("\n📁 Очистка папок:")
    for folder in folders_to_clean:
        if os.path.exists(folder):
            try:
                files_in_folder = glob.glob(f"{folder}*")
                for file_path in files_in_folder:
                    if os.path.isfile(file_path):
                        size = os.path.getsize(file_path)
                        os.remove(file_path)
                        saved_bytes += size
                        deleted_count += 1
                print(f"   ✅ Очищена: {folder} ({len(files_in_folder)} файлов)")
            except Exception as e:
                print(f"   ❌ Ошибка очистки {folder}: {e}")
        else:
            print(f"   ⚠️ Не найдена: {folder}")
    
    # Переименовываем основной бот
    print("\n🔄 Переименование:")
    if os.path.exists('telegram_bot_v2.py'):
        if not os.path.exists('telegram_bot.py'):  # если старый уже удален
            try:
                shutil.move('telegram_bot_v2.py', 'telegram_bot.py')
                print(f"   ✅ telegram_bot_v2.py → telegram_bot.py")
            except Exception as e:
                print(f"   ❌ Ошибка переименования: {e}")
        else:
            print(f"   ⚠️ telegram_bot.py уже существует")
    
    # Создаем папки для организации
    print("\n📂 Создание структуры папок:")
    folders_to_create = ['docs', 'tests/integration', 'scripts']
    
    for folder in folders_to_create:
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
                print(f"   ✅ Создана: {folder}/")
            except Exception as e:
                print(f"   ❌ Ошибка создания {folder}: {e}")
        else:
            print(f"   ⚠️ Уже существует: {folder}/")
    
    # Перемещаем файлы
    print("\n📦 Перемещение файлов:")
    moves = [
        # Документация в docs/
        ('*.md', 'docs/'),
        # Оставшиеся тесты в tests/
        ('test_*.py', 'tests/'),
        ('check_*.py', 'tests/'),
        # Скрипты анализа
        ('analyze_project.py', 'scripts/'),
    ]
    
    for pattern, destination in moves:
        files = glob.glob(pattern)
        for file_path in files:
            if os.path.isfile(file_path):
                dest_path = os.path.join(destination, os.path.basename(file_path))
                try:
                    shutil.move(file_path, dest_path)
                    print(f"   ✅ {file_path} → {dest_path}")
                except Exception as e:
                    print(f"   ❌ Ошибка перемещения {file_path}: {e}")
    
    print("\n" + "=" * 40)
    print("📊 РЕЗУЛЬТАТ ОЧИСТКИ:")
    print(f"   Удалено файлов: {deleted_count}")
    print(f"   Освобождено места: {saved_bytes:,} bytes ({saved_bytes/1024:.1f} KB)")
    print("\n✨ Проект очищен и реорганизован!")
    
    return deleted_count, saved_bytes

if __name__ == "__main__":
    # Предупреждение
    print("⚠️ ВНИМАНИЕ: Этот скрипт удалит файлы!")
    print("Убедитесь что у вас есть backup или Git commit.")
    
    response = input("\nПродолжить? (y/N): ")
    
    if response.lower() in ['y', 'yes', 'да']:
        deleted, saved = cleanup_project()
        print(f"\n🎉 Очистка завершена: удалено {deleted} файлов, освобождено {saved/1024:.1f} KB")
    else:
        print("❌ Очистка отменена")
