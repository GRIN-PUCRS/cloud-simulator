class ObjectCollection:
    def __init__(self):
        pass

    @classmethod
    def find_by_id(cls, id):
        """ Finds a class object based on its ID attribute.
        """

        return(next(instance for instance in cls.instances if instance.id == id))

    @classmethod
    def all(cls):
        """ Returns the list of created objects of a given class.
        """

        return(cls.instances)

    @classmethod
    def count(cls):
        """ Returns the amount of created objects of a given class.
        """

        return(len(cls.instances))
