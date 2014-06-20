# para correr en manage.py shell

for x in Poi.objects.all():
    if Poi.objects.filter(nom__contains=','.join(x.nom.split(',')[:2])).count() > 1:
        x.delete()
    else:
        x.nom=','.join(x.nom.split(',')[:2])
        x.save()