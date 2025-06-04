from django.core.mail import send_mail
from ninja import Router, Form, File
from django.conf import settings
from ninja import NinjaAPI, File, Schema
from ninja.files import UploadedFile
from typing import List, Optional
from decimal import Decimal
from django.conf import settings



from ninja.files import UploadedFile
from ninja.security import HttpBearer
from core.models import (
    Etablissement, Personne, Jour, Category, Tag, Ingredient, Allergene, Item, Image, Menu,
    Constituer, Contenir, Contenir_Allergene, Concerner, Donner_Avis, QRCode
)
from core.schemas import (
    EtablissementIn, EtablissementUpdate, LoginIn, EtablissementOut, TokenOut,
    PersonneIn, PersonneOut, JourIn, JourOut, CategoryIn, CategoryOut, TagIn, TagOut,
    IngredientIn, IngredientOut, AllergeneIn, AllergeneOut, ImageIn, ImageOut,
    ItemIn, ItemOut, MenuIn, MenuOut, ContenirIn, ContenirOut, ContenirAllergeneIn,
    ConcernerIn, DonnerAvisIn, DonnerAvisOut, QRCodeOut, ErrorResponse, WarningResponse,QRCodeIn
)
import jwt
import uuid
import qrcode
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.http import FileResponse, HttpResponse
from datetime import datetime, timedelta
from typing import List

api = NinjaAPI()

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            etablissement = Etablissement.objects.get(id_etablissement=payload['id_etablissement'])
            return etablissement
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Etablissement.DoesNotExist):
            return None

