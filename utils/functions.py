from datetime import datetime, timezone

def humanize_time(dt):
    now = datetime.now(timezone.utc)
    diff = now - dt
    seconds = diff.total_seconds()

    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    minutes = int(seconds // 60)
    if minutes < 60:
        return f"{minutes} minutes ago"
    hours = int(minutes // 60)
    if hours < 24:
        return f"{hours} hours ago"
    days = int(hours // 24)
    if days < 7:
        return f"{days} days ago"
    return dt.strftime("%b %d, %Y %H:%M:%S")