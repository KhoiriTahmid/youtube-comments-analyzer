import sys
import json
import itertools
from youtube_comment_downloader import YoutubeCommentDownloader

def get_comments(video_id:str):
    max_results=10000
    data = []
    downloader = YoutubeCommentDownloader()
    try:
        comment_generator = downloader.get_comments(youtube_id=video_id)

        for comment in itertools.islice(comment_generator, max_results):
            # You can append the whole comment object or just specific parts
            data.append({
                'cid': comment.get('cid'),
                'video_id':video_id,
                'text': comment.get('text'),
                'author': comment.get('author'),
            })
        return data 
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        video_id_arg = sys.argv[1]
        
        data = get_comments(video_id_arg)
        
        print(json.dumps(data))
    else:
        print(json.dumps({"error": "Video ID atau max_results tidak diberikan."}))