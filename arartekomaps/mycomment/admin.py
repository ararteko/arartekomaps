from arartekomaps.mycomment.models import Comment as MyComment
from django.contrib.comments import Comment
from django.contrib import admin

class CommentAdmin(admin.ModelAdmin):
    list_display = ('slug', 'author','public_date','parent','is_public','is_deleted')
    raw_id_fields = ('parent', 'author')   
    ordering = ('public_date',)
    search_fields = ['body','author']
    date_hierarchy = 'public_date'
    
admin.site.unregister(Comment)
admin.site.register(MyComment, CommentAdmin)  