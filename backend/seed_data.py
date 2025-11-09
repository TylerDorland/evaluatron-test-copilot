"""
Seed database with initial data for testing
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.models import Base, Company, User, Topic
from app.core.security import get_password_hash


def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)


def seed_data():
    """Seed initial data"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Company).first():
            print("Database already seeded!")
            return
        
        # Create companies
        companies = [
            Company(name="Acme Corp", is_active=True),
            Company(name="TechStart Inc", is_active=True),
            Company(name="Global Solutions", is_active=True),
        ]
        
        for company in companies:
            db.add(company)
        
        db.commit()
        
        # Create users
        users = [
            User(
                email="admin@acme.com",
                hashed_password=get_password_hash("password123"),
                full_name="Admin User",
                company_id=companies[0].id,
                is_superuser=True,
                is_active=True
            ),
            User(
                email="user1@acme.com",
                hashed_password=get_password_hash("password123"),
                full_name="John Doe",
                company_id=companies[0].id,
                is_active=True
            ),
            User(
                email="user2@techstart.com",
                hashed_password=get_password_hash("password123"),
                full_name="Jane Smith",
                company_id=companies[1].id,
                is_active=True
            ),
            User(
                email="user3@global.com",
                hashed_password=get_password_hash("password123"),
                full_name="Bob Johnson",
                company_id=companies[2].id,
                is_active=True
            ),
        ]
        
        for user in users:
            db.add(user)
        
        db.commit()
        
        # Create topics
        topics = [
            Topic(
                name="Customer Support",
                description="Customer support related queries",
                company_id=companies[0].id
            ),
            Topic(
                name="Product Development",
                description="Product and feature questions",
                company_id=companies[0].id
            ),
            Topic(
                name="Marketing",
                description="Marketing and content generation",
                company_id=companies[1].id
            ),
            Topic(
                name="Research",
                description="Research and analysis topics",
                company_id=companies[2].id
            ),
        ]
        
        for topic in topics:
            db.add(topic)
        
        db.commit()
        
        print("✅ Database seeded successfully!")
        print("\nTest Credentials:")
        print("  Admin: admin@acme.com / password123")
        print("  User1: user1@acme.com / password123")
        print("  User2: user2@techstart.com / password123")
        print("  User3: user3@global.com / password123")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Creating tables...")
    create_tables()
    print("Seeding data...")
    seed_data()
