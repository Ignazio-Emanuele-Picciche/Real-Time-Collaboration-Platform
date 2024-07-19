class CRDT:
    """
        This class implements the CRDT data structure for the shared file
    """

    '''
        This method initializes the CRDT class

        Args:
            None

        Returns:
            None
    '''
    def __init__(self):
        self.document = ""
        self.operations =[]
    
    '''
        This method generates a unique identifier for an operation

        Args:
            operation: The operation to apply to the document

        Returns:
            None
    '''
    def apply_operation(self, operation):
        if operation['type'] == 'insert':
            self.document = self.document[:operation['index']] + operation['char'] + self.document[operation['index']:]
        elif operation['type'] == 'delete':
            self.document = self.document[:operation['index']] + self.document[operation['index'] +1:]
            self.operations.append(operation)
    
    '''
        This method gets the document
        Args:
            None
        Returns:
            document: The document
    '''
    def get_document(self):
        return self.document