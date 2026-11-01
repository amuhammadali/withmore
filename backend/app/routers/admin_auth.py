import re
import secrets
from datetime import timedelta

from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .. import botstate
from ..core import audit, fmt_dt, process_upload
from ..db import get_db
from ..models import PERMISSIONS, AdminAccount, now
from ..security import (COOKIE, check_password_policy, current_admin, hash_password, make_session_cookie,
                        rate_limit_check, rate_limit_fail, rate_limit_reset, read_session,
                        require_owner, set_cookie, verify_password)

router = APIRouter(prefix="/api/admin", tags=["admin-auth"])


def admin_out(a: AdminAccount) -> dict:
    return {"id": a.id, "full_name": a.full_name, "tg_username": a.tg_username, "login": a.login,
            "role": a.role, "permissions": PERMISSIONS if a.role == "owner" else (a.permissions or []),
            "avatar": a.avatar, "accepts_orders": a.accepts_orders, "blocked": a.blocked,
            "last_login": fmt_dt(a.last_login), "telegram_linked": a.tg_chat_id is not None}


class LoginIn(BaseModel):
    login: str
    password: str


@router.post("/login")
def login(body: LoginIn, request: Request, response: Response, db: Session = Depends(get_db)):
    key = f"{request.client.host if request.client else '?'}|{body.login.lower()}"
    rate_limit_check(key)
    admin = db.query(AdminAccount).filter(AdminAccount.login == body.login.strip().lower()).first()
    if not admin or admin.blocked or not verify_password(body.password, admin.password_hash):
        rate_limit_fail(key)
        raise HTTPException(401, "Login yoki parol noto'g'ri")
    rate_limit_reset(key)
    admin.last_login = now()
    audit(db, admin, "login", "admin", admin.id)
    db.commit()
    token, csrf = make_session_cookie(admin)
    set_cookie(response, token, request=request)
    return {"admin": admin_out(admin), "csrf": csrf}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE, path="/")
    return {"ok": True}


@router.get("/me")
def me(request: Request, admin: AdminAccount = Depends(current_admin)):
    data = read_session(request.cookies.get(COOKIE))
    return {"admin": admin_out(admin), "csrf": data["c"]}


class PasswordIn(BaseModel):
    old_password: str
    new_password: str


@router.post("/me/password")
def change_password(body: PasswordIn, response: Response, admin: AdminAccount = Depends(current_admin),
                    db: Session = Depends(get_db)):
    if not verify_password(body.old_password, admin.password_hash):
        raise HTTPException(400, "Eski parol noto'g'ri")
    check_password_policy(body.new_password)
    admin.password_hash = hash_password(body.new_password)
    admin.session_version += 1
    audit(db, admin, "password_change", "admin", admin.id)
    db.commit()
    token, csrf = make_session_cookie(admin)
    set_cookie(response, token, request=request)
    return {"csrf": csrf}


@router.post("/me/telegram-link")
async def telegram_link(request: Request, admin: AdminAccount = Depends(current_admin), db: Session = Depends(get_db)):
    admin.link_token = secrets.token_urlsafe(12)
    admin.link_token_expires = now() + timedelta(minutes=15)
    db.commit()
    from .. import bot as botmod
    bot = botstate.bot_username or await botmod.ensure_bot_started(request.app)
    return {
        "token": admin.link_token,
        "bot_username": bot,
        "url": f"https://t.me/{bot}?start=link_{admin.link_token}" if bot else None,
        "miniapp_https_url": botmod.app_url() if botmod.app_url().startswith("https://") else None,
    }


# ---------------- team (owner only) ----------------
class TeamIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    tg_username: str = ""
    login: str = Field(min_length=3, max_length=64)
    password: str | None = None
    role: str = "admin"
    permissions: list[str] = []
    accepts_orders: bool = False


def _clean(body: TeamIn):
    if body.role not in ("owner", "admin"):
        raise HTTPException(422, "Rol noto'g'ri")
    if any(p not in PERMISSIONS for p in body.permissions):
        raise HTTPException(422, "Ruxsat noto'g'ri")
    if not re.fullmatch(r"[a-z0-9_.-]+", body.login.strip().lower()):
        raise HTTPException(422, "Login faqat lotin harf, raqam va _ . - dan iborat bo'lsin")
    return body.tg_username.strip().lstrip("@")


