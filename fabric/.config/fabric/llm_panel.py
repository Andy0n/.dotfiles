from panel import Panel


class LlmPanel(Panel):
    def __init__(self, app, **kwargs):
        super().__init__(title="LLM", **kwargs)

        self.app = app

        # self.a
