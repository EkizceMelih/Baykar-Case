from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Bir sözlükten (dictionary) belirtilen anahtarın (key) değerini alır.
    Eğer sözlük geçerli değilse veya anahtar yoksa, hata vermek yerine
    güvenli bir şekilde None döndürür.
    """
    if not isinstance(dictionary, dict):
        return None  # Eğer bir sözlük değilse, None döndür
        
    return dictionary.get(key)
