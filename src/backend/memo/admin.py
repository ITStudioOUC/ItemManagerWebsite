from django.contrib import admin
from .models import Memo, MemoImage


class MemoImageInline(admin.TabularInline):
    model = MemoImage
    extra = 0


@admin.register(Memo)
class MemoAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_at', 'updated_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MemoImageInline]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(MemoImage)
class MemoImageAdmin(admin.ModelAdmin):
    list_display = ['memo', 'alt_text', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['memo__title', 'alt_text']
