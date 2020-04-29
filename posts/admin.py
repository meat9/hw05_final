from django.contrib import admin
from .models import Post, Group, Comment

class PostAdmin(admin.ModelAdmin):
    # поля, отображаемые в админке
    list_display = ("pk", "text", "pub_date", "author") 
    # поиск по тексту постов
    search_fields = ("text",) 
    # фильтрация по дате
    list_filter = ("pub_date",) 
    empty_value_display = "-пусто-" # где пусто - там будет эта строка (для всех колонок)

admin.site.register(Post, PostAdmin)


class GroupAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "description") 
    search_fields = ("text",) 
    empty_value_display = "-пусто-"  
    

admin.site.register(Group, GroupAdmin)

class PostComment(admin.ModelAdmin):
    list_display = ("post", "author", "text", "created")

admin.site.register(Comment, PostComment)