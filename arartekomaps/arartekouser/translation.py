from modeltranslation.translator import translator, TranslationOptions
from models import ArartekoUser

class UserTranslationOptions(TranslationOptions):
    fields = ('fullname',)

translator.register(ArartekoUser, UserTranslationOptions)

#ALTER TABLE `arartekouser_arartekouser` ADD `fullname_es` VARCHAR(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `fullname`, ADD `fullname_eu` VARCHAR(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `fullname_es`, ADD `fullname_en` VARCHAR(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `fullname_eu`;