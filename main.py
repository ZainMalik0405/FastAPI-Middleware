from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import time

USERNAME = "admin"
PASSWORD = "securepass"
TOKEN = "expensetoken"
isLoggedIn = False

app = FastAPI()

class LoginModel(BaseModel):
    username: str
    password: str

@app.middleware("http")
async def authenticator(request: Request, call_next):
    if request.url.path in ["/", "/login", "/logout", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    token = request.headers.get("x-token")
    if token == TOKEN and isLoggedIn:
        return await call_next(request)
    return JSONResponse(status_code=401, content={"error": "Not Authorized"})

@app.middleware("http")
async def logger(request: Request, call_next):
    start = time.time()
    print("Request URL Path =", request.url.path)
    print("Request Method =", request.method)
    response = await call_next(request)
    end = time.time()
    print("Time Taken =", round((end - start) * 1000, 2), "ms")
    return response

@app.post("/login")
def login(data: LoginModel):
    if data.username == USERNAME and data.password == PASSWORD:
        global isLoggedIn
        isLoggedIn = True
        return {"message": "Login Success", "token": TOKEN}
    return JSONResponse(status_code=401, content={"error": "Invalid Credentials"})

@app.post("/logout")
def logout():
    global isLoggedIn
    isLoggedIn = False
    return {"message": "Logout Success"}

class Expense(BaseModel):
    id: int
    title: str
    amount: float
    category: str

expenses: List[Expense] = []

@app.get("/")
def home():
    return {"message": "Welcome to Expense Tracker"}

@app.get("/expenses")
def get_all_expenses():
    return expenses

@app.get("/expenses/{expense_id}")
def get_expense(expense_id: int):
    for e in expenses:
        if e.id == expense_id:
            return e
    return {"error": "Expense not found"}

@app.post("/expenses")
def add_expense(expense: Expense):
    for e in expenses:
        if e.id == expense.id:
            return {"error": "ID already exists"}
    expenses.append(expense)
    return {"message": "Expense added"}

@app.put("/expenses/{expense_id}")
def update_expense(expense_id: int, expense: Expense):
    for i, e in enumerate(expenses):
        if e.id == expense_id:
            expenses[i] = expense
            return {"message": "Expense updated"}
    return {"error": "Expense not found"}

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    for i, e in enumerate(expenses):
        if e.id == expense_id:
            expenses.pop(i)
            return {"message": "Expense deleted"}
    return {"error": "Expense not found"}

@app.delete("/expenses")
def delete_all_expenses():
    if not expenses:
        return {"error": "No expenses to delete"}
    expenses.clear()
    return {"message": "All expenses deleted"}
