class CustomRouter:
    def db_for_read(self, model, **hints):
        if hasattr(model, 'use_db'):
            return model.use_db
        return None

    def db_for_write(self, model, **hints):
        if hasattr(model, 'use_db'):
            return model.use_db
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # modify this so it checks the actual model class to see what database it should be migrated to
        if app_label == 'bankapi':
            return db == 'bank_data'
        return None