@router.get("/team")
def team_list(owner: AdminAccount = Depends(require_owner), db: Session = Depends(get_db)):
    return [admin_out(a) for a in db.query(AdminAccount).order_by(AdminAccount.id).all()]


@router.post("/team", status_code=201)
def team_add(body: TeamIn, owner: AdminAccount = Depends(require_owner), db: Session = Depends(get_db)):
    uname = _clean(body)
    check_password_policy(body.password or "")
    login_ = body.login.strip().lower()
    if db.query(AdminAccount).filter_by(login=login_).first():
        raise HTTPException(409, "Bunday login mavjud")
    a = AdminAccount(full_name=body.full_name.strip(), tg_username=uname, login=login_,
                     password_hash=hash_password(body.password), role=body.role,
                     permissions=body.permissions, accepts_orders=body.accepts_orders)
    db.add(a)
    db.flush()
    audit(db, owner, "team_add", "admin", a.id, f"{a.login} role={a.role} perms={a.permissions}")
    db.commit()
    return admin_out(a)


@router.patch("/team/{aid}")
def team_edit(aid: int, body: TeamIn, owner: AdminAccount = Depends(require_owner),
              db: Session = Depends(get_db)):
    a = db.get(AdminAccount, aid) or _404()
    uname = _clean(body)
    if a.id == owner.id and body.role != "owner":
        raise HTTPException(400, "O'z rolingizni o'zgartira olmaysiz")
    other = db.query(AdminAccount).filter(AdminAccount.login == body.login.strip().lower(),
                                          AdminAccount.id != aid).first()
    if other:
        raise HTTPException(409, "Bunday login mavjud")
    changed_access = (a.role != body.role or set(a.permissions or []) != set(body.permissions))
    a.full_name, a.tg_username, a.login = body.full_name.strip(), uname, body.login.strip().lower()
    a.role, a.permissions, a.accepts_orders = body.role, body.permissions, body.accepts_orders
    if changed_access:
        a.session_version += 1
    audit(db, owner, "team_edit", "admin", a.id, f"role={a.role} perms={a.permissions} accepts={a.accepts_orders}")
    db.commit()
    return admin_out(a)


def _404():
    raise HTTPException(404, "Topilmadi")


@router.post("/team/{aid}/reset-password")
def team_reset(aid: int, body: dict, owner: AdminAccount = Depends(require_owner), db: Session = Depends(get_db)):
    a = db.get(AdminAccount, aid) or _404()
    pw = body.get("password", "")
    check_password_policy(pw)
    a.password_hash = hash_password(pw)
    a.session_version += 1
    audit(db, owner, "team_reset_password", "admin", a.id)
    db.commit()
    return {"ok": True}


@router.post("/team/{aid}/block")
def team_block(aid: int, owner: AdminAccount = Depends(require_owner), db: Session = Depends(get_db)):
    a = db.get(AdminAccount, aid) or _404()
    if a.id == owner.id:
        raise HTTPException(400, "O'zingizni bloklab bo'lmaydi")
    a.blocked = True
    a.session_version += 1
    audit(db, owner, "team_block", "admin", a.id)
    db.commit()
    return admin_out(a)


@router.post("/team/{aid}/unblock")
def team_unblock(aid: int, owner: AdminAccount = Depends(require_owner), db: Session = Depends(get_db)):
    a = db.get(AdminAccount, aid) or _404()
    a.blocked = False
    audit(db, owner, "team_unblock", "admin", a.id)
    db.commit()
    return admin_out(a)


@router.post("/team/{aid}/avatar")
async def team_avatar(aid: int, file: UploadFile = File(...), owner: AdminAccount = Depends(require_owner),
                      db: Session = Depends(get_db)):
    a = db.get(AdminAccount, aid) or _404()
    up = await process_upload(file, db, owner.id, subdir="avatars", max_side=400)
    a.avatar = up.path
    audit(db, owner, "team_avatar", "admin", a.id)
    db.commit()
    return admin_out(a)
