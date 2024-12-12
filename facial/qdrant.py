from pathlib import Path
from qdrant_client import QdrantClient, models
from qdrant_client.models import VectorParams, Distance, ScoredPoint
import face_recognition
import numpy as np
import hashlib
from typing import Dict, List
from facialExceptions import FaceAlreadyExistsException
from datetime import datetime
# Constants
SIMILARITY_THRESHOLD = 0.54
FACE_COLLECTION_NAME = 'faces'

def get_encodings(image_path: Path) -> List[np.array]:
    """
    :param      image_path: Path to the image to encode
    :return:    A list of np arrays, where each np array is of shape (128,) and
                contains the encoding of a face detected in the image
    """
    return face_recognition.face_encodings(
        face_recognition.load_image_file(image_path), num_jitters=10, model='large')


def register_face(face_encoding: np.array, name: str, birthday: str, relations: Dict):
    """
    Registers a face in the database
    :param face_encoding:
    :param name:
    :param birthday:
    :param relations:
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
    results = search(qdrant_client, face_encoding)
    if len(results) == 1:
        raise FaceAlreadyExistsException(
            f'Trying to register a face that matches already '
            f'registered face: {results[0].payload["name"]}')

    # Insert the record into the database
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
                    'lastVisitDate' : datetime.today().strftime('%Y-%m-%d'),
                    'numberOfVisits': 0,
                    'reasonForLastVisit' : "none",
                    'peopleKnown' : [],
                    'numberOfVisits': 0
                }
            )
        ]
    )
    print(f'Registered {image} with ID {user_hash}')


def search(client: QdrantClient, face_encoding: np.array) -> List[ScoredPoint]:
    return client.search(
        collection_name=FACE_COLLECTION_NAME,
        query_vector=list(face_encoding),
        limit=1,
        score_threshold=SIMILARITY_THRESHOLD,
        with_payload=True
    )


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
                jason_encoding = encodings[0]
            elif image == Path('images/sophia.jpg'):
                sophia_encoding = encodings[0]
            elif image == Path('images/miguel.jpg'):
                miguel_encoding = encodings[0]
            print(f'Registering {image}')
            try:
                register_face(encodings[0], image, 'MM-DD-YYYY', {})
            except FaceAlreadyExistsException as e:
                print(e)



    print(np.linalg.norm(miguel_encoding - jason_encoding))

    encoding = get_encodings('testImages/maximostest1.jpg')[0]
    #print(search(encoding))
