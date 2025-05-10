from django.shortcuts import render, redirect
from .forms import MaskCompareForm
from .models import Mask, ImageUpload, QueryHistory
from django.db.models import Q
from .utils import extract_attributes
from django.http import JsonResponse, StreamingHttpResponse
import os
from django.conf import settings
import json
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone
from datetime import datetime
import pytz

# 添加登录要求装饰器
@login_required(login_url='masks:login')
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
            
            # 记录查询历史
            query_description = []
            for field, value in nonzero_fields.items():
                query_description.append(f"{field}:{value}")
            for field in zero_fields:
                query_description.append(f"{field}:0")
            
            if query_description:  # 只在有查询条件时记录
                # 获取用户的最后一条记录的查询次数
                last_query = QueryHistory.objects.filter(user=request.user).order_by('-query_count').first()
                query_count = (last_query.query_count + 1) if last_query else 1
                
                # 保存查询记录
                QueryHistory.objects.create(
                    user=request.user,
                    mask_name=", ".join(query_description),
                    query_count=query_count
                )
                
                # 只保留最近5条记录
                records = list(QueryHistory.objects.filter(user=request.user)
                              .order_by('-query_time')
                              .values_list('id', flat=True))
                
                if len(records) > 5:
                    # 获取需要删除的记录ID
                    records_to_delete = records[5:]
                    # 删除这些记录
                    QueryHistory.objects.filter(id__in=records_to_delete).delete()
            
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

@login_required
def upload_image(request):
    if not request.user.is_cloud_member:
        return JsonResponse({
            'success': False,
            'error': '你当前不是云栈帮众，无法使用此功能'
        })
    print("Upload endpoint hit")
    if request.method == 'POST' and request.FILES.getlist('images'):
        print(f"Files received: {request.FILES.getlist('images')}")
        combined_results = {}
        
        try:
            for image in request.FILES.getlist('images'):
                print(f"Processing image: {image.name}")
                results = extract_attributes(image)
                
                if results.get('error'):
                    print(f"Error processing {image.name}: {results['error']}")
                    continue
                
                # 合并结果，保留非零值
                for key, value in results.items():
                    if value != 0 or key not in combined_results:
                        combined_results[key] = value
                
                # 删除已处理的图片
                try:
                    image_path = os.path.join(settings.MEDIA_ROOT, 'uploads', image.name)
                    if os.path.exists(image_path):
                        os.remove(image_path)
                except Exception as e:
                    print(f"Error deleting image {image.name}: {e}")
            
            print(f"Final combined results: {combined_results}")
            return JsonResponse({
                'success': True,
                'data': combined_results
            }, content_type='application/json; charset=utf-8')
            
        except Exception as e:
            print(f"Error processing upload: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, content_type='application/json; charset=utf-8')
    
    print("No files in request")
    return JsonResponse({
        'success': False, 
        'error': '没有上传图片'
    }, content_type='application/json; charset=utf-8')

def login_view(request):
    # 如果用户已登录，直接重定向到查询页面
    if request.user.is_authenticated:
        return redirect('masks:compare_masks')
        
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('masks:compare_masks')
        else:
            messages.error(request, '用户名或密码错误')
    return render(request, 'masks/login.html')

def register_view(request):
    # 如果用户已登录，直接重定向到查询页面
    if request.user.is_authenticated:
        return redirect('masks:compare_masks')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '注册成功！')
            return redirect('masks:compare_masks')
        else:
            for error in form.errors.values():
                messages.error(request, error[0])
    return render(request, 'masks/register.html')

# 检查是否是管理员
def is_admin(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_admin)
def user_management(request):
    if not request.user.is_superuser:
        return redirect('masks:compare_masks')
    
    users = User.objects.all().order_by('-date_joined')
    
    # 转换时区为北京时间
    beijing_tz = pytz.timezone('Asia/Shanghai')
    for user in users:
        if user.date_joined:
            user.date_joined = user.date_joined.astimezone(beijing_tz)
        if user.last_login:
            user.last_login = user.last_login.astimezone(beijing_tz)
    
    return render(request, 'masks/user_management.html', {
        'users': users
    })

@user_passes_test(is_admin)
def toggle_user_status(request, user_id):
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            if user.is_superuser:
                return JsonResponse({'success': False, 'error': '不能修改管理员状态'})
            user.is_active = not user.is_active
            user.save()
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': '用户不存在'})
    return JsonResponse({'success': False, 'error': '方法不允许'})

@user_passes_test(is_admin)
def delete_user(request, user_id):
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            if user.is_superuser:
                return JsonResponse({'success': False, 'error': '不能删除管理员'})
            user.delete()
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': '用户不存在'})
    return JsonResponse({'success': False, 'error': '方法不允许'})

@user_passes_test(is_admin)
def user_history(request, user_id):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': '权限不足'})
        
    try:
        user = User.objects.get(id=user_id)
        history = user.queries.all()
        
        # 转换时区为北京时间
        beijing_tz = pytz.timezone('Asia/Shanghai')
        history_data = [{
            'query_time': h.query_time.astimezone(beijing_tz).strftime('%Y-%m-%d %H:%M:%S'),
            'mask_name': h.mask_name
        } for h in history]
        
        return JsonResponse({
            'success': True,
            'history': history_data
        })
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': '用户不存在'})

@login_required
def user_query_history(request):
    if request.method == 'POST':
        history_id = request.POST.get('history_id')
        custom_name = request.POST.get('custom_name')
        try:
            history = QueryHistory.objects.get(id=history_id, user=request.user)
            history.custom_name = custom_name
            history.save()
            return JsonResponse({'success': True})
        except QueryHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': '记录不存在'})
    
    history = QueryHistory.objects.filter(user=request.user).order_by('-query_time')[:5]
    return render(request, 'masks/my_history.html', {'history': history})

@login_required
def load_history_params(request, history_id):
    if not request.user.is_cloud_member:
        return JsonResponse({
            'success': False,
            'error': '你当前不是云栈帮众，无法使用此功能'
        })
    try:
        history = QueryHistory.objects.get(id=history_id, user=request.user)
        params = history.get_params_dict()
        if not params:
            return JsonResponse({'success': False, 'error': '无法解析查询参数'})
        return JsonResponse({'success': True, 'params': params})
    except QueryHistory.DoesNotExist:
        return JsonResponse({'success': False, 'error': '记录不存在'})
    except Exception as e:
        print(f"Error in load_history_params: {e}")
        return JsonResponse({'success': False, 'error': '加载参数时发生错误'})

@login_required
def toggle_cloud_member(request, user_id):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': '只有管理员可以执行此操作'})
    
    try:
        user = User.objects.get(id=user_id)
        
        # 不允许修改超级用户的云栈成员状态
        if user.is_superuser:
            return JsonResponse({'success': False, 'error': '不能修改管理员的云栈成员状态'})
        
        # 切换云栈成员状态
        user.is_cloud_member = not user.is_cloud_member
        user.save()
        
        return JsonResponse({
            'success': True, 
            'is_cloud_member': user.is_cloud_member
        })
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': '用户不存在'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def logout_view(request):
    """自定义退出视图函数"""
    logout(request)
    return redirect('masks:login') 