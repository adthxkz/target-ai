#!/usr/bin/env python3
"""
Предварительный просмотр очистки (без удаления)
"""

import os
import glob

def preview_cleanup():
    """Показывает что будет удалено/перемещено"""
    
    print("👀 ПРЕДВАРИТЕЛЬНЫЙ ПРОСМОТР ОЧИСТКИ")
    print("=" * 50)
    
    # Файлы для удаления
    files_to_delete = [
        'test_bot_integration.py',
        'test_simple_bot.py', 
        'test_fixed_integration.py',
        'test_bot_production.py',
        'test_openai_connection.py',
        'telegram_bot.py',
        'bot.py',
        'target_ai_api.py',
        'flask_app.py',
        'requirements.txt.new',
        'README_NEW.md',
        '__main__.py',
        'setup.py',
    ]
    
    total_size = 0
    delete_count = 0
    
    print("\n🗑️ ФАЙЛЫ ДЛЯ УДАЛЕНИЯ:")
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            total_size += size
            delete_count += 1
            print(f"   ❌ {file_path} ({size:,} bytes)")
        else:
            print(f"   ⚪ {file_path} (не найден)")
    
    # Временные файлы
    print("\n📁 ВРЕМЕННЫЕ ФАЙЛЫ:")
    if os.path.exists('tmp'):
        tmp_files = glob.glob('tmp/*')
        for file_path in tmp_files:
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                total_size += size
                delete_count += 1
                print(f"   ❌ {file_path} ({size:,} bytes)")
    else:
        print("   ⚪ tmp/ (папка не найдена)")
    
    # Перемещения
    print("\n📦 ФАЙЛЫ ДЛЯ ПЕРЕМЕЩЕНИЯ:")
    
    # Документация
    md_files = glob.glob('*.md')
    if md_files:
        print("   📚 Документация → docs/:")
        for file in md_files:
            print(f"      📄 {file}")
    
    # Тесты
    test_files = glob.glob('test_*.py') + glob.glob('check_*.py')
    if test_files:
        print("   🧪 Тесты → tests/:")
        for file in test_files:
            print(f"      🧪 {file}")
    
    # Переименования
    print("\n🔄 ПЕРЕИМЕНОВАНИЯ:")
    if os.path.exists('telegram_bot_v2.py'):
        print("   ✏️ telegram_bot_v2.py → telegram_bot.py")
    
    print("\n" + "=" * 50)
    print("📊 ИТОГО:")
    print(f"   Файлов к удалению: {delete_count}")
    print(f"   Размер удаляемых файлов: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    print(f"   Файлов к перемещению: {len(md_files + test_files)}")
    
    print("\n🎯 ОСНОВНЫЕ ПРЕИМУЩЕСТВА:")
    print("   ✅ Убирает дублирующиеся боты")
    print("   ✅ Удаляет устаревшие тесты")
    print("   ✅ Организует файлы по папкам")
    print("   ✅ Упрощает структуру проекта")
    
    print("\n⚠️ ВАЖНЫЕ ФАЙЛЫ ОСТАЮТСЯ:")
    important_files = [
        'app/',
        'telegram_bot_v2.py (→ telegram_bot.py)',
        'requirements.txt',
        '.env.example',
        '.gitignore',
        'render.yaml'
    ]
    for file in important_files:
        print(f"   ✅ {file}")

if __name__ == "__main__":
    preview_cleanup()
