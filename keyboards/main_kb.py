import os

from keyboards import inline_builder

def inlineKb(isAdmin):
    if isAdmin:
        return admin_kb
    else:
        return client_kb
    
text_client = ["📚 Материалы", "📄 Пробники"]
callback_client = ["materials", "tests"]
sizes_client = [2]

text_admin = ["📚 Материалы", "📄 Пробники", "Тестирование", "Таблица лидеров", "✅ Добавить данные", "❌ Удалить данные", "✔ Выложить данные"]
calback_admin = ["materials", "tests", "testing", "leaderboard", "add", "delete_", "post"]
sizes_admin = [2, 2, 2, 1]

client_kb = inline_builder(text=text_client, callback_data=callback_client, sizes=sizes_client)

admin_kb = inline_builder(text=text_admin, callback_data=calback_admin, sizes=sizes_admin)

beta = os.getenv('BETA')
if beta:
    callback_client.append("testing")
    text_client.append("Тестирование")
    callback_client.append("leaderboard")
    text_client.append("Таблица лидеров")
    sizes_client.append(2)