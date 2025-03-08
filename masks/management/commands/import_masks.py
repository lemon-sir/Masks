import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand
from masks.models import Mask
from django.conf import settings
import os

class Command(BaseCommand):
    help = '从Excel文件导入脸谱数据'

    def handle(self, *args, **options):
        # 使用相对路径获取Excel文件
        excel_path = os.path.join(settings.BASE_DIR, 'masks', 'static', 'Data', 'RawData.xlsx')
        
        if not os.path.exists(excel_path):
            self.stdout.write(self.style.ERROR(f'Excel文件不存在：{excel_path}'))
            return

        try:
            # 读取Excel文件，将所有数值型空值填充为0
            df = pd.read_excel(excel_path)
            numeric_columns = ['宽和', '霸道', '恬淡', '好胜', '超然', '入世', '多情', 
                             '无情', '随和', '桀骜', '耿直', '玲珑', '根骨', '弘毅', 
                             '胆识', '身手', '睿智', '童趣', '福缘', '交际', '魅力', 
                             '名气', '体魄', '威望']
            
            # 将数值列的NaN填充为0
            for col in numeric_columns:
                df[col] = df[col].fillna(0)
            
            # 将字符串列的NaN填充为空字符串
            df['收集属性'] = df['收集属性'].fillna('')
            df['脸谱名称'] = df['脸谱名称'].fillna('')
            df['颜色'] = df['颜色'].fillna('')
            
            self.stdout.write(self.style.SUCCESS(f'Excel文件中的列名：{list(df.columns)}'))
            
            # 清除现有数据
            Mask.objects.all().delete()
            
            for _, row in df.iterrows():
                try:
                    Mask.objects.create(
                        name=row['脸谱名称'],
                        kuanhe=int(row['宽和']),
                        badao=int(row['霸道']),
                        tiandan=int(row['恬淡']),
                        haosheng=int(row['好胜']),
                        chaoran=int(row['超然']),
                        rushi=int(row['入世']),
                        duoqing=int(row['多情']),
                        wuqing=int(row['无情']),
                        suihe=int(row['随和']),
                        jiao=int(row['桀骜']),
                        gengzhi=int(row['耿直']),
                        linglong=int(row['玲珑']),
                        gengu=int(row['根骨']),
                        hongyi=int(row['弘毅']),
                        danshi=int(row['胆识']),
                        shenshou=int(row['身手']),
                        ruizhi=int(row['睿智']),
                        tongqu=int(row['童趣']),
                        fuyuan=int(row['福缘']),
                        jiaoji=int(row['交际']),
                        meili=int(row['魅力']),
                        mingqi=int(row['名气']),
                        tipo=int(row['体魄']),
                        weiwang=int(row['威望']),
                        collection_info=row['收集属性'],
                        color=row['颜色']
                    )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'导入行失败：{str(e)}'))
                    self.stdout.write(self.style.ERROR(f'问题数据：{row.to_dict()}'))
                    continue
            
            self.stdout.write(self.style.SUCCESS('数据导入成功！'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'导入失败：{str(e)}')) 