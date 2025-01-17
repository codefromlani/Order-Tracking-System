from fastapi import FastAPI
from database import Base, engine
from routers import vendor_router, product_router, client_router, order_router, invoice_router, expense_router, shipping_router, reporting_router
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request


# Drop all tables (use only in development!)
# Base.metadata.drop_all(bind=engine)

# Recreate the tables
Base.metadata.create_all(bind=engine) 


app = FastAPI(
    title="Order Tracking System"
)

app.include_router(vendor_router.router)
app.include_router(product_router.router)
app.include_router(client_router.router)
app.include_router(order_router.router)
app.include_router(invoice_router.router)
app.include_router(expense_router.router)
app.include_router(shipping_router.router)
app.include_router(reporting_router.router)


templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})