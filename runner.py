rfs_gateway = [
    {
        "venue": "B2C2",
        "connected": "true"
    },
    {
        "venue": "CUMBERLAND",
        "connected": "true"
    },
    {
        "venue": "JUMP",
        "connected": "false"
    },
    {
        "venue": "OSL",
        "connected": "false"
    },
    {
        "venue": "WINTERMUTE",
        "connected": "true"
    },
    {
        "venue": "GALAXY",
        "connected": "false"
    }
]
gateway = 'OSL'
for value in rfs_gateway:
    if value['venue'] == gateway:
        connected_value = value['connected']
        print(value['venue'], connected_value)