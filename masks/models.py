from django.db import models

class Mask(models.Model):
    name = models.CharField(max_length=100, verbose_name='脸谱名称')
    kuanhe = models.IntegerField(verbose_name='宽和')
    badao = models.IntegerField(verbose_name='霸道')
    tiandan = models.IntegerField(verbose_name='恬淡')
    haosheng = models.IntegerField(verbose_name='好胜')
    chaoran = models.IntegerField(verbose_name='超然')
    rushi = models.IntegerField(verbose_name='入世')
    duoqing = models.IntegerField(verbose_name='多情')
    wuqing = models.IntegerField(verbose_name='无情')
    suihe = models.IntegerField(verbose_name='随和')
    jiao = models.IntegerField(verbose_name='桀骜')
    gengzhi = models.IntegerField(verbose_name='耿直')
    linglong = models.IntegerField(verbose_name='玲珑')
    gengu = models.IntegerField(verbose_name='根骨')
    hongyi = models.IntegerField(verbose_name='弘毅')
    danshi = models.IntegerField(verbose_name='胆识')
    shenshou = models.IntegerField(verbose_name='身手')
    tipo = models.IntegerField(verbose_name='体魄')
    ruizhi = models.IntegerField(verbose_name='睿智')
    tongqu = models.IntegerField(verbose_name='童趣')
    fuyuan = models.IntegerField(verbose_name='福缘')
    jiaoji = models.IntegerField(verbose_name='交际')
    meili = models.IntegerField(verbose_name='魅力')
    mingqi = models.IntegerField(verbose_name='名气')
    weiwang = models.IntegerField(verbose_name='威望')
    collection_info = models.TextField(verbose_name='收集属性信息')
    color = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '脸谱'
        verbose_name_plural = '脸谱' 