from flask import Flask, jsonify, request
import requests
import json
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
import uuid
import time


app = Flask(__name__)


# 진짜 코드
# @app.route('/upload', methods=['POST', 'GET'])
# def process_image():
#     if request.method == 'POST':
#         file = request.files['file']
#         if file:
#             # API 설정
#             api_url = 'https://eoxy3e0azd.apigw.ntruss.com/custom/v1/29612/cb56e51bd632826fb10645cf94923e9934c4789df11256f9baaf17de98b0e7f9/general'
#             secret_key = 'VG1ocGpZcXlDU2xuRWFRaU1XdEtWWm1JSlZxeVV2c1A='
#             headers = {'X-OCR-SECRET': secret_key}
#
#             # 이미지 로드
#             image = Image.open(file.stream)
#             draw = ImageDraw.Draw(image)
#             font_path = './Font/Korail_Round_Gothic_Bold.ttf'
#             font = ImageFont.truetype(font_path, 16)
#
#
#             # 파일을 메모리에서 직접 읽어 API로 전송
#             file.seek(0)  # 스트림 위치를 처음으로 되돌림
#             files = {'file': (file.filename, file, file.content_type)}
#
#             request_json = {
#                 'images': [{'format': file.content_type.split('/')[1], 'name': 'demo'}],
#                 'requestId': str(uuid.uuid4()),
#                 'version': 'V2',
#                 'timestamp': int(round(time.time() * 1000))
#             }
#             payload = {'message': json.dumps(request_json).encode('UTF-8')}
#
#             try:
#                 response = requests.post(api_url, headers=headers, files=files, data=payload)
#                 response.raise_for_status()
#                 result = response.json()
#                 text_results = ' '.join([field['inferText'] for field in result['images'][0]['fields']])
#
#                 # 바운딩 박스 그리기
#                 for field in result['images'][0]['fields']:
#                     infer_text = field['inferText']
#                     vertices = field['boundingPoly']['vertices']
#                     draw.polygon([
#                         (vertices[0]['x'], vertices[0]['y']),
#                         (vertices[1]['x'], vertices[1]['y']),
#                         (vertices[2]['x'], vertices[2]['y']),
#                         (vertices[3]['x'], vertices[3]['y'])
#                     ], outline='red')
#
#                     text_position = (vertices[0]['x'], vertices[0]['y'] - 20)  # 텍스트 위치 조정 필요시 수정
#                     draw.text(text_position, infer_text, fill=(255, 0, 0), font=font)
#
#                 # 이미지를 Base64로 인코딩
#                 buffered = BytesIO()
#                 image.save(buffered, format="JPEG")
#                 image.show()
#                 img_str = base64.b64encode(buffered.getvalue()).decode()
#
#                 return jsonify({'text': text_results, 'image': img_str})
#
#             except requests.exceptions.RequestException as e:
#                 return jsonify({'error': str(e)}), 500
#
#     return jsonify({'error': 'No file provided'}), 400

@app.route('/upload', methods=['POST', 'GET'])
def process_image():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # API 설정
            api_url = 'https://eoxy3e0azd.apigw.ntruss.com/custom/v1/29612/cb56e51bd632826fb10645cf94923e9934c4789df11256f9baaf17de98b0e7f9/general'
            secret_key = 'VG1ocGpZcXlDU2xuRWFRaU1XdEtWWm1JSlZxeVV2c1A='
            headers = {'X-OCR-SECRET': secret_key}

            # 이미지 로드 및 준비
            image = Image.open(file.stream)
            draw = ImageDraw.Draw(image)
            font_path = './Font/Korail_Round_Gothic_Bold.ttf'
            font = ImageFont.truetype(font_path, 16)

            # 파일을 메모리에서 직접 읽어 API로 전송
            file.seek(0)
            files = {'file': (file.filename, file, file.content_type)}
            request_json = {
                'images': [{'format': file.content_type.split('/')[1], 'name': 'demo'}],
                'requestId': str(uuid.uuid4()),
                'version': 'V2',
                'timestamp': int(round(time.time() * 1000))
            }
            payload = {'message': json.dumps(request_json).encode('UTF-8')}

            # OCR API 요청
            try:
                response = requests.post(api_url, headers=headers, files=files, data=payload)
                response.raise_for_status()
                result = response.json()
                fields = result['images'][0]['fields']

                # 바운딩 박스 크기 계산 및 상위 5개 필드 필터링
                fields_with_size = [(field, (field['boundingPoly']['vertices'][1]['x'] - field['boundingPoly']['vertices'][0]['x']) *
                    (field['boundingPoly']['vertices'][2]['y'] - field['boundingPoly']['vertices'][1]['y'])) for field in fields]
                fields_with_size.sort(key=lambda x: x[1], reverse=True)
                top_fields = fields_with_size[:5]

                # 상위 5개 필드에 대한 바운딩 박스 그리기
                combined_text = []
                for field, size in top_fields:
                    infer_text = field['inferText']
                    vertices = field['boundingPoly']['vertices']
                    draw.polygon([vertices[0]['x'], vertices[0]['y'], vertices[1]['x'], vertices[1]['y'],
                                  vertices[2]['x'], vertices[2]['y'], vertices[3]['x'], vertices[3]['y']], outline='red')
                    text_position = (vertices[0]['x'], vertices[0]['y'] - 20)
                    draw.text(text_position, infer_text, fill=(255, 0, 0), font=font)
                    combined_text.append(infer_text)

                # 이미지를 Base64로 인코딩하여 결과와 함께 반환
                buffered = BytesIO()
                image.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()

                return jsonify({'text': " ".join(combined_text), 'image': img_str})

            except requests.exceptions.RequestException as e:
                return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'No file provided'}), 400



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

