from models.customer import Customer
from sqlalchemy.orm import Session


class ClientController:

    def get_all(self, db: Session):
        return db.query(Customer).all()

    def get_by_id(self, db: Session, client_id: int):
        return db.query(Customer).filter(Customer.id == client_id).first()

    def create(self, db: Session, data: dict):
        client = Customer(**data)
        db.add(client)
        db.commit()
        db.refresh(client)
        return client

    def update(self, db: Session, client_id: int, data: dict):
        client = db.query(Customer).filter(Customer.id == client_id).first()
        if not client:
            return None

        for key, value in data.items():
            setattr(client, key, value)

        db.commit()
        db.refresh(client)
        return client

    def delete(self, db: Session, client_id: int):
        client = db.query(Customer).filter(Customer.id == client_id).first()
        if not client:
            return None
        db.delete(client)
        db.commit()
        return True
