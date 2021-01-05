class SlateTextIndexer(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        # text indexer for slate blocks. Relies on the slate field
        block = block or {}

        if block.get("searchableText"):
            return

        # BBB compatibility with slate blocks that used the "plaintext" field
        return (block or {}).get("plaintext", "")
