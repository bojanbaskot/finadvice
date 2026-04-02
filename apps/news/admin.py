from django.contrib import admin
from .models import NewsCategory, NewsTag, NewsArticle, PropertyCategory, Property, PropertyImage, PropertyFeature


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(NewsTag)
class NewsTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'is_featured', 'views_count', 'published_at']
    list_filter = ['status', 'category', 'is_featured', 'published_at']
    list_editable = ['status', 'is_featured']
    search_fields = ['title', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    date_hierarchy = 'published_at'
    filter_horizontal = ['tags']


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 3
    fields = ['image', 'caption', 'is_cover', 'order']


@admin.register(PropertyCategory)
class PropertyCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'property_type']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'listing_type', 'country', 'city', 'price', 'currency', 'status', 'is_featured']
    list_filter = ['listing_type', 'country', 'status', 'category', 'is_featured']
    list_editable = ['status', 'is_featured']
    search_fields = ['title', 'city', 'address']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'price_per_sqm', 'created_at', 'updated_at']
    inlines = [PropertyImageInline]


@admin.register(PropertyFeature)
class PropertyFeatureAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    filter_horizontal = ['properties']
