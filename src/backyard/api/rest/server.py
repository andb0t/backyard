import logging

import connexion


class RestServer:
    app = None

    def start(self, port=8080):
        self.app = connexion.AioHttpApp(__name__, specification_dir='./', debug=True)
        self.app.app.logger.setLevel(logging.DEBUG)
        self.app.add_api('api.yaml', arguments={'title': 'Cyber fighters backyard REST API'}, pass_context_arg_name='request_ctx')
        self.app.run(port=port)

    def stop(self):
        self.app.shutdown()
