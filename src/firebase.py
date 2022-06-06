from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.client import Client
from google.cloud.firestore_v1.collection import CollectionReference

from src.model import Review

cred = credentials.Certificate(
    "./resources/healysis-firebase-adminsdk-4wiie-475fa59222.json",
)

default_app = firebase_admin.initialize_app(cred)


class ReviewController:
    def __init__(self) -> None:
        self.client: Client = firestore.client(app=default_app)

        self.collection: CollectionReference = self.client.collection(
            'reviews'
        )

    def addReview(self, review: Review) -> None:

        self.collection.add(document_data=review.toMap())

    def getReview(self, id: str) -> Review:

        return Review.fromSnapshot(self.collection.document(id).get())

    def getReviewsInRange(self, start: datetime, stop: datetime) -> list[Review]:
        start = int(start.timestamp() * (10 ** 6))
        stop = int(stop.timestamp() * (10 ** 6))

        return [Review.fromSnapshot(document) for document in self.collection.where(u'createdTime', u'>=', start).where(u'createdTime', u'<', stop).get()]
