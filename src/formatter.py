from datetime import datetime, timezone
from typing import Dict, Any, Optional


def get_difficulty_badge(rating: Optional[int]) -> str:
    """Returns a colored indicator and label based on problem rating."""
    if rating is None:
        return "⚪ Unrated"
    if rating < 1200:
        return f"🟢 Easy ({rating})"
    if rating < 1600:
        return f"🟡 Medium ({rating})"
    if rating < 2000:
        return f"🟠 Hard ({rating})"
    if rating < 2400:
        return f"🔴 Very Hard ({rating})"
    return f"🟣 Master/Grandmaster ({rating})"


def get_daily_tip() -> str:
    """Returns a helpful DSA & competitive programming tip."""
    tips = [
        "Check array & data constraints first to deduce the required time complexity O(N), O(N log N), or O(1).",
        "Write out edge cases (N=0, N=1, max/min values, negative numbers) before writing code.",
        "Spend 20-25 minutes thinking with pen & paper before typing out a solution.",
        "Look for monotonic properties — if increasing a threshold preserves validity, Binary Search on Answer will work!",
        "Watch out for 32-bit integer overflow! Use 64-bit integers (long long / BigInt) when sums exceed 2*10^9.",
        "For graph/tree problems, check if it's a DAG (Dynamic Programming/Topo Sort) or if standard BFS/DFS is sufficient.",
        "If you get stuck on a 2D matrix or grid problem, consider transforming it into BFS shortest-path or DSU.",
        "Always review the editorial/top solutions after solving to discover cleaner idioms and techniques."
    ]
    import random
    return random.choice(tips)


def format_whatsapp_message(
    problem: Dict[str, Any],
    handle: str = "",
    target_range: str = ""
) -> str:
    """
    Format DSA problem details into a clean, beautiful WhatsApp message.
    """
    today_str = datetime.now(timezone.utc).strftime("%A, %d %B %Y")
    
    contest_id = problem.get("contestId", "")
    index = problem.get("index", "")
    name = problem.get("name", "Unknown")
    rating = problem.get("rating")
    tags = problem.get("tags", [])
    url = problem.get("url", "")
    
    tags_str = ", ".join(tags) if tags else "General DSA"
    difficulty = get_difficulty_badge(rating)
    tip = get_daily_tip()

    lines = [
        "🔥 *DAILY DSA NOTIFIER* 🔥",
        f"📅 _{today_str}_",
        ""
    ]

    if handle:
        user_rating = problem.get("user_rating")
        rating_info = f" (Rating: {user_rating})" if user_rating else ""
        lines.append(f"👤 *Coder:* @{handle}{rating_info}")
    
    if target_range:
        lines.append(f"🎯 *Target Rating:* {target_range}")

    lines.extend([
        f"📌 *Problem:* {contest_id}{index} - *{name}*",
        f"⭐ *Level:* {difficulty}",
        f"🏷️ *DSA Topics:* {tags_str}",
        "",
        f"🔗 *Solve Link:*",
        f"{url}",
        "",
        f"💡 *DSA Tip of the Day:*",
        f"_{tip}_",
        "",
        "🚀 _Keep up the streak and build your problem-solving muscle!_ ✨"
    ])

    return "\n".join(lines)
