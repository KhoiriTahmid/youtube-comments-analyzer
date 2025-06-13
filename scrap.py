import itertools
from youtube_comment_downloader import YoutubeCommentDownloader
downloader = YoutubeCommentDownloader()

def get_comments(video_id:str):
    max_results=10000
    data = []
    try:
        comment_generator = downloader.get_comments(youtube_id=video_id)

        for comment in itertools.islice(comment_generator, max_results):
            data.append({
                'cid': comment.get('cid'),
                'video_id':video_id,
                'text': comment.get('text'),
                'author': comment.get('author'),
            })
            
        return data 
    except Exception as e:
        return {"error": str(e)}
