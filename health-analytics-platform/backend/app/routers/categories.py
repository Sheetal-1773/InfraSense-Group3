from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..models.database import get_db
from ..models.models import Category
from ..schemas.schemas import CategoryResponse, CategoryWithHealth
from ..services.health_service import calculate_category_health

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=List[CategoryWithHealth])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    result = []
    for cat in categories:
        health = calculate_category_health(db, cat.id)
        cat_dict = {
            "id": cat.id,
            "name": cat.name,
            "type": cat.type,
            "description": cat.description,
            "created_at": cat.created_at,
            "updated_at": cat.updated_at,
            "health_score": health.get("score"),
            "health_status": health.get("status"),
            "total_components": health.get("totalComponents", 0),
            "healthy_components": health.get("healthyComponents", 0),
            "warning_components": health.get("warningComponents", 0),
            "critical_components": health.get("criticalComponents", 0),
            "unknown_components": health.get("unknownComponents", 0),
        }
        result.append(cat_dict)
    return result


@router.get("/{category_id}", response_model=CategoryWithHealth)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return {"error": "Category not found"}
    
    health = calculate_category_health(db, category_id)
    return {
        "id": category.id,
        "name": category.name,
        "type": category.type,
        "description": category.description,
        "created_at": category.created_at,
        "updated_at": category.updated_at,
        "health_score": health.get("score"),
        "health_status": health.get("status"),
        "total_components": health.get("totalComponents", 0),
        "healthy_components": health.get("healthyComponents", 0),
        "warning_components": health.get("warningComponents", 0),
        "critical_components": health.get("criticalComponents", 0),
        "unknown_components": health.get("unknownComponents", 0),
    }