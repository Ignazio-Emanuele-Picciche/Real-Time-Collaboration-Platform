'''
   This class implements the CRDT data structure for the shared file
'''
class CRDT:

    def __init__(self):
        self.document = ""
        self.operations =[]

    
    '''
        This method applies an operation to the document, such as inserting or deleting a character

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
    
    
    # Returns the document
    def get_document(self):
        return self.document