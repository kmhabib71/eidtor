import logging
from datetime import datetime, timedelta
from typing import Optional, List
from passlib.context import CryptContext
from jose import jwt
from bson.objectid import ObjectId

from app.core.config import settings
from app.db.mongodb import get_database
from app.models.user import User, UserCreate, UserInDB, UserUpdate, Token

logger = logging.getLogger("silence-cutter")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user_collection():
    db = await get_database()
    return db.users

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_user_by_email(email: str) -> Optional[UserInDB]:
    users = await get_user_collection()
    user_data = await users.find_one({"email": email})
    if user_data:
        return UserInDB(**user_data)
    return None

async def get_user_by_id(user_id: str) -> Optional[User]:
    users = await get_user_collection()
    user_data = await users.find_one({"id": user_id})
    if user_data:
        user_in_db = UserInDB(**user_data)
        return User(
            id=user_in_db.id,
            email=user_in_db.email,
            full_name=user_in_db.full_name,
            is_active=user_in_db.is_active,
            is_admin=user_in_db.is_admin,
            subscription_tier=user_in_db.subscription_tier,
            subscription_end_date=user_in_db.subscription_end_date,
            processing_minutes_used=user_in_db.processing_minutes_used,
            processing_minutes_limit=user_in_db.processing_minutes_limit,
            created_at=user_in_db.created_at,
            updated_at=user_in_db.updated_at
        )
    return None

async def authenticate_user(email: str, password: str) -> Optional[User]:
    user = await get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    
    return User(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_admin=user.is_admin,
        subscription_tier=user.subscription_tier,
        subscription_end_date=user.subscription_end_date,
        processing_minutes_used=user.processing_minutes_used,
        processing_minutes_limit=user.processing_minutes_limit,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

async def create_user(user_create: UserCreate) -> User:
    users = await get_user_collection()
    
    # Check if user already exists
    existing_user = await get_user_by_email(user_create.email)
    if existing_user:
        logger.warning(f"Attempted to create user with existing email: {user_create.email}")
        return None
    
    # Create new user
    user_in_db = UserInDB(
        email=user_create.email,
        full_name=user_create.full_name,
        hashed_password=get_password_hash(user_create.password),
    )
    
    result = await users.insert_one(user_in_db.model_dump())
    
    logger.info(f"Created new user with email: {user_create.email}")
    
    return User(
        id=user_in_db.id,
        email=user_in_db.email,
        full_name=user_in_db.full_name,
        is_active=user_in_db.is_active,
        is_admin=user_in_db.is_admin,
        subscription_tier=user_in_db.subscription_tier,
        subscription_end_date=user_in_db.subscription_end_date,
        processing_minutes_used=user_in_db.processing_minutes_used,
        processing_minutes_limit=user_in_db.processing_minutes_limit,
        created_at=user_in_db.created_at,
        updated_at=user_in_db.updated_at
    )

async def update_user(user_id: str, user_update: UserUpdate) -> Optional[User]:
    users = await get_user_collection()
    user = await get_user_by_id(user_id)
    
    if not user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    # If password is being updated, hash it
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # Add updated_at timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    # Update user in database
    await users.update_one(
        {"id": user_id},
        {"$set": update_data}
    )
    
    # Return updated user
    return await get_user_by_id(user_id)

async def delete_user(user_id: str) -> bool:
    users = await get_user_collection()
    result = await users.delete_one({"id": user_id})
    return result.deleted_count > 0

async def get_all_users(skip: int = 0, limit: int = 100) -> List[User]:
    users = await get_user_collection()
    user_list = []
    
    cursor = users.find().skip(skip).limit(limit)
    async for user_data in cursor:
        user_in_db = UserInDB(**user_data)
        user = User(
            id=user_in_db.id,
            email=user_in_db.email,
            full_name=user_in_db.full_name,
            is_active=user_in_db.is_active,
            is_admin=user_in_db.is_admin,
            subscription_tier=user_in_db.subscription_tier,
            subscription_end_date=user_in_db.subscription_end_date,
            processing_minutes_used=user_in_db.processing_minutes_used,
            processing_minutes_limit=user_in_db.processing_minutes_limit,
            created_at=user_in_db.created_at,
            updated_at=user_in_db.updated_at
        )
        user_list.append(user)
    
    return user_list 