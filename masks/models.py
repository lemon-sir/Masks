from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_migrate
from django.dispatch import receiver

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

class ImageUpload(models.Model):
    image = models.ImageField(upload_to='uploads/%Y/%m/%d/', verbose_name='截图')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '图片上传'
        verbose_name_plural = '图片上传'

class QueryHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='queries')
    query_time = models.DateTimeField(auto_now_add=True)
    mask_name = models.CharField(max_length=5000)
    custom_name = models.CharField(max_length=100, blank=True, null=True)
    query_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-query_time']
        verbose_name = '查询历史'
        verbose_name_plural = '查询历史'

    def __str__(self):
        return f"{self.user.username} - {self.get_display_name()} - {self.query_time}"
    
    def get_display_name(self):
        if self.custom_name:
            return self.custom_name
        return f"第{self.query_count}次查询结果"

    def get_formatted_params(self):
        """用于显示在历史记录页面的格式化参数"""
        try:
            # 将拼音转换为中文显示
            pinyin_to_cn = {
                'kuanhe': '宽和', 'badao': '霸道', 'tiandan': '恬淡',
                'haosheng': '好胜', 'chaoran': '超然', 'rushi': '入世',
                'duoqing': '多情', 'wuqing': '无情', 'suihe': '随和',
                'jiao': '桀骜', 'gengzhi': '耿直', 'linglong': '玲珑',
                'gengu': '根骨', 'hongyi': '弘毅', 'danshi': '胆识',
                'shenshou': '身手', 'tipo': '体魄', 'ruizhi': '睿智',
                'tongqu': '童趣', 'fuyuan': '福缘', 'jiaoji': '交际',
                'meili': '魅力', 'mingqi': '名气', 'weiwang': '威望'
            }
            
            params = []
            for param in self.mask_name.split(', '):
                if ':' in param:
                    key, value = param.split(':')
                    key = key.strip()
                    if key in pinyin_to_cn:
                        params.append(f"{pinyin_to_cn[key]}: {value}")
            return params
        except Exception as e:
            print(f"Error in get_formatted_params: {e}")
            return []

    def get_params_dict(self):
        """用于导入到查询表单的参数字典"""
        try:
            params = {}
            for param in self.mask_name.split(', '):
                if ':' in param:
                    key, value = param.split(':')
                    key = key.strip()
                    value = value.strip()
                    params[key] = value
            return params
        except Exception as e:
            print(f"Error in get_params_dict: {e}")
            return {}

# 添加云栈成员标记
User.add_to_class('is_cloud_member', models.BooleanField(default=False, verbose_name='云栈成员'))

@receiver(post_migrate)
def add_cloud_member_field(sender, **kwargs):
    from django.db import connection
    cursor = connection.cursor()
    try:
        cursor.execute("""
            ALTER TABLE auth_user
            ADD COLUMN is_cloud_member BOOLEAN DEFAULT FALSE
        """)
    except:
        pass  # 字段已存在 