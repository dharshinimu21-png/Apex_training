from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import conn, cursor


app = FastAPI()


# --------------------------------------------------
# STATIC FILES
# --------------------------------------------------

app.mount("/static", StaticFiles(directory="static"), name="static")


# --------------------------------------------------
# TEMPLATES
# --------------------------------------------------

templates = Jinja2Templates(directory="templates")


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="home.html"
    )


# --------------------------------------------------
# LOGIN PAGE
# --------------------------------------------------

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    login_type: str = Form(...)
):

    # --------------------------------------------------
    # ADMIN LOGIN
    # --------------------------------------------------

    if login_type == "admin":

        if username == "admin" and password == "admin123":

            return RedirectResponse(
                "/admin",
                status_code=303
            )

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": "Invalid Admin username or password"
            }
        )


    # --------------------------------------------------
    # USER LOGIN
    # --------------------------------------------------

    elif login_type == "user":

        cursor.execute(
            """
            SELECT account_no, customer_name, password, balance
            FROM account
            WHERE customer_name = %s
            AND password = %s
            """,
            (username, password)
        )

        user = cursor.fetchone()

        if user:

            return RedirectResponse(
                f"/user/{username}",
                status_code=303
            )

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": "Invalid User username or password"
            }
        )


# --------------------------------------------------
# ADMIN DASHBOARD
# --------------------------------------------------

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    section: str = "create",
    success: str = "",
    error: str = ""
):

    cursor.execute(
        """
        SELECT account_no, customer_name, password, balance
        FROM account
        """
    )

    accounts = cursor.fetchall()

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "accounts": accounts,
            "section": section,
            "success": success,
            "error": error
        }
    )

# --------------------------------------------------
# CREATE ACCOUNT
# --------------------------------------------------

@app.post("/create")
async def create_account(
    account_no: int = Form(...),
    customer_name: str = Form(...),
    password: str = Form(...),
    balance: float = Form(...)
):

    try:

        cursor.execute(
            """
            INSERT INTO account
            (account_no, customer_name, password, balance)
            VALUES (%s, %s, %s, %s)
            """,
            (
                account_no,
                customer_name,
                password,
                balance
            )
        )

        conn.commit()

        return RedirectResponse(
            "/admin?section=create&success=Account+created+successfully!",
            status_code=303
        )

    except Exception as e:

        conn.rollback()

        return HTMLResponse(
            f"""
            <h2>Error creating account</h2>
            <p>{e}</p>
            <a href="/admin">Back</a>
            """
        )


# --------------------------------------------------
# CHANGE PASSWORD
# --------------------------------------------------

@app.post("/change_password")
async def change_password(
    account_no: int = Form(...),
    old_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):

    try:

        # Check old password
        cursor.execute(
            """
            SELECT password
            FROM account
            WHERE account_no = %s
            """,
            (account_no,)
        )

        result = cursor.fetchone()

        if not result:

            return RedirectResponse(
                "/admin?section=change&error=Account+not+found",
                status_code=303
            )

        current_password = result[0]

        # Check old password
        if old_password != current_password:

            return RedirectResponse(
                "/admin?section=change&error=Old+password+is+incorrect",
                status_code=303
            )

        # Check new password and confirm password
        if new_password != confirm_password:

            return RedirectResponse(
                "/admin?section=change&error=New+password+and+confirm+password+do+not+match",
                status_code=303
            )

        # Update password
        cursor.execute(
            """
            UPDATE account
            SET password = %s
            WHERE account_no = %s
            """,
            (
                new_password,
                account_no
            )
        )

        conn.commit()

        return RedirectResponse(
            "/admin?section=change&success=Password+changed+successfully!",
            status_code=303
        )

    except Exception as e:

        conn.rollback()

        return HTMLResponse(
            f"""
            <h2>Error changing password</h2>
            <p>{e}</p>
            <a href="/admin?section=change">Back</a>
            """
        )
# --------------------------------------------------
# USER DASHBOARD
# --------------------------------------------------

@app.get("/user/{username}", response_class=HTMLResponse)
async def user_dashboard(
    request: Request,
    username: str,
    section: str = "dashboard",
    success: str = "",
    amount: str = "",
    current_balance: str = ""
):

    cursor.execute(
        """
        SELECT account_no, customer_name, password, balance
        FROM account
        WHERE customer_name = %s
        """,
        (username,)
    )

    user = cursor.fetchone()

    if not user:

        return HTMLResponse(
            """
            <h2>User not found</h2>
            <a href="/login">Login</a>
            """
        )

    return templates.TemplateResponse(
        request=request,
        name="user.html",
        context={
            "user": user,
            "section": section,
            "success": success,
            "amount": amount,
            "current_balance": current_balance
        }
    )


# --------------------------------------------------
# DEPOSIT
# --------------------------------------------------

