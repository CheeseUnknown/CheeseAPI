import uuid
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from User.model import User

users: Dict[uuid.UUID, 'User'] = {}
