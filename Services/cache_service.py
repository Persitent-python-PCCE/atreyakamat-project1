# Services/cache_service.py
#
# WHY: Provides simple caching configuration and invalidation utilities.
# The analytics cache is cleared whenever data changes (event updates, bookings, cancellations).

from app import cache

def invalidate_analytics_cache():
    """
    WHY: Clears the in-process cache to ensure stale analytics dashboard
    or top events summaries are recalculated immediately after mutations.
    """
    try:
        cache.clear()
    except Exception:
        pass
