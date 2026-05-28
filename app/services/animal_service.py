from sqlalchemy import String, func, or_, select
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.schemas.animal import AnimalCreate, AnimalUpdate


class AnimalService:
    @staticmethod
    def get_active_animal(db: Session, animal_id: int) -> Animal | None:
        return db.scalar(
            select(Animal).where(
                Animal.id == animal_id,
                Animal.is_active.is_(True),
            )
        )

    @staticmethod
    def animal_code_exists(db: Session, animal_code: str, exclude_id: int | None = None) -> bool:
        query = select(Animal.id).where(Animal.animal_code == animal_code)
        if exclude_id is not None:
            query = query.where(Animal.id != exclude_id)
        return db.scalar(query) is not None

    @staticmethod
    def tag_number_exists(db: Session, tag_number: str, exclude_id: int | None = None) -> bool:
        query = select(Animal.id).where(Animal.tag_number == tag_number)
        if exclude_id is not None:
            query = query.where(Animal.id != exclude_id)
        return db.scalar(query) is not None

    @staticmethod
    def validate_parent_ids(db: Session, mother_id: int | None, father_id: int | None, animal_id: int | None = None) -> str | None:
        if mother_id is not None and father_id is not None and mother_id == father_id:
            return "Mother and father cannot reference the same animal."

        for parent_id, label in ((mother_id, "Mother"), (father_id, "Father")):
            if parent_id is None:
                continue
            if animal_id is not None and parent_id == animal_id:
                return f"{label} cannot reference the same animal."

            parent = db.get(Animal, parent_id)
            if parent is None:
                return f"{label} animal not found."

        return None

    @staticmethod
    def create_animal(db: Session, payload: AnimalCreate) -> Animal:
        animal = Animal(**payload.model_dump(mode="python"))
        db.add(animal)
        db.commit()
        db.refresh(animal)
        return animal

    @staticmethod
    def update_animal(db: Session, animal: Animal, payload: AnimalUpdate) -> Animal:
        updates = payload.model_dump(mode="python", exclude_unset=True)
        for field, value in updates.items():
            setattr(animal, field, value)

        db.commit()
        db.refresh(animal)
        return animal

    @staticmethod
    def soft_delete_animal(db: Session, animal: Animal) -> Animal:
        animal.is_active = False
        db.commit()
        db.refresh(animal)
        return animal

    @staticmethod
    def list_animals(
        db: Session,
        *,
        page: int,
        limit: int,
        search: str | None,
        animal_type: str | None,
        current_status: str | None,
        breed: str | None,
    ) -> tuple[list[Animal], int]:
        filters = [Animal.is_active.is_(True)]

        if search:
            search_term = f"%{search.strip()}%"
            filters.append(
                or_(
                    Animal.animal_code.ilike(search_term),
                    Animal.tag_number.ilike(search_term),
                    Animal.name.ilike(search_term),
                    Animal.breed.ilike(search_term),
                )
            )
        if animal_type:
            filters.append(Animal.animal_type == animal_type)
        if current_status:
            filters.append(Animal.current_status == current_status)
        if breed:
            filters.append(func.lower(Animal.breed.cast(String)) == breed.strip().lower())

        base_query = select(Animal).where(*filters)
        total = db.scalar(select(func.count()).select_from(base_query.subquery())) or 0

        animals = db.scalars(
            base_query
            .order_by(Animal.created_at.desc(), Animal.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        ).all()
        return animals, total
