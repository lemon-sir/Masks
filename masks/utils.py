import cv2
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR
import logging
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',  # 只显示消息内容，不显示时间戳等其他信息
    handlers=[
        logging.StreamHandler()  # 添加控制台处理器
    ]
)
logger = logging.getLogger(__name__)

# 初始化 PaddleOCR，使用中文模型
ocr = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)

def extract_attributes(image_file):
    try:
        image = Image.open(image_file)
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # OCR识别整个图片
        result = ocr.ocr(cv_image, cls=True)
        if not result or not result[0]:
            logger.warning("No text detected in image")
            return {'error': 'No text detected'}
        
        # 存储所有识别到的文本及其位置
        text_boxes = []
        logger.info("=== 开始OCR识别 ===")
        
        for line in result[0]:
            box = line[0]
            text = line[1][0]
            confidence = line[1][1]
            
            center_x = (box[0][0] + box[2][0]) / 2
            center_y = (box[0][1] + box[2][1]) / 2
            
            text_boxes.append({
                'text': text,
                'center_x': center_x,
                'center_y': center_y,
                'confidence': confidence,
                'box': box
            })
            logger.info(f"识别到文本: '{text}' 位置: ({center_x}, {center_y}) 置信度: {confidence}")
        
        # 输出所有识别到的文本
        logger.info("=== 所有识别到的文本 ===")
        for box in text_boxes:
            logger.info(f"文本: '{box['text']}' 位置: ({box['center_x']:.1f}, {box['center_y']:.1f})")
        
        # 初始化结果
        results = {}
        
        # 定义属性名称映射（天资能力和气质才情）
        attribute_mapping = {
            # 天资能力属性
            '根骨': 'gengu',
            '弘毅': 'hongyi',
            '胆识': 'danshi',
            '身手': 'shenshou',
            '体魄': 'tipo',
            '酒量': 'jiliang',
            '饭量': 'fanliang',
            # 气质才情属性
            '睿智': 'ruizhi',
            '童趣': 'tongqu',
            '福缘': 'fuyuan',
            '交际': 'jiaoji',
            '魅力': 'meili',
            '威望': 'weiwang',
            '名气': 'mingqi',
        }
        
        # 定义性情属性对
        personality_pairs = {
            '霸道': {'opposite': '宽和', 'key': 'badao', 'opposite_key': 'kuanhe'},
            '恬淡': {'opposite': '好胜', 'key': 'tiandan', 'opposite_key': 'haosheng'},
            '超然': {'opposite': '入世', 'key': 'chaoran', 'opposite_key': 'rushi'},
            '多情': {'opposite': '无情', 'key': 'duoqing', 'opposite_key': 'wuqing'},
            '随和': {'opposite': '桀骜', 'key': 'suihe', 'opposite_key': 'jiao'},
            '耿直': {'opposite': '玲珑', 'key': 'gengzhi', 'opposite_key': 'linglong'},
            # 添加反向映射
            '宽和': {'opposite': '霸道', 'key': 'kuanhe', 'opposite_key': 'badao'},
            '好胜': {'opposite': '恬淡', 'key': 'haosheng', 'opposite_key': 'tiandan'},
            '入世': {'opposite': '超然', 'key': 'rushi', 'opposite_key': 'chaoran'},
            '无情': {'opposite': '多情', 'key': 'wuqing', 'opposite_key': 'duoqing'},
            '桀骜': {'opposite': '随和', 'key': 'jiao', 'opposite_key': 'suihe'},
            '玲珑': {'opposite': '耿直', 'key': 'linglong', 'opposite_key': 'gengzhi'},
        }
        
        # 处理性情属性
        processed_pairs = set()
        numbers = []

        # 先收集所有数字
        for box in text_boxes:
            text = box['text'].strip()
            # 过滤掉带有"、"的文本，因为这些通常是额外的信息（如"霸道320、无情30"）
            if "、" in text:
                continue
            
            if re.search(r'\d+', text):
                numbers.append({
                    'number': int(re.search(r'\d+', text).group()),
                    'center_x': box['center_x'],
                    'center_y': box['center_y']
                })

        # 处理每个属性对
        for box in text_boxes:
            text = box['text'].strip()
            for key in personality_pairs.keys():
                if key in text and key not in processed_pairs:
                    pair_info = personality_pairs[key]
                    opposite_key = pair_info['opposite']
                    
                    # 找到同一行的数字
                    row_numbers = []
                    for num in numbers:
                        y_diff = abs(num['center_y'] - box['center_y'])
                        if y_diff < 35:  # 使用35像素的阈值
                            x_diff = num['center_x'] - box['center_x']
                            row_numbers.append({
                                'number': num['number'],
                                'x_diff': x_diff
                            })
                    
                    if row_numbers:
                        if key in ['霸道', '宽和']:
                            # 霸道/宽和属性对：只使用右边的数值
                            right_number = next((n['number'] for n in row_numbers if n['x_diff'] > 0), None)
                            if right_number is not None:
                                results[pair_info['key']] = right_number
                                results[pair_info['opposite_key']] = 0
                        else:
                            # 其他属性对：从中心点往两侧查找
                            opposite_box = next((opp_box for opp_box in text_boxes 
                                              if opposite_key in opp_box['text'].strip()), None)
                            
                            if opposite_box:
                                center_x = (box['center_x'] + opposite_box['center_x']) / 2
                                
                                for num in row_numbers:
                                    relative_x = num['x_diff'] + box['center_x'] - center_x
                                    if relative_x > 0:  # 数字在中心点右侧
                                        if key in text:  # 当前是左侧属性
                                            results[pair_info['opposite_key']] = num['number']
                                            results[pair_info['key']] = 0
                                        else:  # 当前是右侧属性
                                            results[pair_info['key']] = num['number']
                                            results[pair_info['opposite_key']] = 0
                                    else:  # 数字在中心点左侧
                                        if key in text:  # 当前是左侧属性
                                            results[pair_info['key']] = num['number']
                                            results[pair_info['opposite_key']] = 0
                                        else:  # 当前是右侧属性
                                            results[pair_info['opposite_key']] = num['number']
                                            results[pair_info['key']] = 0
                
                        processed_pairs.add(key)
                        processed_pairs.add(opposite_key)

        # 处理天资能力和气质才情属性
        for box in text_boxes:
            text = box['text'].strip()
            if text in attribute_mapping:
                # 查找最近的数字
                value = None
                min_distance = float('inf')
                
                for other_box in text_boxes:
                    other_text = other_box['text'].strip()
                    if other_text.isdigit():
                        x_diff = other_box['center_x'] - box['center_x']
                        y_diff = abs(other_box['center_y'] - box['center_y'])
                        
                        if x_diff > 0 and y_diff < 30:
                            distance = ((x_diff ** 2) + (y_diff ** 2)) ** 0.5
                            if distance < min_distance:
                                min_distance = distance
                                value = int(other_text)
                
                if value is not None:
                    results[attribute_mapping[text]] = value
                    logger.info(f"匹配到 {text}: {value}")
        
        logger.info(f"最终结果: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Error in extract_attributes: {str(e)}")
        logger.exception("详细错误信息")
        return {'error': str(e)} 