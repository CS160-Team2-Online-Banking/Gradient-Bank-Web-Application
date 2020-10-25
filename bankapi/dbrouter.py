class CustomRouter:
    def db_for_read(self, model, **hints):
        if hasattr(model, 'use_db'):
            return model.use_db
        return None

    def db_for_write(self, model, **hints):
        if hasattr(model, 'use_db'):
            return model.use_db
        return None
