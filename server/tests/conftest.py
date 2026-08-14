import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from app.main import app
from app.database import get_session
import fakeredis
from app.models import User, UserCreate, Role
from app.services import auth_service
from sqlalchemy.pool import StaticPool

# Setup SQLite In-Memory Database
# Hanya di RAM dan akan hancur ketika testing selesai
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

# fixture = prepare kebutuhan sebelum test jalan dan membersihkan setelah test selesai sehingga independen testingnya
# Buat database beserta tabel SQLite
@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session
        
    SQLModel.metadata.drop_all(engine)

# Membuat client untuk testing (nembak API)
@pytest.fixture(name="client")
def client_fixture(session: Session):
    # Membajak (Override) koneksi database aplikasi
    # Saat aplikasi memanggil get_session(), kita beri session SQLite bohongan ini
    def get_session_override():
        return session
        
    app.dependency_overrides[get_session] = get_session_override
    
    # Hasilkan robot penguji (TestClient)
    with TestClient(app) as client:
        yield client
        
    app.dependency_overrides.clear()

# Membuat akun user testing beserta JWT tokennya
@pytest.fixture(name="normal_user")
def normal_user_fixture(session: Session):
    user_data = UserCreate(name="Budi Test", email="budi@test.com", password="password123")
    user = auth_service.register_new_user(session, user_data)
    return user

@pytest.fixture(autouse=True)
def mock_redis(mocker):
    # Gunakan fakeredis agar tes tidak membutuhkan server Redis betulan
    fake_redis = fakeredis.FakeRedis(decode_responses=True)
    mocker.patch("app.services.url_service.get_redis_client", return_value=fake_redis)
    yield fake_redis

@pytest.fixture(name="auth_headers")
def auth_headers_fixture(normal_user: User):
    from app.utils.jwt import create_access_token
    token = create_access_token({"sub": str(normal_user.id), "role": normal_user.role.value})
    return {"Authorization": f"Bearer {token}"}

# Membuat akun admin testing beserta JWT tokennya
@pytest.fixture(name="admin_user")
def admin_user_fixture(session: Session):
    user_data = UserCreate(name="Admin Test", email="admin@test.com", password="password123")
    user = auth_service.register_new_user(session, user_data)
    user.role = Role.admin
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture(name="admin_headers")
def admin_headers_fixture(admin_user: User):
    from app.utils.jwt import create_access_token
    token = create_access_token({"sub": str(admin_user.id), "role": admin_user.role.value})
    return {"Authorization": f"Bearer {token}"}
