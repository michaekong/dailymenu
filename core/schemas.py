from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from decimal import Decimal
from .models import *

class ErrorResponse(BaseModel):
    error: str
    class Config:
       from_attributes = True

class WarningResponse(BaseModel):
    warning: str
    class Config:
       from_attributes = True

# Etablissement Schemas
class EtablissementIn(BaseModel):
    nom_etablissement: str = Field(..., max_length=50)
    email_pro: EmailStr
    numtel: str = Field(..., max_length=50)
    adresse_physique: str = Field(..., max_length=50)
    latitude: float
    longitude: float
    password: str
    class Config:
       from_attributes = True

class EtablissementUpdate(BaseModel):
    nom_etablissement: Optional[str] = Field(None, max_length=50)
    email_pro: Optional[EmailStr] = None
    numtel: Optional[str] = Field(None, max_length=50)
    adresse_physique: Optional[str] = Field(None, max_length=50)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    class Config:
       from_attributes = True

class EtablissementOut(BaseModel):
    id_etablissement: str
    nom_etablissement: str
    email_pro: str
    numtel: str
    adresse_physique: str
    latitude: float
    longitude: float
    is_verified: bool
    class Config:
       from_attributes = True

class LoginIn(BaseModel):
    email: EmailStr
    password: str
    class Config:
       from_attributes = True

class TokenOut(BaseModel):
    token: str
    
    class Config:
       from_attributes = True
# Personne Schemas
class PersonneIn(BaseModel):
    email: str = Field(..., max_length=50)
    geolocalisation: Optional[str] = Field(None, max_length=255)
    marque_tel: Optional[str] = Field(None, max_length=50)
    class Config:
       from_attributes = True

class PersonneOut(BaseModel):
    id_personne: int
    email: str
    geolocalisation: str
    marque_tel: str
    
    class Config:
       from_attributes = True

# Jour Schemas
class JourIn(BaseModel):
    nom: str = Field(..., max_length=50)
    class Config:
       from_attributes = True

class JourOut(BaseModel):
    id_jour: int
    nom: str
    class Config:
       from_attributes = True

# Category Schemas
class CategoryIn(BaseModel):
    name: str = Field(..., max_length=255)
    parent_id: Optional[str] = None
    class Config:
       from_attributes = True
class CategoryOut(BaseModel):
    id_category: str
    name: str
    parent_id: Optional[str] = None
    class Config:
       from_attributes = True

# Tag Schemas
class TagIn(BaseModel):
    name: str = Field(..., max_length=50)
    class Config:
        orm_mode = True  # ⬅️ obligatoire pour supporter les objets Django


class TagOut(BaseModel):
    id_tag: str
    name: str
    class Config:
       from_attributes = True

# Ingredient Schemas
class IngredientIn(BaseModel):
    nom_ingredient: str = Field(..., max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    categorie: str = Field(..., max_length=50)
    class Config:
        orm_mode = True  # ⬅️ obligatoire pour supporter les objets Django


class IngredientOut(BaseModel):
    id_ingredient: int
    nom_ingredient: str
    description: str
    categorie: str
    class Config:
       from_attributes = True
# Allergene Schemas
class AllergeneIn(BaseModel):
    nom_allergene: str = Field(..., max_length=50)
    categorie_allergene: str = Field(..., max_length=50)
    dangerosite: int
    class Config:
       from_attributes = True  # ⬅️ obligatoire pour supporter les objets Django



class AllergeneOut(BaseModel):
    id_allergene: int
    nom_allergene: str
    categorie_allergene: str
    dangerosite: int
    class Config:
       from_attributes = True  # ⬅️ obligatoire pour supporter les objets Django


# Image Schemas
class ImageIn(BaseModel):
    url_image: str = Field(..., max_length=255)
    id_item: int
    class Config:
       from_attributes = True  # ⬅️ obligatoire pour supporter les objets Django


class ImageOut(BaseModel):
    id_image: int
    url_image: str
    id_item: int

    class Config:
        from_attributes = True

class QRCodeIn(BaseModel):
    menu_id: str

# Item Schemas
class ItemIn(BaseModel):
    nom_plat: str = Field(..., max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    disponibilite: bool = False
    price: Decimal
    prep_time: int
    category_ids: List[str] = []
    tag_ids: List[str] = []
    ingredient_ids: List[int] = []
    jour_ids: List[int] = []
    quantites: List[str] = []
    class Config:
       from_attributes = True  # ⬅️ obligatoire pour supporter les objets Django



class ItemOut(BaseModel):
    id_item: int
    nom_plat: str
    description: str
    disponibilite: bool
    price: Decimal
    prep_time: int
    categories: List[CategoryOut]
    tags: List[TagOut]
    ingredients: List[IngredientOut]
    jours_disponibilite: List[JourOut]
    images: List[ImageOut]
    class Config:
       from_attributes = True  # ⬅️ obligatoire pour supporter les objets Django


# Update IngredientOut
class IngredientOut2(BaseModel):
    id_ingredient: int
    nom_ingredient: str
    description: str
    categorie: str
    allergenes: List[AllergeneOut] = []  # Added
  
# Update ItemOut
class ItemOut2(BaseModel):
    id_item: int
    nom_plat: str
    description: str
    disponibilite: bool
    price: Decimal
    prep_time: int
    categories: List[CategoryOut]
    tags: List[TagOut]
    ingredients: List[IngredientOut2]
    jours_disponibilite: List[JourOut]
    images: List[ImageOut]
    allergenes: List[AllergeneOut]  # ✅ C'EST ICI qu'on ajoute le champ
    average_rating: Decimal
  
# Menu Schemas
class MenuIn(BaseModel):
    nom: str = Field(..., max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    item_ids: List[int] = []
    class Config:
       from_attributes = True  # ⬅️ obligatoire pour supporter les objets Django


class MenuOut2(BaseModel):
    id_menu: str
    nom: str
    description: str
    items: List[ItemOut2]
    class Config:
        from_attributes = True

class MenuOut(BaseModel):
    id_menu: str
    nom: str
    description: str
    items: List[ItemOut]
    class Config:
       from_attributes = True  # ⬅️ obligatoire pour supporter les objets Django



# Contenir Schemas
class ContenirIn(BaseModel):
    id_item: int
    id_ingredient: int
    quantite: str = Field(..., max_length=50)
    class Config:
       from_attributes = True

class ContenirOut(BaseModel):
    id_item: int
    id_ingredient: int
    quantite: str
    class Config:
       from_attributes = True

# Contenir_Allergene Schema
class ContenirAllergeneIn(BaseModel):
    id_ingredient: int
    id_allergene: int
    class Config:
       from_attributes = True

# Concerner Schema
class ConcernerIn(BaseModel):
    id_personne: int
    id_allergene: int
    class Config:
       from_attributes = True

# Donner_Avis Schemas
class DonnerAvisIn(BaseModel):
    id_personne: int
    note: int
    class Config:
       from_attributes = True

class DonnerAvisOut(BaseModel):
    id_personne: int
    id_etablissement: str
    date_avis: str
    note: int

# QRCode Schema
class QRCodeOut(BaseModel):
    id_qrcode: str
    menu_id: str
    url: str
    scans: int