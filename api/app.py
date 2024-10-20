# app.py
import uuid
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from models import session
from seal import cipher
from utils import hash_password, verify_password, create_access_token
from prometheus_fastapi_instrumentator import Instrumentator

# Инициализация FastAPI и шаблонов
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Инструментатор для Prometheus
@app.on_event("startup")
async def startup():
    Instrumentator().instrument(app).expose(app)

# Получение текущего пользователя через JWT-токен
def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token.split("Bearer ")[-1], Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# Главная страница
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Регистрация пользователя
@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(request: Request, username: str = Form(...), password: str = Form(...), full_name: str = Form(...), email: str = Form(...)):
    hashed_password = hash_password(password)
    try:
        session.execute(
            "INSERT INTO users (username, hashed_password, full_name, email, role) VALUES (%s, %s, %s, %s, 'user')",
            (username, hashed_password, full_name, email)
        )
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        return templates.TemplateResponse("register.html", {"request": request, "error": "User already exists"})

# Вход в систему
@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user_row = session.execute("SELECT * FROM users WHERE username=%s", (username,)).one()
    if user_row and verify_password(password, user_row.hashed_password):
        access_token = create_access_token(data={"sub": user_row.username}, expires_delta=timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES))
        response = RedirectResponse(url="/cabinet", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
        return response
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})

# Личный кабинет пользователя
@app.get("/cabinet", response_class=HTMLResponse)
async def cabinet(request: Request, current_user: str = Depends(get_current_user)):
    rows = session.execute("SELECT id, value, type FROM secrets WHERE owner=%s", (current_user,))
    secrets = [{"id": row.id, "value": cipher.decrypt(row.value.encode()).decode(), "type": row.type} for row in rows]
    return templates.TemplateResponse("cabinet.html", {"request": request, "secrets": secrets, "username": current_user})

# Добавление секрета
@app.get("/cabinet/add_secret", response_class=HTMLResponse)
async def add_secret_form(request: Request, current_user: str = Depends(get_current_user)):
    return templates.TemplateResponse("add_secret.html", {"request": request})

@app.post("/cabinet/add_secret")
async def add_secret(request: Request, value: str = Form(...), type: str = Form(...), namespace: str = Form(...), current_user: str = Depends(get_current_user)):
    secret_id = str(uuid.uuid4())
    encrypted_value = cipher.encrypt(value.encode()).decode()
    session.execute("""
        INSERT INTO secrets (id, value, type, owner, namespace) VALUES (%s, %s, %s, %s, %s)
    """, (secret_id, encrypted_value, type, current_user, namespace))
    return RedirectResponse(url="/cabinet", status_code=status.HTTP_303_SEE_OTHER)

# Обновление секрета с версионированием
@app.post("/cabinet/update_secret")
async def update_secret(request: Request, secret_id: str = Form(...), value: str = Form(...), type: str = Form(...), current_user: str = Depends(get_current_user)):
    old_secret = session.execute("SELECT * FROM secrets WHERE id=%s AND owner=%s", (secret_id, current_user)).one()
    
    if old_secret:
        session.execute("""
            INSERT INTO secret_versions (version_id, secret_id, value, type, owner, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (str(uuid.uuid4()), secret_id, old_secret.value, old_secret.type, current_user, datetime.utcnow()))
    
        encrypted_value = cipher.encrypt(value.encode()).decode()
        session.execute("""
            UPDATE secrets SET value=%s, type=%s WHERE id=%s AND owner=%s
        """, (encrypted_value, type, secret_id, current_user))

    return RedirectResponse(url="/cabinet", status_code=status.HTTP_303_SEE_OTHER)

# Добавление динамического секрета с TTL
@app.post("/cabinet/add_dynamic_secret")
async def add_dynamic_secret(request: Request, value: str = Form(...), type: str = Form(...), ttl_minutes: int = Form(...), current_user: str = Depends(get_current_user)):
    secret_id = str(uuid.uuid4())
    encrypted_value = cipher.encrypt(value.encode()).decode()
    ttl = datetime.utcnow() + timedelta(minutes=ttl_minutes)
    session.execute("""
        INSERT INTO dynamic_secrets (id, value, type, owner, ttl) VALUES (%s, %s, %s, %s, %s)
    """, (secret_id, encrypted_value, type, current_user, ttl))
    return RedirectResponse(url="/cabinet", status_code=status.HTTP_303_SEE_OTHER)

# Очистка динамических секретов по истечению TTL
@app.get("/cleanup_expired_secrets")
async def cleanup_expired_secrets():
    session.execute("""
        DELETE FROM dynamic_secrets WHERE ttl < toTimestamp(now())
    """)
    return {"message": "Expired secrets deleted"}

# Добавление неймспейса
@app.post("/cabinet/add_namespace")
async def add_namespace(request: Request, namespace_name: str = Form(...), current_user: str = Depends(get_current_user)):
    namespace_id = str(uuid.uuid4())
    session.execute("""
        INSERT INTO namespaces (namespace_id, namespace_name, owner) VALUES (%s, %s, %s)
    """, (namespace_id, namespace_name, current_user))
    return RedirectResponse(url="/cabinet", status_code=status.HTTP_303_SEE_OTHER)

# Удаление секрета
@app.post("/cabinet/delete_secret")
async def delete_secret(request: Request, secret_id: str = Form(...), current_user: str = Depends(get_current_user)):
    session.execute("DELETE FROM secrets WHERE id=%s AND owner=%s", (secret_id, current_user))
    return RedirectResponse(url="/cabinet", status_code=status.HTTP_303_SEE_OTHER)
