import asyncio


# Define the asynchronous function to run the task
async def my_background_task():
    print("Task is running in the background")


# Define another asynchronous function to handle the delay and task scheduling
async def schedule_task(task_callable, delay):
    # Wait for the delay
    await asyncio.sleep(delay)
    # Run the background task
    await task_callable()


# Entry point for the asyncio program
async def main():
    # Schedule the background task
    task = asyncio.create_task(schedule_task(my_background_task, 5))
    print("Task scheduled, it will run after 2 hours")
    print("Task scheduled, it will run after 2 hours")
    print("Task scheduled, it will run after 2 hours")
    print("Task scheduled, it will run after 2 hours")
    print("Task scheduled, it will run after 2 hours")
    print("Task scheduled, it will run after 2 hours")
    # Optionally, await the task if you need to keep the main function alive
    await task


# Run the asyncio program
asyncio.run(main())
