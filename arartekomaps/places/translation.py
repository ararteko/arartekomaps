from modeltranslation.translator import translator, TranslationOptions
from arartekomaps.places.models import Place

class PlaceTranslationOptions(TranslationOptions):
    fields = ('description','url','adescription')

translator.register(Place, PlaceTranslationOptions)
