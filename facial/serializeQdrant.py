from dataclasses import dataclass
from qdrant_client.models import VectorParams, Distance, ScoredPoint
from qdrant_client import QdrantClient, models
import hashlib
from datetime import datetime
import numpy as np
FACE_COLLECTION_NAME = 'faces'
@dataclass
class person:
    name: str
    birthday: str
    relationship: list[str]
    lastVisitDate: str
    numberOfVisits: int
    reasonForVisit: str
    peopleKnown: list[str]
    user_hash: int

    def __init__(self, payload):
        self.name = payload["name"]
        self.birthday = payload["birthday"]
        self.relationship = payload["relations"]
        self.lastVisitDate = payload["lastVisitDate"]
        self.numberOfVisits = payload["numberOfVisits"]
        self.reasonForVisit = payload["reasonForLastVisit"]
        self.peopleKnown = payload["peopleKnown"]
        self.user_hash = int(hashlib.sha256(f'{self.name}-{self.birthday}'.encode('utf-8')).hexdigest(), 16) % (10 ** 18)


    """
    The following are used for fetching for an instantiated person.
    Writes to the database are also reflected on the person object.
    """
    @property
    def getName(self) -> str:
        return self.name

    @property
    def getBirthday(self) -> str:
        return self.name

    @property
    def getRelationships(self) -> list[str]:
        return self.relationship

    @property
    def getLastVisitDate(self) -> str:
        return self.lastVisitDate

    @property
    def getNumberOfVisits(self) -> int:
        return self.numberOfVisits

    @property
    def getReasonForLastVisit(self) -> str:
        return self.reasonForVisit

    @property
    def getListOfPeopleKnown(self) -> list[str]:
        return self.peopleKnown

    # DO NOT CALL FROM FRONT END.
    def writePayload(self, payloadIn):
         with open('qdrant_key.txt', 'r') as f:
            hostname = f.readline().rstrip()
            key = f.readline().rstrip()

            client = QdrantClient(host=hostname,
                                 api_key=key)
            client.set_payload(
            collection_name=FACE_COLLECTION_NAME,
            payload=payloadIn,
                points=[self.user_hash],
            )

    # DO NOT CALL FROM FRONT END.
    def retrievePayload(self):
        with open('qdrant_key.txt', 'r') as f:
            hostname = f.readline().rstrip()
            key = f.readline().rstrip()

            client = QdrantClient(host=hostname,
                                 api_key=key)
        results = client.retrieve(
            collection_name=FACE_COLLECTION_NAME,
            ids=[self.user_hash],
        )
        return results



    def updateRelationships(self, payload: list[str], operation: str):
        if operation == "ADD":
            self.relationship = list(set(self.relationship + payload))
        elif operation == "DELETE":
            self.relationship= [personName for personName in self.peopleKnown if personName not in payload]
        else:
            print("UNKNOWN OPERATION")
        payload={
            "relations":self.relationship,
        }
        self.writePayload(payload)

    "Used internally for testing."
    def pullRelationships(self) -> list[str]:
        results = self.retrievePayload()
        return results[0].payload["relations"]

    "Used internally for testing."
    def pullKnownPeople(self) -> list[str]:
        results = self.retrievePayload()
        return results[0].payload["peopleKnown"]

    def updateLastDateOfVisit(self):
        payload={
            "lastVisitDate": datetime.today().strftime('%m-%d-%Y'),
        }
        self.writePayload(payload)

    def updateNumberOfVisits(self):
        self.numberOfVisits +=1
        payload={
                "numberOfVisits" : self.numberOfVisits
        }
        self.writePayload(payload)

    def updateReasonForVisit(self, reason : str):
        self.reasonForVisit = reason
        payload={
            "reasonForLastVisit" : self.reasonForVisit
        }
        self.writePayload(payload)


    def updateListOfPeopleKnown(self, payload : list[str], operation: str):
        if operation == "ADD":
            self.peopleKnown = list(set(self.peopleKnown + payload))
        elif operation == "DELETE":
            self.peopleKnown = [personName for personName in self.peopleKnown if personName not in payload]
        else:
            print("UNKNOWN OPERATION")
        payload={
                "peopleKnown" : self.peopleKnown
            }
        self.writePayload(payload)
