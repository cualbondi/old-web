from moderation import moderation
from moderation.moderator import GenericModerator
from moderacion.models import Linea, Recorrido

class CustomModerator(GenericModerator):
    auto_approve_for_staff = False
    visibility_column = 'visible'

moderation.register(Linea, CustomModerator)
moderation.register(Recorrido, CustomModerator)