from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django import forms
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import (
	authenticate, 
	get_user_model, 
	login,
	logout,
	)

from .models import (
	AdminUserProfile, 
	MkulimaUserProfile, 
	CustomerUserProfile,
	Product,
	Order,
	
	)


User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
	email = forms.EmailField(label='Email Address')
	email2 = forms.EmailField(label='Confirm Email')
	password = forms.CharField(widget=forms.PasswordInput())

	class Meta:
		model = User
		fields = ['username', 'email', 'email2', 'password']

	def clean_email2(self):
		email = self.cleaned_data.get('email')
		email2 = self.cleaned_data.get('email2')
		if email != email2:
			raise forms.ValidationError("Emails must match")

		email_qs = User.objects.filter(email=email)
		if email_qs.exists():
			raise forms.ValidationError("This email has already been registered")

		return email

class NewSaccoForm(forms.ModelForm):
	class Meta:
		model = AdminUserProfile
		fields = ['sacco_name']

class MkulimaSaccoRegistrationForm(forms.ModelForm):
	class Meta:
		model = MkulimaUserProfile
		fields = ['sacco_name','mkulimaoption']

class SaccoMembersForm(forms.ModelForm):
	first_name = forms.CharField(required=True, label='First Name')
	last_name = forms.CharField(required=True, label='Last Name')
	email = forms.EmailField(required=True, label='Email')
	username = forms.CharField()
	
	class Meta:
		model = User
		fields = ['first_name','last_name','email','username']

	def clean_email(self):
		email = self.cleaned_data.get('email')
		email_qs = User.objects.filter(email=email)
		if email_qs.exists():
			raise forms.ValidationError("This email has already been registered")

		return email

#used together with UserReg form
class ClientProfileForm(forms.ModelForm):
	class Meta:
		model = CustomerUserProfile
		fields = ['bio']

class ProductForm(forms.ModelForm):
	name = forms.CharField(required=True, label='Product Name')
	price = forms.CharField(required=True, label='Product Price')

	class Meta:
		model = Product
		fields = ['name', 'price']


def admin_register_view(request, template_name="registration_form.html"):

	

	adminregistrationform = UserRegistrationForm(request.POST or None)

	saccoregistrationform = NewSaccoForm(request.POST or None)

	if adminregistrationform.is_valid() and saccoregistrationform.is_valid():
	

		password = adminregistrationform.cleaned_data.get('password')
		username = adminregistrationform.cleaned_data.get('username')
		sacco_name = saccoregistrationform.cleaned_data.get('sacco_name')

		admin = adminregistrationform.save()
		admin.set_password(password)
		admin.save()

		sacco = saccoregistrationform.save(commit=False)
		sacco.user = admin

		adminobject = User.objects.get(username=username)
		newgroup = Group.objects.create(name=sacco_name)
		adminobject.groups.add(Group.objects.get(name=newgroup.name))


		sacco.save()

		
	return render(request, template_name, {'adminregistrationform': adminregistrationform, 'saccoregistrationform':saccoregistrationform})


def add_sacco_members_view(request, pk=None, template_name="sacco_member_form.html"):

	saccoobject = get_object_or_404(AdminUserProfile, pk=pk)

	sacco_name = saccoobject.sacco_name
	admin_name = saccoobject.user.username

	saccomemberform = MkulimaSaccoRegistrationForm(request.POST or None)
	addsaccomembersform = SaccoMembersForm(request.POST or None)
	

	if addsaccomembersform.is_valid() and saccomemberform.is_valid():
		first_name = addsaccomembersform.cleaned_data.get('first_name')
		last_name = addsaccomembersform.cleaned_data.get('last_name')
		email = addsaccomembersform.cleaned_data.get('email')
		username = addsaccomembersform.cleaned_data.get('username')



		mkulima = addsaccomembersform.save()
		mkulima.set_password(email)
		
		mkulima.save()

		member = addsaccomembersform.save(commit=False)
		member.user = mkulima

		
		memberobject = User.objects.get(email=email)
		memberobject.groups.add(Group.objects.get(name=sacco_name))
		member.save()

	return render(request, template_name, {'sacco_name':sacco_name, 'admin_name':admin_name, 'addsaccomembersform':addsaccomembersform, 'saccomemberform':saccomemberform})



