from sqlalchemy import create_engine
import models

engine = create_engine('sqlite:///app.db')
models.Base.metadata.create_all(engine)
