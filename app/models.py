from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.timezone import now
from django.db.models import Avg, Count
# Create your models here.


class MyCustomerManager(BaseUserManager):
    def create_user(self, email ,first_name,last_name, mobile, password=None):
        if not email:
            raise ValueError("User must have email address.")
        if not first_name:
            raise ValueError("Users must have an first name")
        if not last_name:
            raise ValueError("Users must have an last name")
        if not mobile:
            raise ValueError("Users must have an mobile")
        

        user = self.model(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            mobile = mobile,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, first_name, last_name, mobile, password):
        user = self.create_user(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            mobile=mobile,
            password= password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Customer(AbstractBaseUser):
    first_name = models.CharField(verbose_name='first name',max_length=30)
    last_name = models.CharField(verbose_name='last name',max_length=30)
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    mobile = models.CharField(verbose_name='mobile no', max_length=12)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'mobile']

    objects = MyCustomerManager()

    def __str__(self):
        return self.email
    

    
    # Checking for permission
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True
    

CATEGORY = (
    ('National', 'National'),
    ('English Premier League', 'English Premier League'),
    ('La Liga', 'La Liga'),
    ('Bundesliga', 'Bundesliga'),
    ('Seria A', 'Seria A'),
    ('Ligue 1', 'Ligue 1'),
    ('Premiera Liga', 'Premiera Liga'),
    ('Indian Super League', 'Indian Super League'),
)

class Product(models.Model):
    name = models.CharField(max_length=50)
    o_price = models.FloatField(verbose_name='Original Price')
    d_price = models.FloatField(verbose_name='Discounted Price')
    category = models.CharField(choices=CATEGORY, max_length=40)
    star = models.IntegerField()
    unit = models.CharField(max_length=5)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    @property
    def get_discount(self):
        discont = ((self.o_price - self.d_price) / self.o_price) * 100
        return discont
    @property
    def saved(self):
        save = self.o_price - self.d_price
        return save

    @property
    def imageUrl(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    
    def averageReview(self):
        reviews = ProductReview.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def countReview(self):
        reviews = ProductReview.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count



class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.subject



class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)
    date_completed  = models.DateField(default=now)


    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_item(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.d_price * self.quantity
        return total

    def __str__(self):
        return str(self.product)
    

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    landmark = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    city = models.CharField(max_length=200, null=False)
    zipcode = models.IntegerField(null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.customer)



class Newsletter(models.Model):
    email = models.EmailField(max_length=60,)
    consent =models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.email


class Queries(models.Model):
    name = models.CharField(max_length=60)
    email = models.EmailField(max_length=60)
    subject = models.CharField(max_length=60)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name




