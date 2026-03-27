from common.db.connection import init_db_connection
from common.db.repository_people_neo4j import RepositoryPeopleNeo4j
from brain.graph_data_loader import GraphDataLoader
from common.schemas.person import TypePerson
from neomodel import db
from brain.model_trainer import ModelTrainer
from brain.model_predictor import ModelPredictor
from brain.models.bot_detector_gcn import BotDetectorGCN
from common.logger import Logger
from brain.config import settings

def train():
    Logger.setup_logging()
    logger = Logger(name="brain.main")
    init_db_connection()

    repository_people = RepositoryPeopleNeo4j(db=db)
    graph_data_loader = GraphDataLoader(repository_people=repository_people)
    logger.info("Loading graph data...")
    data_graph = graph_data_loader.create_graph(p_validation=settings.ratio_validation)

    bot_model = BotDetectorGCN(in_channels=data_graph.num_features, hidden_channels=settings.hidden_channels,
                               out_channels=2)
    model_trainer = ModelTrainer(data=data_graph, model=bot_model, epochs=settings.epochs, lr=settings.learning_rate)
    logger.info("Training the model...")
    model_trainer.train()
    logger.info("Saving the model...")
    model_trainer.save_model(settings.model_path)


def predict_eval():
    Logger.setup_logging()
    logger = Logger(name="brain.main")
    init_db_connection()

    repository_people = RepositoryPeopleNeo4j(db=db)
    graph_data_loader = GraphDataLoader(repository_people=repository_people)

    logger.info("Getting random persons for prediction...")
    persons_randoms = repository_people.get_random_nodes(n=settings.n_nodes_test)

    logger.info("Creating subgraph for prediction...")
    names = [person.name for person in persons_randoms]
    new_data = graph_data_loader.create_subgraph_by_persons(names=names, mask_predict=True)

    bot_model = BotDetectorGCN(in_channels=new_data.num_features, hidden_channels=settings.hidden_channels,
                               out_channels=2)

    logger.info("Predicting on new data...")
    model_predictor = ModelPredictor(model=bot_model, model_path=settings.model_path)

    logger.info("Making predictions...")
    predictions = model_predictor.predict(new_data=new_data, names=names)


    for idx, person in enumerate(persons_randoms):
        person_type = person.user_type
        person.user_type = TypePerson.PERSON if person.user_type == TypePerson.INFLUENCER else person.user_type
        if person.user_type != predictions[idx].user_type:
            print(f"Person: {person.name}")
            print(f"Type: {person_type}, posts {person.posts}, followers {person.n_followers}, following {person.n_following}")
            print(f"Prediction: {predictions[idx].user_type}, Confidence: {predictions[idx].confidence:.4f}")
            print("-" * 30)

    accuracy = sum(1 for i in range(len(predictions)) if predictions[i].user_type == persons_randoms[i].user_type) / len(predictions)
    logger.info(f"Prediction accuracy: {accuracy:.4f}")


if __name__ == "__main__":
    # train()
    predict_eval()
