def initialize_app(app):
    from api_service.register_all import register_routes
    register_routes(app)
    return app