def generate_token(id_etablissement):
    payload = {
        'id_etablissement': id_etablissement,
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

@api.post("/etablissement/register", response={201: EtablissementOut, 400: ErrorResponse})
def register(request, data: EtablissementIn):
    if Etablissement.objects.filter(email_pro=data.email_pro).exists():
        return 400, {"error": "Email already exists"}

    etablissement = Etablissement(**data.dict(exclude={'password'}))
    etablissement.set_password(data.password)
    etablissement.save()

    # Construction de l’URL de vérification
    verification_url = f"{settings.FRONTEND_URL}api/etablissement/verify/{etablissement.verification_token}"

    # Render du template HTML
    html_content = render_to_string("verify_email_url.html", {
        "nom": etablissement.nom_etablissement,
        "verification_url": verification_url,
    })

    # Création de l’email avec version texte + HTML
    email = EmailMultiAlternatives(
        subject='Vérifiez votre adresse email',
        body=f"Veuillez vérifier votre adresse en cliquant ici : {verification_url}",  # version texte
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[etablissement.email_pro],
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)

    return 201, etablissement


from django.http import HttpResponseRedirect
from django.urls import reverse

@api.get("/etablissement/verify/{token}")
def verify_email(request, token: str):
    try:
        etablissement = Etablissement.objects.get(verification_token=token)
        if etablissement.is_verified:
            return HttpResponseRedirect(f"{reverse('first')}?status=already_verified")
        etablissement.is_verified = True
        etablissement.save()
        return HttpResponseRedirect(f"{reverse('first')}?status=success")
    except Etablissement.DoesNotExist:
        return HttpResponseRedirect(f"{reverse('first')}?status=invalid")

@api.post("/login", response={200: TokenOut, 401: ErrorResponse})
def login(request, data: LoginIn):
    try:
        etablissement = Etablissement.objects.get(email_pro=data.email)
        if not etablissement.is_verified:
            return 401, {"error": "Email not verified"}
        if etablissement.check_password(data.password):
            token = generate_token(etablissement.id_etablissement)
            return {"token": token}
        return 401, {"error": "Invalid credentials"}
    except Etablissement.DoesNotExist:
        return 401, {"error": "Invalid credentials"}

@api.get("/etablissement/me", response=EtablissementOut, auth=AuthBearer())
def get_etablissement(request):
    etablissement = request.auth
    return EtablissementOut(
        id_etablissement=etablissement.id_etablissement,
        nom_etablissement=etablissement.nom_etablissement,
        email_pro=etablissement.email_pro,
        numtel=etablissement.numtel,
        adresse_physique=etablissement.adresse_physique,
        latitude=etablissement.latitude,
        longitude=etablissement.longitude,
        is_verified=etablissement.is_verified,
    )

@api.put("/etablissement/me", response=EtablissementOut, auth=AuthBearer())
def update_etablissement(request, data: EtablissementUpdate):
    etablissement = request.auth
    for key, value in data.dict(exclude_unset=True).items():
        setattr(etablissement, key, value)
    etablissement.save()

    return EtablissementOut(
        id_etablissement=etablissement.id_etablissement,
        nom_etablissement=etablissement.nom_etablissement,
        email_pro=etablissement.email_pro,
        numtel=etablissement.numtel,
        adresse_physique=etablissement.adresse_physique,
        latitude=etablissement.latitude,
        longitude=etablissement.longitude,
        is_verified=etablissement.is_verified,
    )

# Personne Endpoints
@api.post("/personnes", response={201: PersonneOut, 400: ErrorResponse})
def create_personne(request, data: PersonneIn):
    if Personne.objects.filter(email=data.email).exists():
        return 400, {"error": "Email already exists"}
    personne = Personne.objects.create(**data.dict())
    return 201, personne

@api.get("/personnes", response=List[PersonneOut])
def list_personnes(request):
    return Personne.objects.all()
@api.post("/jours", response={201: JourOut, 400: ErrorResponse})
def create_jour(request, data: JourIn):
    if Jour.objects.filter(nom=data.nom).exists():
        return 400, {"error": "Jour already exists"}
    jour = Jour.objects.create(**data.dict())
    return 201, JourOut(id_jour=jour.id_jour, nom=jour.nom)

@api.get("/jours", response=List[JourOut])
def list_jours(request):
    return [
        JourOut(id_jour=j.id_jour, nom=j.nom)
        for j in Jour.objects.all()
    ]


# Category Endpoints
@api.post("/categories", response={201: CategoryOut, 400: ErrorResponse}, auth=AuthBearer())
def create_category(request, data: CategoryIn):
    category = Category.objects.create(
        etablissement=request.auth,
        name=data.name,
        parent_id=data.parent_id
    )
    return 201, CategoryOut(
        id_category=category.id_category,
        name=category.name,
        parent_id=category.parent_id
    )

@api.get("/categories", response=List[CategoryOut], auth=AuthBearer())
def list_categories(request):
    return [
        CategoryOut(
            id_category=c.id_category,
            name=c.name,
            parent_id=c.parent_id
        )
        for c in Category.objects.filter(etablissement=request.auth)
    ]

# Tag Endpoints
@api.post("/tags", response={201: TagOut, 400: ErrorResponse}, auth=AuthBearer())
def create_tag(request, data: TagIn):
    tag = Tag.objects.create(etablissement=request.auth, **data.dict())
    return 201, TagOut(id_tag=tag.id_tag, name=tag.name)

@api.get("/tags", response=List[TagOut], auth=AuthBearer())
def list_tags(request):
    return [
        TagOut(id_tag=t.id_tag, name=t.name)
        for t in Tag.objects.filter(etablissement=request.auth)
    ]
@api.post("/ingredients", response={201: IngredientOut, 400: ErrorResponse})
def create_ingredient(request, data: IngredientIn):
    ingredient = Ingredient.objects.create(**data.dict())
    return 201, IngredientOut(
        id_ingredient=ingredient.id_ingredient,
        nom_ingredient=ingredient.nom_ingredient,
        description=ingredient.description or "",
        categorie=ingredient.categorie
    )

@api.get("/ingredients", response=List[IngredientOut])
def list_ingredients(request):
    return [
        IngredientOut(
            id_ingredient=i.id_ingredient,
            nom_ingredient=i.nom_ingredient,
            description=i.description or "",
            categorie=i.categorie
        )
        for i in Ingredient.objects.all()
    ]
@api.post("/allergenes", response={201: AllergeneOut, 400: ErrorResponse})
def create_allergene(request, data: AllergeneIn):
    allergene = Allergene.objects.create(**data.dict())
    return 201, AllergeneOut(
        id_allergene=allergene.id_allergene,
        nom_allergene=allergene.nom_allergene,
        categorie_allergene=allergene.categorie_allergene,
        dangerosite=allergene.dangerosite
    )

@api.get("/allergenes", response=List[AllergeneOut])
def list_allergenes(request):
    return [
        AllergeneOut(
            id_allergene=a.id_allergene,
            nom_allergene=a.nom_allergene,
            categorie_allergene=a.categorie_allergene,
            dangerosite=a.dangerosite
        )
        for a in Allergene.objects.all()
    ]
@api.post("/items", response={201: ItemOut, 400: ErrorResponse}, auth=AuthBearer())
def create_item(
    request,
    nom_plat: str = Form(...),
    description: Optional[str] = Form(None),
    disponibilite: bool = Form(...),
    price: Decimal = Form(...),
    prep_time: int = Form(...),
    category_ids: List[str] = Form(...),
    tag_ids: List[str] = Form(...),
    ingredient_ids: List[int] = Form(...),
    jour_ids: List[int] = Form(...),
    quantites: List[str] = Form(...),
    image_files: List[UploadedFile] = File(default=[])
):
    print(
        description,
        disponibilite,
        price,
        prep_time,
        category_ids,
        tag_ids,
        ingredient_ids,
        jour_ids,
        quantites,
        image_files
    )

    if len(ingredient_ids) != len(quantites):
        return 400, {"error": "Le nombre d'ingrédients ne correspond pas au nombre de quantités"}

    try:
        item = Item.objects.create(
            etablissement=request.auth,
            nom_plat=nom_plat,
            description=description,
            disponibilite=disponibilite,
            price=price,
            prep_time=prep_time
        )

        for category_id in category_ids:
            category = Category.objects.get(id_category=category_id, etablissement=request.auth)
            item.categories.add(category)

        for tag_id in tag_ids:
            tag = Tag.objects.get(id_tag=tag_id, etablissement=request.auth)
            item.tags.add(tag)

        for jour_id in jour_ids:
            jour = Jour.objects.get(id_jour=jour_id)
            item.jours_disponibilite.add(jour)

        seen_ingredients = set()
        for idx, ingredient_id in enumerate(ingredient_ids):
            if ingredient_id in seen_ingredients:
                continue  # Ignore les doublons
            seen_ingredients.add(ingredient_id)

            ingredient = Ingredient.objects.get(id_ingredient=ingredient_id)
            Contenir.objects.create(
                id_item=item,
                id_ingredient=ingredient,
                quantite=quantites[idx]
            )

        for image_file in image_files:
            Image.objects.create(item=item, url_image=image_file)
        item_out = ItemOut(
            id_item=item.id_item,
            nom_plat=item.nom_plat,
            description=item.description,
            disponibilite=item.disponibilite,
            price=item.price,
            prep_time=item.prep_time,
            categories=[CategoryOut.model_validate(c) for c in item.categories.all()],
            tags=[TagOut.model_validate(t) for t in item.tags.all()],
            ingredients=[IngredientOut.model_validate(c.id_ingredient) for c in Contenir.objects.filter(id_item=item)],
            jours_disponibilite=[JourOut.model_validate(j) for j in item.jours_disponibilite.all()],
          images = [
    ImageOut(
        id_image=image.id_image,
        url_image=image.url_image.url,   # .url renvoie une chaîne valide
        id_item=image.item.id_item       # s'assurer que c’est un int
    )
    for image in item.images.all()
]
        )
        return 201, item_out    

        


    except Exception as e:
        print("Erreur:", str(e))
        return 400, {"error": f"Erreur lors de la création de l'item: {str(e)}"}


def serialize_item(item: Item) -> ItemOut:
    return ItemOut(
        id_item=item.id_item,
        nom_plat=item.nom_plat,
        description=item.description,
        disponibilite=item.disponibilite,
        price=item.price,
        prep_time=item.prep_time,
        categories=[
            CategoryOut(id_category=c.id_category, name=c.name)
            for c in item.categories.all()
        ],
        tags=[
            TagOut(id_tag=t.id_tag, name=t.name)
            for t in item.tags.all()
        ],
        ingredients=[
            IngredientOut(
                id_ingredient=i.id_ingredient,
                nom_ingredient=i.nom_ingredient,
                description=i.description,
                categorie=i.categorie
            ) for i in item.ingredients.all()
        ],
        jours_disponibilite=[
            JourOut(id_jour=j.id_jour, nom=j.nom)
            for j in item.jours_disponibilite.all()
        ],
        images= [
            ImageOut(
                id_image=img.id_image,
                url_image=img.url_image.url,  # <- .url pour obtenir le lien réel
                id_item=img.item.id_item      # <- on passe l'ID de l'objet
            ) for img in item.images.all()
        ]
    )


@api.get("/items", response=List[ItemOut], auth=AuthBearer())
def list_items(request):
    items = Item.objects.all().filter(etablissement=request.auth).prefetch_related("categories", "tags", "ingredients", "jours_disponibilite", "images")
    return [serialize_item(item) for item in items]

@api.delete("/items/{item_id}", response={204: None, 404: ErrorResponse}, auth=AuthBearer())
def delete_item(request, item_id: int):
    try:
        item = Item.objects.get(id_item=item_id , etablissement=request.auth)
        item.delete()
        return 204, None
    except Item.DoesNotExist:
        return 404, {"error": "Item introuvable"}
    
@api.post("/menus", response={201: MenuOut, 400: ErrorResponse}, auth=AuthBearer())
def create_menu(request, data: MenuIn):
    menu = Menu.objects.create(
        etablissement=request.auth,
        nom=data.nom,
        description=data.description
    )
    for idx, item_id in enumerate(data.item_ids):
        try:
            item = Item.objects.get(id_item=item_id, etablissement=request.auth)
            Constituer.objects.create(id_menu=menu, id_item=item, order=idx)
        except Item.DoesNotExist:
            return 400, {"error": f"Item avec id {item_id} introuvable."}

    items = [
        serialize_item(item)
        for item in menu.items.all()
    ]

    return 201, MenuOut(
        id_menu=menu.id_menu,
        nom=menu.nom,
        description=menu.description or "",
        items=items
    )
    
@api.get("/menus", response=List[MenuOut], auth=AuthBearer())
def list_menus(request):
    menus = Menu.objects.filter(etablissement=request.auth)
    return [
        MenuOut(
            id_menu=m.id_menu,
            nom=m.nom,
            description=m.description or "",
            items=[serialize_item(i) for i in m.items.all()]
        )
        for m in menus
    ]
@api.get("/menus/{menu_id}/export-pdf", auth=AuthBearer())
def export_menu_pdf(request, menu_id: str):
    try:
        menu = Menu.objects.get(id_menu=menu_id, etablissement=request.auth)
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.drawString(100, 750, f"Menu: {menu.nom}")
        p.drawString(100, 730, f"Description: {menu.description or 'No description'}")
        y = 700
        for item in menu.items.all():
            p.drawString(100, y, f"- {item.nom_plat}: {item.price} EUR")
            y -= 20
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, filename=f"{menu.nom}.pdf")
    except Menu.DoesNotExist:
        return {"error": "Menu not found"}, 404
