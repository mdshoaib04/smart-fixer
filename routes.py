from flask import session, render_template, request, jsonify, redirect, url_for
from flask_login import current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from app import app, db
from replit_auth import require_login, make_replit_blueprint
from models import *
from gemini_helper import *
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from datetime import datetime, date
import os

app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")
socketio = SocketIO(app, cors_allowed_origins="*")

@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('upload_or_write'))
    return render_template('login.html')

@app.route('/upload-or-write')
@require_login
def upload_or_write():
    return render_template('upload_or_write.html', user=current_user)

@app.route('/editor')
@require_login
def editor():
    return render_template('editor.html', user=current_user)

@app.route('/api/detect-language', methods=['POST'])
@require_login
def api_detect_language():
    data = request.json
    code = data.get('code', '')
    language = detect_language(code)
    return jsonify({'language': language})

@app.route('/api/review', methods=['POST'])
@require_login
def api_review():
    data = request.json
    code = data.get('code', '')
    language = data.get('language', 'Unknown')
    profession = data.get('profession', 'student')
    
    result = review_code(code, language, profession)
    
    history = CodeHistory(
        user_id=current_user.id,
        code=code,
        language=language,
        action='review',
        result=result
    )
    db.session.add(history)
    db.session.commit()
    
    return jsonify({'result': result})

@app.route('/api/explain', methods=['POST'])
@require_login
def api_explain():
    data = request.json
    code = data.get('code', '')
    language = data.get('language', 'Unknown')
    profession = data.get('profession', 'student')
    
    result = explain_code(code, language, profession)
    
    history = CodeHistory(
        user_id=current_user.id,
        code=code,
        language=language,
        action='explain',
        result=result
    )
    db.session.add(history)
    db.session.commit()
    
    return jsonify({'result': result})

@app.route('/api/compile', methods=['POST'])
@require_login
def api_compile():
    data = request.json
    code = data.get('code', '')
    language = data.get('language', 'Unknown')
    profession = data.get('profession', 'student')
    
    result = compile_check(code, language, profession)
    
    history = CodeHistory(
        user_id=current_user.id,
        code=code,
        language=language,
        action='compile',
        result=result
    )
    db.session.add(history)
    db.session.commit()
    
    return jsonify({'result': result})

@app.route('/api/question', methods=['POST'])
@require_login
def api_question():
    data = request.json
    question = data.get('question', '')
    code = data.get('code')
    language = data.get('language')
    
    result = answer_question(question, code, language)
    return jsonify({'result': result})

@app.route('/api/translate', methods=['POST'])
@require_login
def api_translate():
    data = request.json
    code = data.get('code', '')
    from_lang = data.get('from_lang', 'Unknown')
    to_lang = data.get('to_lang', 'Python')
    
    result = translate_code(code, from_lang, to_lang)
    return jsonify({'result': result})

@app.route('/api/dictionary', methods=['POST'])
@require_login
def api_dictionary():
    data = request.json
    language = data.get('language', 'Python')
    searchTerm = data.get('searchTerm', '')
    
    result = get_dictionary_content(language, searchTerm)
    return jsonify({'result': result})

@app.route('/api/code-history')
@require_login
def api_code_history():
    history = CodeHistory.query.filter_by(user_id=current_user.id).order_by(CodeHistory.created_at.desc()).limit(50).all()
    return jsonify([{
        'id': h.id,
        'code': h.code,
        'language': h.language,
        'action': h.action,
        'result': h.result,
        'created_at': h.created_at.isoformat()
    } for h in history])

@app.route('/api/update-profession', methods=['POST'])
@require_login
def api_update_profession():
    data = request.json
    profession = data.get('profession', 'student')
    current_user.profession = profession
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/profile')
@require_login
def api_profile():
    posts = Post.query.filter_by(user_id=current_user.id).all()
    friends = Friendship.query.filter(
        ((Friendship.user_id == current_user.id) | (Friendship.friend_id == current_user.id)) &
        (Friendship.status == 'accepted')
    ).all()
    
    return jsonify({
        'user': {
            'id': current_user.id,
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'email': current_user.email,
            'profile_image_url': current_user.profile_image_url,
            'bio': current_user.bio,
            'profession': current_user.profession
        },
        'posts_count': len(posts),
        'friends_count': len(friends)
    })

