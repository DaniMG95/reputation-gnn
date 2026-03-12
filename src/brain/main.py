from common.db.connection import init_db_connection
from common.db.repository_people_neo4j import RepositoryPeopleNeo4j
from brain.graph_data_loader import GraphDataLoader
from common.schemas.person import TypePerson
from neomodel import db
from brain.model_trainer import ModelTrainer
from brain.model_predictor import ModelPredictor
from brain.models.bot_detector_gcn import BotDetectorGCN
from common.logger import LoggerIngest

def train():
    LoggerIngest.setup_logging()
    logger = LoggerIngest(name="brain.main")
    init_db_connection()

    repository_people = RepositoryPeopleNeo4j(db=db)
    graph_data_loader = GraphDataLoader(repository_people=repository_people)
    bot_model = BotDetectorGCN(in_channels=3, hidden_channels=32, out_channels=2)

    logger.info("Loading graph data...")
    data_graph = graph_data_loader.create_graph()


    model_trainer = ModelTrainer(data=data_graph, model=bot_model, epochs=200, lr=0.01)
    logger.info("Training the model...")
    model_trainer.train()
    logger.info("Saving the model...")
    model_trainer.save_model("bot_detector_gcn.pth")


def predict():
    LoggerIngest.setup_logging()
    logger = LoggerIngest(name="brain.main")
    init_db_connection()

    repository_people = RepositoryPeopleNeo4j(db=db)
    graph_data_loader = GraphDataLoader(repository_people=repository_people)
    bot_model = BotDetectorGCN(in_channels=3, hidden_channels=32, out_channels=2)

    logger.info("Predicting on new data...")
    model_predictor = ModelPredictor(model=bot_model, model_path="bot_detector_gcn.pth")

    logger.info("Getting random persons for prediction...")
    persons_randoms = repository_people.get_random_nodes(n=30)

    logger.info("Creating subgraph for prediction...")
    new_data = graph_data_loader.create_subgraph_by_persons(names=[person.name for person in persons_randoms], hops=2,
                                                            predict_mask=True)

    logger.info("Making predictions...")
    predictions = model_predictor.predict(new_data)

    for idx, person in enumerate(persons_randoms):
        person.user_type = TypePerson.PERSON if person.user_type == TypePerson.INFLUENCER else person.user_type
        print(f"Person: {person.name}")
        print(f"Type: {person.user_type}")
        print(f"Prediction: {predictions[idx][0]}, Confidence: {predictions[idx][1]:.4f}")
        print("-" * 30)

    accuracy = sum(1 for i in range(len(predictions)) if predictions[i][0] == persons_randoms[i].user_type) / len(predictions)
    logger.info(f"Prediction accuracy: {accuracy:.4f}")


if __name__ == "__main__":
    train()
    predict()