import os 
@api.post("/qrcodes", response={201: QRCodeOut, 400: ErrorResponse}, auth=AuthBearer())
def create_qrcode(request, data: QRCodeIn):
    try:
        menu = Menu.objects.get(id_menu=data.menu_id, etablissement=request.auth)

        # Génère l'URL cible pour le menu
        target_url = f"{settings.FRONTEND_URL}menus/{data.menu_id}"

        # Génère le QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(target_url)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        # Crée un nom de fichier unique
        filename = f"{uuid.uuid4()}.png"
        folder = os.path.join(settings.MEDIA_ROOT, "qrcodes")
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)
        img.save(filepath)

        # Construit l'URL publique vers l'image
        image_url = f"/qrcodes/{filename}"

        # Crée et enregistre le QRCode dans la base de données
        qr_code = QRCode.objects.create(
            id_qrcode=str(uuid.uuid4()),
            menu=menu,
            url=image_url,
            scans=0
        )

        return 201, QRCodeOut(
            id_qrcode=qr_code.id_qrcode,
            menu_id=str(menu.id_menu),
            
            url=qr_code.url,
            scans=qr_code.scans
        )

    except Menu.DoesNotExist:
        return 400, {"error": "Menu not found"}

@api.get("/qrcodes", response=List[QRCodeOut], auth=AuthBearer())
def list_qrcodes(request):
    qrcodes = QRCode.objects.filter(menu__etablissement=request.auth)
    return [
        QRCodeOut(
            id_qrcode=qr.id_qrcode,
            menu_id=str(qr.menu.nom),
            url=qr.url,
            scans=qr.scans
        )
        for qr in qrcodes
    ]

