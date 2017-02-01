from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.core.urlresolvers import reverse

# Create your models here.


class AdminUserProfile(models.Model):
	user = models.OneToOneField(User)
	sacco_name = models.CharField(max_length=255, null=False, blank=False)
	usertype = models.CharField(max_length=120, default="Admin")

	def __str__(self):
		return self.user.username



class MkulimaUserProfile(models.Model):
	user = models.OneToOneField(User)
	sacco_name = models.CharField(max_length=255, default="None")
	MKULIMA_OPTIONS = (

			('Goods', 'Goods'),
			('Services', 'Services'),
			('Both', 'Both'),

		)

	mkulimaoption = models.CharField(max_length=30, choices=MKULIMA_OPTIONS, null=False, blank=False, default="Goods")
	usertype = models.CharField(max_length=120, default="Mkulima")


	def __str__(self):
		return self.user.username
	

class CustomerUserProfile(models.Model):
	user = models.OneToOneField(User)
	bio = models.TextField(null=True, blank=True)
	usertype = models.CharField(max_length=120, default="Customer")
	

	def __str__(self):
		return self.user.username


class Product(models.Model):
	user = models.ForeignKey(User)
	name = models.CharField(max_length=255, null=True, blank=True)
	price = models.IntegerField(default=0)
	slug = models.SlugField(unique=True)
	taps = models.IntegerField(default=0)
	trashes = models.IntegerField(default=0)
	
	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('product-details', kwargs={'slug':self.slug})

class Order(models.Model):
	user = models.ForeignKey(User, default=1)
	product = models.ForeignKey(Product)
	timestamp = models.DateTimeField(auto_now_add=False, auto_now=False)

	def __str__(self):
		return self.product.name



def create_slug(instance, new_slug=None):

	#new_slug is none
	slug = slugify(instance.name)

	#new_slug exists
	if new_slug is not None:
		slug = new_slug
	qs = Product.objects.filter(slug=slug).order_by("-id")
	exists = qs.exists()

	if exists:
		new_slug = " %s-%s" %(slug, qs.first().id)
		return create_slug(instance, new_slug=new_slug)

	return slug


def pre_save_post_receiver(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = create_slug(instance)



pre_save.connect(pre_save_post_receiver, sender=Product)