@app.route('/api/update-profile', methods=['POST'])
@require_login
def api_update_profile():
    data = request.json
    current_user.bio = data.get('bio', current_user.bio)
    current_user.profession = data.get('profession', current_user.profession)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/posts', methods=['GET', 'POST'])
@require_login
def api_posts():
    if request.method == 'POST':
        data = request.json
        post = Post(
            user_id=current_user.id,
            code=data.get('code', ''),
            language=data.get('language', 'Unknown'),
            description=data.get('description', '')
        )
        db.session.add(post)
        db.session.commit()
        return jsonify({'success': True, 'post_id': post.id})
    
    posts = Post.query.order_by(Post.created_at.desc()).limit(50).all()
    return jsonify([{
        'id': p.id,
        'user_id': p.user_id,
        'author_name': f"{p.author.first_name or ''} {p.author.last_name or ''}".strip() or 'User',
        'author_image': p.author.profile_image_url,
        'code': p.code,
        'language': p.language,
        'description': p.description,
        'likes': p.likes,
        'created_at': p.created_at.isoformat(),
        'comments_count': len(p.comments)
    } for p in posts])

@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
@require_login
def api_like_post(post_id):
    post = Post.query.get_or_404(post_id)
    existing_like = PostLike.query.filter_by(post_id=post_id, user_id=current_user.id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        post.likes -= 1
    else:
        like = PostLike(post_id=post_id, user_id=current_user.id)
        db.session.add(like)
        post.likes += 1
        
        if post.user_id != current_user.id:
            notif = Notification(
                user_id=post.user_id,
                type='like',
                content=f"{current_user.first_name} liked your post",
                from_user_id=current_user.id
            )
            db.session.add(notif)
    
    db.session.commit()
    return jsonify({'success': True, 'likes': post.likes})

@app.route('/api/posts/<int:post_id>/comments', methods=['GET'])
@require_login
def api_comments(post_id):
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    return jsonify([{
        'id': c.id,
        'author_name': f"{c.user.first_name or ''} {c.user.last_name or ''}".strip() or 'User',
        'user_image': c.user.profile_image_url,
        'content': c.content,
        'created_at': c.created_at.isoformat()
    } for c in comments])

@app.route('/api/posts/<int:post_id>/comment', methods=['POST'])
@require_login
def api_add_comment(post_id):
    data = request.json
    comment = Comment(
        post_id=post_id,
        user_id=current_user.id,
        content=data.get('content', '')
    )
    db.session.add(comment)
    
    post = Post.query.get(post_id)
    if post and post.user_id != current_user.id:
        notif = Notification(
            user_id=post.user_id,
            type='comment',
            content=f"{current_user.first_name} commented on your post",
            from_user_id=current_user.id
        )
        db.session.add(notif)
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/explore-posts')
@require_login
def api_explore_posts():
    friend_ids = []
    friendships = Friendship.query.filter(
        ((Friendship.user_id == current_user.id) | (Friendship.friend_id == current_user.id)) &
        (Friendship.status == 'accepted')
    ).all()
    
    for f in friendships:
        friend_id = f.friend_id if f.user_id == current_user.id else f.user_id
        friend_ids.append(friend_id)
    
    posts = Post.query.filter(Post.user_id.in_(friend_ids)).order_by(Post.created_at.desc()).limit(50).all()
    
    return jsonify([{
        'id': p.id,
        'user_id': p.user_id,
        'author_name': f"{p.author.first_name or ''} {p.author.last_name or ''}".strip() or 'User',
        'author_image': p.author.profile_image_url,
        'code': p.code,
        'language': p.language,
        'description': p.description,
        'likes': p.likes,
        'liked': bool(PostLike.query.filter_by(post_id=p.id, user_id=current_user.id).first()),
        'created_at': p.created_at.isoformat(),
        'comments_count': len(p.comments)
    } for p in posts])

@app.route('/api/friends')
@require_login
def api_friends():
    friends = Friendship.query.filter(
        ((Friendship.user_id == current_user.id) | (Friendship.friend_id == current_user.id)) &
        (Friendship.status == 'accepted')
    ).all()
    
    friend_list = []
    for f in friends:
        friend_user = User.query.get(f.friend_id if f.user_id == current_user.id else f.user_id)
        if friend_user:
            friend_list.append({
                'id': friend_user.id,
                'name': f"{friend_user.first_name or ''} {friend_user.last_name or ''}".strip() or 'User',
                'image': friend_user.profile_image_url,
                'email': friend_user.email
            })
    
    return jsonify(friend_list)

@app.route('/api/friend-request', methods=['POST'])
@require_login
def api_friend_request():
    data = request.json
    friend_email = data.get('email', '')
    friend = User.query.filter_by(email=friend_email).first()
    
    if not friend:
        return jsonify({'error': 'User not found'}), 404
    
    if friend.id == current_user.id:
        return jsonify({'error': 'Cannot add yourself'}), 400
    
    existing = Friendship.query.filter(
        ((Friendship.user_id == current_user.id) & (Friendship.friend_id == friend.id)) |
        ((Friendship.user_id == friend.id) & (Friendship.friend_id == current_user.id))
    ).first()
    
    if existing:
        return jsonify({'error': 'Request already exists'}), 400
    
    friendship = Friendship(user_id=current_user.id, friend_id=friend.id, status='pending')
    db.session.add(friendship)
    
    notif = Notification(
        user_id=friend.id,
        type='friend_request',
        content=f"{current_user.first_name} sent you a friend request",
        from_user_id=current_user.id
    )
    db.session.add(notif)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/notifications')
@require_login
def api_notifications():
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(50).all()
    
    return jsonify([{
        'id': n.id,
        'type': n.type,
        'content': n.content,
        'from_user': {
            'id': n.from_user.id,
            'name': f"{n.from_user.first_name or ''} {n.from_user.last_name or ''}".strip() or 'User',
            'image': n.from_user.profile_image_url
        } if n.from_user else None,
        'read': n.read,
        'created_at': n.created_at.isoformat()
    } for n in notifs])

@app.route('/api/notifications/<int:notif_id>/respond', methods=['POST'])
@require_login
def api_respond_notification(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    data = request.json
    action = data.get('action')
    
    if notif.type == 'friend_request':
        friendship = Friendship.query.filter(
            ((Friendship.user_id == notif.from_user_id) & (Friendship.friend_id == current_user.id))
        ).first()
        
        if friendship:
            if action == 'accept':
                friendship.status = 'accepted'
            else:
                db.session.delete(friendship)
    
    notif.read = True
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/time-spent')
@require_login
def api_time_spent():
    time_data = TimeSpent.query.filter_by(user_id=current_user.id).order_by(TimeSpent.date.desc()).limit(365).all()
    return jsonify([{
        'date': t.date.isoformat(),
        'minutes': t.minutes
    } for t in time_data])

@app.route('/api/track-time', methods=['POST'])
@require_login
def api_track_time():
    today = date.today()
    time_entry = TimeSpent.query.filter_by(user_id=current_user.id, date=today).first()
    
    if not time_entry:
        time_entry = TimeSpent(user_id=current_user.id, date=today, minutes=1)
        db.session.add(time_entry)
    else:
        time_entry.minutes += 1
    
    db.session.commit()
    return jsonify({'success': True})

@socketio.on('join')
def on_join(data):
    room = data.get('room')
    join_room(room)
    emit('user_joined', {'user': current_user.first_name}, room=room)

@socketio.on('leave')
def on_leave(data):
    room = data.get('room')
    leave_room(room)
    emit('user_left', {'user': current_user.first_name}, room=room)

@socketio.on('send_message')
def on_message(data):
    room = data.get('room')
    message_text = data.get('message')
    code_snippet = data.get('code_snippet')
    receiver_id = data.get('receiver_id')
    
    message = Message(
        sender_id=current_user.id,
        receiver_id=receiver_id if receiver_id else None,
        content=message_text,
        code_snippet=code_snippet
    )
    db.session.add(message)
    db.session.commit()
    
    emit('receive_message', {
        'sender': current_user.first_name,
        'sender_image': current_user.profile_image_url,
        'message': message_text,
        'code_snippet': code_snippet,
        'timestamp': message.created_at.isoformat()
    }, room=room)

@app.route('/api/messages/<user_id>')
@require_login
def api_get_messages(user_id):
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()
    
    return jsonify([{
        'id': m.id,
        'sender_id': m.sender_id,
        'content': m.content,
        'code_snippet': m.code_snippet,
        'created_at': m.created_at.isoformat()
    } for m in messages])
