from pathlib import Path
from qdrant_client import QdrantClient, models
from qdrant_client.models import VectorParams, Distance, ScoredPoint
import face_recognition
import numpy as np
import hashlib
from typing import Dict, List
from facialExceptions import FaceAlreadyExistsException
from qdrant import search, get_encodings, register_face
#from facial import parseTestImage
import serializeQdrant


if __name__ == '__main__':
    with open('qdrant_key.txt', 'r') as f:
        hostname = f.readline().rstrip()
        key = f.readline().rstrip()

    qdrant_client = QdrantClient(host=hostname,
                                 api_key=key)

    test_list = Path('testImages').glob('*.jpg')
    for image in test_list:
        encoding = get_encodings(image)
        if image == Path('testImages/miguel.jpg'):
            res = search(qdrant_client,encoding[0])
            serializedPayload = serializeQdrant.person(res[0].payload)
            assert res[0].payload["name"] == "Miguel"
            updateRelationship = ["person is my father"]
            serializedPayload.updateRelationships(updateRelationship, "ADD")
            serializedPayload.updateLastDateOfVisit
            assert serializedPayload.pullRelationships().count(updateRelationship[0]) == 1
            assert serializedPayload.getListOfPeopleKnown.count("maximos") == 1
            serializedPayload.updateRelationships(updateRelationship, "DELETE")
            assert serializedPayload.pullRelationships().count(updateRelationship[0]) == 0
            newPeople = ["doowan"]
            serializedPayload.updateListOfPeopleKnown(newPeople, "ADD")
            assert serializedPayload.getListOfPeopleKnown.count("maximos") == 1
            assert serializedPayload.getListOfPeopleKnown.count("doowan") == 1
            # See if changes are persistent in database
            knownPeople = serializedPayload.pullKnownPeople()
            assert knownPeople.count("doowan") == 1
            assert knownPeople.count("maximos") == 1
            serializedPayload.updateListOfPeopleKnown(newPeople, "DELETE")
            assert serializedPayload.getListOfPeopleKnown.count("doowan") == 0
        elif image == Path('testImages/maximostest1.jpg'):
            res = search(qdrant_client,encoding[0])
            assert res[0].payload["name"] == "Max"
        elif image == Path('testImages/rand.jpg'):
            res = search(qdrant_client,encoding[0])
            assert not res
