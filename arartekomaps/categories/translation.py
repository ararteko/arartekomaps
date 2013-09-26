from modeltranslation.translator import translator, TranslationOptions
from arartekomaps.places.models import Category

class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(Category, CategoryTranslationOptions)
