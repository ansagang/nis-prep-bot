from keyboards import inline_builder

def inlineKb(isAdmin):
    if isAdmin:
        return admin_kb
    else:
        return client_kb

client_kb = inline_builder(text=["📚 Материалы", "📄 Пробники"], callback_data=["materials", "tests"], sizes=2)

admin_kb = inline_builder(text=["📚 Материалы", "📄 Пробники", "✅ Добавить данные", "❌ Удалить данные", "✔ Выложить данные"], callback_data=["materials", "tests", "add", "delete_", "post"], sizes=[2, 2, 1])