# Contenir Endpoints
@api.post("/contenir", response={201: ContenirOut, 400: ErrorResponse}, auth=AuthBearer())
def create_contenir(request, data: ContenirIn):
    try:
        item = Item.objects.get(id_item=data.id_item, etablissement=request.auth)
        ingredient = Ingredient.objects.get(id_ingredient=data.id_ingredient)
        contenir = Contenir.objects.create(id_item=item, id_ingredient=ingredient, quantite=data.quantite)
        return 201, contenir
    except (Item.DoesNotExist, Ingredient.DoesNotExist):
        return 400, {"error": "Invalid item or ingredient ID"}

# Contenir_Allergene Endpoints
@api.post("/contenir_allergene", response={201: None, 400: ErrorResponse})
def create_contenir_allergene(request, data: ContenirAllergeneIn):
    try:
        ingredient = Ingredient.objects.get(id_ingredient=data.id_ingredient)
        allergene = Allergene.objects.get(id_allergene=data.id_allergene)
        Contenir_Allergene.objects.create(id_ingredient=ingredient, id_allergene=allergene)
        return 201, None
    except (Ingredient.DoesNotExist, Allergene.DoesNotExist):
        return 400, {"error": "Invalid ingredient or allergene ID"}

# Concerner Endpoints
@api.post("/concerner", response={201: None, 400: ErrorResponse})
def create_concerner(request, data: ConcernerIn):
    try:
        personne = Personne.objects.get(id_personne=data.id_personne)
        allergene = Allergene.objects.get(id_allergene=data.id_allergene)
        Concerner.objects.create(id_personne=personne, id_allergene=allergene)
        return 201, None
    except (Personne.DoesNotExist, Allergene.DoesNotExist):
        return 400, {"error": "Invalid personne or allergene ID"}

# Donner_Avis Endpoints
@api.post("/avis", response={201: DonnerAvisOut, 400: ErrorResponse}, auth=AuthBearer())
def create_avis(request, data: DonnerAvisIn):
    try:
        personne = Personne.objects.get(id_personne=data.id_personne)
        avis = Donner_Avis.objects.create(
            id_personne=personne,
            id_etablissement=request.auth,
            note=data.note
        )
        return 201, avis
    except Personne.DoesNotExist:
        return 400, {"error": "Invalid personne ID"}

@api.get("/avis", response=List[DonnerAvisOut], auth=AuthBearer())
def list_avis(request):
    return Donner_Avis.objects.filter(id_etablissement=request.auth)

# Test Email Endpoint
@api.post("/test-email", response={200: WarningResponse, 500: ErrorResponse})
def test_email(request):
    try:
        send_mail(
            'Test Email',
            'This is a test email from dailyMenu.',
            settings.DEFAULT_FROM_EMAIL,
            ['test@example.com'],
            fail_silently=False,
        )
        return {"warning": "Test email sent successfully"}
    except Exception as e:
        return 500, {"error": f"Failed to send email: {str(e)}"}