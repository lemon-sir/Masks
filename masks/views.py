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
        # 分别获取非0和0值的字段
        nonzero_fields = {
            field: int(value) 
            for field, value in form.cleaned_data.items() 
            if value is not None and value != '' and int(value) > 0 and field not in ['name', 'collection_info']
        }
        
        zero_fields = {
            field
            for field, value in form.cleaned_data.items() 
            if value is not None and value != '' and int(value) == 0 and field not in ['name', 'collection_info']
        }
        
        print(f"非0字段: {nonzero_fields}")
        print(f"0值字段: {zero_fields}")
        
        if nonzero_fields or zero_fields:
            all_masks = Mask.objects.all()
            print(f"数据库中的脸谱数量: {all_masks.count()}")
            
            for mask in all_masks:
                # 检查是否有任何必需属性被设置为0
                has_zero_required = False
                for zero_field in zero_fields:
                    if getattr(mask, zero_field) > 0:
                        has_zero_required = True
                        break
                
                # 如果有必需属性为0，则既不是已达成也不是未达成
                if has_zero_required:
                    continue
                
                is_achieved = True
                differences = {}
                
                # 只检查非0字段
                for field, user_value in nonzero_fields.items():
                    mask_value = getattr(mask, field)
                    if mask_value > 0 and user_value < mask_value:
                        is_achieved = False
                        differences[field] = mask_value - user_value
                
                if action == 'check_achieved' and is_achieved:
                    achieved_masks.append(mask)
                elif action == 'check_unachieved' and not is_achieved:
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