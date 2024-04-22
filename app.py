from flask import Flask, request, jsonify
import requests
import uuid
import json
import time
import os

app = Flask(__name__)

# 업로드 된 이미지에서 글자 인식 후 반환
# @app.route('/upload', methods=['POST', 'GET'])
# def process_image():
#     api_url = 'https://eoxy3e0azd.apigw.ntruss.com/custom/v1/29612/cb56e51bd632826fb10645cf94923e9934c4789df11256f9baaf17de98b0e7f9/general'
#     secret_key = 'VG1ocGpZcXlDU2xuRWFRaU1XdEtWWm1JSlZxeVV2c1A='
#     headers = {
#         'X-OCR-SECRET': secret_key
#     }
#     path = "./image_test/gamja.jpg"
#
#     # 파일을 여는 방법을 변경
#     if not os.path.exists(path):
#         return jsonify({'error': 'File not found'}), 404
#
#     files = {'file': open(path, 'rb')}
#     request_json = {
#         'images': [{'format': 'jpg', 'name': 'demo'}],
#         'requestId': str(uuid.uuid4()),
#         'version': 'V2',
#         'timestamp': int(round(time.time() * 1000))
#     }
#     payload = {'message': json.dumps(request_json).encode('UTF-8')}
#
#     try:
#         # 파일과 함께 페이로드 전송
#         response = requests.post(api_url, headers=headers, files=files, data=payload)
#         response.raise_for_status()  # 요청 실패 시 예외 발생
#         result = response.json()
#         text_results = ' '.join([field['inferText'] for field in result['images'][0]['fields']])
#         return jsonify({'text': text_results})
#     except requests.exceptions.RequestException as e:
#         return jsonify({'error': str(e)}), 500
#     finally:
#         files['file'].close()  # 파일 핸들을 명시적으로 닫음
#
#
# # 이미지 업로드 된 거 받아오기
# UPLOAD_FOLDER = '/path/to/the/uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#
# @app.route('/imageupload', methods=['POST'])
# def file_upload():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400
#     if file:
#         filename = file.filename
#         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#         return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200


# 새로운 코드
@app.route('/upload', methods=['POST', 'GET'])
def process_image():
    if request.method == 'POST':
        # 파일 받기
        file = request.files['file']
        print(file)
        if file:
            # API 설정
            api_url = 'https://eoxy3e0azd.apigw.ntruss.com/custom/v1/29612/cb56e51bd632826fb10645cf94923e9934c4789df11256f9baaf17de98b0e7f9/general'
            secret_key = 'VG1ocGpZcXlDU2xuRWFRaU1XdEtWWm1JSlZxeVV2c1A='
            headers = {
                'X-OCR-SECRET': secret_key
            }

            # 파일을 메모리에서 직접 읽어 API로 전송
            files = {'file': (file.filename, file.stream, file.content_type)}
            request_json = {
                'images': [{'format': file.content_type.split('/')[1], 'name': 'demo'}],
                'requestId': str(uuid.uuid4()),
                'version': 'V2',
                'timestamp': int(round(time.time() * 1000))
            }
            payload = {'message': json.dumps(request_json).encode('UTF-8')}
            print(payload)

            try:
                # 파일과 함께 페이로드 전송
                response = requests.post(api_url, headers=headers, files=files, data=payload)
                response.raise_for_status()  # 요청 실패 시 예외 발생
                result = response.json()
                text_results = ' '.join([field['inferText'] for field in result['images'][0]['fields']])
                print(text_results)
                print("SUCCESS")
                # return jsonify({'text': "SUCCESS"})
                return jsonify({'text': text_results})

            except requests.exceptions.RequestException as e:
                print("FAIL")
                print(e)
                return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'No file provided'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

