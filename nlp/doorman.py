import time
import sys
from pathlib import Path
sys.path.insert(1, '../')
import numpy as np
import pandas as pd
import client.server_access as camera_client
from typing import Dict, List
import face_recognition
from sentence_transformers import util, SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint
from facial.qdrant import get_encodings,search, register_face
from facial.facialExceptions import FaceAlreadyExistsException
from facial.serializeQdrant import *
from util import convertDate
# TODO: make local?
#modelPath = 'all-MiniLM-L6-v2'
modelPath = 'multi-qa-MiniLM-L6-dot-v1'
model = SentenceTransformer(modelPath)
INTENTS_CSV = 'intents.csv'

SIMILARITY_THRESHOLD = 0.54
FACE_COLLECTION_NAME = 'faces'
ACCEPTANCE_THRESHOLD = 0.775

ERROR_UNABLE_TO_CAPTURE_FACE = "Unable to determine if there is a person at the door."

def search(client: QdrantClient, face_encoding):
    return client.search(
        collection_name=FACE_COLLECTION_NAME,
        query_vector=(face_encoding),
        limit=1,
        score_threshold=SIMILARITY_THRESHOLD,
        with_payload=True
    )

class Doorman:
    def __init__(self):
        # data schema from qdrant
        self.v_data = None
        # time.time() timestamp of last visitor's time
        self.v_time = 0
        self.VISITOR_TIME_DELAY_ALLOWED = 5*60 # 5 minutes
        # list of (embeddings, id) tuples
        intents_df = pd.read_csv(INTENTS_CSV)
        self.intents_embeddings = self._embed_intents(intents_df) # embed intents_df
        self.last_visitor_time = time.time()
        self.last_visitor_id = None
        self.intent_id = 0
        with open('qdrant_key.txt', 'r') as f:
            hostname = f.readline().rstrip()
            key = f.readline().rstrip()

        self.qdrant_client = QdrantClient(host=hostname,
                                    api_key=key)
        self.serializedPerson = None


    def handleRequest(self, user_speech: str):
        """Returns the text response to the user's input"""
        # if the visitor is new
        if (time.time() - self.last_visitor_time > self.VISITOR_TIME_DELAY_ALLOWED or self.v_data == None):
            self.last_visitor_time = time.time()
            # call camera and get rbg ndarray
            image = camera_client.request_image()
            camera_client.save_image(image)
            #face_embeddings = face_recognition.face_encodings(image)
            imgPath = Path('../CapturedImages/capturedImage.png')
            face_embeddings = get_encodings(imgPath)
            if len(face_embeddings) == 0:
                return ERROR_UNABLE_TO_CAPTURE_FACE
            # call call qdrant
            results = search(self.qdrant_client, face_embeddings[0])
            if len(results) == 1:
                self.v_data = results[0].payload
                print("got a match")
                self.serializedPerson = person(results[0].payload)
                self.last_visitor_id = 2
        self.intent_id = self._get_intent(user_speech)
        text_response = self._get_response(self.intent_id)
        return (text_response, face_embeddings)

    def _get_intent(self, user_speech: str) -> int:
        """Returns the id of the most similar intent to the user's input or None if there is no reasonable match.
        :param user_speech:
        :return int:
        """
        user_embeddings = model.encode(user_speech)
        max_sim = -1.1
        max_sim_id = None
        for intent_embedding, id in self.intents_embeddings:
            sim = util.cos_sim(user_embeddings, intent_embedding)
            if max_sim < sim:
                max_sim = sim
                max_sim_id = id
        print("For sentence ", user_speech, " best score was " , max_sim)
        if max_sim > ACCEPTANCE_THRESHOLD:
            return max_sim_id
        return None

    def _get_response(self, intent_id: int) -> str:
        """Obtains response from intent_id, otherwise return a string to report no action take.
        :param intent_id:
        :return: str
        """
        print("generating response")
        if self.last_visitor_id == None:
            return "I'm not who is at the door"
        if self.intent_id == None:
            return "I'm not sure what you meant by that, please rephrase"
        if intent_id == 0:
            return f"{self.v_data['name']} is at the door"
        elif intent_id == 1:
            englishDate = convertDate(self.v_data['lastVisitDate'])
            return f"{self.v_data['name']} was last here on {englishDate}"
        elif intent_id == 2:
            return f"{self.v_data['name']} is registered on the doorman service"
        elif intent_id == 3:
            if len(self.v_data['relations']) >= 2:
                relationships_text = ", ".join(self.v_data['relations'][:-1]) + ", and " + self.v_data['relations'][1]
            elif len(self.v_data['relations']) == 1:
                relationships_text = self.v_data['relations'][0]
            else:
                return f"{self.v_data['name']} has no recorded relationships with you."
            return f"{self.v_data['name']} is related to you by being {relationships_text}"
        elif intent_id == 4:
            if len(self.v_data['peopleKnown']) >= 2:
                relationships_text = ", ".join(self.v_data['peopleKnown'][:-1]) + ", and " + self.v_data['peopleKnown'][1]
            elif len(self.v_data['peopleKnown']) == 1:
                relationships_text = self.v_data['peopleKnown'][0]
            else:
                return f"{self.v_data['name']} has no record of knoowing anyone here"
            return f"{self.v_data['name']} knows the following people, {relationships_text}"
        elif intent_id == 5:
            englishDate = convertDate(self.v_data['birthday'])
            return f"{self.v_data['name']}'s birthday is {englishDate}"
        elif intent_id == 6:
            return f"{self.v_data['name']} was here last time for {self.v_data['reasonForLastVisit']}"
        elif intent_id == 7:
            englishDate = convertDate(datetime.today().strftime('%m-%d-%Y'))
            self.serializedPerson.updateLastDateOfVisit()
            #self.v_data['lastVisitDate'] = self.serializedPerson.getLastVisitDate()
            self.serializedPerson.updateNumberOfVisits()
            #self.v_data['numberOfVisits'] +=1
            return f"{self.v_data['name']} last visit date was changed to be today, which is {englishDate}, and their number of visits is now {self.v_data['numberOfVisits']}"
        elif intent_id == 8:
            return f"{self.v_data['name']} has been here {self.v_data['numberOfVisits']} times"
        elif intent_id == 9:
            return "Please specify the name of the person you want to add."
        else:
            return "Unrecognized intent. Internal Error."

    def _embed_intents(self, intents_df):
        intents_embeddings = []
        for i, row in intents_df.iterrows():
            embeddings = model.encode(row.intent)
            intents_embeddings.append((embeddings,row.id))
        return intents_embeddings
    
    def add_new_user(self, name: str, embeddings: np.array):
        try:
                register_face(embeddings[0], name, self.v_data['birthday'], self.v_data['relations'])
        except FaceAlreadyExistsException as e:
                print(e)
        return f"{name} added to the database."
