from django.contrib.gis import admin
from editor.models import (LineaRevision, RecorridoRevision,
            HorarioRevision, ParadaRevision)


class RevisionAdmin(admin.GeoModelAdmin):
    exclude = ('moderado', 'editor')

    def save_model(self, request, obj, form, change):
        obj.editor = request.user
        obj.save()

admin.site.register(LineaRevision, RevisionAdmin)
admin.site.register(RecorridoRevision, RevisionAdmin)
admin.site.register(ParadaRevision, RevisionAdmin)
admin.site.register(HorarioRevision, RevisionAdmin)