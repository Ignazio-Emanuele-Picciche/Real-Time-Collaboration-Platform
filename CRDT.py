class CRDT:
    """
        This class implements the CRDT data structure for the shared file
    """
    def __init__(self):
        self.document = ""
        self.operations =[]
    
    # Method to generate a unique identifier for an operation
    def apply_operation(self, operation):
        if operation['type'] == 'insert':
            self.document = self.document[:operation['index']] + operation['char'] + self.document[operation['index']:]
        elif operation['type'] == 'delete':
            self.document = self.document[:operation['index']] + self.document[operation['index'] +1:]
            self.operations.append(operation)
    
    # Method to apply an operation to the document
    def get_document(self):
        return self.document