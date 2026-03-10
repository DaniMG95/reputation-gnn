from common.db.connection import init_db_connection
from common.db.repository_people_neo4j import RepositoryPeopleNeo4j
from brain.graph_data_loader import GraphDataLoader
from neomodel import db
from brain.model_trainer import ModelTrainer
from brain.model_predictor import ModelPredictor
from brain.models.bot_detector_gcn import BotDetectorGCN
from torch_geometric.data import Data
import torch

def main():
    init_db_connection()
    repository_people = RepositoryPeopleNeo4j(db=db)
    graph_data_loader = GraphDataLoader(repository_people=repository_people)
    data_graph = graph_data_loader.create_graph()


    bot_model = BotDetectorGCN(in_channels=data_graph.num_node_features, hidden_channels=16, out_channels=2)
    model_trainer = ModelTrainer(data=data_graph, model=bot_model, epochs=200, lr=0.01)
    model_trainer.train()
    model_trainer.save_model("bot_detector_gcn.pth")


    model_predictor = ModelPredictor(model=bot_model, model_path="bot_detector_gcn.pth")


    prediction = model_predictor.predict(new_data)

    print(f'Predicted type: {prediction[0]}, Confidence: {prediction[1]:.4f}')
