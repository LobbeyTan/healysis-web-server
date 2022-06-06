import json
from typing_extensions import Self
from google.protobuf.timestamp_pb2 import Timestamp
from google.cloud.firestore_v1.base_document import DocumentSnapshot


class SentimentScore:

    def __init__(self, pos: float, neg: float, neu: float) -> None:
        self.pos = pos
        self.neg = neg
        self.neu = neu

    def toMap(self) -> dict:
        return {
            'pos': self.pos,
            'neg': self.neg,
            'neu': self.neu,
        }

    def toJson(self) -> str:
        return json.dumps(self.toMap())

    def fromMap(data: dict) -> Self:
        return SentimentScore(
            pos=float(data.get('pos', 0.00)),
            neg=float(data.get('neg', 0.00)),
            neu=float(data.get('neu', 0.00)),
        )

    def fromSnapshot(document: DocumentSnapshot) -> Self:
        return SentimentScore.fromMap(document.to_dict())

    def fromJson(source: str) -> Self:
        return SentimentScore.fromMap(json.loads(source))

    def __str__(self) -> str:
        return f'SentimentScore(pos: {self.pos}, neg: {self.neg}, neu: {self.neu})'


class Review:

    def __init__(self, text: str, nWords: int, highestLabel: str, highestScorePercentage: float, sentimentScore: SentimentScore, createdTime: Timestamp) -> None:
        self.text = text
        self.nWords = nWords
        self.highestLabel = highestLabel
        self.highestScorePercentage = highestScorePercentage
        self.sentimentScore = sentimentScore
        self.createdTime = createdTime

    def toMap(self) -> dict:
        return {
            'text': self.text,
            'nWords': self.nWords,
            'highestLabel': self.highestLabel,
            'highestScorePercentage': self.highestScorePercentage,
            'sentimentScore': self.sentimentScore.toMap(),
            'createdTime': self.createdTime.ToMicroseconds(),
        }

    def toJson(self) -> str:
        return json.dumps(self.toMap())

    def fromMap(data: dict) -> Self:
        timestamp = Timestamp()
        timestamp.FromMicroseconds(data.get('createdTime', 0))

        return Review(
            data.get('text', ''),
            int(data.get('nWords', 0)),
            data.get('highestLabel'),
            float(data.get('highestScorePercentage', 0.00)),
            SentimentScore.fromMap(data.get('sentimentScore', [])),
            timestamp,
        )

    def fromSnapshot(document: DocumentSnapshot) -> Self:
        return Review.fromMap(document.to_dict())

    def fromJson(source: str) -> Self:
        return Review.fromMap(json.loads(source))

    def __str__(self) -> str:
        return f'Review(text: {self.text}, nWords: {self.nWords}, highestLabel: {self.highestLabel}, highestScorePercentage: {self.highestScorePercentage}, sentimentScore: {self.sentimentScore}, createdTime: {self.createdTime})'
