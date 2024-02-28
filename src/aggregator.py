import json
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient


async def aggregate_salary_data(dt_from, dt_upto, group_type):
    client = AsyncIOMotorClient(
            'mongodb://127.0.0.1:27017/',
        )
    db = client['payments']
    collection = db['sample_collection']

    if group_type == 'hour':
        date_format = '%Y-%m-%dT%H:00:00'
    elif group_type == 'day':
        date_format = '%Y-%m-%dT00:00:00'
    elif group_type == 'month':
        date_format = '%Y-%m-01T00:00:00'

    pipeline = [
        {
            '$match': {
                'dt': {
                    '$gte': datetime.fromisoformat(dt_from),
                    '$lte': datetime.fromisoformat(dt_upto)
                }
            }
        },
        {
            '$group': {
                '_id': {
                    '$dateToString': {'format': date_format, 'date': {'$toDate': '$dt'}}
                },
                'total': {'$sum': '$value'}
            }
        },
        {
            '$sort': {'_id': 1}
        }
    ]

    result = await collection.aggregate(pipeline).to_list(length=None)
    dataset = [doc['total'] for doc in result]
    labels = [doc['_id'] for doc in result]

    return json.dumps({'dataset': dataset, 'labels': labels})
