# apply_schema_fix.py
#
# Production consistency migration script for MySQL schema.
# Aligns ENUM columns with application lifecycle states.

from app import create_app, db
from sqlalchemy import text

def apply_fixes():
    app = create_app()
    with app.app_context():
        statements = [
            "ALTER TABLE seat_holds MODIFY COLUMN status ENUM('active','released','expired','consumed','converted') NOT NULL DEFAULT 'active';",
            "ALTER TABLE events MODIFY COLUMN status ENUM('draft','published','upcoming','ongoing','completed','cancelled') NOT NULL DEFAULT 'published';",
            "ALTER TABLE venues MODIFY COLUMN venue_type ENUM('seated','general','general_admission','mixed') NOT NULL DEFAULT 'seated';",
            "ALTER TABLE reward_transactions MODIFY COLUMN transaction_type ENUM('cashback','redeemed','adjustment','credit','debit') NOT NULL;",
            "ALTER TABLE notifications MODIFY COLUMN notification_type ENUM('booking','booking_confirmation','booking_cancellation','ticket','reward','event','event_reschedule','reschedule','promo','system') NOT NULL DEFAULT 'system';",
            "ALTER TABLE users MODIFY COLUMN phone VARCHAR(20) DEFAULT NULL;",
            "ALTER TABLE users MODIFY COLUMN id_document VARCHAR(255) DEFAULT NULL;",
        ]

        for stmt in statements:
            print("Executing:", stmt)
            db.session.execute(text(stmt))
        
        db.session.commit()
        print("\nAll ALTER TABLE statements applied successfully to MySQL!")

if __name__ == "__main__":
    apply_fixes()
