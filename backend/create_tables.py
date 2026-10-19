from database import Base, engine
from models import User, Document, ChatHistory


print("Creating MySQL tables...")

Base.metadata.create_all(bind=engine)

print("MySQL tables created successfully!")
print("Tables:")
print("- users")
print("- documents")
print("- chat_history")