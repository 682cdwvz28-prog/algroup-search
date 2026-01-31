import asyncio
import logging
from task_queue import TaskQueue
from mailer import send_email

logger = logging.getLogger("worker")

class MailWorker:
    def __init__(self, queue: TaskQueue, delay_seconds: int = 2):
        self.queue = queue
        self.delay = delay_seconds
        self._running = False

    async def start(self):
        self._running = True
        logger.info("MailWorker started")
        while self._running:
            task = await self.queue.get()
            if task is None:
                await asyncio.sleep(1)
                continue

            email = task["email"]
            subject = task["subject"]
            body = task["body"]

            try:
                send_email(email, subject, body)
                logger.info(f"Sent email to {email}")
            except Exception as e:
                logger.error(f"Error sending email to {email}: {e}")

            await asyncio.sleep(self.delay)

    def stop(self):
        self._running = False
