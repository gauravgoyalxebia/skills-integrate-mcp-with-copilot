"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School, and enables organizers
to create and manage events.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities and managing events")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Enum for event status
class EventStatus(str, Enum):
    FRESH = "FRESH"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

# Pydantic models for request bodies
class EventCreate(BaseModel):
    title: str
    category: str
    date: str
    time: str
    location: str
    description: str
    organizer_name: str
    organizer_email: str
    capacity: int
    permission_document: str = None  # File path or URL
    event_image: str = None  # File path or URL

class EventApproval(BaseModel):
    status: EventStatus
    notes: str = ""

# In-memory approved organizers database
approved_organizers = {
    "john.smith@mergington.edu": {"name": "John Smith", "approved_at": "2026-06-01"},
    "maria.garcia@mergington.edu": {"name": "Maria Garcia", "approved_at": "2026-06-05"}
}

# In-memory events database
events = {}

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}


# Event Management Endpoints

@app.post("/events")
def create_event(event: EventCreate):
    """Create a new event. Requires organizer to be approved."""
    # Check if organizer is approved
    if event.organizer_email not in approved_organizers:
        raise HTTPException(
            status_code=403,
            detail="Organizer is not approved to create events"
        )
    
    # Generate event ID
    event_id = len(events) + 1
    
    # Create event with FRESH status
    events[event_id] = {
        "id": event_id,
        "title": event.title,
        "category": event.category,
        "date": event.date,
        "time": event.time,
        "location": event.location,
        "description": event.description,
        "organizer_name": event.organizer_name,
        "organizer_email": event.organizer_email,
        "capacity": event.capacity,
        "permission_document": event.permission_document,
        "event_image": event.event_image,
        "status": EventStatus.FRESH,
        "created_at": datetime.now().isoformat(),
        "attendees": []
    }
    
    return {
        "message": "Event created successfully",
        "event_id": event_id,
        "status": EventStatus.FRESH
    }


@app.get("/events/{event_id}")
def get_event_details(event_id: int):
    """Get details of a specific event"""
    if event_id not in events:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return events[event_id]


@app.get("/organizers/{organizer_email}/events")
def get_organizer_events(organizer_email: str):
    """Get all events created by a specific organizer"""
    organizer_events = [
        event for event in events.values()
        if event["organizer_email"] == organizer_email
    ]
    
    if not organizer_events:
        raise HTTPException(
            status_code=404,
            detail="No events found for this organizer"
        )
    
    return {
        "organizer_email": organizer_email,
        "events": organizer_events,
        "total": len(organizer_events)
    }


@app.get("/events")
def list_all_events(status: str = None):
    """List all events, optionally filtered by status"""
    all_events = list(events.values())
    
    if status:
        all_events = [e for e in all_events if e["status"] == status]
    
    return {
        "total": len(all_events),
        "events": all_events
    }


@app.patch("/events/{event_id}/approve")
def approve_event(event_id: int, approval: EventApproval):
    """Approve or reject an event"""
    if event_id not in events:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event = events[event_id]
    event["status"] = approval.status
    if approval.notes:
        event["approval_notes"] = approval.notes
    event["updated_at"] = datetime.now().isoformat()
    
    return {
        "message": f"Event status updated to {approval.status}",
        "event_id": event_id,
        "status": approval.status
    }


@app.post("/events/{event_id}/register")
def register_for_event(event_id: int, email: str):
    """Register a student for an event"""
    if event_id not in events:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event = events[event_id]
    
    # Check if event is approved
    if event["status"] != EventStatus.APPROVED:
        raise HTTPException(
            status_code=400,
            detail="Event is not approved yet"
        )
    
    # Check if event is full
    if len(event["attendees"]) >= event["capacity"]:
        raise HTTPException(
            status_code=400,
            detail="Event is at full capacity"
        )
    
    # Check if already registered
    if email in event["attendees"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already registered for this event"
        )
    
    event["attendees"].append(email)
    return {
        "message": f"Registered {email} for event '{event['title']}'",
        "spots_remaining": event["capacity"] - len(event["attendees"])
    }


@app.delete("/events/{event_id}/unregister")
def unregister_from_event(event_id: int, email: str):
    """Unregister a student from an event"""
    if event_id not in events:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event = events[event_id]
    
    if email not in event["attendees"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not registered for this event"
        )
    
    event["attendees"].remove(email)
    return {
        "message": f"Unregistered {email} from event '{event['title']}'",
        "spots_available": event["capacity"] - len(event["attendees"])
    }
