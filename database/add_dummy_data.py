from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
import configparser
from models import Base, City
from sample_data import sample_cities

config = configparser.ConfigParser()
config.read('config.ini')

engine = create_engine(
    f"postgresql://{config['POSTGRESQL']['USER']}:"
    f"{config['POSTGRESQL']['PASSWORD']}@"
    f"{config['POSTGRESQL']['HOST']}/"
    f"{config['POSTGRESQL']['DBNAME']}"
)

inspector = inspect(engine)

if 'cities' not in inspector.get_table_names():
    Base.metadata.create_all(engine) 

Session = sessionmaker(bind=engine)

with Session() as session:
    try:
        session.add_all(sample_cities)
        session.commit()
        print("Sample data inserted successfully.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")