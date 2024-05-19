# Micro Attendance System

"micro-attendance-system" or "mas" is a lightweight and easy to use attendance server that allows you to easily track your attendance
manage classroom and generate attendance records of each student.


## Dependencies

There are a couple of dependencies you need to install before you can start using this project.

```bash
fastapi pydantic uvicorn sqlite3 requests
```

Use poetry to install those packages

```bash
poetry install
```

## Usage

```bash
poetry run start
```

To create record a single attendance the system must create 3 entities
including **student**,**classroom**,**enrollment** and finally the
**attendance** record. These items must be created in order.


## Entities
There are multiple entities available in this project including
- student
- classroom
- attendance
- enrollment
The entities are not a lot as for now because we want to keep the system as
lean as possible. Any new features will be added in the future and many more
entities will be included.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
