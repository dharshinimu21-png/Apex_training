from fastapi import FastAPI
from pydantic import BaseModel
from database import SessionLocal, engine, Base
from model import Student

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student CRUD API")

class StudentSchema(BaseModel):
    name: str
    age: int
    department: str

@app.get("/")
def home():
    return {"message": "Welcome to Student CRUD API"}

# CREATE
@app.post("/students")
def create_student(student: StudentSchema):
    db = SessionLocal()

    new_student = Student(
        name=student.name,
        age=student.age,
        department=student.department
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    db.close()

    return {"message": "Student Created Successfully"}

# READ ALL
@app.get("/students")
def get_students():
    db = SessionLocal()
    students = db.query(Student).all()
    db.close()
    return students

# READ BY ID
@app.get("/students/{student_id}")
def get_student(student_id: int):
    db = SessionLocal()

    student = db.query(Student).filter(Student.id == student_id).first()

    db.close()

    if student:
        return student

    return {"message": "Student Not Found"}

# UPDATE
@app.put("/students/{student_id}")
def update_student(student_id: int, data: StudentSchema):
    db = SessionLocal()

    student = db.query(Student).filter(Student.id == student_id).first()

    if student is None:
        db.close()
        return {"message": "Student Not Found"}

    student.name = data.name
    student.age = data.age
    student.department = data.department

    db.commit()
    db.refresh(student)
    db.close()

    return {"message": "Student Updated Successfully"}

# DELETE
@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    db = SessionLocal()

    student = db.query(Student).filter(Student.id == student_id).first()

    if student is None:
        db.close()
        return {"message": "Student Not Found"}

    db.delete(student)
    db.commit()
    db.close()

    return {"message": "Student Deleted Successfully"}