@app.post("/deposit")
async def deposit(
    account_no: int = Form(...),
    amount: float = Form(...)
):

    try:

        if amount <= 0:

            return HTMLResponse(
                """
                <h2>Invalid Amount</h2>
                <p>Amount must be greater than 0.</p>
                <a href="/login">Back</a>
                """
            )

        # Get customer name
        customer_name = get_customer_name(account_no)

        if not customer_name:

            return HTMLResponse(
                """
                <h2>Account not found</h2>
                <a href="/login">Back</a>
                """
            )

        # Deposit
        cursor.execute(
            """
            UPDATE account
            SET balance = balance + %s
            WHERE account_no = %s
            """,
            (
                amount,
                account_no
            )
        )

        conn.commit()

        # Get updated balance
        cursor.execute(
            """
            SELECT balance
            FROM account
            WHERE account_no = %s
            """,
            (account_no,)
        )

        result = cursor.fetchone()

        current_balance = float(result[0])

        return RedirectResponse(
            f"/user/{customer_name}"
            f"?section=deposit"
            f"&success=Deposit+successful!"
            f"&amount={amount:.2f}"
            f"&current_balance={current_balance:.2f}",
            status_code=303
        )

    except Exception as e:

        conn.rollback()

        return HTMLResponse(
            f"""
            <h2>Deposit Error</h2>
            <p>{e}</p>
            <a href="/login">Back</a>
            """
        )


# --------------------------------------------------
# WITHDRAW
# --------------------------------------------------

@app.post("/withdraw")
async def withdraw(
    account_no: int = Form(...),
    amount: float = Form(...)
):

    try:

        if amount <= 0:

            return HTMLResponse(
                """
                <h2>Invalid Amount</h2>
                <p>Amount must be greater than 0.</p>
                <a href="/login">Back</a>
                """
            )

        # Get current balance
        cursor.execute(
            """
            SELECT balance
            FROM account
            WHERE account_no = %s
            """,
            (account_no,)
        )

        result = cursor.fetchone()

        if not result:

            return HTMLResponse(
                """
                <h2>Account not found</h2>
                <a href="/login">Back</a>
                """
            )

        balance = float(result[0])

        # Check balance
        if amount > balance:

            return HTMLResponse(
                """
                <h2>Insufficient Balance</h2>
                <p>You do not have enough balance.</p>
                <a href="/login">Back</a>
                """
            )

        # Get customer name
        customer_name = get_customer_name(account_no)

        # Withdraw
        cursor.execute(
            """
            UPDATE account
            SET balance = balance - %s
            WHERE account_no = %s
            """,
            (
                amount,
                account_no
            )
        )

        conn.commit()

        # Get updated balance
        cursor.execute(
            """
            SELECT balance
            FROM account
            WHERE account_no = %s
            """,
            (account_no,)
        )

        result = cursor.fetchone()

        current_balance = float(result[0])

        return RedirectResponse(
            f"/user/{customer_name}"
            f"?section=withdraw"
            f"&success=Withdrawal+successful!"
            f"&amount={amount:.2f}"
            f"&current_balance={current_balance:.2f}",
            status_code=303
        )

    except Exception as e:

        conn.rollback()

        return HTMLResponse(
            f"""
            <h2>Withdraw Error</h2>
            <p>{e}</p>
            <a href="/login">Back</a>
            """
        )


# --------------------------------------------------
# CHECK BALANCE
# --------------------------------------------------

@app.get("/balance/{username}", response_class=HTMLResponse)
async def check_balance(username: str):

    cursor.execute(
        """
        SELECT balance
        FROM account
        WHERE customer_name = %s
        """,
        (username,)
    )

    result = cursor.fetchone()

    if result:

        return HTMLResponse(
            f"""
            <html>

            <head>

                <title>Balance</title>

                <link rel="stylesheet"
                      href="/static/style.css">

            </head>


            <body>

                <div class="balance-box">

                    <h1>Account Balance</h1>

                    <h2>
                        ₹ {float(result[0]):.2f}
                    </h2>

                    <a href="/user/{username}">
                        Back to Dashboard
                    </a>

                </div>

            </body>

            </html>
            """
        )

    return HTMLResponse(
        """
        <h2>Account not found</h2>
        <a href="/login">Login</a>
        """
    )


# --------------------------------------------------
# EDIT ACCOUNT
# --------------------------------------------------

@app.post("/edit_account")
async def edit_account(
    account_no: int = Form(...),
    customer_name: str = Form(...)
):

    try:

        cursor.execute(
            """
            UPDATE account
            SET customer_name = %s
            WHERE account_no = %s
            """,
            (
                customer_name,
                account_no
            )
        )

        conn.commit()

        return RedirectResponse(
            "/admin?section=view&success=Account+updated+successfully!",
            status_code=303
        )

    except Exception as e:

        conn.rollback()

        return HTMLResponse(
            f"""
            <h2>Error updating account</h2>
            <p>{e}</p>
            <a href="/admin?section=view">Back</a>
            """
        )


# --------------------------------------------------
# DELETE ACCOUNT
# --------------------------------------------------

@app.post("/delete_account")
async def delete_account(
    account_no: int = Form(...)
):

    try:

        cursor.execute(
            """
            DELETE FROM account
            WHERE account_no = %s
            """,
            (account_no,)
        )

        conn.commit()

        return RedirectResponse(
            "/admin?section=view&success=Account+deleted+successfully!",
            status_code=303
        )

    except Exception as e:

        conn.rollback()

        return HTMLResponse(
            f"""
            <h2>Delete Error</h2>
            <p>{e}</p>
            <a href="/admin?section=view">Back</a>
            """
        )


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.get("/logout")
async def logout():

    return RedirectResponse(
        "/login",
        status_code=303
    )


# --------------------------------------------------
# GET CUSTOMER NAME
# --------------------------------------------------

def get_customer_name(account_no):

    cursor.execute(
        """
        SELECT customer_name
        FROM account
        WHERE account_no = %s
        """,
        (account_no,)
    )

    result = cursor.fetchone()

    if result:

        return result[0]

    return ""