def add_mkulima_view(request, template_name="registration_form.html"):

	mkulimaregistrationform = UserRegistrationForm(request.POST or None)

	#will always be none
	addsaccomembersform = MkulimaSaccoRegistrationForm(request.POST or None)

	if mkulimaregistrationform.is_valid():
		password = mkulimaregistrationform.cleaned_data.get('password')
		#username = mkulimaregistrationform.cleaned_data.get('username')
		mkulima = mkulimaregistrationform.save()
		mkulima.set_password(password)
		mkulima.save()

		#default sacco value will be None
		member = addsaccomembersform.save(commit=False)
		member.user = mkulima
		member.save()

	return render(request, template_name, {'mkulimaregistrationform':mkulimaregistrationform, 'addsaccomembersform':addsaccomembersform})

def add_customer_view(request, template_name="registration_form.html"):
	customerregistrationform = UserRegistrationForm(request.POST or None)
	customerprofileform = ClientProfileForm(request.POST or None)

	if customerregistrationform.is_valid() and customerprofileform.is_valid():
		password = customerregistrationform.cleaned_data.get('password')

		customer = customerregistrationform.save()
		customer.set_password(password)
		customer.save()

		customerinfo = customerprofileform.save(commit=False)
		customerinfo.user = customer
		customerinfo.save()

	return render(request, template_name, {'customerregistrationform':customerregistrationform, 'customerprofileform':customerprofileform})

def add_product_view(request, template_name="product_form.html"):

	user = request.user
	
	mkulimaobj = MkulimaUserProfile.objects.all()
	
	
	

	if not request.user.is_authenticated() and not mkulimaobj.exists():
		raise Http404

	addproductform = ProductForm(request.POST or None)

	if addproductform.is_valid():

		product = addproductform.save(commit=False)
		product.user = request.user
		product.save()


	return render(request, template_name, {'addproductform':addproductform})

def edit_product_view(request, slug=None, template_name="product_form.html"):
	



	product = get_object_or_404(Product, slug=slug)

	if not request.user.is_authenticated() and request.user != product.user:
		raise Http404

	addproductform = ProductForm(request.POST or None, instance=product)

	if addproductform.is_valid():

		product = addproductform.save(commit=False)

		product.save()
		#return HttpResponseRedirect(product.get_absolute_url())


	return render(request, template_name, {'addproductform':addproductform})

def delete_product_view(request, template_name="product_form.html"):
	addproductform = ProductForm(request.POST or None)

	if addproductform.is_valid():

		product = addproductform.save(commit=False)
		product.user = request.user
		product.save()


	return render(request, template_name, {'addproductform':addproductform})

def product_list_view(request, template_name="product_list.html"):
	
	today = timezone.now()
	queryset_list = Product.objects.all()


	


	return render(request, template_name, {'today':today, 'products':queryset_list})
	
def product_details_view(request, slug=None, template_name="product_details.html"):
	
	product = get_object_or_404(Product, slug=slug)

	if addproductform.is_valid():

		product = addproductform.save(commit=False)
		product.user = request.user
		product.save()


	return render(request, template_name, {'addproductform':addproductform})

		
def tap_product(request):
	
	today = timezone.now()
	user = request.user

	product_id = None
	if request.method=="GET":
		product_id = request.GET['product_id']
		

	taps = 0
	if product_id:
		product = Product.objects.get(id=int(product_id))
		if product:
			taps = product.taps + 1
			product.taps = taps
			Order.objects.create(user=user, product=product, timestamp=timezone.now())

			product.save()
	

	return HttpResponse(taps)

def trash_product(request):
	

	product_id = None
	if request.method=="GET":
		product_id = request.GET['product_id']
		
		

	trashes = 0
	if product_id:
		product = Product.objects.get(id=int(product_id))
		if product:
			
			trashes = product.trashes + 1
			product.trashes = trashes

			product.save()
	

	return HttpResponse(trashes)




	

