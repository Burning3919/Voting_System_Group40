from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Customer, Poll, Option, Administrator

admin.site.register(Customer)
admin.site.register(Poll)
admin.site.register(Option)
admin.site.register(Administrator)