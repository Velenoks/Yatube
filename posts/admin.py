from django.contrib import admin

from .models import Group, Post, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author", "group")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class PostAdminGroup(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "description")
    search_fields = ("title",)
    empty_value_display = "-пусто-"


class PostAdminComment(admin.ModelAdmin):
    list_display = ("pk", "author", "text", "created", "post",)
    search_fields = ("post", "author", "text")
    list_filter = ("author", "created")


admin.site.register(Post, PostAdmin)
admin.site.register(Group, PostAdminGroup)
admin.site.register(Comment, PostAdminComment)
