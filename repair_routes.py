
import os

file_path = r'c:\Users\Admin\OneDrive\Desktop\SmartFixer\routes.py'

# Read the file
with open(file_path, 'rb') as f:
    content_bytes = f.read()

# Try to decode as utf-8, ignoring errors to get the good part
content = content_bytes.decode('utf-8', errors='ignore')

# Find the point where corruption starts (around line 636)
# The corruption looks like " @ a p p . r o u t e"
split_marker = "@ a p p . r o u t e"
split_index = content.find(split_marker)

if split_index != -1:
    clean_content = content[:split_index]
else:
    # If we can't find the marker, try to find the last good line
    # Line 635 is "            return jsonify({'success': False, 'error': 'Failed to upload file'}), 500"
    last_good_line = "return jsonify({'success': False, 'error': 'Failed to upload file'}), 500"
    split_index = content.find(last_good_line)
    if split_index != -1:
        clean_content = content[:split_index + len(last_good_line)] + "\n\n"
    else:
        print("Could not find split point, using hardcoded line count approach")
        # Fallback: read lines and stop when we see spaced out chars
        lines = content.splitlines()
        clean_lines = []
        for line in lines:
            if " @ a p p " in line or "\x00" in line:
                break
            clean_lines.append(line)
        clean_content = "\n".join(clean_lines)

# Ensure init_app calls register_socketio_events
if "register_socketio_events()" not in clean_content:
    clean_content = clean_content.replace("register_routes()", "register_routes()\n    register_socketio_events()")

# Append the missing code
new_code = """
    @app.route('/api/user-status/<user_id>')
    @require_login
    def api_user_status(user_id):
        \"\"\"API endpoint to get user's online status\"\"\"
        try:
            user = User.query.get(user_id)
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            # Format last seen time in 12-hour format with AM/PM
            last_seen_formatted = None
            if user.last_seen:
                # Convert UTC to local time (IST) and format as 12-hour with AM/PM
                from datetime import timezone, timedelta
                # Assuming IST (UTC+5:30)
                ist_offset = timedelta(hours=5, minutes=30)
                last_seen_ist = user.last_seen + ist_offset
                last_seen_formatted = last_seen_ist.strftime('%I:%M %p')
            
            return jsonify({
                'success': True,
                'is_online': user.is_online,
                'last_seen': user.last_seen.isoformat() if user.last_seen else None,
                'last_seen_formatted': last_seen_formatted
            })
        except Exception as e:
            print(f"Error getting user status: {e}")
            return jsonify({'success': False, 'error': 'Failed to get user status'}), 500

def register_socketio_events():
    \"\"\"Register Socket.IO event handlers\"\"\"
    
    @socketio.on('join')
    def on_join(data):
        \"\"\"Handle user joining a chat room\"\"\"
        room = data.get('room')
        if room:
            join_room(room)
            print(f"User joined room: {room}")
    
    @socketio.on('chat_window_opened')
    def on_chat_window_opened(data):
        \"\"\"Handle user opening chat window - mark as online\"\"\"
        if current_user.is_authenticated:
            # Mark user as online
            current_user.is_online = True
            current_user.last_seen = datetime.utcnow()
            current_user.last_active = datetime.utcnow()
            db.session.commit()
            
            print(f"User {current_user.id} ({current_user.username}) is now ONLINE")
            
            # Emit presence update to all connected clients
            socketio.emit('user_presence_update', {
                'user_id': current_user.id,
                'is_online': True,
                'last_seen': current_user.last_seen.isoformat()
            }, broadcast=True)
            
            print(f"Broadcasted ONLINE status for user {current_user.id}")
    
    @socketio.on('chat_window_closed')
    def on_chat_window_closed(data):
        \"\"\"Handle user closing chat window - mark as offline\"\"\"
        if current_user.is_authenticated:
            # Mark user as offline
            current_user.is_online = False
            current_user.last_seen = datetime.utcnow()
            db.session.commit()
            
            print(f"User {current_user.id} ({current_user.username}) is now OFFLINE")
            
            # Emit presence update to all connected clients
            socketio.emit('user_presence_update', {
                'user_id': current_user.id,
                'is_online': False,
                'last_seen': current_user.last_seen.isoformat()
            }, broadcast=True)
            
            print(f"Broadcasted OFFLINE status for user {current_user.id}")
    
    @socketio.on('user_activity')
    def on_user_activity(data):
        \"\"\"Handle user activity events for presence tracking\"\"\"
        if current_user.is_authenticated:
            # Update user's last active timestamp (keep online status)
            current_user.last_active = datetime.utcnow()
            current_user.last_seen = datetime.utcnow()
            if not current_user.is_online:
                current_user.is_online = True
            db.session.commit()
            
            # Emit presence update to all connected clients
            socketio.emit('user_presence_update', {
                'user_id': current_user.id,
                'is_online': True,
                'last_seen': current_user.last_seen.isoformat()
            }, broadcast=True)
    
    @socketio.on('disconnect')
    def on_disconnect():
        \"\"\"Handle user disconnect\"\"\"
        if current_user.is_authenticated:
            # Mark user as offline and update last seen timestamp
            current_user.is_online = False
            current_user.last_seen = datetime.utcnow()
            db.session.commit()
            
            # Emit presence update to all connected clients
            socketio.emit('user_presence_update', {
                'user_id': current_user.id,
                'is_online': False,
                'last_seen': current_user.last_seen.isoformat()
            }, broadcast=True)
"""

full_content = clean_content + new_code

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(full_content)

print("Successfully repaired routes.py")
