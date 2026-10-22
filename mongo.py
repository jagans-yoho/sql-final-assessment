import mongomock
client = mongomock.MongoClient()
mongo_db = client["retail_db"]
events_col = mongo_db["order_events"]

events_col.delete_many({})

events = [
    {
        "event_id": "EVT101",
        "customer_id": 1,
        "amount": 700,
        "status": "COMPLETED",
    },
    {
        "event_id": "EVT102",
        "customer_id": 1,
        "amount": 600,
        "status": "COMPLETED",
    },
    {
        "event_id": "EVT103",
        "customer_id": 2,
        "amount": 300,
        "status": "COMPLETED",
    },
    {
        "event_id": "EVT104",
        "customer_id": 2,
        "amount": 550,
        "status": "COMPLETED",
    },
    {
        "event_id": "EVT105",
        "customer_id": 3,
        "amount": 400,
        "status": "COMPLETED",
    },
]

events_col.insert_many(events)
print("Inserted 5 order events into MongoDB successfully.")

pipeline = [
    {
        "$group": {
            "_id": "$customer_id",
            "total_sales": {"$sum": "$amount"},
            "order_count": {"$sum": 1},
        }
    },
    {"$sort": {"_id": 1}},
]

print("\n MongoDB Totals per Customer ")
results = list(events_col.aggregate(pipeline))
for doc in results:
  print(f"Mongo totals: customer {doc['_id']} -> {doc['total_sales']}")