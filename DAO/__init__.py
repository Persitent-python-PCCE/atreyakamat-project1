# DAO (Data Access Object) package for SeatMeUp.
#
# Each file in this folder handles database operations for ONE model.
# For example, user_dao.py only talks to the `users` table.
# This file just makes the DAO classes easy to import elsewhere:
#
#     from DAO import UserDAO
#
# We deliberately do NOT use a generic BaseDAO or abstract repository pattern.
# Each DAO is written explicitly and is easy to read on its own.

from .user_dao import UserDAO

__all__ = ["UserDAO"]
