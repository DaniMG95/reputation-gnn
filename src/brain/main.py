from common.db.connection import init_db_connection
from common.db.repository_people_neo4j import RepositoryPeopleNeo4j
from brain.data.graph_loader import GraphDataLoader
from neomodel import db
from brain.trainers.factory import ModelTrainerFactory
from brain.predictor import ModelPredictor
from brain.architectures.factory import ModelFactory
from common.logger import Logger
from brain.config import settings
from brain.trainers.components.early_stopping import EarlyStopping

Logger.setup_logging()
init_db_connection()
repository_people = RepositoryPeopleNeo4j(db=db)
graph_data_loader = GraphDataLoader(repository_people=repository_people)


def train():
    logger = Logger(name="brain.main_train")

    logger.info(f"Splitting graph data into training, validation, and test sets with ratios "
                f"validation {settings.ratio_validation} and test {settings.ratio_test}...")
    training_graph, validation_graph, test_graph = graph_data_loader.split_graph_train_val_test(
        ratio_validation=settings.ratio_validation, ratio_test=settings.ratio_test)

    bot_model = ModelFactory.create_model(model_name=settings.model_name,in_channels=training_graph.num_features,
                                          hidden_channels=settings.hidden_channels, out_channels=2)
    early_stopping = EarlyStopping(patience=settings.early_stopping_patience,
                                   min_delta=settings.early_stopping_delta)
    logger.info(f"Creating model trainer of type {settings.type_trainer} with early stopping "
                     f"patience {settings.early_stopping_patience} and delta {settings.early_stopping_delta}...")
    model_trainer = ModelTrainerFactory.create_trainer_model(type_model_trainer=settings.type_trainer, model=bot_model,
                                                             epochs=settings.epochs, lr=settings.learning_rate,
                                                             early_stopping=early_stopping)

    logger.info(f"Preparing data for training and validation using strategy {settings.type_trainer}...")
    train_data = graph_data_loader.prepare_data_for_strategy(data=training_graph, strategy=settings.type_trainer)
    val_data = graph_data_loader.prepare_data_for_strategy(data=validation_graph, strategy=settings.type_trainer)

    logger.info("Training the model...")
    model_trainer.train(train_data=train_data, validation_data=val_data)
    logger.info("Saving the model...")
    model_trainer.save_model(settings.model_path)

    acc = model_trainer.eval_predict(data=test_graph)

    logger.info(f"Test Accuracy: {acc*100:.2f}%")

def test():
    logger = Logger(name="brain.main_test")

    logger.info(f"Selecting {settings.n_nodes_test} random nodes for testing...")
    persons_randoms = repository_people.get_random_nodes(n=settings.n_nodes_test)
    names_randoms = [person.name for person in persons_randoms]

    logger.info(f"Loading graph data by test {settings.n_nodes_test} nodes...")
    test_graph, _ = graph_data_loader.create_subgraph_by_persons(names=names_randoms, mask_predict=True, normalise=True)

    bot_model = ModelFactory.create_model(model_name=settings.model_name, in_channels=test_graph.num_features,
                                          hidden_channels=settings.hidden_channels, out_channels=2)
    logger.info("Loading the model...")
    model_predictor = ModelPredictor(model=bot_model, model_path=settings.model_path)


    acc = model_predictor.eval_predict(data=test_graph)

    logger.info(f"Test Accuracy: {acc*100:.2f}%")

if __name__ == "__main__":
    train()
    test()
