from django.shortcuts import render
from .forms import MaskCompareForm
from .models import Mask
from django.db.models import Q

def compare_masks(request):
    print("视图函数被调用")
    print(f"请求方法: {request.method}")
    print(f"POST数据: {request.POST}")
    
    # 添加字段名称映射
    field_names = {
        'kuanhe': '宽和',
        'badao': '霸道',
        'tiandan': '恬淡',
        'haosheng': '好胜',
        'chaoran': '超然',
        'rushi': '入世',
        'duoqing': '多情',
        'wuqing': '无情',
        'suihe': '随和',
        'jiao': '桀骜',
        'gengzhi': '耿直',
        'linglong': '玲珑',
        'gengu': '根骨',
        'hongyi': '弘毅',
        'danshi': '胆识',
        'shenshou': '身手',
        'ruizhi': '睿智',
        'tongqu': '童趣',
        'fuyuan': '福缘',
        'jiaoji': '交际',
        'meili': '魅力',
        'mingqi': '名气',
        'tipo': '体魄',
        'weiwang': '威望',
    }
    
    form = MaskCompareForm(request.POST or None)
    unachieved_masks = []
    achieved_masks = []
    action = request.POST.get('action') if request.method == 'POST' else None
    
    print(f"Action: {action}")
    
    if request.method == 'POST' and form.is_valid():
        print("表单验证通过")
        filled_fields = {
            field: int(value) 
            for field, value in form.cleaned_data.items() 
            if value is not None and value != '' and field not in ['name', 'collection_info']
        }
        
        print(f"填写的字段: {filled_fields}")
        
        if filled_fields:
            all_masks = Mask.objects.all()
            print(f"数据库中的脸谱数量: {all_masks.count()}")
            
            for mask in all_masks:
                requirements = {}
                for field in filled_fields.keys():
                    db_value = getattr(mask, field)
                    if db_value > 0:
                        requirements[field] = db_value
                
                if not requirements:
                    continue
                
                is_achieved = True
                differences = {}
                
                for field, required_value in requirements.items():
                    user_value = filled_fields.get(field, 0)
                    if user_value < required_value:
                        is_achieved = False
                        differences[field] = required_value - user_value
                
                if action == 'check_achieved' and is_achieved:
                    achieved_masks.append(mask)
                elif action == 'check_unachieved' and not is_achieved:
                    # 将字段名称转换为中文
                    mask.differences = {field_names[field]: value for field, value in differences.items()}
                    unachieved_masks.append(mask)
            
            if action == 'check_unachieved' and unachieved_masks:
                unachieved_masks.sort(key=lambda x: sum(x.differences.values()))
    
    return render(request, 'masks/compare.html', {
        'form': form,
        'unachieved_masks': unachieved_masks,
        'achieved_masks': achieved_masks,
        'action': action,
    }) 