import mysql.connector

# MySQL Connection
conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="0909",
    database="bank"
)

cursor = conn.cursor()
print("Connected Successfully")

while True:
    print("\n===== BANK MANAGEMENT SYSTEM =====")
    print("1. Create Account")
    print("2. Display Accounts")
    print("3. Deposit Money")
    print("4. Withdraw Money")
    print("5. Check Balance")
    print("6. Delete Account")
    print("7. Exit")

    choice = input("Enter your choice: ")

    # Create Account
    if choice == "1": 
        name = input("Enter customer name: ") 
        balance = float(input("Enter initial balance: ")) 
 
        sql = "INSERT INTO account (customer_name, balance) VALUES (%s, %s)" 
        cursor.execute(sql, (name, balance)) 
        conn.commit() 
 
        print("Account created successfully!") 
        print("Account Number:", cursor.lastrowid)    
    # Display Accounts
    elif choice == "2":
        cursor.execute("SELECT * FROM account")
        records = cursor.fetchall()

        for row in records:
            print(row)

    # Deposit
    elif choice == "3":
        acc_no = int(input("Enter account number: "))
        amount = float(input("Enter deposit amount: "))

        sql = "UPDATE account SET balance = balance + %s WHERE account_no = %s"
        cursor.execute(sql, (amount, acc_no))
        conn.commit()

        print("Amount deposited successfully!")

    # Withdraw
    elif choice == "4":
        acc_no = int(input("Enter account number: "))
        amount = float(input("Enter withdrawal amount: "))

        sql = "UPDATE account SET balance = balance - %s WHERE account_no = %s"
        cursor.execute(sql, (amount, acc_no))
        conn.commit()

        print("Amount withdrawn successfully!")

    # Check Balance
    elif choice == "5":
        acc_no = int(input("Enter account number: "))

        cursor.execute(
            "SELECT customer_name, balance FROM account WHERE account_no = %s"
            (acc_no,)
        )

        record = cursor.fetchone()

        if record:
            print("Customer:", record[0])
            print("Balance:", record[1])
        else:
            print("Account not found!")

    # Delete Account
    elif choice == "6":
        acc_no = int(input("Enter account number to delete: "))

        cursor.execute(
            sql = "DELETE FROM account WHERE account_no = %s"
            (acc_no,)
        )
        conn.commit()

        if cursor.rowcount > 0:
            print("Account deleted successfully!")
        else:
            print("Account not found!")

    # Exit
    elif choice == "7":
        print("Thank you!")
        break

    else:
        print("Invalid choice!")

cursor.close()
conn.close()