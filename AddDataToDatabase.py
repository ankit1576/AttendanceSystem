import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate("serviceAccountkey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendence1576-default-rtdb.firebaseio.com/"
})

ref=db.reference('Students')
data={
    "1":
        {
            "name":"Ankit Pandey",
            "Branch":"MCA",
            "Starting_year":2022,
            "total_attendence":7,
            "year":4,
            "last_attendence_time":"2024-03-11 12:24:35"
        },
    "2":
        {
            "name":"Narendra modi",
            "Branch":"Politics",
            "Starting_year":2022,
            "total_attendence":3,
            "year":4,
            "last_attendence_time":"2024-03-11 12:24:35"
        },
    "3":
        {
            "name":"Elon musk",
            "Branch":"SpaceX",
            "Starting_year":2022,
            "total_attendence":7,
            "year":4,
            "last_attendence_time":"2024-03-11 12:24:35"
        }

}

for key,value in data.items():
    ref.child(key).set(value)