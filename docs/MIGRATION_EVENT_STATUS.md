# Event Status Migration: Published / Unpublished Only

## Overview
This migration standardizes the `events.status` column across SeatMeUp so that the ONLY valid statuses are:
- `published`
- `unpublished`

All legacy/custom statuses (`draft`, `cancelled`, `completed`, `upcoming`, `ongoing`) are eliminated.

---

## Safe SQL Migration Script

```sql
-- Step 1: Temporarily expand the ENUM to include 'unpublished'
ALTER TABLE events 
MODIFY COLUMN status ENUM('draft', 'published', 'upcoming', 'ongoing', 'completed', 'cancelled', 'unpublished') 
NOT NULL DEFAULT 'unpublished';

-- Step 2: Safely update existing rows with legacy statuses
UPDATE events 
SET status = 'unpublished' 
WHERE status IN ('draft', 'cancelled', 'completed', 'upcoming', 'ongoing');

UPDATE events 
SET status = 'published' 
WHERE status = 'published';

-- Step 3: Strictly restrict ENUM to ONLY 'published' and 'unpublished'
ALTER TABLE events 
MODIFY COLUMN status ENUM('published', 'unpublished') 
NOT NULL DEFAULT 'unpublished';
```

---

## Rollback SQL (If ever needed)
```sql
ALTER TABLE events 
MODIFY COLUMN status ENUM('draft', 'published', 'upcoming', 'ongoing', 'completed', 'cancelled') 
NOT NULL DEFAULT 'draft';
```
