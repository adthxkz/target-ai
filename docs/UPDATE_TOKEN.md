# 🔄 Обновление токена в Render.com

## Новый токен готов к использованию!
✅ Токен протестирован и работает  
✅ Старый токен отозван  
✅ Интеграция проверена  

## Обновление в Render.com

### Шаг 1: Откройте настройки Render.com
1. Перейдите на https://render.com
2. Войдите в свой аккаунт
3. Найдите сервис `target-ai-prlm`
4. Нажмите на него

### Шаг 2: Обновите переменную окружения
1. В левом меню выберите **"Environment"**
2. Найдите переменную `TELEGRAM_BOT_TOKEN`
3. Нажмите на кнопку редактирования (карандаш)
4. Замените значение на:
   ```
   [НОВЫЙ_ТОКЕН_ОТ_BOTFATHER]
   ```
5. Нажмите **"Save Changes"**

### Шаг 3: Дождитесь перезапуска
- Render.com автоматически перезапустит сервис
- Это займет 2-3 минуты
- Следите за логами на вкладке "Logs"

### Шаг 4: Проверьте результат
После перезапуска в логах должно появиться:
```
База данных инициализирована
Telegram webhook установлен: https://target-ai-prlm.onrender.com/webhook/telegram
Telegram бот запущен
```

## Тестирование бота

### В Telegram:
1. Откройте: https://t.me/aidigitaltarget_bot
2. Нажмите "START" или отправьте `/start`
3. Бот должен ответить главным меню

### Через API:
```bash
# Проверка webhook
curl "https://api.telegram.org/bot[НОВЫЙ_ТОКЕН]/getWebhookInfo"

# Проверка здоровья сервера
curl "https://target-ai-prlm.onrender.com/health"
```

## Если что-то не работает

1. **Проверьте логи** в Render.com
2. **Убедитесь** что токен скопирован правильно
3. **Подождите** полного перезапуска (до 5 минут)
4. **Протестируйте** локально с новым токеном

## ⚠️ Безопасность
- Новый токен НЕ коммитится в Git
- Используется только через переменные окружения
- Старый токен корректно отозван
