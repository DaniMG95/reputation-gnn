from common.db.connection import init_db_connection
from common.db.repository_people_neo4j import RepositoryPeopleNeo4j
from brain.graph_data_loader import GraphDataLoader
from neomodel import db
from brain.model.full_batch_model import FullBatchModel
from brain.model.model_predictor import ModelPredictor
from brain.models.model_factory import ModelFactory
from common.logger import Logger
from brain.config import settings

Logger.setup_logging()
init_db_connection()
repository_people = RepositoryPeopleNeo4j(db=db)
graph_data_loader = GraphDataLoader(repository_people=repository_people)


def train():
    logger = Logger(name="brain.main_train")

    logger.info("Loading graph data by training...")
    training_graph, validation_graph, test_graph = graph_data_loader.split_graph_train_val_test(
        ratio_validation=settings.ratio_validation, ratio_test=settings.ratio_test)

    bot_model = ModelFactory.create_model(model_name=settings.model_name,in_channels=training_graph.num_features,
                                          hidden_channels=settings.hidden_channels, out_channels=2)
    model_trainer = FullBatchModel(model=bot_model, epochs=settings.epochs, lr=settings.learning_rate)

    logger.info("Training the model...")
    model_trainer.train(train_data=training_graph, validation_data=validation_graph)
    logger.info("Saving the model...")
    model_trainer.save_model(settings.model_path)

    acc = model_trainer.eval_predict(data=test_graph)

    logger.info(f"Test Accuracy: {acc*100:.2f}%")

def test():
    logger = Logger(name="brain.main_test")

    logger.info(f"Loading graph data by test {settings.n_nodes_test} nodes...")
    persons_randoms = repository_people.get_random_nodes(n=settings.n_nodes_test)
    names_randoms = [person.name for person in persons_randoms]
    test_graph = graph_data_loader.create_subgraph_by_persons(names=names_randoms, mask_predict=True, normalise=True)

    bot_model = ModelFactory.create_model(model_name=settings.model_name, in_channels=test_graph.num_features,
                                          hidden_channels=settings.hidden_channels, out_channels=2)
    logger.info("Loading the model...")
    model_predictor = ModelPredictor(model=bot_model, model_path=settings.model_path)


    acc = model_predictor.eval_predict(data=test_graph)

    logger.info(f"Test Accuracy: {acc*100:.2f}%")

if __name__ == "__main__":
    train()
    test()
