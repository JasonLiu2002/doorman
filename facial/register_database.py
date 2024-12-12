from pathlib import Path
from qdrant_client import QdrantClient, models
from qdrant_client.models import VectorParams, Distance, ScoredPoint
import face_recognition
import numpy as np
import hashlib
from typing import Dict, List
from facialExceptions import FaceAlreadyExistsException
from qdrant import get_encodings,search
from datetime import datetime
# Constants
SIMILARITY_THRESHOLD = 0.6
FACE_COLLECTION_NAME = 'faces'


def register_face(face_encoding: np.array, name: str, birthday: str, relations: list[str], reason: str, peopleKnown: list[str]) -> None:
    """
    Registers a face in the database
    :param face_encoding:
    :param name:
    :param birthday:
    :param relations:
    :param lastVisitDate:
    :param numberOfVisits:
    :param reasonForLastVisit:
    :param peopleKnown:
    :return:
    """
    # Hash is used as the point's ID and should be a one-to-one
    # correspondence to a person in the database
    user_hash = int(hashlib.sha256(f'{name}-{birthday}'.encode('utf-8')).hexdigest(), 16) % (10 ** 18)

    # Scan the database for a matching name/birthday combination
    results = qdrant_client.retrieve(
        collection_name=FACE_COLLECTION_NAME,
        ids=[user_hash]
    )
    if len(results) == 1:
        raise FaceAlreadyExistsException(
            f'Trying to register a user with the same name and '
            f'birthday as: {results[0].payload["name"]}')

    # Scan the database for a similar face
    results = search(qdrant_client,face_encoding)
    if len(results) == 1:
        raise FaceAlreadyExistsException(
            f'Trying to register a face that matches already '
            f'registered face: {results[0].payload["name"]}')

    # Insert the record into the database
    print(datetime.today().strftime('%m-%d-%Y'))
    qdrant_client.upsert(
        collection_name=FACE_COLLECTION_NAME,
        points=[
            models.PointStruct(
                id=user_hash,
                vector=list(face_encoding),
                payload={
                    'name': name,
                    'birthday': birthday,
                    'relations': relations,
                    'lastVisitDate' : datetime.today().strftime('%m-%d-%Y'),
                    'numberOfVisits': 0,
                    'reasonForLastVisit' : reason,
                    'peopleKnown' : peopleKnown

                }
            )
        ]
    )
    print(f'Registered {image} with ID {user_hash}')

# Register our faces
# Need to tune similarity threshold before Sophia can be registered

if __name__ == '__main__':
    # Init qdrant client
    with open('qdrant_key.txt', 'r') as f:
        hostname = f.readline().rstrip()
        key = f.readline().rstrip()

    qdrant_client = QdrantClient(host=hostname,
                                 api_key=key)

    image_list = Path('images').glob('*.jpg')
    for image in image_list:
        encodings = get_encodings(image)
        if len(encodings) == 1:
            if image == Path('images/jason1.jpg'):
                try:
                    register_face(encodings[0], "Jason", 'MM-DD-YYYY', [], "unknown", [])
                except FaceAlreadyExistsException as e:
                    print(e)
            elif image == Path('images/danny.jpg'):
                try:
                    register_face(encodings[0], "Danny", 'MM-DD-YYYY', [], "unknown", [])
                except FaceAlreadyExistsException as e:
                    print(e)
            elif image == Path('images/sophia.jpg'):
                try:
                    register_face(encodings[0], "Sophia", 'MM-DD-YYYY', [], "unknown", [])
                except FaceAlreadyExistsException as e:
                    print(e)
            elif image == Path('images/miguel.jpg'):
                try:
                    register_face(encodings[0], "Miguel", 'MM-DD-YYYY', [], "social gathering", ["maximos", "paul", "jouzef"])
                except FaceAlreadyExistsException as e:
                    print(e)
            elif image == Path('images/golfsteak2.jpg'):
                try:
                    register_face(encodings[0], "Zack", 'MM-DD-YYYY', [], "unknown", [])
                except FaceAlreadyExistsException as e:
                    print(e)
            elif image == Path('images/maximos0.jpg'):
                try:
                    register_face(encodings[0], "Max", '01-14-2001', ["manager at arbys"], "investigated dog nappings", ["your mother"])
                except FaceAlreadyExistsException as e:
                    print(e)

            elif image == Path('images/ruhaan.jpg'):
                try:
                    register_face(encodings[0], "Ruhaan", 'MM-DD-YYYY', [], "unknown", [])
                except FaceAlreadyExistsException as e:
                    print(e)
            print(f'Registering {image}')
