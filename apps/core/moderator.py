from moderation import moderation
from moderation.moderator import GenericModerator
from apps.core.models import Linea, Recorrido

class CustomModerator(GenericModerator):
    auto_approve_for_superusers = True
    auto_approve_for_staff = False

moderation.register(Linea, CustomModerator)
moderation.register(Recorrido, CustomModerator)
