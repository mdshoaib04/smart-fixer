
@app.route('/api/user-stats')
@require_login
def api_user_stats():
    """Get current user stats including time tracking"""
    try:
        # Post count
        post_count = Post.query.filter_by(user_id=current_user.id).count()
        
        # Follower/Following counts
        follower_count = Follower.query.filter_by(user_id=current_user.id).count()
        following_count = Follower.query.filter_by(follower_id=current_user.id).count()
        
        # Time tracking stats
        today = date.today()
        
        # 1. Today's time
        today_time = TimeSpent.query.filter_by(user_id=current_user.id, date=today).first()
        today_minutes = today_time.minutes if today_time else 0
        
        # 2. Last 7 days
        last_7_days = []
        for i in range(7):
            day = today - timedelta(days=i)
            time_record = TimeSpent.query.filter_by(user_id=current_user.id, date=day).first()
            minutes = time_record.minutes if time_record else 0
            last_7_days.append({
                'date': day.isoformat(),
                'day_name': day.strftime('%a'),
                'minutes': minutes
            })
        last_7_days.reverse() # Show oldest to newest
        
        # 3. Last month total
        thirty_days_ago = today - timedelta(days=30)
        last_month_total = db.session.query(db.func.sum(TimeSpent.minutes)).filter(
            TimeSpent.user_id == current_user.id,
            TimeSpent.date >= thirty_days_ago
        ).scalar() or 0
        
        # 4. Total active days
        total_active_days = TimeSpent.query.filter_by(user_id=current_user.id).count()
        
        # 5. Streaks
        current_streak = current_user.current_streak or 0
        
        # Check streak validity (if missed yesterday, streak is 0 for display unless today is tracked)
        # However, we only reset on write. For read, let's keep it simple: what's in DB.
        # But if last_streak_date < yesterday, effectively streak is broken. 
        # API should reflect that? Or just let the tracking update fix it? 
        # Let's trust DB but maybe visually indicate if it's "at risk"? 
        # User asked for "Real". If I login today after a week, it shows my old streak until I track time? 
        # No, better to show 0 if broken.
        
        if current_user.last_streak_date and current_user.last_streak_date < (today - timedelta(days=1)):
             current_streak = 0
             
        longest_streak = current_user.longest_streak or 0

        # Format time for display (e.g. "2h 35m")
        def format_minutes(mins):
            h = mins // 60
            m = mins % 60
            if h > 0:
                return f"{h}h {m}m"
            return f"{m}m"

        return jsonify({
            'post_count': post_count,
            'follower_count': follower_count,
            'following_count': following_count,
            'today_minutes': today_minutes,
            'today_time_display': format_minutes(today_minutes),
            'last_7_days': last_7_days,
            'last_month_total': last_month_total,
            'last_month_display': format_minutes(last_month_total),
            'total_active_days': total_active_days,
            'current_streak': current_streak,
            'longest_streak': longest_streak
        })
        
    except Exception as e:
        print(f"Error fetching user stats: {e}")
        return jsonify({'error': 'Failed to fetch stats'}), 500

@app.route('/api/track-time', methods=['POST'])
@require_login
def track_time():
    """Track user time on site and update streaks"""
    try:
        data = request.get_json()
        duration_seconds = data.get('duration', 0)
        
        if not duration_seconds or duration_seconds <= 0:
            return jsonify({'success': False})
            
        today = date.today()
        user = User.query.get(current_user.id)
        
        # 1. Update TimeSpent
        time_record = TimeSpent.query.filter_by(user_id=current_user.id, date=today).first()
        if not time_record:
            time_record = TimeSpent(user_id=current_user.id, date=today, minutes=0)
            db.session.add(time_record)
        
        # Add 1 minute roughly for every 60s sent. 
        # We assume frontend sends heartbeat every 60s.
        if duration_seconds >= 30: 
             time_record.minutes += 1
        
        # 2. Update Streaks
        last_date = user.last_streak_date
        
        if last_date != today:
            if last_date == today - timedelta(days=1):
                # Consecutive day: increment
                user.current_streak = (user.current_streak or 0) + 1
            elif last_date is None:
                # First time ever
                user.current_streak = 1
            else:
                # Broken streak (last active > 1 day ago)
                # Reset to 1 (today counts as 1)
                user.current_streak = 1
                
            user.last_streak_date = today
            
            # Update longest
            if user.current_streak > (user.longest_streak or 0):
                user.longest_streak = user.current_streak
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'daily_minutes': time_record.minutes,
            'streak': user.current_streak
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error tracking time: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
