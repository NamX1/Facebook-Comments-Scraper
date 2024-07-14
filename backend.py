from flask import Flask, jsonify, request, send_from_directory
import requests

app = Flask(__name__)

# Replace with your actual access token and page ID
ACCESS_TOKEN = 'EAAeVZBkw52iMBO0YcwpeM7WSUVLCDuwZCz2U0YrQnQh3hfR8ENKZC725W3XCEgQZBSwFpBEQR2ERjBTG4lQZBAmfdZB8g6qANZCBi1UKuiFTWabNL5ZCeaw712ZAZCdj8Mk9s80ZAKOVdcdgw0JBA8TnZAeI9bkZAu1jTUn4gAvo6AIK6y6H2ZBinzpQRGB1kGILXypiO9JiwGOJSM70U5ZCPKZCOITWjfqz'
PAGE_ID = '375167915678217'

def fetch_comments_from_facebook():
    comments = []
    url = f'https://graph.facebook.com/v20.0/{PAGE_ID}/feed'
    params = {
        'access_token': ACCESS_TOKEN,
        'fields': 'comments{message,from{name,id},created_time,comment_count,is_hidden}',
        'limit': 100  # Adjust based on your needs, max is 1000 per Facebook's API
    }
    try:
        while True:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise HTTPError for bad responses
            data = response.json()
            if 'data' in data:
                for post in data['data']:
                    if 'comments' in post:
                        for comment in post['comments']['data']:
                            comments.append({
                                'id': comment['id'],
                                'message': comment.get('message', ''),
                                'from': {
                                    'name': comment['from']['name'],
                                    'id': comment['from']['id']
                                },
                                'created_time': comment.get('created_time', ''),
                                'is_hidden': comment.get('is_hidden', False)
                            })
                if 'paging' in data and 'next' in data['paging']:
                    url = data['paging']['next']
                else:
                    break
            else:
                break
        return comments
    except requests.exceptions.RequestException as e:
        print(f"Error fetching comments from Facebook API: {str(e)}")
        raise  # Re-raise the exception to be handled by Flask route

@app.route('/fetch_comments', methods=['POST'])
def fetch_comments():
    try:
        comments = fetch_comments_from_facebook()
        if comments:
            return jsonify({'status': 'success', 'comments': comments})
        else:
            return jsonify({'status': 'error', 'message': 'No comments found from Facebook'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    except KeyError as e:
        return jsonify({'status': 'error', 'message': f'KeyError: {str(e)}'}), 500
    
@app.route('/delete_comment', methods=['POST'])
def delete_comment():
    comment_id = request.json['comment_id']
    url = f'https://graph.facebook.com/v20.0/{comment_id}'
    response = requests.delete(url, params={'access_token': ACCESS_TOKEN})
    if response.status_code == 200:
        return jsonify({'status': 'success', 'response': response.json()})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to delete comment on Facebook'})

@app.route('/hide_comment', methods=['POST'])
def hide_comment():
    comment_id = request.json['comment_id']
    is_hidden = request.json.get('is_hidden', True)
    url = f'https://graph.facebook.com/v20.0/{comment_id}'
    params = {'access_token': ACCESS_TOKEN, 'is_hidden': str(is_hidden).lower()}
    response = requests.post(url, params=params)
    if response.status_code == 200:
        return jsonify({'status': 'success', 'response': response.json()})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to hide comment on Facebook'})

@app.route('/unhide_comment', methods=['POST'])
def unhide_comment():
    comment_id = request.json['comment_id']
    url = f'https://graph.facebook.com/v20.0/{comment_id}'
    params = {'access_token': ACCESS_TOKEN, 'is_hidden': 'false'}
    response = requests.post(url, params=params)
    if response.status_code == 200:
        return jsonify({'status': 'success', 'response': response.json()})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to unhide comment on Facebook'})

@app.route('/reply_comment', methods=['POST'])
def reply_comment():
    comment_id = request.json['comment_id']
    message = request.json['message']
    url = f'https://graph.facebook.com/v20.0/{comment_id}/comments'
    params = {'access_token': ACCESS_TOKEN, 'message': message}
    response = requests.post(url, params=params)
    if response.status_code == 200:
        return jsonify({'status': 'success', 'response': response.json()})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to reply to comment on Facebook'})

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
