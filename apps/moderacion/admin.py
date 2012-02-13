from django.contrib.gis import admin
from moderation.admin import ModerationAdmin
from moderation.models import ModeratedObject
from moderacion.models import Linea, Recorrido

class CustomAdmin(ModerationAdmin, admin.GeoModelAdmin):
    exclude = ()

    def queryset(self, request):
        qs = super(CustomAdmin, self).queryset(request)
	not_moderated = []
	if not request.user.is_superuser:
	    not_moderated = [obj.object_pk for obj in ModeratedObject.objects.filter(moderation_status__in=[2,0])]
        return qs.exclude(id__in=not_moderated)

admin.site.register(Linea, CustomAdmin)
admin.site.register(Recorrido, CustomAdmin)
