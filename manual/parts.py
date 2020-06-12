"""
"""
from jupydoc import DocPublisher

__docs__ = ['ManualParts']

class ManualParts(DocPublisher):
    """
    title: Manual parts
    abstract: Sections of a manual, meant to be included 
    
    sections: 
          replacement section_with_subsections
          
    subsections:
        section_with_subsections:
            first_subsection
            second_subsection
    """

    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass
    
    def replacement(self):
        """Replacement
        
        * list 
        {test_list}
        * dict {test_dict}
        """
        test_list = range(10)
        test_dict = dict( (i, i*i) for i in test_list)
        self.publishme()
        
    def section_with_subsections(self):
        """Section with subsection
        
        This section was declared to have subsections, via a "subsections:"  line in the class docstring
        It produces this:

        
        When the document is assembled, after the function is run in the loop over sections, each of its 
        subsections is run, in the order declared.
        
        """
        r = 1/3
        test_dict = self.info
        self.publishme()
    
    def first_subsection(self):
        """First Subsection

        r={r:.2f}
        """
        self.publishme()
        
    def second_subsection(self):
        """Second subsection
        
        {self.subsection_dict}
        """
        self.publishme()
