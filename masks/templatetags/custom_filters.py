from django import template
import random

register = template.Library()

@register.filter
def random_color(value):
    # 生成柔和的随机颜色
    hue = random.randint(0, 360)
    return f'hsl({hue}, 50%, 85%)' 