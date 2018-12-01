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
Response:
```
{
  "success": True,
  "data": [
    {
      "id": 0,
      "title": “Event 1”,
      "detail": "abc",
      “date”: <USER INPUT DATE>,
      “location”: “Gates Hall”,
      “importance”: 1
    },
    {
      "id": 1,
      "title": “Event 2”,
      "detail": "abc",
      “date”: <USER INPUT DATE>,
      “location”: “Gates Hall”,
      “importance”: 3
    }
  ]
}
```

#### Get events list in descending order for a given date
Request: GET /api/events/{date}/order/
Response:
```
{
  "success": True,
  "data": [
    {
      "id": 0,
      "title": “Event 1”,
      "detail": "abc",
      “date”: <USER INPUT DATE>,
      “location”: “Gates Hall”,
      “importance”: 3
    },
    {
      "id": 1,
      "title": “Event 2”,
      "detail": "abc",
      “date”: <USER INPUT DATE>,
      “location”: “Gates Hall”,
      “importance”: 1
    }
  ]
}
```

#### Create an event
Request: POST /api/events/
Body:
```
{
  "title": <USER INPUT>,
  "detail": <USER INPUT>,
  “date”: <USER INPUT>,
  “location”: <USER INPUT>,
  “importance”: <USER INPUT>
}
```
Response:
```
{
  "success": True,
  "data": {
    "id": <ID>
    "title": <USER INPUT FOR TITLE>,
    "detail": <USER INPUT FOR DETAIL>,
    "date": <USER INPUT FOR date>,
    "location": <USER INPUT FOR LOCATION>,
    "importance": <USER INPUT FOR IMPORTANCE>
  }
}
```

#### Edit an event
Request: POST /api/event/{event_id}/
Body:
```
{
  "title": <USER INPUT>,
  "detail": <USER INPUT>,
  “date”: <USER INPUT>,
  “location”: <USER INPUT>,
  “importance”: <USER INPUT>
}
```
Response:
```
{
  "success": True,
  "data": <UPDATED POST WITH ID {event_id}>
}
```

#### Delete a specific post 
Request: DELETE /api/event/{event_id}/
```
Response: 
{
  "success": True,
  "data": <DELETED EVENT>
}
```

#### Get all events
Request: GET /api/events/
Response:
```
{
  "success": True,
  "data": [
    {
      "id": 0,
      "title": “Event 1”,
      "detail": "abc",
      “date”: “2018-11-11”,
      “location”: “Gates Hall”,
      “importance”: 3
    },
    {
      "id": 1,
      "title": “Event 1”,
      "detail": "abc",
      “date”: “2018-11-11”,
      “location”: “Gates Hall”,
      “importance”: 3
    }
  ]
}
```

#### Log in
Request: POST /login/
Body:
```
{
   “email”: <USER INPUT>,
   “password”: <USER INPUT>
}
```

Register
Request: Post /register/
```
Body:
{
   “email”: <USER INPUT>,
   “password”: <USER INPUT>
}
```




