from django.contrib import admin
from .models import *

@admin.register(Etablissement)
class EtablissementAdmin(admin.ModelAdmin):
    list_display = ("nom_etablissement", "email_pro", "numtel", "is_verified")
    search_fields = ("nom_etablissement", "email_pro", "numtel")
    list_filter = ("is_verified",)


@admin.register(Personne)
class PersonneAdmin(admin.ModelAdmin):
    list_display = ("email", "geolocalisation", "marque_tel")
    search_fields = ("email",)


@admin.register(Jour)
class JourAdmin(admin.ModelAdmin):
    list_display = ("nom",)
    search_fields = ("nom",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "etablissement", "parent")
    list_filter = ("etablissement",)
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "etablissement")
    list_filter = ("etablissement",)
    search_fields = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("nom_ingredient", "categorie", "description")
    search_fields = ("nom_ingredient", "categorie")


@admin.register(Allergene)
class AllergeneAdmin(admin.ModelAdmin):
    list_display = ("nom_allergene", "categorie_allergene", "dangerosite")
    list_filter = ("categorie_allergene",)
    search_fields = ("nom_allergene",)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("nom_plat", "etablissement", "price", "prep_time", "disponibilite")
    list_filter = ("etablissement", "disponibilite", "categories", "tags", "jours_disponibilite")
    search_fields = ("nom_plat", "description")
    filter_horizontal = ("categories", "tags", "jours_disponibilite")


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("item", "url_image")
    search_fields = ("item__nom_plat",)


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("nom", "etablissement", "description", "created_at")
    list_filter = ("etablissement",)
    search_fields = ("nom",)


@admin.register(Constituer)
class ConstituerAdmin(admin.ModelAdmin):
    list_display = ("id_menu", "id_item", "order")
    list_filter = ("id_menu",)
    ordering = ("id_menu", "order")


@admin.register(Contenir)
class ContenirAdmin(admin.ModelAdmin):
    list_display = ("id_item", "id_ingredient", "quantite")
    search_fields = ("id_item__nom_plat", "id_ingredient__nom_ingredient")


@admin.register(Contenir_Allergene)
class ContenirAllergeneAdmin(admin.ModelAdmin):
    list_display = ("id_ingredient", "id_allergene")
    list_filter = ("id_allergene",)


@admin.register(Concerner)
class ConcernerAdmin(admin.ModelAdmin):
    list_display = ("id_personne", "id_allergene")
    list_filter = ("id_allergene",)


@admin.register(Donner_Avis)
class DonnerAvisAdmin(admin.ModelAdmin):
    list_display = ( "id_etablissement", "date_avis", "note")
    list_filter = ("note", "date_avis", "id_etablissement")


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ("menu", "url", "created_at", "scans")
    search_fields = ("menu__nom",)
    list_filter = ("created_at",)
