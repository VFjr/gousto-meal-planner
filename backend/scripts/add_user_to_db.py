# run with uv run -m scripts.add_user_to_db username password email

import argparse
import asyncio
import os
from dotenv import load_dotenv

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.models import UserInDB

load_dotenv()

# Load environment variables
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

# Database URL
DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB}"

# Create an asynchronous engine
async_engine = create_async_engine(DATABASE_URL, echo=True)

# Create a session factory bound to the async engine
AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


async def add_user(username: str, password: str, email: str):
    # Create a new user instance
    hashed_password = get_password_hash(password)
    new_user = UserInDB(username=username, hashed_password=hashed_password, email=email)

    # Add the user to the database
    async with AsyncSessionLocal() as session:
        async with session.begin():
            session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        print(f"User {new_user.username} added with ID {new_user.id}")


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Add a new user to the database.")
    parser.add_argument("username", type=str, help="The username of the new user.")
    parser.add_argument("password", type=str, help="The password of the new user.")
    parser.add_argument("email", type=str, help="The email of the new user.")
    args = parser.parse_args()

    # Run the add_user function in an event loop
    asyncio.run(add_user(args.username, args.password, args.email))
