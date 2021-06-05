class ObjectCollection:
    """ This class provides a set of auxiliar methods that facilitates
    objects manipulation so that we can just create objects and accessing
    them using these methods instead of storing them into lists and
    passing these lists to each method we want to call.
    """

    def __init__(self):
        pass


    @classmethod
    def find_by(cls, attribute_name, desired_attribute_value):
        """ Finds class objects based on any object
        attribute. User must inform the attribute name.

        Parameters
        ==========
        attribute_name : String
            Attribute that we will use to search the objects

        desired_attribute_value : Any
            The value by which we will look for the objects
        """

        return([classInstance for classInstance in cls.instances
        	if getattr(classInstance, attribute_name) == desired_attribute_value])


    @classmethod
    def find_by_id(cls, id):
        """ Finds a class object based on its ID attribute.

        Parameters
        ==========
        id : int
            Unique identifier that will be used to find a given object
        """

        return(next((classInstance for classInstance in cls.instances
            if classInstance.id == id), None))


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


    @classmethod
    def first(cls):
        """ Returns the first class object.
        """

        return(cls.instances[0])


    @classmethod
    def last(cls):
        """ Returns the last class object.
        """

        return(cls.instances[-1])
