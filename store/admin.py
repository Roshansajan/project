from django.contrib import admin
from django.utils.html import format_html
from .models import *

admin.site.register(Color)
admin.site.register(Size)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'image_preview', 'created_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    
    image_preview.short_description = 'Image'

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ['image_preview'] 
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.image.url)
        return "No Image"
    
    image_preview.short_description = 'Preview'

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    filter_horizontal = ('colors', 'sizes') 
    list_display = ['name', 'main_image_preview', 'category', 'price', 'stock', 'is_available']
    list_filter = ['category', 'is_available', 'created_at']
    search_fields = ['name', 'description']

    def main_image_preview(self, obj):
        main_img = obj.images.filter(is_main=True).first() or obj.images.first()
        if main_img and main_img.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', main_img.image.url)
        return "No Image"
    
    main_image_preview.short_description = 'Main Image'

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('product', 'quantity', 'product_price', 'color', 'size', 'ordered')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'email', 'city', 'order_total', 'status', 'is_ordered', 'created_at']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'last_name', 'email']
    list_per_page = 20
    inlines = [OrderProductInline]

    def full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(Cart)
admin.site.register(CartItem)