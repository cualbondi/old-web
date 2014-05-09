from django import template
import re
from django.contrib.flatpages.models import FlatPage

# by Julian Perelli, 2014
#
# tag usage 1:
# {% load flatpages_list %}
# {% flatpages_list %}
# {% for flatpage in flatpages_list %}
#   ...
# {% endfor%}
#
# tag usage 2:
# {% load flatpages_list %}
# {% flatpages_list as fpl %}
# {% for flatpage in fpl %}
#   ...
# {% endfor%}

register = template.Library()

class FlatpagesList(template.Node):
    def __init__(self, varname):
        if varname is None:
            self.varname = "flatpages_list"
        else:
            self.varname = varname
    def render(self, context):
        context[self.varname] = FlatPage.objects.order_by("title")
        return ''

@register.tag(name="flatpages_list")
def do_flatpages_list(parser, token): 
    m = re.search(r'^(\w+)( as \w+)?$', token.contents)
    if not m:
        raise template.TemplateSyntaxError("flatpages_list tag had invalid arguments")
    tagname, varname = m.groups()
    return FlatpagesList(varname)