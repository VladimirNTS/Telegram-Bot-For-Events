# api/dependencies/admin_permissions.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Dict, Any, Callable, Optional
from app.config import settings
from app.api_router.schemas import AdminTokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class PermissionChecker:
    def __init__(self, required_permissions: Optional[Dict[str, str]] = None):
        """
        required_permissions = {
            "events": "editor",  # требует права editor на events
            "users": "viewer"    # требует права viewer на users
        }
        """
        self.required_permissions = required_permissions or {}
    
    async def __call__(
        self,
        token: str = Depends(oauth2_scheme)
    ):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        forbidden_exception = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )
        
        try:
            # Декодируем JWT
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            
            # Проверяем, что это админ
            if payload.get("type") != "admin":
                raise credentials_exception
            
            login = payload.get("sub")
            super_user = payload.get("super_user", False)
            permissions = payload.get("permissions", {})
            
            token_data = AdminTokenData(
                login=login,
                super_user=super_user,
                permissions=permissions
            )
            
            # Суперпользователь имеет все права
            if super_user:
                return token_data
            
            # Проверяем каждое требуемое право
            for resource, required_level in self.required_permissions.items():
                user_level = permissions.get(resource, "forbidden")
                
                if not self._check_permission_level(user_level, required_level):
                    raise forbidden_exception
            
            return token_data
            
        except JWTError:
            raise credentials_exception
    
    def _check_permission_level(self, user_level: str, required_level: str) -> bool:
        """Проверка уровня доступа"""
        levels = {"forbidden": 0, "viewer": 1, "editor": 2}
        return levels.get(user_level, 0) >= levels.get(required_level, 0)

# Фабрики для разных проверок
def require_any_admin():
    """Просто проверка что это админ (без прав)"""
    return PermissionChecker()

def require_editor(resource: str):
    """Требует права редактора на конкретный ресурс"""
    return PermissionChecker({resource: "editor"})

def require_viewer(resource: str):
    """Требует права просмотра на конкретный ресурс"""
    return PermissionChecker({resource: "viewer"})

def require_multiple(permissions: Dict[str, str]):
    """Требует несколько прав"""
    return PermissionChecker(permissions)

# Удобные пресеты для каждого раздела
can_edit_events = require_editor("events")
can_view_events = require_viewer("events")

can_edit_registers = require_editor("registers")
can_view_registers = require_viewer("registers")

can_edit_partners = require_editor("partners_apply")
can_view_partners = require_viewer("partners_apply")

can_edit_exhibitions = require_editor("exhibitions_apply")
can_view_exhibitions = require_viewer("exhibitions_apply")

can_edit_users = require_editor("users")
can_view_users = require_viewer("users")

can_edit_queue = require_editor("queue")
can_view_queue = require_viewer("queue")

can_edit_payments = require_editor("payments")
can_view_payments = require_viewer("payments")

can_edit_documents = require_editor("documents")
can_view_documents = require_viewer("documents")

can_edit_reviews = require_editor("reviews")
can_view_reviews = require_viewer("reviews")

can_edit_notifications = require_editor("notifications")
can_view_notifications = require_viewer("notifications")

can_edit_support = require_editor("support")
can_view_support = require_viewer("support")

can_edit_qr = require_editor("qr_codes")
can_view_qr = require_viewer("qr_codes")
