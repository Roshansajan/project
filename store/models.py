from django.db import models
from django.contrib.auth.models import User 
# Create your models here.
class Category(models.Model):
    name=models.CharField(max_length=255)
    image=models.ImageField(upload_to='category/images/')
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Color(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10, blank=True, null=True) 

    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name
    
class Product(models.Model):
    category=models.ForeignKey(Category,related_name='products',on_delete=models.CASCADE)
    name=models.CharField(max_length=225)
    price=models.DecimalField(max_digits=10,decimal_places=2)

    colors = models.ManyToManyField(Color, blank=True)
    sizes = models.ManyToManyField(Size, blank=True)


    description=models.TextField(blank=True)
    stock=models.PositiveIntegerField(default=0)
    is_available=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    @property
    def get_main_image(self):
        main_img = self.images.filter(is_main=True).first()
        if not main_img:
            main_img = self.images.first()
        return main_img
    
class ProductImage(models.Model):
    product=models.ForeignKey(Product,related_name='images',on_delete=models.CASCADE)
    image=models.ImageField(upload_to='products/images/')
    is_main=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name



class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return self.product.name
    


class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    order_number = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    order_note = models.CharField(max_length=255, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=255, choices=STATUS, default='New')
    ip = models.CharField(blank=True, max_length=255)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True) 
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.name