from django import template

register = template.Library()

censor_words = ["post", "text"]

@register.filter(name='censor')
def censor(censor_text):
    for word in censor_words:
        censor_text = censor_text.lower().replace(word.lower(),'*')
    return censor_text