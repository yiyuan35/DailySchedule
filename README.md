# Daily Scheduler Backend
Link IOS repo: 

## Summary: 
We are creating a daily scheduler. The user can add events, rank them with importance rate, and delete them. When they click on a event, it will open up another UIviewController where they can edit details. 

## Functions:
- Register and Login 
- View the events on a specific date
- Edit events (set title, detail, location, etc;)
- Sort event according to importance rate
- Delete event

## Routes
#### Get events for a given date
Request: GET /api/events/{date}/

#### Get events list in descending order for a given date
Request: GET /api/events/{date}/order/

#### Create an event
Request: POST /api/events/
Body:
{
  "title": <USER INPUT>,
  "detail": <USER INPUT>,
  “date”: <USER INPUT>,
  “location”: <USER INPUT>,
  “importance”: <USER INPUT>
}

