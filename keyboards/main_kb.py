from keyboards import inline_builder

def inlineKb(isAdmin):
    if isAdmin:
        return admin_kb
    else:
        return client_kb

client_kb = inline_builder(text=["Советы", "Материалы", "Пробники"], callback_data=["tips", "materials", "tests"], sizes=3)

admin_kb = inline_builder(text=["Советы", "Материалы", "Пробники", "Выложить пост", "Добавить пост"], callback_data=["tips", "materials", "tests", "post_post", "add_post"], sizes=[3, 2])