from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Etablissement(models.Model):
    id_etablissement = models.CharField(max_length=50, primary_key=True, default=generate_uuid)
    nom_etablissement = models.CharField(max_length=50)
    email_pro = models.EmailField(max_length=100, unique=True)
    numtel = models.CharField(max_length=50)
    adresse_physique = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()
    password_hash = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=50, default=generate_uuid)

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)

    def __str__(self):
        return self.nom_etablissement

class Personne(models.Model):
    id_personne = models.AutoField(primary_key=True)
    email = models.CharField(max_length=50, unique=True)
    geolocalisation = models.CharField(max_length=255, blank=True)
    marque_tel = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.email

class Jour(models.Model):
    id_jour = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nom

class Category(models.Model):
    id_category = models.CharField(max_length=50, primary_key=True, default=generate_uuid)
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subcategories')

    def __str__(self):
        return self.name

class Tag(models.Model):
    id_tag = models.CharField(max_length=50, primary_key=True, default=generate_uuid)
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name='tags')
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    id_ingredient = models.AutoField(primary_key=True)
    nom_ingredient = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True)
    categorie = models.CharField(max_length=50)

    def __str__(self):
        return self.nom_ingredient

class Allergene(models.Model):
    id_allergene = models.AutoField(primary_key=True)
    nom_allergene = models.CharField(max_length=50)
    categorie_allergene = models.CharField(max_length=50)
    dangerosite = models.IntegerField()

    def __str__(self):
        return self.nom_allergene

class Item(models.Model):
    id_item = models.AutoField(primary_key=True)
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name='items')
    nom_plat = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True)
    disponibilite = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    prep_time = models.IntegerField()  # En minutes
    categories = models.ManyToManyField(Category, related_name='items')
    tags = models.ManyToManyField(Tag, related_name='items')
    ingredients = models.ManyToManyField(Ingredient, through='Contenir')
    jours_disponibilite = models.ManyToManyField(Jour, related_name='items')

    def __str__(self):
        return self.nom_plat

class Image(models.Model):
    id_image = models.AutoField(primary_key=True)
    url_image = models.ImageField(upload_to='items_images/')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return f"Image for {self.item.nom_plat}"

class Menu(models.Model):
    id_menu = models.CharField(max_length=50, primary_key=True, default=generate_uuid)
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name='menus')
    nom = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True)
    items = models.ManyToManyField(Item, through='Constituer')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

class Constituer(models.Model):
    id_menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    id_item = models.ForeignKey(Item, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)  # Pour l'ordre dans le menu

    class Meta:
        ordering = ['order']

class Contenir(models.Model):
    id_item = models.ForeignKey(Item, on_delete=models.CASCADE)
    id_ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantite = models.CharField(max_length=50)

    class Meta:
        unique_together = ('id_item', 'id_ingredient')

class Contenir_Allergene(models.Model):
    id_ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    id_allergene = models.ForeignKey(Allergene, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('id_ingredient', 'id_allergene')

class Concerner(models.Model):
    id_personne = models.ForeignKey(Personne, on_delete=models.CASCADE)
    id_allergene = models.ForeignKey(Allergene, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('id_personne', 'id_allergene')

class Donner_Avis(models.Model):
    
    id_avis = models.CharField(max_length=50, primary_key=True, default=generate_uuid)
    id_item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='avis',blank=True)
    
    id_etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name='avis')
    date_avis = models.DateField(auto_now_add=True)
    note = models.IntegerField()
    description=models.TextField(blank=True)

    class Meta:
        unique_together = ( 'id_etablissement', 'date_avis', 'id_avis','description','id_item')

class QRCode(models.Model):
    id_qrcode = models.CharField(max_length=50, primary_key=True, default=generate_uuid)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='qrcodes')
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    scans = models.IntegerField(default=0)

    def __str__(self):
        return f"QRCode for {self.menu.nom}"