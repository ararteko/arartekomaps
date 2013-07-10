from arartekomaps.mycomment.models import Comment
from django.contrib import admin

class CommentAdmin(admin.ModelAdmin):
    list_display = ('slug', 'author','public_date','parent')
    raw_id_fields = ('parent', 'author')   
    ordering = ('public_date',)
    search_fields = ['body','author']
    date_hierarchy = 'public_date'
    
admin.site.register(Comment, CommentAdmin)  